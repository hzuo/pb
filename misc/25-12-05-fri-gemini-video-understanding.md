# Part 1: Google Gemini 3 Pro video understanding: Complete developer guide

**Gemini 3 Pro, announced November 18, 2025, delivers state-of-the-art video understanding with an 87.6% score on Video-MMMU**—the highest of any AI model. The model introduces high-frame-rate action capture and can synthesize narratives across hours of continuous footage, marking a substantial leap from Gemini 2.5 Pro's already impressive 83.6% benchmark score. Available now via Google AI Studio, Vertex AI, and the Gemini API at **$2/million input tokens**, it represents Google's most capable multimodal model for video analysis.

---

## What Gemini 3 Pro brings to video understanding

Google dropped the ".0" naming convention with this generation, calling it simply "Gemini 3 Pro." The model accepts raw video input and handles frame extraction internally using a variable-sequence video tokenizer (replacing Pan & Scan from 2.x), enabling true temporal reasoning across the content. Three capabilities stand out for video developers:

**High-frame-rate understanding** captures rapid action that previous models missed. Google specifically designed this for fast-moving scenes where critical moments occur between standard 1 FPS sampling intervals.

**Long-context video recall** enables the model to pinpoint specific details and synthesize narratives across extended footage. With the **1 million token context window** (1M input / 64k output), developers can process up to **~45 minutes of video with audio** or **~1 hour without audio** per request.

**Variable sequence length tokenization** replaces the "Pan and Scan" method from previous models, improving both quality and latency simultaneously. A new `media_resolution` parameter gives granular control over the quality-cost tradeoff.

| Resolution Setting             | Tokens/Frame | Notes                     |
| ------------------------------ | ------------ | ------------------------- |
| `MEDIA_RESOLUTION_HIGH`        | 280          | Best quality, most tokens |
| `MEDIA_RESOLUTION_MEDIUM`      | 70           | Balanced                  |
| `MEDIA_RESOLUTION_LOW`         | 70           | Same as medium for 3 Pro  |
| `MEDIA_RESOLUTION_UNSPECIFIED` | 70           | Default                   |

---

## Simple REST API example for video understanding

The minimal approach uses the File API to upload video, then references it in a generateContent request:

### Step 1: Upload video via File API

```bash
# Get upload URI
curl "https://generativelanguage.googleapis.com/upload/v1beta/files?key=${GEMINI_API_KEY}" \
  -D upload-header.tmp \
  -H "X-Goog-Upload-Protocol: resumable" \
  -H "X-Goog-Upload-Command: start" \
  -H "X-Goog-Upload-Header-Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Header-Content-Type: video/mp4" \
  -H "Content-Type: application/json" \
  -d '{"file": {"display_name": "sample_video"}}'

# Extract upload URL from response headers and upload
upload_url=$(grep -i "x-goog-upload-url" upload-header.tmp | cut -d' ' -f2 | tr -d '\r')

curl "${upload_url}" \
  -H "Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Offset: 0" \
  -H "X-Goog-Upload-Command: upload, finalize" \
  --data-binary "@video.mp4"
```

### Step 2: Generate content with video

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "contents": [{
      "parts": [
        {
          "fileData": {
            "mimeType": "video/mp4",
            "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/abc123xyz"
          }
        },
        {"text": "Summarize the key events in this video."}
      ]
    }]
  }'
```

For videos under 20MB, use inline base64 encoding instead:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {
          "inlineData": {
            "mimeType": "video/mp4",
            "data": "'$(base64 -w0 video.mp4)'"
          }
        },
        {"text": "What happens in this video?"}
      ]
    }]
  }'
```

---

## Maximally complex REST API example with all parameters

This example demonstrates every available configuration option for video understanding:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "contents": [{
      "role": "user",
      "parts": [
        {
          "fileData": {
            "mimeType": "video/mp4",
            "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/video123"
          },
          "videoMetadata": {
            "startOffset": {"seconds": 60, "nanos": 0},
            "endOffset": {"seconds": 300, "nanos": 0},
            "fps": 2.0
          }
        },
        {
          "fileData": {
            "mimeType": "video/mp4",
            "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/video456"
          }
        },
        {"text": "Compare the events in both videos. Provide detailed timestamps for key moments."}
      ]
    }],
    "systemInstruction": {
      "role": "system",
      "parts": [{
        "text": "You are an expert video analyst. Always provide timestamps in MM:SS format. Structure your analysis with clear sections for: scene description, key events, notable objects/people, and temporal relationships. Be precise and cite specific visual evidence."
      }]
    },
    "generationConfig": {
      "temperature": 0.7,
      "topP": 0.9,
      "topK": 40,
      "candidateCount": 1,
      "maxOutputTokens": 8192,
      "stopSequences": ["[END ANALYSIS]"],
      "responseMimeType": "application/json",
      "responseJsonSchema": {
        "type": "object",
        "properties": {
          "summary": {"type": "string"},
          "key_events": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "timestamp": {"type": "string", "description": "MM:SS format"},
                "video_source": {"type": "string", "enum": ["video1", "video2"]},
                "description": {"type": "string"},
                "significance": {"type": "string"}
              },
              "required": ["timestamp", "description"]
            }
          },
          "comparison": {"type": "string"},
          "temporal_relationships": {
            "type": "array",
            "items": {"type": "string"}
          }
        },
        "required": ["summary", "key_events"]
      },
      "seed": 42,
      "presencePenalty": 0.1,
      "frequencyPenalty": 0.1,
      "mediaResolution": "MEDIA_RESOLUTION_HIGH"
    },
    "safetySettings": [
      {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
      {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
      {"category": "HARM_CATEGORY_CIVIC_INTEGRITY", "threshold": "BLOCK_NONE"}
    ],
    "tools": [{
      "functionDeclarations": [{
        "name": "get_frame_details",
        "description": "Extract detailed information about a specific frame in the video",
        "parameters": {
          "type": "object",
          "properties": {
            "timestamp": {"type": "string", "description": "Timestamp in MM:SS format"},
            "analysis_type": {
              "type": "string",
              "enum": ["objects", "text", "faces", "scene", "motion"],
              "description": "Type of analysis to perform"
            },
            "bounding_boxes": {"type": "boolean", "description": "Whether to return bounding box coordinates"}
          },
          "required": ["timestamp", "analysis_type"]
        }
      }]
    }],
    "toolConfig": {
      "functionCallingConfig": {
        "mode": "AUTO"
      }
    }
  }'
```

### Parameter reference for video understanding

| Parameter                   | Purpose                  | Values                                                                     |
| --------------------------- | ------------------------ | -------------------------------------------------------------------------- |
| `videoMetadata.startOffset` | Clip video start time    | `{"seconds": N}` or `"Ns"`                                                 |
| `videoMetadata.endOffset`   | Clip video end time      | `{"seconds": N}` or `"Ns"`                                                 |
| `videoMetadata.fps`         | Frame sampling rate      | Float (default: 1.0)                                                       |
| `mediaResolution`           | Quality/token tradeoff   | `MEDIA_RESOLUTION_LOW`, `MEDIA_RESOLUTION_MEDIUM`, `MEDIA_RESOLUTION_HIGH` |
| `responseMimeType`          | Output format            | `text/plain`, `application/json`                                           |
| `responseSchema`            | Structured output schema | JSON Schema object                                                         |

---

## Benchmark performance shows clear leadership

Gemini 3 Pro achieves the highest scores on comprehensive video understanding benchmarks, with particularly strong gains in temporal reasoning and long-form video comprehension.

### Video-MMMU: The flagship video understanding benchmark

| Model             | Video-MMMU Score | Gap vs. Gemini 3 |
| ----------------- | ---------------- | ---------------- |
| **Gemini 3 Pro**  | **87.6%**        | —                |
| Gemini 2.5 Pro    | 83.6%            | -4.0             |
| GPT-5.1           | ~80.4%*          | -7.2             |
| Gemini 2.5 Flash  | 79.2%            | -8.4             |
| Claude Sonnet 4.5 | 68.4%            | -19.2            |
| GPT-4.1           | 60.9%            | -26.7            |

*GPT-5.1 score is from third-party evaluations; OpenAI has not published official Video-MMMU results.

### VideoMME: Comprehensive multimodal evaluation

Gemini 2.5 Pro holds the current measured record at **84.8-86.9%** (depending on audio inclusion), substantially ahead of GPT-4.1's **72.0-79.6%**. The **+7-10 point advantage** persists across visual-only and audio-visual configurations.

### Long-form video understanding stands out

On Google's **1H-VideoQA benchmark** testing hour-long videos (40-105 minutes), Gemini 2.5 Pro scores **81.0%** versus GPT-4.1's **56.8%**—a **24.2 point gap** demonstrating superior long-context video reasoning. The model's performance improves consistently as frame count increases, indicating genuine temporal understanding rather than sampling luck.

| Benchmark        | Gemini 2.5/3 Pro | GPT-4.1 | Advantage |
| ---------------- | ---------------- | ------- | --------- |
| 1H-VideoQA       | 81.0%            | 56.8%   | +24.2     |
| ActivityNet-QA   | 66.7%            | 60.4%   | +6.3      |
| YouCook2 (CIDEr) | 188.3            | 127.6   | +47.6%    |
| EgoSchema        | 64.5%            | 55.6%   | +8.9      |

---

## How Gemini 3 Pro differs from previous versions

The evolution from 1.5 Pro through 3 Pro shows consistent improvements in video capabilities, with each generation adding substantial new features.

### Capability progression across versions

**Gemini 1.5 Pro (February 2024)** introduced native multimodal video processing with the breakthrough 1M-2M token context window. It processed 1 frame per second, allowed only 1 video per request, and achieved **99%+ needle recall** in video haystack tests.

**Gemini 2.0 Flash (December 2024)** added the **Multimodal Live API** for real-time bidirectional video interactions, improved spatial understanding for accurate bounding boxes, and delivered **2x faster** processing than 1.5 Pro while outperforming it on benchmarks.

**Gemini 2.5 Pro (March-May 2025)** brought the most dramatic video improvements: support for **up to 10 videos per request** (versus 1 previously), video clipping with `startOffset`/`endOffset`, configurable FPS sampling, low-resolution mode enabling 6-hour videos, and **direct YouTube URL support**. Benchmark scores jumped to **84.8% on VideoMME**.

**Gemini 3 Pro (November 2025)** pushes further with **high-frame-rate understanding** for fast action, improved variable sequence length tokenization, and **87.6% on Video-MMMU**. The granular `media_resolution` parameter offers four quality tiers for fine-tuned cost optimization.

### Key technical differences

| Feature                 | 1.5 Pro | 2.0 Flash | 2.5 Pro  | 3 Pro   |
| ----------------------- | ------- | --------- | -------- | ------- |
| Videos per request      | 1       | 1         | **10**   | 10      |
| YouTube URLs            | No      | No        | **Yes**  | Yes     |
| Video clipping          | No      | No        | **Yes**  | Yes     |
| Custom FPS              | No      | No        | **Yes**  | Yes     |
| Real-time streaming     | No      | **Yes**   | Yes      | No      |
| Max duration (w/ audio) | 2 hr    | 2 hr      | **6 hr** | ~45 min |
| High-frame-rate mode    | No      | No        | No       | **Yes** |

---

## Supported formats and technical constraints

Gemini 3 Pro accepts these video formats: `video/mp4`, `video/mpeg`, `video/mov`, `video/avi`, `video/x-flv`, `video/mpg`, `video/webm`, `video/wmv`, `video/3gpp`.

**Token calculation (Gemini 3 Pro)**: At default resolution, video consumes **70 tokens per frame** (sampled at 1 FPS by default). At `MEDIA_RESOLUTION_HIGH`, this increases to **280 tokens per frame**. Audio is tokenized separately. The 300/100 tokens-per-second heuristic applies to Gemini 2.x models, not 3 Pro.

**File limits**: Maximum **2GB per file**, **20GB total storage** per project. Uploaded files expire after **48 hours**. For videos over 20MB or longer than 1 minute, use the File API rather than inline base64 encoding.

---

## Conclusion

Gemini 3 Pro represents the current frontier of AI video understanding, with benchmark scores that substantially exceed both previous Gemini versions and competitors. The **87.6% Video-MMMU score** and **24-point advantage** on hour-long video comprehension translate to practical capabilities: analyzing security footage, generating video summaries, understanding tutorials, and extracting structured data from video content.

For developers, the most impactful changes are the high-frame-rate processing mode for capturing fast action, the four-tier `media_resolution` parameter for cost optimization, and the continued support for processing up to 10 videos simultaneously with YouTube URL compatibility. The REST API structure remains consistent with Gemini 2.5, making migration straightforward—the primary change is simply updating the model identifier to `gemini-3-pro`.

---

# Part 2: Self-contained `uv` script for long video analysis

Here’s the core idea: Gemini 3 Pro gives you a ~1M token context window and can directly “watch” video, but a single request is still capped to ~45 minutes of video with audio, ~1 hour without, and 2 GB per file via the Files API. For _hours_-long MP4s you need to:

- **Probe & slice** the video into safe-length chunks (I use ~20 min by default, well under the 45 min limit and away from the extreme edge of the context window).
- **Upload each chunk** via the Files API (`media.upload` → `files.get`) and wait for `state == ACTIVE`.
- **Analyze each chunk** with `gemini-3-pro-preview:generateContent`, asking for structured JSON so the script can stitch everything back together.
- **Aggregate across chunks** in a final text-only call that consumes all the chunk summaries in the 1M-token window.

The script below implements exactly that, with:

- ffprobe/ffmpeg-based slicing
- Files API resumable upload via **pure `requests`**
- A **map → (optional rolling context) → reduce** pattern over chunks
- All the important **knobs** exposed at the top: model ID, chunk size, media resolution, sampling params, JSON mode, etc.

---

## 1. The self-contained `uv` script

Save this as e.g. `gemini_video_analyzer.py` and run with `uv run gemini_video_analyzer.py your_video.mp4`.

> **Prereqs**
>
> - Python ≥ 3.11
> - `uv` installed
> - `ffmpeg` and `ffprobe` available on `$PATH`
> - A Gemini API key from Google AI Studio in `GEMINI_API_KEY`

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.32.3",
# ]
# ///

"""
gemini_video_analyzer.py

Analyze long videos with Gemini 3 Pro via the REST API.

Key design choices:
- Upload video ONCE, slice via videoMetadata.startOffset/endOffset (no ffmpeg re-encoding)
- Use actual structured output (responseJsonSchema in generationConfig)
- System instructions go in systemInstruction only (no duplication in prompts)
- ffmpeg physical chunking only as fallback for >2GB files
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import requests

# ============================================================================
# TOP-LEVEL CONFIG (ALL YOUR KNOBS LIVE HERE)
# ============================================================================

GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com"
GEMINI_MODEL = "gemini-3-pro-preview"

# ---- System instruction (high-level role/rules only) -----------------------
SYSTEM_INSTRUCTION = """You are an expert multimodal analyst. Your goals:
- Understand the story, structure, and key entities in video content
- Identify important scenes and turning points with timestamps
- Track evolving topics, arguments, or plot lines over time
- Capture both high-level summary and important details

Always respond with valid JSON matching the provided schema."""

# ---- Model limits ----------------------------------------------------------
MODEL_MAX_INPUT_TOKENS = 1_048_576
MODEL_MAX_OUTPUT_TOKENS = 65_536
MODEL_MAX_VIDEO_WITH_AUDIO_SEC = 45 * 60     # ~45 minutes
MODEL_MAX_VIDEO_WITHOUT_AUDIO_SEC = 60 * 60  # ~60 minutes
FILES_API_MAX_BYTES = 2 * 1024**3            # 2 GiB per file

# ---- Chunking defaults -----------------------------------------------------
TARGET_CHUNK_DURATION_SEC = 20 * 60  # 20 minutes per logical chunk

# Chunk-level strategy:
# - "independent": each chunk summarized with no prior context; final call stitches
# - "rolling": pass running summary into each chunk for narrative continuity
VIDEO_CHUNK_STRATEGY = "rolling"

# Token estimation: This is a ROUGH PLANNING HEURISTIC only.
# Actual tokenization depends on media_resolution and fps settings.
# At default (1 FPS, MEDIUM resolution): ~70 tokens/frame = ~70 tokens/sec
# At HIGH resolution: ~280 tokens/frame
# If you change fps or resolution, this heuristic becomes inaccurate.
TOKENS_PER_FRAME_DEFAULT = 70
DEFAULT_FPS = 1.0

# ---- Generation config -----------------------------------------------------
# All the sampling/output knobs in one place.
GENERATION_CONFIG: dict[str, Any] = {
    # Sampling / decoding
    "temperature": 0.4,          # lower = more deterministic
    "topP": 0.9,
    "topK": 32,
    "candidateCount": 1,

    # Length / stopping
    "maxOutputTokens": 4096,
    "stopSequences": [],         # e.g. ["[END]"]

    # Output format - JSON mode with schema enforcement
    "responseMimeType": "application/json",

    # Media handling
    # Options: MEDIA_RESOLUTION_UNSPECIFIED / LOW / MEDIUM / HIGH
    "mediaResolution": "MEDIA_RESOLUTION_MEDIUM",

    # Optional penalties & determinism (uncomment to use):
    # "presencePenalty": 0.0,
    # "frequencyPenalty": 0.0,
    # "seed": 42,
}

# Safety settings (optional). Leaving empty uses model defaults.
SAFETY_SETTINGS: list[dict[str, Any]] = [
    # Example:
    # {
    #     "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    #     "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    # },
]

# External tools
FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "ffmpeg")
FFPROBE_BIN = os.environ.get("FFPROBE_BIN", "ffprobe")

# ============================================================================
# JSON SCHEMAS FOR STRUCTURED OUTPUT
# ============================================================================

CHUNK_ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "chunk_index": {"type": "integer"},
        "start_sec": {"type": "number"},
        "end_sec": {"type": "number"},
        "summary": {"type": "string"},
        "timeline": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "timestamp_sec": {"type": "number"},
                    "description": {"type": "string"},
                },
                "required": ["timestamp_sec", "description"],
            },
        },
        "key_entities": {"type": "array", "items": {"type": "string"}},
        "open_questions": {"type": "array", "items": {"type": "string"}},
        "running_summary": {"type": "string"},
    },
    "required": ["chunk_index", "start_sec", "end_sec", "summary", "running_summary"],
}

FINAL_SUMMARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "overall_summary": {"type": "string"},
        "key_scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start_sec": {"type": "number"},
                    "end_sec": {"type": "number"},
                    "label": {"type": "string"},
                    "details": {"type": "string"},
                },
                "required": ["start_sec", "label"],
            },
        },
        "characters_or_entities": {"type": "array", "items": {"type": "string"}},
        "topics": {"type": "array", "items": {"type": "string"}},
        "questions_answered": {"type": "array", "items": {"type": "string"}},
        "unresolved_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["overall_summary"],
}

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class VideoMetadata:
    path: Path
    duration_sec: float
    has_audio: bool
    size_bytes: int


@dataclass
class ChunkPlan:
    index: int
    start_sec: float
    end_sec: float


# ============================================================================
# HELPERS
# ============================================================================

def require_api_key() -> str:
    key = os.environ.get(GEMINI_API_KEY_ENV)
    if not key:
        sys.exit(f"ERROR: Set {GEMINI_API_KEY_ENV} environment variable")
    return key


def run_subprocess(cmd: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit(f"ERROR: {cmd[0]} not found. Install it or set FFMPEG_BIN/FFPROBE_BIN.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"ERROR: {' '.join(cmd)}\n{e.stderr}")


def prune_nones(d: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from dict (useful for optional config fields)."""
    return {k: v for k, v in d.items() if v is not None}


def probe_video(path: Path) -> VideoMetadata:
    """Get video metadata via ffprobe."""
    cmd = [FFPROBE_BIN, "-v", "error", "-show_entries", "format=duration",
           "-show_streams", "-print_format", "json", str(path)]
    result = run_subprocess(cmd)
    data = json.loads(result.stdout or "{}")

    duration = float(data.get("format", {}).get("duration", 0))
    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))

    return VideoMetadata(
        path=path,
        duration_sec=duration,
        has_audio=has_audio,
        size_bytes=path.stat().st_size,
    )


def plan_chunks(meta: VideoMetadata) -> list[ChunkPlan]:
    """Plan logical chunks respecting model limits."""
    if meta.duration_sec <= 0:
        return [ChunkPlan(0, 0, 0)]

    max_dur = (MODEL_MAX_VIDEO_WITH_AUDIO_SEC if meta.has_audio
               else MODEL_MAX_VIDEO_WITHOUT_AUDIO_SEC)

    chunk_dur = min(TARGET_CHUNK_DURATION_SEC, max_dur)
    chunk_dur = max(chunk_dur, 60)  # At least 1 minute

    if meta.duration_sec <= chunk_dur:
        return [ChunkPlan(0, 0, meta.duration_sec)]

    num_chunks = math.ceil(meta.duration_sec / chunk_dur)
    chunk_len = meta.duration_sec / num_chunks

    return [
        ChunkPlan(
            index=i,
            start_sec=i * chunk_len,
            end_sec=meta.duration_sec if i == num_chunks - 1 else (i + 1) * chunk_len,
        )
        for i in range(num_chunks)
    ]


# ============================================================================
# FILES API
# ============================================================================

def upload_file(api_key: str, path: Path, mime_type: str = "video/mp4",
                display_name: Optional[str] = None) -> dict:
    """Upload via resumable upload protocol."""
    num_bytes = path.stat().st_size
    display_name = display_name or path.name

    # Start upload
    start_resp = requests.post(
        f"{GEMINI_API_BASE}/upload/v1beta/files?key={api_key}",
        headers={
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(num_bytes),
            "X-Goog-Upload-Header-Content-Type": mime_type,
            "Content-Type": "application/json",
        },
        json={"file": {"display_name": display_name}},
        timeout=60,
    )
    start_resp.raise_for_status()
    upload_url = start_resp.headers.get("X-Goog-Upload-Url")
    if not upload_url:
        raise RuntimeError("Upload URL missing from response")

    # Upload content
    with path.open("rb") as f:
        upload_resp = requests.post(
            upload_url,
            headers={
                "Content-Length": str(num_bytes),
                "X-Goog-Upload-Offset": "0",
                "X-Goog-Upload-Command": "upload, finalize",
            },
            data=f,
            timeout=600,
        )
    upload_resp.raise_for_status()
    return upload_resp.json().get("file", upload_resp.json())


def wait_for_active(api_key: str, file_obj: dict, poll_sec: int = 5) -> dict:
    """Poll until video processing completes."""
    name = file_obj.get("name")
    while (file_obj.get("state") or "").upper() != "ACTIVE":
        print(f"  [files] state={file_obj.get('state')}, waiting {poll_sec}s...")
        time.sleep(poll_sec)
        resp = requests.get(
            f"{GEMINI_API_BASE}/v1beta/{name}",
            headers={"x-goog-api-key": api_key},
            timeout=30,
        )
        resp.raise_for_status()
        file_obj = resp.json()
    return file_obj


def get_file_uri(file_obj: dict) -> str:
    """Extract file URI from file object (handles API variations)."""
    uri = file_obj.get("uri") or file_obj.get("fileUri") or file_obj.get("file_uri")
    if not uri:
        raise RuntimeError(f"No URI found in file object: {file_obj}")
    return uri


# ============================================================================
# GENERATE CONTENT
# ============================================================================

def call_generate_content(api_key: str, payload: dict) -> dict:
    """Call generateContent endpoint."""
    resp = requests.post(
        f"{GEMINI_API_BASE}/v1beta/models/{GEMINI_MODEL}:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=600,
    )
    resp.raise_for_status()
    return resp.json()


def extract_text(resp: dict) -> str:
    """Extract text from generateContent response."""
    try:
        return resp["candidates"][0]["content"]["parts"][0].get("text", "")
    except (KeyError, IndexError):
        return json.dumps(resp, indent=2)


def analyze_chunk(
    api_key: str,
    file_uri: str,
    chunk: ChunkPlan,
    total_chunks: int,
    running_summary: Optional[str],
) -> dict:
    """Analyze a single chunk using API-side video slicing."""

    config = dict(GENERATION_CONFIG)
    config["responseJsonSchema"] = CHUNK_ANALYSIS_SCHEMA

    prompt = f"""Analyze chunk {chunk.index + 1} of {total_chunks}.
Time range: {chunk.start_sec:.1f}s to {chunk.end_sec:.1f}s

{"Previous context: " + running_summary if running_summary else "This is the first chunk."}

For this chunk:
1. Summarize what happens
2. List key events with timestamps (relative to video start)
3. Note important entities
4. Flag any open questions
5. Update the running summary (≤200 words) for the next chunk"""

    payload: dict[str, Any] = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": [{
            "parts": [
                {
                    "fileData": {"fileUri": file_uri, "mimeType": "video/mp4"},
                    "videoMetadata": {
                        "startOffset": {"seconds": int(chunk.start_sec)},
                        "endOffset": {"seconds": int(chunk.end_sec)},
                    },
                },
                {"text": prompt},
            ]
        }],
        "generationConfig": prune_nones(config),
    }

    if SAFETY_SETTINGS:
        payload["safetySettings"] = SAFETY_SETTINGS

    resp = call_generate_content(api_key, payload)
    text = extract_text(resp)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {"chunk_index": chunk.index, "start_sec": chunk.start_sec,
                "end_sec": chunk.end_sec, "summary": text, "running_summary": text}

    # Ensure mandatory fields
    data.setdefault("chunk_index", chunk.index)
    data.setdefault("start_sec", chunk.start_sec)
    data.setdefault("end_sec", chunk.end_sec)

    return data


def aggregate_chunks(api_key: str, chunk_results: list[dict]) -> dict:
    """Final aggregation pass over all chunk summaries."""

    config = dict(GENERATION_CONFIG)
    config["maxOutputTokens"] = 8192
    config["responseJsonSchema"] = FINAL_SUMMARY_SCHEMA

    prompt = f"""Here are the analyses of each chunk of a long video:

{json.dumps(chunk_results, indent=2)}

Produce a coherent overall summary:
1. Overall narrative/summary
2. Key scenes with timestamps
3. Main characters/entities and their roles
4. Major topics/themes
5. Questions the video answers, and those left unresolved"""

    payload: dict[str, Any] = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": prune_nones(config),
    }

    if SAFETY_SETTINGS:
        payload["safetySettings"] = SAFETY_SETTINGS

    resp = call_generate_content(api_key, payload)
    text = extract_text(resp)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"overall_summary": text}


# ============================================================================
# FALLBACK: PHYSICAL CHUNKING FOR >2GB FILES
# ============================================================================

def split_video_ffmpeg(meta: VideoMetadata, chunks: list[ChunkPlan],
                       out_dir: Path) -> list[Path]:
    """Physical chunking via ffmpeg - only for files > 2GB."""
    paths = []
    for chunk in chunks:
        out_path = out_dir / f"{meta.path.stem}_chunk{chunk.index:03d}.mp4"
        cmd = [
            FFMPEG_BIN, "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{chunk.start_sec:.3f}",
            "-t", f"{chunk.end_sec - chunk.start_sec:.3f}",
            "-i", str(meta.path),
            "-c", "copy", str(out_path),
        ]
        print(f"  [ffmpeg] Creating chunk {chunk.index}")
        run_subprocess(cmd)
        paths.append(out_path)
    return paths


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Analyze long videos with Gemini 3 Pro")
    parser.add_argument("video", type=Path, help="Path to video file")
    parser.add_argument(
        "--strategy",
        choices=["independent", "rolling"],
        default=VIDEO_CHUNK_STRATEGY,
        help="Chunk strategy: 'independent' or 'rolling' context (default: rolling)",
    )
    args = parser.parse_args()

    api_key = require_api_key()
    meta = probe_video(args.video)

    print(f"Video: {meta.path}")
    print(f"Duration: {meta.duration_sec/60:.1f} min | Size: {meta.size_bytes/1024**2:.1f} MB")
    print(f"Audio: {meta.has_audio} | Strategy: {args.strategy}")

    chunks = plan_chunks(meta)
    print(f"\nPlanned {len(chunks)} chunk(s):")
    for c in chunks:
        print(f"  Chunk {c.index}: {c.start_sec:.1f}s → {c.end_sec:.1f}s "
              f"({(c.end_sec - c.start_sec)/60:.1f} min)")

    # Decide: API-side slicing (preferred) vs physical chunking (fallback)
    use_physical_chunking = meta.size_bytes > FILES_API_MAX_BYTES

    if use_physical_chunking:
        print(f"\n⚠️  File > 2GB, using physical chunking (slower)")
        with tempfile.TemporaryDirectory() as tmpdir:
            chunk_paths = split_video_ffmpeg(meta, chunks, Path(tmpdir))
            chunk_results = []
            running_summary = None

            for chunk, chunk_path in zip(chunks, chunk_paths):
                print(f"\n=== Chunk {chunk.index + 1}/{len(chunks)} ===")
                file_obj = upload_file(api_key, chunk_path,
                                       display_name=f"{meta.path.name} [chunk {chunk.index}]")
                file_obj = wait_for_active(api_key, file_obj)

                result = analyze_chunk(
                    api_key, get_file_uri(file_obj), chunk, len(chunks),
                    running_summary if args.strategy == "rolling" else None
                )
                chunk_results.append(result)
                if args.strategy == "rolling":
                    running_summary = result.get("running_summary", running_summary)
    else:
        # Preferred path: upload once, slice via API
        print(f"\nUploading video (once)...")
        file_obj = upload_file(api_key, meta.path)
        file_obj = wait_for_active(api_key, file_obj)
        file_uri = get_file_uri(file_obj)
        print(f"  Ready: {file_uri}")

        chunk_results = []
        running_summary = None

        for chunk in chunks:
            print(f"\n=== Chunk {chunk.index + 1}/{len(chunks)} "
                  f"({chunk.start_sec:.0f}s-{chunk.end_sec:.0f}s) ===")
            result = analyze_chunk(
                api_key, file_uri, chunk, len(chunks),
                running_summary if args.strategy == "rolling" else None
            )
            chunk_results.append(result)
            if args.strategy == "rolling":
                running_summary = result.get("running_summary", running_summary)

    print("\n=== Aggregating ===")
    final = aggregate_chunks(api_key, chunk_results)

    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(json.dumps(final, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("PER-CHUNK SUMMARIES")
    print("=" * 60)
    print(json.dumps(chunk_results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

---

## 2. How this addresses your specific questions

### (1) Long video vs context window and "optimal slicing"

Key constraints (Gemini 3 Pro):

- **1,048,576 input tokens / 65,536 output tokens per request.**
- **Max ~45 minutes of video with audio (~60 minutes without) per request**, regardless of context window.
- **Files API per-file limit is 2 GB and 20 GB total per project.**

The script plans chunk sizes by taking the minimum of:

- The ~45 min model limit
- A comfortable **20-minute target** (leaving headroom for context and avoiding quality degradation near limits)

**Key efficiency improvement**: Instead of physically slicing the video with ffmpeg and re-uploading each chunk, the script now:

1. **Uploads the video once** via the Files API
2. **Slices via the API** using `videoMetadata.startOffset` / `endOffset` in each `generateContent` call

This saves bandwidth, avoids hitting storage limits, and eliminates per-chunk transcoding latency. Physical ffmpeg chunking is retained only as a fallback for files > 2GB.

### (2) Independent chunks vs rolling context

The script supports both strategies via `--strategy`:

1. **Independent** (`--strategy independent`):
   - Each chunk summarized with no prior context
   - Final aggregation call stitches everything together
   - Pros: Simple, robust, parallelizable
   - Cons: May miss cross-chunk narrative threads

2. **Rolling** (`--strategy rolling`, default):
   - Each chunk receives `running_summary` from previous chunk
   - Each chunk returns updated `running_summary` (≤200 words)
   - Pros: Maintains narrative continuity across chunks
   - Cons: Sequential processing, summary may drift

For most "watch & understand" use-cases, **rolling** gives more coherent results.

### (3) Structured output with schemas

The script now properly uses **structured output** via the Gemini API:

```python
config["responseJsonSchema"] = CHUNK_ANALYSIS_SCHEMA
```

This ensures the model returns valid JSON matching the schema, rather than just "asking nicely" in the prompt. The schemas are defined once and passed to `generationConfig.responseJsonSchema` for both chunk analysis and final aggregation.

### (4) System instructions

System instructions appear in **one place only** (`systemInstruction.parts[0].text`). The user prompt contains only chunk-specific context and instructions, avoiding token waste from duplication.

### (5) All the knobs surfaced

The script exposes the important Gemini knobs in one place:

- **Model & endpoint**: `GEMINI_MODEL`, `GEMINI_API_BASE`
- **Generation config** (inside `GENERATION_CONFIG`):
  - `temperature`, `topP`, `topK`, `candidateCount`
  - `maxOutputTokens`, `stopSequences`
  - `responseMimeType` for JSON mode
  - `mediaResolution` (LOW/MEDIUM/HIGH/UNSPECIFIED) to trade visual detail vs token usage
  - (commented) `presencePenalty`, `frequencyPenalty`, `seed`
- **Safety**: `SAFETY_SETTINGS` array for harm categories & thresholds
- **Chunking**: `TARGET_CHUNK_DURATION_SEC`, `VIDEO_CHUNK_STRATEGY`
- **Tools**: `FFMPEG_BIN`, `FFPROBE_BIN` for container/custom binary paths

The script is executable as-is, but also readable enough to quickly tweak for specific pipelines (e.g., change the JSON schema, add domain-specific prompts for lecture summarization vs security footage analysis).

---

# Part 3: Additional technical details from Vertex AI documentation

This section captures supplementary details from the official [Vertex AI Video Understanding documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/video-understanding) (updated 2025-12-04) that didn't fit neatly into Parts 1–2.

---

## File API processing internals

When you upload video via the File API, the backend processes it as follows:

| Media type | Sampling rate | Notes |
|------------|---------------|-------|
| Video | **1 frame per second (FPS)** | Configurable via `videoMetadata.fps` |
| Audio | **1 Kbps, mono** | Single channel, heavily compressed |
| Timestamps | **Added every 1 second** | Aligned with frame sampling |

These rates may change in future releases as Google optimizes for quality and latency.

---

## Timestamp format requirements

The model expects timestamps in specific formats depending on your FPS setting:

| FPS setting | Required format | Example |
|-------------|-----------------|---------|
| **≤ 1 FPS** (default) | `MM:SS` or `H:MM:SS` | `05:23` or `1:05:23` |
| **> 1 FPS** | `MM:SS.sss` or `H:MM:SS.sss` | `05:23.250` or `1:05:23.250` |

When prompting the model to output timestamps, explicitly request the appropriate format. For the script in Part 2 (which uses default 1 FPS), `MM:SS` is correct.

---

## Per-part media resolution override

You can set `mediaResolution` globally in `generationConfig`, but you can also override it **per-part** by adding a `mediaResolution` field as a **sibling** to `fileData` and `videoMetadata` within the Part object. The per-part field uses a `PartMediaResolution` structure with a nested `level` property:

```json
{
  "contents": [{
    "parts": [
      {
        "fileData": {
          "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/video1",
          "mimeType": "video/mp4"
        },
        "videoMetadata": {
          "startOffset": {"seconds": 0},
          "endOffset": {"seconds": 120}
        },
        "mediaResolution": {
          "level": "MEDIA_RESOLUTION_HIGH"
        }
      },
      {
        "fileData": {
          "fileUri": "https://generativelanguage.googleapis.com/v1beta/files/video2",
          "mimeType": "video/mp4"
        },
        "mediaResolution": {
          "level": "MEDIA_RESOLUTION_LOW"
        }
      },
      {"text": "Compare these two videos."}
    ]
  }],
  "generationConfig": {
    "mediaResolution": "MEDIA_RESOLUTION_MEDIUM"
  }
}
```

The per-part setting overrides the global `generationConfig.mediaResolution`.

---

## Vertex AI ingestion paths and limits

If you're using **Vertex AI** (rather than the direct Gemini API), you have additional ingestion options beyond the File API:

### Cloud Storage URI
- Point `fileUri` at a `gs://bucket/path/video.mp4` URI
- Must be in the same project or publicly accessible
- **2 GB** max object size (for gemini-2.0-flash / flash-lite)

### HTTP URL
- Point `fileUri` at a public HTTPS URL
- Hard limits per request:
  - **1 video file**
  - **1 audio file**
  - **Up to 10 images**
  - Each audio/video/document ≤ **15 MB**

### YouTube URL
- Exactly **1 YouTube URL** per request
- Must be public or owned by the project's service account
- **Preview status** (Pre-GA) — behavior may change

### Vertex AI Studio UI
- Supports direct upload, URL, YouTube, Cloud Storage, and Google Drive
- Google Drive uploads are limited: **10 MB total**, **7 MB per file**

The File API approach in Part 2 (resumable upload to `upload/v1beta/files`) remains the most flexible for large files: **2 GB per file**, **20 GB per project**, **48-hour expiration**.

---

## Best practices

These recommendations come directly from the Vertex AI documentation:

1. **Place video before text** — If there's a single video, put the `fileData` part before the `text` part in `contents`. This improves model attention.

2. **Prefer one video per prompt** — While up to 10 videos are supported, best quality comes from single-video analysis. Use multi-video only when comparison is the goal.

3. **Request timestamps explicitly** — Ask the model to output timestamps in the format matching your FPS (see table above).

4. **Adjust FPS for content type**:
   - **Lower than 1 FPS**: Lectures, talking heads, mostly static content
   - **Higher FPS**: Sports, action sequences, fast-moving visuals

5. **Slow down fast clips if needed** — At default 1 FPS, rapid action sequences may lose critical frames. If you can't increase FPS, consider slowing the clip (e.g., 0.5x speed) before upload.

---

## Known limitations

1. **Content moderation** — The model will refuse or sanitize outputs for videos that violate Google's safety policies. This is not bypassable via `safetySettings`.

2. **Non-speech audio recognition** — Models can be unreliable on non-speech sounds (sound effects, music, ambient noise). Speech transcription and understanding is much stronger.

3. **1 FPS default can miss action** — Fast movements between frame samples may not be captured. Use higher FPS or slower playback for action-critical analysis.

4. **Token budget for long videos** — Even with 1M tokens, very long videos at high resolution can exhaust context. The Part 2 script's chunking approach mitigates this.

5. **48-hour file expiration** — Files uploaded via the File API expire after 48 hours. For persistent workflows, re-upload or use Cloud Storage URIs (Vertex AI).

---

## Thinking level for video reasoning

Gemini 3 Pro introduces a `thinking_level` parameter that controls the depth of internal reasoning before generating a response. This is particularly useful for complex video analysis:

| Setting | Behavior | Best for |
|---------|----------|----------|
| `HIGH` (default) | Maximum reasoning, "Deep Think" mode | Complex cause-and-effect analysis, multi-step logic |
| `LOW` | Constrained reasoning, faster response | Simple queries, high-throughput batch processing |

Example usage in `generationConfig`:

```json
{
  "generationConfig": {
    "thinkingConfig": {
      "thinkingLevel": "HIGH"
    },
    "mediaResolution": "MEDIA_RESOLUTION_HIGH"
  }
}
```

When analyzing complex videos (e.g., "Why did the car crash?" or "Explain the physics of this golf swing"), `HIGH` enables the model to trace cause-and-effect relationships in the visual timeline rather than just describing what happened.

---

## Bounding box and spatial output format

When requesting object detection or spatial localization in video, Gemini 3 Pro returns bounding boxes in a specific format:

- **Coordinate system**: Normalized to `[0, 1000]` scale (0 = top/left, 1000 = bottom/right)
- **Box format**: `[ymin, xmin, ymax, xmax]` — note that Y comes first
- **Video responses**: Each detection includes a timestamp (MM:SS or milliseconds)

Example output for object tracking:

```json
[
  {
    "timestamp": "00:05",
    "label": "soccer ball",
    "box_2d": [550, 480, 590, 520]
  },
  {
    "timestamp": "00:06",
    "label": "soccer ball",
    "box_2d": [545, 495, 585, 535]
  }
]
```

**Note**: Gemini 3 Pro returns bounding boxes (rectangles) only—it does not currently support pixel-level segmentation masks.

## Tokens-per-minute (TPM) quotas (Vertex AI, 2.0 models)

If you're using **Gemini 2.0 Flash** or **2.0 Flash-Lite** on Vertex AI, be aware of regional TPM limits:

### Gemini 2.0 Flash
| Resolution | US / Asia | EU |
|------------|-----------|-----|
| High / Medium / Default | 38M TPM | 10M TPM |
| Low | 10M TPM | 2.5M TPM |

### Gemini 2.0 Flash-Lite
| Resolution | US / Asia | EU |
|------------|-----------|-----|
| High / Medium / Default | 38M TPM | 10M TPM |
| Low | 10M TPM | 2.5M TPM |

These quotas don't directly apply to Gemini 3 Pro, but matter if you're mixing models or using 2.x for cost-sensitive workloads.
