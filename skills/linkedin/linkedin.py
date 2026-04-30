#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///
"""
LinkedIn API CLI — auth, whoami, stats.

Usage:
  uv run skills/linkedin/linkedin.py auth                       # one-time OAuth
  uv run skills/linkedin/linkedin.py whoami                     # verify connection
  uv run skills/linkedin/linkedin.py stats <post-url> [...]     # likes/comments per post
  uv run skills/linkedin/linkedin.py stats <urls...> --csv output/performance.csv

Setup:
  1. Create app at https://developer.linkedin.com/ → My Apps → Create app
  2. Auth tab: add Authorized redirect URL: http://localhost:8765/callback/
  3. Products tab: request "Sign In with LinkedIn using OpenID Connect" and "Share on LinkedIn"
     (For richer stats request whatever LinkedIn currently lists for r_member_social.)
  4. Copy .env.example to .env and fill LINKEDIN_CLIENT_ID + LINKEDIN_CLIENT_SECRET
  5. Run `uv run skills/linkedin/linkedin.py auth`
"""

import argparse
import csv
import http.server
import json
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
TOKEN_FILE = REPO_ROOT / ".linkedin-token.json"

load_dotenv(ENV_FILE)

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8765/callback/").strip()
SCOPES = os.getenv("LINKEDIN_SCOPES", "openid profile w_member_social").strip()
API_VERSION = os.getenv("LINKEDIN_API_VERSION", "202601").strip()

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
API_BASE = "https://api.linkedin.com"

CALLBACK_PORT = 8765


# ---------- Token storage ----------

def save_token(data: dict) -> None:
    data = dict(data)
    if "expires_in" in data and "expires_at" not in data:
        data["expires_at"] = int(time.time()) + int(data["expires_in"])
    TOKEN_FILE.write_text(json.dumps(data, indent=2))
    print(f"[ok] Token saved to {TOKEN_FILE}", file=sys.stderr)


def load_token() -> Optional[dict]:
    if not TOKEN_FILE.exists():
        return None
    return json.loads(TOKEN_FILE.read_text())


def get_access_token() -> str:
    token = load_token()
    if not token:
        sys.exit("[err] No token. Run `auth` first.")
    if token.get("expires_at") and int(time.time()) > token["expires_at"]:
        sys.exit("[err] Token expired. Run `auth` again.")
    return token["access_token"]


# ---------- OAuth flow ----------

class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    code: Optional[str] = None
    state: Optional[str] = None
    error: Optional[str] = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        _CallbackHandler.code = params.get("code", [None])[0]
        _CallbackHandler.state = params.get("state", [None])[0]
        _CallbackHandler.error = params.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        if _CallbackHandler.error:
            msg = f"<h1>Auth failed: {_CallbackHandler.error}</h1>"
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
        sys.exit("[err] LINKEDIN_CLIENT_ID / LINKEDIN_CLIENT_SECRET not set in .env")

    state = secrets.token_urlsafe(16)
    auth_url = (
        f"{AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI, safe='')}"
        f"&state={state}"
        f"&scope={urllib.parse.quote(SCOPES)}"
    )

    server = http.server.HTTPServer(("localhost", CALLBACK_PORT), _CallbackHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print(f"[info] Opening browser for LinkedIn OAuth ({SCOPES})", file=sys.stderr)
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


# ---------- whoami ----------

def run_whoami():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{API_BASE}/v2/userinfo", headers=headers, timeout=30)
    if resp.status_code != 200:
        sys.exit(f"[err] {resp.status_code} {resp.text}")
    info = resp.json()
    print(json.dumps(info, indent=2, ensure_ascii=False))


# ---------- stats ----------

def post_url_to_urn(url: str) -> str:
    """
    Extract the activity/share/ugcPost URN from a LinkedIn post URL.
    Supported patterns:
      .../feed/update/urn:li:activity:1234567890/
      .../posts/...activity-1234567890-...
      .../posts/...ugcPost-1234567890-...
    """
    if "urn:li:activity:" in url:
        start = url.find("urn:li:activity:") + len("urn:li:activity:")
        end = start
        while end < len(url) and url[end].isdigit():
            end += 1
        return f"urn:li:activity:{url[start:end]}"

    for kind in ("activity-", "ugcPost-", "share-"):
        if kind in url:
            start = url.find(kind) + len(kind)
            end = start
            while end < len(url) and url[end].isdigit():
                end += 1
            urn_kind = kind.rstrip("-")
            return f"urn:li:{urn_kind}:{url[start:end]}"

    raise ValueError(f"Could not extract LinkedIn URN from URL: {url}")


def fetch_social_actions(post_urn: str, headers: dict) -> dict:
    encoded = urllib.parse.quote(post_urn, safe="")
    resp = requests.get(
        f"{API_BASE}/v2/socialActions/{encoded}",
        headers=headers,
        timeout=30,
    )
    return {"status": resp.status_code, "body": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text}


def run_stats(post_urls, output_csv: Optional[Path] = None):
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": API_VERSION,
    }

    rows = []
    for url in post_urls:
        try:
            urn = post_url_to_urn(url)
        except ValueError as e:
            print(f"[warn] {e}", file=sys.stderr)
            continue

        result = fetch_social_actions(urn, headers)
        if result["status"] != 200:
            print(f"[warn] {urn}: HTTP {result['status']} — {result['body']}", file=sys.stderr)
            continue

        body = result["body"]
        likes = (
            body.get("likesSummary", {}).get("totalLikes")
            or body.get("numLikes")
            or 0
        )
        comments = (
            body.get("commentsSummary", {}).get("aggregatedTotalComments")
            or body.get("numComments")
            or 0
        )

        rows.append({
            "post_urn": urn,
            "url": url,
            "likes": likes,
            "comments": comments,
        })

    print(f"\n{'URN':<48} {'Likes':>6} {'Comments':>10}")
    print("-" * 68)
    for r in rows:
        print(f"{r['post_urn']:<48} {r['likes']:>6} {r['comments']:>10}")

    if output_csv:
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        with output_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["post_urn", "url", "likes", "comments"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n[ok] Wrote {len(rows)} rows to {output_csv}", file=sys.stderr)


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(description="LinkedIn API CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("auth", help="One-time OAuth flow")
    sub.add_parser("whoami", help="Verify connectivity (prints profile info)")

    p_stats = sub.add_parser("stats", help="Pull engagement stats for given posts")
    p_stats.add_argument("urls", nargs="+", help="LinkedIn post URL(s)")
    p_stats.add_argument("--csv", type=Path, default=None, help="Write CSV to this path")

    args = parser.parse_args()

    if args.cmd == "auth":
        run_auth()
    elif args.cmd == "whoami":
        run_whoami()
    elif args.cmd == "stats":
        run_stats(args.urls, args.csv)


if __name__ == "__main__":
    main()
