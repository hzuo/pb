# Landing AI's Agentic Document Extraction API: Complete Technical Reference

Landing AI's **Agentic Document Extraction (ADE)** API transforms complex documents—PDFs, scanned images, and multi-page files—into structured markdown and JSON with visual grounding coordinates. Unlike traditional OCR+LLM approaches, ADE uses an "agentic" methodology that breaks extraction into subtasks with reasoning, achieving **17x faster processing** (median 8 seconds vs. 135 seconds) while preserving tables, forms, signatures, and element relationships without templates or training.

## Two-stage architecture separates parsing from extraction

The modern ADE API follows a **decoupled design** introduced in September 2025: the **Parse API** converts documents to markdown, and the **Extract API** pulls structured fields from that markdown. This separation lets you parse once and extract multiple times with different schemas—ideal for experimentation or multi-field workflows.

| Endpoint | Purpose | HTTP Method | URL |
|----------|---------|-------------|-----|
| **ADE Parse** | Document → Markdown + chunks | POST | `https://api.va.landing.ai/v1/ade/parse` |
| **ADE Extract** | Markdown → structured fields | POST | `https://api.va.landing.ai/v1/ade/extract` |
| **ADE Parse Jobs** | Async for large documents | POST | `https://api.va.landing.ai/v1/ade/parse/jobs` |
| **Get Parse Job** | Retrieve async results | GET | `https://api.va.landing.ai/v1/ade/parse/jobs/{jobId}` |
| **Legacy (deprecated)** | Combined parse + extract | POST | `https://api.va.landing.ai/v1/tools/agentic-document-analysis` |

For **EU data residency**, replace `api.va.landing.ai` with `api.va.eu-west-1.landing.ai`.

---

## Complete ADE Parse API parameters

The Parse endpoint accepts documents via multipart form-data and returns markdown with structured chunks. Here are **all configurable parameters**:

### Authentication header (required)
```
Authorization: Bearer YOUR_API_KEY
```
API keys are obtained from:
- **US**: https://va.landing.ai/settings/api-key
- **EU**: https://va.eu-west-1.landing.ai/settings/api-key

### Request body parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document` | file | One of `document` or `document_url` | Binary file upload (PDF or image). Supports PDF, TIFF, ODP, PNG, JPEG, and formats supported by OpenCV. |
| `document_url` | string | One of `document` or `document_url` | URL pointing to the document file |
| `model` | string | Optional | Parsing model version. Options: `dpt-2-latest` (default), `dpt-2-20251103`, `dpt-2-mini` (preview) |
| `split` | string | Optional | Set to `page` to split output at page boundaries. Returns separate chunks/markdown per page in the `splits` array. |

### Model options explained

- **`dpt-2-latest`**: Automatically uses the latest snapshot; recommended for production
- **`dpt-2-20251103`**: Specific snapshot with improved table parsing, figure captioning, agentic table captioning, and expanded chunk ontology (attestations, ID cards, logos, barcodes, QR codes)
- **`dpt-2-mini`** (Preview): Lightweight model for simple, digitally-native documents at **1.5 credits/page** vs. 3 credits/page for standard models. Does not support scanned documents or handwritten content.

---

## Raw HTTP request structure for PDF to markdown

### Basic cURL example
```bash
curl -X POST 'https://api.va.landing.ai/v1/ade/parse' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F 'document=@document.pdf' \
  -F 'model=dpt-2-latest'
```

### With page-level splitting
```bash
curl -X POST 'https://api.va.landing.ai/v1/ade/parse' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F 'document=@document.pdf' \
  -F 'model=dpt-2-latest' \
  -F 'split=page'
```

### Using document URL instead of file upload
```bash
curl -X POST 'https://api.va.landing.ai/v1/ade/parse' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F 'document_url=https://example.com/document.pdf' \
  -F 'model=dpt-2-latest'
```

### Response JSON schema
```json
{
  "markdown": "<full document as markdown string>",
  "chunks": [
    {
      "markdown": "<chunk content>",
      "type": "<chunk_type>",
      "id": "<unique_uuid>",
      "grounding": {
        "box": {
          "left": 123,
          "top": 123,
          "right": 123,
          "bottom": 123
        },
        "page": 0
      }
    }
  ],
  "splits": [
    {
      "class": "<string>",
      "identifier": "<string>",
      "pages": [0, 1, 2],
      "markdown": "<split markdown>",
      "chunks": ["<chunk_ids>"]
    }
  ],
  "grounding": {},
  "metadata": {
    "filename": "<string>",
    "org_id": "<string>",
    "page_count": 5,
    "duration_ms": 8000,
    "credit_usage": 15,
    "job_id": "<string>",
    "version": "dpt-2-latest"
  }
}
```

### Chunk types recognized
The API identifies these element types: `title`, `text`, `table`, `figure`, `form_field`, `checkbox`, `signature`, `attestation`, `logo`, `barcode`, `qr_code`, `id_card`, `marginalia`.

---

## Vanilla Python requests examples

### Basic PDF to markdown extraction
```python
import requests

API_KEY = "your_api_key_here"
API_URL = "https://api.va.landing.ai/v1/ade/parse"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Upload a PDF file
with open("document.pdf", "rb") as f:
    files = {"document": ("document.pdf", f, "application/pdf")}
    data = {"model": "dpt-2-latest"}

    response = requests.post(API_URL, headers=headers, files=files, data=data)

result = response.json()

# Extract markdown content
markdown_content = result["markdown"]
print(f"Extracted {len(markdown_content)} characters of markdown")

# Save to file
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown_content)

# Access structured chunks with coordinates
for chunk in result["chunks"]:
    print(f"Type: {chunk['type']}, Page: {chunk['grounding']['page']}")
```

### With page-level splitting
```python
import requests
import json

API_KEY = "your_api_key_here"
API_URL = "https://api.va.landing.ai/v1/ade/parse"

headers = {"Authorization": f"Bearer {API_KEY}"}

with open("multipage.pdf", "rb") as f:
    files = {"document": ("multipage.pdf", f, "application/pdf")}
    data = {
        "model": "dpt-2-latest",
        "split": "page"  # Enable page-level splitting
    }

    response = requests.post(API_URL, headers=headers, files=files, data=data)

result = response.json()

# Access per-page splits
for i, split in enumerate(result.get("splits", [])):
    print(f"Page {i}: {len(split['markdown'])} chars")
    # Save each page separately
    with open(f"page_{i}.md", "w") as f:
        f.write(split["markdown"])
```

### Using document URL instead of file upload
```python
import requests

API_KEY = "your_api_key_here"
API_URL = "https://api.va.landing.ai/v1/ade/parse"

headers = {"Authorization": f"Bearer {API_KEY}"}

data = {
    "document_url": "https://example.com/sample.pdf",
    "model": "dpt-2-latest"
}

response = requests.post(API_URL, headers=headers, data=data)
result = response.json()

print(result["markdown"])
```

### Complete parse and extract workflow
```python
import requests
import json

API_KEY = "your_api_key_here"
PARSE_URL = "https://api.va.landing.ai/v1/ade/parse"
EXTRACT_URL = "https://api.va.landing.ai/v1/ade/extract"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Step 1: Parse PDF to markdown
with open("invoice.pdf", "rb") as f:
    files = {"document": ("invoice.pdf", f, "application/pdf")}
    data = {"model": "dpt-2-latest"}
    parse_response = requests.post(PARSE_URL, headers=headers, files=files, data=data)

parse_result = parse_response.json()
markdown_content = parse_result["markdown"]

# Save markdown for extraction
with open("temp_markdown.md", "w", encoding="utf-8") as f:
    f.write(markdown_content)

# Step 2: Define extraction schema
extraction_schema = {
    "type": "object",
    "properties": {
        "vendor_name": {
            "type": "string",
            "description": "Name of the vendor or supplier"
        },
        "invoice_number": {
            "type": "string",
            "description": "The invoice number"
        },
        "total_amount": {
            "type": "number",
            "description": "Total invoice amount"
        },
        "invoice_date": {
            "type": "string",
            "description": "Date of the invoice"
        }
    },
    "required": ["vendor_name", "invoice_number", "total_amount"]
}

# Step 3: Extract fields from markdown
with open("temp_markdown.md", "rb") as f:
    files = {"markdown": ("temp_markdown.md", f, "text/markdown")}
    data = {
        "schema": json.dumps(extraction_schema),
        "model": "extract-latest"
    }
    extract_response = requests.post(EXTRACT_URL, headers=headers, files=files, data=data)

extract_result = extract_response.json()

print("Extracted fields:", extract_result["extraction"])
print("Field references:", extract_result["extraction_metadata"])
```

### Async processing for large documents (Parse Jobs)
```python
import requests
import time

API_KEY = "your_api_key_here"
CREATE_JOB_URL = "https://api.va.landing.ai/v1/ade/parse/jobs"
GET_JOB_URL = "https://api.va.landing.ai/v1/ade/parse/jobs/{job_id}"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Create async parse job
with open("large_document.pdf", "rb") as f:
    files = {"document": ("large_document.pdf", f, "application/pdf")}
    data = {"model": "dpt-2-latest"}

    response = requests.post(CREATE_JOB_URL, headers=headers, files=files, data=data)

job_data = response.json()
job_id = job_data["job_id"]
print(f"Created job: {job_id}")

# Poll for completion
while True:
    status_response = requests.get(
        GET_JOB_URL.format(job_id=job_id),
        headers=headers
    )
    status_data = status_response.json()

    if status_data["status"] == "completed":
        print("Job completed!")
        print(status_data["data"]["markdown"][:500])
        break
    elif status_data["status"] == "failed":
        print(f"Job failed: {status_data.get('error')}")
        break
    else:
        print(f"Status: {status_data['status']}, waiting...")
        time.sleep(5)
```

### Error handling with retries
```python
import requests
import time
from requests.exceptions import RequestException

API_KEY = "your_api_key_here"
API_URL = "https://api.va.landing.ai/v1/ade/parse"

def parse_with_retry(file_path, max_retries=3, initial_wait=1):
    """Parse document with exponential backoff retry."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    wait_time = initial_wait

    for attempt in range(max_retries):
        try:
            with open(file_path, "rb") as f:
                files = {"document": (file_path, f, "application/pdf")}
                data = {"model": "dpt-2-latest"}

                response = requests.post(
                    API_URL,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=120
                )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                wait_time *= 2  # Exponential backoff
            elif response.status_code in [408, 502, 503, 504]:
                print(f"Server error {response.status_code}, retrying...")
                time.sleep(wait_time)
                wait_time *= 2
            else:
                response.raise_for_status()

        except RequestException as e:
            print(f"Request failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(wait_time)
                wait_time *= 2

    raise Exception(f"Failed after {max_retries} attempts")

# Usage
result = parse_with_retry("document.pdf")
print(result["markdown"])
```

---

## ADE Extract API parameters

The Extract API pulls structured fields from parsed markdown:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `markdown` | file | One of `markdown` or `markdown_url` | Markdown file to extract from |
| `markdown_url` | string | One of `markdown` or `markdown_url` | URL to markdown file |
| `schema` | string (JSON) | **Required** | Valid JSON schema defining fields to extract |
| `model` | string | Optional | Extraction model: `extract-latest`, `extract-20251024` |

### Extract response schema
```json
{
  "extraction": {
    "field_name": "extracted_value"
  },
  "extraction_metadata": {
    "field_name": {
      "value": "extracted_value",
      "references": ["chunk_uuid_1", "chunk_uuid_2"]
    }
  },
  "metadata": {
    "filename": "document.md",
    "org_id": null,
    "duration_ms": 1018,
    "credit_usage": 0.6,
    "version": "extract-latest"
  }
}
```

---

## Legacy API parameters (deprecated)

The original combined endpoint at `/v1/tools/agentic-document-analysis` offers additional tuning options not yet available in the new endpoints:

| Parameter | Type | Description |
|-----------|------|-------------|
| `pdf` | file | PDF file (50 pages max) |
| `image` | file | Image file (50MB max) |
| `pages` | string | Specific pages to process: `"0,1,2"` |
| `include_marginalia` | boolean | Include headers, footers, margin notes |
| `include_metadata_in_markdown` | boolean | Embed metadata in markdown output |
| `enable_rotation_detection` | boolean | Auto-detect and correct rotated pages |
| `fields_schema` | JSON string | Extraction schema for combined parse+extract |

### Legacy endpoint cURL
```bash
curl -X POST 'https://api.va.landing.ai/v1/tools/agentic-document-analysis' \
  -H 'Authorization: Bearer YOUR_API_KEY' \
  -F 'pdf=@document.pdf' \
  -F 'include_marginalia=true' \
  -F 'include_metadata_in_markdown=true' \
  -F 'enable_rotation_detection=false' \
  -F 'fields_schema={"type":"object","properties":{"name":{"type":"string"}}}'
```

---

## API limits, quotas, and supported formats

### Document size limits

| API | Page Limit | File Size |
|-----|------------|-----------|
| ADE Parse | **100 pages** per request | — |
| ADE Parse Jobs (async) | **1,000 pages** | **1 GB** |
| Legacy endpoint | 50 pages | 50 MB (images) |

### Supported file types
- **Documents**: PDF, TIFF, ODP (OpenDocument Presentation)
- **Images**: PNG, JPEG/JPG, and other OpenCV-supported formats

### Rate limiting and retries
- Automatic retry on: **408, 429, 502, 503, 504**
- Default: 2 retries with exponential backoff
- Initial retry wait: 1 second (increases exponentially with jitter up to 10 seconds)
- The Python SDK handles rate limiting automatically; for raw requests, implement exponential backoff

### Credit pricing
- **dpt-2 models**: 3 credits per page
- **dpt-2-mini**: 1.5 credits per page
- **Zero Data Retention (ZDR)**: +1 credit per page
- Extract API: ~0.6 credits per extraction

---

## Configuration via environment variables

The official Python libraries support these environment variables for tuning:

```bash
# Authentication
export VISION_AGENT_API_KEY="your-api-key"

# Parallelism (for batch processing with SDK)
export BATCH_SIZE=4           # Files processed in parallel (default: 4)
export MAX_WORKERS=5          # Threads per file (default: 5)

# Retry behavior
export MAX_RETRIES=100        # Maximum retry attempts (default: 100)
export MAX_RETRY_WAIT_TIME=60 # Max wait between retries in seconds

# Logging
export RETRY_LOGGING_STYLE=log_msg  # Options: log_msg, inline_block, none

# EU endpoint (legacy library)
export ENDPOINT_HOST=https://api.va.eu-west-1.landing.ai
```

---

## Key differences between legacy and new APIs

| Feature | New API (`/v1/ade/parse`) | Legacy (`/v1/tools/agentic-document-analysis`) |
|---------|---------------------------|------------------------------------------------|
| Workflow | Decoupled parse + extract | Combined single call |
| Response wrapper | Direct JSON | Wrapped in `data` object |
| Bounding box keys | `left`, `top`, `right`, `bottom` | `l`, `t`, `r`, `b` |
| Chunk type field | `type` | `chunk_type` |
| Chunk ID field | `id` | `chunk_id` |
| Chunk content | `markdown` attribute | `text` attribute |
| Marginalia control | Not yet available | `include_marginalia` parameter |
| Rotation detection | Not yet available | `enable_rotation_detection` parameter |
| Page selection | Full document only | `pages` parameter |

## Conclusion

Landing AI's ADE API provides a production-ready document extraction solution with **three key integration patterns**: the modern decoupled Parse/Extract endpoints for flexibility, the Parse Jobs endpoint for documents up to 1,000 pages, and the legacy combined endpoint for backward compatibility. The API excels at preserving complex layouts—tables, forms, signatures, and visual relationships—while providing visual grounding coordinates that trace every extracted value back to its source location. For most new integrations, use the `/v1/ade/parse` endpoint with the `dpt-2-latest` model and Bearer token authentication.
