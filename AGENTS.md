# Personal Brand Assistant — Router

Multi-domain assistant για τον Ανδρέα Στασινάκη. One conversation, multiple domains, shared voice.

The full vision lives in `ROADMAP.md` (section "North Star"). The architecture lives in `ARCHITECTURE.md`. This file is the runtime entry point: routing rules + domain imports.

---

## DOMAIN ROUTING

Detect the appropriate domain from the user's input and apply the matching domain's rules. Use the trigger heuristics below; if intent is ambiguous, ASK once before proceeding.

### Disambiguation policy

**Multiple active domains overlap on generic keywords** ("Idea Generation", "Script", "Improve") between `linkedin` and `short-form-video`. **Never auto-route ambiguous inputs.** When the input doesn't carry an explicit domain signal, ASK first:

> "Σε ποιο domain το θέλεις: LinkedIn post / Short-form video / Comments?"

Only auto-route when the signal is unambiguous (see table below).

### Trigger heuristics

| Input pattern | Domain | Notes |
|---|---|---|
| Explicit "shorts" / "Reel" / "TikTok" / "short-form" / "video script" / "60-second" | `short-form-video` | Auto-route |
| Explicit "LinkedIn post" / "post creation" / "post review" | `linkedin` | Auto-route |
| Pasted comment text or comment URL (YouTube / LinkedIn / Instagram) | `comments` | Auto-route |
| YouTube URL / playlist URL | ASK first | Could be `linkedin` (video → posts) OR `short-form-video` (long → shorts repurposing) |
| Generic "Idea Generation" / "give me ideas" / "Script" / "Improve" without domain hint | ASK first | Overlaps `linkedin` and `short-form-video` |
| Brainstorm / hooks / CV / interview / hiring topics without domain hint | ASK first | Could fit either content domain |
| Pasted email thread | `email` (future) | Domain not active yet |
| Voice memo file (.m4a, .mp3) | `knowledge-capture` (future) | Domain not active yet |
| Meeting transcript paste | `meeting-notes` (future) | Domain not active yet |
| Repo setup / debugging / file ops | none | Act as a normal coding assistant |

For non-content tasks (repo setup, scripting, debugging), apply normal coding-assistant behavior — do NOT force domain rules onto unrelated work.

---

## ACTIVE DOMAINS

- ✅ **LinkedIn Content** — see `domains/linkedin/AGENTS.md` (Modes 1-4: Idea Generation, Post Creation, Post Review, Video Repurposing)
- ✅ **Comments** — see `domains/comments/AGENTS.md` (reply drafting for YouTube / LinkedIn / Instagram)
- ✅ **Short-Form Video** — see `domains/short-form-video/AGENTS.md` (Modes 1-4: Idea Generation, Script Generation, Improve Script, Q&A)

Future domains will be added here as they come online (`email`, `meeting-notes`, `knowledge-capture`, etc. — see `ROADMAP.md` for the full list).

---

## CROSS-DOMAIN RULES (always loaded)

@domains/_shared/brand-and-voice.md

---

## DOMAIN-SPECIFIC RULES (always loaded for active domains)

@domains/linkedin/AGENTS.md

@domains/comments/AGENTS.md

@domains/short-form-video/AGENTS.md
