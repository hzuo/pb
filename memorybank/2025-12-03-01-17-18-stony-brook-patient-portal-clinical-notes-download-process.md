---
filename: 2025-12-03-01-17-18-stony-brook-patient-portal-clinical-notes-download-process
timestamp: '2025-12-03T01:17:18.112270+00:00'
title: Stony Brook Patient Portal Clinical Notes Download Process
---

# Stony Brook Medicine Patient Portal - Clinical Notes Download Process

## Overview

Process to programmatically download clinical notes (PDFs) from the Stony Brook Medicine patient portal using Playwright and Chrome DevTools Protocol (CDP).

## Connection

- Connect to Chrome via CDP on port 9315: `p.chromium.connect_over_cdp("http://localhost:9315")`
- Use existing browser context (inherits cookies/session)
- Always use `with sync_playwright() as p:` to properly close context

## Page Structure (Nested Iframe)

```
Main Page: myhealthelife.stonybrookmedicine.edu/pages/health_record/open_notes?pagelet=...
└── Frame 0: Main page
└── Frame 1: iframe (patientportal.myhealthelife.stonybrookmedicine.edu)
             └── Contains the actual notes list
```

Access iframe: `frames = page.frames; iframe_frame = frames[1]`

## URL Pattern

- Main: `https://myhealthelife.stonybrookmedicine.edu/pages/health_record/open_notes?pagelet=https%3A%2F%2Fpatientportal.myhealthelife.stonybrookmedicine.edu%2Fperson%2F{USER_ID}%2Fhealth-record%2Fopen-notes`
- PDF links: `/person/{USER_ID}/health-record/open-notes/types/common/{DOC_ID}`
- Base for PDFs: `https://patientportal.myhealthelife.stonybrookmedicine.edu`

## DOM Structure

- Each note is a `.consumer-card-item` containing:
  - `.document-view` link (href has the doc_id)
  - Metadata: note type, dates, description
- Pagination via `.next-pages` button (25 items per page)
- Pages cycle after end (detect via duplicate hrefs)

## Extracting Card Metadata

```javascript
// Find parent .consumer-card-item for each .document-view
let current = el;
while (current && current.parentElement) {
    current = current.parentElement;
    if (current.classList.contains('consumer-card-item')) {
        cardText = current.innerText;
        break;
    }
}
```

## Downloading PDFs

1. Use `page.request.get(full_url)` - inherits browser authentication
2. Check `response.headers['content-type']` contains 'pdf'
3. Extract filename from `Content-Disposition` header: `filename="Note Type MM-DD-YYYY.pdf"`
4. Verify PDF starts with `b'%PDF'`
5. Save with naming: `{Note Type} {Date}_{doc_id}.pdf`

## Batch Processing

Process in batches of ~50 to avoid connection timeouts. Reconnect to CDP for each batch.

## TSV Schema

| Column | Description |
|--------|-------------|
| card_text | innerText of .consumer-card-item (cleaned, single line) |
| href | Relative path e.g. /person/.../11940951421 |
| content_disposition_filename | Original filename from header |

## Deduplication

- Use doc_id (from href) as unique identifier
- Check for content duplicates via MD5 hash
- Naming convention ensures uniqueness: `{name}_{doc_id}.pdf`

## Troubleshooting

- "Difficulty retrieving reports" error: Navigate to home, click Clinical Notes link
- Connection drops: Use batch processing with reconnects
- Empty iframe: Increase wait time, check session validity
