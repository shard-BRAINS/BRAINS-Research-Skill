# BRAINS Research Skill — Design Specification

**Version:** Draft v1
**Date:** 2026-05-28
**Status:** Awaiting user review
**Brand routing:** BRAINS parent (community-facing surfaces) · BRAINS Incubator (origin credit)
**Distribution intent:** Public release via the shard-BRAINS GitHub organisation, MIT licensed

---

## 1. Purpose

A Claude Code skill that maintains the BRAINS research library — a curated, categorised corpus of PDFs covering AI, neurodiversity, ethics, mental health, and related domains. The skill runs the inbox-to-library pipeline (extract → dedupe → categorise → rename → file → append catalog) against a locked 10-category taxonomy, producing an append-only `_catalog.csv` that is the canonical record of what has been read and where it lives.

The skill exists because:

- The BRAINS Certified standard and the BRAINS Weekly Intelligence Brief both depend on a defensible evidence base. An ad-hoc folder of PDFs is not a defensible evidence base; a catalogued library with a locked taxonomy is.
- Manual filing of research is unreliable at scale. The corpus already exceeds 100 papers across ten categories, with new papers arriving weekly. Without automation, naming conventions drift, duplicates accumulate, and provenance is lost.
- The same library will later mirror to the BRAINS website as a public research base supporting the standard. Cataloguing now produces the metadata structure that the future publish step consumes.

## 2. Scope

### In scope for v1

1. **`/brains-research-process`** — the ingest pipeline. Empty-check, batch text extraction (first two pages), byte-exact dedupe against the existing corpus, categorisation against the locked 10-category taxonomy, rename to canonical form, move into the correct category folder, append a row to `_catalog.csv`.
2. **`/brains-research-status`** — a read-only summary. Total catalogued count, count by category, last N additions, inbox count, duplicates count, and a catalog integrity check (rows pointing to missing files, files under `Completed Review/` not in the catalog).
3. **Config-driven paths.** All filesystem locations are read from a per-machine `config.json` so the skill works against any Research root the user points it at, with the default set to the BRAINS share at `\\192.168.1.101\Singularity_Backup\Research`.
4. **Reference content as separate files.** The locked taxonomy, organisation abbreviations, filename rules, and edge-case handling live in `references/` and are loaded on demand by the slash commands, rather than inlined into the command body.
5. **Install scripts.** One-line installers for Windows (cmd + PowerShell) and macOS / Linux (bash) that scaffold `config.json` from the example, copy or symlink the skill into `~/.claude/skills/brains-research/`, and copy the slash commands into `~/.claude/commands/`.
6. **Public GitHub release.** Repo `shard-BRAINS/BRAINS-Research-Skill`, MIT licensed, README and SKILL.md modelled on the existing `BRAINS-resume-skill`.

### Out of scope for v1

- Website mirror — handled by a future companion skill (working name `brains-research-publish`) that consumes `_catalog.csv` and produces a website-ready manifest.
- Per-paper review, summarisation, or BRAINS-specific commentary on individual papers.
- Cross-paper synthesis (e.g. "what does the corpus say about X?").
- Auto-drafting of LinkedIn or Bluesky posts from new additions.
- OCR of scanned image-only PDFs (flagged for manual review instead).
- Live fetching of papers from arXiv, SSRN, journal portals.
- Catalog editing or correction tools (catalog is append-only; edits are explicit and manual).
- Sharing or syncing the library across multiple BRAINS team members.
- Web UI or dashboard.

### Decision ledger

| # | Decision | Choice | Rationale |
|---|---|---|---|
| 1 | Skill name | `brains-research` | Matches `brains-*` convention, broad enough to absorb future capabilities (search, publish, cross-reference) without rename |
| 2 | Scope of v1 | Cataloguer only | Ships fastest; website mirror becomes a separate skill that consumes the catalog |
| 3 | Path strategy | Skill-local `config.json` | Per-machine override without code edits; works for anyone who clones the repo |
| 4 | Repo location | `shard-BRAINS/BRAINS-Research-Skill` | Matches existing BRAINS skill pattern; public, MIT |
| 5 | Commands | Two: `/brains-research-process`, `/brains-research-status` | Process is the core workflow; status is the foundation for future publish work |
| 6 | Old `/process-research` command | Deprecated, redirect to new command | One canonical entry point per skill |
| 7 | Reference content | Split into `references/*.md` | Slash command stays short; Claude loads only what it needs per turn |
| 8 | Taxonomy | Code-side, not config | Categories are doctrine, not preference |
| 9 | Catalog mutability | Append-only | Audit trail integrity; corrections are explicit separate operations |
| 10 | Research data in repo | Excluded via `.gitignore` | Corpus is not source; lives only on the share; repo contains tooling only |
| 11 | Sample empty Research folder | Included for new installs | Lowers onboarding friction; skill is designed to grow with more capabilities |
| 12 | License | MIT | Matches BRAINS-resume-skill; permissive for community use |
| 13 | Visibility | Public | Tooling has no proprietary content; aligns with BRAINS open-source posture |

## 3. Architecture

### 3.1 Repo layout

```
BRAINS-Research-Skill/
├── SKILL.md                       Skill entry point and behavioural contract
├── README.md                      GitHub-facing project overview
├── LICENSE                        MIT
├── CHANGELOG.md
├── CONTRIBUTING.md
├── STATUS.yml                     Version, last-updated, supported platforms
├── config.json.example            Template copied to config.json on install
├── .gitignore                     Excludes config.json, research-data/, build artefacts
│
├── commands/
│   ├── brains-research-process.md   The ingest workflow
│   └── brains-research-status.md    The catalog summary
│
├── scripts/
│   ├── __init__.py
│   ├── config.py                    Loads config.json, validates paths
│   ├── extract_all.py               Batch text extraction → _extract_all.json
│   ├── extract_text.py              Single-file diagnostic
│   └── apply_renames.py             Reads _rename_plan.json, moves files, appends catalog
│
├── references/
│   ├── taxonomy.md                  The 10 locked categories with scope rules
│   ├── org-abbreviations.md         WHO, OECD, etc. — appendable list
│   ├── filename-rules.md            YYYY - Author - Title.pdf conventions
│   └── edge-cases.md                Scanned PDFs, collisions, non-PDFs, cross-cutting
│
├── research-data/                   Empty scaffold (only .gitkeep files committed; corpus excluded by .gitignore)
│   ├── to be reviwed/.gitkeep       (typo retained for path compatibility)
│   ├── Completed Review/.gitkeep
│   └── _duplicates/.gitkeep
│
├── install/
│   ├── install.cmd                  Windows cmd entry
│   ├── install.ps1                  PowerShell installer
│   └── install.sh                   bash installer (macOS / Linux / WSL)
│
├── docs/
│   ├── specs/                       Design specifications (this file)
│   └── plans/                       Implementation plans
│
├── pyproject.toml
├── requirements.txt                 pypdf>=4.0
├── requirements-dev.txt             pytest, ruff
│
└── tests/
    ├── fixtures/                    Tiny sample PDFs and expected outputs
    ├── test_config.py
    ├── test_extract.py
    └── test_apply_renames.py
```

### 3.2 Key changes from the current ad-hoc scripts

- Scripts move from `_extract_all.py`-style root-level files to `scripts/extract_all.py` (proper Python package).
- Paths read from `config.json` rather than hardcoded module constants.
- Reference content (taxonomy, abbreviations, edge cases) extracted from the slash-command markdown into `references/*.md`, loaded on demand.
- Test fixtures and a pytest suite verify the extract and rename behaviour against known inputs.

### 3.3 Data not in the repo

All current Research content — `Completed Review/`, `_duplicates/`, `to be reviwed/`, `_catalog.csv`, `_rename_plan.json`, `_extract_all.json`, `MG_Backlog.md`, and every PDF — stays on the share at `\\192.168.1.101\Singularity_Backup\Research`. The repo contains only the skill code, references, install scripts, tests, and a `research-data/` scaffold of empty placeholder folders for new installs. `.gitignore` enforces this exclusion.

## 4. Config and path strategy

### 4.1 `config.json` schema

```json
{
  "research_root": "\\\\192.168.1.101\\Singularity_Backup\\Research",
  "inbox_dir": "to be reviwed",
  "completed_dir": "Completed Review",
  "duplicates_dir": "_duplicates",
  "catalog_csv": "_catalog.csv",
  "extract_pages": 2,
  "extract_max_chars": 3000
}
```

### 4.2 Behaviour

- `config.json.example` ships in the repo with the BRAINS-share default.
- Install scripts copy `config.json.example` → `config.json` and prompt the user to confirm or override `research_root`.
- `config.json` is `.gitignore`-listed — per-machine, never committed.
- `scripts/config.py` exposes `load_config()` which:
  - reads `config.json` from the skill root
  - resolves relative subdirectory names against `research_root`
  - validates that `research_root` exists and is readable
  - raises a clear error if missing keys or unreachable paths
- All other scripts import paths only from `config.py`. No module-level constants for filesystem locations.

### 4.3 Locked-in-code values

The 10-category taxonomy, the canonical filename format, the organisation-abbreviation seed list, and the edge-case rules are not config. They are doctrine and live in `references/` plus light coordination logic in the slash commands.

## 5. Commands

### 5.1 `/brains-research-process`

Functionally equivalent to the current `/process-research` command, with three changes:

1. Paths come from `config.json` rather than hardcoded.
2. Taxonomy, filename rules, organisation abbreviations, and edge-case handling are loaded from `references/*.md` on demand rather than inlined.
3. Steps reference `scripts/extract_all.py` and `scripts/apply_renames.py` (proper package paths).

Pipeline:

1. **Empty check.** If `inbox_dir` has no PDFs, report `No new files.` and stop.
2. **Extract.** Run `python -m scripts.extract_all`. Writes `_extract_all.json` to the Research root with `{filename: {size, text, pages, error}}` for every PDF in the inbox.
3. **Dedupe.** For each new file, compare byte size against every file already in `Completed Review/**`. Byte-exact match → move to `_duplicates/` and skip.
4. **Categorise.** Load `references/taxonomy.md`. Claude (not a script) reads `_extract_all.json` and for each non-duplicate file decides `year`, `author`, `title`, `category` (must be one of the ten), `doc_type`. Never invent a new category silently. If `_extract_all.json` is large (>25 KB), Claude splits it into chunks of approximately 18 entries and processes them sequentially.
5. **Build filenames.** Load `references/filename-rules.md`. Canonical form is `YYYY - ShortAuthor - Descriptive title.pdf`.
6. **Write `_rename_plan.json`.** At the Research root, overwriting any prior plan.
7. **Apply.** Run `python -m scripts.apply_renames`. Moves files and appends to `_catalog.csv`.
8. **Report back.** Concise summary: N moved by category, N quarantined as duplicates (with names), any files where extraction failed or year / author was uncertain.

### 5.2 `/brains-research-status`

A read-only summary. Reads `_catalog.csv`, walks `Completed Review/`, and reports:

- Total catalogued count
- Count by category (matched against the locked 10)
- Last N additions (default N = 10), with the date filed
- Inbox count (anything in `to be reviwed/`)
- Duplicates folder count
- **Catalog integrity check:**
  - Catalog rows whose `new_path` no longer exists on disk
  - Files under `Completed Review/` not present in the catalog

This command never writes. It is safe to run any time and forms the foundation for the future `brains-research-publish` skill (which consumes catalog integrity + new additions to drive the website mirror).

## 6. SKILL.md behavioural contract

Same shape as `BRAINS-resume-skill`'s SKILL.md. Key clauses:

- **Locked taxonomy.** Never silently add a category. If a paper genuinely does not fit one of the ten, surface it and ask the user. The taxonomy lives in `references/taxonomy.md` and is canonical.
- **Locked dedupe rule.** Byte-exact match against `Completed Review/**` is the only dedupe signal. No fuzzy-match, no near-duplicate inference. False negatives are acceptable; false positives are not.
- **Append-only catalog.** `_catalog.csv` is never rewritten. Corrections to past entries are out of scope for v1 and must be done manually.
- **No silent renames.** A file already in `Completed Review/` is not renamed by this skill. If the user wants to rename, that is a separate explicit task.
- **Brand-aware tone.** Status reports and error messages are plain and direct. Identity-first language by default. No deficit framing of neurodivergence in any reference, command, or output.
- **Air-gap awareness.** The library backs BRAINS Certified evidence. This skill never reveals, summarises, or speculates on BRAINS scoring criteria, calibration vignettes, or rubric mechanics from within the papers it catalogues. That concern is handled by `brains-weekly-intel`.
- **Confirm before destructive moves.** The pipeline reports its plan before applying it. The user can request a dry run.

## 7. Migration and install

### 7.1 Migration of the existing corpus

The existing 102 catalogued entries on the share are the source of truth. They are not touched during migration. Specifically:

- `_catalog.csv` is not rewritten.
- Files under `Completed Review/` are not renamed.
- `_duplicates/` is not touched.
- `to be reviwed/` is processed by the new pipeline once it ships, identically to how `/process-research` would process it.

Migration steps:

1. Update the three existing scripts on the share **in place first** — make them config-driven against the new UNC root. Verifies the rewrite works against the real corpus before anything ships to GitHub.
2. Run a dry-run of the new pipeline against the current three PDFs in `to be reviwed/` to confirm parity.
3. Copy the working scripts into the new skill repo and continue development from there.
4. Deprecate the old `/process-research` slash command (rename to `_process-research.md.deprecated` or delete after the new flow is confirmed working).

### 7.2 Install (post GitHub push)

```
git clone https://github.com/shard-BRAINS/BRAINS-Research-Skill.git c:\Brains_Research_Skill
cd c:\Brains_Research_Skill
.\install\install.ps1
```

The PowerShell installer:

1. Copies `config.json.example` → `config.json` if `config.json` does not exist.
2. Prompts the user to confirm or override `research_root` (default: the BRAINS share UNC path).
3. Validates that `research_root` exists.
4. Copies or symlinks the skill bundle into `~/.claude/skills/brains-research/`.
5. Copies the two `commands/*.md` files into `~/.claude/commands/`.
6. Creates a `.venv`, installs `requirements.txt`.
7. Prints next-step instructions.

Equivalent `install.cmd` and `install.sh` ship for Windows cmd and macOS / Linux respectively.

## 8. Future roadmap

Out of scope for v1, but the architecture leaves room for:

- **`brains-research-publish`** — consumes `_catalog.csv` and a per-paper abstract field to produce a website-ready manifest (catalog.json) plus optional metadata-only mirror.
- **`/brains-research-find`** — semantic or keyword search across the catalogued corpus.
- **`/brains-research-summarise`** — generate a structured summary of a single paper, with neuro-affirming framing and an optional draft BRAINS LinkedIn or Bluesky post for the user to review.
- **`/brains-research-synthesise`** — cross-paper synthesis on a user-supplied topic, returning citations from the catalogued corpus only.
- **Per-paper review tags** — add a `review_status` column (read / skimmed / pending) and a `notes_path` column linking to user notes.
- **Multi-user sync** — share the corpus across BRAINS team members.

These are intentionally not v1 work.

## 9. Acceptance criteria for v1

1. Repo `shard-BRAINS/BRAINS-Research-Skill` exists, public, MIT licensed.
2. README is brand-compliant and modelled on `BRAINS-resume-skill`'s README.
3. `install.ps1` runs cleanly on Matthew's Windows machine, produces a working `config.json` and registers both slash commands.
4. `/brains-research-process` against the current inbox produces the same outcome as the existing `/process-research` (three PDFs catalogued into the correct categories, `_catalog.csv` extended by three rows).
5. `/brains-research-status` against the current corpus reports the correct count (102 existing rows pre-migration, 105 post) and zero integrity violations.
6. `pytest` passes against the bundled test fixtures.
7. The existing share is untouched apart from the in-place script update plus normal inbox processing.
8. No corpus data is committed to the repo.
