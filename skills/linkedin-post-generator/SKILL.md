---
name: linkedin-post-generator
description: Generate, review, and refine LinkedIn content for Andreas Stasinakis inside the personal-brand-content-studio project. Use when Codex needs to handle LinkedIn idea generation, full post creation, post review, repurposing notes into posts, saving LinkedIn writing outputs under output/, or matching Andreas's established Greek-first voice from post/Ανδρέας.docx.
---

# LinkedIn Post Generator

Use this skill only for LinkedIn content tasks.

Follow this workflow:

1. Detect the mode.
2. Read the relevant reference files before writing.
3. Work from the project folders instead of chat history alone.
4. Save every usable output under the correct `output/` subfolder as a timestamped Markdown file.

Detect the mode like this:

- If the user clearly wants topics or angles, use Idea Generation.
- If the user wants a full post, use Post Creation.
- If the user wants to improve a draft, use Post Review.
- If the user did not specify the mode, ask:

```text
Which mode would you like to use?

1. Idea Generation
2. Post Creation
3. Post Review
```

Read [references/brand-guidelines.md](references/brand-guidelines.md) for voice, audience, formatting, and content constraints.

Read [references/workflow.md](references/workflow.md) for mode-specific execution rules, source priority, and output persistence.

Use `scripts/save-output.ps1` to persist usable outputs instead of inventing ad hoc filenames.

Use this output structure:

- `output/ideas/` for Idea Generation
- `output/ready-posts/` for Post Creation
- `output/reviews/` for Post Review

Always pass a descriptive topic slug so the filename is readable without opening the file.

Before writing, inspect the workspace and confirm these folders exist if relevant:

- `ideas/`
- `post/`
- `output/`

For Idea Generation:

- Read all useful files under `ideas/` before generating ideas.
- Extract recurring themes, audience needs, and credible angles.
- Produce exactly 10 distinct ideas by default, each with a 1-2 sentence explanation.
- Save the final ideation output to `output/ideas/`.

For Post Creation:

- Treat `post/Ανδρέας.docx` as the style source of truth unless the user explicitly replaces it.
- Match its tone, rhythm, wording, and paragraph flow more closely than generic LinkedIn best practices.
- Deliver only the final post text when presenting the finished post.
- Save the final post output to `output/ready-posts/`.

For Post Review:

- Preserve the original message and voice.
- Improve clarity, hook strength, credibility, scannability, and ending quality.
- Correct weak, vague, or inaccurate claims directly.
- Save the revised draft to `output/reviews/`.

If Google Drive sync is configured in the project workflow, refresh the local mirror first and then read the local files.

Do not invent personal experiences, metrics, employer details, or achievements.
