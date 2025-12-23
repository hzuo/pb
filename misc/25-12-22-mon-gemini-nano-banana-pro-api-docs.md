# Using Google's gemini-3-pro-image-preview via REST API

Google's **gemini-3-pro-image-preview** model (internally codenamed "Nano Banana Pro") enables native image generation through the familiar `generateContent` endpoint. For developers experienced with the standard Gemini API, the key difference is configuration: you must explicitly request image output via `responseModalities` and can control output with a new `imageConfig` object.

## Model identification and endpoint structure

The model string is exactly `gemini-3-pro-image-preview` and uses the **v1beta** API version. The REST endpoint follows the same pattern as text generation:

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent
```

For Vertex AI, you must use the **global location**—regional endpoints do not support this model:

```
POST https://aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/publishers/google/models/gemini-3-pro-image-preview:generateContent
```

The related production model `gemini-2.5-flash-image` supports regional deployment but maxes out at **1024px** resolution. Deprecated models `gemini-2.0-flash-preview-image-generation` and `gemini-2.5-flash-image-preview` retire **October 31, 2025**.

## The critical configuration difference

Unlike standard text generation where `generationConfig` is optional, image generation **requires** you to specify output modalities. Without this, the model returns only text:

```json
{
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "2K"
    }
  }
}
```

The `responseModalities` array must include `"IMAGE"` to trigger image generation. You can use `["TEXT", "IMAGE"]` for mixed output or `["IMAGE"]` for image-focused responses, though the model always returns accompanying text.

## New imageConfig parameters unique to image generation

| Parameter | Values | Notes |
|-----------|--------|-------|
| `aspectRatio` | `"1:1"`, `"2:3"`, `"3:2"`, `"3:4"`, `"4:3"`, `"4:5"`, `"5:4"`, `"9:16"`, `"16:9"`, `"21:9"` | Default is `"1:1"` |
| `imageSize` | `"1K"`, `"2K"`, `"4K"` | **4K only available on gemini-3-pro-image-preview**. Must use uppercase "K" |

The `style` parameter is **not supported** and will throw an error. Standard text generation parameters like `temperature`, `topP`, `topK`, and `maxOutputTokens` remain available.

## Response schema differences from text generation

Images return as **base64-encoded PNG data** within the `inlineData` field. The response structure nests image data alongside text in the `parts` array:

```json
{
  "candidates": [{
    "content": {
      "role": "model",
      "parts": [
        {"text": "Here is your generated image..."},
        {
          "inlineData": {
            "mimeType": "image/png",
            "data": "/9j/4AAQSkZJRgABAQ..."
          }
        }
      ]
    },
    "finishReason": "STOP"
  }],
  "usageMetadata": {
    "promptTokenCount": 15,
    "candidatesTokenCount": 1305,
    "totalTokenCount": 1320
  }
}
```

New `finishReason` values specific to image generation include `IMAGE_SAFETY`, `IMAGE_PROHIBITED_CONTENT`, `IMAGE_RECITATION`, and `NO_IMAGE`. Each generated image consumes approximately **1,120-2,000 tokens** depending on resolution.

### Thought signatures for multi-turn editing

Gemini 3 Pro uses built-in "thinking mode" that generates interim reasoning. Responses may include a `thought_signature` field on image parts:

```json
{
  "inlineData": {"mimeType": "image/png", "data": "..."},
  "thought_signature": "<encrypted_signature>"
}
```

For multi-turn conversations, you **must pass these signatures back** in subsequent requests or receive a 400 error. Official SDKs handle this automatically; for raw REST calls, preserve and include all signature fields.

## Complete curl example for text-to-image

```bash
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{"text": "Create a photorealistic image of a mountain landscape at golden hour, 35mm photography style"}]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"],
      "imageConfig": {
        "aspectRatio": "16:9",
        "imageSize": "2K"
      }
    }
  }'
```

## Image-to-image editing request

```bash
IMAGE_BASE64=$(base64 -w0 input.jpg)

curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {"text": "Replace the sky with dramatic storm clouds"},
        {
          "inline_data": {
            "mime_type": "image/jpeg",
            "data": "'$IMAGE_BASE64'"
          }
        }
      ]
    }],
    "generationConfig": {
      "responseModalities": ["TEXT", "IMAGE"]
    }
  }'
```

The model accepts up to **14 reference images** (6 objects + 5 humans for character consistency), compared to just 3 images for gemini-2.5-flash-image.

## Google Search grounding for real-time data

A unique capability of gemini-3-pro-image-preview is generating images based on current information:

```json
{
  "contents": [{"parts": [{"text": "Create a weather forecast chart for Tokyo this week"}]}],
  "tools": [{"google_search": {}}],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {"aspectRatio": "16:9"}
  }
}
```

This enables generating visualizations of stock data, weather forecasts, or recent events.

## Pricing structure for image generation

| Model | Per-Image Cost | Input Tokens | Notes |
|-------|---------------|--------------|-------|
| gemini-3-pro-image-preview (1K/2K) | **$0.134** | $2.00/1M | 1,120 output tokens per image |
| gemini-3-pro-image-preview (4K) | **$0.24** | $2.00/1M | 2,000 output tokens per image |
| gemini-2.5-flash-image | **$0.039** | $0.30/1M | 1,290 output tokens per image |

Image output is approximately **10x more expensive** than text output per token. Batch API processing offers 50% discounts. Image generation **requires a paid billing account**—it is not available in the free tier.

## Rate limits differ from text generation

Rate limits are per-project (not per-API-key) and vary by payment tier:

| Tier | Qualification | Batch Tokens (enqueued) |
|------|--------------|------------------------|
| Tier 1 | Paid billing linked | 2,000,000 |
| Tier 2 | $250+ spent, 30+ days | 270,000,000 |
| Tier 3 | $1,000+ spent, 30+ days | 1,000,000,000 |

Quotas reset at **midnight Pacific Time**. Failed generation attempts still consume quota.

## Safety settings and content filtering

The same `safetySettings` array works for image generation with one key difference: additional image-specific finish reasons. Safety categories remain unchanged (`HARM_CATEGORY_HARASSMENT`, `HARM_CATEGORY_HATE_SPEECH`, `HARM_CATEGORY_SEXUALLY_EXPLICIT`, `HARM_CATEGORY_DANGEROUS_CONTENT`, `HARM_CATEGORY_CIVIC_INTEGRITY`).

Blocked responses indicate the cause via `finishReason`:

```json
{
  "candidates": [{
    "content": {"parts": [{"text": "I cannot generate that image."}]},
    "finishReason": "IMAGE_SAFETY"
  }]
}
```

Child safety and PII filters **cannot be disabled**. All generated images include an invisible **SynthID watermark** for provenance tracking.

## Critical gotchas and limitations

- **Always returns text with images**: Cannot generate image-only responses; text accompanies every image
- **No streaming for images**: Unlike text, image data arrives in the complete response only
- **Uppercase "K" required**: `imageSize: "2k"` fails; use `"2K"`
- **Ambiguous prompts produce text**: Explicitly state "create an image of" or "generate an image of"
- **Multi-turn requires signatures**: Raw REST calls must preserve `thought_signature` fields or face 400 errors
- **20MB request limit**: For larger inputs, use the Files API
- **Thinking mode is mandatory**: Gemini 3 Pro generates interim "thought images" (up to 2) before final output; this cannot be disabled

### Best language support

The model performs best with: ar-EG, de-DE, EN, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN.

## Conclusion

For developers already using the standard Gemini API, adding image generation requires three changes: use the `-image` model variant, add `responseModalities: ["TEXT", "IMAGE"]` to `generationConfig`, and parse base64-encoded PNG data from `inlineData` in responses. The endpoint structure, authentication, and safety settings remain identical. Key new capabilities include 4K resolution output, multi-image input for consistency, and Google Search grounding for real-time visualizations. Budget approximately **$0.13-0.24 per image** for gemini-3-pro-image-preview depending on resolution.

---

The “**gemini-3-pro-image-preview API**” is not some separate, magical image endpoint. It’s the **same `generateContent` REST API you already know**, with two big gotchas: **(1) the response includes image parts**, and **(2) multi-turn image editing will hard-fail with 400s unless you correctly replay *thought signatures* and prior image parts.** ([Google AI for Developers][1])

Below is a REST-level, end-to-end guide focused on what’s *different* vs `gemini-3-pro-preview`, and what you need to do to make image generation + editing reliable.

---

## 1) What the model is (and what changes vs “regular” Gemini 3 Pro)

`gemini-3-pro-image-preview` (aka “Gemini 3 Pro Image”, “Nano Banana Pro”) is designed for **image generation + image editing** with **1K/2K/4K output**, **strong text-in-image rendering**, **optional grounding via Google Search**, and **up to 14 reference images** in a prompt. ([Google AI for Developers][2])

Two consequences for API usage:

* You must request/handle **IMAGE modality** outputs (image bytes come back in content parts). ([Google AI for Developers][2])
* For **conversational editing**, you must replay **thought signatures** and the **prior image** in the conversation history, or the API may return **HTTP 400**. ([Google AI for Developers][3])

Also: generated images include a **SynthID watermark**. ([Google AI for Developers][2])

---

## 2) Endpoints and auth (Developer API / API key)

For the Gemini Developer API (AI Studio / API key flow), you call:

* `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent` ([Google AI for Developers][4])
* Include `x-goog-api-key: $GEMINI_API_KEY` ([Google AI for Developers][1])

Minimal curl skeleton:

```bash
curl -sS \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @request.json
```

The request body is a `GenerateContentRequest` with `contents[]` (conversation turns), plus optional `tools`, `systemInstruction`, `generationConfig`, etc. ([Google AI for Developers][4])

---

## 3) The request/response shape you must internalize

### 3.1 Conversation structure: `contents[]` of `Content` turns

Each turn has:

* `role`: `"user"` or `"model"`
* `parts[]`: list of “Part” objects (text, inline media, file refs, tool calls, etc.) ([Google AI for Developers][1])

### 3.2 Media parts: inline vs file references

**Inline bytes** go in a `Part.inline_data` “Blob”:

```json
{
  "inline_data": {
    "mime_type": "image/png",
    "data": "BASE64..."
  }
}
```

This exact pattern is shown throughout the REST examples. ([Google AI for Developers][1])

**File references** use `file_data` (after uploading via the Files API). ([Google AI for Developers][1])

> **Note on naming weirdness:** Google’s docs for the Developer API REST examples consistently use `inline_data` / `mime_type` / `file_data`. ([Google AI for Developers][1])
> Some SDK-oriented examples show `inlineData` / `mimeType`. Treat those as the same conceptual fields—just follow the REST docs when constructing JSON for `generativelanguage.googleapis.com`.

---

## 4) Text-to-image: the canonical REST call

Here’s a clean request that:

* generates an image,
* forces image-only output (no explanatory text),
* sets aspect ratio + resolution (2K).

```json
{
  "contents": [{
    "role": "user",
    "parts": [{"text": "Create a vibrant infographic that explains photosynthesis in simple terms."}]
  }],
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "2K"
    }
  }
}
```

`responseModalities` controls whether you get `TEXT`, `IMAGE`, or both, and the image model supports `imageConfig.aspectRatio` and (for this model) `imageConfig.imageSize` including 1K/2K/4K. ([Google AI for Developers][2])

### Parsing the response

The model returns `candidates[].content.parts[]`. Image bytes arrive as a media part (inline bytes), and text may also appear depending on your `responseModalities`. ([Google AI for Developers][1])

---

## 5) Image editing (single-turn): text + image → image

At the REST level: put the image in a `Part.inline_data`, add a text instruction, and ask for IMAGE output.

```json
{
  "contents": [{
    "role": "user",
    "parts": [
      {
        "inline_data": {
          "mime_type": "image/png",
          "data": "BASE64_SOURCE_IMAGE"
        }
      },
      { "text": "Edit this image: make the background a sunset, keep everything else unchanged." }
    ]
  }],
  "generationConfig": {
    "responseModalities": ["IMAGE"]
  }
}
```

The general “inline image data” pattern is the same as image understanding; you’re just using it with an image-generation-capable model and expecting an image back. ([Google AI for Developers][5])

---

## 6) Multi-turn editing (the part everyone screws up)

This is where `gemini-3-pro-image-preview` behaves differently from “normal chat”:

### 6.1 Thought signatures are **strict** for image generation/editing

Gemini 3 introduces `thoughtSignature`. For **image generation/editing**, strict validation is enforced: **if the model returns `thoughtSignature` on model parts, you must replay them in subsequent turns exactly, or you get a 400**. ([Google AI for Developers][3])

Additionally, for image editing:

* Signatures are guaranteed on the **first part after thoughts** (text or image) and on **every subsequent image (`inlineData`) part**; you must return them all. ([Google AI for Developers][3])

### 6.2 You must include the prior generated image as a `"model"` turn

Google’s own REST example for iterative editing shows the conversation like:

1. user asks for image
2. model returns an image (you include it back as a model turn)
3. user asks for modification ([Google AI for Developers][2])

A practical template (you fill in the actual base64 image + signatures you received):

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [{"text": "Create a vibrant infographic that explains photosynthesis..."}]
    },

    {
      "role": "model",
      "parts": [
        {
          "text": "I will generate a vibrant infographic...",
          "thoughtSignature": "<Signature_D>"
        },
        {
          "inline_data": { "mime_type": "image/png", "data": "<PREVIOUS_IMAGE_BASE64>" },
          "thoughtSignature": "<Signature_E>"
        }
      ]
    },

    {
      "role": "user",
      "parts": [{"text": "Update this infographic to be in Spanish. Do not change any other elements."}]
    }
  ],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": { "aspectRatio": "16:9", "imageSize": "2K" }
  }
}
```

The “include previous image as model content” + “tools + imageConfig” pattern is explicitly shown in the image-generation guide’s REST example. ([Google AI for Developers][2])

---

## 7) Grounded image generation via Google Search tool

`gemini-3-pro-image-preview` can use **Google Search grounding**. In REST you pass:

```json
"tools": [{ "google_search": {} }]
```

This is called out as a core capability (“Grounding with Google Search”), and the image-generation guide shows it in a REST request. ([Google AI for Developers][2])

---

## 8) Multi-image composition and “reference images” (up to 14)

### 8.1 The headline limits

* `gemini-3-pro-image-preview` supports **up to 14** reference images total. ([Google AI for Developers][2])
* Docs call out **5 images with high fidelity** and up to 14 total, and that `gemini-2.5-flash-image` is best with ~3 inputs. ([Google AI for Developers][2])
* Within the 14, guidance includes “up to 6 object images” (high fidelity) and “up to 5 human images” (character consistency). ([Google AI for Developers][2])

### 8.2 REST pattern: prompt + multiple `inline_data` parts

Conceptually:

* First part(s): your instruction text
* Next parts: each reference image as `inline_data`

(Exact code omitted here only because you’ll have a lot of base64 blobs, but it’s literally the same `inline_data` pattern repeated.) ([Google AI for Developers][2])

---

## 9) Controlling aspect ratio, resolution, and cost/tokens

For `gemini-3-pro-image-preview`, you control:

* `generationConfig.imageConfig.aspectRatio`
* `generationConfig.imageConfig.imageSize` ∈ `"1K" | "2K" | "4K"` ([Google AI for Developers][2])

The image generation guide provides a full mapping from aspect ratio + size → output resolution and “image tokens” (e.g., 4K is 2000 tokens per image). ([Google AI for Developers][2])

---

## 10) Payload size and the Files API (when inline bytes stop being viable)

Inline media has a hard practical ceiling: **the total request size must be < 20MB** when you embed bytes directly. ([Google AI for Developers][5])

When you exceed that, or you want reuse:

* Upload via Files API (store up to **20GB per project**, **2GB per file**, retained **48 hours**) ([Google AI for Developers][6])
* Then reference via a `file_data` part in `contents`. ([Google AI for Developers][7])

---

## 11) Streaming (SSE) and signatures

If you use streaming (`streamGenerateContent`), Gemini 3 can emit signatures in a chunk where text is empty; your parser must not assume “no text => nothing important.” ([Google AI for Developers][3])

(For image editing specifically, the big rule remains: **replay the signatures you got**.)

---

## 12) Practical “gotchas” checklist

* **No image returned?** You probably set response modalities to text-only; make sure `responseModalities` includes `"IMAGE"` (or omit it and accept the default mixed output). ([Google AI for Developers][2])
* **HTTP 400 in multi-turn editing?** You failed to replay **all** `thoughtSignature` fields from the model’s parts in the “current turn” / history. ([Google AI for Developers][3])
* **Requests too big?** Inline bytes push you over the ~20MB request size guidance; use Files API. ([Google AI for Developers][5])
* **Model ignores “exactly N images”?** That limitation is explicitly called out. ([Google AI for Developers][2])
* **Language quality:** there’s a recommended language list for best image generation performance. ([Google AI for Developers][2])

---

## Optional: Vertex AI differences (if you deploy via GCP)

On Vertex AI, the model exists as `gemini-3-pro-image-preview` (public preview, release date Nov 20, 2025) with the same token limits and supports text+image input and text+image output; you’ll use Vertex authentication and must access it in `global`. ([Google Cloud Documentation][8])

---

If you tell me whether you’re calling the **Developer API (`generativelanguage.googleapis.com`)** or **Vertex AI**, and whether you want **(a)** “single-shot image generation” only or **(b)** “multi-turn editing,” I can give you a hardened set of curl scripts + a response parser strategy that won’t break on signatures or mixed text/image parts.

[1]: https://ai.google.dev/api "Gemini API reference  |  Google AI for Developers"
[2]: https://ai.google.dev/gemini-api/docs/image-generation "Image generation with Gemini (aka Nano Banana & Nano Banana Pro)  |  Gemini API  |  Google AI for Developers"
[3]: https://ai.google.dev/gemini-api/docs/gemini-3 "Gemini 3 Developer Guide  |  Gemini API  |  Google AI for Developers"
[4]: https://ai.google.dev/api/generate-content "Generating content  |  Gemini API  |  Google AI for Developers"
[5]: https://ai.google.dev/gemini-api/docs/image-understanding "Image understanding  |  Gemini API  |  Google AI for Developers"
[6]: https://ai.google.dev/gemini-api/docs/files "Files API  |  Gemini API  |  Google AI for Developers"
[7]: https://ai.google.dev/api/files "Using files  |  Gemini API  |  Google AI for Developers"
[8]: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro-image?utm_source=chatgpt.com "Gemini 3 Pro Image | Generative AI on Vertex AI"

---

Yes, `gemini-3-pro-image-preview` is currently the best image generation model Google exposes via API.

To answer your specific questions on the naming confusion: **No, it is not the same as "Nano Banana." It is significantly better.**

Here is the breakdown of the current hierarchy:

### 1. The Hierarchy (Decoded)

Google's internal codenames leaked into the public discourse (via leaderboards like LMSYS), leading to some confusion. Here is how they map to the actual API models:

| Public Nickname | Official API Model ID | Capabilities | Status |
| --- | --- | --- | --- |
| **Nano Banana Pro** | **`gemini-3-pro-image-preview`** | **State-of-the-Art.** Uses "Thinking" (reasoning) to plan images. Best for text, diagrams, and complex prompt adherence. | **Current Best** |
| **Nano Banana** | `gemini-2.5-flash-image` | **Previous Gen.** Optimized for speed and high throughput. Good for general images but fails at complex text or logic. | Legacy / Fast |
| **Imagen 3** | `imagen-3.0-generate-002` | **Older / Different Family.** Uses the older diffusion architecture. Still good, but lacks the "reasoning" capabilities of the Gemini 3 vision models. | Specialized |

### 2. Why is "Pro" (Gemini 3) better than "Nano Banana" (Gemini 2.5)?

The "Pro" version (Gemini 3) is a fundamental shift in how images are generated. It is not just higher resolution; it is **agentic**.

* **It "Thinks" Before It Draws:**
As mentioned in the previous writeup, `gemini-3-pro-image-preview` uses reasoning tokens. If you ask for a "diagram of a jet engine," Nano Banana (2.5) just guesses based on pixel patterns. Nano Banana Pro (3.0) actually "reasons" through the components (intake, compression, combustion, exhaust) *in text/latent space* before rendering the pixels.
* **Text Rendering:**
Nano Banana (2.5) struggles with long sentences or specific font instructions. The Pro model is currently the market leader in rendering legible, correct text within images (e.g., for logos, diagrams, or signs).
* **Instruction Following:**
If you give a complex negative prompt or a multi-step instruction (e.g., "A cat on a box, but the box is blue and the cat is looking left, and there is no red in the image"), the Pro model follows this significantly better due to its reasoning layer.

### 3. Summary Recommendation

If you are building an app where **speed and cost** are the only factors, use the original **Nano Banana** (`gemini-2.5-flash-image`).

If you need **accuracy, text rendering, diagrams, or complex scene composition**, you should absolutely use **`gemini-3-pro-image-preview`** (Nano Banana Pro). It is the smartest visual model Google currently offers.
