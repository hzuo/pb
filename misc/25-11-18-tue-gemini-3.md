<!-- GUIDE 1 -->

This guide covers building an agentic loop using the **Gemini 3 API** (`gemini-3-pro-preview`). This model introduces strict validation for tool calling and a new requirement called **Thought Signatures** which must be preserved to maintain reasoning capabilities.

We will use **Python 3.13** and the vanilla `requests` library to demonstrate exactly how the raw HTTP protocol works, avoiding the abstraction of client SDKs.

### Prerequisites

-   **Python 3.13** installed.
-   **API Key**: Get one from Google AI Studio.
-   **Library**: `pip install requests`

---

### Key Concepts for Gemini 3

1.  **Thought Signatures**: Gemini 3 generates encrypted reasoning tokens (`thought_signature`) inside the response parts. **You must return these** in your conversation history for the next turn, or the model will lose context and may error out.
2.  **Strict Tool Validation**: If the model calls a function, you *must* provide a `functionResponse` in the next turn.
3.  **Multimodal Tool Results**: You can now return images (or PDFs) as the "result" of a tool call. We do this by sending a `functionResponse` part *alongside* an `inlineData` part in the same turn.

---

### Complete Code Example

Save this as `agent.py`. This script defines a `GeminiAgent` class that handles the loop, tool execution, and image returning.

```python
import os
import json
import base64
import requests
from typing import List, Dict, Any, Optional

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")

MODEL_NAME = "gemini-3-pro-preview"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

# --- Tools Definition ---
# We define two tools: one for weather (text) and one for a camera (image).
TOOLS_SCHEMA = [
    {
        "function_declarations": [
            {
                "name": "get_weather",
                "description": "Get the current weather for a location.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "location": {"type": "STRING", "description": "City and state, e.g. San Francisco, CA"}
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "take_snapshot",
                "description": "Take a photo of the current environment using the security camera.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "camera_id": {"type": "STRING", "description": "The ID of the camera to access"}
                    },
                    "required": ["camera_id"]
                }
            }
        ]
    }
]

class GeminiAgent:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def _call_api(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sends the conversation history to the Gemini 3 REST API."""
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": messages,
            "tools": TOOLS_SCHEMA,
            # 'function_calling_config' is optional but good for forcing behavior if needed
            "tool_config": {
                "function_calling_config": {"mode": "AUTO"}
            }
        }

        url = f"{BASE_URL}?key={API_KEY}"
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"Error API Response: {response.text}")
            response.raise_for_status()

        return response.json()

    def _execute_tool(self, name: str, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes the requested tool and returns a LIST of parts.
        This allows us to return both a functionResponse and inlineData (image) simultaneously.
        """
        print(f"  🛠️  Executing Tool: {name} with args: {args}")

        if name == "get_weather":
            # mimic a weather API
            return [{
                "functionResponse": {
                    "name": name,
                    "response": {"name": name, "content": {"temperature": "72F", "condition": "Sunny"}}
                }
            }]

        elif name == "take_snapshot":
            # mimic taking a photo (generating a simple red pixel dot for demo)
            # In production, this would be your actual image bytes
            # 1x1 red pixel PNG base64
            red_pixel_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

            # Return TWO parts:
            # 1. The structural response (status)
            # 2. The actual image data
            return [
                {
                    "functionResponse": {
                        "name": name,
                        "response": {"name": name, "content": {"status": "success", "timestamp": "2025-11-18T10:00:00Z"}}
                    }
                },
                {
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": red_pixel_b64
                    }
                }
            ]

        else:
            return [{
                "functionResponse": {
                    "name": name,
                    "response": {"error": "Unknown tool"}
                }
            }]

    def chat(self, user_input: str):
        """Main loop for handling user input and agentic tool cycles."""

        # Add user message to history
        self.history.append({
            "role": "user",
            "parts": [{"text": user_input}]
        })

        while True:
            print("\nThinking...")
            response_data = self._call_api(self.history)

            # Gemini 3 returns 'candidates'. We usually take the first one.
            candidate = response_data.get("candidates", [{}])[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            # 1. CRITICAL: Gemini 3 'Thought Signatures'
            # We must preserve the exact parts returned by the model (including thought_signature fields)
            # and add them to our history as the 'model' turn.
            self.history.append(content)

            # Check if the model wants to stop (has text final answer) or call a function
            function_calls = [p for p in parts if "functionCall" in p]

            if not function_calls:
                # No function calls? We are done. Print text response.
                text_parts = [p.get("text", "") for p in parts if "text" in p]
                print(f"🤖 Gemini: {''.join(text_parts)}")
                break

            # 2. Handle Tool Calls (Agentic Loop)
            # We create a new 'function' role message for the next turn
            tool_response_parts = []

            for call in function_calls:
                fc = call["functionCall"]
                fn_name = fc["name"]
                fn_args = fc.get("args", {})

                # Execute and get results (list of parts)
                result_parts = self._execute_tool(fn_name, fn_args)
                tool_response_parts.extend(result_parts)

            # Append the tool results to history as a 'function' response (technically 'user' role in v1beta)
            # In Gemini API, function responses are sent as role='user' but contain functionResponse parts.
            self.history.append({
                "role": "user",
                "parts": tool_response_parts
            })

            # Loop continues... sending the history (with tool results) back to model

# --- Run the Agent ---
if __name__ == "__main__":
    agent = GeminiAgent()

    print("--- Text Tool Test ---")
    agent.chat("What's the weather in Tokyo?")

    print("\n--- Image Tool Test (Advanced) ---")
    agent.chat("Take a picture of the back door and tell me if it looks safe.")
```

---

### Code Breakdown & Advanced Topics

#### 1. Handling `Thought Signatures`
In Gemini 3, the model "thinks" before answering. This thinking process is encoded in a `thought_signature` field inside the JSON `parts` returned by the API.
*   **The Rule**: You do not need to decode this. You simply must ensure that when you append the model's response to your `self.history` list, you include the *entire* object (or at least the full `parts` list containing that field).
*   **In the code**: `self.history.append(content)` does this automatically. If you were to manually construct a new text-only object for the history, you would lose the signature, and the next request would fail with a validation error.

#### 2. The "Image Result" Pattern
Historically, LLM tool calling only supported JSON text results. Gemini 3 supports **multimodal tool outputs**.
*   **The Problem**: A function like `take_snapshot` returns binary image data, not JSON.
*   **The Solution**: In the `_execute_tool` method, we return **two parts** for a single function call:
    1.  `functionResponse`: Contains metadata (status: success, timestamp) to satisfy the strict API requirement that every call gets a response.
    2.  `inlineData`: Contains the base64 encoded image.

The model receives this in the conversation history as: *"I called `take_snapshot`, and the result was `{status: success}` AND [Image]"*. This allows it to "see" the function result.

#### 3. Raw REST Structure
The payload sent to `https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent` looks like this during the tool execution step:

```json
{
  "contents": [
    { "role": "user", "parts": [{ "text": "Take a picture..." }] },
    { "role": "model", "parts": [{ "functionCall": { "name": "take_snapshot", ... }, "thought_signature": "..." }] },
    { "role": "user", "parts": [
        { "functionResponse": { "name": "take_snapshot", "response": { "status": "ok" } } },
        { "inlineData": { "mimeType": "image/png", "data": "..." } }
      ]
    }
  ],
  "tools": [...]
}
```

#### 4. Minimal Dependencies
We used `requests` and standard library `json`/`os`/`base64`. This makes the code portable to any environment (Lambda, Cloud Functions, tiny containers) without the heavy `google-generativeai` SDK, giving you full control over the HTTP implementation.

<!-- GUIDE 2 -->

### **Gemini 3 Agentic Guide: Advanced Tool Loops**

This guide covers how to build a robust agentic loop with **Gemini 3** (`gemini-3-pro-preview`) using Python 3.13 and raw REST calls. It focuses on the new **Thought Signatures** requirement and how to handle complex **Multimodal Function Responses** (mixing text and images).

### **The Core Rules for Gemini 3**

1.  **Thought Signatures are Mandatory**: Gemini 3 "thinks" before it acts. You will see a `thought_signature` field in the model's response. You **must** echo this back in the next turn's history, or the model will crash/hallucinate.
2.  **Multimodal Responses**: You can return images, PDFs, and text *as the result* of a function call.
3.  **Mixed Content**: Yes, you can mix `functionResponse`, `text`, and `inlineData` (images) in a single turn. This allows an agent to say, *"I ran the tool; here is the metadata (JSON) and here is the visual evidence (Image)."*

---

### **Comprehensive Code Example**

This script implements a "Security Agent" that has a camera tool. When asked, it "takes a photo" (generates a dummy image), analyzes it, and returns a mixed response containing:
1.  **Text**: Context about the action.
2.  **Image**: The actual "snapshot".
3.  **FunctionResponse**: The structural result (JSON) to satisfy the API.

#### `agent_gemini3.py`

```python
import os
import json
import requests
import base64
from typing import List, Dict, Any

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3-pro-preview"
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

# --- Tool Definitions ---
TOOLS = [{
    "function_declarations": [
        {
            "name": "inspect_perimeter",
            "description": "Check a specific area of the building. Returns a report and a visual snapshot.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "sector": {"type": "STRING", "description": "The sector to check, e.g., 'North Gate', 'Lobby'"}
                },
                "required": ["sector"]
            }
        }
    ]
}]

class Gemini3Agent:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def _send_request(self, content_payload: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Issues the raw HTTP POST to Gemini."""
        url = f"{BASE_URL}?key={API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": content_payload,
            "tools": TOOLS,
            "tool_config": {"function_calling_config": {"mode": "AUTO"}}
        }

        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code != 200:
            print(f"\n🔥 API Error: {resp.text}")
            resp.raise_for_status()
        return resp.json()

    def _generate_dummy_image(self) -> str:
        """Generates a 1x1 red pixel PNG to simulate a camera snapshot."""
        # In a real app, this would be bytes from a camera or file
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

    def _handle_tool_execution(self, call: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes the tool and constructs a MIXED response:
        Text Context + Function JSON + Image Data
        """
        name = call["name"]
        args = call.get("args", {})
        print(f"  ⚙️  Tool Triggered: {name} ({args})")

        if name == "inspect_perimeter":
            sector = args.get("sector", "Unknown")

            # We construct a list of parts to return to the model.
            # This answers your question: Yes, we can mix them!
            return [
                # Part 1: Text Context (Optional but helpful for reasoning)
                {
                    "text": f"I have successfully accessed the camera feed for {sector}. Encrypted link established."
                },
                # Part 2: The Structural Function Response (Mandatory)
                {
                    "functionResponse": {
                        "name": name,
                        "response": {
                            "status": "secure",
                            "timestamp": "2025-11-18T12:00:00Z",
                            "detected_objects": ["gate", "guard_booth"]
                        }
                    }
                },
                # Part 3: The Visual Evidence (Multimodal Result)
                {
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": self._generate_dummy_image()
                    }
                }
            ]
        return []

    def chat(self, user_prompt: str):
        print(f"\n👤 User: {user_prompt}")

        # Add user message to history
        self.history.append({
            "role": "user",
            "parts": [{"text": user_prompt}]
        })

        while True:
            # 1. Call API
            response = self._send_request(self.history)

            # 2. Extract candidate and content
            candidate = response.get("candidates", [{}])[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            # 3. CRITICAL: Preserve Thought Signatures
            # We explicitly append the FULL model content (including invisible fields like 'thought_signature')
            # to the history. If you manually reconstruct this dict, you WILL break the loop.
            self.history.append(content)

            # 4. Check for Tool Calls
            function_calls = [p["functionCall"] for p in parts if "functionCall" in p]

            if function_calls:
                print("  🧠  Model Thought: (Signature Preserved)")

                # Prepare the response parts list
                # The 'user' role response to a tool call can contain multiple parts
                tool_response_parts = []

                for fc in function_calls:
                    # Execute tool and get its mixed parts (Text + JSON + Image)
                    result_parts = self._handle_tool_execution(fc)
                    tool_response_parts.extend(result_parts)

                # Append the mixed tool response to history
                self.history.append({
                    "role": "user",
                    "parts": tool_response_parts
                })
                # Loop back to send this info to the model...
            else:
                # Final natural language response
                text_ans = "".join([p.get("text", "") for p in parts if "text" in p])
                print(f"🤖 Agent: {text_ans}")
                break

# --- Run ---
if __name__ == "__main__":
    agent = Gemini3Agent()
    agent.chat("Check the North Gate and tell me if you see any issues.")
```

---

### **Deep Dive: The "Mixed" Response Structure**

You asked: *"can functionResponse be mixed? so text, image, text, image, etc."*

**Yes.**
The Gemini API treats the "Tool Output" turn simply as a message from the `user`. This message can contain a list of `parts`. The model uses all of these parts as context to generate its final answer.

Here is exactly what the payload looks like when we return a mixed response:

```json
{
  "role": "user",
  "parts": [
    {
      "text": "I have accessed the camera feed..."
    },
    {
      "functionResponse": {
        "name": "inspect_perimeter",
        "response": { "status": "secure", "lux_level": 450 }
      }
    },
    {
      "inlineData": {
        "mimeType": "image/png",
        "data": "iVBORw0K..."
      }
    },
    {
      "text": "Warning: Low light conditions detected in the corner."
    }
  ]
}
```

#### **Why this works**
1.  **`functionResponse`**: Resolves the pending `functionCall` state on the server.
2.  **`inlineData`**: Provides the raw visual data to the model's multimodal encoder.
3.  **`text`**: Provides "Hinting" or "System Logs" that guide the model's reasoning about the data.

### **Advanced: Gemini 3 "Thinking" & Signatures**

The most common error in Gemini 3 loops is `400 Bad Request: Missing thought_signature`.

*   **What is it?** An encrypted token string hidden inside the `functionCall` part of the model's response.
*   **Where is it?**
    ```json
    // Model Response
    {
      "parts": [
        {
          "functionCall": {
            "name": "inspect_perimeter",
            "args": {...}
          },
          "thought_signature": "A1B2C3D4..." // <--- HIDDEN FIELD
        }
      ]
    }
    ```
*   **How to handle it:**
    Never try to parse the model's response into a new dictionary (e.g., `{"role": "model", "parts": [{"functionCall": ...}]}`).
    **Always** take the entire `candidate['content']` object received from the API and append it directly to your `self.history` list. This ensures the `thought_signature` is preserved perfectly for the next request.

### **Best Practices**

1.  **One Turn, One List**: Even if you execute 3 tools in parallel, send back **one** message with `role: "user"` containing all the `functionResponse` parts for those tools.
2.  **Image Placement**: While you *can* interleave text and images, it is best practice to put the `functionResponse` (JSON) and `inlineData` (Image) adjacent to each other so the model associates the image with that specific tool result.
3.  **Token Management**: Images in tool loops consume tokens. If your agent loops 10 times taking photos, you might hit context limits. Gemini 3 has a huge context window, but latency will increase.

<!-- GUIDE 3 -->

Here’s a full “from scratch” guide for building Gemini-3 agentic tool-calling loops over raw HTTP with `requests` and typed Python 3.13.

I’ll focus on the **Gemini API** (ai.google.dev) with **Gemini 3 Pro Preview** (`gemini-3-pro-preview`), and show how to:

* Define tools (function declarations)
* Detect and execute tool calls
* Feed **function responses** back into the model
* Build a generic **agent loop** (multi-step, multi-tool)
* Return **image results** from tools using Gemini 3’s **multimodal function responses** ([Google Cloud Documentation][1])

---

## 0. Mental model: what “agentic tool calling” looks like

At a high level, a Gemini 3 agent with tools works like this: ([Google AI for Developers][2])

1. You define **function declarations** (`tools.functionDeclarations`), a subset of OpenAPI schema.
2. You send:

   * User prompt(s) as `contents`
   * The tool declarations
   * Optional `toolConfig.functionCallingConfig` (AUTO / ANY / NONE)
3. Gemini 3 returns:

   * Either a **normal answer**, or
   * One or more **`functionCall`** objects (which function to call + JSON arguments)
4. Your code:

   * Maps `functionCall.name` → your Python function
   * Executes it with the provided JSON args
   * Builds a **`functionResponse`** message and appends it to the conversation history
5. You call Gemini again with the updated `contents`, and it **uses the tool results** to continue or finish the task.
6. Repeat until you’re happy (or you hit a max-steps safety guard).

Gemini 3 specifically adds: ([Google AI for Developers][3])

* Better planning for **long-horizon agent loops**
* **Multimodal function responses** (your tools can return images / PDFs that the model can see)
* Streaming arguments for function calls
* Tight integration with **thought signatures** (if you enable “thinking”), which matters for multi-step loops (we’ll design our loop to preserve them automatically).

---

## 1. Minimal HTTP client for Gemini 3 (with `requests` only)

### 1.1. Basic constants

Gemini API REST endpoint format:

```text
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent
```

Examples in the docs use `gemini-2.5-flash`, etc. ([Google AI for Developers][2])
Gemini 3 Pro Preview appears as `gemini-3-pro-preview` in current docs / ecosystem. ([Google Cloud][4])

```python
# gemini_client.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import os
import requests


JSONDict = Dict[str, Any]


@dataclass
class GeminiClient:
    api_key: str
    model: str = "gemini-3-pro-preview"
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    timeout_s: int = 30

    def generate_content(self, body: JSONDict) -> JSONDict:
        """
        Low-level wrapper for POST /models/{model}:generateContent
        """
        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        resp = requests.post(url, headers=headers, json=body, timeout=self.timeout_s)
        resp.raise_for_status()
        return resp.json()
```

Usage:

```python
client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
```

---

## 2. Representing tools and tool results in Python

Gemini’s **function declarations** must follow a limited OpenAPI-ish schema (`type`, `properties`, `required`, `enum`, etc.). ([Google AI for Developers][5])

We’ll build a tiny abstraction:

```python
# tools.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Protocol


JSONDict = Dict[str, Any]


class ToolHandler(Protocol):
    def __call__(self, args: JSONDict) -> "ToolResult": ...


@dataclass
class ToolResult:
    """
    Result of executing a tool.

    - response: JSON-serializable dict Gemini will see in functionResponse.response
    - parts: optional multimodal parts (image/pdf/etc) for Gemini 3's multimodal function responses.
    """
    response: JSONDict
    parts: List[JSONDict] = field(default_factory=list)


@dataclass
class Tool:
    name: str
    description: str
    parameters: JSONDict  # OpenAPI-ish schema
    handler: ToolHandler

    @property
    def function_declaration(self) -> JSONDict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
```

Example of a **simple JSON-only tool**:

```python
def get_current_weather_handler(args: JSONDict) -> ToolResult:
    location = args["location"]
    unit = args.get("unit", "celsius")

    # In a real app: call your weather API here.
    fake_data = {
        "location": location,
        "temperature": 18.3,
        "unit": unit,
        "conditions": "light rain",
    }
    return ToolResult(response=fake_data)


get_current_weather_tool = Tool(
    name="get_current_weather",
    description="Get the current weather for a city.",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name, e.g. 'Boston, MA'",
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit",
            },
        },
        "required": ["location"],
    },
    handler=get_current_weather_handler,
)
```

---

## 3. One-shot function calling via REST

Let’s build the **minimum** end-to-end function calling flow:

1. Send user prompt + tool declaration.
2. Check response for a function call.
3. Run the tool.
4. Send a second request with a `functionResponse`.
5. Get the final natural-language answer.

### 3.1. Extracting function calls from the raw JSON

Per docs, a candidate may expose function calls as either:

* `candidate["functionCalls"]` (especially for parallel calls) ([Google Cloud Documentation][1])
* or as `candidate["content"]["parts"][i]["functionCall"]` (older pattern still shown in Gemini API docs). ([Google AI for Developers][2])

We’ll support both:

```python
# parsing.py
from __future__ import annotations
from typing import Any, Dict, List

JSONDict = Dict[str, Any]


def extract_function_calls(response: JSONDict) -> List[JSONDict]:
    """
    Return a list of functionCall objects from the first candidate.

    FunctionCall shape (per docs):
      {
        "name": "<function_name>",
        "args": { ... JSON object ... },
        # optional: "thoughtSignature": "..." for thinking models
      }
    """
    candidates = response.get("candidates") or []
    if not candidates:
        return []

    candidate = candidates[0]

    # 1) Newer pattern: candidate["functionCalls"]
    function_calls: List[JSONDict] = list(candidate.get("functionCalls") or [])

    # 2) Fallback: scan candidate["content"]["parts"][].functionCall
    content = candidate.get("content") or {}
    for part in content.get("parts", []):
        fc = part.get("functionCall")
        if fc:
            function_calls.append(fc)

    return function_calls
```

### 3.2. Building the request body

```python
from __future__ import annotations

from typing import List
from gemini_client import GeminiClient
from tools import Tool, ToolResult
from parsing import extract_function_calls


def build_contents_from_text(user_text: str) -> List[dict]:
    return [
        {
            "role": "user",
            "parts": [{"text": user_text}],
        }
    ]


def one_shot_function_call_example(
    client: GeminiClient,
    tool: Tool,
    user_prompt: str,
) -> str:
    """
    Single tool, single call, two-round flow:
    - Request 1: prompt + tool declaration -> functionCall
    - Request 2: functionResponse -> final answer
    """
    contents = build_contents_from_text(user_prompt)

    body = {
        "contents": contents,
        "tools": [
            {
                "functionDeclarations": [tool.function_declaration],
            }
        ],
        # Optional: nudge model to use tools but not fully force it
        "toolConfig": {
            "functionCallingConfig": {
                "mode": "AUTO"  # or "ANY" to force, "NONE" to disable tools
            }
        },
    }

    first_response = client.generate_content(body)
    function_calls = extract_function_calls(first_response)

    if not function_calls:
        # Model answered directly; just return its text.
        return first_response["candidates"][0]["content"]["parts"][0].get(
            "text", ""
        )

    # Take first function call
    fc = function_calls[0]
    fn_name: str = fc["name"]
    fn_args: dict = fc.get("args", {})

    if fn_name != tool.name:
        raise ValueError(f"Unexpected function name: {fn_name}")

    tool_result: ToolResult = tool.handler(fn_args)

    # Append model's tool call message to history (important for thought signatures).
    contents.append(first_response["candidates"][0]["content"])

    # Build functionResponse Content
    func_response_content = {
        "role": "user",  # Gemini/Vertex docs accept 'user' here for functionResponse messages
        "parts": [
            {
                "functionResponse": {
                    "name": tool.name,
                    "response": tool_result.response,
                }
            }
        ],
    }
    contents.append(func_response_content)

    # Second call: give model the tool result so it can answer user
    second_body = {
        "contents": contents,
        "tools": [
            {
                "functionDeclarations": [tool.function_declaration],
            }
        ],
    }

    final_response = client.generate_content(second_body)
    # Simple text extraction
    parts = final_response["candidates"][0]["content"]["parts"]
    text_chunks = [p.get("text", "") for p in parts if "text" in p]
    return "".join(text_chunks).strip()
```

Usage:

```python
if __name__ == "__main__":
    import os
    from tools import get_current_weather_tool

    client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
    answer = one_shot_function_call_example(
        client,
        tool=get_current_weather_tool,
        user_prompt="What's the weather in Boston in celsius?",
    )
    print(answer)
```

---

## 4. A reusable agent loop (multi-tool, multi-step)

Now let’s generalize this into a small **agent framework** for Gemini 3:

* Maintains a `contents` conversation history.
* Supports **multiple tools**.
* Handles **multiple function calls per turn**.
* Limits number of tool rounds to avoid infinite loops.

### 4.1. The agent harness

```python
# agent.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from gemini_client import GeminiClient
from tools import Tool, ToolResult
from parsing import extract_function_calls


JSONDict = Dict[str, Any]


@dataclass
class GeminiAgent:
    client: GeminiClient
    tools: Mapping[str, Tool]
    system_instruction: Optional[str] = None
    max_tool_round_trips: int = 5

    def _tool_declarations(self) -> List[JSONDict]:
        return [t.function_declaration for t in self.tools.values()]

    def _build_initial_contents(self, user_prompt: str) -> List[JSONDict]:
        contents: List[JSONDict] = []
        if self.system_instruction:
            contents.append(
                {
                    "role": "user",  # systemInstruction can also be separate; we keep it simple.
                    "parts": [{"text": self.system_instruction}],
                }
            )
        contents.append(
            {
                "role": "user",
                "parts": [{"text": user_prompt}],
            }
        )
        return contents

    def _build_request_body(self, contents: List[JSONDict]) -> JSONDict:
        return {
            "contents": contents,
            "tools": [
                {
                    "functionDeclarations": self._tool_declarations(),
                }
            ],
            "toolConfig": {
                "functionCallingConfig": {
                    # AUTO = let model choose between natural answer and tools.
                    # ANY  = force function calling (useful for structured pipelines).
                    "mode": "AUTO",
                }
            },
            # Optional: generationConfig for temperature, thinking, etc.
            # "generationConfig": {
            #     "temperature": 0.2,
            # },
        }

    def run(self, user_prompt: str) -> str:
        """
        Run an agentic loop until:
        - The model responds without any tool calls, or
        - max_tool_round_trips is reached.
        """
        contents = self._build_initial_contents(user_prompt)
        tool_rounds = 0

        while True:
            body = self._build_request_body(contents)
            response = self.client.generate_content(body)
            candidates = response.get("candidates") or []
            if not candidates:
                return "No response from model."

            candidate = candidates[0]
            function_calls = extract_function_calls(response)

            if not function_calls:
                # No tool calls → final answer
                parts = candidate["content"]["parts"]
                text_chunks = [p.get("text", "") for p in parts if "text" in p]
                return "".join(text_chunks).strip()

            # Guard: we have tool calls
            tool_rounds += 1
            if tool_rounds > self.max_tool_round_trips:
                return "[tool limit reached]"

            # 1. Append the model's 'tool call' message (keeps thought signatures etc.)
            contents.append(candidate["content"])

            # 2. Execute each requested tool call (parallel tool calling)
            function_response_parts: List[JSONDict] = []
            for fc in function_calls:
                name: str = fc["name"]
                args: JSONDict = fc.get("args", {})

                tool = self.tools.get(name)
                if tool is None:
                    # Unknown tool → send an error-like response back
                    tool_result = ToolResult(
                        response={"error": f"Unknown tool: {name}"}
                    )
                else:
                    # You probably want robust validation here in production.
                    tool_result = tool.handler(args)

                fr: JSONDict = {
                    "name": name,
                    "response": tool_result.response,
                }
                if tool_result.parts:
                    # Gemini 3 multimodal function responses:
                    # attach the multimodal parts to the functionResponse.
                    fr["parts"] = tool_result.parts

                function_response_parts.append({"functionResponse": fr})

            # 3. Add tool responses as a new Content turn
            contents.append(
                {
                    # Gemini docs tend to use 'user' here, Vertex examples sometimes
                    # use 'tool'. Either works; 'user' is the canonical Gemini API example. :contentReference[oaicite:8]{index=8}
                    "role": "user",
                    "parts": function_response_parts,
                }
            )
            # Loop continues: the next iteration will call the model again with updated contents.
```

Usage:

```python
if __name__ == "__main__":
    import os
    from tools import get_current_weather_tool

    client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
    agent = GeminiAgent(
        client=client,
        tools={get_current_weather_tool.name: get_current_weather_tool},
        system_instruction=(
            "You are a travel assistant. "
            "Always call tools for up-to-date weather before answering."
        ),
    )

    print(
        agent.run("I'm going to Boston and Chicago tomorrow, what should I pack?")
    )
```

This is now a **general agentic loop**:

* Gemini 3 decides **which tools** to use and **in which order**.
* It can make **multiple parallel tool calls** in one turn (we handle that).
* We maintain full `contents` including the model’s intermediate messages, which is important for **thinking / thought signatures** in Gemini 3. ([Google Cloud Documentation][1])

---

## 5. Controlling tool behavior (AUTO vs ANY vs NONE)

Gemini tool behavior is controlled by `toolConfig.functionCallingConfig.mode` with values: ([Firebase][6])

* `"AUTO"` – default; model decides whether to call tools or answer naturally.
* `"ANY"` – **forced tool calling**: model must output a function call (or calls).
* `"NONE"` – model is forbidden from calling tools (equivalent to no tools).

You can also restrict tools by name:

```python
"toolConfig": {
    "functionCallingConfig": {
        "mode": "ANY",
        "allowedFunctionNames": ["get_current_weather", "get_flights"],
    }
}
```

In our `GeminiAgent._build_request_body`, you can uncomment/change accordingly:

```python
"toolConfig": {
    "functionCallingConfig": {
        "mode": "ANY",
        "allowedFunctionNames": list(self.tools.keys()),
    }
}
```

**Warning:** with `ANY`, Gemini will *keep* trying to call tools unless your tool results + prompts strongly signal “we’re done.” Always keep a **max rounds** guard (`max_tool_round_trips`) to avoid infinite loops, especially in early Gemini 3 preview where people have observed this exact failure mode. ([Google AI Developers Forum][7])

---

## 6. Advanced: image results from tools (multimodal function responses)

This is the piece you explicitly asked for: **how do I pass image results from a tool back into Gemini 3** so it can reason over the image?

Gemini 3 Pro lets you include **images and documents inside `functionResponse` parts**, using either `inlineData` (base64) or `fileData` (URI). ([Google Cloud Documentation][1])

### 6.1. The JSON shape

From the Vertex AI function-calling docs (applies to Gemini 3 Pro): ([Google Cloud Documentation][1])

* In `contents`, you send a `Content` like:

```jsonc
{
  "role": "user",
  "parts": [
    {
      "functionResponse": {
        "name": "get_image",
        "response": {
          "image_ref": { "$ref": "wakeupcat.jpg" }
        },
        "parts": [
          {
            "fileData": {
              "displayName": "wakeupcat.jpg",
              "mimeType": "image/jpeg",
              "fileUri": "gs://cloud-samples-data/vision/label/wakeupcat.jpg"
            }
          }
        ]
      }
    }
  ]
}
```

Key ideas:

* Each multimodal **part** is nested inside `functionResponse.parts`.
* Your **structured `response` JSON** can refer to media via `{"$ref": "<displayName>"}`.
* `displayName` must be unique and can be referenced exactly once in `response`.

You may also use `inlineData` if you want to embed bytes instead of a URI.

### 6.2. A tool that returns a product image

Say we have a tool that looks up an order item and returns an image URL + mime type:

```python
# image_tools.py
from __future__ import annotations

import base64
from typing import Dict, Any
from tools import Tool, ToolResult

JSONDict = Dict[str, Any]


def get_order_image_handler(args: JSONDict) -> ToolResult:
    item_name: str = args["item_name"]

    # Real implementation: query your DB or storage.
    # Here we fake a hosted URL.
    image_url = f"https://example.com/images/{item_name.replace(' ', '_')}.png"
    mime_type = "image/png"

    display_name = f"{item_name}.png"

    # The 'response' JSON refers to this image by $ref
    response = {
        "image_ref": {"$ref": display_name},
        "metadata": {
            "item_name": item_name,
            "source": "product-catalog",
        },
    }

    # The 'parts' list contains the actual media reference.
    parts = [
        {
            "fileData": {
                "displayName": display_name,
                "mimeType": mime_type,
                "fileUri": image_url,
            }
        }
    ]

    return ToolResult(response=response, parts=parts)


get_order_image_tool = Tool(
    name="get_order_image",
    description="Retrieve the primary product image for an order item.",
    parameters={
        "type": "object",
        "properties": {
            "item_name": {
                "type": "string",
                "description": "The item description, e.g. 'green shirt'",
            }
        },
        "required": ["item_name"],
    },
    handler=get_order_image_handler,
)
```

Now plug this into our `GeminiAgent` from before:

```python
from gemini_client import GeminiClient
from agent import GeminiAgent
from image_tools import get_order_image_tool

client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"])
agent = GeminiAgent(
    client=client,
    tools={get_order_image_tool.name: get_order_image_tool},
    system_instruction=(
        "You are an order support assistant. "
        "If the user asks to *see* an item, call get_order_image."
    ),
)

print(agent.run("Show me the green shirt I ordered last month."))
```

Flow:

1. Model decides to call `get_order_image(item_name="green shirt")`.
2. Our handler returns a `ToolResult` with:

   * `response.image_ref = {"$ref": "green shirt.png"}`
   * `parts[0].fileData.displayName = "green shirt.png"` + `fileUri`.
3. We construct a `functionResponse` with those fields and send it back.
4. On the next round, Gemini 3 *has the image* in context and can:

   * Describe it,
   * Compare multiple images,
   * Use it in further reasoning (e.g., “does this match the size chart?”).

### 6.3. Using inline base64 instead of URLs

If your tool returns raw bytes (e.g., screenshot service), use `inlineData` instead of `fileData`:

```python
def screenshot_handler(args: JSONDict) -> ToolResult:
    url: str = args["url"]
    # bytes_png = ... generate screenshot bytes ...
    bytes_png = b"..."

    display_name = f"screenshot-{hash(url)}.png"
    b64 = base64.b64encode(bytes_png).decode("ascii")

    response = {
        "image_ref": {"$ref": display_name},
        "url": url,
    }
    parts = [
        {
            "inlineData": {
                "displayName": display_name,
                "mimeType": "image/png",
                "data": b64,
            }
        }
    ]
    return ToolResult(response=response, parts=parts)
```

Everything else in the agent loop stays the same.

---

## 7. Thinking & thought signatures (for “deep” agentic loops)

Gemini 3 and 2.5 have **thinking modes** and **thought signatures**. For Gemini 3, you control a `thinking_level` (`low`/`high`), and the model can emit separate “thought” parts that summarize its internal reasoning. ([Google AI for Developers][3])

Key implications for tool loops (based on the official docs): ([Google Cloud Documentation][1])

* When thinking is enabled, the model includes **thought signatures** in its responses.
* If you want the model to maintain coherent reasoning over many tool steps, you must:

  * **Return the entire `candidate["content"]`** as part of the next request (we already do this by `contents.append(candidate["content"])`).
  * Never merge or strip parts that contain thought signatures.

So our `GeminiAgent` is already “future-proof” for thinking models because it:

* Takes the whole `candidate["content"]` and appends it as a new turn in `contents`.
* Doesn’t inspect or mutate the inner parts (beyond reading function calls separately via `extract_function_calls`).

If you want to explicitly enable thinking in the direct Gemini API, you’d add a `thinkingConfig` either in `generationConfig` or as a top-level field, depending on final REST spec (the docs keep evolving there), e.g.:

```python
"generationConfig": {
    "thinkingConfig": {
        "thinkingLevel": "high",      # Gemini 3
        "includeThoughts": True,
    }
}
```

Check the **Thinking** docs for the precise field layout; it mirrors the OpenAI compatibility mapping you saw (`reasoning_effort` → `thinking_level`). ([Google AI for Developers][8])

---

## 8. Practical tips & gotchas

### 8.1. Schema quality matters

Function declarations are the only thing the model sees about your tools’ signatures. Per docs, you’ll get best results if: ([Firebase][6])

* `name` is descriptive but short (`get_order_image`, not `tool1`).
* `description` is explicit about when to use the tool.
* `parameters` include clear property `description`s and realistic `enum`s.
* You avoid unsupported OpenAPI fields like `oneOf`, `maximum`, `default`.

### 8.2. Always guard loops

* Hard-limit `max_tool_round_trips`.
* Optionally track a **budget** (wall-clock time, token usage, or number of external API calls) and stop if exceeded.
* In “ANY” mode, consider prompting the model to **summarize and stop** after tools succeed.

### 8.3. Validate tool arguments

Never treat `fc["args"]` as trusted input:

* Validate required fields and ranges.
* For actions that mutate state (payments, email sending…), insert your own business-logic checks & approvals.

### 8.4. Observability

* Log `request_body`, `response`, and tool calls (with PII scrubbing) so you can debug “why did the agent do that?”.
* Watch for:

  * “Tool spam” (repeated calls that don’t change results)
  * Hallucinated tool names (handle gracefully with error toolResponse like we did).

### 8.5. When to use Gemini’s *built-in* tools vs your own

Gemini API also offers built-in tools like: Google Search, Google Maps, File Search, Code Execution, etc. ([Google AI for Developers][2])

* For **web / search grounding**, prefer the built-ins (`google_search` / `File Search`) instead of writing your own RAG stack.
* For business-specific actions (CRUD on your DB, internal APIs, third-party SaaS), use **custom function tools** like we’ve implemented here.

---

## 9. Where to go deeper

If you want to push this further:

* **Parallel & compositional function calling** – the same structure we used supports multiple tools per turn; docs have more patterns (like multi-step chains) you can follow. ([Google AI for Developers][2])
* **Streaming function-call arguments** – for Gemini 3 Pro you can set `streamFunctionCallArguments: true` in `toolConfig.functionCallingConfig` when calling `streamGenerateContent`, and start executing tools before the args are fully generated. ([Google Cloud Documentation][9])
* **File Search tool** – fully-managed RAG for grounding tools that work on your documents, now a first-class Gemini API feature. ([blog.google][10])

---

If you tell me more about your concrete use case (e.g. “support bot that calls Shopify / internal order APIs” or “energy queue agent that reads grid models and spreadsheets”), I can adapt this skeleton into a domain-specific agent with realistic tools and prompts.

[1]: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling "Introduction to function calling  |  Generative AI on Vertex AI  |  Google Cloud Documentation"
[2]: https://ai.google.dev/gemini-api/docs/function-calling "Function calling with the Gemini API  |  Google AI for Developers"
[3]: https://ai.google.dev/gemini-api/docs/gemini-3?utm_source=chatgpt.com "Gemini 3 Developer Guide | Gemini API"
[4]: https://console.cloud.google.com/vertex-ai/publishers/google/model-garden/gemini-3-pro-preview?utm_source=chatgpt.com "Gemini 3 Pro Preview – Vertex AI"
[5]: https://ai.google.dev/gemini-api/docs/function-calling?utm_source=chatgpt.com "Function calling with the Gemini API | Google AI for Developers"
[6]: https://firebase.google.com/docs/ai-logic/function-calling?utm_source=chatgpt.com "Function calling using the Gemini API | Firebase AI Logic"
[7]: https://discuss.ai.google.dev/t/infinite-tool-call-loop-when-setting-function-calling-config-to-any-mode/97307?utm_source=chatgpt.com "Infinite tool call loop when setting function_calling_config to ..."
[8]: https://ai.google.dev/gemini-api/docs/openai "OpenAI compatibility  |  Gemini API  |  Google AI for Developers"
[9]: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling?utm_source=chatgpt.com "Introduction to function calling | Generative AI on Vertex AI"
[10]: https://blog.google/technology/developers/file-search-gemini-api/?utm_source=chatgpt.com "Introducing the File Search Tool in Gemini API"

<!-- GUIDE 4 -->

Short answer: **yes and no, depending on *where* you’re mixing things.**

---

## 1. At the *message* level (`Content.parts`) → yes

For a normal Gemini message, `Content.parts` is an array of `Part`, and each `Part` can be:

* `text`
* `inlineData` (bytes for image / audio / video)
* `fileData` (URI-based image / doc / etc.)
* `functionCall`
* `functionResponse`
  …etc. ([Google Cloud][1])

So this is totally valid:

```jsonc
{
  "role": "user",
  "parts": [
    { "text": "Here is the first image:" },
    { "fileData": { "mimeType": "image/png", "fileUri": "gs://bucket/a.png" } },
    { "text": "And another one:" },
    { "fileData": { "mimeType": "image/png", "fileUri": "gs://bucket/b.png" } }
  ]
}
```

That’s **text → image → text → image** and is exactly how you send multimodal prompts. ([Scribd][2])

You can likewise have multiple `parts` in a *tool-response message*:

```jsonc
{
  "role": "user",
  "parts": [
    { "functionResponse": { ... } },
    { "functionResponse": { ... } }
  ]
}
```

(i.e., multiple tool results in one turn).

---

## 2. Inside `functionResponse.parts[]` → *only media*, not text

The confusing bit is **inside** the `functionResponse` object itself.

A `functionResponse` has this shape: ([Google Cloud][1])

```jsonc
{
  "name": "your_tool",
  "response": { /* arbitrary JSON */ },
  "parts": [ { /* FunctionResponsePart */ }, ... ]
}
```

And each `FunctionResponsePart` is **media-only**:

```jsonc
{
  "inlineData": { /* FunctionResponseBlob */ }
  // or
  "fileData": { /* FunctionResponseFileData */ }
}
```

No `text` field exists on `FunctionResponsePart` – the union is just `inlineData | fileData`. ([Google Cloud][1])

So:

* ✅ You **can** have multiple media parts, in any order, e.g.:

  ```jsonc
  "parts": [
    { "inlineData": { "mimeType": "image/png", "data": "..." } },
    { "fileData":   { "mimeType": "image/jpeg", "fileUri": "..." } },
    { "inlineData": { "mimeType": "application/pdf", "data": "..." } }
  ]
  ```

* ❌ You **can’t** directly do `text, image, text, image` *inside* `functionResponse.parts`, because those parts only support media, not text.

Instead, you do:

* Text / structure in `functionResponse.response` (JSON), possibly referring to media via `$ref` + `displayName`. ([Google Cloud Documentation][3])
* Media blobs/URIs in `functionResponse.parts[]`.

Example pattern:

```jsonc
{
  "role": "user",
  "parts": [
    {
      "functionResponse": {
        "name": "get_gallery",
        "response": {
          "items": [
            "First image caption",
            { "$ref": "img1" },
            "Second image caption",
            { "$ref": "img2" }
          ]
        },
        "parts": [
          {
            "inlineData": {
              "mimeType": "image/png",
              "data": "...base64...",
              "displayName": "img1"
            }
          },
          {
            "fileData": {
              "mimeType": "image/jpeg",
              "fileUri": "https://example.com/img2.jpg",
              "displayName": "img2"
            }
          }
        ]
      }
    }
  ]
}
```

From Gemini’s POV:

* It sees **structured text/metadata** in `response.items` (`"First image caption"`, `"Second image caption"`)
* It sees **media** in `parts[]` (`img1`, `img2`)
* It can reason over both together.

If *your UI* wants to literally render text → image → text → image, you just interpret that `items` array on the client side.

---

### TL;DR

* **Yes**: At the outer `Content.parts` level, you can freely alternate text, images, and functionResponses.
* **No**: Inside `functionResponse.parts`, you can’t interleave text and media; that array is media-only (`inlineData` / `fileData`). Put text / structure in `functionResponse.response` JSON and use `$ref` to tie it to the media parts.

If you describe the exact structure you want for UI rendering, I can sketch a concrete JSON schema + example functionResponse for it.

[1]: https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1beta1/Content "Content  |  Generative AI on Vertex AI  |  Google Cloud Documentation"
[2]: https://www.scribd.com/document/803988658/Generate-content-with-the-Gemini-Enterprise-API-Generative-AI-on-Vertex-AI-Google-Cloud?utm_source=chatgpt.com "Generate Content With The Gemini Enterprise API"
[3]: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/function-calling?utm_source=chatgpt.com "Introduction to function calling | Generative AI on Vertex AI"
