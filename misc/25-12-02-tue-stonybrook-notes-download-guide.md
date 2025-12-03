# Stony Brook Medicine Patient Portal - Clinical Notes Download Guide

This document describes how to programmatically download all clinical notes (PDFs) from the Stony Brook Medicine patient portal using Playwright and Chrome DevTools Protocol (CDP).

## Prerequisites

- Chrome browser running with remote debugging enabled on port 9315
- Python with `playwright` library (sync API)
- User must be logged into the patient portal in the Chrome browser

## Overview

The process involves:
1. Connecting to Chrome via CDP
2. Navigating to the clinical notes page
3. Extracting document links from a paginated list
4. Downloading each PDF using authenticated requests
5. Collecting metadata into a TSV file

---

## Step 1: Connect to Chrome via CDP

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9315")
    context = browser.contexts[0]  # Use existing browser context (with cookies/session)
    page = context.pages[0] if context.pages else context.new_page()
```

**Important:** Always use `with` statement to properly close the Playwright context after each operation.

---

## Step 2: Page Structure (Nested Iframe)

The clinical notes page has a **nested iframe structure**:

```
Main Page (myhealthelife.stonybrookmedicine.edu)
└── Frame 0: Main page content
└── Frame 1: iframe (patientportal.myhealthelife.stonybrookmedicine.edu)
             └── Contains the actual notes list
```

**URL Structure:**
- Main page: `https://myhealthelife.stonybrookmedicine.edu/pages/health_record/open_notes?pagelet=...`
- Iframe: `https://patientportal.myhealthelife.stonybrookmedicine.edu/person/{user_id}/health-record/open-notes`

**Accessing the iframe:**
```python
frames = page.frames
iframe_frame = frames[1] if len(frames) > 1 else None
```

---

## Step 3: Navigate to Clinical Notes Page

```python
url = "https://myhealthelife.stonybrookmedicine.edu/pages/health_record/open_notes?pagelet=https%3A%2F%2Fpatientportal.myhealthelife.stonybrookmedicine.edu%2Fperson%2F{USER_ID}%2Fhealth-record%2Fopen-notes"

page.goto(url, wait_until="load", timeout=15000)
page.wait_for_timeout(4000)  # Allow iframe content to load
```

**Note:** If the page shows an error ("We're having difficulty retrieving your reports"), try:
1. Navigate to home page first
2. Click "Clinical Notes" from the navigation menu
3. This often resolves the loading issue

---

## Step 4: Document Link Structure

Each clinical note appears as a `.consumer-card-item` containing a `.document-view` link:

```html
<div class="consumer-card-item">
    <a class="document-view" href="/person/{user_id}/health-record/open-notes/types/common/{doc_id}">
        Note Title
    </a>
    <!-- Additional metadata: dates, description, etc. -->
</div>
```

**Extracting links:**
```python
doc_views = iframe_frame.query_selector_all(".document-view")
for el in doc_views:
    href = el.get_attribute("href")  # e.g., /person/.../11940951421
    doc_id = href.split('/')[-1]     # e.g., 11940951421
```

---

## Step 5: Pagination

The notes list is paginated with 25 items per page. Navigation uses `.next-pages` button:

```python
all_links = []
seen_hrefs = set()
page_num = 1

while True:
    frames = page.frames
    iframe_frame = frames[1] if len(frames) > 1 else None

    if not iframe_frame:
        break

    # Wait for content
    try:
        iframe_frame.wait_for_selector(".document-view", timeout=5000)
    except:
        break

    # Collect links from current page
    doc_views = iframe_frame.query_selector_all(".document-view")
    for el in doc_views:
        href = el.get_attribute("href")
        if href and href not in seen_hrefs:
            seen_hrefs.add(href)
            all_links.append(href)

    print(f"Page {page_num}: {len(doc_views)} items (total: {len(all_links)})")

    # Check for next button
    next_btn = iframe_frame.query_selector(".next-pages")
    if not next_btn or not next_btn.is_visible():
        break

    next_btn.click()
    page.wait_for_timeout(2000)
    page_num += 1
```

**Note:** After the last page, clicking "Next" cycles back to earlier pages (duplicates detected via `seen_hrefs`).

---

## Step 6: Downloading PDFs

### Authentication
The `page.request.get()` method automatically uses the browser's cookies/session - no manual cookie handling needed.

### Getting Filename from Content-Disposition
The server returns the PDF with a `Content-Disposition` header containing the filename:

```
Content-Type: application/pdf
Content-Disposition: inline; filename="General Medicine Progress Note 12-02-2025.pdf" ...
```

### Download Code
```python
import re
from urllib.parse import urljoin

base_url = "https://patientportal.myhealthelife.stonybrookmedicine.edu"
workspace = Path.home() / "Downloads" / "mf"
workspace.mkdir(parents=True, exist_ok=True)

for href in all_links:
    doc_id = href.split('/')[-1]
    full_url = urljoin(base_url, href)

    response = page.request.get(full_url, timeout=30000)

    # Verify response
    if response.status != 200:
        print(f"Failed: {doc_id} (status {response.status})")
        continue

    content_type = response.headers.get('content-type', '')
    if 'pdf' not in content_type.lower():
        print(f"Not a PDF: {doc_id}")
        continue

    # Extract filename from Content-Disposition header
    cd = response.headers.get('content-disposition', '')
    match = re.search(r'filename="([^"]+)"', cd)
    filename = match.group(1) if match else f"document_{doc_id}.pdf"

    # Append doc_id to ensure unique filenames
    base = filename.rsplit('.', 1)[0]
    filename = f"{base}_{doc_id}.pdf"

    body = response.body()

    # Verify PDF header
    if not body.startswith(b'%PDF'):
        print(f"Invalid PDF: {doc_id}")
        continue

    # Save file
    output_path = workspace / filename
    output_path.write_bytes(body)
```

### Batch Processing
For large numbers of files, process in batches to avoid connection timeouts:

```python
batch_size = 50
for batch_start in range(0, len(all_links), batch_size):
    batch = all_links[batch_start:batch_start + batch_size]

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9315")
        context = browser.contexts[0]
        page = context.pages[0]

        for href in batch:
            # ... download logic ...
```

---

## Step 7: Collecting Metadata for TSV

To get the full card text (including dates and descriptions), find the `.consumer-card-item` parent:

```python
entries = iframe_frame.evaluate('''() => {
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
}''')
```

---

## Step 8: Creating the TSV File

```python
import csv

tsv_rows = []
for card_text, href in metadata_entries:
    doc_id = href.split('/')[-1]

    # Get filename from downloaded files
    cd_filename = doc_id_to_filename.get(doc_id, "")

    # Clean card text (remove newlines/tabs)
    card_text_clean = re.sub(r'[\t\n\r]+', ' ', card_text)
    card_text_clean = re.sub(r' +', ' ', card_text_clean).strip()

    tsv_rows.append({
        'card_text': card_text_clean,
        'href': href,
        'content_disposition_filename': cd_filename
    })

# Write TSV
with open(workspace / "notes_metadata.tsv", 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f,
        fieldnames=['card_text', 'href', 'content_disposition_filename'],
        delimiter='\t')
    writer.writeheader()
    writer.writerows(tsv_rows)
```

---

## Step 9: Deduplication

Check for duplicates via MD5 hash:

```python
import hashlib

hash_to_files = {}
for pdf in workspace.glob("*.pdf"):
    with open(pdf, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    hash_to_files.setdefault(md5, []).append(pdf.name)

duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
```

---

## File Naming Convention

All PDFs follow this naming pattern:
```
<Note Type> <MM-DD-YYYY>_<doc_id>.pdf
```

Examples:
- `General Medicine Progress Note 12-02-2025_11940951421.pdf`
- `Surgery Consult 12-02-2025_11939730250.pdf`
- `EKG 11-15-2025_11896aborr249.pdf`

The `doc_id` suffix ensures uniqueness when multiple notes have the same type and date.

---

## Output Summary

| Item | Count |
|------|-------|
| Total PDFs | 259 |
| Total Size | ~100 MB |
| TSV Columns | card_text, href, content_disposition_filename |
| Pages Scraped | 11 (25 items each, last page has 9) |

---

## Troubleshooting

### "We're having difficulty retrieving your reports"
- Navigate to home page first, then click "Clinical Notes" link

### Connection dropped / socket hang up
- Process in smaller batches
- Reconnect to CDP for each batch

### Empty iframe content
- Increase wait time after navigation
- Check if session has expired (may need to re-login in browser)

### Missing Content-Disposition header
- Fall back to `document_{doc_id}.pdf` naming
