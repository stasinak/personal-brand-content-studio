# Roadmap

Μελλοντικά enhancements. Όχι σε σειρά προτεραιότητας — απλώς για να μην ξεχαστούν. Το North Star παρακάτω επανατοποθετεί όλα τα υπόλοιπα σαν βήματα προς αυτή τη γενικότερη κατεύθυνση.

---

## 0. North Star: Personal Brand Assistant (multi-domain)

Long-term: αυτό δεν είναι LinkedIn tool. Είναι ο **προσωπικός βοηθός του Ανδρέα** που χειρίζεται πολλές πλευρές της content + communication ζωής του, με κοινό voice/memory σε όλα τα domains.

### Domains

**Content creation:**

| Domain | Status | Scope |
|--------|--------|-------|
| LinkedIn Content | ✅ done | Ideas / Posts / Reviews / Video Repurposing (modes 1-4) |
| Short-form Video Creator | ✅ done | Modes 1-4 (Idea Generation, Script Generation, Improve Script, Q&A) για YouTube Shorts / Reels / TikTok. Long-form video → multiple shorts repurposing και title/caption/tags optimization παραμένουν 🔮 future. |
| Long-form Video Creator | 🔮 future | Full episode outlines, talking points, intro/outro, structure. Idea pool for episodes seeded από Discord questions + comments + trending topics. |
| Podcast / Vidcast Support | 🔮 future | Episode planning, guest question prep, show notes, chapter timestamps, post-episode social clips. |
| Newsletter | 🔮 future | Weekly digest από Discord highlights + recent posts + community moments. |

**Communication:**

| Domain | Status | Scope |
|--------|--------|-------|
| Comment Responses | 🎯 next | Drafts απαντήσεων σε YouTube / LinkedIn / Discord / IG comments στο voice σου |
| Email Drafting | 🔮 future | Drafts επαγγελματικών emails στο voice σου |
| DM/Connection Triage | 🔮 future | Auto-categorize incoming DMs (mentor / collab / recruiter spam) με templated replies |

**Knowledge & ops:**

| Domain | Status | Scope |
|--------|--------|-------|
| Meeting Notes & Actions | 🔮 future | Meeting transcript → action items + follow-ups |
| Knowledge Capture | 🔮 future | Voice memo / quick note → categorized output |
| Title / Thumbnail / SEO | 🔮 future | Title variants + thumbnail copy + tag suggestions για videos και shorts |

### Shared resources (cross-domain)

- **`STYLE_GUIDE.md`** — voice fingerprint, με sub-sections για tone variants (long-form post, comment-casual, email-formal)
- **`/ideas/`** source material — YouTube transcripts + Discord messages ωφελούν πολλά domains (πχ. comment patterns τροφοδοτούν τη φωνή του comment-response domain)
- **Memory + project context** — persists ανεξαρτήτως domain

### Proposed folder structure

Όταν γίνει το refactor, τα τωρινά LinkedIn rules μετακινούνται σε domain folder. Το top-level `AGENTS.md` γίνεται router.

```
AGENTS.md              # top-level: domain router, trigger detection
domains/
  linkedin/AGENTS.md   # current rules (modes 1-4) move here
  comments/AGENTS.md   # new: comment response rules
  email/AGENTS.md      # future
  ...
output/
  ready-posts.md
  comment-replies/     # new
  ...
```

### Trigger detection (top-level AGENTS.md)

Το top-level AGENTS.md αποφασίζει ποιο domain χειρίζεται κάθε input:

- YouTube URL → `linkedin/video-repurposing`
- "Idea Generation" / "Post Creation" / "Post Review" → `linkedin`
- Pasted comment text or comment URL → `comments`
- Pasted email thread → `email`
- Meeting transcript → `meeting-notes`
- Voice memo file → `knowledge-capture`

### Phased rollout plan

1. **Refactor top-level AGENTS.md** as router; μετακίνηση τωρινών rules σε `domains/linkedin/AGENTS.md`
2. **Add `domains/comments/AGENTS.md`** με comment-response rules
3. **Distill comment voice** από τα `all_*_comments.md` → `domains/comments/STYLE_GUIDE.md` (Andreas's actual reply patterns)
4. **Test** με πραγματικά comments, iterate
5. **Επόμενα domains** (email, meetings, newsletter) follow το ίδιο pattern

### Open questions για το comments domain (immediate next)

- **Platforms in scope:** YouTube + LinkedIn confirmed; Discord; Instagram;
- **Input mode:** paste text / URL / screenshot / bulk file
- **Context needs:** χρειάζομαι το original post που σχολιάστηκε, ή το αναζητώ;
- **Output:** μόνο reply text για copy-paste / αυτόματη δημοσίευση μέσω API / save σε log
- **Voice calibration:** ξεχωριστό `STYLE_GUIDE_COMMENTS.md` distilled από τα δικά σου replies?

---

## 1. Pull statistics από LinkedIn

Δυνατότητα να τραβάμε engagement data για τα δημοσιευμένα posts.

**Decisions to make πριν την υλοποίηση:**

- **Ποια stats:**
  - ✅ Εφικτά μέσω LinkedIn API: likes count, comments count, reactions breakdown, comment threads, post URLs
  - ⚠️ Δύσκολα (απαιτούν Marketing Developer Platform — partner approval): impressions, reach, demographic breakdown, click-through rates
  - 🔄 Workaround για τα δύσκολα: manual export από LinkedIn (Settings → Data Privacy → Get a copy) και import σε local file
- **Επιλογή scope:** μόνο εφικτά / και τα δύσκολα μέσω export / και τα δύο
- **Storage:** πού αποθηκεύονται τα stats; Πρόταση: `output/performance.md` log όπου ανά post κρατάμε likes/comments/notable replies. Σταδιακά γίνεται feedback loop για τι αγγίζει το κοινό.
- **API permissions:** το `.env` έχει σήμερα scope `openid profile w_member_social`. Για read social, πιθανόν να χρειαστεί επιπλέον scope (`r_member_social` ή equivalent — να επιβεβαιωθεί ότι είναι διαθέσιμο για το app).

**Πρόταση implementation (όταν έρθει η ώρα):** ξεκίνα από τα εφικτά, βάλε το manual-export workaround σαν 2η φάση.

---

## 2. Direct publishing στο LinkedIn με το νέο flow

Το `scripts/linkedin-mvp.ps1 publish` ήδη υπάρχει, αλλά παίρνει `-FilePath ./output/your-post.md` (παλιό μοντέλο "ένα αρχείο = ένα post"). Με το νέο μοντέλο (`ready-posts.md` = consolidated file), χρειάζεται adapter.

**Decisions to make:**

- **UX:**
  - (a) Νέα εντολή `publish-latest` → publish το πρώτο (newest) post στο `ready-posts.md`
  - (b) `publish --title "..."` → επιλογή ανά τίτλο
  - (c) `publish --date 2026-04-30` → επιλογή ανά ημερομηνία
  - Πιο φυσικό για το current flow: **(a)** σαν default, με optional (b)/(c)
- **Status tracking:** μετά το publish, να μαρκάρεται το post στο `ready-posts.md` ως published. Πρόταση: προσθήκη `**Status:** Published 2026-04-30` line κάτω από το heading.
- **Idempotency:** να μη γίνει double-publish κατά λάθος. Έλεγχος status πριν το send.

**Prerequisites:** LinkedIn app στο Developer Portal με σωστά permissions (έχει ήδη γίνει partial setup με βάση το `.env.example`).

---


## 3. Automation ideas (brainstorm)

Σκοπός: αυτο-σύστημα που τρέχει με ελάχιστη παρέμβαση. Grouped κατά phase του workflow.

### Sourcing & insight refresh

- **Auto-mining refresh** — Periodic re-run του mining όταν έρχονται νέα δεδομένα στο `/ideas` (νέα YouTube videos, comments, Discord messages). Auto-update του analysis report χωρίς manual trigger.
- **Comment-to-idea pipeline** — Σχόλια από YouTube/LinkedIn με επαναλαμβανόμενες ερωτήσεις → αυτο-μετατροπή σε entries στο `idea-pool.md` με την ερώτηση σαν seed. Το audience γράφει το backlog για σένα.
- **Trending topic detection** — Monitor σε Greek tech / programming spectrum (HN, Reddit, X, Discord servers) και surface τα topics που τρέχουν τώρα + δικές σου σχετικές ιδέες.
- **YouTube/Discord auto-pull** — Όταν ανεβάζεις νέο video ή τρέχει νέα κουβέντα στο Discord, αυτό-ενημέρωση των source files στο `/ideas`. Αντί για manual export.

### Content creation

- **Repurpose engine: video → posts** — Από long-form video transcript, auto-παραγωγή 3-5 LinkedIn post angles ανά video. Με 99 videos ήδη υπάρχοντα, massive content multiplier.
- **Cross-format conversion** — Από ένα published LinkedIn post → auto-variants για X/Twitter, Instagram caption, newsletter snippet, YouTube community post. Μία γραφή, πολλά κανάλια.
- **Voice consistency linter** — Automated check πριν το delivery: hook patterns, emoji count, no hashtags, `""` quotes, length match (overlap με το pre-publish checklist που είναι ήδη στις low-priority).

### Publishing

- **Auto-cross-posting** — Όταν δημοσιεύεται post στο LinkedIn, αυτό-distribution σε Discord (community announcement) και προσχέδιο για το newsletter.
- **Posting scheduler** — Queue + auto-post σε optimal windows (πρωινές εργάσιμες ώρες ΕΕΤ). Idempotency baked in (no double-publish).
- **Pre-publish factual sanity check** — Πριν στείλει, για posts με νούμερα/ονόματα/εταιρείες, auto-flag claims που χρειάζονται verification.

### Engagement

- **Engagement watchdog** — Polling likes/comments τις πρώτες 6-12 ώρες μετά το publish. Alert όταν γίνεται viral, όταν εμφανίζεται heated/hate thread, ή όταν senior βλέπει το post (signal για cross-promotion).
- **Comment response drafter** — Drafts απαντήσεων σε εισερχόμενα LinkedIn comments βάσει `STYLE_GUIDE.md`. Άνθρωπος εγκρίνει πριν αποσταλεί (review queue).
- **DM/connection triage** — Αυτο-categorize εισερχόμενα DMs (mentor request / collaboration / recruiter spam / community feedback) με templated replies για κάθε bucket.

### Ops loop

- **Idea-pool auto-replenishment** — Όταν το pool πέφτει κάτω από threshold (πχ. 10 active ιδέες), αυτό-trigger Idea Generation flow.
- **Auto-archiving stale ideas** — Ιδέες που κάθονται >90 μέρες χωρίς να χρησιμοποιηθούν → auto-move σε archive section (όχι deletion).
- **Auto-learning από performance** — Όταν έρχονται stats από #1, αυτό-ενημέρωση εσωτερικών rules για το τι hook patterns / θέματα / lengths δουλεύουν. Sleeve-rolled feedback loop.
- **Weekly digest** — Κάθε Δευτέρα: τι post πήγε καλύτερα την εβδομάδα, τι ιδέες προστέθηκαν στο pool, τι trends εμφανίζονται.

---

## 4. Tracking & Index (foundation για stats + analytics)

Cross-domain tracking: ιδέα → script/post → published → engagement. Σήμερα το status ζει διάχυτο σε markdown files χωρίς stable IDs ή unified view.

**Approach:** hybrid με markdown ως source of truth + regenerable CSV index. Όχι SQLite τώρα — markdown + git είναι το strength του setup. SQLite μπαίνει αργότερα **μόνο** για quantitative metrics (#1).

### Phase A — Tracking foundation

1. **Stable IDs + status frontmatter σε όλα τα content files** — π.χ.
   ```yaml
   ---
   id: short-20260430-001
   type: short | post | idea | comment-reply
   status: idea | scripted | drafted | published
   topic: career-change | junior | mental-side | ...
   created: 2026-04-30
   published_at: null
   source_idea: idea-20260428-003   # cross-link
   ---
   ```
2. **`scripts/build-index.py`** — διαβάζει frontmatters από όλο το `output/`, βγάζει `output/tracking.csv` με columns: `id, type, status, topic, created, published_at, source_idea, title, word_count, file_path`. Ανοίγει σε Excel / pandas.
3. **AGENTS.md updates** — οι 4 domains γράφουν πάντα frontmatter (auto, χωρίς manual step).
4. **Backfill** των υπαρχόντων content files με IDs.
5. **Optional:** git pre-commit hook → regenerate CSV πριν κάθε commit (ώστε CSV πάντα sync).

### Phase B — Performance tracking (joins με #1)

Όταν έρχονται stats από LinkedIn API:
- SQLite DB **μόνο** για metrics (impressions, likes, comments, reach over time)
- Join με content via `id` → performance dashboard
- Content παραμένει σε markdown — δεν μπαίνει σε DB

### Decisions να ληφθούν όταν πάμε υλοποίηση

- **CSV committed ή gitignored;** Committed = τρέχει σε άλλους clones. Gitignored = το κάθε run γεννά fresh.
- **ID format:** `<type>-<YYYYMMDD>-<NNN>` ή UUID; (Πρόταση: το πρώτο — readable.)
- **Topic taxonomy:** σταθερή λίστα ή ελεύθερη; (Πρόταση: σταθερή list βασισμένη στους buckets του STYLE_GUIDE.)
- **Cross-domain ID linking:** όταν ένα idea γίνεται και short και LinkedIn post, χρειάζονται 2 source_idea links ή ένα-προς-πολλά πεδίο;

---

## Άλλες ιδέες (low priority)

Από προηγούμενες συζητήσεις — όχι κρίσιμες, αλλά να μην χαθούν:

- **Pre-publish style checklist** — automated check πριν παραδώσω post (hook patterns, emoji count, no hashtags, `""` quotes, length match)
- **Topic-balance awareness στο Idea Generation** — να κοιτάει την κατανομή του pool και να στοχεύει τα under-represented buckets
- **Repurposing flow (4ο mode)** — Post Refresh: παλιό post από `Ανδρέας.docx` → ξαναγραφή για σημερινό audience
- **Idea metadata** — `Added: YYYY-MM-DD` σε κάθε idea στο pool για να μπορούμε να κλαδέψουμε stale ιδέες
- **Proven posts folder** — 5-10 από τα καλύτερα LinkedIn posts σου με metadata (engagement, ημερομηνία) σαν reference για τι αγγίζει
- **Length variants opt-in** — `/post-variants` εντολή που παράγει short/medium/long
