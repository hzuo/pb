---
filename: 2025-12-12-21-36-16-video-analysis-methodology-atlas-directed-deep-dives
timestamp: '2025-12-12T21:36:16.295087+00:00'
title: 'Video Analysis Methodology: Atlas + Directed Deep Dives'
---

Author: personalbot02-25-12-12-16-47-57-9d571aff-2962-407d-b969-8f1bfc71b0e9

# Video Analysis Methodology: Atlas + Directed Deep Dives

A systematic approach for extracting comprehensive understanding from video content using AI-powered transcription, semantic chunking, and targeted visual analysis.

## Overview

This methodology treats video analysis as a multi-pass process:

1. **Pass 1 - Audio Transcript**: Extract what was *said* (spoken content)
2. **Pass 2 - Semantic Chunks (Atlas)**: Extract what was *shown* (visual content + context)
3. **Pass 3 - Directed Deep Dives**: Zoom into specific segments with targeted questions

The key insight is that undirected summarization misses details. By first building an "atlas" of the video, you can then perform directed investigations into areas of interest or confusion.

## The Scripts

### Script 1: Audio Transcription Pipeline

**Location**: `~/git/howardbot/scripts/25-09-13-01-audio-transcribe-pipeline.py`

**Purpose**: Extracts audio from MP4, splits into ~5-minute chunks aligned to silence points, transcribes each chunk via OpenAI's `gpt-4o-transcribe`, and concatenates into a final markdown transcript.

**Usage**:
```bash
OPENAI_API_KEY=... ./25-09-13-01-audio-transcribe-pipeline.py /path/to/video.mp4 [--prompt "Domain terms..."]
```

**Output**: Creates a `<video>_transcription/` workspace with:
- `<video>.m4a` - Lossless audio extraction
- `chunks/<video>_5m_partNN.m4a` - Audio chunks
- `chunks/<video>_5m_partNN.json` - Transcription JSON per chunk
- `<video>_transcript.md` - Final concatenated transcript

### Script 2: Gemini Semantic Chunking

**Location**: `~/git/pb/scripts/25-12-10-wed-gemini-video-semantic-chunks.py`

**Purpose**: Uploads video to Gemini, analyzes in 10-minute segments, produces granular semantic chunks with timestamps, summaries, and detailed workflow descriptions.

**Usage**:
```bash
GEMINI_API_KEY=... uv run 25-12-10-wed-gemini-video-semantic-chunks.py video.mp4 -o chunks.json
```

**Output**: JSON array of semantic chunks, each with:
- `start_timestamp` / `end_timestamp`
- `summary` - 2-4 sentence narrative description
- `workflow_description` - Detailed UI/screen description (or null if no screen share)

## The Methodology

### Step 1: Generate Audio Transcript

```python
import subprocess
import os

video_path = "/path/to/video.mp4"
script_path = os.path.expanduser("~/git/howardbot/scripts/25-09-13-01-audio-transcribe-pipeline.py")

result = subprocess.run(
    [script_path, video_path],
    capture_output=True, text=True,
    env={**os.environ}
)
print(result.stdout)
```

**What you get**: Raw spoken content - the narrator's words, reasoning, informal commentary, domain explanations.

### Step 2: Generate Semantic Chunks (Atlas)

```python
script_path = os.path.expanduser("~/git/pb/scripts/25-12-10-wed-gemini-video-semantic-chunks.py")
output_path = "/path/to/chunks.json"

result = subprocess.run(
    ["uv", "run", script_path, video_path, "-o", output_path],
    capture_output=True, text=True,
    env={**os.environ}
)
print(result.stdout)
```

**What you get**: Visual content map - what's on screen, UI navigation, file structures, code visible.

### Step 3: Read and Synthesize

**This is a critical step. Do not rush it.**

#### Read Both Files IN FULL

Before attempting any deep dives, you MUST read both output files completely:

1. **The transcript markdown** - Every word the narrator said
2. **The chunks JSON** - Every chunk's summary and workflow_description

**Do not skim. Do not truncate. Do not summarize prematurely.**

| If you skip/skim... | You will... |
|---------------------|-------------|
| Parts of transcript | Miss context that explains what's on screen |
| Parts of chunks JSON | Not know which timestamps to zoom into |
| workflow_descriptions | Lose the visual context that complements audio |
| Either file | Ask redundant questions Gemini already answered |

#### Don't Fear Context Limits

These files are typically **well within context limits**:
- A 30-minute video transcript: ~8,000-15,000 words
- Chunks JSON for same video: ~30-50 chunks, ~10,000-20,000 words

**This is not a lot of text.** Read it all. Print it all. Do not use `[:1000]` or `head`. Do not ask for summaries of the files - you ARE the one who should be synthesizing.

#### How to Read

```python
import json

# Read transcript IN FULL - do not truncate
with open(f"{video_stem}_transcription/{video_stem}_transcript.md") as f:
    transcript = f.read()
print(transcript)  # Yes, print ALL of it. Read ALL of it.

# Read chunks IN FULL - do not truncate
with open("chunks.json") as f:
    chunks = json.load(f)

# Print every chunk - do not limit to first N
for i, chunk in enumerate(chunks):
    print(f"\n{'='*60}")
    print(f"CHUNK {i+1}: {chunk['start_timestamp']} - {chunk['end_timestamp']}")
    print(f"{'='*60}")
    print(f"SUMMARY: {chunk['summary']}")
    print(f"\nWORKFLOW: {chunk['workflow_description']}")
```

#### What Full Reading Gives You

After reading both files in their entirety, you will have:
- **Mental map** of the entire video's arc
- **Identified gaps** where transcript and chunks conflict or are vague
- **Specific timestamps** for deep dive targets
- **Domain vocabulary** to use in your deep dive questions
- **Context** to provide Gemini in your directed questions

At this point, you have ~80-90% understanding. Now identify gaps that warrant deep dives:
- Transcription errors (audio misheard domain terms)
- Ambiguous references ("offshore" - wind or team?)
- Exact values you need (file contents, column names)
- Code structure details

Only after completing this synthesis should you proceed to Step 4.

### Step 4: Directed Deep Dives

Upload video once, keep it server-side, then zoom into specific segments with targeted questions.

```python
import requests
import time
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_BASE = "https://generativelanguage.googleapis.com"

def upload_video(path):
    """Upload video and return file object."""
    num_bytes = os.path.getsize(path)

    # Start resumable upload
    start_resp = requests.post(
        f"{GEMINI_API_BASE}/upload/v1beta/files?key={GEMINI_API_KEY}",
        headers={
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(num_bytes),
            "X-Goog-Upload-Header-Content-Type": "video/mp4",
            "Content-Type": "application/json",
        },
        json={"file": {"display_name": "analysis-video"}},
        timeout=60,
    )
    start_resp.raise_for_status()
    upload_url = start_resp.headers.get("X-Goog-Upload-Url")

    print(f"Uploading {num_bytes / 1024**2:.1f} MB...")

    with open(path, "rb") as f:
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

def wait_for_active(file_obj, poll_sec=5):
    """Wait until video processing completes."""
    name = file_obj.get("name")
    while (file_obj.get("state") or "").upper() != "ACTIVE":
        print(f"  Processing... state={file_obj.get('state')}")
        time.sleep(poll_sec)
        resp = requests.get(
            f"{GEMINI_API_BASE}/v1beta/{name}",
            headers={"x-goog-api-key": GEMINI_API_KEY},
            timeout=30,
        )
        resp.raise_for_status()
        file_obj = resp.json()
    return file_obj

def deep_dive(file_uri, start_sec, end_sec, question, fps=1.0):
    """Zoom into specific segment with a directed question."""

    payload = {
        "contents": [{
            "parts": [
                {
                    "fileData": {"fileUri": file_uri, "mimeType": "video/mp4"},
                    "videoMetadata": {
                        "startOffset": {"seconds": int(start_sec)},
                        "endOffset": {"seconds": int(end_sec)},
                        "fps": fps,
                    },
                },
                {"text": question},
            ]
        }],
        "generationConfig": {
            "thinkingConfig": {"thinkingLevel": "HIGH"},
        },
    }

    resp = requests.post(
        f"{GEMINI_API_BASE}/v1beta/models/gemini-3-pro-preview:generateContent",
        headers={"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=300,
    )
    resp.raise_for_status()
    result = resp.json()

    # Extract text (skip thought parts)
    try:
        parts = result["candidates"][0]["content"]["parts"]
        for part in parts:
            if not part.get("thought"):
                return part.get("text", "")
    except (KeyError, IndexError):
        return str(result)

def delete_file(file_name):
    """Clean up uploaded video."""
    resp = requests.delete(
        f"{GEMINI_API_BASE}/v1beta/{file_name}",
        headers={"x-goog-api-key": GEMINI_API_KEY},
        timeout=30,
    )
    return resp.status_code in (200, 204)

# Usage:
file_obj = upload_video(video_path)
file_obj = wait_for_active(file_obj)
file_uri = file_obj.get("uri") or file_obj.get("fileUri")

# Now do targeted deep dives using the chunks atlas as your guide
answer = deep_dive(
    file_uri,
    start_sec=145,   # Use timestamps from chunks atlas
    end_sec=275,
    question="""Examine the spreadsheet shown. What are the exact column headers?
    What values appear in the 'Status' column? Be precise."""
)
print(answer)

# When done, clean up
delete_file(file_obj.get("name"))
```

### Providing Context to Gemini

When calling `deep_dive()`, remember that **Gemini only sees the small video segment and your question** - it has no knowledge of the rest of the video, the transcript, or your overall understanding.

**Empathize with the model**: You've read the full transcript and chunks atlas. Gemini hasn't. You need to bridge this gap by providing sufficient context in your question.

#### Bad Question (No Context)
```python
answer = deep_dive(
    file_uri,
    start_sec=740,
    end_sec=780,
    question="What does she say about Claude?"
)
```
Gemini doesn't know who "she" is, what Claude refers to, or why this matters.

#### Good Question (With Context)
```python
answer = deep_dive(
    file_uri,
    start_sec=740,
    end_sec=780,
    question="""This video is a knowledge transfer recording by Kate, an engineer
explaining the SPP (Southwest Power Pool) queue update workflow. She's walking
through a Jupyter notebook that processes generator interconnection data.

At this point in the video, she mentions using "Claude" (an AI assistant) to
help clean up the notebook code.

Please examine this segment and tell me:
1. What specific code cells or output are visible when she makes this comment?
2. What exactly looks "redundant" or "repeating" that she's referring to?
3. What are the variable names visible in the code?

I want to understand what Claude's cleanup produced and what the redundancy looks like."""
)
```

#### Context Template

For directed deep dives, structure your question like this:

```
[BACKGROUND]
Brief description of the overall video content and narrator.

[LOCAL CONTEXT]
What's happening at this point based on your atlas/transcript reading.

[SPECIFIC QUESTIONS]
Numbered list of precise things you want to know.

[PURPOSE]
Why you're asking - helps the model prioritize what to look for.
```

#### What Context to Include

| Include | Why |
|---------|-----|
| Who is speaking | Gemini may not recognize the narrator |
| Domain/topic | Technical terms need framing |
| What just happened | Continuity from previous segments |
| What you already know | Prevents redundant explanations |
| What's confusing you | Focuses the model's attention |

#### What NOT to Include

- Don't dump the entire transcript (too long, dilutes focus)
- Don't provide wrong assumptions (biases the model)
- Don't ask 10 questions at once (pick 3-5 max)

This context-setting is what makes deep dives powerful - you're combining your global understanding with Gemini's ability to see the actual pixels and hear the actual audio.

### Types of Deep Dive Questions

**Correcting transcription errors**:
> "The transcript says 'DICES' but what text actually appears on screen in the Cluster column?"

**Clarifying ambiguous terms**:
> "The code mentions 'offshore_mapping_task'. Is this about offshore wind projects or an offshore team? Look at context clues."

**Extracting exact values**:
> "What are the exact contents of dispatch_adjustment.csv? List all key-value pairs visible."

**Understanding code structure**:
> "What function is defined at this moment? What are its parameters and what does it return?"

**Verifying relationships**:
> "How does the control_area file map utilities to geographic groups? Show specific examples."

## When to Use Each Pass

| Pass | Best For | Misses |
|------|----------|--------|
| Audio Transcript | Reasoning, explanations, informal comments, domain knowledge | Visual content, exact spellings, code |
| Semantic Chunks | UI navigation, file structures, what's on screen | Nuance, exact values, deep detail |
| Deep Dives | Exact values, correcting errors, resolving ambiguity | Inefficient for broad coverage |

## Example Revelations from Deep Dives

In a real analysis, deep dives revealed:

1. **Transcription error**: Audio said "DICES" but screen showed "DISIS" (Definitive Interconnection System Impact Study)
2. **Jargon clarification**: "offshore" referred to an offshore data entry team, not offshore wind
3. **Exact file structure**: dispatch_adjustment.csv contained `prior_q_gen_pct_region_5, 0.46`
4. **Hidden context**: Light load case was commented out in code, only Summer/Winter Peak remained

## Tips

- **Use chunks as timestamps**: The atlas tells you where to look (e.g., "13:45 - POI changes discussed")
- **Ask specific questions**: "What columns are visible?" beats "What's happening?"
- **Iterate**: Follow up if the answer raises new questions
- **Cross-reference**: Compare what transcript says vs. what screen shows
- **Clean up**: Always delete uploaded video when done

---

## Appendix A: Audio Transcription Script

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
# ]
# ///

"""
Audio transcription pipeline (mp4 -> workspace with lossless audio, 5m chunks aligned to silence, transcripts, final markdown).

- Input: path to an .mp4 video file (positional arg)
- Workspace: created adjacent to the input, named "<stem>_transcription"
  - <stem>.m4a (lossless audio stream copy)
  - chunks/<stem>_5m_partNN.m4a
  - chunks/<stem>_5m_partNN.json (OpenAI gpt-4o-transcribe output)
  - <stem>_transcript.md (concatenated text with part headers)
- Best practices: server-side VAD (`chunking_strategy={"type":"server_vad"}`), language=en, response_format=json, temperature=0, strict guard on usage.output_tokens < 2000
- Happy path only: minimal error handling; failures raise.

Usage:
  OPENAI_API_KEY=... ./25-09-13-01-audio-transcribe-pipeline.py /path/to/file.mp4 [--prompt "Domain jargon, names, terms..."]
"""

from __future__ import annotations

import argparse
import bisect
import json
import math
import os
import subprocess
from array import array
from pathlib import Path

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")
CURL = os.environ.get("CURL", "curl")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def ffprobe_duration(path: Path) -> float:
    cmd = [
        FFPROBE,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(path),
    ]
    out = run(cmd).stdout
    return float(json.loads(out)["format"]["duration"])


def extract_audio_lossless(mp4: Path, out_m4a: Path) -> None:
    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-nostats",
        "-v",
        "error",
        "-i",
        str(mp4),
        "-vn",
        "-map",
        "0:a:0",
        "-c:a",
        "copy",
        str(out_m4a),
    ]
    run(cmd)


def pcm_envelope(
    audio_m4a: Path, ar: int = 4000, win_sec: float = 0.50, step_sec: float = 0.25
) -> tuple[list[float], list[float]]:
    cmd = [
        FFMPEG,
        "-hide_banner",
        "-nostats",
        "-v",
        "error",
        "-i",
        str(audio_m4a),
        "-ac",
        "1",
        "-ar",
        str(ar),
        "-f",
        "s16le",
        "pipe:1",
    ]
    proc = subprocess.run(cmd, check=True, capture_output=True)
    raw = proc.stdout
    n = len(raw) // 2
    samples = array("h")
    samples.frombytes(raw[: n * 2])

    win = int(win_sec * ar)
    step = int(step_sec * ar)
    times: list[float] = []
    vals: list[float] = []
    for start in range(0, n - win + 1, step):
        window = samples[start : start + win]
        ssum = 0
        for v in window:
            ssum += v * v
        rms = math.sqrt(ssum / len(window))
        t = (start + win / 2) / ar
        times.append(t)
        vals.append(rms)
    return times, vals


def pick_cut(
    target: float,
    rms_times: list[float],
    rms_vals: list[float],
    window: float = 30.0,
    widen_to: float = 90.0,
) -> float:
    i0 = bisect.bisect_left(rms_times, target - window)
    i1 = bisect.bisect_right(rms_times, target + window)
    if i0 >= i1:
        i0 = bisect.bisect_left(rms_times, target - widen_to)
        i1 = bisect.bisect_right(rms_times, target + widen_to)
        if i0 >= i1:
            j = bisect.bisect_left(rms_times, target)
            j = max(0, min(j, len(rms_times) - 1))
            return rms_times[j]
    min_idx = i0
    min_val = rms_vals[i0]
    for k in range(i0 + 1, i1):
        v = rms_vals[k]
        if v < min_val:
            min_val = v
            min_idx = k
    return rms_times[min_idx]


def build_boundaries_5m(
    total: float, rms_times: list[float], rms_vals: list[float]
) -> list[float]:
    targets = [t for t in (i * 300.0 for i in range(1, 100)) if t < total]
    cuts = [pick_cut(t, rms_times, rms_vals) for t in targets]
    return [0.0] + cuts + [total]


def split_copy(
    audio_m4a: Path, boundaries: list[float], chunks_dir: Path, stem: str
) -> list[Path]:
    chunks_dir.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []
    for idx in range(len(boundaries) - 1):
        start = round(boundaries[idx], 3)
        end = round(boundaries[idx + 1], 3)
        dur = round(max(0.0, end - start), 3)
        outp = chunks_dir / f"{stem}_5m_part{idx + 1:02d}.m4a"
        cmd = [
            FFMPEG,
            "-y",
            "-hide_banner",
            "-nostats",
            "-v",
            "error",
            "-i",
            str(audio_m4a),
            "-ss",
            f"{start:.3f}",
            "-t",
            f"{dur:.3f}",
            "-map",
            "0:a:0",
            "-c",
            "copy",
            "-avoid_negative_ts",
            "make_zero",
            "-fflags",
            "+genpts",
            "-reset_timestamps",
            "1",
            str(outp),
        ]
        run(cmd)
        out_paths.append(outp)
    return out_paths


def transcribe_chunk(cf: Path, prompt: str | None) -> dict:
    url = "https://api.openai.com/v1/audio/transcriptions"
    api_key = os.environ["OPENAI_API_KEY"]
    cmd = [
        CURL,
        "-sS",
        url,
        "-H",
        f"Authorization: Bearer {api_key}",
        "-H",
        "Content-Type: multipart/form-data",
        "-F",
        "model=gpt-4o-transcribe",
        "-F",
        f"file=@{cf}",
        "-F",
        "language=en",
        "-F",
        "response_format=json",
        "-F",
        "temperature=0",
        "-F",
        'chunking_strategy={"type":"server_vad"}',
    ]
    if prompt:
        cmd += ["-F", f"prompt={prompt}"]
    out = run(cmd).stdout
    data = json.loads(out)
    if "usage" not in data:
        raise RuntimeError(f"missing usage in response for {cf.name}")
    tok = data["usage"].get("output_tokens")
    if tok is None:
        raise RuntimeError(f"missing usage.output_tokens for {cf.name}")
    if tok >= 2000:
        raise RuntimeError(f"output truncated (>=2000 tokens) for {cf.name}: {tok}")
    return data


def _mmss(t: float) -> str:
    t = max(0.0, float(t))
    m = int(t // 60)
    s = int(t - m * 60)
    return f"{m}:{s:02d}"


def concat_markdown(
    json_files: list[Path], boundaries: list[float], out_md: Path, title: str
) -> None:
    parts_md: list[str] = []
    for i, jf in enumerate(json_files, start=1):
        start = boundaries[i - 1]
        end = boundaries[i]
        d = json.loads(jf.read_text(encoding="utf-8"))
        txt = (d.get("text") or "").strip()
        header = f"## Part {i} ({_mmss(start)}-{_mmss(end)})"
        section = header + ("\n\n" + txt if txt else "")
        parts_md.append(section)
    body = "\n\n".join(parts_md)
    md = f"# {title}\n\n" + body
    out_md.write_text(md, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(
        description="mp4 -> workspace with lossless audio, 5m chunks, transcripts, unified markdown"
    )
    ap.add_argument("input_mp4", type=Path, help="Path to input .mp4")
    ap.add_argument(
        "--prompt", type=str, default=None, help="Optional prompt to bias transcription"
    )
    args = ap.parse_args()

    inp: Path = args.input_mp4
    prompt: str | None = args.prompt

    parent = inp.parent
    stem = inp.stem
    workspace = parent / f"{stem}_transcription"
    chunks_dir = workspace / "chunks"
    workspace.mkdir(parents=True, exist_ok=True)

    audio_full = workspace / f"{stem}.m4a"
    print(f"[1/6] Extracting audio -> {audio_full}")
    extract_audio_lossless(inp, audio_full)

    print("[2/6] Probing duration")
    total = ffprobe_duration(audio_full)

    print("[3/6] Building RMS envelope and choosing ~5m silence-aligned cut points")
    rms_times, rms_vals = pcm_envelope(audio_full, ar=4000, win_sec=0.50, step_sec=0.25)
    boundaries = build_boundaries_5m(total, rms_times, rms_vals)
    print(f"  - boundaries: {[_mmss(b) for b in boundaries]}")

    print(f"[4/6] Splitting into {len(boundaries) - 1} chunks (AAC stream copy)")
    chunk_paths = split_copy(audio_full, boundaries, chunks_dir, stem)

    print("[5/6] Transcribing chunks via OpenAI (gpt-4o-transcribe)")
    json_paths: list[Path] = []
    for cf in chunk_paths:
        data = transcribe_chunk(cf, prompt)
        jf = cf.with_suffix(".json")
        jf.write_text(json.dumps(data, indent=2), encoding="utf-8")
        json_paths.append(jf)
        tok = data["usage"]["output_tokens"]
        print(f"  - {cf.name}: output_tokens={tok}")

    out_md = workspace / f"{stem}_transcript.md"
    print(f"[6/6] Concatenating transcript -> {out_md}")
    concat_markdown(json_paths, boundaries, out_md, f"Transcript: {stem}")

    print("Done.")
    print(f"Workspace: {workspace}")


if __name__ == "__main__":
    main()

```

---

## Appendix B: Gemini Semantic Chunking Script

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "requests>=2.32.5",
# ]
# ///

"""
gemini-video-semantic-chunks.py

Semantically chunk a video using Gemini 3 Pro. The model analyzes the video
in configurable segments (default 10 minutes) and breaks each down into
granular sub-minute semantic chunks with detailed summaries.

Usage:
    uv run gemini-video-semantic-chunks.py video.mp4
    uv run gemini-video-semantic-chunks.py video.mp4 --context "Meeting between Alice and Bob about Q4 planning"
    uv run gemini-video-semantic-chunks.py video.mp4 -o chunks.json

The output is a JSON array of semantic chunks, each with:
- start_timestamp: Start timestamp in MM:SS or H:MM:SS format
- end_timestamp: End timestamp in MM:SS or H:MM:SS format
- summary: Detailed description of what happens in this chunk
- workflow_description: Detailed workflow description when workflow is being shown, null otherwise

Design notes:
- Uses Gemini 3 Pro defaults (temperature=1.0, thinkingLevel=HIGH)
- Only overrides responseMimeType and responseJsonSchema for structured output
- Rolling context: each segment receives summaries of all prior segments (not individual chunks)
- Biases towards granular sub-minute chunks with multiple sentences each

Author: personalbot02-25-12-10-22-21-08-82ea23b7-710c-49ee-9334-1f49dd278328
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


def indent_lines(text: str, prefix: str = "    ") -> str:
    """Indent each line of text with the given prefix."""
    return "\n".join(prefix + line for line in text.splitlines())


# ============================================================================
# CONFIG
# ============================================================================

GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com"
GEMINI_MODEL = "gemini-3-pro-preview"

# Default 10 minutes per API call - well under the 45-min limit for video with audio
DEFAULT_SEGMENT_DURATION_MIN = 10

# Default frame rate for video sampling (valid range: 0 < fps <= 24.0)
DEFAULT_FPS = 1.0

# System instruction for semantic chunking
SYSTEM_INSTRUCTION = """
You are an expert video analyst creating semantic segmentations of video content.

Your task is to break down video content into small, semantically meaningful chunks.

## Chunking Guidelines

- **Be granular**: Prefer many small chunks over few large ones
- **Sub-minute chunks**: Most chunks should be 10-60 seconds, rarely longer
- **Topic boundaries**: Start a new chunk when the topic, speaker focus, or workflow step changes
- **Strict contiguity**: Each chunk's start_timestamp must exactly equal the previous chunk's end_timestamp. No gaps. First chunk starts at segment start, last chunk ends at segment end.

## For Each Chunk Provide

1. **start_timestamp**: When this semantic chunk begins in MM:SS format (or H:MM:SS if >= 1 hour). Time from VIDEO START, not segment start.
2. **end_timestamp**: When this semantic chunk ends in MM:SS format (must equal next chunk's start_timestamp). Also relative to video start.
3. **summary**: 2-4 sentence narrative description of what happens
4. **workflow_description**: See below

## workflow_description

This field captures workflow information when a screen is being shared, and a workflow is being shown.

**Set to null when**: No screen is being shared, or no workflow is being shown (e.g., just people talking on webcam, a conversation without screen visuals)

**When a screen IS being shared**: Write an EXTREMELY DETAILED tutorial-style description that would enable someone to replicate the exact workflow without watching the video.

Be verbose and specific. Describe:
- **Every visible UI element**: application name, page title, sidebar menus, tabs, buttons, toolbars, panels
- **All readable text**: transcribe headers, labels, button text, menu items, field values, table data, URLs exactly as shown
- **Each action taken**: "The user clicks the 'Dashboards' item in the left sidebar" - specify what was clicked and where
- **Every transition**: what appears after each click, loading states, panels opening, data populating, fully describe every state transition
- **Table contents**: column headers AND the actual data values in visible rows
- **Form contents**: field labels AND their current values

Litmus Test: The workflow should be **perfectly reproducible** solely on the basis of your description. If someone would struggle to reproduce the workflow solely on the basis of workflow_description, introduce additional detail and precision until it is clear that they would no longer struggle.

Write in flowing, detailed prose. Imagine you're writing a step-by-step tutorial for someone who cannot see the screen. Include every detail they would need to follow along and perform the same actions.
""".strip()

# Output schema for semantic chunks
SEMANTIC_CHUNKS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "segment_start_timestamp": {
            "type": "string",
            "description": "Start of the analyzed segment in MM:SS or H:MM:SS format",
        },
        "segment_end_timestamp": {
            "type": "string",
            "description": "End of the analyzed segment in MM:SS or H:MM:SS format",
        },
        "chunks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start_timestamp": {
                        "type": "string",
                        "description": "Start timestamp in MM:SS or H:MM:SS format, e.g. '08:50' or '1:05:12'. This should be absolute and relative to the start of the full video, not the start of this particular segment. So use the segment_start_timestamp as the base.",
                    },
                    "end_timestamp": {
                        "type": "string",
                        "description": "End timestamp in MM:SS or H:MM:SS format. Also relative to video start.",
                    },
                    "summary": {
                        "type": "string",
                        "description": "Comprehensive description of this chunk. Typically at least 2-4 sentences.",
                    },
                    "workflow_description": {
                        "type": ["string", "null"],
                        "description": "Comprehensive description of screen content and actions if a workflow is being shown. Typically at least 100-200 words. Null if no workflow is being shown.",
                    },
                },
                "required": [
                    "start_timestamp",
                    "end_timestamp",
                    "summary",
                    "workflow_description",
                ],
            },
        },
        "segment_summary": {
            "type": "string",
            "description": "Overall summary of this segment, particularly focusing on context relevant for interpreting future segments. Typically at least 4 sentences.",
        },
    },
    "required": [
        "segment_start_timestamp",
        "segment_end_timestamp",
        "chunks",
        "segment_summary",
    ],
}

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
class Segment:
    """A segment of video to analyze in a single API call."""

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


def run_subprocess(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit(f"ERROR: {cmd[0]} not found. Install ffmpeg/ffprobe.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"ERROR: {' '.join(cmd)}\n{e.stderr}")


def probe_video(path: Path) -> VideoMetadata:
    """Get video metadata via ffprobe."""
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

    duration = float(data.get("format", {}).get("duration", 0))
    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))

    return VideoMetadata(
        path=path,
        duration_sec=duration,
        has_audio=has_audio,
        size_bytes=path.stat().st_size,
    )


def plan_segments(meta: VideoMetadata, segment_duration_sec: int) -> list[Segment]:
    """Plan segments for API calls based on specified duration."""
    if meta.duration_sec <= 0:
        return []

    if meta.duration_sec <= segment_duration_sec:
        return [Segment(0, 0, meta.duration_sec)]

    num_segments = math.ceil(meta.duration_sec / segment_duration_sec)

    return [
        Segment(
            index=i,
            start_sec=i * segment_duration_sec,
            end_sec=min((i + 1) * segment_duration_sec, meta.duration_sec),
        )
        for i in range(num_segments)
    ]


def format_timestamp(seconds: float) -> str:
    """
    Format seconds as MM:SS or H:MM:SS.

    Examples: 0 -> '00:00', 90 -> '01:30', 3809 -> '1:03:29'
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# ============================================================================
# FILES API
# ============================================================================


def upload_file(
    api_key: str,
    path: Path,
    mime_type: str = "video/mp4",
    display_name: str | None = None,
) -> dict:
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
        state = file_obj.get("state")
        eprint(f"  [files] state={state}, waiting {poll_sec}s...")
        time.sleep(poll_sec)
        resp = requests.get(
            f"{GEMINI_API_BASE}/v1beta/{name}",
            headers={"x-goog-api-key": api_key},
            timeout=30,
        )
        resp.raise_for_status()
        file_obj = resp.json()
    return file_obj


def delete_remote_file(api_key: str, file_name: str) -> None:
    """Delete a file from Gemini storage."""
    url = f"{GEMINI_API_BASE}/v1beta/{file_name}"
    resp = requests.delete(url, headers={"x-goog-api-key": api_key}, timeout=30)
    if resp.status_code not in (200, 404):
        eprint(f"  [cleanup] Warning: Failed to delete {file_name}")


def get_file_uri(file_obj: dict) -> str:
    """Extract file URI from file object."""
    uri = file_obj.get("uri") or file_obj.get("fileUri")
    if not uri:
        raise RuntimeError(f"No URI found in file object: {file_obj}")
    return uri


# ============================================================================
# GENERATE CONTENT
# ============================================================================


def call_generate_content(api_key: str, payload: dict) -> dict:
    """Call generateContent endpoint with exponential backoff retry."""
    retryable_status_codes = {429, 500, 502, 503, 504}
    max_backoff_sec = 60

    url = f"{GEMINI_API_BASE}/v1beta/models/{GEMINI_MODEL}:generateContent"
    headers = {"x-goog-api-key": api_key, "Content-Type": "application/json"}

    backoff = 1.0
    while True:
        resp = requests.post(url, headers=headers, json=payload, timeout=600)

        if resp.ok:
            return resp.json()

        if resp.status_code in retryable_status_codes:
            eprint(f"  [retry] {resp.status_code}: {resp.text}")
            eprint(f"  [retry] Backing off {backoff:.1f}s...")
            time.sleep(backoff)
            backoff = min(backoff * 2, max_backoff_sec)
            continue

        # Non-retryable error
        eprint(f"API Error: {resp.text}")
        resp.raise_for_status()


def extract_text(resp: dict) -> str:
    """Extract text from generateContent response."""
    try:
        parts = resp["candidates"][0]["content"]["parts"]
        # Skip thought parts, get the actual response
        for part in parts:
            if not part.get("thought"):
                return part.get("text", "")
        return ""
    except (KeyError, IndexError):
        return json.dumps(resp, indent=2)


def analyze_segment(
    api_key: str,
    file_uri: str,
    segment: Segment,
    total_segments: int,
    prior_segment_summaries: list[dict],
    user_context: str | None,
    fps: float = DEFAULT_FPS,
    verbose: bool = False,
) -> tuple[list[dict], str]:
    """Analyze a video segment and extract semantic chunks.

    Returns:
        Tuple of (chunks, segment_summary)
    """

    # Build the user prompt
    prompt_parts = []

    # Rolling context from prior segment summaries
    if prior_segment_summaries:
        prior_context = "\n".join(
            f"[{s['start_timestamp']}-{s['end_timestamp']}] {s['summary']}"
            for s in prior_segment_summaries
        )
        prompt_parts.append(f"PRIOR SEGMENTS (for context):\n{prior_context}\n")

    prompt_parts.append(
        textwrap.dedent(
            f"""
            CURRENT SEGMENT: {format_timestamp(segment.start_sec)} to {format_timestamp(segment.end_sec)} (segment {segment.index + 1} of {total_segments})

            Analyze this segment and break it into granular semantic chunks.

            Follow these guidelines:
            - Maximize the amount of information you extract from both the video and audio.
            - Describe everything that happens in the segment in great detail.
            - Both the `summary` and `workflow_description` are expected to be very verbose, do not shy away from verbosity.
            - If someone reads the `summary` and the `workflow_description` for every chunk, they should be fully caught up on EVERYTHING that happens in the segment.
            - In other words, if they read your complete output, they should miss nothing if they were to never watch this segment. Ensure this holds true.
            - Be maximally comprehensive.
            """
        ).strip()
    )

    # User context goes after video (per best practices)
    if user_context:
        prompt_parts.append(f"\nADDITIONAL CONTEXT FROM USER:\n{user_context}")

    prompt = "\n\n".join(prompt_parts)

    payload: dict[str, Any] = {
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": [
            {
                "parts": [
                    {
                        "fileData": {"fileUri": file_uri, "mimeType": "video/mp4"},
                        "videoMetadata": {
                            "startOffset": {"seconds": int(segment.start_sec)},
                            "endOffset": {"seconds": int(segment.end_sec)},
                            "fps": fps,
                        },
                    },
                    {"text": prompt},
                ]
            }
        ],
        "generationConfig": {
            # Only pass what differs from defaults
            "responseMimeType": "application/json",
            "responseJsonSchema": SEMANTIC_CHUNKS_SCHEMA,
            "thinkingConfig": {
                "thinkingLevel": "HIGH",
                "includeThoughts": True,
            },
        },
    }

    if verbose:
        eprint(f"\n  [request] Sending to {GEMINI_MODEL}...")
        eprint(f"  [request] Segment: {segment.start_sec}s - {segment.end_sec}s")
        eprint(f"  [request] Prior segment summaries: {len(prior_segment_summaries)}")

    resp = call_generate_content(api_key, payload)

    if verbose:
        # Print usage metadata
        usage = resp.get("usageMetadata", {})
        eprint("  [response] usageMetadata:")
        eprint(indent_lines(json.dumps(usage, indent=2)))

        # Print thoughts if present
        try:
            parts = resp["candidates"][0]["content"]["parts"]
            for part in parts:
                if part.get("thought"):
                    thought_text = part.get("text", "")
                    eprint(f"  [response] Model thinking ({len(thought_text)} chars):")
                    eprint(indent_lines(thought_text.strip()))
                    eprint()
        except (KeyError, IndexError):
            pass

    text = extract_text(resp)

    try:
        data = json.loads(text)
        chunks = data.get("chunks", [])
        segment_summary = data.get("segment_summary", "")
        if verbose:
            eprint(f"  [response] Chunks ({len(chunks)}):")
            eprint(indent_lines(json.dumps(chunks, indent=2)))
            eprint()
            eprint(f"  [response] Segment summary: {segment_summary}")
        return chunks, segment_summary
    except json.JSONDecodeError:
        eprint("Warning: Failed to parse response as JSON")
        return [], ""


# ============================================================================
# MAIN
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Semantically chunk a video using Gemini 3 Pro"
    )
    parser.add_argument("video", type=Path, help="Path to video file")
    parser.add_argument(
        "-c",
        "--context",
        type=str,
        default=None,
        help="Additional context for the AI (e.g., participant names, meeting topic)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output JSON file (default: stdout)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output: print requests, responses, and usage metadata to stderr",
    )
    parser.add_argument(
        "--segment-minutes",
        type=int,
        default=DEFAULT_SEGMENT_DURATION_MIN,
        metavar="MIN",
        help=f"Duration of each analysis segment in minutes (default: {DEFAULT_SEGMENT_DURATION_MIN})",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=DEFAULT_FPS,
        metavar="FPS",
        help=f"Frame rate for video sampling, range (0, 24.0] (default: {DEFAULT_FPS})",
    )
    args = parser.parse_args()

    if not args.video.exists():
        sys.exit(f"ERROR: Video file not found: {args.video}")

    if args.segment_minutes < 1:
        sys.exit("ERROR: --segment-minutes must be at least 1")

    if not (0 < args.fps <= 24.0):
        sys.exit("ERROR: --fps must be in range (0, 24.0]")

    if args.video.suffix.lower() != ".mp4":
        sys.exit("ERROR: Only .mp4 files are supported")

    api_key = require_api_key()
    meta = probe_video(args.video)

    if meta.duration_sec <= 0:
        sys.exit("ERROR: Could not determine video duration")

    eprint(f"Video: {meta.path}")
    eprint(
        f"Duration: {format_timestamp(meta.duration_sec)} ({meta.duration_sec:.1f}s)"
    )
    eprint(f"Size: {meta.size_bytes / 1024**2:.1f} MB")
    eprint(f"Audio: {meta.has_audio}")

    # Plan segments
    segment_duration_sec = args.segment_minutes * 60
    segments = plan_segments(meta, segment_duration_sec)
    eprint(f"\nPlanned {len(segments)} segment(s) of {args.segment_minutes} min each")

    # Upload video once
    eprint("\nUploading video...")
    if args.verbose:
        eprint(f"  [upload] File: {meta.path}")
        eprint(f"  [upload] Size: {meta.size_bytes} bytes")
    file_obj = upload_file(api_key, meta.path)
    if args.verbose:
        eprint("  [upload] Response:")
        eprint(indent_lines(json.dumps(file_obj, indent=2)))
    file_obj = wait_for_active(api_key, file_obj)
    file_uri = get_file_uri(file_obj)
    eprint(f"  Ready: {file_uri}")

    # Process each segment with rolling context
    all_chunks: list[dict] = []
    segment_summaries: list[dict] = []

    try:
        for segment in segments:
            eprint(
                f"\n=== Segment {segment.index + 1}/{len(segments)} "
                f"({format_timestamp(segment.start_sec)}-{format_timestamp(segment.end_sec)}) ==="
            )

            chunks, segment_summary = analyze_segment(
                api_key=api_key,
                file_uri=file_uri,
                segment=segment,
                total_segments=len(segments),
                prior_segment_summaries=segment_summaries,
                user_context=args.context,
                fps=args.fps,
                verbose=args.verbose,
            )

            eprint(f"\n  Found {len(chunks)} semantic chunks")
            all_chunks.extend(chunks)

            # Track segment summary for rolling context
            segment_summaries.append(
                {
                    "start_timestamp": format_timestamp(segment.start_sec),
                    "end_timestamp": format_timestamp(segment.end_sec),
                    "summary": segment_summary,
                }
            )

    finally:
        # Clean up uploaded file
        if file_obj and file_obj.get("name"):
            eprint(f"\n[cleanup] Deleting {file_obj['name']}...")
            delete_remote_file(api_key, file_obj["name"])
            if args.verbose:
                eprint("  [cleanup] Done")

    # Output results
    eprint(f"\n{'=' * 60}")
    eprint(f"TOTAL: {len(all_chunks)} semantic chunks")
    eprint(f"{'=' * 60}")

    output_json = json.dumps(all_chunks, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output_json, encoding="utf-8")
        eprint(f"\nOutput written to: {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()

```
