---
filename: 2025-12-22-22-41-23-gemini-image-generation-api-gemini3proimagepreview
timestamp: '2025-12-22T22:41:23.168857+00:00'
title: Gemini Image Generation API (gemini-3-pro-image-preview)
---

# Gemini Image Generation API (gemini-3-pro-image-preview)

Google's `gemini-3-pro-image-preview` model (codename "Nano Banana Pro") generates and edits images via the standard `generateContent` endpoint. This is the best image generation model Google currently offers via API.

## Endpoint and Authentication

```bash
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent
```

Authentication via `x-goog-api-key` header.

## Quick Start: Self-Contained curl

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [{"text": "Create a cartoon illustration of a yellow rubber duck floating on blue water."}]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {
        "aspectRatio": "1:1",
        "imageSize": "1K"
      }
    }
  }' | jq -r '.candidates[0].content.parts[] | select(.inlineData) | .inlineData.data' | base64 -d > output.jpg
```

## Critical: responseModalities is Required

Without `responseModalities` including `"IMAGE"`, the model returns only text. Always include:

```json
"generationConfig": {
  "responseModalities": ["TEXT", "IMAGE"]
}
```

Options:
- `["TEXT", "IMAGE"]` - Returns explanatory text + image
- `["IMAGE"]` - Returns image only (no text parts)

## Image Configuration Options

```json
"imageConfig": {
  "aspectRatio": "16:9",
  "imageSize": "2K"
}
```

| Parameter | Values | Default |
|-----------|--------|---------|
| `aspectRatio` | `"1:1"`, `"2:3"`, `"3:2"`, `"3:4"`, `"4:3"`, `"4:5"`, `"5:4"`, `"9:16"`, `"16:9"`, `"21:9"` | `"1:1"` |
| `imageSize` | `"1K"`, `"2K"`, `"4K"` | `"1K"` |

**Important**: Use uppercase `"K"` (not `"2k"`).

Token consumption: ~1200 tokens for 1K/2K, ~2000 tokens for 4K.

## Response Structure

Images return as base64-encoded data in `inlineData`. **Check `mimeType` - the API returns JPEG despite docs claiming PNG.**

```json
{
  "candidates": [{
    "content": {
      "role": "model",
      "parts": [
        {
          "inlineData": {
            "mimeType": "image/jpeg",
            "data": "/9j/4AAQSkZJRg..."
          },
          "thoughtSignature": "Er..."
        }
      ]
    },
    "finishReason": "STOP"
  }],
  "usageMetadata": {
    "promptTokenCount": 17,
    "candidatesTokenCount": 1196,
    "totalTokenCount": 1239
  }
}
```

## Python Helper for API Calls

```python
import requests
import base64

API_KEY = "your-api-key"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent"

def call_gemini_image(request_body: dict, timeout: int = 180) -> dict:
    response = requests.post(
        BASE_URL,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY,
        },
        json=request_body,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()

def save_image(result: dict, filepath: str) -> str | None:
    """Save image from response, using correct extension from mimeType."""
    parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [])

    for part in parts:
        if "inlineData" in part:
            mime_type = part["inlineData"].get("mimeType", "image/jpeg")
            data = part["inlineData"].get("data", "")

            # Determine extension from mimeType
            ext_map = {
                "image/png": ".png",
                "image/jpeg": ".jpg",
                "image/webp": ".webp",
                "image/gif": ".gif",
            }
            ext = ext_map.get(mime_type, ".jpg")

            # Remove existing extension and add correct one
            if "." in filepath:
                filepath = filepath.rsplit(".", 1)[0]
            filepath = f"{filepath}{ext}"

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(data))
            return filepath
    return None

def get_model_parts(result: dict) -> list:
    """Extract model parts from response - KEEP THESE for multi-turn!"""
    return result.get("candidates", [{}])[0].get("content", {}).get("parts", [])
```

## Feature 1: Text-to-Image Generation

```python
request = {
    "contents": [{
        "role": "user",
        "parts": [{"text": "Create a photorealistic mountain landscape at golden hour."}]
    }],
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {"aspectRatio": "16:9", "imageSize": "2K"}
    }
}

result = call_gemini_image(request)
model_parts = get_model_parts(result)  # KEEP THIS for multi-turn
save_image(result, "landscape.jpg")
```

## Feature 2: Image-to-Image Editing

Send an existing image with editing instructions:

```python
with open("input.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

request = {
    "contents": [{
        "role": "user",
        "parts": [
            {"inlineData": {"mimeType": "image/jpeg", "data": image_b64}},
            {"text": "Change the sky to a dramatic sunset with orange and purple clouds."}
        ]
    }],
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {"aspectRatio": "16:9", "imageSize": "1K"}
    }
}

result = call_gemini_image(request)
model_parts = get_model_parts(result)  # KEEP THIS
save_image(result, "edited.jpg")
```

## Feature 3: Multi-Turn Editing (CRITICAL)

**Always keep model parts around!** Multi-turn requires:
1. The previous `thoughtSignature` fields
2. The previous image data

Without these, the API returns HTTP 400:
```
"Image part is missing a thought_signature in content position 2, part position 1"
```

### Recommended Pattern: Conversation State Class

```python
class GeminiImageConversation:
    def __init__(self):
        self.history = []

    def generate(self, prompt: str, image_config: dict = None) -> dict:
        """Generate or continue editing images."""
        self.history.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        config = {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": image_config or {"aspectRatio": "1:1", "imageSize": "1K"}
        }

        result = call_gemini_image({
            "contents": self.history,
            "generationConfig": config
        })

        # CRITICAL: Append model response to history for multi-turn
        model_parts = get_model_parts(result)
        self.history.append({
            "role": "model",
            "parts": model_parts  # Includes inlineData + thoughtSignature
        })

        return result

    def edit(self, instruction: str) -> dict:
        """Continue editing the last generated image."""
        return self.generate(instruction)

# Usage:
conv = GeminiImageConversation()

# Turn 1: Generate
result1 = conv.generate("Create an illustration of a red apple on a wooden table.")
save_image(result1, "apple_v1.jpg")

# Turn 2: Edit (works because we kept model_parts!)
result2 = conv.edit("Change the apple to green and add a knife next to it.")
save_image(result2, "apple_v2.jpg")

# Turn 3: Edit again
result3 = conv.edit("Now add a glass of water in the background.")
save_image(result3, "apple_v3.jpg")
```

### Manual Multi-Turn (Without Class)

```python
history = []

# Turn 1
history.append({"role": "user", "parts": [{"text": "Create a red apple on a table."}]})
result1 = call_gemini_image({"contents": history, "generationConfig": {...}})
model_parts1 = get_model_parts(result1)
history.append({"role": "model", "parts": model_parts1})  # KEEP THE PARTS!

# Turn 2
history.append({"role": "user", "parts": [{"text": "Make the apple green."}]})
result2 = call_gemini_image({"contents": history, "generationConfig": {...}})
model_parts2 = get_model_parts(result2)
history.append({"role": "model", "parts": model_parts2})  # KEEP AGAIN!
```

## Feature 4: Google Search Grounding

Generate images based on real-time information:

```python
request = {
    "contents": [{
        "role": "user",
        "parts": [{"text": "Create a weather forecast infographic for Tokyo, Japan this week."}]
    }],
    "tools": [{"google_search": {}}],  # Enable grounding
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {"aspectRatio": "16:9", "imageSize": "1K"}
    }
}

result = call_gemini_image(request)
# Response includes groundingMetadata with search sources
```

## Feature 5: Multiple Reference Images

Up to 14 reference images (6 objects + 5 humans for best results):

```python
with open("duck.jpg", "rb") as f:
    duck_b64 = base64.b64encode(f.read()).decode("utf-8")
with open("apple.jpg", "rb") as f:
    apple_b64 = base64.b64encode(f.read()).decode("utf-8")

request = {
    "contents": [{
        "role": "user",
        "parts": [
            {"text": "Combine these two objects into a single scene on a kitchen counter."},
            {"inlineData": {"mimeType": "image/jpeg", "data": duck_b64}},
            {"inlineData": {"mimeType": "image/jpeg", "data": apple_b64}}
        ]
    }],
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {"aspectRatio": "16:9", "imageSize": "1K"}
    }
}
```

## Request Field Naming

The API accepts both camelCase and snake_case in requests:
- `inlineData` or `inline_data`
- `mimeType` or `mime_type`

Responses always use camelCase (`inlineData`, `mimeType`, `thoughtSignature`).

## Safety and Content Filtering

Same `safetySettings` as standard Gemini. Image-specific `finishReason` values:
- `IMAGE_SAFETY` - Blocked for safety
- `IMAGE_PROHIBITED_CONTENT` - Prohibited content
- `IMAGE_RECITATION` - Copyright concerns
- `NO_IMAGE` - Failed to generate

All images include invisible SynthID watermark.

## Pricing (Approximate)

| Resolution | Cost per Image | Output Tokens |
|------------|----------------|---------------|
| 1K / 2K | ~$0.13 | ~1,200 |
| 4K | ~$0.24 | ~2,000 |

Input tokens: $2.00/1M. Image generation requires paid billing.

## Key Gotchas

1. **Always check `mimeType`** - Returns JPEG, not PNG as docs claim
2. **`thoughtSignature` is mandatory** for multi-turn - API returns 400 without it
3. **Keep model parts** - Store full response parts for conversation continuity
4. **Uppercase "K"** - Use `"2K"` not `"2k"` for imageSize
5. **20MB request limit** - Use Files API for larger inputs
6. **No streaming for images** - Image data arrives in complete response only
7. **Be explicit** - Say "create an image of" or "generate an image of" for best results

## Complete Working Example

```python
import requests
import base64

API_KEY = "your-api-key"
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent"

class GeminiImageSession:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.history = []

    def _call(self, request: dict) -> dict:
        resp = requests.post(URL,
            headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
            json=request, timeout=240)
        resp.raise_for_status()
        return resp.json()

    def _get_parts(self, result: dict) -> list:
        return result.get("candidates", [{}])[0].get("content", {}).get("parts", [])

    def generate(self, prompt: str, aspect="1:1", size="1K", grounding=False) -> dict:
        self.history.append({"role": "user", "parts": [{"text": prompt}]})

        request = {
            "contents": self.history,
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {"aspectRatio": aspect, "imageSize": size}
            }
        }
        if grounding:
            request["tools"] = [{"google_search": {}}]

        result = self._call(request)
        self.history.append({"role": "model", "parts": self._get_parts(result)})
        return result

    def edit_with_image(self, image_path: str, instruction: str, aspect="1:1", size="1K") -> dict:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        mime = "image/png" if image_path.endswith(".png") else "image/jpeg"
        self.history.append({
            "role": "user",
            "parts": [
                {"inlineData": {"mimeType": mime, "data": b64}},
                {"text": instruction}
            ]
        })

        result = self._call({
            "contents": self.history,
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {"aspectRatio": aspect, "imageSize": size}
            }
        })
        self.history.append({"role": "model", "parts": self._get_parts(result)})
        return result

    def save(self, result: dict, path: str) -> str:
        for part in self._get_parts(result):
            if "inlineData" in part:
                ext = ".png" if "png" in part["inlineData"].get("mimeType", "") else ".jpg"
                if "." in path: path = path.rsplit(".", 1)[0]
                path = f"{path}{ext}"
                with open(path, "wb") as f:
                    f.write(base64.b64decode(part["inlineData"]["data"]))
                return path
        return None

# Usage
session = GeminiImageSession(API_KEY)
r1 = session.generate("A red sports car in a showroom", aspect="16:9", size="2K")
session.save(r1, "car_v1")

r2 = session.generate("Change the car color to blue")  # Multi-turn works!
session.save(r2, "car_v2")

r3 = session.generate("Add a person standing next to it")
session.save(r3, "car_v3")
```
