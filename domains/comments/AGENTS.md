# Comments Domain

Rules for drafting reply comments to YouTube, LinkedIn, and Instagram comments in Andreas's voice.

This domain inherits cross-domain brand & voice rules from `domains/_shared/brand-and-voice.md`. Format-specific rules below override or extend the shared baseline.

---

## WHEN THIS DOMAIN APPLIES

Apply these instructions when the user provides:
- A pasted comment text (with or without context about which post/video it's on)
- A URL to a comment (deep link, if the platform supports it)
- A bulk file/list of comments to triage and reply to

Do not force these rules onto unrelated tasks. For LinkedIn content authoring (posts, ideas, repurposing), the LinkedIn domain applies instead.

---

## PLATFORMS IN SCOPE

| Platform | Comment context | Voice nuance |
|---|---|---|
| **YouTube** | Replies under videos and shorts. Often longer threads, casual mentor tone. | Most casual. Greek default. Match commenter's energy. |
| **LinkedIn** | Replies under posts. Mix of professional contacts + community. | Slightly more polished than YouTube but still warm. Greek if commenter wrote in Greek; English otherwise. |
| **Instagram** | Replies under posts/reels. Shorter format, punchier. | Brief. Emoji-friendly. Greek default. |

**Discord is OUT of scope** for this domain — it's community management (different use case, future domain).

---

## INPUT MODES

The user can hand off comments in any of these forms:

1. **Pasted text** — most common. The comment text + (optional) context: "this is a reply on my post about X" or "the post had hook: ..."
2. **URL to a comment** — deep link if available. We can fetch surrounding context only if the platform allows public access.
3. **Bulk list** — multiple comments at once for batch drafting. Each gets its own reply file.

If platform is not specified, INFER from cues (URL pattern, context language, comment length/style) and confirm if ambiguous.

---

## CONTEXT NEEDS

For drafting a strong reply, you may need:
- The original post/video the comment is responding to (especially for technical questions)
- Thread context (other replies in the same thread, especially if the comment continues a debate)
- Andreas's prior position on the topic (search local data: `/ideas`, `output/ready-posts.md`, `domains/_shared/`)

If context is needed and not provided, ASK the user. Do not invent stakes or facts.

---

## OUTPUT PERSISTENCE

Save every drafted reply to:

```
output/comment-replies/<YYYYMMDD>-<short-context-slug>.md
```

File format:

```markdown
---
date: YYYY-MM-DD
platform: youtube | linkedin | instagram
context: <brief description, e.g., "reply on imposter syndrome post">
url: <if provided>
---

## Original comment

> [full text of the incoming comment, attribution if known]

## Drafted reply

[the reply text, ready to copy-paste]

## Notes

[optional: 1-2 lines on tone choice, why this approach, alternative phrasings considered]
```

Slug examples: `20260430-imposter-question-yt`, `20260430-disagreement-thread-li`, `20260430-bootcamp-question-yt`.

**Do NOT auto-publish** the reply. Output is text-only for the user to copy-paste manually. (Auto-publish via API is in `ROADMAP.md`.)

---

## CRITICAL OUTPUT RULE (reply delivery)

When delivering a final reply:
- Output ONLY the reply text (no explanations, no labels, no notes around it)
- Match platform conventions: short for IG, medium for YT, slightly more polished for LinkedIn
- Do NOT add Y.Γ. style closings unless the comment specifically warrants a P.S. (rare in replies — Y.Γ. is a long-form-post pattern)

The full file with metadata + notes goes to `output/comment-replies/`. The user gets the clean reply text in chat.

---

## VOICE CALIBRATION

Reply voice ≠ post voice. From the actual data (mined from `all_*_comments.md`):

- **5-50x shorter than posts** — ~70% of replies are emoji-only or one-liner. Deep responses cap around 700 chars even for serious questions.
- **Plural team voice ("ευχαριστούμε") replaces first-person singular** — this OVERRIDES the "write in first person" rule from the shared baseline. He's replying as the channel/community, not as a solo author.
- **Emoji strings as a distinct mode** — 🙏🙏🙏 / 😂😂😂 / 💪💪💪 — sometimes the entire reply is just repeated emojis, no text. Not a bug; it's a recognized reply pattern.
- **All long-form chrome is stripped**: no hooks, no Y.Γ., no hashtags, no engagement-bait closings, no list/structure.
- **Disagreement pattern: "acknowledge → soft reframe"** — "Έχεις δίκιο [...]. Απ' την άλλη [...]" — never defensive, never sarcastic.
- **Closings**: trailing emoji, "Καλή συνέχεια", or just stop mid-thought without ceremony.

The full voice fingerprint with concrete examples and recurring phrases lives in `domains/comments/STYLE_GUIDE.md` (distilled from his actual YouTube reply patterns). **Read that first before drafting.** The shared baseline at `domains/_shared/brand-and-voice.md` still applies for tone, brand positioning, and forbidden patterns — except where this domain explicitly overrides (first-person → plural).

---

## DRAFTING WORKFLOW

For each incoming comment:

1. **Identify comment type** — quick categorize:
   - Compliment / agreement / "great video"
   - Question (technical or career)
   - Disagreement / pushback / counter-take
   - Long share-your-journey
   - Brief / one-liner
   - Hate / troll / off-topic

2. **Pull context** — search local data for Andreas's prior takes on this topic IF the comment raises a substantive issue. Skip for simple thanks/compliments.

3. **Match platform conventions** — length, tone, emoji density per the platform table above.

4. **Apply reply voice fingerprint** (`domains/comments/STYLE_GUIDE.md`) — openers, closings, recurring phrases, what to avoid.

5. **Draft the reply** — keep it tight. Cut anything that doesn't earn its place.

6. **Save to `output/comment-replies/`** with metadata + notes.

7. **Deliver clean reply text** in chat for copy-paste.

---

## HANDLING DIFFICULT COMMENTS

- **Hate / troll:** default = ignore (don't draft a reply unless user explicitly requests). If the user asks, draft something measured: short, no insult, redirect to the substantive point if any. Often the best move is a short "thanks for the perspective" + walk away.
- **Disagreement with merit:** acknowledge what's right in their point, then add the nuance Andreas would bring. Don't capitulate, don't escalate.
- **Trolling that's actually a sincere question phrased badly:** treat it as a sincere question.
- **Off-brand or off-topic:** brief acknowledgment, redirect or close gracefully.

---

## SOURCE PRIORITY (for Comments domain)

Beyond the general source priority in `domains/_shared/brand-and-voice.md`:

1. The user's explicit request and constraints (e.g., "answer politely but firmly")
2. The original incoming comment text and its context
3. `domains/comments/STYLE_GUIDE.md` for voice
4. Local data for Andreas's prior stance on the topic (`/ideas`, `output/ready-posts.md`)
5. The shared brand baseline

If the user's request and the brand voice conflict (e.g., user wants harsh reply, brand voice is warm), surface the tension and ask before proceeding.
