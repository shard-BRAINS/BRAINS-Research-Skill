# Review template — what to put in each section

The `.review.md` file is written by `scripts.review.write_review_file`. Below is what Claude should produce for each section when running `/brains-research-review`. The template fills these into a markdown file at `Reviews/<Category>/<stem>.review.md`.

## Objective summary

Target ≈200 words (150–300 acceptable). Neutral abstract-style. Cover:

- What the paper studies
- Method (study type, sample, instruments)
- Findings (specific, not vague)
- Claimed implications

No BRAINS framing yet. No editorialising. Direct quotes only where attributing a specific claim. Identity-first language by default.

## Analytical review

Target ≈400 words (300–600 acceptable). Critical, not promotional. Cover:

- **Strengths** — what the paper does well (specific)
- **Weaknesses** — methodological gaps, scope limits, alternative explanations
- **Sample / generalisability** — N, diversity, neurodivergent representation specifically
- **Methodology questions** — what the paper does not address that a critical reader would ask
- **Gaps** — what is missing from the analysis

### Bias and methodology flags

A bulleted list of short tag-style flags. Examples:
- `small_sample` (N < 50)
- `no_nd_participants` (study about ND topic without ND participants)
- `deficit_framing` (frames neurodivergence as deficit)
- `single_site` (single-institution data)
- `industry_funded` (potential conflict of interest)
- `convenience_sample` (non-representative recruitment)
- `self_report_only` (no objective measures)

These tags populate the `bias_flags` column of `_reviews.csv` (semi-colon joined).

### Candidate quotes

Three to six direct quotes from the paper that capture key claims, surprising findings, or quotable phrasing. Use blockquotes (`>`).

## BRAINS commentary

Loaded through the `brains-brand` lens (see `~/.claude/skills/brains-brand/SKILL.md` and references). If `brains-brand` is unavailable, write neuro-affirming commentary without the BRAINS-specific surfaces and add a note: `(brains-brand fallback active — generic neuro-affirming commentary)`.

### Alignment

What the paper says that supports the BRAINS mission: neuro-affirming AI, evidence-based standards, accountability of AI systems to neurodivergent users. Be specific. Quote where useful.

### Friction

Where the paper falls short of a neuro-affirming framing. Examples:
- Frames neurodivergence as deficit
- Uses person-first language inappropriately
- Treats neurotypical baselines as the standard
- Misses ND-specific considerations a BRAINS-aligned reader would expect

### Evidence base fit

How the paper fits the broader BRAINS Certified evidence base. **Air-gap rule:** describe BRAINS only through public concepts (the eight evaluation domains, alignment frameworks, public mission language). Never reveal, infer, or speculate on BRAINS scoring criteria, calibration vignettes, or rubric mechanics — even hypothetically.

If a paper's methodology is uncomfortably close to BRAINS rubric mechanics, acknowledge the topic and stop short of internals.

### Candidate quotes for BRAINS use

Bulleted list of quotes that could appear in BRAINS-facing content (LinkedIn, newsletter, blog), with the speaker / attribution.

## Tags

Free-text cross-cutting tags, semi-colon separated, used for future search. Examples: `chatbot;crisis;regulation`, `ND_voice;workforce;burnout`.

## Next action

Optional. Free text. Examples:
- `follow up with author for clarification on Table 2`
- `include in BRAINS evidence base - high-quality empirical work`
- `re-review in 6 months when follow-up study is published`
- `do not draft a post yet - too preliminary`

Defaults to `-` if nothing useful.
