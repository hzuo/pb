#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "requests>=2.32.0",
# ]
# ///

"""
Stony Brook Medicine Clinical Notes - PDF to Markdown Converter

Converts PDFs in the workspace to markdown using Landing AI's
Agentic Document Extraction API.

Logic (stateless, idempotent):

    for each *.pdf in workspace:
        sibling_md = pdf.with_suffix(".md")
        if not sibling_md.exists():
            markdown = call_landing_ai_parse(pdf)
            save(sibling_md, markdown)

Prerequisites:
- LANDINGAI_API_KEY environment variable set

Usage:
    ./scripts/25-12-02-tue-stonybrook-notes-convert.py
    ./scripts/25-12-02-tue-stonybrook-notes-convert.py --workers 8
    ./scripts/25-12-02-tue-stonybrook-notes-convert.py --dry-run
"""

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

# --------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------

GIT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".git").exists())
WORKSPACE = (GIT_ROOT / "_scratch" / "mf").resolve()

LANDING_AI_API_URL = "https://api.va.landing.ai/v1/ade/parse"
LANDING_AI_MODEL = "dpt-2-latest"

DEFAULT_WORKERS = 16

# --------------------------------------------------------------------
# Core Functions
# --------------------------------------------------------------------


def get_api_key() -> str:
    """Get Landing AI API key from environment."""
    api_key = os.environ.get("LANDINGAI_API_KEY")
    if not api_key:
        print("ERROR: LANDINGAI_API_KEY environment variable not set")
        sys.exit(1)
    return api_key


def convert_pdf_to_markdown(
    pdf_path: Path, api_key: str
) -> tuple[bool, str, dict | None]:
    """
    Convert a single PDF to markdown using Landing AI.

    Returns:
        (success, message, metadata)
    """
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        with open(pdf_path, "rb") as f:
            files = {"document": (pdf_path.name, f, "application/pdf")}
            data = {"model": LANDING_AI_MODEL}

            response = requests.post(
                LANDING_AI_API_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=300,  # 5 min timeout for large docs
            )

        if response.status_code != 200:
            return (
                False,
                f"API error: {response.status_code} - {response.text[:200]}",
                None,
            )

        result = response.json()
        markdown = result.get("markdown", "")
        metadata = result.get("metadata", {})

        if not markdown:
            return False, "API returned empty markdown", None

        return True, markdown, metadata

    except requests.Timeout:
        return False, "Request timed out", None
    except Exception as e:
        return False, f"Exception: {e}", None


def process_single_pdf(
    pdf_path: Path, api_key: str, dry_run: bool
) -> tuple[Path, bool, str]:
    """
    Process a single PDF: convert to markdown and save.

    Returns:
        (pdf_path, success, message)
    """
    md_path = pdf_path.with_suffix(".md")

    # Skip if already converted
    if md_path.exists():
        return pdf_path, True, "already exists"

    if dry_run:
        return pdf_path, True, "would convert (dry-run)"

    # Convert
    success, result, metadata = convert_pdf_to_markdown(pdf_path, api_key)

    if not success:
        return pdf_path, False, result

    # Save markdown
    try:
        md_path.write_text(result, encoding="utf-8")
        page_count = metadata.get("page_count", "?") if metadata else "?"
        credits = metadata.get("credit_usage", "?") if metadata else "?"
        return pdf_path, True, f"converted ({page_count} pages, {credits} credits)"
    except Exception as e:
        return pdf_path, False, f"Failed to save: {e}"


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDFs to markdown using Landing AI"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of parallel workers (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without actually converting",
    )
    args = parser.parse_args()

    print(f"Workspace: {WORKSPACE}")
    print(f"Workers: {args.workers}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Get API key
    api_key = get_api_key()

    # Find all PDFs
    pdfs = sorted(WORKSPACE.glob("*.pdf"))
    print(f"Found {len(pdfs)} PDFs")

    # Find which need conversion
    to_convert = [p for p in pdfs if not p.with_suffix(".md").exists()]
    already_done = len(pdfs) - len(to_convert)

    print(f"Already converted: {already_done}")
    print(f"To convert: {len(to_convert)}")
    print()

    if not to_convert:
        print("Nothing to do!")
        return

    # Process with thread pool
    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(process_single_pdf, pdf, api_key, args.dry_run): pdf
            for pdf in to_convert
        }

        for i, future in enumerate(as_completed(futures), 1):
            pdf_path, success, message = future.result()
            status = "OK" if success else "FAIL"
            print(f"[{i}/{len(to_convert)}] {status}: {pdf_path.name}")
            print(f"         {message}")

            if success and "converted" in message:
                success_count += 1
            elif not success:
                fail_count += 1

    print()
    print(f"Done! Converted: {success_count}, Failed: {fail_count}")


if __name__ == "__main__":
    main()
