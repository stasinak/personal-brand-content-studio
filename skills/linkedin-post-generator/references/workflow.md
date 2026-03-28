# Workflow

## Source Priority

Use context in this order:

1. The user's explicit request
2. The active mode instructions in this skill
3. Files under `ideas/` for Idea Generation
4. `post/Ανδρέας.docx` for Post Creation
5. Extra drafts or notes provided by the user

If sources conflict, prefer the user's request unless that would reduce quality or introduce inaccuracies.

## Repository Workflow

Work from the local project mirror, not from chat history alone.

If Google Drive integration is configured:

- refresh the local mirror first
- read local files from `ideas/` or `post/`
- generate the output
- save the result locally in the correct `output/` subfolder

Treat these folders as the operational workspace:

- `ideas/` for research material and idea sources
- `post/` for style sources and post inputs
- `output/ideas/` for idea generation deliverables
- `output/ready-posts/` for final post deliverables
- `output/reviews/` for revised draft deliverables

## Mode Rules

### Idea Generation

- Identify audience, goal, topic area, and any time sensitivity before generating ideas.
- Use all relevant material in `ideas/`.
- Produce exactly 10 ideas by default.
- Make each idea distinct, credible, and useful for Andreas.
- Include a 1-2 sentence explanation for each idea.

### Post Creation

- Identify audience, goal, main message, tone, desired length, and CTA preference when possible.
- If context is missing, default to:
  - audience: professionals in tech, data, and adjacent career-focused audiences
  - goal: authority plus engagement
  - tone: thoughtful, practical, human
  - length: medium
  - CTA: soft question or reflective close
- Use `post/Ανδρέας.docx` as the style source of truth.
- Keep one clear core idea per post.
- Improve weak sequencing or hooks without changing the core message.

### Post Review

- Preserve the draft's intent and believable voice.
- Improve clarity, engagement, structure, flow, and scannability.
- Remove fluff and repetition.
- Fix factual or conceptual issues directly.

## Validation Rules

- Do not invent personal details.
- Keep uncertain or current claims general unless the user provides a source.
- Favor honest observational framing over forced storytelling.

## Persistence

Save every usable output to the correct `output/` subfolder as a descriptive Markdown file with a timestamp.

Folder mapping:

- `ideas` mode -> `output/ideas/`
- `post` mode -> `output/ready-posts/`
- `review` mode -> `output/reviews/`

Naming convention:

- use a descriptive topic slug
- avoid generic names like `draft`, `post`, or `test`
- prefer filenames that are understandable at a glance

Examples:

- `output/ideas/20260328-networking-not-just-job-search.md`
- `output/ready-posts/20260328-junior-candidates-showing-their-work.md`
- `output/reviews/20260328-community-building-consistency.md`

Prefer the bundled helper:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\linkedin-post-generator\scripts\save-output.ps1 -Mode post -Content $postText -Slug "networking-not-just-job-search"
```

Or save from an existing file:

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\linkedin-post-generator\scripts\save-output.ps1 -Mode review -InputFile .\temp\review.md -Slug "community-building-consistency"
```

Suggested filename patterns:

- `output/linkedin-ideas-YYYY-MM-DD-HHMM.md`
- `output/linkedin-post-YYYY-MM-DD-HHMM.md`
- `output/linkedin-review-YYYY-MM-DD-HHMM.md`
