# LinkedIn Posts Generator

Local CLI wrapper around Codex for three workflows:

- idea generation
- post creation
- post review

## Requirements

- Node.js 20+
- Codex CLI installed and logged in

## Run

```bash
cd linkedin-posts-generator
node index.js
```

The CLI will show this menu first:

```text
Which mode would you like to use?
1. Idea Generation
2. Post Creation
3. Post Review
```

The CLI:

- asks for the mode first
- uses `instructions.md` as the base behavior file
- uses every file in `ideas/` for idea generation
- uses the file(s) in `post/` as the writing-style source for post creation
- saves each result as a Markdown file in `output/`

For multiline input in post creation and post review, finish input with:

```text
END
```

## Interactive Examples

### 1. Idea Generation

Run:

```bash
node index.js
```

Example session:

```text
Which mode would you like to use?
1. Idea Generation
2. Post Creation
3. Post Review
Select 1, 2, or 3: 1
Optional topic or direction for idea generation (press Enter to skip): AI agents for work
```

Result:

- the CLI uses all files in `ideas/`
- Codex generates 10 LinkedIn post ideas
- the result is saved into `output/`

### 2. Post Creation

Run:

```bash
node index.js
```

Example session:

```text
Which mode would you like to use?
1. Idea Generation
2. Post Creation
3. Post Review
Select 1, 2, or 3: 2
Paste the bullets or raw context for the post.
Finish with a single line containing END
> I used AI agents to reduce repetitive work.
> I still review everything manually.
> The main gain is better focus, not magic.
> END
```

Result:

- the CLI uses the style file in `post/`
- Codex returns one final post and one alternative
- both are saved in the same Markdown file under `# Final` and `# Alternative`

### 3. Post Review

Run:

```bash
node index.js
```

Example session:

```text
Which mode would you like to use?
1. Idea Generation
2. Post Creation
3. Post Review
Select 1, 2, or 3: 3
Paste the draft you want to improve.
Finish with a single line containing END
> I started using AI agents at work and they changed everything.
> They save me time, but only when I give them good instructions.
> I think most people use them wrong because they expect magic.
> END
```

Result:

- the CLI improves the draft
- Codex returns one improved version and one alternative
- both are saved in the same Markdown file

## Non-Interactive Examples

You can also run the CLI directly from the command line.

### Idea Generation

```bash
node index.js --mode 1 --input "AI agents for work"
```

### Post Creation

```bash
node index.js --mode 2 --input "I used AI agents to reduce repetitive work.\nI still review everything manually.\nThe real gain is better focus."
```

### Post Review

```bash
node index.js --mode 3 --input "I started using AI agents at work and they changed everything.\nThey save me time, but only when I give them good instructions."
```

## Output

Each run creates one Markdown file in `output/`.

Example:

```text
output/20260325-195333-ai-agents-for-work.md
```

For idea generation, the file contains:

```md
# Ideas

...
```

For post creation and post review, the file contains:

```md
# Final

...

# Alternative

...
```
