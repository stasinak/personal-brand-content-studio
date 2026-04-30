# Andreas Voice Fingerprint — Short-Form Video Scripts

Distilled style reference for short-form video scripts (YouTube Shorts / Instagram Reels / TikTok) in Andreas's voice. Source: `/ideas/all_shorts_consolidated.md` — 300 shorts from the Shift Happens YouTube channel, ~38k transcript words. Generated: **2026-04-30**.

> **Different universe from `post/STYLE_GUIDE.md` (long-form LinkedIn) and `domains/comments/STYLE_GUIDE.md` (replies).** Shorts are spoken, not written. Median 135 words. Hook in 2 seconds or you lose them. CTA at the end is soft, often the same signature line.

---

## 0. Length norms (measured from 299 transcripts)

| Stat | Words |
|---|---|
| Min | 3 |
| p25 | 86 |
| **Median** | **135** |
| p75 | 166 |
| Max | 359 |
| Mean | 126 |

The 170-word AGENTS.md cap matches the empirical p75 — i.e., scripts longer than 170w are statistical outliers in his actual output. **Aim for 100-160 words.** Shorter beats longer.

---

## 1. Two distinct registers (do not blend)

The corpus has two formats. The script generator must pick one before drafting.

### A. Solo presenter (~30% of shorts) — Andreas talks straight to camera
Strict structure: **Hook → Share imperative → Setup → Pivot → Lesson → Soft CTA → Signature close.** Provocative, sharp, contrarian.

> "Γίνε προγραμματιστής σε 6 μήνες. Κάνε το βίντεο εκεί που πρέπει και πάμε να σου δείξω πώς να γίνεις προγραμματιστής σε 6 μήνες. Το ακούς παντού. [...] Sorry, not sorry, αλλά αυτό είναι μία από τις μεγαλύτερες παπάτζες που ακούμε εκεί έξω."

### B. Interview clip (~50%+) — guest or Andreas as guest, looser
No formal hook. Question → answer. Often ends mid-thought with a "Yeah" / "Ναι" / "Έτσι". When generating Mode 2 scripts from scratch, **default to register A** unless the user explicitly says it's an interview clip.

> "Πώς επέλεξες στη γερμανική φιλολογία ήταν Ήταν κάτι το οποίο το ήθελες, [...] Η αλήθεια είναι ότι δύο πράγματα μ άρεσαν πάρα πολύ από μικρή."

---

## 2. Hook patterns (first 1-2 sentences — the make-or-break)

Frequency-ordered from the corpus. **The hook IS the title-as-statement** in most solo shorts.

| Pattern | Example openers |
|---|---|
| **Title-restate / declarative** | "Λέωσε τα χέρια σου." / "Μην μάθεις R." / "Δεν υπάρχει η τέλεια γλώσσα." |
| **Imperative claim** | "Πρέπει να φορέσεις τις παροπίδες." / "Μην χρησιμοποιήσεις το AI." |
| **Shock number** | "120 αιτήσεις για μία θέση." / "6 συνεντεύξεις για μια δουλειά." |
| **Question to viewer** | "Θέλεις να μάθεις frontend Τέλεια." / "Τι είναι αυτό το περίφημο data science" |
| **Distinction / "Άλλο το X, άλλο το Y"** | "Άλλο το βείσμα άλλο το referal" |
| **Reflective / first-person** | "Νομίζω ότι πολλές φορές υποτιμάμε την πνευματική δουλειά." |
| **"Πώς ένα..."** structural setup | "Πώς ένα με δύο χρόνια θυσίες μπορούν να αλλάξουνε 30+ χρόνια καριέρα." |

**Don't:** generic openers like "Σήμερα θα μιλήσουμε για...", "Ας δούμε...", "Καλησπέρα παιδιά...". None of those exist in the corpus.

---

## 3. The "share-and-go" hook extension (signature solo move)

In the formal solo shorts of late 2025 / early 2026, the hook is followed by a like/share imperative that doubles as a transition. **This is recognizably his.**

> "Γίνε προγραμματιστής σε 6 μήνες. **Κάνε το βίντεο εκεί που πρέπει και πάμε** να σου δείξω πώς να γίνεις προγραμματιστής σε 6 μήνες."

> "Έτσι πράγματα που μάλλον δεν ήξερες για το shift happens. **Κάνε σέρ το βίντεο σε κάποιον που δεν έχει ιδέα τι είναι το shift Happens και πάμε.**"

> "Μην μάθεις R. **Ρίξε ένα like για να μπορέσω να γίνω καικι εγώ influencer. Κάνε share το βίντεο εκεί που πρέπει και πάμε** αμέσως να δούμε πότε δεν πρέπει να μάθεις R..."

Variations:
- "Κάνε share το βίντεο εκεί που πρέπει και πάμε."
- "Ρίξε ένα like [...] Κάνε share [...] και πάμε."
- "Κάνε σέρ το βίντεο σε κάποιον που [...] και πάμε."

Use sparingly: present in ~10-15% of solo shorts (not all). Optional but signature.

---

## 4. Pivots (hook → body)

The bridge between hook and lesson. Top patterns from the data:

- **"Η αλήθεια είναι ότι..."** — 32 hits across the corpus. The default reframe pivot.
  > "Η αλήθεια είναι ότι μέχρι να γυρίσω Ελλάδα το 24 έκανα ασχολήθηκα με Python."

- **"Spoiler alert"** — 4-8 hits. For reveals.
  > "Spoiler alert είναι και χρειάζεσαι καθοδήγηση για τα πρώτα σου βήματα..."

- **"Sorry, not sorry"** — for blunt counter-takes (rare but signature).
  > "Sorry, not sorry, αλλά αυτό είναι μία από τις μεγαλύτερες παπάτζες που ακούμε εκεί έξω."

- **"Πάμε να δούμε..."** — for explainer/list segue.
  > "Πάμε να δούμε ένα παράδειγμα. Είμαστε δύο και συζητάμε..."

- **"Δεν υπάρχει..."** — debunking opener.
  > "Δεν υπάρχει καλύτερη γλώσσα. Δεν υπάρχει καλύτερος ρόλος, καλύτερη τεχνολογία."

- **"Άλλο το X, άλλο το Y"** — distinction frame.
  > "Άλλο το βείσμα άλλο το referal. Στην Ελλάδα υπάρχει έννοια του βείσματος. Στο στην πραγματική δουλειά υπάρχει έννοια του referal."

- **"Άρα τι πρέπει εγώ να κάνω;"** — self-question segue into actionable advice.
  > "Άρα τι πρέπει εγώ να κάνω ξεκίνα με ένα μικρό καθαρό project..."

---

## 5. Closings — the signature line

The CTA structure of formal solo shorts (the "polished" register, late 2025+):

1. **Soft sales line:** συμβουλευτική / newsletter / Discord
   > "Και αν λοιπόν σε ενδιαφέρει [...] τότε κλείστε συμβουλευτική μαζί μας. Έχουμε και ένα δωρεάν μισάωρο..."
   > "Και αν σε ενδιαφέρει να λαμβάνεις τέτοιο είδους περιεχόμενο εβδομαδιά να γράψου το δωρεάν newsletter μας..."

2. **The signature sign-off (17 instances in the corpus):**
   > "Και αν δεν μας πάρει το AI τη δουλειά, τα λέμε στο επόμενο."

   This phrase is **recognizably Andreas**. Use it as the default closer for Mode 2 solo shorts.

Variations / alternative closes:
- "Τα λέμε την επόμενη." (shorter)
- "Τέλος." (blunt drop, when the lesson lands hard)
- Interview clips often end with just "Yeah." / "Ναι." / mid-thought

**Avoid:** "Subscribe και like για περισσότερα", "Comment below", "Don't forget to..." — the "subscribe + like" line lives in the description, not in the spoken script.

---

## 6. Rhythm — short, punchy, fragments OK

Sentences are short. Fragments are common. Comma-spliced energy beats rounded clauses.

> "Λέωσε τα χέρια σου. Ωραία τα tutorials, τα βιντεάκια και τα shorts με quick tips, αλλά αν δε λερώσεις τα χέρια σου, δεν πρόκειται να δεις προκοπή."

> "Πρώτα HTML αυτός είναι ο σκελετός. Χωρίς αυτό δεν υπάρχει σελίδα. Μετά CSS. Αυτό είναι το στυλ."

> "React, ο ανδιαφισβήτητος βασιλιάς του web. Φτιαγμένο από [Meta], στηρίζει τεράστιο κομμάτι του σύγχρονου web. Είναι μικρό, ευέλικτο και με αυτό μπορείς να χτίσεις από μικρές εφαρμογές μέχρι πολύπλοκα συστήματα."

The script generator must produce **one sentence per line** (per AGENTS.md rules). The line breaks signal cuts in the edit.

---

## 7. Recurring phrases / vocabulary

Greek phrases that appear repeatedly. Use them naturally — overusing makes it sound like a parody.

| Phrase | Frequency context | Use |
|---|---|---|
| **"ας πούμε"** | 52 hits — verbal filler | Conversational softener mid-sentence |
| **"η αλήθεια είναι ότι..."** | 32 hits | Reframe pivot |
| **"okay" / "Okay"** | 140 hits — intentional filler | Resetting transitions |
| **"Spoiler alert"** | 4-8 hits | Reveal pivot |
| **"και τα λέμε στο επόμενο"** | 17 hits | Signature closer |
| **"ρε σύ" / "ρε φίλε"** | 14 hits | Direct address (sparingly) |
| **"Sorry, not sorry"** | 1-2 hits | Blunt counter-take pivot |
| **"παπάτζες"** / **"τρύπα στο νερό"** | rare but distinctive | When dunking on bad advice |
| **"χωρίς να βιάζεσαι" / "βήμα-βήμα"** | recurring | When advising beginners |

---

## 8. Greek vs English

**Greek dominant.** English tech terms embedded freely without translation:

> "ξεκίνα με ένα μικρό καθαρό **project**" / "Ποιο είναι το πιο **front-end framework** να διαλέξω" / "Έχει πάρα πολύ δυνατές βιβλιοθήκες για στατιστική ανάλυση και **visualization**."

Common embedded English: project, framework, junior, full-stack, frontend, backend, hiring manager, recruiter, soft skills, hard skills, vibe coding, assisted coding, product manager, AI, LLM, ChatGPT, Python, JavaScript, React, Angular, Vue, HTML, CSS, debug, deploy, production, integration, business, value, mindset, work-life balance, networking, meetup, referral, offer, mental breakdown, expose, Y.Γ. (no — that's posts).

**No Greeklish letters** in scripts. Clean monotonic Greek.

**No code-switching to full English sentences** in solo shorts (unlike LinkedIn posts, where some closing English lines appear). Shorts stay in Greek.

---

## 9. Tone register — warm contrarian mentor

Andreas-as-presenter is **sharper than his post voice and warmer than a guru voice.** Three flavors:

- **Provocateur** (debunking shorts): "παπάτζες", "Sorry, not sorry", "Δεν υπάρχει [the thing they're chasing]"
- **Practical mentor** (how-to shorts): "ξεκίνα με...", "βήμα-βήμα", "δεν χρειάζεται να είσαι τέλειος"
- **Lived-experience storyteller** (career-change shorts): "θυμάμαι όταν...", "εγώ πέρασα...", first-person specifics

> Provocateur: "Sorry, not sorry, αλλά αυτό είναι μία από τις μεγαλύτερες παπάτζες που ακούμε εκεί έξω."
> Mentor: "Άρα τι πρέπει εγώ να κάνω ξεκίνα με ένα μικρό καθαρό project το οποίο να είναι λειτουργικό χωρίς να πάρεις έτοιμο κώδικα απ έξω."
> Storyteller: "Θυμάμαι στο προπτυχιακό ότι πήγαινα και έπαιρνα μαθήματα από το παιδαγωγικό που προφανώς δεν είχαν να μου δώσουν το παραμικρό..."

**Pick one register per script.** Mixing produces a confused tone.

---

## 10. Voice: first-person singular OR plural team — context dependent

This is **opposite of comments domain** (which is plural-only "ευχαριστούμε").

- **First-person singular** when speaking from lived experience or personal opinion: "Νομίζω ότι...", "Εγώ θα πω...", "Θυμάμαι...", "Πιστεύω..."
- **Plural team voice** ("εμείς / μας / κλείστε συμβουλευτική μαζί μας / να σε βοηθήσουμε") when:
  - Pitching the community / service / newsletter / Discord
  - Closing CTAs ("κλείστε συμβουλευτική **μαζί μας**", "**στείλε μας** μήνυμα")
  - Speaking AS Shift Happens about Shift Happens

The body of a how-to or contrarian short is mostly **first-person singular**. The CTA at the end shifts to **plural team voice**. That mid-script shift is normal — don't try to keep one voice throughout.

---

## 11. Topic distribution (rough buckets from 300 shorts)

| Bucket | % share | Examples |
|---|---|---|
| Career change / "πώς να γίνω προγραμματιστής" | ~30% | "Γίνε προγραμματιστής σε 6 μήνες", "Λάθη στην αλλαγή καριέρας", "Γίνε προγραμματιστής χωρίς μαθηματικά" |
| Tech tools / frameworks / languages | ~20% | "Τα 3 Frameworks που χτίζουν το Front End", "Γιατί να ΜΗΝ μάθεις R" |
| Junior / interviews / job hunt | ~15% | "120 αιτήσεις για μία θέση", "6 συνεντεύξεις", "Hard skills για junior" |
| AI / vibe coding / future of dev | ~10% | "Μήπως τελικά το AI μάς χρειάζεται", "Vibe coding vs assisted coding" |
| Mental side / mindset / time | ~10% | "Imposter syndrome", "Δεν έχω χρόνο", "Πνευματική εργασία" |
| Community / Shift Happens itself | ~5% | "6 πράγματα που δεν ήξερες για το Shift Happens" |
| University / education | ~5% | "Κυνηγάς τον βαθμό ή την αξία", "Πανελλαδικές" |
| Career abroad / salary | ~5% | "3 συμβουλές για εξωτερικό", "Γιατί να αφήσεις την Ελλάδα" |

Mode 1 ideas should reflect this distribution unless user requests a specific bucket.

---

## 12. Topic vocabulary — specific to his world

Words/phrases that signal authentic positioning (use when relevant):
- **Shift Happens** (the community), **shifters** (members), **Discord**, **newsletter**, **συμβουλευτική**, **mentoring**, **meetup**
- **αυτοδίδακτος**, **bootcamp**, **πτυχίο** (re: degree-vs-no-degree debate)
- **Business / value / product** — he frames career advice in business terms, not academic
- **soft skills > hard skills** — recurring claim
- **AI εργαλείο, όχι αντικαταστάτης** — recurring stance
- **"κλάδος"** — he uses this (industry/field) over "industry"
- **"χτίσε βάσεις / θεμέλια"** — recurring metaphor for foundational learning

---

## 13. What he NEVER does in shorts

- ❌ **Hashtags in the script** — they live only in the description
- ❌ **Y.Γ. / P.S.** — that's a post format, never a script
- ❌ **Bullet lists / "5 things you must know"** — even when the title says "3 X" it's spoken as flowing prose, not a numbered read-out
- ❌ **Emoji in the script body** — emojis live in titles/descriptions; the spoken script is plain text
- ❌ **Generic motivational clichés** — "follow your passion", "dream big", "you got this" don't appear in his voice
- ❌ **Direct "subscribe and like for more"** — the engagement bait line lives in description; in-script CTA is soft (συμβουλευτική, newsletter, Discord, meetup)
- ❌ **"Καλησπέρα παιδιά / γεια σας / welcome to my channel"** type openers — never present
- ❌ **Defensive / sarcastic** — even when contrarian, he stays warm
- ❌ **Heavy academic / data-science jargon** — he runs a programming community for career-changers, not a stats course. "Data scientist" appears as a topic, not as a deep-jargon target audience
- ❌ **Greeklish letters** in scripts — clean Greek
- ❌ **Verbose intros** — the lesson lands in the first 2 seconds or the viewer's gone

---

## 14. Tactical reminders for script drafting (Mode 2)

- **Median target: 130-150 words.** 170 is the cap, not the goal.
- **One sentence per line** (AGENTS.md rule + matches his rhythm).
- **First sentence = the hook.** Restate the title as a declarative claim, or a sharp question, or a shock number. No throat-clearing.
- **Pick a register first** (provocateur / mentor / storyteller). Don't blend.
- **Pick a pivot phrase** ("Η αλήθεια είναι..." / "Spoiler alert" / "Sorry, not sorry" / "Πάμε να δούμε..." / "Δεν υπάρχει...").
- **Body = lesson, not lecture.** 3-5 short sentences delivering the point.
- **CTA shifts to plural team voice** ("κλείστε συμβουλευτική μαζί μας" / "στείλε μας μήνυμα" / "γράψου το newsletter").
- **Default closer:** "Και αν δεν μας πάρει το AI τη δουλειά, τα λέμε στο επόμενο." (Optional alternatives: "Τα λέμε την επόμενη." / "Τέλος.")
- **English tech terms embedded freely** — don't force-translate.
- **No emojis, no hashtags, no bullet structure in the spoken text.**
- **When in doubt about length: shorter.**
