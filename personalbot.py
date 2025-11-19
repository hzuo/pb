#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = "~=3.13.9"
# dependencies = [
#     "openai>=2.8.0",
#     "anthropic>=0.72.0",
#     "prompt-toolkit>=3.0.51",
#     "pydantic>=2.11.7",
#     "rich>=14.1.0",
#     "pymysql>=1.1.1",
#     "psycopg>=3.2.10",
#     "pyyaml>=6.0.2",
#     "duckdb>=1.3.2",
#     "polars>=1.32.3",
#     "pandas>=2.3.1",
#     "playwright>=1.54.0",
#     "pypandoc>=1.15.0",
#     "pymupdf>=1.26.3",
#     "matplotlib>=3.10.6",
#     "humanize>=4.13.0",
#     "lxml>=6.0.2",
#     "beautifulsoup4>=4.13.5",
#     "markdownify>=1.2.0",
#     "pillow>=11.3.0",
#     "requests>=2.32.5",
#     "httpx>=0.28.1",
#     "tiktoken>=0.11.0",
#     "prance[osv]>=25.4.8.0",
#     "pyjwt[crypto]>=2.10.1",
#     "paramiko>=4.0.0",
#     "fabric>=3.2.2",
#     "fitdecode>=0.11.0",
# ]
# ///

import argparse
import base64
import code
import collections
import contextlib
import copy
import datetime
import importlib
import inspect
import io
import json
import mimetypes
import os
import queue
import re
import shlex
import subprocess
import sys
import textwrap
import threading
import uuid
from pathlib import Path
from typing import Any, Literal, Tuple

import openai
import prompt_toolkit
import requests
import yaml
from pydantic import BaseModel, Field, RootModel, computed_field
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

SYSTEM_PROMPT = """
You are Personal Bot, an advanced Agentic AI assisting the user for a variety of personal tasks.

You have access to a full-fledged Python kernel that has full access to the user's personal machine, including:
- Full network access. You can browse the web, make API calls, connect to DBs, etc.
- Full filesystem access. You can read and write files on the filesystem.
- Full access to an extensive set of CLI tools that you can invoke via subprocess, including ripgrep, curl, git, jq, ls, find, sed, ffmpeg, etc. You should heavily lean into the Unix philosophy and "shell out" to these external tools. Shelling out is often easier and more concise than attempting to write a bunch of Python code to do the same thing.

Many of the tasks delegated to you will be complex. You should take full advantage of the interactivity: Execute some Python, examine and reason over the output, execute some more Python, and keep iterating until you come up with the solution to the best of your ability. If necessary, perform post verification steps to ensure that your solution is correct.

You will have access to some existing helpers that will be pre-imported into your Python kernel. The definition of these helpers is shown below:

<helpers_def>
```python
{{helpers_def}}
```
</helpers_def>

<available_libraries>
dependencies = [
  "openai>=2.8.0",
  "pydantic>=2.11.7",
  "pymysql>=1.1.1",
  "psycopg>=3.2.10",
  "pyyaml>=6.0.2",
  "duckdb>=1.3.2",
  "polars>=1.32.3",
  "pandas>=2.3.1",
  "playwright>=1.54.0",
  "pypandoc>=1.15.0",
  "pymupdf>=1.26.3",
  "matplotlib>=3.10.6",
  "humanize>=4.13.0",
  "lxml>=6.0.1",
  "beautifulsoup4>=4.13.5",
  "markdownify>=1.2.0",
  "pillow>=11.3.0",
  "requests>=2.32.5",
  "httpx>=0.28.1",
  "tiktoken>=0.11.0",
  "prance[osv]>=25.4.8.0",
  "pyjwt[crypto]>=2.10.1",
  "paramiko>=4.0.0",
  "fabric>=3.2.2",
  "fitdecode>=0.11.0",
]
</available_libraries>

About the memory subsystem:
- The memory subsystem is just a normal Python class called "LongTermMemory" that's invokable via the "python_exec" tool.
- It allows you read, write, and search over on-disk files that persist across multiple sessions. These on-disk files are called "memory files", and are simply Markdown files with some YAML frontmatter attached.
- These on-disk memory files are saved in durable storage, allowing you to persist knowledge so that it is accessible to your future self in future sessions.
- Do not proactively create memory files on your own. Only do so when explicitly asked to do so by the user you're assisting. If you identify a reusable piece of knowledge during the course of working on a particular task, you can call it out - but only create the memory file after the user gives you the go-ahead.
- When editing or correcting an existing memory file, do not introduce editorial artifacts like "corrected" / "final version" / etc. You should always try to keep the writing in each memory file as clean as possible, as though it was written correctly the first time. The editorial process should be invisible to the reader.
- When editing or correcting an existing memory file, do not over-index on the edit or correction being made. Understand the key points being made by the memory file, and make the edit surgically. Insert the edit into its appropriate position in the overall importance hierarchy of the memory file.
- If it's not immediately obvious how to do the task at hand, it's usually a good idea to call "memory_list" and "memory_read" to look for a helpful memory file.
- When reading a memory file, read it in full by printing out the entire file. Do not truncate the file contents. For memory files, do not worry about the size of the output; you can assume memory files are small and the more important thing is to see the full context and not miss any info.

Here is a tutorial on how to use the "python_exec" tool:
<tutorial_yaml>
```yaml
- kind: python_exec_tool_call
  code: |
    # printing allows you to capture stuff to stdout

    print("hey")
  output:
    status: ok
    stdout: |
      hey
    stderr: ""
- kind: python_exec_tool_call
  code: |
    # You can import any helper libraries you need.
    # Note how these can be used in in later "python_exec" calls without needing to re-import.

    import datetime
    import json
    import zoneinfo
  output:
    status: ok
    stdout: ""
    stderr: ""
- kind: python_exec_tool_call
  code: |
    # note usage of datetime and zoneinfo without re-importing
    now_pt = datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York"))
    now_pt_pretty = now_pt.strftime("%A, %B %d, %Y %I:%M %p %Z")

    print("When was this tutorial created?")
    print(now_pt_pretty)
  output:
    status: ok
    stdout: |
      When was this tutorial created?
      Monday, August 11, 2025 03:16 AM EDT
    stderr: ""
```
</tutorial_yaml>

As an Agentic AI, follow these persistence guidelines:
<persistence_guidelines>
- You are an autonomous agent. Keep going until the user's query is completely resolved, before ending your turn and yielding back to the user.
- You should only end your turn if one of the following is true: (1) you are sure that the problem is solved, or (2) there's a hard blocker that you cannot work around.
- You should plan extensively before each tool call, and reflect extensively on the outcomes of previous tool calls. Reason carefully and reorient appropriately after receiving tool results. Make inferences based on each tool result, and determine the next best step based on new findings in this process.
</persistence_guidelines>

Note that you have a lot of access. Be responsible with the amount of access you have. You should never take irreversible or broadly destructive actions. Make the user manually do so if that's what they desire. You may give them instructions or commands, but never take high-risk actions directly - make the user do so instead.

You are now being connected with the user. They will delegate to you an important task, and your job is to find a solution to the best of your ability. Be persistent, diligent, and maximally helpful.
""".strip()

PYTHON_EXEC_TOOL_DESCRIPTION = """
Execute Python code in the stateful kernel environment.

Semantics and guidelines:
- When you call the python_exec tool you may pass in an arbitrary sequence of Python statements as the code to execute.
- The kernel is running Python 3.13, so feel free to use all the latest and greatest Python features and built-ins.
- The code you pass will be executed in the kernel, and the stdout and stderr emitted during the course of executing your code will be captured and returned back to you in the tool result. You must explicitly print things in order to see them - unlike a REPL you can't just evaluate an expression like "x + 1" and see its value in the output, you have to use "print(x + 1)" instead.
- The kernel is a stateful environment. All globals and any in-memory state will persist for the duration of the entire session. This persistence holds both intra-turn and inter-turn - across all rounds of python_exec calls within the same assistant turn, and across all rounds of user/assistant turns throughout the entire session.
- In other words, any variable you've previously set in a python_exec call will be available in subsequent python_exec calls. You SHOULD reuse those variables whenever possible. Do NOT unnecessarily re-build state from scratch. Do NOT import libraries when you've already imported them in a previous python_exec call.
- Think about the most concise and token-efficient way to express your intent when writing the Python code to pass into python_exec. For example, when doing data analysis, you should prefer to use DuckDB and SQL instead of Pandas or Polars, because you can express much more intent-per-token in concise high-level SQL, vs verbose low-level Pandas/Polars. Another example is shelling out to CLI tools instead of writing Python code to do the same thing.
- Prefer to use many smaller python_exec calls to quickly and iteratively probe your environment in a step-wise fashion. This will almost always allow you to reach your goals faster than if you attempted to do everything in one go.

The Small Steps Principle:
- The python_exec tool allows you to both explore and act in the world. Through executing Python code you can essentially do anything.
- When you do not yet understand the world-state you're operating in, you should make many small, iterative calls to probe the world.
- Heavily read and research the world in a step-by-step fashion in order to gain a clear understanding of the world-state in which you're operating.
- You are only allowed to make large tool calls when you have full clarity on the world-state in which you're operating.
- Do not make large tool calls attempting to speculatively one-shot the solution before you have reached this level of full clarity.
- Do not write code that is heavily branched attempting to anticipate a bunch of different potential world-states. Do a series of read calls to figure out what the actual world-state is first.
- You can make as many tool calls as you like. Take the time to fully explore the world-state so that you can maximize the correctness of your final answer.
- The user is very patient and prioritizes correctness above all else.

You must strongly adhere to the Small Steps Principle when making calls to this tool.
""".strip()


# <helpers_def>

# Note that all of these definitions get pre-defined in the kernel before your python_exec code runs.
# Your code can use them without importing them - they are ready for immediate use without causing NameError.


class Memory(BaseModel):
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    content: str = Field(
        description=(
            "The content of the memory in markdown format. "
            "Can be as short/simple or long/complex as necessary. "
            "If long/complex, add structure to make it easy to scan - "
            "use sections (headings) and bullet points (ordered and unordered lists). "
            "Feel free to take advantage of markdown features: fenced code blocks, blockquotes, etc."
        )
    )
    title: str = Field(
        description="A short and pithy title for the memory. Should be a sentence or a phrase."
    )

    @staticmethod
    def memory_compute_filename(timestamp: datetime.datetime, title: str) -> str:
        """Compute a filename for a memory based on its timestamp and title."""

        title_kebab = re.sub(r"[^a-zA-Z0-9\s]", "", title.lower())
        title_kebab = re.sub(r"\s+", "-", title_kebab.strip())

        timestamp_str = timestamp.astimezone(datetime.timezone.utc).strftime(
            "%Y-%m-%d-%H-%M-%S"
        )

        return f"{timestamp_str}-{title_kebab}"

    @computed_field
    @property
    def filename(self) -> str:
        return self.memory_compute_filename(self.timestamp, self.title)


class LongTermMemory:
    def __init__(self):
        self.memory_dir = Path(__file__).resolve().parent / "memorybank"

    @staticmethod
    def memory_compute_file_content(memory: Memory) -> str:
        """Compute the file content of a memory file, i.e. YAML frontmatter + Markdown content."""

        frontmatter = {
            "filename": memory.filename,
            "timestamp": memory.timestamp.isoformat(),
            "title": memory.title,
        }

        yaml_frontmatter = yaml.dump(frontmatter, sort_keys=False)

        return f"---\n{yaml_frontmatter}---\n\n{memory.content.strip()}\n"

    @staticmethod
    def memory_parse_file_content(file_content: str) -> Memory:
        """Parse the content of a memory file and return a Memory object."""

        # Split frontmatter from body
        parts = file_content.split("---\n", 2)
        frontmatter = yaml.safe_load(parts[1])
        content = parts[2].strip()

        data = {
            "title": frontmatter["title"],
            "timestamp": frontmatter["timestamp"],
            "content": content,
        }

        return Memory.model_validate(data)

    def memory_dir_get(self) -> Path:
        """Get the memory dir. Useful when direct filesystem-level ops are necessary (e.g. grepping)."""
        return self.memory_dir

    def memory_save(self, memory: Memory) -> Path:
        """Save a memory to the memory bank."""

        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Create the full file path
        file_path = self.memory_dir / f"{memory.filename}.md"

        # Generate the markdown content
        file_content = self.memory_compute_file_content(memory)

        # Write the file
        file_path.write_text(file_content, encoding="utf-8")

        return file_path

    def memory_delete(self, filename: str) -> bool:
        """Delete a memory by its filename (without .md extension)."""
        file_path = self.memory_dir / f"{filename}.md"

        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def memory_read_object(self, filename: str) -> Memory | None:
        """Read a memory by its filename (without .md extension)."""
        file_path = self.memory_dir / f"{filename}.md"

        if not file_path.exists():
            return None

        content = file_path.read_text(encoding="utf-8")

        try:
            memory = self.memory_parse_file_content(content)

            # Validate that the filename is self-consistent
            if memory.filename != filename:
                print(f"[libmemory] WARNING: filename mismatch for {filename}")
                return None

            return memory
        except Exception:
            # Invalid file format or validation error
            print(
                f"[libmemory] WARNING: invalid file format or validation error for {filename}"
            )
            return None

    def memory_read(self, filename: str) -> str:
        """Read a memory by its filename (without .md extension) as a string."""
        memory = self.memory_read_object(filename)
        if memory is None:
            return f"[failed to read memory {filename}]"
        return self.memory_compute_file_content(memory)

    def memory_dump(self) -> list[Memory]:
        """Dump memories as a list of Memory objects. Ordered from oldest to newest."""
        memories: list[Memory] = []
        for f in self.memory_dir.glob("*.md"):
            memory = self.memory_read_object(f.stem)
            if memory is None:
                continue
            memories.append(memory)
        memories.sort(key=lambda m: m.timestamp)
        return memories

    def memory_list(self) -> str:
        """Produce an overview of all memories as a string."""
        memories = self.memory_dump()
        lines = []
        lines.append("<memory_list>")
        for memory in memories:
            line = f"  - {memory.filename}"
            lines.append(line)
        lines.append("</memory_list>")
        return "\n".join(lines)


class Helpers:
    def __init__(self):
        self.image_attachments: list[str] = []
        self.openai_client = None

    def attach_image_to_tool_result(self, image_abs_path: str):
        """
        Attach an image to the tool result.
        This allows you to use your vision capabilities to examine images.
        You must pass an absolute path to a .png/.jpeg file saved on the local filesystem.
        The image must be <=5MB in size. If the image is too large, reduce the size via compression / scaling / cropping / grayscale / etc.
        Default to JPEG compression, but choose the best technique based on the use case.
        You can call this function multiple times to attach multiple images to the tool result.
        """

        assert (
            image_abs_path.endswith(".png")
            or image_abs_path.endswith(".jpg")
            or image_abs_path.endswith(".jpeg")
        ) and os.path.isabs(image_abs_path), (
            f"[attach_image_to_tool_result] invalid image path: {image_abs_path}"
        )

        size = os.path.getsize(image_abs_path)
        assert size <= 5 * 1024 * 1024, (
            f"[attach_image_to_tool_result] too large: {image_abs_path} - size: {size} bytes"
        )

        self.image_attachments.append(image_abs_path)
        print(f"[attach_image_to_tool_result] {image_abs_path}")

    def drain_image_attachments(self) -> list[str]:
        """
        Drain the image attachments.
        The kernel infra will automatically call this function after every python_exec call, and attach all drained images to the tool result.
        """

        drained = self.image_attachments
        self.image_attachments = []
        return drained

    def check_expected_env(self) -> dict[str, bool]:
        keys = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GEMINI_API_KEY",
        ]
        return {key: bool(os.environ.get(key)) for key in keys}

    def get_openapi_specs(self) -> list[str]:
        urls = [
            "https://raw.githubusercontent.com/frontapp/front-api-specs/refs/heads/main/core-api/core-api.json",
        ]
        return urls

    def openai_simple_call(
        self,
        instructions: str,
        input: str,
        model: Literal["gpt-5.1", "gpt-5-mini"] = "gpt-5.1",
        reasoning_effort: Literal["low", "medium", "high"] = "high",
    ):
        api_key = os.environ.get("OPENAI_API_KEY")
        assert api_key, "OPENAI_API_KEY is not set"
        if not self.openai_client:
            self.openai_client = openai.OpenAI(api_key=api_key)
        response = self.openai_client.responses.create(
            model=model,
            instructions=instructions,
            input=input,
            reasoning={
                "effort": reasoning_effort,
                "summary": "detailed",
            },
            include=["reasoning.encrypted_content"],
            previous_response_id=None,
        )
        return response.output_text

    # if you want to look something up on the web, this should be your first stop
    def openai_web_search(self, input: str) -> str:
        api_key = os.environ.get("OPENAI_API_KEY")
        assert api_key, "OPENAI_API_KEY is not set"
        if not self.openai_client:
            self.openai_client = openai.OpenAI(api_key=api_key)

        tool = {
            "type": "web_search",
            "search_context_size": "high",  # low, medium, high
        }

        include = [
            "reasoning.encrypted_content",
            "web_search_call.action.sources",
        ]

        response = self.openai_client.responses.create(
            model="gpt-5.1",
            input=input,
            tools=[tool],
            tool_choice="auto",
            reasoning={
                "effort": "high",
                "summary": "detailed",
            },
            include=include,
            previous_response_id=None,
        )
        return response.output_text

    def anthropic_simple_call(
        self,
        *,
        user_prompt: str,
        system_prompt: str | None = None,
        # don't change these defaults unless the user says otherwise
        model: Literal[
            "claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001"
        ] = "claude-sonnet-4-5-20250929",
        thinking_budget_tokens: int = 4000,
        max_tokens: int = 6000,
    ) -> str:
        anthropic_api_key = os.environ["ANTHROPIC_API_KEY"]
        assert anthropic_api_key, "ANTHROPIC_API_KEY is not set"
        req = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [],
        }
        if thinking_budget_tokens > 0:
            req["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget_tokens,
            }
        if system_prompt:
            req["system"] = system_prompt
        req["messages"].append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=req,
            timeout=120,
        )
        if not res.ok:
            print(f"Error response body: {res.text}")
        res.raise_for_status()
        res = res.json()
        res_text_blocks = [
            block.get("text")
            for block in res.get("content")
            if block.get("type") == "text"
        ]
        res_text = "\n".join(res_text_blocks)
        return res_text

    def load_local_lib(
        self,
        lib_name: str,
        src_dir: str = str((Path(__file__).parent / "platform" / "src").resolve()),
        reload: bool = False,
    ):
        """
        Ensure platform/src is on sys.path, import mod_name, and return the module.
        Idempotent: repeated calls won't duplicate sys.path entries or re-import unless reload=True.
        """
        src_path = Path(src_dir).resolve()
        if not src_path.exists():
            raise FileNotFoundError(
                f"load_local_lib import failed: source dir not found: {src_path}"
            )
        # Idempotent sys.path insertion
        sp = str(src_path)
        if sp not in sys.path:
            sys.path.insert(0, sp)
        mod = importlib.import_module(lib_name)
        if reload:
            mod = importlib.reload(mod)
        return mod

    def load_libpersonal(self):
        # source code is located at "./platform/src/libpersonal.py"
        # feel free to examine the source code to see what's available
        # (or use something like "print(help(mod))", or "inspect", etc)
        return self.load_local_lib(lib_name="libpersonal")


class MutationsApi:
    """
    Rules of Mutations:
    - Any functionality exposed by the MutationsApi is called a "Mutation" and should only be called via the MutationsApi.
    - If there are alternate ways to perform the same Mutation, do not do so. You must use the MutationsApi instead.
    - Do not call the MutationsApi unless the user explicitly asks you to do so.

    Note that unlike Helpers and LongTermMemory, MutationsApi does not have a pre-defined singleton instance.
    You should instantiate a new MutationsApi instance if you actually need to perform a Mutation (as explicitly directed by the user).
    """

    def __init__(self):
        pass


# Pre-defined singleton instances. Immediately available as globals in the kernel.
helpers = Helpers()
ltm = LongTermMemory()

# </helpers_def>


def assemble_system_prompt() -> str:
    """Assemble the system prompt for the agentic assistant."""

    # Read the source file at runtime
    source_file = Path(__file__)
    source_content = source_file.read_text()

    # Find the helpers_def section between delimiters
    start_marker = "# <helpers_def>"
    end_marker = "# </helpers_def>"

    start_idx = source_content.find(start_marker)
    end_idx = source_content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        raise ValueError("Could not find helpers_def delimiters in source file")

    # Extract the code between delimiters (excluding the delimiter lines themselves)
    # Move past the start marker and its newline
    start_idx = source_content.find("\n", start_idx) + 1
    # The end_idx is already at the start of the end marker line

    helpers_code = source_content[start_idx:end_idx].rstrip()

    # Replace the placeholder in SYSTEM_PROMPT
    assembled_prompt = SYSTEM_PROMPT.replace("{{helpers_def}}", helpers_code)

    return assembled_prompt


sandbox_globals = {
    "__builtins__": __builtins__,
    "datetime": datetime,
    "json": json,
    "textwrap": textwrap,
    "Memory": Memory,
    "LongTermMemory": LongTermMemory,
    "Helpers": Helpers,
    "MutationsApi": MutationsApi,
    "helpers": helpers,
    "ltm": ltm,
    "session_id": None,  # this gets set right at python_exec time, since this can change
    # "history": None,   # TODO(25-10-15-sun): we should set this too, enables cool use cases
    "command_params": {},  # mutated by handle_slash_command
}

sandbox = code.InteractiveConsole(locals=sandbox_globals)


class PythonExecResponse(BaseModel):
    status: str
    stdout: str
    stderr: str
    image_attachments: list[Tuple[str, str]]


def python_exec_impl(source: str) -> PythonExecResponse:
    sandbox_globals["session_id"] = session_id

    buf_out = io.StringIO()
    buf_err = io.StringIO()

    status = "unknown"
    code = None
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        try:
            code = sandbox.compile(source=source, filename="<input>", symbol="exec")
        except (OverflowError, SyntaxError, ValueError):
            sandbox.showsyntaxerror(filename="<input>")
            status = "syntax_error"

        if status == "syntax_error":
            pass
        elif code is None:
            status = "incomplete_code"
        else:
            try:
                exec(code, globals=sandbox_globals, locals=None)

                status = "ok"
            except Exception:
                sandbox.showtraceback()
                status = "runtime_error"

    return PythonExecResponse(
        status=status,
        stdout=buf_out.getvalue(),
        stderr=buf_err.getvalue(),
        image_attachments=[],
    )


console = Console(stderr=True, soft_wrap=True)
dspq = queue.Queue()


def python_exec(code: str) -> PythonExecResponse:
    dspq.put(
        {
            "type": "data-python-exec-call-start",
            "code": code,
        }
    )
    # this join is important to ensure the queue is empty before we start python_exec_impl
    # otherwise the printer thread's output will get captured by the contextlib calls made by python_exec_impl
    dspq.join()

    result = python_exec_impl(code)

    image_attachment_files = helpers.drain_image_attachments()
    image_attachments = read_image_attachments(image_attachment_files)

    result.image_attachments = image_attachments

    dspq.put(
        {
            "type": "data-python-exec-call-end",
            "status": result.status,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "image_attachments": image_attachments,
        }
    )
    dspq.join()

    return result


def read_image_attachments(image_attachment_files: list[str]) -> list[Tuple[str, str]]:
    ret: list[Tuple[str, str]] = []
    for file in image_attachment_files:
        image_bytes = Path(file).read_bytes()
        image_base64 = base64.b64encode(image_bytes).decode("ascii")

        content_type, content_encoding = mimetypes.guess_type(file)
        if not content_type:
            console.print(f"[yellow]Unexpected image content_type: {file}[/yellow]")
            continue
        if content_encoding:
            console.print(f"[yellow]Unexpected image content_encoding: {file}[/yellow]")
            continue

        base64_data_url = f"data:{content_type};base64,{image_base64}"
        ret.append((file, base64_data_url))
    return ret


def dsp_console_print(event: dict):
    event_type = event.get("type")

    if event_type == "start-step":
        turn_number = event["turn_number"]
        step_number = event["step_number"]
        console.print(
            f"[dim]<turn_{turn_number}_step_{step_number}>[/dim]", highlight=False
        )

    elif event_type == "finish-step":
        turn_number = event["turn_number"]
        step_number = event["step_number"]
        console.print(
            f"[dim]</turn_{turn_number}_step_{step_number}>[/dim]", highlight=False
        )

    elif event_type == "data-python-exec-call-start":
        code = event["code"]
        console.print("[dim]<python_exec_call>[/dim]", highlight=False)
        console.print(
            Syntax(
                code,
                "python",
                background_color="default",
            )
        )
        console.print("[dim]</python_exec_call>[/dim]", highlight=False)

    elif event_type == "data-python-exec-call-end":
        status = event["status"]
        stdout = event["stdout"]
        stderr = event["stderr"]
        image_attachments = event["image_attachments"]

        console.print("[dim]<python_exec_result>[/dim]", highlight=False)
        console.print(
            f"[dim]<status>[/dim][bold]{status}[/bold][dim]</status>[/dim]",
            highlight=False,
        )
        console.print("[dim]<stdout>[/dim]", highlight=False)
        console.print(
            Syntax(
                stdout,
                "markdown",
                background_color="default",
            )
        )
        console.print("[dim]</stdout>[/dim]", highlight=False)
        if stderr:
            console.print("[dim]<stderr>[/dim]", highlight=False)
            console.print(
                Syntax(
                    stderr,
                    "markdown",
                    background_color="default",
                )
            )
            console.print("[dim]</stderr>[/dim]", highlight=False)
        if image_attachments:

            def trunc(s: str, n: int = 100) -> str:
                return s if len(s) <= n else f"{s[:n]} [...{len(s) - n} more]"

            print_json = collections.OrderedDict()
            for file, base64_data_url in image_attachments:
                print_json[file] = trunc(base64_data_url)
            console.print("[dim]<image_attachments>[/dim]", highlight=False)
            console.print(
                Syntax(
                    json.dumps(print_json, indent=2),
                    "json",
                    background_color="default",
                )
            )
            console.print("[dim]</image_attachments>[/dim]", highlight=False)
        console.print("[dim]</python_exec_result>[/dim]", highlight=False)

    elif event_type == "data-openai-responses-api-streaming-event-pre":
        event_type = event["event_type"]
        if event_type == "response.reasoning_summary_part.added":
            console.print("[dim]<reasoning_summary_part>[/dim]", highlight=False)

    elif event_type == "data-openai-responses-api-streaming-event-post":
        event_type = event["event_type"]
        if event_type == "response.reasoning_summary_part.done":
            console.print("\n[dim]</reasoning_summary_part>[/dim]", highlight=False)

    elif event_type == "data-response-start":
        console.print("[dim]<response>[/dim]", highlight=False)

    elif event_type == "data-response-end":
        console.print("[dim]</response>[/dim]", highlight=False)

        usage = event["usage"]
        if usage:
            console.print("\n[dim]<usage>[/dim]", highlight=False)
            console.print(
                Syntax(
                    json.dumps(usage),
                    "json",
                    background_color="default",
                ),
            )
            console.print("[dim]</usage>[/dim]", highlight=False)

        console.print()

    elif event_type == "reasoning-start":
        console.print("[dim]<reasoning>[/dim]", highlight=False)

    elif event_type == "reasoning-end":
        console.print("[dim]</reasoning>[/dim]", highlight=False)

    elif event_type == "reasoning-delta":
        delta = event.get("delta", "")
        console.print(delta, end="", highlight=False)

    elif event_type == "text-start":
        console.print("\n[dim]<message>[/dim]", highlight=False)

    elif event_type == "text-end":
        console.print("\n[dim]</message>[/dim]", highlight=False)

    elif event_type == "text-delta":
        delta = event.get("delta", "")
        console.print(delta, end="", highlight=False)

    elif event_type == "tool-input-start":
        console.print("\n[dim]<function_call>[/dim]", highlight=False)

    elif event_type == "tool-input-end":
        console.print("\n[dim]</function_call>[/dim]", highlight=False)

    elif event_type == "tool-input-delta":
        delta = event.get("delta", "")
        console.print(delta, end="", highlight=False)

    elif event_type == "error":
        error_text = event.get("errorText", "")
        console.print(f"\n[yellow]error: {error_text}[/yellow]")

    else:
        console.print(f"\n[yellow]unknown event: {json.dumps(event)}[/yellow]")


def dsp_console_print_loop():
    while True:
        event = dspq.get()
        if event is None:  # stop indicator
            dspq.task_done()
            break
        dsp_console_print(event)
        dspq.task_done()


instructions = None

anthropic_model = "claude-sonnet-4-5-20250929"


def anthropic_call(history: list):
    global instructions
    if instructions is None:
        instructions = assemble_system_prompt()

    headers = {
        "content-type": "application/json",
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "interleaved-thinking-2025-05-14",
    }

    messages2 = copy.deepcopy(history)
    for message in reversed(messages2):
        if message["role"] == "user":
            assert isinstance(message["content"], list)
            assert len(message["content"]) > 0
            assert isinstance(message["content"][-1], dict)
            message["content"][-1]["cache_control"] = {"type": "ephemeral", "ttl": "5m"}
            break  # only add to the latest one
    req = {
        "model": anthropic_model,
        "max_tokens": 8000,
        "thinking": {
            "type": "enabled",
            "budget_tokens": 31_999,
        },
        "tools": [
            {
                "name": "python_exec",
                "description": PYTHON_EXEC_TOOL_DESCRIPTION,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Python code to execute.",
                        },
                    },
                    "required": ["code"],
                    "additionalProperties": False,
                },
            }
        ],
        "tool_choice": {
            "type": "auto",
            "disable_parallel_tool_use": True,
        },
        "system": [
            {
                "type": "text",
                "text": instructions,
                # always cache system prompt with 1h
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            }
        ],
        "messages": messages2,
    }

    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=req,
    )
    if not res.ok:
        dspq.put(
            {
                "type": "error",
                "errorText": f"anthropic error! {res.text}",
            }
        )
    res.raise_for_status()
    return res.json()


def anthropic_dsp_write(res: dict):
    dspq.put(
        {
            "type": "data-response-start",
            "id": res.get("id"),
        }
    )

    for block in res.get("content", []):
        block_type = block.get("type")

        if block_type == "thinking":
            dspq.put(
                {
                    "type": "reasoning-start",
                    "id": block.get("id"),
                }
            )
            thinking_text = block.get("thinking", "")
            if thinking_text:
                dspq.put(
                    {
                        "type": "reasoning-delta",
                        "id": block.get("id"),
                        "delta": thinking_text.strip() + "\n",
                    }
                )
            dspq.put(
                {
                    "type": "reasoning-end",
                    "id": block.get("id"),
                }
            )

        elif block_type == "text":
            dspq.put(
                {
                    "type": "text-start",
                    "id": block.get("id"),
                }
            )
            text_content = block.get("text", "")
            if text_content:
                dspq.put(
                    {
                        "type": "text-delta",
                        "id": block.get("id"),
                        "delta": text_content,
                    }
                )
            dspq.put(
                {
                    "type": "text-end",
                    "id": block.get("id"),
                }
            )

        elif block_type == "tool_use":
            dspq.put(
                {
                    "type": "tool-input-start",
                    "toolCallId": block.get("id"),
                    "toolName": block.get("name"),
                }
            )
            tool_input = json.dumps(block.get("input", {}), indent=2)
            if tool_input:
                dspq.put(
                    {
                        "type": "tool-input-delta",
                        "toolCallId": block.get("id"),
                        "delta": tool_input,
                    }
                )
            dspq.put(
                {
                    "type": "tool-input-end",
                    "id": block.get("id"),
                }
            )

    usage = res.get("usage", {})
    if usage:
        usage_copy = dict(usage)
        usage_copy["provider"] = "anthropic"
        usage_copy["model"] = res.get("model")
        dspq.put(
            {
                "type": "data-response-end",
                "id": res.get("id"),
                "usage": usage_copy,
            }
        )
    else:
        dspq.put(
            {
                "type": "data-response-end",
                "id": res.get("id"),
                "usage": None,
            }
        )


def anthropic_construct_tool_result_content(result: PythonExecResponse) -> str | list:
    text_output = result.model_dump_json(exclude={"image_attachments"})

    if not result.image_attachments:
        return text_output

    content_blocks: list = []

    content_blocks.append(
        {
            "type": "text",
            "text": f"<text_output>\n{text_output}\n</text_output>\n",
        }
    )

    content_blocks.append(
        {
            "type": "text",
            "text": "<image_output>\n",
        }
    )
    for file, base64_data_url in result.image_attachments:
        content_blocks.append(
            {
                "type": "text",
                "text": f"image path: {file}\n",
            }
        )

        header, b64 = base64_data_url.split(",", 1)
        assert header.startswith("data:"), "Invalid data URL: missing 'data:' prefix"
        assert header.endswith(";base64"), (
            "Invalid data URL header: must end with ';base64'"
        )
        media_type = header[len("data:") : -len(";base64")]
        assert media_type, "Invalid data URL: missing media_type"
        assert b64, "Invalid data URL: missing base64 payload"
        # base64.b64decode(b64, validate=True)

        content_blocks.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": b64,
                },
            }
        )
    content_blocks.append(
        {
            "type": "text",
            "text": "</image_output>\n",
        }
    )

    return content_blocks


def anthropic_run_turn(history: list, turn_number: int):
    step_number = 0
    while True:
        step_number += 1

        dspq.put(
            {
                "type": "start-step",
                "turn_number": turn_number,
                "step_number": step_number,
            }
        )

        res = anthropic_call(history)

        # we don't do streaming for anthropic so we just emit all the DSP events at once here
        anthropic_dsp_write(res)
        dspq.join()

        history.append({"role": "assistant", "content": res["content"]})

        write_history(history)

        if res["stop_reason"] == "tool_use":
            tool_results = []
            for block in res["content"]:
                if block.get("type") == "tool_use":
                    code = (block.get("input") or {}).get("code")
                    assert isinstance(code, str)
                    python_exec_res = python_exec(code=code)
                    tool_result_content = anthropic_construct_tool_result_content(
                        python_exec_res
                    )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.get("id"),
                            "content": tool_result_content,
                        }
                    )
            history.append({"role": "user", "content": tool_results})

        dspq.put(
            {
                "type": "finish-step",
                "turn_number": turn_number,
                "step_number": step_number,
            }
        )

        if res["stop_reason"] == "end_turn":
            dspq.join()

            res_text_blocks = [
                # concat all text
                block.get("text")
                for block in res.get("content")
                if block.get("type") == "text"
            ]
            res_text = "\n".join(res_text_blocks)
            return res_text
        elif res["stop_reason"] == "tool_use":
            pass
        else:
            raise RuntimeError(f"Bad stop_reason: {res['stop_reason']}")


def anthropic_append_user_message(history: list, message: str):
    history.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": message,
                }
            ],
        }
    )


def anthropic_validate_history(history: list):
    # there should be at least 1 message with role "user" and has a "text" content block
    # note that openai uses "input_text" instead of "text" so this check is sufficient to distinguish
    found = False
    for item in history:
        if (
            item["role"] == "user"
            and isinstance(item["content"], list)
            and any(content.get("type") == "text" for content in item["content"])
        ):
            found = True
            break
    if not found:
        raise ValueError("history is unlikely to be anthropic history")


class OpenAIPythonExecArgs(BaseModel):
    code: str = Field(description="The Python code to execute.")


# NOTE(25-10-30-thu): The Python SDK forces us to use pydantic_function_tool.
# Here's how we would do it plainly:
# https://gist.github.com/hzuo/510c26b36c58538750cba7c3c2e21ca8
openai_python_exec_tool = openai.pydantic_function_tool(
    OpenAIPythonExecArgs,
    name="python_exec",
    description=PYTHON_EXEC_TOOL_DESCRIPTION,
)

openai_service_tier: Literal["priority", "default"] | None = None


def openai_call(
    client: openai.OpenAI,
    history: list,
) -> Any:
    global instructions
    global openai_service_tier

    if instructions is None:
        instructions = assemble_system_prompt()

    if openai_service_tier is None:
        if os.environ.get("OPENAI_SERVICE_TIER") == "priority" or sys.stdin.isatty():
            openai_service_tier = "priority"
        else:
            openai_service_tier = "default"

    with client.responses.stream(
        model="gpt-5.1",
        reasoning={"effort": "high", "summary": "detailed"},
        instructions=instructions,
        tools=[openai_python_exec_tool],
        tool_choice="auto",
        input=history,
        include=["reasoning.encrypted_content"],
        parallel_tool_calls=False,
        previous_response_id=None,
        store=False,
        service_tier=openai_service_tier,
        prompt_cache_retention="24h",
    ) as stream:
        current_tool_call_id = None
        for event in stream:
            dspq.put(
                {
                    "type": "data-openai-responses-api-streaming-event-pre",
                    "event_type": getattr(event, "type", None),
                    "event_item_type": (
                        getattr(getattr(event, "item", {}), "type", None)
                    ),
                    "event": event,
                }
            )
            if event.type == "response.created":
                dspq.put(
                    {
                        "type": "data-response-start",
                        "id": event.response.id,
                    }
                )
            elif event.type == "response.in_progress":
                pass
            elif event.type == "response.completed":
                usage = (
                    event.response.usage.model_dump() if event.response.usage else {}
                )
                usage["provider"] = "openai"
                usage["model"] = event.response.model
                dspq.put(
                    {
                        "type": "data-response-end",
                        "id": event.response.id,
                        "usage": usage,
                    }
                )
            elif event.type == "response.output_item.added":
                if event.item.type == "reasoning":
                    dspq.put(
                        {
                            "type": "reasoning-start",
                            "id": event.item.id,
                        }
                    )
                elif event.item.type == "function_call":
                    dspq.put(
                        {
                            "type": "tool-input-start",
                            "toolCallId": event.item.call_id,
                            "toolName": event.item.name,
                        }
                    )
                    current_tool_call_id = event.item.call_id
                elif event.item.type == "message":
                    dspq.put(
                        {
                            "type": "text-start",
                            "id": event.item.id,
                        }
                    )
            elif event.type == "response.output_item.done":
                if event.item.type == "reasoning":
                    dspq.put(
                        {
                            "type": "reasoning-end",
                            "id": event.item.id,
                        }
                    )
                elif event.item.type == "function_call":
                    dspq.put(
                        {
                            "type": "tool-input-end",
                            "id": event.item.call_id,
                        }
                    )
                elif event.item.type == "message":
                    dspq.put(
                        {
                            "type": "text-end",
                            "id": event.item.id,
                        }
                    )
            elif event.type == "response.content_part.added":
                pass
            elif event.type == "response.content_part.done":
                pass
            elif event.type == "response.output_text.delta":
                dspq.put(
                    {
                        "type": "text-delta",
                        "id": event.item_id,
                        "delta": event.delta,
                    }
                )
            elif event.type == "response.output_text.done":
                pass
            elif event.type == "response.reasoning_summary_part.added":
                pass
            elif event.type == "response.reasoning_summary_text.delta":
                dspq.put(
                    {
                        "type": "reasoning-delta",
                        "id": event.item_id,
                        "delta": event.delta,
                    }
                )
            elif event.type == "response.reasoning_summary_text.done":
                pass
            elif event.type == "response.reasoning_summary_part.done":
                pass
            elif event.type == "response.function_call_arguments.delta":
                dspq.put(
                    {
                        "type": "tool-input-delta",
                        "toolCallId": current_tool_call_id,
                        "delta": event.delta,
                    }
                )
            elif event.type == "response.function_call_arguments.done":
                pass
            elif event.type == "response.error":
                dspq.put(
                    {
                        "type": "error",
                        "errorText": f"openai response.error: {event.model_dump_json()}",
                    }
                )
            else:
                dspq.put(
                    {
                        "type": "error",
                        "errorText": f"openai unknown event: {event.model_dump_json()}",
                    }
                )
            dspq.put(
                {
                    "type": "data-openai-responses-api-streaming-event-post",
                    "event_type": getattr(event, "type", None),
                    "event_item_type": (
                        getattr(getattr(event, "item", {}), "type", None)
                    ),
                    "event": event,
                }
            )
        return stream.get_final_response()


# NOTE(25-09-26-fri): This relies on new API surface that OpenAI released on Friday 25-09-26:
# https://x.com/OpenAIDevs/status/1971618905941856495
def openai_construct_function_call_output(result: PythonExecResponse) -> str | list:
    text_output = result.model_dump_json(exclude={"image_attachments"})

    if not result.image_attachments:
        return text_output

    content_blocks = []

    content_blocks.append(
        {
            "type": "input_text",
            "text": f"<text_output>\n{text_output}\n</text_output>\n",
        }
    )

    content_blocks.append(
        {
            "type": "input_text",
            "text": "<image_output>\n",
        }
    )
    for file, base64_data_url in result.image_attachments:
        content_blocks.append(
            {
                "type": "input_text",
                "text": f"image path: {file}\n",
            }
        )
        content_blocks.append(
            {
                "type": "input_image",
                "detail": "high",
                "image_url": base64_data_url,
            }
        )
    content_blocks.append(
        {
            "type": "input_text",
            "text": "</image_output>\n",
        }
    )

    return content_blocks


def openai_run_turn(
    client: openai.OpenAI,
    history: list,
    turn_number: int,
) -> Any:
    step_number = 0
    while True:
        step_number += 1

        dspq.put(
            {
                "type": "start-step",
                "turn_number": turn_number,
                "step_number": step_number,
            }
        )

        final = openai_call(
            client,
            history=history,
        )

        dspq.join()

        history.extend(
            # convert to a plain value that is json-serializable
            # this is exactly what the sdk does internally when we pass history back as input
            openai._utils.transform(
                final.output,
                openai.types.responses.response_input_param.ResponseInputParam,
            )
        )

        write_history(history)

        function_calls = [
            item
            for item in final.output
            if getattr(item, "type", None) == "function_call"
            or (isinstance(item, dict) and item.get("type") == "function_call")
        ]

        if function_calls:
            tool_outputs = []
            for fc in function_calls:
                if fc.name != "python_exec":
                    raise ValueError(f"openai tried to call unknown tool: {fc.name}")

                result = python_exec(fc.parsed_arguments.code)
                output = openai_construct_function_call_output(result)
                wrapper = {
                    "type": "function_call_output",
                    "call_id": fc.call_id,
                    "output": output,
                }
                tool_outputs.append(wrapper)

            history.extend(tool_outputs)

            write_history(history)

        dspq.put(
            {
                "type": "finish-step",
                "turn_number": turn_number,
                "step_number": step_number,
            }
        )

        if not function_calls:
            dspq.join()

            return final.output_text


def openai_append_user_message(history: list, message: str):
    history.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": message,
                }
            ],
        }
    )


def openai_validate_history(history: list):
    # there should be at least 1 message with role "user" and has an "input_text" content block
    # note that anthropic uses "text" instead of "input_text" so this check is sufficient to distinguish
    found = False
    for item in history:
        if (
            item["role"] == "user"
            and isinstance(item["content"], list)
            and any(content.get("type") == "input_text" for content in item["content"])
        ):
            found = True
            break
    if not found:
        raise ValueError("history is unlikely to be openai history")
    openai._models.validate_type(
        type_=openai.types.responses.response_input_param.ResponseInputParam,
        value=history,
    )


GEMINI_MODEL_NAME = "gemini-3-pro-preview"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent"
GEMINI_FUNCTION_DECLARATIONS = [
    {
        "name": "python_exec",
        "description": "Execute Python code in the shared python_exec sandbox and return stdout/stderr.",
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
]
GEMINI_REQUEST_TIMEOUT = 120


def gemini_history_to_contents(history: list) -> list[dict]:
    contents: list[dict] = []
    for item in history:
        parts = item.get("parts")
        if parts is None:
            content = item.get("content")
            if isinstance(content, list):
                parts = content
        if parts is None:
            continue
        contents.append(
            {
                "role": item.get("role") or "user",
                "parts": parts,
            }
        )
    return contents


def gemini_extract_function_calls(candidate: dict) -> list[dict]:
    calls: list[dict] = []
    content = candidate.get("content") or {}
    for part in content.get("parts", []):
        fc = part.get("functionCall")
        if fc:
            calls.append(fc)
    for extra_key in ("functionCalls", "function_calls"):
        maybe = candidate.get(extra_key)
        if isinstance(maybe, list):
            calls.extend(maybe)
    return calls


def gemini_call(history: list) -> dict:
    global instructions
    if instructions is None:
        instructions = assemble_system_prompt()

    api_key = os.environ.get("GEMINI_API_KEY")
    assert api_key, "GEMINI_API_KEY is not set"

    payload: dict[str, Any] = {
        "contents": gemini_history_to_contents(history),
        "tools": [
            {
                "functionDeclarations": GEMINI_FUNCTION_DECLARATIONS,
            }
        ],
        "toolConfig": {
            "functionCallingConfig": {
                "mode": "AUTO",
            }
        },
        "generationConfig": {
            "thinkingConfig": {
                "thinkingLevel": "HIGH",
                "includeThoughts": True,
            }
        },
        "systemInstruction": {
            "parts": [
                {
                    "text": instructions,
                }
            ]
        },
    }

    response = requests.post(
        f"{GEMINI_API_URL}?key={api_key}",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=GEMINI_REQUEST_TIMEOUT,
    )
    if not response.ok:
        dspq.put(
            {
                "type": "error",
                "errorText": f"gemini error! {response.text}",
            }
        )
    response.raise_for_status()
    return response.json()


def gemini_dsp_write(res: dict):
    response_id = res.get("responseId")
    dspq.put(
        {
            "type": "data-response-start",
            "id": response_id,
        }
    )

    candidates = res.get("candidates") or []
    content = {}
    if candidates:
        content = candidates[0].get("content") or {}
    parts = content.get("parts") or []

    for part in parts:
        if part.get("thought"):
            part_id = part.get("thoughtSignature") or str(uuid.uuid4())
            dspq.put(
                {
                    "type": "reasoning-start",
                    "id": part_id,
                }
            )
            text = part.get("text", "")
            if text:
                dspq.put(
                    {
                        "type": "reasoning-delta",
                        "id": part_id,
                        "delta": text,
                    }
                )
            dspq.put(
                {
                    "type": "reasoning-end",
                    "id": part_id,
                }
            )
        elif part.get("functionCall"):
            call = part["functionCall"]
            call_id = (
                call.get("id") or part.get("thoughtSignature") or str(uuid.uuid4())
            )
            dspq.put(
                {
                    "type": "tool-input-start",
                    "toolCallId": call_id,
                    "toolName": call.get("name"),
                }
            )
            args = call.get("args") or {}
            if args:
                dspq.put(
                    {
                        "type": "tool-input-delta",
                        "toolCallId": call_id,
                        "delta": json.dumps(args, indent=2),
                    }
                )
            dspq.put(
                {
                    "type": "tool-input-end",
                    "id": call_id,
                }
            )
        elif "text" in part:
            text_id = str(uuid.uuid4())
            dspq.put(
                {
                    "type": "text-start",
                    "id": text_id,
                }
            )
            dspq.put(
                {
                    "type": "text-delta",
                    "id": text_id,
                    "delta": part.get("text", ""),
                }
            )
            dspq.put(
                {
                    "type": "text-end",
                    "id": text_id,
                }
            )

    usage = res.get("usageMetadata")
    if usage:
        usage_copy = dict(usage)
        usage_copy["provider"] = "gemini"
        usage_copy["model"] = res.get("modelVersion") or GEMINI_MODEL_NAME
    else:
        usage_copy = None

    dspq.put(
        {
            "type": "data-response-end",
            "id": response_id,
            "usage": usage_copy,
        }
    )


def gemini_construct_function_response(result: PythonExecResponse) -> dict:
    response_data = result.model_dump(exclude={"image_attachments"})
    function_response: dict[str, Any] = {
        "functionResponse": {
            "name": "python_exec",
            "response": response_data,
        }
    }

    if result.image_attachments:
        inline_parts = []
        image_refs = []
        for index, (file_path, data_url) in enumerate(result.image_attachments):
            header, b64 = data_url.split(",", 1)
            assert header.startswith("data:"), "Invalid data URL"
            assert header.endswith(";base64"), "Invalid data URL header"
            media_type = header[len("data:") : -len(";base64")]
            display_name = Path(file_path).name or f"python-exec-image-{index}"
            inline_parts.append(
                {
                    "inlineData": {
                        "mimeType": media_type,
                        "data": b64,
                        "displayName": display_name,
                    }
                }
            )
            image_refs.append(
                {
                    "$ref": display_name,
                    "source_path": str(file_path),
                }
            )
        function_response["functionResponse"]["parts"] = inline_parts
        response_data["image_refs"] = image_refs

    return function_response


def gemini_run_turn(history: list, turn_number: int) -> str:
    step_number = 0
    while True:
        step_number += 1
        dspq.put(
            {
                "type": "start-step",
                "turn_number": turn_number,
                "step_number": step_number,
            }
        )

        res = gemini_call(history)

        gemini_dsp_write(res)
        dspq.join()

        candidates = res.get("candidates") or []
        if not candidates:
            dspq.put(
                {
                    "type": "finish-step",
                    "turn_number": turn_number,
                    "step_number": step_number,
                }
            )
            dspq.join()
            raise ValueError("Gemini returned no candidates")

        candidate = candidates[0]
        candidate_content = candidate.get("content") or {}
        parts = candidate_content.get("parts", [])
        role = candidate_content.get("role", "model")

        history.append(
            {
                "role": role,
                "content": parts,
                "parts": parts,
            }
        )
        write_history(history)

        function_calls = gemini_extract_function_calls(candidate)

        if not function_calls:
            dspq.put(
                {
                    "type": "finish-step",
                    "turn_number": turn_number,
                    "step_number": step_number,
                }
            )
            dspq.join()

            text_blocks = [
                part.get("text", "")
                for part in parts
                if part.get("text") and not part.get("thought")
            ]
            return "\n".join(text_blocks).strip()

        response_parts = []
        for call in function_calls:
            args = call.get("args") or {}
            code = args.get("code")
            if not isinstance(code, str):
                continue
            python_exec_result = python_exec(code=code)
            response_parts.append(
                gemini_construct_function_response(python_exec_result)
            )

        if not response_parts:
            dspq.put(
                {
                    "type": "finish-step",
                    "turn_number": turn_number,
                    "step_number": step_number,
                }
            )
            dspq.join()
            raise ValueError(
                "Gemini requested python_exec but no valid code was returned"
            )

        history.append(
            {
                "role": "user",
                "content": response_parts,
                "parts": response_parts,
            }
        )
        write_history(history)

        dspq.put(
            {
                "type": "finish-step",
                "turn_number": turn_number,
                "step_number": step_number,
            }
        )


def gemini_append_user_message(history: list, message: str):
    parts = [
        {
            "text": message,
        }
    ]
    history.append(
        {
            "role": "user",
            "content": parts,
            "parts": parts,
        }
    )


def gemini_validate_history(history: list):
    found_text = False
    for item in history:
        parts = item.get("parts")
        if parts is None:
            content = item.get("content")
            if isinstance(content, list):
                parts = content
                item["parts"] = parts
        if (
            item.get("role") == "user"
            and isinstance(parts, list)
            and any(part.get("text") for part in parts)
        ):
            found_text = True
    if not found_text:
        raise ValueError("history is unlikely to be gemini history")


def get_model_interface():
    # look for a flag that's like -m or --model and get the value
    # it can either be "openai" or "anthropic"
    # if not found, default to "openai"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--model",
        choices=["openai", "anthropic", "sonnet", "haiku", "gemini"],
        default="openai",
    )
    args = parser.parse_args()
    if args.model == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        assert api_key, "OPENAI_API_KEY is not set"
        client = openai.OpenAI(api_key=api_key)

        def run_turn(history: list, turn_number: int) -> Any:
            return openai_run_turn(client, history, turn_number)

        return {
            "model_type": "openai",
            "session_namespace": "personalbot01",
            "validate_history": openai_validate_history,
            "append_user_message": openai_append_user_message,
            "run_turn": run_turn,
        }
    elif args.model == "anthropic" or args.model == "sonnet":
        return {
            "model_type": "anthropic-sonnet",
            "session_namespace": "personalbot02",
            "validate_history": anthropic_validate_history,
            "append_user_message": anthropic_append_user_message,
            "run_turn": anthropic_run_turn,
        }
    elif args.model == "haiku":
        global anthropic_model
        anthropic_model = "claude-haiku-4-5-20251001"
        return {
            "model_type": "anthropic-haiku",
            "session_namespace": "personalbot02",
            "validate_history": anthropic_validate_history,
            "append_user_message": anthropic_append_user_message,
            "run_turn": anthropic_run_turn,
        }
    elif args.model == "gemini":
        return {
            "model_type": "gemini",
            "session_namespace": "personalbot03",
            "validate_history": gemini_validate_history,
            "append_user_message": gemini_append_user_message,
            "run_turn": gemini_run_turn,
        }
    else:
        raise ValueError(f"unknown model: {args.model}")


model_interface = get_model_interface()

SESSION_NAMESPACE = model_interface["session_namespace"]


def new_session_id():
    dt = datetime.datetime.now()
    dt_str = dt.strftime("%y-%m-%d-%H-%M-%S")
    session_uuid = str(uuid.uuid4())
    return f"{SESSION_NAMESPACE}-{dt_str}-{session_uuid}"


session_id = new_session_id()


def write_history(history: list):
    if not history:
        return
    global session_id
    session_file = Path(f"~/.dataland/sessions/{session_id}.json").expanduser()
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(json.dumps(history, indent=2), encoding="utf-8")


class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Any | None = None
    id: int | str | None = None


class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Any | None = None


class JsonRpcResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    result: Any | None = None
    error: JsonRpcError | None = None
    id: int | str | None = None


class RpcGetSessionIdResult(BaseModel):
    session_id: str


class RpcPromptParams(BaseModel):
    prompt: str


class RpcPromptResult(BaseModel):
    response_output_text: str


class RpcPythonExecParams(BaseModel):
    code: str


class RpcPythonExecResult(BaseModel):
    session_id: str
    status: str
    stdout: str
    stderr: str
    image_attachments: list[Tuple[str, str]]


class RpcRunCommandParams(BaseModel):
    command: str


class RpcRunCommandResult(BaseModel):
    session_id: str
    requests: list[JsonRpcRequest]
    responses: list[JsonRpcResponse]


def api_handler(request: JsonRpcRequest, state: dict) -> JsonRpcResponse:
    global session_id
    try:
        if request.method == "get_session_id":
            return JsonRpcResponse(
                result=RpcGetSessionIdResult(session_id=session_id), id=request.id
            )
        if request.method == "prompt":
            try:
                params = RpcPromptParams.model_validate(request.params)
            except Exception as e:
                return JsonRpcResponse(
                    error=JsonRpcError(
                        code=-32602,
                        message=f"Invalid RpcPromptParams: {e}",
                        data=request.params,
                    ),
                    id=request.id,
                )
            turn_number = calc_turn_number(state["history"])
            console.print(f"[dim]<turn_{turn_number}_prompt>[/dim]", highlight=False)
            console.print(
                Syntax(
                    params.prompt,
                    "markdown",
                    background_color="default",
                )
            )
            console.print(f"[dim]</turn_{turn_number}_prompt>[/dim]", highlight=False)
            model_interface["append_user_message"](state["history"], params.prompt)
            write_history(state["history"])
            output_text = model_interface["run_turn"](state["history"], turn_number)
            result = RpcPromptResult(
                session_id=session_id,
                # this output_text value is synthesized by the openai sdk layer via:
                #
                # @property
                # def output_text(self) -> str:
                #     """Convenience property that aggregates all `output_text` items from the `output` list.
                #     If no `output_text` content blocks exist, then an empty string is returned.
                #     """
                #     texts: List[str] = []
                #     for output in self.output:
                #         if output.type == "message":
                #             for content in output.content:
                #                 if content.type == "output_text":
                #                     texts.append(content.text)
                #     return "".join(texts)
                response_output_text=output_text,
            )
            return JsonRpcResponse(result=result, id=request.id)
        elif request.method == "python_exec":
            try:
                params = RpcPythonExecParams.model_validate(request.params)
            except Exception as e:
                return JsonRpcResponse(
                    error=JsonRpcError(
                        code=-32602,
                        message=f"Invalid RpcPythonExecParams: {e}",
                        data=request.params,
                    ),
                    id=request.id,
                )
            result = python_exec(code=params.code)
            result = RpcPythonExecResult(
                session_id=session_id,
                status=result.status,
                stdout=result.stdout,
                stderr=result.stderr,
                image_attachments=result.image_attachments,
            )
            return JsonRpcResponse(result=result, id=request.id)
        elif request.method == "run_command":
            try:
                params = RpcRunCommandParams.model_validate(request.params)
            except Exception as e:
                return JsonRpcResponse(
                    error=JsonRpcError(
                        code=-32602,
                        message=f"Invalid RpcRunCommandParams: {e}",
                        data=request.params,
                    ),
                    id=request.id,
                )
            argv = shlex.split(params.command, posix=True)
            requests, responses = handle_slash_command(state["history"], argv)
            result = RpcRunCommandResult(
                session_id=session_id,
                requests=requests,
                responses=responses,
            )
            return JsonRpcResponse(result=result, id=request.id)
        else:
            return JsonRpcResponse(
                error=JsonRpcError(code=-32601, message="Unknown method", data=request),
                id=request.id,
            )
    except Exception as e:
        return JsonRpcResponse(
            error=JsonRpcError(code=1, message=f"Unexpected error: {e}", data=request),
            id=request.id,
        )


def handle_slash_command(
    history: list, argv: list[str]
) -> tuple[list[JsonRpcRequest], list[JsonRpcResponse]]:
    if not argv:
        raise ValueError("Empty argv")

    command_token = argv[0]
    if command_token.endswith(".md"):
        command_path = Path(command_token).expanduser().resolve()
    else:
        commands_dir = Path(__file__).resolve().parent / "commands"
        command_path = commands_dir / f"{command_token}.md"

    if not command_path.exists():
        raise FileNotFoundError(f"File not found: {command_path}")

    raw_markdown = command_path.read_text(encoding="utf-8")

    class Frontmatter(RootModel[dict[str, Any]]):
        pass

    def parse_frontmatter(markdown: str) -> tuple[Frontmatter, str]:
        frontmatter_pattern = re.compile(
            r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", re.DOTALL
        )
        frontmatter_match = frontmatter_pattern.match(markdown)
        remaining_markdown = markdown

        if not frontmatter_match:
            raise ValueError("Frontmatter not found")

        frontmatter_text = frontmatter_match.group(1)
        raw_yaml = yaml.safe_load(frontmatter_text)
        remaining_markdown = markdown[frontmatter_match.end() :]

        frontmatter = Frontmatter.model_validate(raw_yaml)

        return frontmatter, remaining_markdown

    def parse_args(argv: list[str]) -> dict[str, str]:
        """
        Return a dict of --key value pairs from argv[1:].
        Supports --k v and --k=v. Bare --flag maps to "".
        """
        out: dict[str, str] = {}
        i = 0
        n = len(argv)
        while i < n:
            tok = argv[i]
            if tok == "--":
                break  # stop option parsing
            if tok.startswith("--") and len(tok) > 2:
                key = tok[2:]
                if "=" in key:  # --k=v
                    k, v = key.split("=", 1)
                elif i + 1 < n and not argv[i + 1].startswith("-"):
                    k, v = key, argv[i + 1]  # --k v
                    i += 1
                else:
                    k, v = key, ""  # bare --flag -> ""
                out[k.replace("-", "_")] = v  # last one wins
            # else: ignore short flags/positionals
            i += 1
        return out

    def inject_params(text: str) -> str:
        if not text:
            return text

        result = text
        for name, value in sandbox_globals["command_params"].items():
            result = result.replace(f"{{{{{name}}}}}", value)

        if "{{" in result or "}}" in result:
            unresolved = re.findall(r"\{\{(.*?)\}\}", result)
            if unresolved:
                raise ValueError(
                    "Missing values for parameters: "
                    + ", ".join(sorted(set(unresolved)))
                )
            raise ValueError("Prompt contains unmatched parameter delimiters")

        return result

    frontmatter, markdown_body = parse_frontmatter(raw_markdown)
    arg_dict = parse_args(argv[1:])

    sandbox_globals["command_params"].update(arg_dict)

    page_split_re = re.compile(r"(?m)^\\pagebreak\s*$|<!--\s*(?i:pagebreak)\s*-->")
    raw_pages: list[str] = [page.strip() for page in page_split_re.split(markdown_body)]
    raw_pages: list[str] = [page for page in raw_pages if page]

    def extract_meta_and_body(page: str, page_index: int) -> tuple[dict[str, Any], str]:
        meta_codefence_start = "```yaml META"
        meta_codefence_end = "```"

        page = page.lstrip()
        lines = page.splitlines()
        if not lines or lines[0].strip() != meta_codefence_start:
            raise ValueError(
                f"Page {page_index + 1}: YAML META block is missing header line"
            )

        closing_index = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == meta_codefence_end:
                closing_index = i
                break

        if closing_index is None:
            raise ValueError(
                f"Page {page_index + 1}: YAML META block is missing closing fence"
            )

        meta_lines = lines[1:closing_index]
        after_lines = lines[closing_index + 1 :]

        # Trim marker/newline noise without disturbing indentation that may matter for YAML or markdown body.
        meta_block = "\n".join(meta_lines).rstrip("\r\n")
        after_meta = "\n".join(after_lines).lstrip("\r\n")

        if not meta_block:
            meta_dict: dict[str, Any] = {}
        else:
            parsed = yaml.safe_load(meta_block)
            if parsed is None:
                meta_dict = {}
            elif isinstance(parsed, dict):
                meta_dict = dict(parsed)
            else:
                raise ValueError(
                    f"Page {page_index + 1}: META YAML must deserialize to a mapping"
                )

        return meta_dict, after_meta

    code_block_re = re.compile(r"```(?:python|py)?\s*\n(.*?)(?:\n)?```", re.DOTALL)

    def extract_python_code(page_body: str, page_index: int) -> str:
        match = code_block_re.search(page_body)
        if not match:
            raise ValueError(
                f"Page {page_index + 1}: python_exec/python_prompt page requires a Python code block"
            )
        code_block = match.group(1)
        code_block = textwrap.dedent(code_block).strip()
        if not code_block:
            raise ValueError(
                f"Page {page_index + 1}: Python code block must not be empty"
            )
        return code_block

    def parse_pages():
        parsed_pages = []
        for i, page in enumerate(raw_pages):
            meta, body = extract_meta_and_body(page, i)
            parsed_pages.append((meta, body))
        return parsed_pages

    parsed_pages = parse_pages()

    def check_for_duplicate_ids():
        page_ids = []
        for meta, _ in parsed_pages:
            page_id = meta.get("id")
            if page_id is not None:
                assert isinstance(page_id, str), f"Page id must be a string: {page_id}"
                page_ids.append(page_id)

        duplicate_ids = [
            id for id, count in collections.Counter(page_ids).items() if count > 1
        ]
        if duplicate_ids:
            raise ValueError(f"Duplicate page ids found: {duplicate_ids}")

    check_for_duplicate_ids()

    control_flow_mode = False

    def set_control_flow_mode():
        nonlocal control_flow_mode
        nonlocal parsed_pages

        if not parsed_pages:
            return

        first_meta, first_body = parsed_pages[0]
        if not (
            first_meta.get("kind") == "python_exec" and first_meta.get("id") == "init"
        ):
            return

        # Execute init page
        console.print("[dim]<init_python_exec>[/dim]", highlight=False)
        code = extract_python_code(first_body, 0)
        result = python_exec(code=code)
        console.print("[dim]</init_python_exec>[/dim]", highlight=False)

        if result.status != "ok":
            raise ValueError(f"Init page failed with status: {result.status}")

        if "control_flow_object" in sandbox_globals:
            assert inspect.isgenerator(sandbox_globals["control_flow_object"]), (
                "control_flow_object must be a generator"
            )
            control_flow_mode = True

        parsed_pages.pop(0)  # Remove init page, otherwise it may get executed twice

    set_control_flow_mode()

    def page_to_request(page_index: int) -> JsonRpcRequest:
        meta, body = parsed_pages[page_index]
        meta = dict(meta)
        kind = meta.get("kind", "prompt")

        # Remove "kind" and "id" since we will be merging in the rest of meta into the params
        meta.pop("kind", None)
        meta.pop("id", None)

        if kind not in {"prompt", "python_exec", "store_text"}:
            raise ValueError(f"Page {page_index + 1}: unsupported kind '{kind}'")

        if kind == "prompt":
            prompt_text = body.strip()
            if not prompt_text:
                raise ValueError(
                    f"Page {page_index + 1}: prompt page must not be empty"
                )
            prompt_text = inject_params(prompt_text)
            prompt_text = prompt_text.strip()
            params = {"prompt": prompt_text}
            params.update(meta)
            return JsonRpcRequest(
                jsonrpc="2.0",
                method="prompt",
                params=params,
                id=str(uuid.uuid4()),
            )
        elif kind == "python_exec":
            code = extract_python_code(body, page_index)
            params = {"code": code}
            params.update(meta)
            return JsonRpcRequest(
                jsonrpc="2.0",
                method="python_exec",
                params=params,
                id=str(uuid.uuid4()),
            )
        elif kind == "store_text":
            var = meta.get("var", "stored_text")
            meta.pop("var", None)
            stored_text = inject_params(body)
            stored_text = stored_text.strip()
            params = {"code": f"globals()[{repr(var)}] = {repr(stored_text)}"}
            params.update(meta)
            return JsonRpcRequest(
                jsonrpc="2.0",
                method="python_exec",
                params=params,
                id=str(uuid.uuid4()),
            )
        else:
            raise AssertionError()

    requests: list[JsonRpcRequest] = []
    responses: list[JsonRpcResponse] = []
    state = {"history": history}

    if control_flow_mode:
        while True:
            unique_prefix = "control_flow_next_id_bxjqsmycpwtgpgvz:"
            # get next id from control flow
            console.print("[dim]<control_flow_python_exec>[/dim]", highlight=False)
            result = python_exec(
                code=f'import json; print("{unique_prefix}" + json.dumps(next(control_flow_object, "[STOPITERATION]")))'
            )
            console.print("[dim]</control_flow_python_exec>[/dim]", highlight=False)

            if result.status != "ok":
                raise ValueError(
                    f"Control flow next() failed with status: {result.status}"
                )

            next_id = json.loads(result.stdout.split(unique_prefix)[1].strip())
            if next_id == "[STOPITERATION]":
                break

            # find page with matching id
            found_index = None
            for i, (meta, _) in enumerate(parsed_pages):
                if meta.get("id") == next_id:
                    found_index = i
                    break

            if found_index is None:
                raise ValueError(
                    f"Control flow yielded id but no page has that id: {next_id}"
                )

            # execute page
            request = page_to_request(found_index)
            response = api_handler(request, state)
            requests.append(request)
            responses.append(response)
    else:
        for i, _ in enumerate(parsed_pages):
            request = page_to_request(i)
            response = api_handler(request, state)
            requests.append(request)
            responses.append(response)

    return requests, responses


def calc_turn_number(history: list) -> int:
    turn_number = 1
    for item in history:
        if isinstance(item, dict) and item.get("role") == "user":
            # handles the anthropic case where tool results are also user messages
            # however those tool results should count as part of the assistant turn
            # as far as we're concerned here
            def is_fake_user_turn() -> bool:
                blocks = None
                content_value = item.get("content")
                if isinstance(content_value, list):
                    blocks = content_value
                elif isinstance(item.get("parts"), list):
                    blocks = item["parts"]

                if blocks is None:
                    return False

                if not blocks:
                    return True

                if all(
                    block.get("type") == "tool_result" or block.get("functionResponse")
                    for block in blocks
                ):
                    return True
                return False

            if not is_fake_user_turn():
                turn_number += 1
    return turn_number


def interactive_main():
    printer_thread = threading.Thread(target=dsp_console_print_loop, daemon=True)
    printer_thread.start()

    global session_id

    history: list = []

    console.print(
        Panel.fit(
            f"[green]{session_id}[/green]",
            title="personalbot-new-session",
        )
    )

    edit_target = "edit_prompt"

    key_bindings = prompt_toolkit.key_binding.KeyBindings()

    @key_bindings.add("c-x", "e")
    def _(event):
        nonlocal edit_target
        edit_target = "edit_prompt"
        event.current_buffer.tempfile_suffix = ".md"
        event.current_buffer.open_in_editor(validate_and_handle=True)

    @key_bindings.add("c-x", "h")
    def _(event):
        nonlocal edit_target
        edit_target = "edit_history"
        history_json = json.dumps(history, indent=2) + "\n"
        event.current_buffer.tempfile_suffix = ".json"
        event.current_buffer.insert_text(history_json)
        event.current_buffer.open_in_editor(validate_and_handle=True)

    @key_bindings.add("c-x", "r")
    def _(event):
        nonlocal edit_target
        edit_target = "edit_python"
        event.current_buffer.tempfile_suffix = ".py"
        event.current_buffer.open_in_editor(validate_and_handle=True)

    prompt_toolkit_prompt_session = prompt_toolkit.PromptSession()

    while True:
        try:
            turn_number = calc_turn_number(history)

            edit_target = "edit_prompt"

            user_input = prompt_toolkit_prompt_session.prompt(
                f"prompt{turn_number}> ",
                multiline=False,
                key_bindings=key_bindings,
            ).strip()

            if not user_input.strip():
                continue

            if edit_target == "edit_history":
                # validate first
                history0 = json.loads(user_input)
                model_interface["validate_history"](history0)

                # save the existing history
                old_session_id = session_id
                write_history(history)

                # start a new session with the new history
                history = history0
                session_id = new_session_id()
                write_history(history)

                console.print(
                    Syntax(
                        json.dumps(
                            {
                                "operation": "edit",
                                "old_session_id": old_session_id,
                                "new_session_id": session_id,
                            },
                            indent=2,
                        ),
                        "json",
                        background_color="default",
                    )
                )
                console.print("")
                console.print(
                    Panel.fit(
                        f"[green]{session_id}[/green]",
                        title="personalbot-new-session",
                    )
                )
                console.print("")
                console.print(
                    Syntax(
                        json.dumps(history, indent=2),
                        "json",
                        background_color="default",
                    )
                )
                continue
            elif edit_target == "edit_python":
                python_exec(code=user_input)
                continue
            elif edit_target == "edit_prompt":
                pass
            else:
                assert False

            if not user_input:
                continue
            elif user_input == "/exit" or user_input == "/quit":
                console.print("[yellow]Goodbye![/yellow]", highlight=False)
                break
            elif user_input == "/id":
                console.print(f"[green]{session_id}[/green]", highlight=False)
                continue
            elif user_input == "/fork" or user_input == "/save":
                old_session_id = session_id
                write_history(history)  # save under old session id
                session_id = new_session_id()
                write_history(history)  # also save under new session id
                console.print(
                    Syntax(
                        json.dumps(
                            {
                                "operation": "fork",
                                "old_session_id": old_session_id,
                                "new_session_id": session_id,
                            },
                            indent=2,
                        ),
                        "json",
                        background_color="default",
                    )
                )
                console.print("")
                console.print(
                    Panel.fit(
                        f"[green]{session_id}[/green]",
                        title="personalbot-new-session",
                    )
                )
                continue
            elif user_input.startswith("/continue "):
                arg = user_input.split(" ")[1]

                if arg.startswith("s3://"):
                    assert arg.endswith(".json"), "S3 session file must end with .json"
                    dest_dir = Path("~/.dataland/sessions").expanduser()
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    filename = arg.split("/")[-1]
                    continue_session_file = (dest_dir / filename).resolve()
                    subprocess.run(
                        ["aws", "s3", "cp", arg, str(continue_session_file)],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                elif arg.endswith(".json"):
                    continue_session_file = Path(arg).expanduser().resolve()
                else:
                    continue_session_file = (
                        Path(f"~/.dataland/sessions/{arg}.json").expanduser().resolve()
                    )

                if not continue_session_file.stem.startswith(SESSION_NAMESPACE):
                    console.print(
                        f"[yellow]Warning: Session file does not start with {SESSION_NAMESPACE}: {continue_session_file}[/yellow]"
                    )

                assert continue_session_file.exists(), (
                    f"Session file not found: {continue_session_file}"
                )
                history0 = continue_session_file.read_text(encoding="utf-8")

                history0 = json.loads(history0)
                model_interface["validate_history"](history0)

                # save the existing history
                old_session_id = session_id
                write_history(history)

                # start a new session with the new history
                history = history0
                session_id = new_session_id()
                write_history(history)

                console.print(
                    Syntax(
                        json.dumps(
                            {
                                "operation": "continue",
                                "continue_session_file": str(continue_session_file),
                                "old_session_id": old_session_id,
                                "new_session_id": session_id,
                            },
                            indent=2,
                        ),
                        "json",
                        background_color="default",
                    )
                )
                console.print("")
                console.print(
                    Panel.fit(
                        f"[green]{session_id}[/green]",
                        title="personalbot-new-session",
                    )
                )
                console.print("")
                console.print(
                    Syntax(
                        json.dumps(history, indent=2),
                        "json",
                        background_color="default",
                    )
                )
                continue
            elif user_input.startswith("/run "):
                split = shlex.split(user_input, posix=True)
                argv = split[1:]  # drop the "/run" part
                try:
                    requests, responses = handle_slash_command(history, argv)
                except Exception as e:
                    console.print(f"[red]Custom Slash Command failed: {e}[/red]")
                    console.print_exception()
                    continue
                continue
            elif user_input == "/send":
                pass
            elif user_input.startswith("/"):
                console.print(f"[yellow]Unknown Slash Command: {user_input}[/yellow]")
                continue
            else:
                model_interface["append_user_message"](history, user_input)

            write_history(history)

            model_interface["run_turn"](history, turn_number)
        except KeyboardInterrupt:
            console.print(
                "\n[yellow]Use EOF, '/exit', or '/quit' to end the session.[/yellow]"
            )
        except EOFError:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Uncaught exception: {e}[/red]")
            console.print_exception()


def programmatic_main():
    printer_thread = threading.Thread(target=dsp_console_print_loop, daemon=True)
    printer_thread.start()

    state = {
        "history": [],
    }

    for line in sys.stdin:
        marker = "qAyAry9gaVx2Zwug:"
        if not line.startswith(marker):
            continue
        rest = line[len(marker) :]
        request = JsonRpcRequest.model_validate_json(rest)
        response = api_handler(request, state)
        print(marker + response.model_dump_json(), flush=True)


def main():
    if sys.stdin.isatty():
        interactive_main()
    else:
        programmatic_main()


if __name__ == "__main__":
    main()
