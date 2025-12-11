#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "playwright>=1.54.0",
# ]
# ///

"""
Stony Brook Medicine Patient Portal - Radiology Test Results Sync

Connects to Chrome via CDP, scrapes the radiology/test results list,
downloads any new PDFs, and updates the metadata TSV.

Prerequisites:
- Chrome running with remote debugging on CDP_PORT
- User logged into the patient portal

Based on: 25-12-02-tue-stonybrook-notes-01-download.py
"""

import csv
import re
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

# --------------------------------------------------------------------
# Configuration (edit these as needed)
# --------------------------------------------------------------------

GIT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".git").exists())
WORKSPACE = (GIT_ROOT / "_scratch" / "mf").resolve()
CDP_PORT = 9315
BASE_URL = "https://myhealthelife.stonybrookmedicine.edu/pages/health_record/radiology"
TSV_FILENAME = "__index_radiology__.tsv"
PDF_BASE_URL = "https://patientportal.myhealthelife.stonybrookmedicine.edu"
BATCH_SIZE = 50

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------


def load_existing_tsv(tsv_path: Path) -> set[str]:
    """Load existing TSV and return set of known doc_ids (from href column)."""
    if not tsv_path.exists():
        return set()

    known_ids = set()
    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            href = row.get("href", "")
            if href:
                doc_id = href.split("/")[-1]
                known_ids.add(doc_id)
    return known_ids


def collect_all_entries(page) -> list[tuple[str, str]]:
    """
    Paginate through all radiology pages and collect (card_text, href) tuples.
    Returns list of unique entries.
    """
    entries = []
    seen_hrefs = set()
    page_num = 1

    while True:
        frames = page.frames
        if len(frames) < 2:
            raise RuntimeError("Could not find iframe - is the page loaded correctly?")

        iframe_frame = frames[1]

        # Wait for content
        try:
            iframe_frame.wait_for_selector(".document-view", timeout=10000)
        except Exception:
            if page_num == 1:
                raise RuntimeError(
                    "No .document-view elements found - page may have failed to load"
                )
            break

        # Extract entries using JavaScript
        page_entries = iframe_frame.evaluate("""() => {
            const results = [];
            const docViews = document.querySelectorAll('.document-view');
            for (const el of docViews) {
                const href = el.getAttribute('href');
                let current = el;
                let cardText = '';
                while (current && current.parentElement) {
                    current = current.parentElement;
                    if (current.classList && current.classList.contains('consumer-card-item')) {
                        cardText = current.innerText;
                        break;
                    }
                }
                results.push({ href, cardText });
            }
            return results;
        }""")

        new_on_page = 0
        for entry in page_entries:
            href = entry["href"]
            card_text = entry["cardText"]
            if href and href not in seen_hrefs:
                seen_hrefs.add(href)
                entries.append((card_text, href))
                new_on_page += 1

        print(f"  Page {page_num}: {len(page_entries)} items ({new_on_page} new)")

        # If no new items, we've cycled back to the beginning
        if new_on_page == 0:
            break

        # Look for next button
        next_btn = iframe_frame.query_selector(".next-pages")
        if not next_btn or not next_btn.is_visible():
            break

        next_btn.click()
        page.wait_for_timeout(2000)
        page_num += 1

        # Safety limit
        if page_num > 200:
            print("  Warning: hit 200 page limit")
            break

    return entries


def download_pdfs(
    entries: list[tuple[str, str]],
    workspace: Path,
) -> list[dict]:
    """
    Download PDFs for the given entries.
    Returns list of row dicts for TSV.
    """
    rows = []
    total = len(entries)

    for batch_start in range(0, total, BATCH_SIZE):
        batch = entries[batch_start : batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1

        if total > BATCH_SIZE:
            print(
                f"  Batch {batch_num} ({batch_start + 1}-{batch_start + len(batch)} of {total})"
            )

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            for i, (card_text, href) in enumerate(batch):
                doc_id = href.split("/")[-1]
                full_url = urljoin(PDF_BASE_URL, href)
                idx = batch_start + i + 1

                try:
                    response = page.request.get(full_url, timeout=30000)

                    if response.status != 200:
                        print(
                            f"  {idx}/{total}: FAILED (status {response.status}) - {doc_id}"
                        )
                        continue

                    content_type = response.headers.get("content-type", "")
                    if "pdf" not in content_type.lower():
                        print(f"  {idx}/{total}: FAILED (not PDF) - {doc_id}")
                        continue

                    # Extract filename from Content-Disposition
                    cd = response.headers.get("content-disposition", "")
                    match = re.search(r'filename="([^"]+)"', cd)
                    cd_filename = match.group(1) if match else f"radiology_{doc_id}.pdf"

                    body = response.body()

                    if not body.startswith(b"%PDF"):
                        print(f"  {idx}/{total}: FAILED (invalid PDF) - {doc_id}")
                        continue

                    # Save with doc_id suffix for uniqueness
                    base = cd_filename.rsplit(".", 1)[0]
                    filename = f"{base}_{doc_id}.pdf"
                    output_path = workspace / filename
                    output_path.write_bytes(body)

                    size_kb = len(body) / 1024
                    print(f"  {idx}/{total}: {filename} ({size_kb:.1f} KB)")

                    # Clean card_text for TSV
                    card_text_clean = re.sub(r"[\t\n\r]+", " ", card_text)
                    card_text_clean = re.sub(r" +", " ", card_text_clean).strip()

                    rows.append(
                        {
                            "card_text": card_text_clean,
                            "href": href,
                            "content_disposition_filename": cd_filename,
                        }
                    )

                except Exception as e:
                    print(f"  {idx}/{total}: ERROR - {doc_id}: {e}")

    return rows


def write_tsv(tsv_path: Path, rows: list[dict], append: bool):
    """Write or append rows to TSV."""
    mode = "a" if append else "w"
    write_header = not append

    with open(tsv_path, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["card_text", "href", "content_disposition_filename"],
            delimiter="\t",
        )
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------


def main():
    print(f"Workspace: {WORKSPACE}")
    print(f"CDP Port: {CDP_PORT}")
    print()

    # Ensure workspace exists
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    # Load existing TSV
    tsv_path = WORKSPACE / TSV_FILENAME
    known_ids = load_existing_tsv(tsv_path)
    tsv_existed = tsv_path.exists()
    print(f"Loaded {len(known_ids)} existing entries from TSV")

    # Connect and navigate
    print()
    print("Connecting to Chrome...")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        print(f"Navigating to {BASE_URL}")
        page.goto(BASE_URL, wait_until="load", timeout=30000)
        page.wait_for_timeout(4000)

        print()
        print("Scanning pages...")
        all_entries = collect_all_entries(page)

    print(f"Total entries found: {len(all_entries)}")

    # Filter to new entries
    new_entries = [
        (card_text, href)
        for card_text, href in all_entries
        if href.split("/")[-1] not in known_ids
    ]

    print(f"New entries: {len(new_entries)}")

    if not new_entries:
        print()
        print("No new radiology results to download.")
        return

    # Download new PDFs (reverse to process oldest-first for chronological TSV)
    print()
    print("Downloading new PDFs...")
    new_entries_reversed = new_entries[::-1]  # Oldest first
    new_rows = download_pdfs(new_entries_reversed, WORKSPACE)

    print()
    print(f"Downloaded {len(new_rows)} PDFs")

    # Update TSV
    if new_rows:
        write_tsv(tsv_path, new_rows, append=tsv_existed)
        total_entries = len(known_ids) + len(new_rows)
        print(f"TSV updated: {total_entries} total entries")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
