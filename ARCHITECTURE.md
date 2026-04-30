# Personal Brand Assistant — Architecture

> Brief design doc για το multi-domain personal assistant. Lean by default — προσθέτουμε complexity μόνο όπου το justify-άρει η χρήση. Βασισμένο σε SOTA Claude Code patterns (2026), προσαρμοσμένο σε single-user content workflow.

## 1. Vision in one sentence

Ένα conversation που χειρίζεται content creation + communication + knowledge ops σε 11 domains, με κοινό voice fingerprint και κοινή memory — χωρίς ο χρήστης να μαθαίνει 11 διαφορετικά εργαλεία.

## 2. Core design principle

**Filesystem-driven, intent-routed, skill-augmented.**

- Filesystem-driven: η δομή του repo είναι το source of truth για ποια domains υπάρχουν και πώς δουλεύουν. Αν φαίνεται στο tree, υπάρχει.
- Intent-routed: το top-level config περιγράφει triggers σε φυσική γλώσσα (URL → video repurpose, paste comment → comments). Όχι slash commands, όχι path-globs — απλώς ο agent καταλαβαίνει.
- Skill-augmented: εκεί που χρειάζεται executable code (fetch transcript, publish post), έχουμε `uv`-based scripts στο `skills/`. Όχι heavy Python services.

**Anti-principle:** μην προσθέτεις Claude Code feature επειδή υπάρχει. Πρόσθεσέ το όταν το current setup σε στραγγίζει.

## 3. Architecture

### 3.1 Filesystem layout

```
personal-brand-content-studio/
├── CLAUDE.md                       # top-level router (replaces current AGENTS.md role)
├── AGENTS.md                       # imported by CLAUDE.md via @AGENTS.md
├── ROADMAP.md                      # vision + future enhancements
├── ARCHITECTURE.md                 # this file
│
├── domains/
│   ├── _shared/
│   │   ├── STYLE_GUIDE.md          # base voice fingerprint
│   │   ├── brand-positioning.md    # role, audience, topics, weighting
│   │   └── source-material.md      # how to find/use /ideas data
│   ├── linkedin/
│   │   ├── AGENTS.md               # current modes 1-4 move here
│   │   ├── STYLE_GUIDE.md          # tone variant if differs from _shared
│   │   └── (domain-specific resources)
│   ├── comments/
│   │   ├── AGENTS.md               # comment-response rules
│   │   └── STYLE_GUIDE.md          # casual/short voice distilled from data
│   └── (future: video, podcast, email, ...)
│
├── ideas/                          # source material (YouTube + Discord exports)
├── post/                           # style sources (Ανδρέας.docx, STYLE_GUIDE.md)
│
├── output/
│   ├── idea-pool.md                # active LinkedIn ideas
│   ├── ready-posts.md              # published-ready LinkedIn posts
│   ├── comment-replies/            # NEW: drafted comment responses
│   ├── _transcripts/               # YouTube transcript cache
│   └── _analysis/                  # mining reports
│
├── skills/                         # executable capabilities (project-internal)
│   ├── youtube-transcript-fetcher/ # uv-based, already exists
│   ├── linkedin-post-generator/
│   └── (future: comment-publisher, email-sender, ...)
│
└── scripts/                        # PowerShell legacy (LinkedIn/Drive OAuth)
```

### 3.2 The 6 layers

| Layer | What it does | Implementation |
|-------|--------------|----------------|
| **Top-level CLAUDE.md** | Router. Detects domain from user input, dispatches to domain config. | Markdown rules with trigger patterns + `@domains/<name>/AGENTS.md` imports |
| **Domain configs** | Per-domain workflow rules, modes, output destinations. | `domains/<name>/AGENTS.md` |
| **Shared resources** | Voice, brand, source-material rules used across domains. | `domains/_shared/*` referenced by `@` imports |
| **Skills** | Executable actions (fetch, publish, transcribe). | `skills/<name>/fetch.py` (uv self-contained scripts) |
| **MCP servers** | External services (Gmail, Drive, Calendar). | Already configured in user-level settings |
| **Memory** | Cross-domain learnings, user preferences. | `~/.claude/projects/<encoded>/memory/MEMORY.md` |

## 4. Trigger detection (the magic of "intent routing")

Το top-level `CLAUDE.md` περιγράφει τις rules με φυσική γλώσσα. Παραδείγματα:

```markdown
## Domain routing

Detect the appropriate domain from the user's input and load the matching
`domains/<name>/AGENTS.md` for its rules:

- YouTube URL → `domains/linkedin/AGENTS.md` (Mode 4: Video Repurposing)
  unless user explicitly says "for podcast" / "for short" → other domain
- "Idea Generation" / "Post Creation" / "Post Review" / mode-1-2-3 keywords
  → `domains/linkedin/AGENTS.md`
- Pasted comment text or comment URL → `domains/comments/AGENTS.md`
- Email thread paste → `domains/email/AGENTS.md`
- Voice memo file (.m4a, .mp3) → `domains/knowledge-capture/AGENTS.md`
- Meeting transcript paste → `domains/meeting-notes/AGENTS.md`
- If unclear, ASK once: "Which domain: <list>?"
```

**Why no router subagent or LLM-based hook:** για 11 domains μέσα σε personal use, ο main agent μπορεί να κάνει routing inline για 0 token overhead. Sub-agents ή hooks είναι enterprise-pattern overkill εδώ.

## 5. Claude Code feature decisions

| Feature | Use? | Reasoning |
|---------|------|-----------|
| **CLAUDE.md / AGENTS.md** + `@` imports | ✅ Primary | Cheap, always loaded, perfect for rules. Modular via imports. |
| **Path-scoped rules** | ❌ | Triggers είναι intent-based (URL paste), όχι file-path-based. |
| **Skills** (`.claude/skills/SKILL.md`) | 🟡 Later | Όταν `uv` scripts γίνουν >5 και επαναλαμβάνονται. Σήμερα τους καλούμε via Bash από οδηγίες στο AGENTS.md. |
| **Sub-agents** (`.claude/agents/`) | 🟡 Selectively | Μόνο για **expensive isolated tasks**: bulk comment drafting, deep mining, video transcription. ΟΧΙ ένα sub-agent ανά domain (4x token cost χωρίς αξία). |
| **Hooks** | 🟡 Guardrails only | Πχ. PreToolUse → `voice-check` πριν δημοσιευτεί κάτι. ΟΧΙ για routing. |
| **MCP servers** | ✅ Already configured | Gmail (email domain), Drive (source material), Calendar (meeting notes). User-level config, reused per project. |
| **Auto-memory** + `MEMORY.md` | ✅ In use | Cross-domain learnings. Δεν αποθηκεύουμε credentials εκεί. |
| **Slash commands** | 🟡 As shortcuts | Όταν workflow γίνει εντελώς προβλέψιμο (πχ. `/linkedin-publish-latest`). Όχι για επιλογή domain. |
| **Managed Agents** (Claude API) | ❌ | Single-user, χωρίς HTTP API need. |

## 6. Voice handling across domains

Single source of truth: `domains/_shared/STYLE_GUIDE.md` με base voice fingerprint.

Domain-specific variants κληρονομούν και overrideουν:
- `domains/linkedin/STYLE_GUIDE.md` — long-form, hooks, Y.Γ., emojis 3-5
- `domains/comments/STYLE_GUIDE.md` — short, conversational, no hooks/Y.Γ., 0-2 emojis
- `domains/email/STYLE_GUIDE.md` — formal but warm, no emojis

Distillation: για κάθε νέο domain, mining από existing data (`/ideas/all_*_comments.md` δείχνει πώς απαντάς σε YT comments → comments STYLE_GUIDE).

## 7. Migration path

### Phase 1 — Refactor in place (~1 hour, zero behavior change)

1. Δημιουργία `domains/_shared/` και μετακίνηση κοινών sections από `AGENTS.md`
2. Δημιουργία `domains/linkedin/AGENTS.md` με τις τωρινές modes 1-4
3. Νέο top-level `CLAUDE.md` (router) που κάνει `@AGENTS.md` import + αναφέρει routing rules
4. Παλιό `AGENTS.md` παραμένει αλλά γίνεται thin (project intro + glue)
5. Test: τα τωρινά flows (Idea Gen, Post Creation, Video Repurposing) δουλεύουν αμετάβλητα

### Phase 2 — Add Comments domain (~1-2 hours)

1. `domains/comments/AGENTS.md` με rules (input formats, output destinations, voice)
2. Mining fork → distill `domains/comments/STYLE_GUIDE.md` από `all_*_comments.md`
3. `output/comment-replies/` directory για log
4. Test με 3-5 πραγματικά comments

### Phase 3 — Add domains incrementally

Κάθε νέο domain = ~30-60 min: AGENTS.md + (optional) STYLE_GUIDE distillation + (optional) skill για executable work. Pattern is replicable.

## 8. Open trade-offs

- **AGENTS.md vs CLAUDE.md naming**: Claude Code reads `CLAUDE.md` natively. Codex/άλλα CLI agents reads `AGENTS.md`. Solution: top-level `CLAUDE.md` που imports `@AGENTS.md` — και τα δύο tools δουλεύουν.
- **Domain depth vs breadth**: 11 domains ακούγονται πολλά. Στην πράξη, 3-4 active + 7 dormant είναι fine. Phase rollout κρατά scope under control.
- **Static voice vs learning voice**: το `STYLE_GUIDE` σήμερα είναι hand-curated. Long-term, performance log (από LinkedIn stats roadmap item) θα δίνει σήμα για auto-tuning.
- **Cross-domain memory pollution**: σήμερα η memory είναι single-pool. Αν κάποιο domain insight δεν ισχύει αλλού, να μαρκάρεται με tag στο memory entry.

## 9. Concrete next 3 steps

1. **Phase 1 refactor** — μηδενικό ρίσκο, πλάκα-καθαρισμός. Όλα τα flows συνεχίζουν να δουλεύουν.
2. **Comments domain** — υψηλή value, ξεκλειδώνει το πρώτο non-LinkedIn use case.
3. **Voice distillation skill** — generic skill που παίρνει ένα corpus (π.χ. comments file) και βγάζει STYLE_GUIDE. Reusable για κάθε νέο domain.

---

**Bottom line:** lean architecture που σε αφήνει να προσθέσεις domain σε 30-60 λεπτά, χωρίς πρόωρο abstraction layer. Claude Code features μπαίνουν σταδιακά όπου το πραγματικό setup χρειάζεται complexity — όχι preemptive.
