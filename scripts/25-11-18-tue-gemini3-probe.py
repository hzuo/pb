#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "requests>=2.32.0",
# ]
# ///

"""
Ad-hoc Gemini 3 API probe for function calling + thinking config.

This script loops with a single python_exec tool, logs full requests/responses,
executes requested code locally, and returns functionResponse payloads (with
optional inlineData) so we can inspect the REST shapes before wiring into
personalbot.py.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import textwrap
import traceback
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Dict, List

import requests

JSONDict = Dict[str, Any]
MODEL_NAME = "gemini-3-pro-preview"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"
PYTHON_EXEC_TOOL_DECL = {
    "name": "python_exec",
    "description": "Execute Python code in a sandboxed environment and return stdout/stderr.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "code": {
                "type": "STRING",
                "description": "Python source code to execute.",
            }
        },
        "required": ["code"],
    },
}
RED_PIXEL_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="


def pretty_print(title: str, data: JSONDict | list[Any]):
    print(f"\n== {title} ==")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def build_payload(
    *,
    contents: List[JSONDict],
    mode: str,
    casing: str,
) -> JSONDict:
    if casing == "camel":
        tool_block = {"functionDeclarations": [PYTHON_EXEC_TOOL_DECL]}
        payload = {
            "contents": contents,
            "tools": [tool_block],
            "toolConfig": {
                "functionCallingConfig": {
                    "mode": mode,
                }
            },
            "generationConfig": {
                "thinkingConfig": {
                    "thinkingLevel": "HIGH",
                    "includeThoughts": True,
                }
            },
        }
    elif casing == "snake":
        tool_block = {"function_declarations": [PYTHON_EXEC_TOOL_DECL]}
        payload = {
            "contents": contents,
            "tools": [tool_block],
            "tool_config": {
                "function_calling_config": {
                    "mode": mode,
                }
            },
            "generation_config": {
                "thinking_config": {
                    "thinking_level": "HIGH",
                    "include_thoughts": True,
                }
            },
        }
    else:
        raise ValueError(f"Unsupported casing: {casing}")
    return payload


def extract_function_calls(candidate: JSONDict) -> List[JSONDict]:
    calls: List[JSONDict] = []
    for key in ("functionCalls", "function_calls"):
        maybe = candidate.get(key)
        if isinstance(maybe, list):
            calls.extend(maybe)
    content = candidate.get("content") or {}
    for part in content.get("parts", []):
        fc = part.get("functionCall") or part.get("function_call")
        if fc:
            calls.append(fc)
    return calls


def capture_python(code: str) -> JSONDict:
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    status = "ok"
    try:
        compiled = compile(code, "<python_exec>", "exec")
        with redirect_stdout(buf_out), redirect_stderr(buf_err):
            exec(compiled, {})
    except SyntaxError:
        status = "syntax_error"
        traceback.print_exc(file=buf_err)
    except Exception:
        status = "runtime_error"
        traceback.print_exc(file=buf_err)
    return {
        "status": status,
        "stdout": buf_out.getvalue(),
        "stderr": buf_err.getvalue(),
    }


def build_function_response(result: JSONDict, *, include_image: bool) -> JSONDict:
    response: JSONDict = dict(result)
    fr: JSONDict = {
        "functionResponse": {
            "name": "python_exec",
            "response": response,
        }
    }
    if include_image:
        fr["functionResponse"]["parts"] = [
            {
                "inlineData": {
                    "mimeType": "image/png",
                    "data": RED_PIXEL_B64,
                    "displayName": "python-exec-demo.png",
                }
            }
        ]
    return fr


def call_gemini(api_key: str, payload: JSONDict, *, timeout: float) -> JSONDict:
    url = f"{BASE_URL}?key={api_key}"
    resp = requests.post(
        url, headers={"Content-Type": "application/json"}, json=payload, timeout=timeout
    )
    if not resp.ok:
        print(resp.text)
    resp.raise_for_status()
    return resp.json()


def run_loop(
    *,
    api_key: str,
    prompt: str,
    mode: str,
    casing: str,
    max_turns: int,
    include_image: bool,
    timeout: float,
):
    contents: List[JSONDict] = [
        {
            "role": "user",
            "parts": [
                {
                    "text": textwrap.dedent(prompt).strip(),
                }
            ],
        }
    ]

    for turn in range(1, max_turns + 1):
        payload = build_payload(contents=contents, mode=mode, casing=casing)
        pretty_print(f"Request #{turn}", payload)
        response = call_gemini(api_key, payload, timeout=timeout)
        pretty_print(f"Response #{turn}", response)

        candidates = response.get("candidates") or []
        if not candidates:
            print("No candidates returned.")
            break

        candidate = candidates[0]
        contents.append(candidate.get("content") or {})

        calls = extract_function_calls(candidate)
        if not calls:
            print("No function calls detected; exiting loop.")
            break

        response_parts = []
        for call in calls:
            args = call.get("args") or {}
            code = args.get("code")
            if not isinstance(code, str):
                print(f"Skipping invalid call payload: {call}")
                continue
            result = capture_python(code)
            response_parts.append(
                build_function_response(result, include_image=include_image)
            )

        if not response_parts:
            print("No valid tool responses produced; aborting.")
            break

        contents.append({"role": "user", "parts": response_parts})

    return contents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe Gemini 3 tool calling")
    parser.add_argument(
        "--prompt",
        default="Please run python_exec to calculate the first 10 Fibonacci numbers and summarize the output.",
    )
    parser.add_argument(
        "--mode",
        default="ANY",
        choices=["AUTO", "ANY", "NONE"],
        help="functionCallingConfig.mode value",
    )
    parser.add_argument(
        "--casing",
        default="camel",
        choices=["camel", "snake"],
        help="Toggle payload casing style",
    )
    parser.add_argument("--max-turns", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--include-image",
        action="store_true",
        help="Attach a demo inlineData blob in functionResponse.parts",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    try:
        run_loop(
            api_key=api_key,
            prompt=args.prompt,
            mode=args.mode,
            casing=args.casing,
            max_turns=args.max_turns,
            include_image=args.include_image,
            timeout=args.timeout,
        )
    except KeyboardInterrupt:
        print("Interrupted.")


if __name__ == "__main__":
    main()
