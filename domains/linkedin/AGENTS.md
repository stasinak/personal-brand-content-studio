# LinkedIn Content Domain

Rules for LinkedIn content tasks: Idea Generation, Post Creation, Post Review, Video Repurposing.

This domain inherits cross-domain brand & voice rules from `domains/_shared/brand-and-voice.md`. Format-specific rules below override or extend the shared baseline.

---

## WHEN THIS DOMAIN APPLIES

Apply these instructions for LinkedIn content tasks, including:
- Idea Generation
- Post Creation
- Post Review
- Video Repurposing
- Repurposing notes into posts
- Rewriting posts for clarity, tone, or engagement
- Saving generated ideas and posts locally

Do not force these instructions onto unrelated repository or setup tasks. For non-writing tasks, act normally.

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
3. Post Review
4. Video Repurposing"

Do not proceed with writing until the user selects a mode, unless the user has already clearly specified the mode in their request.

If the user request clearly maps to a mode, you may infer it:
- Brainstorming topics or angles -> Idea Generation
- Asking for a full post -> Post Creation
- Asking to improve an existing draft -> Post Review
- Providing a YouTube URL (or playlist URL) with extraction intent -> Video Repurposing

---

## CORE RESPONSIBILITIES

- Generate strong LinkedIn post ideas
- Write complete, publish-ready posts
- Review and improve draft posts
- Validate and correct factual or conceptual inaccuracies
- Preserve Andreas's voice while improving clarity and impact

---

## OUTPUT PERSISTENCE

Save every LinkedIn content task that produces usable output locally in `/output`.

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

**Post Review:**
- Save revised posts as `output/reviews/YYYYMMDD-slug.md`

Use a descriptive Markdown filename with a timestamp when possible. Do not rely on chat history alone as the storage location.

---

## GOOGLE DRIVE SOURCE OF TRUTH

If Google Drive integration is configured for this repository, treat Google Drive as the upstream source of truth for:

- `/ideas`
- `/post`
- `/output` as the remote destination for generated files

Operationally, work through the local repository mirror:

- pull the latest Google Drive content into the local repo first
- read the local mirrored files
- generate output
- save the result locally in `/output`

Do not assume chat history contains the latest source material if Google Drive is being used for this workflow.

For Idea Generation specifically:

- use the Drive-backed contents of `/ideas`
- if needed and available, refresh the local mirror from Drive before generating ideas

For Post Creation specifically:

- use the Drive-backed contents of `/post`
- `post/Ανδρέας.docx` remains the style source of truth unless the user explicitly replaces it

The local `/output` folder remains the immediate working output location even when Drive is the upstream source.

---

## STYLE SOURCE OF TRUTH

For Post Creation, the writing style in `post/Ανδρέας.docx` is the single authoritative source of truth.

A distilled quick-reference lives at `post/STYLE_GUIDE.md` — a structured fingerprint of hooks, pivots, lived-experience frames, closings, emoji habits, Greek+English mixing, recurring expressions, and forbidden patterns. Read it first for fast orientation, then reach for the `.docx` for deeper voice match or when STYLE_GUIDE.md is silent on something.

If `STYLE_GUIDE.md` and `Ανδρέας.docx` ever conflict, the `.docx` wins.

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
- Use ONLY the `Andreas.docx` document in the `/post` folder to mimic writing style, tone, sentence structure, and vocabulary
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
- Audience: professionals in tech, data, and adjacent career-focused audiences
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

### 4) Video Repurposing

Triggered when the user provides a YouTube URL (single video or playlist) with intent to extract LinkedIn content from it.

Output destinations:
- **Ideas:** generated LinkedIn angles append to `output/idea-pool.md` per the standard flow
- **Post:** a complete post appends to `output/ready-posts.md` per the standard flow
- If the user does not specify "ιδέες ή post", ask once before proceeding

**Source material acquisition (mandatory before generating):**

Lookup order:
1. Check `output/_transcripts/` for an existing file matching the video ID — if a transcript was previously fetched, reuse it (avoid re-fetch).
2. Check `/ideas` for consolidated transcript files (Andreas's own Shift Happens content may be there).
3. Otherwise, fetch via the skill and save to `output/_transcripts/`:
   ```bash
   uv run skills/youtube-transcript-fetcher/fetch.py <url> > output/_transcripts/<YYYYMMDD>-<video_id>.md 2>/tmp/fetch.stderr
   ```
   - Set Bash timeout to ~600000 ms (10 min) — Whisper fallback can take 1-5 min on CPU
   - Redirect saves the CLEAN transcript file (stdout only); progress/errors go to stderr
   - The skill tries 4 strategies internally (YouTube Data API → transcript-api → yt-dlp+cookies → Whisper local ASR). Whisper is the universal fallback that works on any public video.

Filename convention: `output/_transcripts/<YYYYMMDD>-<video_id>.md`. Extract `<video_id>` from the URL (the 11-char ID after `watch?v=`, `shorts/`, or `youtu.be/`).

After a successful fetch, the transcript file persists for future reuse and provenance.

If automated fetch still fails (rare — typically only on network or unavailable videos), ASK the user to paste the transcript directly. Do not invent content from the title alone.

Whisper model selection:
- Default `--whisper-model small` is appropriate (good quality + reasonable speed)
- `--whisper-model tiny` for fast/dirty drafts
- `--whisper-model medium` or `large-v3` for highest quality on long-form content

**Mining the transcript:**

- Read for: key frames, specific quotable moments, practical takeaways, personal stories, contrarian claims, failed-then-recovered narratives
- Pull verbatim phrasing where useful — Andreas's own voice patterns may already be in the transcript (especially for Shift Happens content)
- Note timestamps when a post will reference a specific moment

**Output behavior:**

- **Ideas mode:** Generate 3 distinct LinkedIn-post angles derived from the video. Each angle must be its own crystallized takeaway, not a summary. Append to `idea-pool.md` per the standard flow, with a `*Source: YouTube — [video title]*` line appended to the *Γιατί δουλεύει* note for traceability.
- **Post mode:** Build a complete post from the strongest single insight in the video. Apply all post creation rules (style guide, source material research, append to `ready-posts.md`). Add a `**Source video:** [title] — [URL]` line directly under the heading for provenance.

**Brand discipline:**

- Keep topic-weighting and brand-voice rules intact — even if the video covers something off-brand, only generate output that fits the brand's audience (career switchers + Greek juniors)
- If the video is fundamentally off-brand for LinkedIn, say so explicitly rather than forcing a fit
- Search and analyze the transcript in whatever language it is; the output ideas/post still follow the default-Greek rule

---

## LINKEDIN-SPECIFIC SOURCE PRIORITY

Beyond the general source priority in `domains/_shared/brand-and-voice.md`, for LinkedIn use:

1. The user's explicit request and constraints
2. The relevant task-mode instructions in this file
3. Reference materials in `/ideas` for Idea Generation
4. `Andreas.docx` in `/post` for Post Creation
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
