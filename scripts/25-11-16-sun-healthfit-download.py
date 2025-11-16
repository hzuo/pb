#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "requests>=2.32.0",
#   "pyjwt[crypto]>=2.10.0",
# ]
# ///

import base64
import datetime
import json
import os
import re
import time
import unicodedata

import jwt
import requests

# --------------------------------------------------------------------
# Hardcoded configuration
# --------------------------------------------------------------------

# Base64-encoded service account JSON (the one you're already using)
SERVICE_ACCOUNT_ENV_VAR = "DL_25_10_21_DATALAND_GOOG_SERVICES_SA_JSON_BASE64"

# Google Drive folder ID to sync from
DRIVE_FOLDER_ID = "1JaOPfeDuyoEgI9di550AmgfAL9kai1H1"

# OAuth2 scope for read-only Drive access
DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.readonly"

# Local directory to sync into
LOCAL_DIR = "misc"

# Name pattern of source files. We only assume a date prefix:
#   YYYY-MM-DD-<rest>
# and we optionally strip a leading 6-digit time segment from <rest>.
SOURCE_NAME_PATTERN = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$")


# --------------------------------------------------------------------
# Auth helpers
# --------------------------------------------------------------------


def load_service_account():
    encoded = os.environ.get(SERVICE_ACCOUNT_ENV_VAR)
    if not encoded:
        raise SystemExit(
            f"Environment variable {SERVICE_ACCOUNT_ENV_VAR} is not set.\n"
            "It must contain the base64-encoded service account JSON."
        )

    sa_json_str = base64.b64decode(encoded).decode("utf-8")
    creds = json.loads(sa_json_str)

    required_keys = ["client_email", "private_key", "token_uri"]
    missing = [k for k in required_keys if k not in creds]
    if missing:
        raise SystemExit(f"Service account JSON is missing keys: {missing}")

    return creds


def get_access_token(creds):
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
        raise SystemExit(
            f"Failed to obtain access token ({resp.status_code}): {resp.text[:500]}"
        )

    token_data = resp.json()
    return token_data["access_token"]


# --------------------------------------------------------------------
# Drive API helpers (no Google SDK, just HTTP)
# --------------------------------------------------------------------


def list_drive_files(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    all_files = []
    page_token = None

    while True:
        params = {
            "q": f"'{DRIVE_FOLDER_ID}' in parents and trashed = false",
            "fields": "files(id,name,mimeType),nextPageToken",
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
            raise SystemExit(
                f"Drive list failed ({resp.status_code}): {resp.text[:500]}"
            )

        data = resp.json()
        all_files.extend(data.get("files", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return all_files


def download_file(access_token, file_id, dest_path):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    resp = requests.get(url, headers=headers, timeout=60)
    if not resp.ok:
        raise RuntimeError(
            f"Download failed for {file_id} ({resp.status_code}): {resp.text[:300]}"
        )

    with open(dest_path, "wb") as f:
        f.write(resp.content)


# --------------------------------------------------------------------
# Filename conversion logic
# --------------------------------------------------------------------


def convert_remote_name_to_local(name):
    """
    Convert a remote filename into our normalized local pattern.

    Expected prefix:  YYYY-MM-DD-
    After that, we *optionally* strip a 6-digit time segment if present:

        2025-11-15-184346-Outdoor Running-Hao’s Apple Watch.fit
    or:  2025-11-15-Outdoor Running-Hao’s Apple Watch.fit

    Both become:
        25-11-15-sat-outdoor-running-hao-s-apple-watch.fit
    """

    m = SOURCE_NAME_PATTERN.match(name)
    if not m:
        return None  # unknown pattern

    year, month, day = map(int, m.group(1, 2, 3))
    rest = m.group(4)

    # If rest starts with a 6-digit segment and a dash, strip it (likely a time HHMMSS)
    m_time = re.match(r"^(\d{6})-(.+)$", rest)
    if m_time:
        rest = m_time.group(2)

    date = datetime.date(year, month, day)
    yy = f"{year % 100:02d}"
    mm = f"{month:02d}"
    dd = f"{day:02d}"
    dow = date.strftime("%a").lower()  # mon, tue, wed, ...

    # Split extension
    if "." in rest:
        base_no_ext, ext = rest.rsplit(".", 1)
        ext = ext.lower()
    else:
        base_no_ext, ext = rest, ""

    # Normalize to ASCII, lowercase, dash-separated
    base = unicodedata.normalize("NFKD", base_no_ext)
    base = base.replace(" ", " ")  # replace non-breaking spaces
    base = base.lower()
    base = re.sub(r"[^a-z0-9]+", "-", base)
    base = base.strip("-") or "file"

    new_name = f"{yy}-{mm}-{dd}-{dow}-{base}"
    if ext:
        new_name += f".{ext}"

    return new_name


# --------------------------------------------------------------------
# Sync logic
# --------------------------------------------------------------------


def sync():
    os.makedirs(LOCAL_DIR, exist_ok=True)

    print("Loading service account credentials...")
    creds = load_service_account()

    print("Obtaining access token...")
    access_token = get_access_token(creds)

    print("Listing files from Google Drive folder...")
    files = list_drive_files(access_token)
    print(f"Found {len(files)} file(s) in folder {DRIVE_FOLDER_ID}")

    newly_downloaded = []
    skipped_existing = []
    skipped_unmatched = []

    for f in files:
        file_id = f.get("id")
        name = f.get("name") or ""

        local_name = convert_remote_name_to_local(name)
        if not local_name:
            skipped_unmatched.append(name)
            print(f"  [skip:not-matching-pattern] {name}")
            continue

        dest_path = os.path.join(LOCAL_DIR, local_name)

        if os.path.exists(dest_path):
            skipped_existing.append(dest_path)
            print(f"  [skip:exists] {dest_path}")
            continue

        print(f"  [download] {name} -> {dest_path}")
        try:
            download_file(access_token, file_id, dest_path)
        except Exception as e:
            print(f"    ERROR downloading {name}: {e}")
            continue

        newly_downloaded.append(dest_path)

    print("\nSummary")
    print("-------")
    print(f"Newly downloaded: {len(newly_downloaded)}")
    print(f"Already existed:  {len(skipped_existing)}")
    print(f"Pattern-mismatch: {len(skipped_unmatched)}")


def main():
    try:
        sync()
    except KeyboardInterrupt:
        print("\nInterrupted.")


if __name__ == "__main__":
    main()
