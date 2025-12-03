#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "requests>=2.32.0",
#   "pyjwt[crypto]>=2.10.0",
# ]
# ///

"""
Stony Brook Medicine Clinical Notes - Google Drive Sync

Syncs the _scratch/mf folder to a Google Drive Shared Drive folder.

Logic (stateless, idempotent):

    remote_files = list_drive_folder()
    for each file in local_folder:
        if file.name not in remote_files:
            upload(file)

Prerequisites:
- DL_25_10_21_DATALAND_GOOG_SERVICES_SA_JSON_BASE64 environment variable set
- Service account has access to the target Shared Drive folder

Usage:
    ./scripts/25-12-02-tue-stonybrook-notes-gdrive-sync.py
    ./scripts/25-12-02-tue-stonybrook-notes-gdrive-sync.py --dry-run
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import jwt
import requests

# --------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------

GIT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / ".git").exists())
WORKSPACE = (GIT_ROOT / "_scratch" / "mf").resolve()

# Service account credentials (base64-encoded JSON)
SERVICE_ACCOUNT_ENV_VAR = "DL_25_10_21_DATALAND_GOOG_SERVICES_SA_JSON_BASE64"

# Target Google Drive Shared Drive folder
DRIVE_FOLDER_ID = "1zGsmdCoYFpIalgxteU2Ta33HQisJRZK9"

# OAuth2 scope - need full drive access for Shared Drives
DRIVE_SCOPE = "https://www.googleapis.com/auth/drive"

DEFAULT_WORKERS = 8

# --------------------------------------------------------------------
# Auth helpers
# --------------------------------------------------------------------


def load_service_account():
    """Load service account credentials from environment variable."""
    encoded = os.environ.get(SERVICE_ACCOUNT_ENV_VAR)
    if not encoded:
        print(f"ERROR: {SERVICE_ACCOUNT_ENV_VAR} environment variable not set")
        sys.exit(1)

    sa_json_str = base64.b64decode(encoded).decode("utf-8")
    creds = json.loads(sa_json_str)

    required_keys = ["client_email", "private_key", "token_uri"]
    missing = [k for k in required_keys if k not in creds]
    if missing:
        print(f"ERROR: Service account JSON is missing keys: {missing}")
        sys.exit(1)

    return creds


def get_access_token(creds):
    """Get OAuth2 access token using service account credentials."""
    sa_email = creds["client_email"]
    private_key = creds["private_key"]
    token_uri = creds.get("token_uri", "https://oauth2.googleapis.com/token")

    now = int(time.time())
    payload = {
        "iss": sa_email,
        "scope": DRIVE_SCOPE,
        "aud": token_uri,
        "exp": now + 3600,
        "iat": now,
    }
    headers = {}
    if creds.get("private_key_id"):
        headers["kid"] = creds["private_key_id"]

    signed_jwt = jwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers=headers or None,
    )

    resp = requests.post(
        token_uri,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": signed_jwt,
        },
        timeout=30,
    )

    if not resp.ok:
        print(
            f"ERROR: Failed to obtain access token ({resp.status_code}): {resp.text[:500]}"
        )
        sys.exit(1)

    token_data = resp.json()
    return token_data["access_token"]


# --------------------------------------------------------------------
# Drive API helpers
# --------------------------------------------------------------------


def list_drive_files(access_token: str) -> dict[str, str]:
    """
    List all files in the target Drive folder.
    Returns dict mapping filename -> file_id.
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    files_map = {}
    page_token = None

    while True:
        params = {
            "q": f"'{DRIVE_FOLDER_ID}' in parents and trashed = false",
            "fields": "files(id,name),nextPageToken",
            "pageSize": 1000,
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
        }
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(
            "https://www.googleapis.com/drive/v3/files",
            headers=headers,
            params=params,
            timeout=30,
        )
        if not resp.ok:
            raise RuntimeError(
                f"Drive list failed ({resp.status_code}): {resp.text[:500]}"
            )

        data = resp.json()
        for f in data.get("files", []):
            files_map[f["name"]] = f["id"]

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return files_map


def upload_file(access_token: str, local_path: Path) -> tuple[bool, str]:
    """
    Upload a file to the target Drive folder.
    Returns (success, message).
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(str(local_path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    # Metadata for the file
    metadata = {
        "name": local_path.name,
        "parents": [DRIVE_FOLDER_ID],
    }

    try:
        file_size = local_path.stat().st_size

        # For small files (< 5MB), use simple multipart upload
        if file_size < 5 * 1024 * 1024:
            with open(local_path, "rb") as f:
                file_content = f.read()

            boundary = "===boundary==="
            body_parts = [
                f"--{boundary}\r\n".encode(),
                b"Content-Type: application/json; charset=UTF-8\r\n\r\n",
                json.dumps(metadata).encode(),
                f"\r\n--{boundary}\r\n".encode(),
                f"Content-Type: {mime_type}\r\n\r\n".encode(),
                file_content,
                f"\r\n--{boundary}--".encode(),
            ]
            body = b"".join(body_parts)

            resp = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true",
                headers={
                    **headers,
                    "Content-Type": f"multipart/related; boundary={boundary}",
                },
                data=body,
                timeout=120,
            )
        else:
            # For larger files, use resumable upload
            resp = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&supportsAllDrives=true",
                headers={
                    **headers,
                    "Content-Type": "application/json; charset=UTF-8",
                    "X-Upload-Content-Type": mime_type,
                    "X-Upload-Content-Length": str(file_size),
                },
                json=metadata,
                timeout=30,
            )

            if not resp.ok:
                return False, f"Failed to initiate upload: {resp.status_code}"

            upload_url = resp.headers.get("Location")
            if not upload_url:
                return False, "No upload URL returned"

            with open(local_path, "rb") as f:
                resp = requests.put(
                    upload_url,
                    headers={"Content-Type": mime_type},
                    data=f,
                    timeout=300,
                )

        if resp.ok:
            size_kb = file_size / 1024
            return True, f"uploaded ({size_kb:.1f} KB)"
        else:
            return False, f"Upload failed: {resp.status_code} - {resp.text[:200]}"

    except Exception as e:
        return False, f"Exception: {e}"


def upload_file_worker(args: tuple) -> tuple[Path, bool, str]:
    """Worker function for parallel uploads."""
    local_path, access_token, dry_run = args

    if dry_run:
        size_kb = local_path.stat().st_size / 1024
        return local_path, True, f"would upload ({size_kb:.1f} KB, dry-run)"

    success, message = upload_file(access_token, local_path)
    return local_path, success, message


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Sync local folder to Google Drive")
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of parallel workers (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without actually uploading",
    )
    args = parser.parse_args()

    print(f"Workspace: {WORKSPACE}")
    print(f"Drive folder: {DRIVE_FOLDER_ID}")
    print(f"Workers: {args.workers}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Load credentials and get token
    print("Authenticating...")
    creds = load_service_account()
    access_token = get_access_token(creds)
    print("  OK")
    print()

    # List remote files
    print("Listing remote files...")
    remote_files = list_drive_files(access_token)
    print(f"  Found {len(remote_files)} files in Drive folder")
    print()

    # Find local files (PDFs and MDs, exclude TSV and guide files)
    local_files = sorted(list(WORKSPACE.glob("*.pdf")) + list(WORKSPACE.glob("*.md")))
    # Filter out guide/meta files that start with date prefix
    local_files = [f for f in local_files if not f.name.startswith("25-")]

    print(f"Found {len(local_files)} local files (PDFs + MDs)")

    # Find which need uploading
    to_upload = [f for f in local_files if f.name not in remote_files]
    already_synced = len(local_files) - len(to_upload)

    print(f"Already synced: {already_synced}")
    print(f"To upload: {len(to_upload)}")
    print()

    if not to_upload:
        print("Nothing to upload!")
        return

    # Upload with thread pool
    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        work_items = [(f, access_token, args.dry_run) for f in to_upload]
        futures = {
            executor.submit(upload_file_worker, item): item[0] for item in work_items
        }

        for i, future in enumerate(as_completed(futures), 1):
            local_path, success, message = future.result()
            status = "OK" if success else "FAIL"
            print(f"[{i}/{len(to_upload)}] {status}: {local_path.name}")
            print(f"         {message}")

            if success and "uploaded" in message:
                success_count += 1
            elif not success:
                fail_count += 1

    print()
    print(f"Done! Uploaded: {success_count}, Failed: {fail_count}")


if __name__ == "__main__":
    main()
