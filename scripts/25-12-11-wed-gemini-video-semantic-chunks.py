#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.32.3",
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
You are an expert video analyst specializing in granular semantic segmentation.

Your task is to break down video content into very small, semantically meaningful chunks. Each chunk should capture a single topic, moment, or idea.

Guidelines for chunking:
- **Be granular**: Prefer many small chunks over few large ones
- **Sub-minute chunks**: Most chunks should be 10-60 seconds, rarely longer
- **Topic boundaries**: Start a new chunk when the topic, speaker focus, or visual content changes
- **Rich detail**: Each chunk summary should be 2-4 sentences capturing the key content
- **Precise timestamps**: Use exact second boundaries based on when content actually changes
- **Strict contiguity**: Each chunk's start_sec must exactly equal the previous chunk's end_sec. No gaps allowed. The first chunk starts at the segment start time, and the last chunk ends at the segment end time.

For each chunk, provide:
1. start_sec: When this semantic unit begins (in seconds from video start)
2. end_sec: When this semantic unit ends (must equal next chunk's start_sec)
3. summary: Detailed description of content, speakers, visuals, and key points

Respond with valid JSON matching the provided schema.
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
                        "description": "Start timestamp in seconds from video beginning (must equal previous chunk's end_sec, or segment_start_sec if this is the first chunk)",
                    },
                    "end_sec": {
                        "type": "number",
                        "description": "End timestamp in seconds from video beginning (must equal next chunk's start_sec, or segment_end_sec if this is the last chunk)",
                    },
                    "summary": {
                        "type": "string",
                        "description": "Detailed 2-4 sentence description of this chunk",
                    },
                },
                "required": ["start_sec", "end_sec", "summary"],
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
        print(f"  [files] state={state}, waiting {poll_sec}s...", file=sys.stderr)
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
        print(f"  [cleanup] Warning: Failed to delete {file_name}", file=sys.stderr)


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
        print(f"API Error: {resp.text}", file=sys.stderr)
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

            Analyze this segment and break it into granular semantic chunks. Remember:
            - Most chunks should be 10-60 seconds
            - Each chunk = one topic/moment/idea
            - 2-4 detailed sentences per chunk summary
            - Timestamps are relative to VIDEO START (not segment start)
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
        },
    }

    resp = call_generate_content(api_key, payload)
    text = extract_text(resp)

    try:
        data = json.loads(text)
        return data.get("chunks", [])
    except json.JSONDecodeError:
        print("Warning: Failed to parse response as JSON", file=sys.stderr)
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
    args = parser.parse_args()

    if not args.video.exists():
        sys.exit(f"ERROR: Video file not found: {args.video}")

    api_key = require_api_key()
    meta = probe_video(args.video)

    print(f"Video: {meta.path}", file=sys.stderr)
    print(
        f"Duration: {format_timestamp(meta.duration_sec)} ({meta.duration_sec:.1f}s)",
        file=sys.stderr,
    )
    print(f"Size: {meta.size_bytes / 1024**2:.1f} MB", file=sys.stderr)
    print(f"Audio: {meta.has_audio}", file=sys.stderr)

    # Plan segments
    call_chunks = plan_call_chunks(meta)
    print(
        f"\nPlanned {len(call_chunks)} segment(s) of {CALL_CHUNK_DURATION_SEC // 60} min each",
        file=sys.stderr,
    )

    # Upload video once
    print("\nUploading video...", file=sys.stderr)
    file_obj = upload_file(api_key, meta.path)
    file_obj = wait_for_active(api_key, file_obj)
    file_uri = get_file_uri(file_obj)
    print(f"  Ready: {file_uri}", file=sys.stderr)

    # Process each segment with rolling context
    all_semantic_chunks: list[dict] = []

    try:
        for chunk in call_chunks:
            print(
                f"\n=== Segment {chunk.index + 1}/{len(call_chunks)} "
                f"({format_timestamp(chunk.start_sec)}-{format_timestamp(chunk.end_sec)}) ===",
                file=sys.stderr,
            )

            segment_chunks = analyze_segment(
                api_key=api_key,
                file_uri=file_uri,
                chunk=chunk,
                total_chunks=len(call_chunks),
                prior_chunks=all_semantic_chunks,
                user_context=args.context,
            )

            print(f"  Found {len(segment_chunks)} semantic chunks", file=sys.stderr)
            all_semantic_chunks.extend(segment_chunks)

    finally:
        # Clean up uploaded file
        if file_obj and file_obj.get("name"):
            print(f"\n[cleanup] Deleting {file_obj['name']}...", file=sys.stderr)
            delete_remote_file(api_key, file_obj["name"])

    # Output results
    print(f"\n{'=' * 60}", file=sys.stderr)
    print(f"TOTAL: {len(all_semantic_chunks)} semantic chunks", file=sys.stderr)
    print(f"{'=' * 60}", file=sys.stderr)

    output_json = json.dumps(all_semantic_chunks, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output_json, encoding="utf-8")
        print(f"\nOutput written to: {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
