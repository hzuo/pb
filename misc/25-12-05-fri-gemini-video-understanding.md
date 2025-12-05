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
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro:generateContent?key=${GEMINI_API_KEY}" \
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
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro:generateContent?key=${GEMINI_API_KEY}" \
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
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro:generateContent?key=${GEMINI_API_KEY}" \
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
      "responseSchema": {
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
| GPT-5.1           | 75.2-80.4%       | -7.2 to -12.4    |
| Gemini 2.5 Flash  | 79.2%            | -8.4             |
| Claude Sonnet 4.5 | 68.4%            | -19.2            |
| GPT-4.1           | 60.9%            | -26.7            |

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
| Real-time streaming     | No      | **Yes**   | Yes      | Yes     |
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

Chunk a long video, send each chunk to Gemini 3 Pro via the REST API using only
`requests`, and then aggregate a global summary.

This is intentionally verbose and heavily commented so it doubles as a "lesson"
on long-video handling with Gemini.
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
from typing import Any, Dict, List, Optional

import requests

# ============================================================================
# TOP-LEVEL CONFIG (ALL YOUR KNOBS LIVE HERE)
# ============================================================================

# Where to read the API key from:
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"

# Base REST endpoint and model id for Gemini 3 Pro preview
GEMINI_API_BASE = "https://generativelanguage.googleapis.com"
GEMINI_MODEL = "gemini-3-pro-preview"  # from Gemini 3 dev guide

# ---- Task prompt -----------------------------------------------------------
# This describes *what* you want from the model. Tweak freely.

BASE_VIDEO_TASK_PROMPT = """
You are an expert multimodal analyst watching a long video on behalf of the user.

Your goals:
- Understand the story, structure, and key entities.
- Identify important scenes and turning points with approximate timestamps.
- Track evolving topics, arguments, or plot lines over time.
- Capture both high-level summary and important technical / visual details.

You will first analyze each video chunk separately, then a final pass will
combine all chunks into a global summary.
"""

# ---- Model/context-related knobs ------------------------------------------
# From the Gemini 3 Pro model card (Vertex docs): 1,048,576 input / 65,536 output tokens.
MODEL_MAX_INPUT_TOKENS = 1_048_576
MODEL_MAX_OUTPUT_TOKENS = 65_536

# From Gemini 3 Pro specs: max video length per request.
MODEL_MAX_VIDEO_LENGTH_WITH_AUDIO_SEC = 45 * 60      # ≈ 45 minutes
MODEL_MAX_VIDEO_LENGTH_WITHOUT_AUDIO_SEC = 60 * 60   # ≈ 60 minutes

# Files API hard limit (per-file).
FILES_API_MAX_BYTES_PER_FILE = 2 * 1024**3  # 2 GiB

# For long videos, we usually don't want to push right to those limits:
# - Smaller chunks are more robust to "context rot" and easier to debug.
# - 15–30 minutes is a nice balance.
TARGET_CHUNK_DURATION_SECONDS = 20 * 60  # default: 20 minutes

# Chunk-level strategy:
# - "independent": each chunk is summarized independently; final call stitches them.
# - "rolling": pass a running global summary into each chunk so the model can
#   maintain cross-chunk narrative continuity.
VIDEO_CHUNK_STRATEGY = "rolling"  # or "independent"

# Rough token heuristic for Gemini 3 video:
# Media resolution docs say Gemini 3's default video resolution uses ~70 tokens
# per frame; in practice the mapping to seconds is internal and opaque.
# We just use a conservative heuristic here so we *don't* plan absurdly large chunks.
APPROX_VIDEO_TOKENS_PER_SECOND = 70.0
VIDEO_TOKEN_BUDGET_FRACTION = 0.75  # reserve ~25% of context for text
TEXT_TOKEN_BUDGET = int(MODEL_MAX_INPUT_TOKENS * (1.0 - VIDEO_TOKEN_BUDGET_FRACTION))

# GenerationConfig: all the juicy sampling / output knobs.
# Names are what the REST API expects in the `generationConfig` object.
GENERATION_CONFIG: Dict[str, Any] = {
    # Sampling / decoding
    "temperature": 0.4,          # lower = more deterministic
    "topP": 0.9,
    "topK": 32,
    "candidateCount": 1,

    # Length / stopping
    "maxOutputTokens": 2048,     # per call; bumped for the final aggregator
    "stopSequences": [],         # e.g. ["</END>"]

    # Output format (JSON mode) – strongly encourages well-formed JSON.
    "responseMimeType": "application/json",

    # Media handling – global default for this request.
    # Options: MEDIA_RESOLUTION_UNSPECIFIED / MEDIA_RESOLUTION_LOW /
    #          MEDIA_RESOLUTION_MEDIUM / MEDIA_RESOLUTION_HIGH
    "mediaResolution": "MEDIA_RESOLUTION_UNSPECIFIED",

    # Optional penalties & determinism:
    # "presencePenalty": 0.0,
    # "frequencyPenalty": 0.0,
    # "seed": 42,
}

# Safety settings (optional). Leaving this empty uses model defaults.
SAFETY_SETTINGS: List[Dict[str, Any]] = [
    # Example:
    # {
    #     "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    #     "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    # },
]

# External tools – override with env vars if needed
FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "ffmpeg")
FFPROBE_BIN = os.environ.get("FFPROBE_BIN", "ffprobe")

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
# GENERIC HELPERS
# ============================================================================

def require_api_key() -> str:
    key = os.environ.get(GEMINI_API_KEY_ENV)
    if not key:
        print(
            f"ERROR: Please export {GEMINI_API_KEY_ENV}=<your Gemini API key> first.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def run_subprocess(cmd: List[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        print(
            f"ERROR: Command not found: {cmd[0]!r}. "
            "Install it or point FFMPEG_BIN/FFPROBE_BIN at the right binary.",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"ERROR running command: {' '.join(cmd)}", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)


def probe_video(path: Path) -> VideoMetadata:
    """Use ffprobe to get duration, detect audio, and file size."""
    cmd = [
        FFPROBE_BIN,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-show_streams",
        "-print_format",
        "json",
        str(path),
    ]
    result = run_subprocess(cmd)
    data = json.loads(result.stdout or "{}")

    duration_str = data.get("format", {}).get("duration", "0")
    try:
        duration = float(duration_str)
    except ValueError:
        duration = 0.0

    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))
    size_bytes = path.stat().st_size

    return VideoMetadata(
        path=path,
        duration_sec=duration,
        has_audio=has_audio,
        size_bytes=size_bytes,
    )


def estimate_max_video_seconds_for_tokens() -> float:
    """
    Heuristic upper bound on seconds of video per request from the token budget.

    For Gemini 3, media tokenization is a bit opaque (per-frame rather than
    fixed tokens per second), so we just use a conservative scalar here and
    leave plenty of slack in the 1M-token window.
    """
    if APPROX_VIDEO_TOKENS_PER_SECOND <= 0:
        return float("inf")
    video_token_budget = MODEL_MAX_INPUT_TOKENS * VIDEO_TOKEN_BUDGET_FRACTION
    return video_token_budget / APPROX_VIDEO_TOKENS_PER_SECOND


def plan_video_chunks(meta: VideoMetadata) -> List[ChunkPlan]:
    """
    Plan chunks that respect:
    - Model per-request video duration limits (≈45–60m).
    - Files API 2 GiB per-file limit.
    - Heuristic token budget (avoid stuffing the full 1M tokens with video).
    """
    if meta.duration_sec <= 0:
        return [ChunkPlan(index=0, start_sec=0.0, end_sec=0.0)]

    # 1) Model-level duration limit
    duration_limit = (
        MODEL_MAX_VIDEO_LENGTH_WITH_AUDIO_SEC
        if meta.has_audio
        else MODEL_MAX_VIDEO_LENGTH_WITHOUT_AUDIO_SEC
    )

    # 2) Files API size limit -> approximate max seconds per file
    if meta.size_bytes > FILES_API_MAX_BYTES_PER_FILE:
        bytes_per_sec = meta.size_bytes / meta.duration_sec
        max_sec_by_size = FILES_API_MAX_BYTES_PER_FILE / max(bytes_per_sec, 1e-6)
    else:
        max_sec_by_size = meta.duration_sec

    # 3) Token budget heuristic
    max_sec_by_tokens = estimate_max_video_seconds_for_tokens()

    hard_cap = min(duration_limit, max_sec_by_size, max_sec_by_tokens)

    # 4) Pick a comfortable target length below that cap
    target = min(TARGET_CHUNK_DURATION_SECONDS, hard_cap)
    target = max(target, 60.0)  # at least 1 minute per chunk

    if meta.duration_sec <= target:
        return [ChunkPlan(index=0, start_sec=0.0, end_sec=meta.duration_sec)]

    num_chunks = math.ceil(meta.duration_sec / target)
    chunk_len = meta.duration_sec / num_chunks

    chunks: List[ChunkPlan] = []
    for i in range(num_chunks):
        start = i * chunk_len
        end = meta.duration_sec if i == num_chunks - 1 else (i + 1) * chunk_len
        chunks.append(ChunkPlan(index=i, start_sec=start, end_sec=end))
    return chunks


def split_video_into_chunks(
    meta: VideoMetadata, chunks: List[ChunkPlan], out_dir: Path
) -> List[Path]:
    """
    Use ffmpeg to generate physical chunk files (stream-copy, no re-encode).
    """
    output_paths: List[Path] = []

    for chunk in chunks:
        out_path = (
            out_dir
            / f"{meta.path.stem}_chunk_{chunk.index:03d}_"
              f"{int(chunk.start_sec):06d}-{int(chunk.end_sec):06d}.mp4"
        )
        duration = max(chunk.end_sec - chunk.start_sec, 0.1)

        cmd = [
            FFMPEG_BIN,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{chunk.start_sec:.3f}",
            "-t",
            f"{duration:.3f}",
            "-i",
            str(meta.path),
            "-c",
            "copy",
            str(out_path),
        ]
        print(
            f"[ffmpeg] Creating chunk {chunk.index} "
            f"({chunk.start_sec:.1f}s–{chunk.end_sec:.1f}s)"
        )
        run_subprocess(cmd)
        output_paths.append(out_path)

    return output_paths


# ============================================================================
# GEMINI REST HELPERS (FILES API + GENERATECONTENT)
# ============================================================================

def upload_file_to_gemini(
    api_key: str, path: Path, mime_type: str, display_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a file via the Files API's resumable upload protocol.
    """
    num_bytes = path.stat().st_size
    display_name = display_name or path.name

    start_url = f"{GEMINI_API_BASE}/upload/v1beta/files?key={api_key}"
    start_headers = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(num_bytes),
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "Content-Type": "application/json",
    }
    start_body = {"file": {"display_name": display_name}}

    start_resp = requests.post(
        start_url, headers=start_headers, json=start_body, timeout=60
    )
    start_resp.raise_for_status()
    upload_url = start_resp.headers.get("X-Goog-Upload-Url")
    if not upload_url:
        raise RuntimeError("Upload URL missing from media.upload response")

    upload_headers = {
        "Content-Length": str(num_bytes),
        "X-Goog-Upload-Offset": "0",
        "X-Goog-Upload-Command": "upload, finalize",
    }
    with path.open("rb") as f:
        upload_resp = requests.post(
            upload_url, headers=upload_headers, data=f, timeout=600
        )
    upload_resp.raise_for_status()
    file_obj = upload_resp.json().get("file") or upload_resp.json()
    return file_obj


def get_file_metadata(api_key: str, file_name: str) -> Dict[str, Any]:
    url = f"{GEMINI_API_BASE}/v1beta/{file_name}"
    headers = {"x-goog-api-key": api_key}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json().get("file") or resp.json()


def wait_for_video_active(
    api_key: str, file_obj: Dict[str, Any], poll_seconds: int = 5
) -> Dict[str, Any]:
    """
    Poll Files API until the video is fully processed (state == ACTIVE).
    """
    name = file_obj.get("name")
    state = (file_obj.get("state") or "").upper()
    while state and state != "ACTIVE":
        print(f"[files] Video state = {state}, waiting {poll_seconds}s…")
        time.sleep(poll_seconds)
        file_obj = get_file_metadata(api_key, name)
        state = (file_obj.get("state") or "").upper()
    return file_obj


def prune_nones(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


def call_gemini_generate_content(
    api_key: str, model: str, payload: Dict[str, Any]
) -> Dict[str, Any]:
    url = f"{GEMINI_API_BASE}/v1beta/models/{model}:generateContent"
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=600)
    resp.raise_for_status()
    return resp.json()


def extract_first_candidate_text(resp: Dict[str, Any]) -> str:
    try:
        return resp["candidates"][0]["content"]["parts"][0].get("text", "")
    except Exception:
        # Fall back to the raw JSON if the shape is unexpected
        return json.dumps(resp, indent=2)


# ============================================================================
# PROMPTS, JSON SCHEMAS & CHUNK ANALYSIS
# ============================================================================

# JSON Schemas are optional but helpful when using JSON mode.
CHUNK_ANALYSIS_SCHEMA: Dict[str, Any] = {
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
                    "t_rel_sec": {"type": "number"},
                    "description": {"type": "string"},
                },
                "required": ["t_rel_sec", "description"],
            },
        },
        "key_entities": {"type": "array", "items": {"type": "string"}},
        "open_questions": {"type": "array", "items": {"type": "string"}},
        # Rolling-mode only:
        "updated_global_summary": {"type": "string"},
    },
    "required": ["chunk_index", "start_sec", "end_sec", "summary"],
}

FINAL_SUMMARY_SCHEMA: Dict[str, Any] = {
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


def build_chunk_prompt(
    chunk: ChunkPlan, total_chunks: int, global_summary: Optional[str]
) -> str:
    global_section = (global_summary or "").strip()
    return (
        f"{BASE_VIDEO_TASK_PROMPT.strip()}\n\n"
        f"You are currently analyzing chunk {chunk.index + 1} of {total_chunks} "
        f"of a longer video.\n"
        f"Chunk time range (seconds): {chunk.start_sec:.1f}–{chunk.end_sec:.1f}.\n\n"
        "If a global summary from previous chunks is provided, use it as context "
        "for continuity, but do not re-summarize it in detail.\n\n"
        "GLOBAL_SUMMARY_SO_FAR (may be empty):\n"
        f"{global_section if global_section else '<none>'}\n\n"
        "For this chunk ONLY:\n"
        "1. Describe what happens in this slice in concise prose.\n"
        "2. Extract a timeline of key events with approximate timestamps (in seconds\n"
        "   relative to the START of this chunk).\n"
        "3. List important people/objects/topics that appear or are mentioned.\n"
        "4. Note any questions or ambiguities that might be resolved later.\n"
        "5. Update the global summary so far in <=300 words, keeping it coherent\n"
        "   and non-redundant.\n\n"
        "Return ONLY a single JSON object with fields matching this JSON Schema:\n"
        f"{json.dumps(CHUNK_ANALYSIS_SCHEMA, indent=2)}"
    )


def analyze_chunk_with_gemini(
    api_key: str,
    chunk: ChunkPlan,
    video_file: Dict[str, Any],
    total_chunks: int,
    global_summary: Optional[str],
) -> Dict[str, Any]:
    """
    Send one chunk to Gemini 3 Pro and get back structured JSON for that chunk.
    """
    file_uri = (
        video_file.get("uri")
        or video_file.get("fileUri")
        or video_file.get("file_uri")
    )
    mime_type = (
        video_file.get("mimeType")
        or video_file.get("mime_type")
        or "video/mp4"
    )
    if not file_uri:
        raise RuntimeError("Uploaded file object is missing uri/file_uri")

    prompt_text = build_chunk_prompt(chunk, total_chunks, global_summary)

    payload: Dict[str, Any] = {
        "systemInstruction": {
            "role": "system",
            "parts": [{"text": BASE_VIDEO_TASK_PROMPT}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "fileData": {
                            "fileUri": file_uri,
                            "mimeType": mime_type,
                        }
                    },
                    {"text": prompt_text},
                ],
            }
        ],
        "generationConfig": prune_nones(GENERATION_CONFIG),
    }
    if SAFETY_SETTINGS:
        payload["safetySettings"] = SAFETY_SETTINGS

    resp = call_gemini_generate_content(api_key, GEMINI_MODEL, payload)
    text = extract_first_candidate_text(resp)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # If JSON mode is disobeyed, wrap raw text into a minimal structure.
        data = {
            "chunk_index": chunk.index,
            "start_sec": chunk.start_sec,
            "end_sec": chunk.end_sec,
            "summary": text,
            "timeline": [],
            "key_entities": [],
            "open_questions": [],
            "updated_global_summary": global_summary or text,
        }

    # Ensure mandatory fields exist
    data.setdefault("chunk_index", chunk.index)
    data.setdefault("start_sec", chunk.start_sec)
    data.setdefault("end_sec", chunk.end_sec)

    return data


def build_final_summary_prompt(chunk_results: List[Dict[str, Any]]) -> str:
    return (
        f"{BASE_VIDEO_TASK_PROMPT.strip()}\n\n"
        "You are now given structured analyses of each chunk of a long video.\n"
        "Each entry includes: chunk_index, start_sec, end_sec, summary, timeline,\n"
        "key_entities, open_questions, and updated_global_summary.\n\n"
        "Your job:\n"
        "1. Produce a coherent overall summary of the ENTIRE video.\n"
        "2. Identify key scenes or segments with approximate timestamps.\n"
        "3. List main characters/entities and their roles.\n"
        "4. Extract main topics/themes.\n"
        "5. Collect important questions that the video answers, and those it leaves\n"
        "   unresolved.\n\n"
        "Return ONLY a single JSON object matching this JSON Schema:\n"
        f"{json.dumps(FINAL_SUMMARY_SCHEMA, indent=2)}\n\n"
        "Here is the list of chunk analyses as JSON:\n"
        f"{json.dumps(chunk_results, indent=2)}"
    )


def aggregate_chunks_with_gemini(
    api_key: str, chunk_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Final "reduce" step: feed all chunk-level JSON to Gemini and ask for a
    global summary.
    """
    prompt = build_final_summary_prompt(chunk_results)

    config = dict(GENERATION_CONFIG)
    config["maxOutputTokens"] = min(int(MODEL_MAX_OUTPUT_TOKENS / 2), 4096)

    payload: Dict[str, Any] = {
        "systemInstruction": {
            "role": "system",
            "parts": [{"text": BASE_VIDEO_TASK_PROMPT}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": prune_nones(config),
    }
    if SAFETY_SETTINGS:
        payload["safetySettings"] = SAFETY_SETTINGS

    resp = call_gemini_generate_content(api_key, GEMINI_MODEL, payload)
    text = extract_first_candidate_text(resp)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {"overall_summary": text}

    return data


# ============================================================================
# MAIN CLI
# ============================================================================

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Chunk a long video and analyze it with Gemini 3 Pro via REST "
            "using only the `requests` library."
        )
    )
    parser.add_argument("video", type=Path, help="Path to the input video file (e.g. .mp4)")
    parser.add_argument(
        "--strategy",
        choices=["independent", "rolling"],
        default=VIDEO_CHUNK_STRATEGY,
        help="Chunk strategy: 'independent' summaries or 'rolling' global context.",
    )
    args = parser.parse_args(argv)

    api_key = require_api_key()
    meta = probe_video(args.video)

    print(f"Input video: {meta.path}")
    print(f"Duration: {meta.duration_sec/60:.1f} minutes")
    print(f"Size: {meta.size_bytes/1024/1024:.1f} MiB")
    print(f"Audio track present: {meta.has_audio}")
    print()

    chunks = plan_video_chunks(meta)
    print(f"Planned {len(chunks)} chunk(s):")
    for c in chunks:
        print(
            f"  Chunk {c.index}: {c.start_sec:.1f}s -> {c.end_sec:.1f}s "
            f"({(c.end_sec - c.start_sec)/60:.1f} min)"
        )
    print()

    with tempfile.TemporaryDirectory(prefix="gemini_video_chunks_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        print(f"Writing temporary chunks to {tmpdir}")
        chunk_paths = split_video_into_chunks(meta, chunks, tmpdir)

        chunk_results: List[Dict[str, Any]] = []
        global_summary: Optional[str] = None

        for chunk, chunk_path in zip(chunks, chunk_paths):
            print(f"\n=== Processing chunk {chunk.index + 1}/{len(chunks)}: {chunk_path.name} ===")
            file_obj = upload_file_to_gemini(
                api_key,
                chunk_path,
                mime_type="video/mp4",
                display_name=f"{meta.path.name} [chunk {chunk.index}]",
            )
            state = (file_obj.get("state") or "").upper()
            if state and state != "ACTIVE":
                print("[files] Waiting for video processing to finish…")
                file_obj = wait_for_video_active(api_key, file_obj)
            else:
                print("[files] Video already ACTIVE in Files API.")

            chunk_result = analyze_chunk_with_gemini(
                api_key=api_key,
                chunk=chunk,
                video_file=file_obj,
                total_chunks=len(chunks),
                global_summary=global_summary if args.strategy == "rolling" else None,
            )
            chunk_results.append(chunk_result)

            if args.strategy == "rolling":
                updated = chunk_result.get("updated_global_summary")
                if isinstance(updated, str) and updated.strip():
                    global_summary = updated

        print("\n=== Aggregating all chunks into a final summary ===")
        final_summary = aggregate_chunks_with_gemini(api_key, chunk_results)

    print("\n\n===== FINAL SUMMARY (JSON) =====")
    print(json.dumps(final_summary, indent=2, ensure_ascii=False))

    print("\n===== PER-CHUNK SUMMARIES (JSON) =====")
    print(json.dumps(chunk_results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

---

## 2. How this addresses your specific questions

### (1) Long video vs context window and “optimal slicing”

Key constraints (Gemini 3 Pro):

- **1,048,576 input tokens / 65,536 output tokens per request.**
- **Max ~45 minutes of video with audio (~60 minutes without) per request**, regardless of context window.
- **Files API per-file limit is 2 GB and 20 GB total per project.**

The script plans chunk sizes by taking the minimum of:

- That ~45 min model limit
- A 2 GB-per-file approximation based on bytes/sec
- A heuristic token budget (about 75% of the 1M context for video, leaving the rest for prompts and text)

Then it _further shrinks_ to a comfortable **20 min target**, because:

- Empirical work on “context rot” shows LLM quality can degrade as you approach the max context window and as information gets further from the prediction point.
- Smaller chunks also make failures (rate limits, safety blocks, etc.) easier to retry independently.

You can change `TARGET_CHUNK_DURATION_SECONDS` and `VIDEO_TOKEN_BUDGET_FRACTION` at the top if you want to push chunk sizes harder or be more conservative.

### (2) Independent chunks vs rolling context

There are two conceptual strategies:

1. **Independent chunks (map → reduce)**

   - Each chunk is summarized with no prior context.
   - A single final call ingests all chunk summaries and produces a global summary.
   - Pros: Simple, robust, cheap.
   - Cons: Local reasoning may miss cross-chunk threads (e.g. payoffs in chunk 7 for a setup in chunk 2).

2. **Rolling context (map w/ state → reduce)**

   - Each chunk sees a compressed “global summary so far”, and returns an `updated_global_summary` capped in length.
   - That updated summary is passed into the next chunk.
   - Pros: The model can maintain global narrative and evolving state (characters, topics, arguments).
   - Cons: Slightly more tokens per call; global summary may drift or over-compress if you don’t constrain it.

The script implements _both_; you pick with `--strategy` or the `VIDEO_CHUNK_STRATEGY` constant:

- In **rolling** mode, `global_summary` is fed into `build_chunk_prompt`, and each chunk returns an `updated_global_summary` which is then threaded forward.
- In **independent** mode, `global_summary` is always `None`, so each chunk is treated as fully local; the final aggregator call is then where cross-chunk stitching happens.

For most “watch & understand” use-cases I’d start with **rolling**; it tends to give more coherent global results without blowing up token usage, because each chunk is explicitly asked to keep the global summary under ~300 words.

### (3) “All the knobs” surfaced

The script exposes the important Gemini knobs in one place:

- **Model & endpoint**: `GEMINI_MODEL`, `GEMINI_API_BASE`
- **Generation config** (inside `GENERATION_CONFIG`):

  - `temperature`, `topP`, `topK`, `candidateCount`
  - `maxOutputTokens`, `stopSequences`
  - `response_mime_type` for JSON mode
  - `media_resolution` (low/medium/high/unspecified) to trade visual detail vs token usage & latency
  - (commented) `presencePenalty`, `frequencyPenalty`, `seed`

- **Safety**: `SAFETY_SETTINGS` stub you can fill with harm categories & thresholds.
- **Chunking**: `TARGET_CHUNK_DURATION_SECONDS`, `VIDEO_CHUNK_STRATEGY`, token heuristics & max-duration constants.
- **Tools**: `FFMPEG_BIN`, `FFPROBE_BIN` so you can swap binaries or container paths.

Everything else is plumbing: the script is meant to be executable as-is, but also readable enough that you can quickly tweak behavior for your specific pipelines (e.g. change the JSON schema, add additional passes like “speech-only transcription first, then visual analysis with the transcript re-injected” as suggested in Google’s own multimodal transcription guide).

If you tell me more about your exact target use-case (lecture summarization, security footage search, e-learning content, etc.), I can adjust the JSON schema & prompts to be more domain-specific.
