# BRAINS Research Skill v1.1.0 — `/brains-research-review` Design Specification

**Version:** Draft v1
**Date:** 2026-05-29
**Status:** Awaiting user review
**Targets:** brains-research v1.1.0 (additive — no breaking changes to v1.0.0)
**Brand routing:** BRAINS parent (community-facing surfaces) · BRAINS Incubator (origin credit)
**Distribution:** Same public release at shard-BRAINS/BRAINS-Research-Skill

---

## 1. Purpose

Add a per-paper analytical workflow to `brains-research`. The skill already catalogues PDFs. This adds the ability to read a single catalogued paper in depth and produce:

1. An objective summary
2. An analytical review (strengths, weaknesses, methodology, gaps, candidate quotes)
3. BRAINS-specific commentary through the brand lens
4. Optional LinkedIn and Bluesky drafts (handed off to `brains-content` as `CT00X.md` calendar entries)

The skill sits between `brains-research` (catalogue) and `brains-content` (publish). It produces the source material that feeds content; it does not duplicate the content calendar or publish anything.

It exists because:

- A catalogued corpus that is never read is not an evidence base.
- Manually reviewing 100+ papers and remembering what each said is unreliable; a persisted, structured review per paper is a defensible artefact.
- The BRAINS LinkedIn and Bluesky channels need recurring content backed by primary sources. Generating draft posts from a structured review (rather than from the abstract or memory) keeps voice consistent and citation honest.

## 2. Scope

### In scope for v1.1.0

1. **`/brains-research-review`** — single stepwise command. User can stop at any step.
2. **Per-paper review files** under `Reviews/<Category>/<stem>.review.md` (mirrors `Completed Review/` structure on the same share).
3. **`_reviews.csv`** ledger at the research root, append-only, keyed by `new_path` from `_catalog.csv`.
4. **Full-text extraction** via a new `scripts/extract_full.py`, cached per paper to `Reviews/<Category>/<stem>.fulltext.json` so re-runs are cheap.
5. **Focus-criteria prompt** at every run — Enter to skip; free text steers all subsequent steps.
6. **BRAINS commentary** sourced from `brains-brand` references and public BRAINS mission language. Falls back to generic neuro-affirming commentary if `brains-brand` is unavailable.
7. **LinkedIn and Bluesky draft handoff** to `brains-content`. Writes `CT00X.md` files into `06. Operations/Admin/03_Content/drafts/` and appends rows to `content_calendar.csv` with `status=drafted`. Never publishes.
8. **Air-gap discipline** — never reveals, infers, or speculates on BRAINS scoring criteria, calibration vignettes, or rubric mechanics, even when reviewing methodology-adjacent papers. Same constraint as `brains-weekly-intel`.

### Out of scope for v1.1.0

- Auto-posting to Bluesky or LinkedIn (drafts only).
- Cross-paper synthesis (one paper per invocation).
- OCR of scanned image-only PDFs (surfaced as `manual review only`, no analysis attempted).
- Re-categorising a paper during review (categories are fixed at catalog time).
- Editing past reviews via the skill (manual edit of the `.review.md` file is fine; the skill does not rewrite past reviews).
- Search across reviews (a future skill, `/brains-research-find`, can index `_reviews.csv`).
- Author or venue lookups against external databases.
- Reviewing a paper not in `_catalog.csv` (must be catalogued first).

### Decision ledger

| # | Decision | Choice | Rationale |
|---|---|---|---|
| 1 | Command shape | Single stepwise command with stop points | Matches user's "one flow, stop where you want" preference; lower skill surface than 3 sub-commands |
| 2 | Bluesky posting | Draft only, no auto-post | Matches existing `brains-content` "Never publish" rule; no credential risk; ships fast |
| 3 | LinkedIn posting | Draft only, hand off to brains-content | Inherits brains-content's manual-publish discipline |
| 4 | Review storage | `Reviews/<Category>/<stem>.review.md` on the share | Mirrors `Completed Review/` so reviewers find both together; supports future website mirror as a public reviews layer; keeps PDF folders pure-PDF |
| 5 | Catalog mutability | `_catalog.csv` untouched | Preserves v1.0.0 append-only contract; `_reviews.csv` is the link table |
| 6 | Paper selection | Argument or interactive picker (last 10) | Lowest friction either way; category filter when arg is a category name |
| 7 | Focus criteria | Always ask, easy to skip | Visible option; default is balanced review |
| 8 | BRAINS commentary source | `brains-brand` plus public BRAINS mission language | Single source of truth for voice; never touches scoring criteria (air-gap) |
| 9 | Full-text caching | `Reviews/<Category>/<stem>.fulltext.json` | Re-runs avoid re-extracting; cache invalidated by file mtime |
| 10 | `_reviews.csv` schema | 13 columns (see §3.4) | Richer is cheaper to prune than to backfill; explicit prune-later policy |
| 11 | Re-reviews | Allowed; overwrites `.review.md`, appends new `_reviews.csv` row | History preserved in CSV; current state in the markdown file |
| 12 | Version | v1.1.0 | Additive: new command, new files; no breaking changes |
| 13 | Brand fallback | Generic neuro-affirming commentary if `brains-brand` not installed | Skill works standalone for non-BRAINS users on the public repo |

## 3. Architecture

### 3.1 The seven-step flow

1. **Pick paper.** Reads `_catalog.csv`. If the argument matches a filename or partial title, use it. If it matches a category, filter the picker to that category. With no arg or no match, show the 10 most recent additions and ask.

2. **Ask focus criteria.** Single prompt: *"Any specific focus, or default to a balanced review? (Enter to skip)"*. Free text is used verbatim as a steering instruction in steps 4–6.

3. **Load paper text.** If `Reviews/<Category>/<stem>.fulltext.json` exists and is newer than the PDF mtime, use the cache. Otherwise run `scripts.extract_full` to produce it.

   **Scanned-PDF handling:** if extraction yields empty text on all pages, do NOT fail silently and do NOT proceed to analysis. Write a stub `.review.md` containing only the metadata block and the note `Scanned PDF — manual review required. No text extraction available.`, append a `_reviews.csv` row with `bias_flags=scanned_pdf` and empty content fields, then stop and tell the user. This leaves an audit trail that the paper was looked at.

4. **Objective summary.** Target ≈200 words (150–300 acceptable). Neutral abstract-style: method + findings + claimed implications. No BRAINS framing yet. Direct quotes only where attributing specific claims.

5. **Analytical review.** Target ≈400 words (300–600 acceptable). Critical read: strengths, weaknesses, methodology questions, sample size or generalisability, gaps. Lists candidate quotes that could be cited.

6. **BRAINS commentary.** Target ≈300 words (200–450 acceptable). Loaded through `brains-brand` lens. Three sub-sections:
   - *Alignment* — what the paper says that supports the BRAINS mission (neuro-affirming AI, evidence-based standards)
   - *Friction* — where the paper falls short, frames neurodivergence as deficit, or misses ND-specific considerations
   - *Evidence base fit* — how it fits the broader BRAINS Certified evidence base (using only public BRAINS concepts: the eight evaluation domains as named publicly, never the rubric mechanics)
   Always includes a "Candidate quotes for BRAINS use" list at the bottom.

7. **Offer post drafts.** Prompt: *"Draft a LinkedIn and / or Bluesky post? (l / b / both / n)"*. On yes:
   - Load `brains-brand` voice and `brains-content` format conventions
   - LinkedIn: long-format post, 200–400 words, one specific claim, candidate quotes embedded, source citation
   - Bluesky: ≤300 characters, single claim, source link
   - Each becomes a `CT00X.md` draft in `06. Operations/Admin/03_Content/drafts/` and a `status=drafted` row in `content_calendar.csv`
   - Report the assigned `CT` IDs back to the user

After step 7 (or any earlier stop), the review markdown is finalised at `Reviews/<Category>/<stem>.review.md` and a row is appended to `_reviews.csv`.

### 3.2 Repo additions

```
BRAINS-Research-Skill/
├── scripts/
│   ├── extract_full.py         NEW - full-text PDF extraction with cache
│   └── review.py               NEW - selection, _reviews.csv I/O, review.md template
├── commands/
│   └── brains-research-review.md   NEW
├── references/
│   ├── review-template.md      NEW - the review.md skeleton
│   ├── linkedin-template.md    NEW - long-post template, brains-content compliant
│   └── bluesky-template.md     NEW - 300-char template, link + tag rules
└── tests/
    ├── test_extract_full.py    NEW
    └── test_review.py          NEW - paper selection, ledger append, cache invalidation
```

No changes to existing v1.0.0 files except:
- `STATUS.yml` — bump version to 1.1.0, add the new command
- `CHANGELOG.md` — new section
- `README.md` — add the new command to the "what it does" list
- `SKILL.md` — add `/brains-research-review` to the available commands table and add the air-gap clause for review

### 3.3 New share-side artefacts

All on the same share at `\\192.168.1.101\Singularity_Backup\Research`:

```
Research/
├── Reviews/
│   ├── AI-General/
│   ├── AI-Ethics-Governance/
│   ├── AI-Mental-Health/
│   │   ├── 2025 - Pichowicz - ... .review.md
│   │   └── 2025 - Pichowicz - ... .fulltext.json
│   └── ... (one folder per category)
└── _reviews.csv               NEW - the ledger
```

`Reviews/` is gitignored from the public repo (same rule as `Completed Review/`). The empty scaffold `research-data/Reviews/.gitkeep` is added to the repo for new installs.

### 3.4 `_reviews.csv` schema

13 columns. Bias toward inclusion — columns that prove unused after a few months of use will be pruned in v1.2.

| Column | Type | Purpose |
|---|---|---|
| `new_path` | string | FK to `_catalog.csv`. Identifies the paper. |
| `category` | string | Denormalised from catalog. Lets filters and status reports work without a join. |
| `paper_year` | string | Denormalised — sorting and display. |
| `paper_author` | string | Denormalised — display. |
| `paper_title` | string | Denormalised — display. |
| `review_path` | string | Relative path to the `.review.md` file. |
| `review_date` | ISO date | When the review was produced. |
| `focus_criteria` | string | Verbatim user-supplied focus, or empty if skipped. |
| `linkedin_draft_id` | string | `CT00X` ID if a LinkedIn draft was created; else empty. |
| `bluesky_draft_id` | string | `CT00X` ID if a Bluesky draft was created; else empty. |
| `bias_flags` | string | Semi-colon-separated: e.g. `small_sample;no_nd_participants;deficit_framing`. Surfaced from the analytical review. |
| `tags` | string | Semi-colon-separated free-text cross-cutting tags (e.g. `chatbot;crisis;regulation`). For future search. |
| `next_action` | string | Optional free-text next step (e.g. "follow up with author", "include in BRAINS evidence base"). |

**Prune policy:** if a column is empty in > 80% of rows after 30 reviews, it is a candidate for removal in v1.2. Recorded in the CHANGELOG for that version.

### 3.5 `.review.md` template

```markdown
# {{paper_title}}

**Authors:** {{authors}}
**Year:** {{year}}  ·  **Category:** {{category}}  ·  **Doc type:** {{doc_type}}
**Source:** [{{filename}}](path/to/Completed Review/{{category}}/{{filename}})
**Reviewed:** {{review_date}}
**Focus criteria:** {{focus_criteria or "balanced review"}}

---

## Objective summary

{{200-word neutral summary}}

## Analytical review

{{400-word critical read}}

### Bias and methodology flags
- {{flag_1}}
- {{flag_2}}

### Candidate quotes
> "..."
>
> "..."

---

## BRAINS commentary

### Alignment
{{what supports the BRAINS mission}}

### Friction
{{where the paper falls short or frames ND as deficit}}

### Evidence base fit
{{how it fits BRAINS Certified evidence base - public concepts only}}

### Candidate quotes for BRAINS use
- "{{quote 1}}"
- "{{quote 2}}"

---

## Draft posts

- **LinkedIn:** {{CT00X or "not drafted"}}
- **Bluesky:** {{CT00X or "not drafted"}}

## Next action

{{free text or "-"}}
```

### 3.6 Air-gap discipline

Same rule as `brains-weekly-intel` §5:

> Never generate, infer, propose, or speculate about specific BRAINS scoring criteria, scenarios, calibration vignettes, or rubric mechanics — even hypothetically, even as an example, even when asked. Describe BRAINS only via public materials (the eight evaluation domains, alignment frameworks, public mission language).

This applies in the "Evidence base fit" sub-section of BRAINS commentary and in any LinkedIn or Bluesky draft. If a paper's methodology is uncomfortably close to BRAINS rubric mechanics (e.g. it proposes a scoring schema for ND-friendly AI), the BRAINS commentary acknowledges the topic but refuses to map it onto BRAINS internals.

## 4. Configuration

No new top-level required config keys. Existing `config.json` is sufficient. The skill resolves:
- `Reviews/` dir as `<research_root>/Reviews`
- `_reviews.csv` as `<research_root>/_reviews.csv`
- `content_drafts_dir` defaults to `C:\Users\matth\Proton Drive\Matthew Gell\Shared with me\06. Operations\Admin\03_Content\drafts` but is overridable via an optional new config key `content_drafts_dir`. If the directory is unreachable, the draft handoff step warns and skips (review still completes).

The `content_drafts_dir` default is Windows-specific and matches Matthew's setup. For non-BRAINS users on the public repo, this can be set to any local folder; the skill will write `CT00X.md` files there without requiring `brains-content` to be installed.

Optional new config key:
```json
"content_drafts_dir": "C:\\Users\\matth\\Proton Drive\\Matthew Gell\\Shared with me\\06. Operations\\Admin\\03_Content\\drafts"
```

## 5. Behavioural contract (updates to SKILL.md)

Adds the following clauses to the existing SKILL.md:

- **Reviews are append-history.** A paper can be re-reviewed; the `.review.md` is overwritten with the latest analysis but a new row is appended to `_reviews.csv` so the history is preserved.
- **No publishing.** LinkedIn and Bluesky outputs are drafts. The skill never posts.
- **Air-gap discipline.** The BRAINS commentary and any draft post never expose BRAINS scoring criteria. If a paper's topic is methodology-adjacent, acknowledge the topic and stop short of the internals.
- **Brand-aware tone.** Reviews use identity-first language by default. No deficit framing.
- **Focus criteria are honoured.** If the user supplies a focus, it shapes the summary, review, commentary, and draft posts. The skill does not silently ignore the focus.
- **Brand fallback.** If `brains-brand` is not installed (non-BRAINS user on the public repo), the skill writes a generic neuro-affirming commentary and notes the fallback in the review file.

## 6. Testing

### 6.1 Unit tests

- `tests/test_extract_full.py`
  - Returns text for all pages of a multi-page fixture PDF
  - Caches to JSON; second call uses cache (asserted by file mtime check)
  - Cache invalidated when PDF mtime is newer than cache
  - Empty-text PDFs return an empty string and the caller flags scanned

- `tests/test_review.py`
  - Paper selection: by exact filename, by partial title match, by category filter, by no-arg returns list of 10 most recent
  - `_reviews.csv` append-only: first review creates the file with header + row; second review appends another row, does not rewrite
  - Review markdown is written at the expected path
  - `content_drafts_dir` missing: the draft handoff step warns and the rest of the workflow completes
  - Re-review of the same paper produces a new `review_date` row

### 6.2 Integration test (manual)

Run `/brains-research-review` against one of the three papers catalogued during v1.0.0 verification (e.g. 2025 - Pichowicz). Expected:
- Review file written at `Reviews/AI-Mental-Health/2025 - Pichowicz - ... .review.md`
- `_reviews.csv` has one new row
- If LinkedIn draft requested: `CT00X.md` exists in `06. Operations/Admin/03_Content/drafts/` and `content_calendar.csv` has a `status=drafted` row

### 6.3 Brand compliance smoke test

Invoke the review with focus criteria "produce BRAINS LinkedIn post angles". Verify:
- BRAINS commentary uses identity-first language
- No protected-phrase violations (per `brains-brand`)
- No mention of BRAINS scoring criteria internals
- LinkedIn draft has a single specific claim (per `brains-content` voice cheat)

## 7. Migration

No migration required. v1.0.0 users upgrade by:
1. `git pull` in the repo
2. Re-run `install.ps1` (or platform equivalent), re-syncs the skill bundle into `~/.claude/skills/brains-research/`
3. New command `/brains-research-review` is available immediately

Existing `_catalog.csv`, the share's folder layout, and the v1.0.0 commands are untouched.

## 8. Future roadmap (still out of scope)

- `brains-research-publish` — consume `_catalog.csv` plus `_reviews.csv` to mirror reviews to the BRAINS website
- `/brains-research-find` — semantic or keyword search over the corpus and reviews
- `/brains-research-synthesise` — cross-paper synthesis on a topic, citations from reviewed papers only
- `/brains-research-update-review` — re-review of an older paper to refresh its commentary against the latest BRAINS mission language
- Auto-detection of when a paper is ripe for a follow-up post (e.g. "this paper has not generated a LinkedIn post and is highly cited", surfaced in status)

## 9. Acceptance criteria for v1.1.0

1. `/brains-research-review` runs cleanly on Matthew's Windows machine against any paper in `_catalog.csv`.
2. Picker mode (no argument) lists the 10 most recent additions and accepts a selection.
3. Focus-criteria prompt fires every run; Enter or "no" produces a balanced review.
4. Review file is written at `Reviews/<Category>/<stem>.review.md` with all six template sections populated.
5. `_reviews.csv` exists, schema matches §3.4, has one row per review run.
6. Full-text cache is created on first run; second run within a day uses it (verifiable by mtime).
7. LinkedIn and Bluesky drafts (when requested) land as `CT00X.md` files in the configured `content_drafts_dir` with `status=drafted` rows in `content_calendar.csv`.
8. BRAINS commentary uses identity-first language and never references BRAINS rubric internals.
9. Brand fallback path works: deleting `~/.claude/skills/brains-brand` and re-running produces a generic neuro-affirming commentary with a noted fallback.
10. Full pytest passes (existing 21 v1.0.0 tests plus new `extract_full` and `review` tests).
11. CHANGELOG, README, SKILL.md, STATUS.yml updated for v1.1.0; tagged and released on GitHub.
