#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "yt-dlp",
#   "youtube-transcript-api<1.0",
#   "google-api-python-client",
#   "google-auth-oauthlib",
#   "google-auth-httplib2",
#   "faster-whisper",
# ]
# ///
"""
Fetch a YouTube video transcript as plain text.

Four strategies tried in order, first success wins:
  1. YouTube Data API v3 (OAuth) — only for videos YOU OWN
  2. youtube-transcript-api — anonymous timedtext, may hit rate limits
  3. yt-dlp with cookies — fallback when timedtext is blocked
  4. Whisper local ASR — works for ANY video, downloads audio + transcribes

Strategy 4 is the universal fallback: free, no auth, no cookies, works for any
public video. Trade-off: 1-5 min processing on CPU. First run downloads model
(~500MB for default "small"). Disable with --no-whisper.

Usage:
    uv run skills/youtube-transcript-fetcher/fetch.py <url>
    uv run skills/youtube-transcript-fetcher/fetch.py <url> --lang en
    uv run skills/youtube-transcript-fetcher/fetch.py <url> --cookies .youtube-cookies.txt
    uv run skills/youtube-transcript-fetcher/fetch.py <url> --whisper-model tiny
    uv run skills/youtube-transcript-fetcher/fetch.py <url> --no-whisper
    uv run skills/youtube-transcript-fetcher/fetch.py auth   # one-time OAuth setup

Env (.env at project root):
    YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET — from Google Cloud Console
"""

import argparse
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"
TOKEN_PATH = REPO_ROOT / ".youtube-token.json"
OAUTH_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
OAUTH_REDIRECT_PORT = 8767


# ---------- env loading ----------


def load_env_file(path: Path) -> dict:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        env[key.strip()] = value
    return env


# ---------- video ID parsing ----------


def extract_video_id(url: str) -> str | None:
    parsed = urlparse(url)
    path = parsed.path
    if "shorts" in path:
        return path.split("/")[-1].split("?")[0] or None
    if parsed.netloc.endswith("youtu.be"):
        return path.lstrip("/").split("?")[0] or None
    qs = parse_qs(parsed.query)
    if "v" in qs:
        return qs["v"][0]
    if len(url) == 11 and "/" not in url and "?" not in url:
        return url
    return None


# ---------- VTT parsing ----------


def vtt_to_text(vtt: str) -> str:
    out: list[str] = []
    for line in vtt.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if "-->" in s:
            continue
        if re.fullmatch(r"\d+", s):
            continue
        s = re.sub(r"<[^>]+>", "", s)
        if s and (not out or out[-1] != s):
            out.append(s)
    return "\n".join(out)


# ---------- metadata ----------


def fetch_metadata(url: str, browser: str | None, cookies: str | None) -> dict:
    opts = {"skip_download": True, "quiet": True, "no_warnings": True}
    if browser:
        opts["cookiesfrombrowser"] = (browser,)
    if cookies:
        opts["cookiefile"] = cookies
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "channel": info.get("channel") or info.get("uploader"),
                "channel_id": info.get("channel_id"),
                "url": info.get("webpage_url") or url,
                "video_id": info.get("id"),
            }
    except Exception as e:
        return {
            "title": None,
            "channel": None,
            "channel_id": None,
            "url": url,
            "video_id": extract_video_id(url),
            "metadata_error": str(e),
        }


# ---------- Strategy 1: YouTube Data API v3 (OAuth) ----------


def get_oauth_credentials(env: dict, interactive: bool):
    """Load existing token or run OAuth flow if interactive."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        return None

    creds = None
    if TOKEN_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), OAUTH_SCOPES)
        except Exception:
            creds = None

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            TOKEN_PATH.write_text(creds.to_json())
            return creds
        except Exception:
            creds = None

    if not interactive:
        return None

    client_id = env.get("YOUTUBE_CLIENT_ID")
    client_secret = env.get("YOUTUBE_CLIENT_SECRET")
    if not client_id or not client_secret:
        print(
            "[ERROR] YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET not set in .env. "
            "See README for Google Cloud setup.",
            file=sys.stderr,
        )
        return None

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [f"http://localhost:{OAUTH_REDIRECT_PORT}/"],
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, OAUTH_SCOPES)
    creds = flow.run_local_server(port=OAUTH_REDIRECT_PORT, open_browser=True)
    TOKEN_PATH.write_text(creds.to_json())
    return creds


def try_youtube_data_api(video_id: str, langs: list[str], creds) -> dict:
    if creds is None:
        return {"transcript": None, "error": "No YouTube OAuth credentials"}
    try:
        from googleapiclient.discovery import build
    except ImportError:
        return {"transcript": None, "error": "google-api-python-client not installed"}

    youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)

    try:
        list_resp = youtube.captions().list(part="snippet", videoId=video_id).execute()
    except Exception as e:
        return {"transcript": None, "error": f"captions.list failed: {e}"}

    items = list_resp.get("items", [])
    if not items:
        return {"transcript": None, "error": "No caption tracks listed"}

    target = None
    for lang in langs:
        for item in items:
            if item["snippet"].get("language") == lang:
                target = item
                break
        if target:
            break
    if target is None:
        target = items[0]

    try:
        download_resp = youtube.captions().download(id=target["id"], tfmt="vtt").execute()
    except Exception as e:
        return {
            "transcript": None,
            "error": (
                f"captions.download failed: {e}. "
                "This typically requires OAuth as the video owner — "
                "works for your own videos, not third-party content."
            ),
        }

    raw = download_resp.decode("utf-8") if isinstance(download_resp, bytes) else download_resp
    return {
        "transcript": vtt_to_text(raw),
        "lang_used": target["snippet"].get("language"),
        "is_generated": target["snippet"].get("trackKind") == "ASR",
        "via": "youtube-data-api-v3",
    }


# ---------- Strategy 2: youtube-transcript-api ----------


def try_transcript_api(video_id: str, langs: list[str]) -> dict:
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    except (TranscriptsDisabled, VideoUnavailable) as e:
        return {"transcript": None, "error": f"{type(e).__name__}: {e}"}
    except Exception as e:
        return {"transcript": None, "error": f"list_transcripts failed: {e}"}

    target = None
    for lang in langs:
        try:
            target = transcripts.find_transcript([lang])
            break
        except NoTranscriptFound:
            continue
    if target is None:
        for t in transcripts:
            target = t
            break
    if target is None:
        return {"transcript": None, "error": "No transcripts available"}

    try:
        data = target.fetch()
    except Exception as e:
        return {"transcript": None, "error": f"fetch failed: {e}"}

    text = "\n".join(item["text"].strip() for item in data if item.get("text", "").strip())
    return {
        "transcript": text,
        "lang_used": target.language_code,
        "is_generated": target.is_generated,
        "via": "youtube-transcript-api",
    }


# ---------- Strategy 3: yt-dlp with cookies ----------


def try_yt_dlp_subs(
    url: str, langs: list[str], browser: str | None, cookies: str | None
) -> dict:
    with tempfile.TemporaryDirectory() as tmpdir:
        outtmpl = str(Path(tmpdir) / "%(id)s.%(ext)s")
        opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [f"{lang}*" for lang in langs],
            "subtitlesformat": "vtt",
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
        }
        if browser:
            opts["cookiesfrombrowser"] = (browser,)
        if cookies:
            opts["cookiefile"] = cookies
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.extract_info(url, download=True)
        except Exception as e:
            return {"transcript": None, "error": f"yt-dlp failed: {e}"}

        sub_files = sorted(Path(tmpdir).glob("*.vtt"))
        if not sub_files:
            return {"transcript": None, "error": "yt-dlp returned no subtitle files"}

        preferred = None
        for lang in langs:
            for f in sub_files:
                if f.stem.endswith(f".{lang}"):
                    preferred = f
                    break
            if preferred:
                break
            for f in sub_files:
                stem_lang = f.stem.split(".")[-1]
                if stem_lang.startswith(lang):
                    preferred = f
                    break
            if preferred:
                break
        if preferred is None:
            preferred = sub_files[0]

        return {
            "transcript": vtt_to_text(preferred.read_text(encoding="utf-8")),
            "lang_used": preferred.stem.split(".")[-1],
            "is_generated": None,
            "via": "yt-dlp",
        }


# ---------- Strategy 4: Whisper local ASR ----------


def try_whisper_asr(url: str, langs: list[str], model_name: str) -> dict:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return {"transcript": None, "error": "faster-whisper not available"}

    with tempfile.TemporaryDirectory() as tmpdir:
        outtmpl = str(Path(tmpdir) / "%(id)s.%(ext)s")
        opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
        }
        try:
            print("[whisper] Downloading audio...", file=sys.stderr)
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.extract_info(url, download=True)
        except Exception as e:
            return {"transcript": None, "error": f"audio download failed: {e}"}

        audio_files = sorted(Path(tmpdir).iterdir())
        if not audio_files:
            return {"transcript": None, "error": "no audio file produced"}
        audio_path = audio_files[0]

        try:
            print(
                f"[whisper] Loading model '{model_name}' (first run downloads ~150MB-1.5GB)...",
                file=sys.stderr,
            )
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
        except Exception as e:
            return {"transcript": None, "error": f"whisper model load failed: {e}"}

        try:
            print(
                f"[whisper] Transcribing {audio_path.name} (lang=auto-detect)...",
                file=sys.stderr,
            )
            # Always auto-detect — language hint can mistranscribe mixed/wrong-lang content
            segments, info = model.transcribe(
                str(audio_path),
                beam_size=5,
                vad_filter=True,
            )
            parts: list[str] = []
            for segment in segments:
                t = segment.text.strip()
                if t and (not parts or parts[-1] != t):
                    parts.append(t)
        except Exception as e:
            return {"transcript": None, "error": f"whisper transcription failed: {e}"}

        return {
            "transcript": "\n".join(parts),
            "lang_used": getattr(info, "language", "auto"),
            "is_generated": True,
            "via": f"whisper-{model_name}",
        }


# ---------- main ----------


def cmd_auth(env: dict) -> int:
    """Run OAuth flow once, persist token to .youtube-token.json."""
    creds = get_oauth_credentials(env, interactive=True)
    if creds is None:
        return 1
    print(f"[OK] Token saved to {TOKEN_PATH}")
    return 0


def cmd_fetch(args, env: dict) -> int:
    langs = [lang.strip() for lang in args.lang.split(",") if lang.strip()]

    meta = fetch_metadata(args.url, args.browser, args.cookies)
    video_id = meta.get("video_id")

    print(f"# {meta.get('title') or '(title unavailable)'}")
    print(f"Channel: {meta.get('channel') or '(unknown)'}")
    print(f"URL: {meta.get('url')}")

    if not video_id:
        print(file=sys.stderr)
        print(f"[ERROR] Could not determine video ID for {args.url}", file=sys.stderr)
        if meta.get("metadata_error"):
            print(f"[ERROR] {meta['metadata_error']}", file=sys.stderr)
        return 1

    # Strategy 1: YouTube Data API v3 (silent if no creds)
    creds = get_oauth_credentials(env, interactive=False)
    result = try_youtube_data_api(video_id, langs, creds) if creds else {"transcript": None}

    # Strategy 2: youtube-transcript-api
    if not result.get("transcript"):
        result = try_transcript_api(video_id, langs)

    # Strategy 3: yt-dlp with cookies
    if not result.get("transcript"):
        result = try_yt_dlp_subs(args.url, langs, args.browser, args.cookies)

    # Strategy 4: Whisper local ASR (universal fallback)
    if not result.get("transcript") and not args.no_whisper:
        print(
            "[INFO] All caption strategies failed. Falling back to Whisper ASR (1-5 min)...",
            file=sys.stderr,
        )
        result = try_whisper_asr(args.url, langs, args.whisper_model)

    if result.get("lang_used"):
        gen = " (auto-generated)" if result.get("is_generated") else ""
        print(f"Language: {result['lang_used']}{gen}")
        print(f"Source: {result.get('via', 'unknown')}")
    print()

    if result.get("transcript"):
        print(result["transcript"])
        return 0

    print(f"[ERROR] {result.get('error')}", file=sys.stderr)
    if args.no_whisper:
        print(
            "[HINT] All caption strategies failed and --no-whisper was set. "
            "Drop --no-whisper to enable Whisper ASR fallback (works for any video).",
            file=sys.stderr,
        )
    else:
        print(
            "[HINT] All strategies failed including Whisper. "
            "Check your network and that the URL is a valid YouTube video.",
            file=sys.stderr,
        )
    return 1


def main() -> int:
    env = load_env_file(ENV_PATH)

    parser = argparse.ArgumentParser(
        description="Fetch a YouTube transcript as plain text."
    )
    parser.add_argument(
        "url",
        help="YouTube URL, or 'auth' to run OAuth setup",
    )
    parser.add_argument(
        "--lang",
        default="el,en",
        help="Comma-separated lang preference (default: el,en)",
    )
    parser.add_argument(
        "--browser",
        default=None,
        help="Pull cookies from a Linux-side browser (firefox, chrome, ...)",
    )
    parser.add_argument(
        "--cookies",
        default=None,
        help="Path to a cookies.txt file (Netscape format)",
    )
    parser.add_argument(
        "--no-whisper",
        action="store_true",
        help="Disable Whisper ASR fallback (fail fast if caption strategies fail)",
    )
    parser.add_argument(
        "--whisper-model",
        default="small",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size (default: small). Larger = better quality + slower.",
    )
    args = parser.parse_args()

    if args.url == "auth":
        return cmd_auth(env)

    return cmd_fetch(args, env)


if __name__ == "__main__":
    sys.exit(main())
