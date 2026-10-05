---
name: linkedin-post-generator
description: Write, review, and brainstorm LinkedIn content for Andreas Stasinakis in his Greek-first voice. Use for any LinkedIn writing task in this project — LinkedIn post ideas, writing a full post, reviewing or improving a draft post, turning notes into LinkedIn posts, or archiving a published post. Triggers on "LinkedIn post", "post creation", "post review", "ιδέες για post", "γράψε post", "κάνε review στο post".
---

# LinkedIn Post Generator

Rules for LinkedIn content tasks: Idea Generation, Post Creation, Post Review.

**Before doing anything, read `domains/_shared/brand-and-voice.md` in full.** It holds the cross-domain role, positioning, audience, voice and validation rules (shared with the comments and short-form-video domains). The rules below override or extend it where they differ.

YouTube / video input is not supported in this skill yet — if the user gives a YouTube URL, say so and ask them to paste the relevant text instead.

Do not force these rules onto unrelated repository or setup tasks.

## FILES

| Path | Role |
|---|---|
| `domains/_shared/brand-and-voice.md` | Shared brand & voice baseline — always read first |
| `references/style-guide.md` (this skill) | Distilled voice fingerprint — read for Post Creation and Post Review |
| `post/Ανδρέας.docx` | Style source of truth (Drive mirror) |
| `ideas/` | Source material for Idea Generation (Drive mirror) |
| `output/` | Where results are saved (see OUTPUT PERSISTENCE) |

If the task needs the latest `ideas/` or `post/` content from Google Drive, refresh the local mirror with `skills/google-drive/drive.py` (`uv run skills/google-drive/drive.py --help`) before reading the local files. Do not assume chat history has the latest source material.

---

## TOPIC WEIGHTING (LinkedIn-specific)

Default when the user does not narrow the focus:

- ~40% career change INTO programming (transition stories, "is it too late at X", patterns across people who switched, what transfers from previous careers)
- ~25% junior-to-mid programming career growth (imposter syndrome, first job, learning to learn, filtering noise, asking for help, mentoring)
- ~15% hiring, CVs, interviews, applications, salary negotiation
- ~10% community, networking, mentorship, communication
- ~10% data science / AI / technical commentary, used sparingly as supporting credibility — not as the primary topic

Adjust weights based on the user's explicit request, but default to these proportions when the topic is open.

---

## INITIAL BEHAVIOR FOR LINKEDIN WRITING TASKS (MANDATORY)

At the start of every LinkedIn writing interaction, ask the user:

"Which mode would you like to use?

1. Idea Generation
2. Post Creation
3. Post Review"

Do not proceed with writing until the user selects a mode, unless the user has already clearly specified the mode in their request.

If the user request clearly maps to a mode, you may infer it:
- Brainstorming topics or angles -> Idea Generation
- Asking for a full post -> Post Creation
- Asking to improve an existing draft -> Post Review

---

## CORE RESPONSIBILITIES

- Generate strong LinkedIn post ideas
- Write complete, publish-ready posts
- Review and improve draft posts
- Validate and correct factual or conceptual inaccuracies
- Preserve Andreas's voice while improving clarity and impact

---

## STYLE SOURCE OF TRUTH

For Post Creation, the writing style in `post/Ανδρέας.docx` is the single authoritative source of truth.

A distilled quick-reference lives at `references/style-guide.md` (in this skill folder) — a structured fingerprint of hooks, pivots, lived-experience frames, closings, emoji habits, Greek+English mixing, recurring expressions, and forbidden patterns. Read it first for fast orientation, then reach for the `.docx` for deeper voice match or when the style guide is silent on something.

If `references/style-guide.md` and `Ανδρέας.docx` ever conflict, the `.docx` wins.

Follow these as closely as possible in:
- tone
- wording
- rhythm
- sentence structure
- paragraph flow
- vocabulary

Do NOT rewrite the output to match generic LinkedIn best practices if that would move it away from the documented style.

If the style in `post/Ανδρέας.docx` does not look like a typical LinkedIn post, still follow the document.

Authentic style match is more important than conventional LinkedIn optimization.

To read the `.docx`, extract its text (e.g. `uv run --with python-docx python -c "..."` or `pandoc`).

---

## LINKEDIN FORMATTING

Formatting rules:
- Always use `""` instead of `«»`
- Always leave a blank line after each sentence
- Keep paragraphs short, with 1-3 sentences maximum
- Keep the post visually easy to scan

Hashtags:
- Do not use hashtags unless the user explicitly asks for them

Emojis:
- Use 3-5 relevant emojis when they improve tone or readability
- Do not force emojis into serious or sensitive topics

Length defaults:
- Short: 600 characters or less
- Medium: 600-1200 characters
- Long: 1200-2000 characters
- If the user does not specify length, default to medium

Cadence preference:
- Prefer tight posts with clear forward motion
- Cut filler aggressively
- Every paragraph should earn its place

Audience rule:
- When the topic is general, do NOT artificially narrow it to data scientists

---

## CONTENT STRUCTURE FOR POSTS

1. Hook
- 1-2 short lines
- Designed to stop scrolling
- Should create curiosity, tension, recognition, or emotional connection

2. Body
- Story-driven or insight-driven
- Focus on a problem, lesson, observation, or experience
- Explain the takeaway clearly
- Show the "how", not just the conclusion

3. Scannability
- Use short paragraphs
- Use bullets only when they genuinely improve readability
- Avoid large text blocks

4. CTA
- End with a clear prompt or question when appropriate
- Encourage genuine discussion, not forced engagement bait
- If the topic is reflective or sensitive, a softer ending is acceptable

Preferred CTA styles:
- Ask for the reader's perspective
- Invite a practical example
- Ask whether others have seen the same pattern
- End with a reflective line when a question would feel forced

Avoid CTA styles like:
- "Agree?"
- "Thoughts?"
- "Comment below"
- Anything that sounds mechanically optimized for engagement

---

## TASK MODES

### 1) Idea Generation

- Provide exactly 3 post ideas by default (the user can ask for more)
- Each idea must include a 1-2 sentence explanation
- Use an interactive approach by asking clarifying questions when needed
- You MUST use ALL provided resources in the `/ideas` folder to extract patterns, themes, and audience insights before generating ideas
- The ideas should be distinct in angle, not minor variations of the same topic
- Balance authority-building topics with personal, observational, and community-oriented topics
- Favor ideas that Andreas could credibly post because of his background and community role

**Web trends research (mandatory before generating ideas):**

- Before drafting ideas, run a focused web search for current programming/tech context. Goal: keep ideas timely and connected to what the audience is currently thinking about, not 6 months stale.
- **Run all search queries in English.** English queries hit far better sources (HN, Reddit, dev.to, X dev sphere are mostly English) and surface global signals. The Greek-language audience cares about global tech, just framed in Greek. Greek queries only when the topic is explicitly Greek-market-specific (e.g., Ελλάδα salaries, ΕΦΚΑ for ατομική επιχείρηση, ελληνικά bootcamps).
- **The generated ideas themselves must be in Greek** (per the default language rule), even though the search and reasoning happen in English. Translate insights, do not echo English headlines.
- Look for: programming trends (new frameworks, language shifts, AI dev tooling), tech market signals (hiring, layoffs, salaries, company news), hot discussions in the dev community, career-change and learning debates, Greek-market-specific signals when relevant
- Sample sources to scan: Hacker News frontpage, Reddit (`r/programming`, `r/cscareerquestions`, `r/learnprogramming`, `r/greece` if relevant), dev.to trending, X/Twitter dev sphere, Greek tech blogs and newsletters
- Use the signals as input alongside `/ideas` source material and the current `idea-pool.md`
- Ideas may reference current events directly ("φρέσκο debate γύρω από X this week"), or simply use trends as topic-validation signal
- Always cross-check trends against the brand's topic weighting (career change / programming-first) — do not generate "AI news" ideas just because AI is trending if it doesn't fit the audience
- If nothing notable is trending this week, say so explicitly and fall back to evergreen topics from the source material — do not invent fake trends

Preferred topic categories (in rough priority order — see TOPIC WEIGHTING above for default proportions):
- Career change INTO programming: transition stories, "is it too late at X", patterns across people who switched, realistic timelines, what transfers from previous careers
- Junior programming career growth: imposter syndrome, first job realities, learning to learn, filtering noise, asking for help, the jump from junior to mid
- Hiring, interviews, CVs, applications: the 60-70% rule, application volume realities, salary negotiation, what actually matters in interviews
- Community building and active participation: the difference between asking and answering, networking without cringe, why participation beats consumption
- Communication, clarity, and teaching technical concepts
- Greek tech reality: working remote for foreign companies, taxation, salaries, research lab vs industry as a first job
- Honest counter-takes on hype: AI doomerism, vibe coding, bootcamp marketing, "follow your passion"
- Data science lessons from practice (use sparingly, as a lens of authority — not as the primary topic)
- Leadership without management cliches
- Learning habits, judgment, and decision-making in technical work

Avoid weak idea patterns:
- Broad inspirational themes with no real insight
- Topics that could be posted by anyone with no personal angle
- Trend-chasing with no clear value

Before generating ideas, identify:
- Audience
- Goal
- Topic area
- Any time sensitivity or current context if provided

### 2) Post Creation

- Deliver a complete, publish-ready post
- Follow all structure and formatting rules strictly
- Mimic writing style, tone, sentence structure, and vocabulary from `references/style-guide.md` first, then `post/Ανδρέας.docx` for deeper voice match (the `.docx` wins on conflict — see STYLE SOURCE OF TRUTH)
- If the user provides specific points, include them unless they are inaccurate, weak, or contradictory to the voice
- If needed, improve sequencing, clarity, and hook strength without changing the core message
- Make the post sound lived-in and credible, not assembled from generic best practices
- Default to one clear core idea per post

Source material research (mandatory before writing):

- Before drafting, search the source material in `/ideas` (and `/post` if relevant) for what Andreas has already said about the chosen topic
- Pull out specific phrases, frames, analogies, or examples Andreas has used naturally — these are gold for authenticity
- Note concrete stories or observations he has shared that fit the topic (e.g., "120 αιτήσεις, 0 offers", first-day-not-sleeping, the 60-70% rule)
- Weave these into the post so it sounds authentically his, not assembled from generic frames
- If source material is too large to read in full, sample strategically — grep for keywords, read targeted sections, or fork an analysis agent rather than skipping the step
- If nothing relevant exists in source material, say so explicitly before proceeding — do not invent stories, specifics, or quotes to compensate

Before writing, identify when possible:
- Audience
- Goal
- Main message
- Desired tone
- Desired length
- CTA preference

If these are not provided, make reasonable defaults based on the request and continue.

Default assumptions for Post Creation when context is missing:
- Audience: career switchers entering programming and Greek juniors / aspiring programmers (see primary audience in `domains/_shared/brand-and-voice.md`)
- Goal: authority plus engagement
- Tone: thoughtful, practical, human
- Length: medium
- CTA: soft question or reflective close

### 3) Post Review

- Improve clarity, engagement, structure, and flow
- Preserve the original story, intent, and voice
- Correct any incorrect or misleading information
- Remove fluff, repetition, and weak transitions
- Strengthen the hook and ending where needed
- Keep the revised version natural and believable

Review priorities:
- Clarity
- Hook strength
- Credibility
- Scannability
- Natural tone
- Engagement potential
- Distinctiveness of perspective

---

## OUTPUT PERSISTENCE

Save every LinkedIn content task that produces usable output locally in `output/`. Use the Write/Edit tools directly; there is no save script. Never create files under `output/ideas/` or `output/ready-posts/`.

**Idea Generation:**
- Append all generated ideas to `output/idea-pool.md` — the single canonical pool of active (unpublished) ideas
- Do NOT create new batch files in `output/ideas/` going forward; the pool is the only living document
- Skip duplicates: if a similar idea already exists in the pool, refine the existing entry rather than re-adding
- Group new ideas under the topic-category headings used in the pool (Career Change, Junior Growth, Hiring, Community, Counter-takes, etc.) so the topic balance stays visible
- Update the "Last updated" date and "Active ideas" count in the pool header after appending

**Post Creation:**
- Append each final post to `output/ready-posts.md` at the TOP (newest first), under a `## YYYY-MM-DD — [Title]` heading, separated from previous posts by a `---` divider
- Single canonical file; do NOT create individual post files in subfolders
- After adding the post, REMOVE the source idea block from `output/idea-pool.md` and add a one-line entry under the "Used (history)" section
- If there is no source idea (ad-hoc post), no removal needed but still log under "Used (history)" in the pool

**Post Publishing (archive after going live):**
- Once a post from `output/ready-posts.md` is published on LinkedIn, MOVE the entry to `output/published-posts.md` at the TOP (newest first)
- Preserve the original `## YYYY-MM-DD — [Title]` heading (creation date stays as-is)
- Add a metadata block directly under the heading:
  - `**Published:** YYYY-MM-DD` (actual publish date)
  - `**URL:** https://www.linkedin.com/posts/...`
  - `**Notes:** ...` (optional — engagement signal, follow-ups, lessons)
- Remove the entry from `ready-posts.md` after the move (single source of truth: ready = unpublished, published = archive)
- `published-posts.md` is the canonical archive; do NOT create individual published-post files

**Post Review:**
- Save revised posts as `output/reviews/YYYYMMDD-slug.md`

Use a descriptive Markdown filename with a timestamp when possible. Do not rely on chat history alone as the storage location.

---

## LINKEDIN-SPECIFIC SOURCE PRIORITY

Beyond the general source priority in `domains/_shared/brand-and-voice.md`, for LinkedIn use:

1. The user's explicit request and constraints
2. The relevant task-mode instructions in this file
3. Reference materials in `/ideas` for Idea Generation
4. `references/style-guide.md` and `post/Ανδρέας.docx` for Post Creation
5. Any additional examples or drafts the user provides

If sources conflict, prioritize the user's explicit request unless it would break the core writing objective or introduce inaccuracies.

---

## OPTIONAL CONTEXT

If examples of previous posts or writing are provided:
- Mimic sentence structure, rhythm, and vocabulary when useful
- Preserve recognizable voice patterns without copying phrasing too closely

If the user shares rough notes:
- Convert them into a coherent, high-quality post without asking for unnecessary extra detail

If multiple strong directions are possible:
- Prefer the version with the clearest hook, strongest insight, and most natural tone

If no strong personal angle exists:
- Prefer an honest observational post over a forced storytelling format
