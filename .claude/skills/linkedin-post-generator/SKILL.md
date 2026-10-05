---
name: linkedin-post-generator
description: Write, review, and brainstorm LinkedIn content for Andreas Stasinakis in his Greek-first voice. Use for any LinkedIn writing task in this project — LinkedIn post ideas, writing a full post, reviewing or improving a draft post, turning notes or a YouTube video into LinkedIn posts, or archiving a published post. Triggers on "LinkedIn post", "post creation", "post review", "ιδέες για post", "γράψε post", "κάνε review στο post".
---

# LinkedIn Post Generator

Entry point for the LinkedIn content domain. The rules live in the domain files, not here — this skill only loads them.

## Before doing anything

Read these two files in full, in this order:

1. `domains/_shared/brand-and-voice.md` — role, positioning, audience, voice, validation rules
2. `domains/linkedin/AGENTS.md` — topic weighting, modes, formatting, post structure, output persistence

`domains/linkedin/AGENTS.md` overrides or extends the shared file where they differ. Follow both as written.

## Modes

Use the four modes defined in `domains/linkedin/AGENTS.md`: Idea Generation, Post Creation, Post Review, Video Repurposing.
If the request does not clearly map to one, ask once which mode to use (the exact prompt is in the domain file).

## Saving output

Save exactly as the "OUTPUT PERSISTENCE" section of `domains/linkedin/AGENTS.md` says — append to
`output/idea-pool.md` and `output/ready-posts.md`, archive to `output/published-posts.md`, reviews in
`output/reviews/`. Use the Write/Edit tools directly; there is no save script.

Do not create files under `output/ideas/` or `output/ready-posts/`.

## Style sources

Read `post/STYLE_GUIDE.md` first, then `post/Ανδρέας.docx` for deeper voice match. The `.docx` wins on conflict.
To read the `.docx`, extract its text (e.g. `uv run --with python-docx python -c "..."` or `pandoc`).

If the task needs the latest `ideas/` or `post/` content from Google Drive, use `skills/google-drive/drive.py`
(`uv run skills/google-drive/drive.py --help`) before reading the local files.
