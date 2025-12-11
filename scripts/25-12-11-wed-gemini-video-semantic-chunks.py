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
in 15-minute segments and breaks each down into granular sub-minute semantic
chunks with detailed summaries.

Usage:
    uv run gemini-video-semantic-chunks.py video.mp4
    uv run gemini-video-semantic-chunks.py video.mp4 --context "Meeting between Alice and Bob about Q4 planning"
    uv run gemini-video-semantic-chunks.py video.mp4 -o chunks.json

The output is a JSON array of semantic chunks, each with:
- start_sec: Start timestamp in seconds
- end_sec: End timestamp in seconds
- summary: Detailed description of what happens in this chunk
- audio_description: Exhaustive visual description for blind accessibility

Design notes:
- Uses Gemini 3 Pro defaults (temperature=1.0, thinkingLevel=HIGH)
- Only overrides responseMimeType and responseJsonSchema for structured output
- Rolling context: each 15-min segment receives all prior semantic chunks
- Biases towards granular sub-minute chunks with multiple sentences each
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

# 15 minutes per API call - well under the 45-min limit for video with audio
CALL_CHUNK_DURATION_SEC = 15 * 60

# System instruction: bias towards granular sub-minute chunks
SYSTEM_INSTRUCTION = """
You are an expert video analyst creating semantic segmentations with detailed workflow descriptions.

Your task is to break down video content into small, semantically meaningful chunks with EXHAUSTIVE descriptions of what is being shown and done on screen.

## Chunking Guidelines
- **Be granular**: Prefer many small chunks over few large ones
- **Sub-minute chunks**: Most chunks should be 10-60 seconds, rarely longer
- **Topic boundaries**: Start a new chunk when the topic, screen, or workflow step changes
- **Strict contiguity**: Each chunk's start_sec must exactly equal the previous chunk's end_sec. No gaps. First chunk starts at segment start, last chunk ends at segment end.

## For Each Chunk Provide

1. **start_sec**: When this semantic unit begins (seconds from VIDEO START, not segment start)
2. **end_sec**: When this semantic unit ends (must equal next chunk's start_sec)
3. **summary**: 2-4 sentence narrative description of what happens
4. **audio_description**: EXHAUSTIVE workflow description (see below)

## audio_description Requirements

The audio_description must enable someone to REPLICATE THE EXACT WORKFLOW without watching the video. Focus on what is being shown and done, not on people or emotions.

**SCREEN CONTENT**:
- Current application/website and page/view name
- Complete UI layout: sidebars, panels, tabs, toolbars, menus
- ALL readable text: headers, labels, buttons, field values, data
- For tables: ALL column headers AND ALL visible row data
- For forms: ALL field labels AND their current values
- URLs, file paths, identifiers visible on screen

**NAVIGATION & ACTIONS** (most critical):
- Exact sequence of clicks: what element was clicked and where it's located
- Menu navigation: which menu, which submenu, which item selected
- Keyboard input: what was typed, keyboard shortcuts used
- Scrolling: direction and what content comes into view
- Selections: what was selected, highlighted, or checked
- Form interactions: fields filled, dropdowns chosen, checkboxes toggled

**TRANSITIONS**:
- What screen/page/view appears after each action
- Loading states and what loads
- Panels, dialogs, or dropdowns opening/closing
- Tab switches and their content

**DATA & RESULTS**:
- Search results or filtered data shown
- Error messages or success confirmations
- Values that change as a result of actions

Write as a step-by-step procedural description. Use numbered steps or clear bullet points. Be specific enough that a reader could perform the identical workflow in the same application.
""".strip()

# Output schema for semantic chunks
SEMANTIC_CHUNKS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "segment_start_sec": {
            "type": "number",
            "description": "Start of the analyzed segment in seconds from video beginning",
        },
        "segment_end_sec": {
            "type": "number",
            "description": "End of the analyzed segment in seconds from video beginning",
        },
        "chunks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start_sec": {
                        "type": "number",
                        "description": "Start timestamp in seconds from video beginning",
                    },
                    "end_sec": {
                        "type": "number",
                        "description": "End timestamp in seconds from video beginning",
                    },
                    "summary": {
                        "type": "string",
                        "description": "2-4 sentence narrative description of this chunk",
                    },
                    "audio_description": {
                        "type": "string",
                        "description": "Step-by-step workflow description enabling replication of shown actions: screen content, navigation, clicks, data values, and transitions",
                    },
                },
                "required": ["start_sec", "end_sec", "summary", "audio_description"],
            },
        },
    },
    "required": ["segment_start_sec", "segment_end_sec", "chunks"],
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
class CallChunk:
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


def run_subprocess(cmd: list[str]) -> subprocess.CompletedProcess:
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


def plan_call_chunks(meta: VideoMetadata) -> list[CallChunk]:
    """Plan 15-minute segments for API calls."""
    if meta.duration_sec <= 0:
        return [CallChunk(0, 0, 0)]

    if meta.duration_sec <= CALL_CHUNK_DURATION_SEC:
        return [CallChunk(0, 0, meta.duration_sec)]

    num_chunks = math.ceil(meta.duration_sec / CALL_CHUNK_DURATION_SEC)

    return [
        CallChunk(
            index=i,
            start_sec=i * CALL_CHUNK_DURATION_SEC,
            end_sec=min((i + 1) * CALL_CHUNK_DURATION_SEC, meta.duration_sec),
        )
        for i in range(num_chunks)
    ]


def format_timestamp(seconds: float) -> str:
    """Format seconds as MM:SS or H:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


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
    """Call generateContent endpoint."""
    resp = requests.post(
        f"{GEMINI_API_BASE}/v1beta/models/{GEMINI_MODEL}:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=600,
    )
    if not resp.ok:
        eprint(f"API Error: {resp.text}")
    resp.raise_for_status()
    return resp.json()


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
    chunk: CallChunk,
    total_chunks: int,
    prior_chunks: list[dict],
    user_context: str | None,
    verbose: bool = False,
) -> list[dict]:
    """Analyze a 15-minute segment and extract semantic chunks."""

    # Build the user prompt
    prompt_parts = []

    # Rolling context from prior segments
    if prior_chunks:
        # Summarize prior chunks concisely to fit context
        prior_summary = "\n".join(
            [
                f"[{format_timestamp(c['start_sec'])}-{format_timestamp(c['end_sec'])}] {c['summary'][:200]}..."
                if len(c["summary"]) > 200
                else f"[{format_timestamp(c['start_sec'])}-{format_timestamp(c['end_sec'])}] {c['summary']}"
                for c in prior_chunks[-50:]  # Last 50 chunks for context
            ]
        )
        prompt_parts.append(f"PRIOR CONTENT (for context):\n{prior_summary}\n")

    prompt_parts.append(
        textwrap.dedent(
            f"""
            CURRENT SEGMENT: {format_timestamp(chunk.start_sec)} to {format_timestamp(chunk.end_sec)} (segment {chunk.index + 1} of {total_chunks})

            Analyze this segment and break it into granular semantic chunks.

            Requirements:
            - Most chunks should be 10-60 seconds
            - Each chunk = one topic/moment/idea
            - Timestamps must be in seconds from VIDEO START (not segment start)
            - summary: 2-4 detailed sentences
            - audio_description: EXHAUSTIVE visual description for blind users
              - Transcribe ALL visible text verbatim
              - Describe ALL UI elements, mouse actions, screen changes
              - Use categorized bullet points (SCREEN CONTENT, ACTIONS, PEOPLE, TRANSITIONS)
              - Be extremely verbose (15-30+ bullet points for complex screens)
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
                            "startOffset": {"seconds": int(chunk.start_sec)},
                            "endOffset": {"seconds": int(chunk.end_sec)},
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
                "includeThoughts": True,
            },
        },
    }

    if verbose:
        eprint(f"\n  [request] Sending to {GEMINI_MODEL}...")
        eprint(f"  [request] Segment: {chunk.start_sec}s - {chunk.end_sec}s")
        eprint(f"  [request] Prior chunks in context: {len(prior_chunks)}")

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
                    eprint(indent_lines(thought_text.strip()) + "\n")
        except (KeyError, IndexError):
            pass

    text = extract_text(resp)

    try:
        data = json.loads(text)
        chunks = data.get("chunks", [])
        if verbose:
            eprint(f"  [response] Chunks ({len(chunks)}):")
            eprint(indent_lines(json.dumps(chunks, indent=2)))
        return chunks
    except json.JSONDecodeError:
        eprint("Warning: Failed to parse response as JSON")
        return []


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
    args = parser.parse_args()

    if not args.video.exists():
        sys.exit(f"ERROR: Video file not found: {args.video}")

    api_key = require_api_key()
    meta = probe_video(args.video)

    eprint(f"Video: {meta.path}")
    eprint(
        f"Duration: {format_timestamp(meta.duration_sec)} ({meta.duration_sec:.1f}s)"
    )
    eprint(f"Size: {meta.size_bytes / 1024**2:.1f} MB")
    eprint(f"Audio: {meta.has_audio}")

    # Plan segments
    call_chunks = plan_call_chunks(meta)
    eprint(
        f"\nPlanned {len(call_chunks)} segment(s) of {CALL_CHUNK_DURATION_SEC // 60} min each"
    )

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
    all_semantic_chunks: list[dict] = []

    try:
        for chunk in call_chunks:
            eprint(
                f"\n=== Segment {chunk.index + 1}/{len(call_chunks)} "
                f"({format_timestamp(chunk.start_sec)}-{format_timestamp(chunk.end_sec)}) ==="
            )

            segment_chunks = analyze_segment(
                api_key=api_key,
                file_uri=file_uri,
                chunk=chunk,
                total_chunks=len(call_chunks),
                prior_chunks=all_semantic_chunks,
                user_context=args.context,
                verbose=args.verbose,
            )

            eprint(f"\n  Found {len(segment_chunks)} semantic chunks")
            all_semantic_chunks.extend(segment_chunks)

    finally:
        # Clean up uploaded file
        if file_obj and file_obj.get("name"):
            eprint(f"\n[cleanup] Deleting {file_obj['name']}...")
            delete_remote_file(api_key, file_obj["name"])
            if args.verbose:
                eprint("  [cleanup] Done")

    # Output results
    eprint(f"\n{'=' * 60}")
    eprint(f"TOTAL: {len(all_semantic_chunks)} semantic chunks")
    eprint(f"{'=' * 60}")

    output_json = json.dumps(all_semantic_chunks, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output_json, encoding="utf-8")
        eprint(f"\nOutput written to: {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
