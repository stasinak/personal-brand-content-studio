# YouTube Transcript Fetcher

Fetches a YouTube video's transcript as plain text. Used by **Mode 4: Video Repurposing** in `AGENTS.md`.

## Strategies

The script tries four strategies in order, taking the first that returns a transcript:

1. **YouTube Data API v3 (OAuth)** — official, free, reliable. **Works only for videos YOU own** (your channel). Best path for Shift Happens content.
2. **`youtube-transcript-api`** — anonymous, hits YouTube's `timedtext` endpoint. Free but increasingly rate-limited.
3. **`yt-dlp` with cookies** — fallback for non-own videos when timedtext is blocked. Requires a logged-in YouTube cookies file.
4. **Whisper local ASR** — universal fallback. Downloads audio + transcribes locally. **Works for ANY public video, no auth, no cookies.** Trade-off: 1-5 min processing on CPU. First run downloads model (~150MB-1.5GB depending on size). Disable with `--no-whisper`.

## Quickstart

```bash
# Standard usage (tries all strategies automatically)
uv run skills/youtube-transcript-fetcher/fetch.py "https://www.youtube.com/watch?v=..."

# English transcript
uv run skills/youtube-transcript-fetcher/fetch.py "<url>" --lang en

# Force-feed cookies for non-own videos
uv run skills/youtube-transcript-fetcher/fetch.py "<url>" --cookies .youtube-cookies.txt
```

## Setup A: YouTube Data API v3 (recommended for own-channel videos)

One-time setup, then everything works automatically.

### 1. Google Cloud Console

1. Go to https://console.cloud.google.com/
2. Create a project (or pick an existing one)
3. Enable **YouTube Data API v3**: APIs & Services → Library → search "YouTube Data API v3" → Enable
4. Configure OAuth consent screen (if not already): External user type, fill the basics, add scope `https://www.googleapis.com/auth/youtube.force-ssl`
5. Create OAuth credentials: APIs & Services → Credentials → Create Credentials → OAuth client ID → **Desktop app**
6. Copy the **Client ID** and **Client Secret**

### 2. Add to `.env`

```
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
```

### 3. Run OAuth flow once

```bash
uv run skills/youtube-transcript-fetcher/fetch.py auth
```

Browser opens → log in with the Google account that owns your YouTube channel → click Allow → token saved to `.youtube-token.json` (gitignored).

After this, fetches against your own videos use this strategy automatically.

## Setup B: Cookies file (for third-party videos)

For videos NOT on your channel, the official API can't download captions (permission denied). Fall back to cookies.

1. Install **"Get cookies.txt LOCALLY"** browser extension (Chrome/Firefox/Edge):
   https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
2. Visit `youtube.com` while logged in
3. Click the extension → "Export As" → "youtube.com"
4. Save as `.youtube-cookies.txt` in the project root (already gitignored)
5. Pass it explicitly:

```bash
uv run skills/youtube-transcript-fetcher/fetch.py "<url>" --cookies .youtube-cookies.txt
```

Cookies typically last weeks-to-months before YouTube invalidates them. Re-export when fetches start failing.

## Setup C: Whisper ASR (no setup needed — works everywhere)

This is the universal fallback. Triggers automatically when strategies 1-3 fail.

- **Default model:** `small` (~500MB, good quality, ~1-2 min for a short)
- **Faster:** `--whisper-model tiny` (~75MB, weaker quality, ~30s)
- **Better:** `--whisper-model medium` or `large-v3` (~1.5-3GB, slow on CPU)

Force-skip Whisper:

```bash
uv run skills/youtube-transcript-fetcher/fetch.py "<url>" --no-whisper
```

First run downloads the model from Hugging Face (one-time). Cached locally in `~/.cache/huggingface/`.

### Quality vs speed (CPU benchmarks, rough)

| Model | Size | 1-min audio | 10-min audio | Greek quality |
|-------|------|-------------|---------------|---------------|
| tiny | 75MB | ~15s | ~2 min | weak |
| base | 150MB | ~25s | ~3 min | OK |
| **small (default)** | **500MB** | **~45s** | **~5 min** | **good** |
| medium | 1.5GB | ~2 min | ~15 min | very good |
| large-v3 | 3GB | ~4 min | ~30 min | best |

## Output format

```
# <video title>
Channel: <channel name>
URL: <canonical URL>
Language: <language code> [(auto-generated)]
Source: youtube-data-api-v3 | youtube-transcript-api | yt-dlp | whisper-{tiny|base|small|medium|large-v3}

<transcript text>
```

## Auth subcommand

```bash
uv run skills/youtube-transcript-fetcher/fetch.py auth
```

Runs the OAuth flow, persists token to `.youtube-token.json`. Run this once after adding env vars; the token auto-refreshes thereafter.

## Requirements

- [`uv`](https://docs.astral.sh/uv/)
- All Python deps handled automatically via PEP 723 inline metadata in `fetch.py`

## Exit codes

- `0`: success
- `1`: no transcript could be retrieved (try the other strategies / setup)
