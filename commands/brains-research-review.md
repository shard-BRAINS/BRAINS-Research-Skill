---
description: Review a single catalogued paper — objective summary, analytical review, BRAINS commentary, optional LinkedIn + Bluesky drafts. Persists to Reviews/<Category>/<stem>.review.md and _reviews.csv.
---

# /brains-research-review

Produce a structured per-paper review and optional draft posts. Stepwise — user can stop at any step.

**Paths come from `config.json` at the skill root.** Reviews land at `<research_root>/Reviews/<Category>/<stem>.review.md`. Optional content drafts land at `<content_drafts_dir>/drafts/CT00X.md`.

**Locked references — load these before producing prose:**

- `references/review-template.md` — what each section of `.review.md` should contain (objective summary, analytical review, BRAINS commentary, candidate quotes)
- `references/linkedin-template.md` — voice and structure for the LinkedIn draft
- `references/bluesky-template.md` — voice and 300-char budget for the Bluesky draft
- `~/.claude/skills/brains-brand/SKILL.md` and its references — brand voice and protected phrases. If unavailable, fall back to generic neuro-affirming commentary and note this in the review.

## Air-gap rule

**Never** reveal, infer, or speculate on BRAINS scoring criteria, calibration vignettes, or rubric mechanics — even when commenting on methodology-adjacent papers. Describe BRAINS only via public materials (the eight evaluation domains, alignment frameworks, public mission language). If a paper's methodology is uncomfortably close, acknowledge the topic and stop short of internals.

## Steps

### Step 1 — Pick paper

If the user supplied an argument:
- First call `scripts.review.select_paper(arg)`. If it returns a row, use that row.
- Otherwise, if the argument matches one of the 10 locked categories (e.g. `AI-Mental-Health`), call `scripts.review.list_recent_papers(n=10, category=arg)` and present the result as a numbered picker.
- Otherwise, fall back to the no-arg flow below.

If no argument: call `scripts.review.list_recent_papers(n=10)` and present the last 10 catalogued papers, numbered. Ask the user to pick one.

Invocation pattern for either function in Python:

```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -c "from scripts.review import list_recent_papers; import json; print(json.dumps(list_recent_papers(n=10, category='AI-Mental-Health'), indent=2))"
```

### Step 2 — Ask focus criteria

Ask exactly once: *"Any specific focus, or default to a balanced review? (Enter to skip)"*

Capture the response verbatim as `focus_criteria` (or empty string if skipped). Pass it as steering context to steps 4–6 and any draft post.

### Step 3 — Load paper text

Resolve `pdf_path` from `<research_root>/<paper.new_path>` and `cache_path` from `scripts.review.fulltext_cache_path_for(paper)`. Call `scripts.extract_full.load_or_extract(pdf_path, cache_path)`. The function returns a list of strings, one per page.

Call `scripts.extract_full.is_scanned(pages)`. If True:
1. Call `scripts.review.write_scanned_stub(paper=paper, review_date=today_iso)`.
2. Call `scripts.review.append_review_row({..., bias_flags: "scanned_pdf", ...all_other_fields_empty})`.
3. Report: *"Scanned PDF — manual review required. Stub review.md written at <path>. No further analysis attempted."*
4. Stop.

Otherwise, the full text (joined with `\n\n` between pages) is the input for the next three steps.

### Step 4 — Objective summary

Produce ≈200 words (150–300 acceptable) per `references/review-template.md` §Objective summary. No BRAINS framing. Identity-first language by default. If the user supplied focus criteria, weight the summary accordingly.

### Step 5 — Analytical review

Produce ≈400 words (300–600 acceptable) per `references/review-template.md` §Analytical review. Produce:
- Strengths
- Weaknesses
- Sample and generalisability
- Methodology questions
- Gaps
- Bias and methodology flags (bulleted, tag-style — these become `bias_flags` semi-colon joined)
- Candidate quotes (3–6 blockquotes)

### Step 6 — BRAINS commentary

Load `~/.claude/skills/brains-brand/SKILL.md` and its references. If unavailable, write neuro-affirming commentary without BRAINS-specific surfaces and add the note `(brains-brand fallback active)` to the BRAINS commentary section.

Produce ≈300 words (200–450 acceptable) per `references/review-template.md` §BRAINS commentary:
- Alignment
- Friction
- Evidence base fit (air-gap rule applies)
- Candidate quotes for BRAINS use

### Step 7 — Offer post drafts

Prompt: *"Draft a LinkedIn and / or Bluesky post? (l / b / both / n)"*

On `n`, skip to write-out. On `l`, `b`, or `both`:

1. Load `references/linkedin-template.md` and / or `references/bluesky-template.md`.
2. Load `brains-brand` voice rules (already loaded in step 6, but confirm — protected phrases, identity-first language).
3. For each requested channel, draft the body per its template.
4. Resolve content root from the config: `cfg.content_drafts_dir`. If it is None or unreachable, skip with a warning — review still completes; the user is told the draft was not written.
5. Call `scripts.review.next_ct_id(content_root)` to get the next ID. If both channels were requested, draft the LinkedIn first, then the Bluesky (so LinkedIn gets `CT_N`, Bluesky gets `CT_(N+1)`).
6. Call `scripts.review.write_content_draft(...)` for each draft.
7. Capture the returned CT IDs as `draft_ids = {"linkedin": "CT00X", "bluesky": "CT00Y"}`.

### Step 8 — Write out

1. Call `scripts.review.write_review_file(...)` with the six sections, `focus_criteria`, `draft_ids`, and the `next_action` (free text if the analytical review suggested one, else empty).
2. Call `scripts.review.append_review_row(...)` with all 13 columns populated as far as possible. Empty columns are empty strings.
3. Report concise summary:
   - Paper reviewed
   - Review file path
   - Bias flags
   - Draft IDs (if any)
   - Next action (if any)
   - Reminder: `_reviews.csv` updated; review.md is the canonical artefact.

## Dry-run

If the user says "dry run" or "preview", produce all six sections in chat but do NOT call `write_review_file`, `append_review_row`, or `write_content_draft`. Report what would have been written.
