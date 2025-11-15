import copy
from typing import Any, Callable, Literal

import requests


class ClaudeAgent:
    def __init__(
        self,
        *,
        api_key: str,
        api_url: str = "https://api.anthropic.com/v1/messages",
        model: Literal["claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001"] = "claude-haiku-4-5-20251001",
        thinking_budget_tokens: int = 10_000,
        max_tokens: int = 4_000,
        disable_parallel_tool_use: bool = True,
        progress_cb: Callable[[dict], Any] = lambda x: None,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.system_prompt = None
        self.messages = []
        self.model = model
        self.thinking_budget_tokens = thinking_budget_tokens
        self.max_tokens = max_tokens
        self.tools = []
        self.tool_handlers = {}
        self.disable_parallel_tool_use = disable_parallel_tool_use
        self.progress_cb = progress_cb

    def set_system_prompt(self, system_prompt: str):
        self.system_prompt = system_prompt

    def set_messages(self, messages: list[dict]):
        self.messages = messages

    def add_tool(self, tool_definition: dict, handler: Callable[[dict], str | list]):
        assert tool_definition["name"]
        assert tool_definition["description"]
        assert tool_definition["input_schema"]
        self.tools.append(tool_definition)
        self.tool_handlers[tool_definition["name"]] = handler

    def _call_api(self) -> dict:
        assert self.system_prompt
        assert self.messages

        headers = {
            "content-type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "interleaved-thinking-2025-05-14",
        }

        messages2 = copy.deepcopy(self.messages)
        for message in reversed(messages2):
            if message["role"] == "user":
                assert isinstance(message["content"], list)
                assert len(message["content"]) > 0
                assert isinstance(message["content"][-1], dict)
                message["content"][-1]["cache_control"] = {"type": "ephemeral", "ttl": "5m"}
                break  # only add to the latest one
        req = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "tools": self.tools,
            "tool_choice": {
                "type": "auto",
                "disable_parallel_tool_use": self.disable_parallel_tool_use,
            },
            "system": [
                {
                    "type": "text",
                    "text": self.system_prompt,
                    # always cache system prompt with 1h
                    "cache_control": {"type": "ephemeral", "ttl": "1h"},
                }
            ],
            "messages": messages2,
        }
        if self.thinking_budget_tokens > 0:
            req["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.thinking_budget_tokens,
            }

        self.progress_cb(
            {
                "type": "api_req",
                "req": req,
                "messages": self.messages,
            }
        )

        res = requests.post(self.api_url, headers=headers, json=req)
        if not res.ok:
            print(f"anthropic error! {res.text}")
        res.raise_for_status()
        return res.json()

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        if tool_name not in self.tool_handlers:
            return f"Error: Tool '{tool_name}' not found"
        return self.tool_handlers[tool_name](tool_input)

    def run(self, user_message: str) -> str:
        self.messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_message,
                    }
                ],
            }
        )
        self.progress_cb(
            {
                "type": "new_user_turn",
                "user_message": user_message,
                "messages": self.messages,
            }
        )

        while True:
            res = self._call_api()

            self.messages.append({"role": "assistant", "content": res["content"]})
            self.progress_cb(
                {
                    "type": "api_res",
                    "res": res,
                    "messages": self.messages,
                }
            )

            if res["stop_reason"] == "end_turn":
                res_text_blocks = [
                    # grab all text
                    block.get("text")
                    for block in res.get("content")
                    if block.get("type") == "text"
                ]
                res_text = "\n".join(res_text_blocks)
                return res_text
            elif res["stop_reason"] == "tool_use":
                tool_results = []
                for block in res["content"]:
                    if block["type"] == "tool_use":
                        tool_res = self._execute_tool(block["name"], block["input"])
                        tool_result = {
                            "type": "tool_result",
                            "tool_use_id": block["id"],
                            "content": tool_res,
                        }
                        tool_results.append(tool_result)
                        self.progress_cb(
                            {
                                "type": "got_tool_result",
                                "tool_use_block": block,
                                "tool_result_block": tool_result,
                                "messages": self.messages,
                            }
                        )
                self.messages.append({"role": "user", "content": tool_results})
                self.progress_cb(
                    {
                        "type": "return_tool_results",
                        "tool_results": tool_results,
                        "messages": self.messages,
                    }
                )
            else:
                raise RuntimeError(f"Bad stop_reason: {res['stop_reason']}")
