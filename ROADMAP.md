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
| Short-form Video Creator | ✅ done | Modes 1-5 (Idea Generation, Script Generation, Improve Script, Q&A, Long-form Video Repurposing — free remixing → 3 standalone shorts ανά video) για YouTube Shorts / Reels / TikTok. Title/caption/tags optimization παραμένει 🔮 future. |
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

> ⚠️ **Verified state (2026-04-30):** programmatic stats reading για personal profiles είναι **partner-only**. Επιβεβαιώθηκε empirically (HTTP 403 ACCESS_DENIED στο `/v2/socialActions/` με `w_member_social` token) και από επίσημα Microsoft Learn docs.

### LinkedIn API reality (hard wall, όχι θέμα setup)

| Δυνατότητα | Status |
|---|---|
| `r_member_social` scope | ❌ "Restricted and available to approved users only" — partner approval needed |
| Member Post Analytics API (released 2025) | ❌ Partner-only — "initial access via select partners (Influent Social κ.ά.)" |
| Marketing Developer Platform approval | ❌ Gated σε agencies / marketing-tech companies, **όχι** individual creators |
| Social Actions endpoint (`/v2/socialActions/`) | ❌ 403 για personal app ακόμα και για own posts (tested 2026-04-30) |

### Realistic paths (ranked)

#### 🟢 (a) LinkedIn Data Export — TOS-safe, manual trigger

1. linkedin.com → Settings & Privacy → Data Privacy → **"Get a copy of your data"**
2. Check **Shares** + **Articles** + **Reactions**
3. ZIP arrives σε ~10-30 min (sometimes 24h)
4. Contains `Shares.csv` με likes/comments per post + impressions για πρόσφατα posts
5. **Implementation:** `skills/linkedin/import_export.py` parser → `output/performance.csv`
6. **Tradeoff:** όχι real-time. Manual download ανά εβδομάδα/μήνα.

#### 💰 (b) Third-party SaaS

Shield, Inlytics, AuthoredUp, Taplio — LinkedIn-approved partners με programmatic access. €20-50/month. Κάποια εκθέτουν API που μπορούμε να καλέσουμε.

**Tradeoff:** ongoing cost + dependency on third party.

#### ⚠️ (c) Browser scraping (Playwright/Puppeteer) — **ΔΕΝ προτείνεται**

Παραβιάζει LinkedIn TOS. Ρεαλιστικός κίνδυνος account suspension/ban — για personal brand που χτίζεται πάνω στο LinkedIn, καταστροφικό.

### Decisions όταν πάμε υλοποίηση

- **Phase 1:** Data export parser (a) → `output/performance.csv` με stable column schema (post_urn, url, date, likes, comments, shares, impressions_if_present)
- **Phase 2:** Join με Tracking & Index (Section 4) via `id` για performance dashboard
- **Refresh cadence:** weekly manual trigger μέχρι να βρεθεί ευκολότερο workflow

### Sources

- [Posts API — Microsoft Learn (LinkedIn, v2026-04)](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-03)
- [LinkedIn FINALLY released a personal analytics API — Garret Caudle, 2025](https://www.linkedin.com/posts/garretcaudle_linkedin-finally-released-a-personal-analytics-activity-7365758127662587904-9jrr)

---

## 2. Direct publishing + scheduling στο LinkedIn

> ⚠️ **Verified state (2026-04-30):** `POST /rest/posts` με `w_member_social` ✅ δουλεύει για immediate publishing. **Server-side scheduling δεν υπάρχει** σαν feature στο API για member posts. Drafts δεν δημιουργούνται μέσω API. Verified από επίσημο Microsoft Learn doc.

### LinkedIn API reality

| Δυνατότητα | Status |
|---|---|
| Immediate publish (member) | ✅ `POST /rest/posts` με `lifecycleState: PUBLISHED` |
| Server-side scheduling (`scheduledAt`) | ❌ **Δεν υπάρχει** σαν field για member posts. Όχι θέμα έγκρισης — δεν existsει |
| Create draft via API | ❌ "PUBLISHED is the only accepted field during creation". DRAFT μόνο σε responses από UI-created drafts |
| Update published post | 🟡 Partial — μόνο `commentary` updateable, όχι αναδημοσίευση |
| Delete post | ✅ `DELETE /rest/posts/{urn}` |
| Rate limit | ~100 calls/day per member |

### Architecture: client-side scheduling (ο μόνος δρόμος)

Αφού server-side scheduling δεν υπάρχει στο API, η μόνη διαδρομή είναι **client-side** — εμείς κρατάμε queue (στο `ready-posts.md`), εμείς πατάμε "publish now" τη σωστή στιγμή. Αυτό κάνουν **όλα** τα third-party tools (Buffer, Hootsuite, Shield) — δεν είναι workaround, είναι ο normal δρόμος για το LinkedIn API.

### Implementation phases

#### Phase 1 — Publish skill

- `skills/linkedin/linkedin.py publish <post-id>` — publish συγκεκριμένο post by id
- Frontmatter στο `ready-posts.md` (συνδέεται με Section 4 — Tracking & Index):
  ```yaml
  ---
  id: post-20260501-001
  status: scheduled | published
  scheduled_at: 2026-05-02T09:00:00+03:00
  published_at: null
  post_urn: null
  ---
  ```
- **Idempotent:** skip ήδη published. Μετά το επιτυχές POST: mark `status: published`, set `published_at` + `post_urn` (από response header `x-restli-id`)

#### Phase 2 — Scheduler

- `linkedin.py publish --next-scheduled` — βρίσκει πρώτο `scheduled_at <= now AND status: scheduled`, publishes
- Cron trigger options:
  - **GitHub Actions cron** ⭐ — cloud-side, no machine-on, token σε encrypted Secret. Free σε personal repo.
  - **Local cron** στο WSL — trivial setup, requires laptop on
  - **Manual** — εσύ τρέχεις `--next-scheduled` όταν θες
- **Token lifecycle:** το LinkedIn token διαρκεί 60 ημέρες. Χρειάζεται είτε manual re-auth κάθε 2 μήνες είτε refresh_token logic (LinkedIn refresh tokens διαρκούν 365 ημέρες — προτεινόμενο).

### Decisions όταν πάμε υλοποίηση

- **UX:** μόνο `scheduled_at` per post, ή high-level κανόνες (πχ. "auto-distribute next 5 posts σε weekday mornings");
- **Optimal posting times:** σταθερό window (πρωινές εργάσιμες ΕΕΤ) ή adaptive βάσει performance data;
- **Failure handling:** retry σε 5xx, alert σε 401/403 (token expired);
- **GitHub Actions secrets:** πώς διατηρείται refreshed το token σε Secret χωρίς manual intervention;
- **Migration path:** το legacy `scripts/linkedin-mvp.ps1` σε rewrite ή deprecate;

### Sources

- [Posts API — Microsoft Learn (LinkedIn, v2026-04)](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-03)

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

## 5. Google Drive integration

Σύνδεση του project με το Google Drive ώστε να γράφει/διαβάζει απευθείας από εκεί. Λύνει 4 προβλήματα μαζί.

**Why:**
- **Mobile access** — γράφεις/διορθώνεις post ή idea από κινητό μέσω Drive app, όχι μόνο desktop + git
- **Cross-device sync χωρίς git workflow** — χωρίς `git pull` σε κάθε συσκευή
- **CSV tracking → Google Sheets** — το `output/tracking.csv` (Section 4) ανοίγει απευθείας ως Sheet, sort/filter/pivot live
- **Voice memo capture pipeline** — υπαγορεύεις στο κινητό → Drive folder → drain skill το γυρνάει σε idea στο `idea-pool.md` (το είχες ζητήσει σε προηγούμενη συνεδρία ως pending)

### Approach options (tradeoffs)

| Approach | Pros | Cons |
|---|---|---|
| **(a) MCP server** (Claude έχει Google Drive MCP διαθέσιμο) | Native — read/write μέσα από conversation. No daemon. On-demand. | Δουλεύει μόνο μέσα από Claude. Δεν βοηθάει για mobile-only edits. |
| **(b) Local sync (Drive Desktop / rclone)** | Transparent — ο κώδικας δεν αλλάζει, files εμφανίζονται μόνα τους στο Drive. Mobile flow δουλεύει. | Sync delays. Conflict resolution αν editing από 2 μεριές. Daemon να τρέχει. |
| **(c) Drive API direct (Python skill)** | Full control. No daemon. Reuse του OAuth setup που ήδη έχουμε για YouTube Data API. | Extra code layer. Όχι transparent — κάθε save χρειάζεται explicit API call. |

### Recommended: hybrid (a) + (b)

- **(a) MCP** για interactive Claude-driven edits — επόμενες συνεδρίες διαβάζουν published posts / scripts / ideas χωρίς git pull
- **(b) Drive Desktop sync** για mobile-to-desktop flow — voice memo upload από κινητό, drain από desktop όταν βρίσκεσαι σε Claude session

### Phase plan

1. **Set up Drive folder structure** — mirror του local `output/` (`output/ready-posts.md`, `output/shorts/`, `output/comment-replies/`, `output/_transcripts/`, `output/tracking.csv`)
2. **Test MCP read** — επιβεβαίωση ότι το Google Drive MCP server διαβάζει τα files σωστά μέσα από Claude session
3. **Voice memo pipeline** — `output/voice-memos/inbox/` (synced από κινητό) → drain skill που τραβάει το audio, transcribes (το `youtube-transcript-fetcher` Whisper logic μπορεί να επαναχρησιμοποιηθεί), προσθέτει entry στο `idea-pool.md`, μετακινεί σε `output/voice-memos/processed/`
4. **Optional bidirectional sync** για `ready-posts.md` — edit από οποιαδήποτε συσκευή, με conflict resolution policy
5. **CSV → Sheets** — το `tracking.csv` της Section 4 γίνεται live Sheet, με filter views ανά domain/status/topic

### Decisions να ληφθούν όταν πάμε υλοποίηση

- **Folder structure στο Drive:** mirror 1:1 με το local, ή flatten με tags;
- **Auth:** OAuth (όπως ήδη στο YouTube setup — refresh token persisted) ή service account;
- **Conflict resolution:** last-write-wins, merge, ή lock-while-editing;
- **Sync trigger:** every save automatic, batched ανά X λεπτά, ή manual `sync` command;
- **Voice memo language detection:** auto-detect (όπως το έχουμε ήδη στο fetch.py) ή force Greek;
- **Privacy:** όλο το `output/` σε Drive ή μόνο published material; (γιατί στο Drive, αν shared, κάποιοι μπορούν να τα δουν)

---

## Άλλες ιδέες (low priority)

Από προηγούμενες συζητήσεις — όχι κρίσιμες, αλλά να μην χαθούν:

- **Pre-publish style checklist** — automated check πριν παραδώσω post (hook patterns, emoji count, no hashtags, `""` quotes, length match)
- **Topic-balance awareness στο Idea Generation** — να κοιτάει την κατανομή του pool και να στοχεύει τα under-represented buckets
- **Repurposing flow (4ο mode)** — Post Refresh: παλιό post από `Ανδρέας.docx` → ξαναγραφή για σημερινό audience
- **Idea metadata** — `Added: YYYY-MM-DD` σε κάθε idea στο pool για να μπορούμε να κλαδέψουμε stale ιδέες
- **Proven posts folder** — 5-10 από τα καλύτερα LinkedIn posts σου με metadata (engagement, ημερομηνία) σαν reference για τι αγγίζει
- **Length variants opt-in** — `/post-variants` εντολή που παράγει short/medium/long
