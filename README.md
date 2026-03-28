# Personal Brand Content Studio

Repository setup for Andreas's personal brand content workflow with Codex.

The current workflow is repository-driven, with LinkedIn content as the first implemented writing flow and optional publishing and sync MVPs.

Codex should read the repo instructions in `AGENTS.md`, use the local source material in `ideas/` and `post/`, and save generated outputs in `output/`.

## Current Content Focus

The active writing workflow currently supports LinkedIn content in three modes:

- idea generation
- post creation
- post review

## Source Material

### Idea Generation

Use all files in `ideas/` as source material for patterns, themes, audience signals, and topic directions.

### Post Creation

Use `post/Ανδρέας.docx` as the single source of truth for writing style.

That means:

- follow its tone, wording, rhythm, sentence structure, paragraph flow, and vocabulary
- do not rewrite toward generic LinkedIn best practices if that would move away from the document
- authenticity to the document matters more than conventional LinkedIn optimization

### Post Review

Preserve the original story and voice while improving clarity and structure.

## Instructions

Persistent behavior lives in `AGENTS.md`.

That file currently defines rules such as:

- ask for the mode at the start of LinkedIn writing tasks unless the mode is already clear
- use `ideas/` for ideation
- use `post/Ανδρέας.docx` as the style source of truth for post creation
- save usable outputs locally in `output/`

## Output

All generated outputs should be stored in `output/` as Markdown files, split by mode:

- `output/ideas/`
- `output/ready-posts/`
- `output/reviews/`

For LinkedIn tasks handled through the project skill, prefer the bundled save helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\linkedin-post-generator\scripts\save-output.ps1 -Mode post -Content $postText -Slug "networking-is-long-term"
```

Naming convention:

- use a descriptive topic slug
- keep the filename readable without opening the file

Example paths:

```text
output/ideas/20260328-junior-candidate-signals.md
output/ready-posts/20260328-networking-is-long-term.md
output/reviews/20260328-community-building-consistency.md
```

## LinkedIn Publishing MVP

This repository includes a minimal PowerShell-based LinkedIn publisher for text-only posts.

What the MVP does:

- authenticates with LinkedIn via OAuth 2.0
- stores a local access token in `.linkedin-token.json`
- publishes a text-only post to a member profile using the Posts API

What the MVP does not do yet:

- images or videos
- scheduling
- company page posting
- token refresh
- approval workflows inside the tool

### Prerequisites

1. Create a LinkedIn app in the LinkedIn Developer Portal.
2. Enable these products for the app:
   - `Sign in with LinkedIn using OpenID Connect`
   - `Share on LinkedIn`
3. Configure this redirect URI in the LinkedIn app settings:

```text
http://localhost:8765/callback/
```

4. Copy `.env.example` to `.env` and fill in your app credentials.

### Commands

Authenticate:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\linkedin-mvp.ps1 auth
```

Show the authenticated member:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\linkedin-mvp.ps1 whoami
```

Publish a generated post from a file:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\linkedin-mvp.ps1 publish -FilePath .\output\your-post.md
```

Publish direct text:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\linkedin-mvp.ps1 publish -Text "My LinkedIn post text"
```

Preview the payload without publishing:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\linkedin-mvp.ps1 publish -FilePath .\output\your-post.md -DryRun
```

### Notes

- The post is published to the authenticated member profile, not a company page.
- The script expects the final file content to already be clean post text.
- If the token expires, run `auth` again.
- The current default API version is `202601`.

## Google Drive API MVP

This repository also includes a minimal Google Drive integration for using Drive as the source of truth for `ideas`, `post`, and `output`.

What the MVP does:

- authenticates with Google OAuth for a desktop app
- lists files in configured Drive folders
- pulls files from Drive into the local repo
- pushes generated Markdown outputs back to Drive

What the MVP does not do yet:

- recursive folder sync
- conflict resolution
- file deletion sync
- Google Docs/Sheets/Slides support beyond the basic export mappings in the script

### Google Cloud setup

1. Create a Google Cloud project.
2. Enable the Google Drive API for that project.
3. Create OAuth credentials for a `Desktop app`.
4. Copy the OAuth `Client ID` and `Client Secret`.
5. Create three folders in Google Drive:
   - one for `ideas`
   - one for `post`
   - one for `output`
6. Copy each folder ID from the Drive URL.

Example:

```text
https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz
```

The folder ID is the final path segment:

```text
1AbCdEfGhIjKlMnOpQrStUvWxYz
```

### Configuration

Add these values to `.env`:

- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REDIRECT_URI`
- `GOOGLE_SCOPES`
- `GOOGLE_DRIVE_IDEAS_FOLDER_ID`
- `GOOGLE_DRIVE_POST_FOLDER_ID`
- `GOOGLE_DRIVE_OUTPUT_FOLDER_ID`

Defaults:

- `GOOGLE_REDIRECT_URI=http://127.0.0.1:8766/`
- `GOOGLE_SCOPES=https://www.googleapis.com/auth/drive`

### Commands

Authenticate with Google Drive:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\google-drive-mvp.ps1 auth
```

List the configured Drive folders:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\google-drive-mvp.ps1 list
```

Pull files from Drive into the repo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\google-drive-mvp.ps1 pull
```

Push one output file back to Drive:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\google-drive-mvp.ps1 push-output -FilePath .\output\your-post.md
```

Push all Markdown files from `output/`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\google-drive-mvp.ps1 push-output
```

### Notes

- This MVP uses a broad Drive scope for simplicity: `https://www.googleapis.com/auth/drive`.
- That is acceptable for local personal use, but you may want a narrower scope in a later production-grade version.
- The `pull` command currently syncs only the configured top-level files in each folder, not nested subfolders.
- Google Docs in the `post` folder are exported as `.docx`.
- Google Docs elsewhere are exported as `.md`.

## Repository Structure

```text
personal-brand-content-studio/
  AGENTS.md
  README.md
  scripts/
    google-drive-mvp.ps1
    linkedin-mvp.ps1
  skills/
    linkedin-post-generator/
  ideas/
  post/
    Ανδρέας.docx
  output/
```
