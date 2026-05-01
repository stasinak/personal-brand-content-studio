#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///
"""
Google Drive API CLI — auth, whoami, list, find, upload, download, mkdir.

Usage:
  uv run skills/google-drive/drive.py auth                              # one-time OAuth
  uv run skills/google-drive/drive.py whoami                            # verify connection
  uv run skills/google-drive/drive.py list [--parent <folder-id>] [--limit 20]
  uv run skills/google-drive/drive.py find "<query>"                    # search by title
  uv run skills/google-drive/drive.py upload <local-path> [--parent <folder-id>] [--name <name>]
  uv run skills/google-drive/drive.py download <file-id> <local-path>
  uv run skills/google-drive/drive.py mkdir <folder-name> [--parent <folder-id>]

Setup:
  1. Create GCP project + enable Google Drive API
  2. OAuth consent screen → External, Testing mode, add yourself as test user
  3. Create OAuth client ID → "Desktop app"
  4. Add to .env:
       GOOGLE_CLIENT_ID=...
       GOOGLE_CLIENT_SECRET=...
  5. Run `uv run skills/google-drive/drive.py auth`
"""

import argparse
import http.server
import json
import mimetypes
import os
import secrets
import sys
import threading
import time
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE = REPO_ROOT / ".env"
TOKEN_FILE = REPO_ROOT / ".google-drive-token.json"

load_dotenv(ENV_FILE)

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
SCOPES = os.getenv("GOOGLE_DRIVE_SCOPES", "https://www.googleapis.com/auth/drive openid email").strip()

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API_BASE = "https://www.googleapis.com/drive/v3"
UPLOAD_BASE = "https://www.googleapis.com/upload/drive/v3"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

CALLBACK_PORT = 8766
REDIRECT_URI = f"http://localhost:{CALLBACK_PORT}/callback/"


# ---------- Token storage ----------

def save_token(data: dict) -> None:
    existing = load_token() or {}
    merged = {**existing, **data}
    if "expires_in" in data:
        merged["expires_at"] = int(time.time()) + int(data["expires_in"])
    TOKEN_FILE.write_text(json.dumps(merged, indent=2))
    print(f"[ok] Token saved to {TOKEN_FILE}", file=sys.stderr)


def load_token() -> Optional[dict]:
    if not TOKEN_FILE.exists():
        return None
    return json.loads(TOKEN_FILE.read_text())


def refresh_access_token(refresh_token: str) -> dict:
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"[err] Token refresh failed: {resp.status_code} {resp.text}")
    return resp.json()


def get_access_token() -> str:
    token = load_token()
    if not token:
        sys.exit("[err] No token. Run `auth` first.")
    if token.get("expires_at") and int(time.time()) > token["expires_at"] - 60:
        if not token.get("refresh_token"):
            sys.exit("[err] Token expired and no refresh_token. Run `auth` again.")
        print("[info] Refreshing access token...", file=sys.stderr)
        new_data = refresh_access_token(token["refresh_token"])
        save_token(new_data)
        token = load_token()
    return token["access_token"]


# ---------- OAuth flow ----------

class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None
    expected_state: Optional[str] = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        err = params.get("error", [None])[0]
        state = params.get("state", [None])[0]

        # Ignore non-callback hits (favicon, etc.) and don't overwrite once set.
        if not parsed.path.rstrip("/").endswith("/callback"):
            self.send_response(404)
            self.end_headers()
            return
        if not code and not err:
            self.send_response(400)
            self.end_headers()
            return
        # Reject stale callbacks (e.g. old browser tab from prior auth attempt).
        if state != _CallbackHandler.expected_state:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>Stale OAuth callback ignored. Close this tab and retry from the new auth URL.</h1>")
            return
        if _CallbackHandler.code is not None or _CallbackHandler.error is not None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h1>Already received auth response.</h1>")
            return

        _CallbackHandler.code = code
        _CallbackHandler.state = state
        _CallbackHandler.error = err
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if err:
            msg = f"<h1>Auth failed: {err}</h1>"
            desc = params.get("error_description", [""])[0]
            if desc:
                msg += f"<p>{desc}</p>"
        else:
            msg = "<h1>Authentication successful — you can close this tab.</h1>"
        self.wfile.write(msg.encode("utf-8"))

    def log_message(self, *args, **kwargs):
        return


def run_auth():
    if not CLIENT_ID or not CLIENT_SECRET:
        sys.exit("[err] GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set in .env")

    state = secrets.token_urlsafe(16)
    _CallbackHandler.expected_state = state
    _CallbackHandler.code = None
    _CallbackHandler.error = None
    _CallbackHandler.state = None
    auth_url = (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
        f"&state={state}"
        f"&scope={urllib.parse.quote(SCOPES)}"
        f"&access_type=offline"
        f"&prompt=consent%20select_account"
    )

    server = http.server.HTTPServer(("localhost", CALLBACK_PORT), _CallbackHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print(f"[info] Opening browser for Google OAuth ({SCOPES})", file=sys.stderr)
    print(f"[info] If browser doesn't open, paste this URL:\n{auth_url}\n", file=sys.stderr)
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    timeout = time.time() + 300
    while _CallbackHandler.code is None and _CallbackHandler.error is None:
        if time.time() > timeout:
            server.shutdown()
            sys.exit("[err] Timed out waiting for OAuth callback.")
        time.sleep(0.2)
    server.shutdown()

    if _CallbackHandler.error:
        sys.exit(f"[err] OAuth failed: {_CallbackHandler.error}")
    if _CallbackHandler.state != state:
        sys.exit("[err] State mismatch — possible CSRF.")

    print("[info] Exchanging code for access token...", file=sys.stderr)
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": _CallbackHandler.code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"[err] Token exchange failed: {resp.status_code} {resp.text}")
    save_token(resp.json())
    print("[ok] Authenticated.", file=sys.stderr)


# ---------- API helpers ----------

def auth_headers() -> dict:
    return {"Authorization": f"Bearer {get_access_token()}"}


def run_whoami():
    headers = auth_headers()
    resp = requests.get(USERINFO_URL, headers=headers, timeout=30)
    if resp.status_code != 200:
        sys.exit(f"[err] {resp.status_code} {resp.text}")
    info = resp.json()
    about = requests.get(
        f"{API_BASE}/about",
        headers=headers,
        params={"fields": "user(displayName,emailAddress),storageQuota(limit,usage)"},
        timeout=30,
    ).json()
    print(json.dumps({"openid": info, "drive": about}, indent=2, ensure_ascii=False))


# ---------- list / find ----------

def _print_files(files):
    print(f"\n{'ID':<45} {'Type':<32} {'Title':<50}")
    print("-" * 130)
    for f in files:
        mime = f.get("mimeType", "")
        short_mime = mime.replace("application/vnd.google-apps.", "g.")
        title = f.get("name", "")[:48]
        print(f"{f['id']:<45} {short_mime:<32} {title:<50}")


def run_list(parent: Optional[str], limit: int):
    headers = auth_headers()
    q = "trashed = false"
    if parent:
        q += f" and '{parent}' in parents"
    resp = requests.get(
        f"{API_BASE}/files",
        headers=headers,
        params={
            "q": q,
            "pageSize": limit,
            "orderBy": "modifiedTime desc",
            "fields": "files(id,name,mimeType,modifiedTime,parents)",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"[err] {resp.status_code} {resp.text}")
    files = resp.json().get("files", [])
    _print_files(files)
    print(f"\n[ok] {len(files)} file(s)")


def run_find(query: str, limit: int):
    headers = auth_headers()
    safe_query = query.replace("'", "\\'")
    q = f"name contains '{safe_query}' and trashed = false"
    resp = requests.get(
        f"{API_BASE}/files",
        headers=headers,
        params={
            "q": q,
            "pageSize": limit,
            "orderBy": "modifiedTime desc",
            "fields": "files(id,name,mimeType,modifiedTime,parents)",
        },
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"[err] {resp.status_code} {resp.text}")
    files = resp.json().get("files", [])
    _print_files(files)
    print(f"\n[ok] {len(files)} match(es)")


# ---------- upload / download / mkdir ----------

def run_upload(local_path: Path, parent: Optional[str], name: Optional[str]):
    if not local_path.exists():
        sys.exit(f"[err] Local file not found: {local_path}")

    metadata = {"name": name or local_path.name}
    if parent:
        metadata["parents"] = [parent]

    mime_type, _ = mimetypes.guess_type(str(local_path))
    if not mime_type:
        mime_type = "application/octet-stream"

    boundary = f"----PB-{secrets.token_hex(8)}"
    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
        f"{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8")
    body += local_path.read_bytes()
    body += f"\r\n--{boundary}--".encode("utf-8")

    headers = {
        **auth_headers(),
        "Content-Type": f"multipart/related; boundary={boundary}",
    }
    resp = requests.post(
        f"{UPLOAD_BASE}/files",
        headers=headers,
        params={"uploadType": "multipart", "fields": "id,name,mimeType,webViewLink"},
        data=body,
        timeout=120,
    )
    if resp.status_code not in (200, 201):
        sys.exit(f"[err] Upload failed: {resp.status_code} {resp.text}")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


def run_download(file_id: str, local_path: Path):
    headers = auth_headers()
    resp = requests.get(
        f"{API_BASE}/files/{file_id}",
        headers=headers,
        params={"alt": "media"},
        timeout=120,
        stream=True,
    )
    if resp.status_code != 200:
        sys.exit(f"[err] Download failed: {resp.status_code} {resp.text}")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    with local_path.open("wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"[ok] Saved to {local_path}", file=sys.stderr)


def run_mkdir(name: str, parent: Optional[str]):
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent:
        metadata["parents"] = [parent]
    resp = requests.post(
        f"{API_BASE}/files",
        headers={**auth_headers(), "Content-Type": "application/json"},
        params={"fields": "id,name,webViewLink"},
        data=json.dumps(metadata),
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        sys.exit(f"[err] Folder create failed: {resp.status_code} {resp.text}")
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(description="Google Drive API CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("auth", help="One-time OAuth flow")
    sub.add_parser("whoami", help="Show authenticated user + storage")

    p_list = sub.add_parser("list", help="List recent files (or files in a folder)")
    p_list.add_argument("--parent", default=None, help="Folder id (omit for all)")
    p_list.add_argument("--limit", type=int, default=20)

    p_find = sub.add_parser("find", help="Search files by name")
    p_find.add_argument("query")
    p_find.add_argument("--limit", type=int, default=20)

    p_up = sub.add_parser("upload", help="Upload a local file")
    p_up.add_argument("path", type=Path)
    p_up.add_argument("--parent", default=None, help="Destination folder id")
    p_up.add_argument("--name", default=None, help="Override file name")

    p_dl = sub.add_parser("download", help="Download a file by id")
    p_dl.add_argument("file_id")
    p_dl.add_argument("path", type=Path)

    p_mk = sub.add_parser("mkdir", help="Create a folder")
    p_mk.add_argument("name")
    p_mk.add_argument("--parent", default=None)

    args = parser.parse_args()

    if args.cmd == "auth":
        run_auth()
    elif args.cmd == "whoami":
        run_whoami()
    elif args.cmd == "list":
        run_list(args.parent, args.limit)
    elif args.cmd == "find":
        run_find(args.query, args.limit)
    elif args.cmd == "upload":
        run_upload(args.path, args.parent, args.name)
    elif args.cmd == "download":
        run_download(args.file_id, args.path)
    elif args.cmd == "mkdir":
        run_mkdir(args.name, args.parent)


if __name__ == "__main__":
    main()
