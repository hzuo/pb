import base64
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Literal

import jwt  # pyjwt
import pypandoc
import requests
from requests.adapters import HTTPAdapter, Retry


def find_git_root() -> Path:
    start = Path(__file__).resolve().parent
    for parent in [start] + list(start.parents):
        if (parent / ".git").is_dir():
            return parent
    raise RuntimeError(f"could not locate git root from starting dir: {start}")


def new_requests_session_with_retry() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
    retry_adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", retry_adapter)
    return session


# https://docs.firecrawl.dev/api-reference/endpoint/scrape
def firecrawl_scrape_url(url: str, include_tags: list[str] | None = None, exclude_tags: list[str] | None = None) -> str:
    session = new_requests_session_with_retry()
    api_key = os.environ["FIRECRAWL_API_KEY"]
    req = {
        "url": url,
        "formats": ["markdown"],  # minimal equivalent
        "maxAge": 60 * 60 * 24,  # 1 day
        # "maxAge": 0,  # force a fresh scrape instead of cached
    }
    if include_tags:
        req["includeTags"] = include_tags
    if exclude_tags:
        req["excludeTags"] = exclude_tags
    res = session.post(
        "https://api.firecrawl.dev/v2/scrape",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=req,
        timeout=60,
    )
    res.raise_for_status()
    res_json = res.json()
    return res_json["data"]["markdown"]


def gdoc_md_get(
    file_name: Literal["TODO"],
) -> str:
    MAPPING = {
        "TODO": {
            "file_id": "TODO",
            "url": "TODO",
        },
    }
    SA_ENV = "DL_25_10_21_DATALAND_GOOG_SERVICES_SA_JSON_BASE64"

    assert file_name in MAPPING, f"Invalid file name: {file_name}"
    file_id = MAPPING[file_name]["file_id"]

    sa_b64 = os.environ.get(SA_ENV)
    assert sa_b64, f"Missing env var: {SA_ENV}"

    try:
        pypandoc.get_pandoc_path()
    except OSError:
        pypandoc.download_pandoc()

    sa_json = json.loads(base64.b64decode(sa_b64).decode("utf-8"))
    client_email = sa_json["client_email"]
    private_key = sa_json["private_key"]
    token_uri = sa_json.get("token_uri", "https://oauth2.googleapis.com/token")

    now = int(time.time())
    assertion = jwt.encode(
        {
            "iss": client_email,
            "scope": "https://www.googleapis.com/auth/drive.readonly",
            "aud": token_uri,
            "exp": now + 3600,
            "iat": now,
        },
        private_key,
        algorithm="RS256",
    )

    tok = requests.post(
        token_uri,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        },
        timeout=60,
    )
    tok.raise_for_status()
    access_token = tok.json()["access_token"]

    r = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}/export",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        timeout=120,
    )
    r.raise_for_status()

    git_root = find_git_root()
    scratch_dir = git_root / "_scratch"
    scratch_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(dir=scratch_dir, prefix="gdoc-md-") as ws0:
        ws = Path(ws0)
        docx_path = ws / "source.docx"
        md_path = ws / "out.md"

        docx_path.write_bytes(r.content)

        pypandoc.convert_file(str(docx_path), to="gfm", outputfile=str(md_path))
        return md_path.read_text(encoding="utf-8")
