# Changelog

All notable changes to BRAINS Research Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-05-29

### Added
- `/brains-research-review` slash command — per-paper review workflow producing an objective summary, an analytical review, BRAINS commentary, and optional LinkedIn and Bluesky drafts handed off to `brains-content`.
- `scripts/extract_full.py` — full-text PDF extraction with per-paper JSON cache, mtime-invalidated.
- `scripts/review.py` — paper selection (filename / partial / category / picker), `_reviews.csv` append-only ledger I/O, `.review.md` writer, content-draft handoff.
- `references/review-template.md`, `references/linkedin-template.md`, `references/bluesky-template.md` — section guides loaded on demand during the review flow.
- Optional `content_drafts_dir` config key (defaults to Matthew's BRAINS content folder). The review command writes `CT00X.md` drafts and appends to `content_calendar.csv`. If the directory is unreachable, the review still completes; only the draft handoff is skipped.
- `_reviews.csv` ledger on the share, 13 columns: `new_path, category, paper_year, paper_author, paper_title, review_path, review_date, focus_criteria, linkedin_draft_id, bluesky_draft_id, bias_flags, tags, next_action`. Append-only.
- Stub `.review.md` + `bias_flags=scanned_pdf` row for scanned image-only PDFs — leaves an audit trail.
- Test fixtures and test files (`tests/test_extract_full.py`, `tests/test_review.py`, two new `test_config.py` cases). New `reportlab` dev dependency for generating the multi-page fixture PDF. 43/43 tests passing.

### Changed
- `scripts/config.py` — `Config` dataclass gains optional `content_drafts_dir: Path | None`.

### Migration notes
- v1.0.0 users upgrade by `git pull` and re-running `install.ps1` (or platform equivalent).
- Existing `_catalog.csv` and v1.0.0 commands are untouched.

## [1.0.0] — 2026-05-29

### Added
- `scripts/config.py` — per-machine `config.json` loader with path validation.
- `scripts/extract_text.py` — single-file PDF text extractor.
- `scripts/extract_all.py` — batch extraction to `_extract_all.json`.
- `scripts/apply_renames.py` — applies `_rename_plan.json`, moves files, appends `_catalog.csv` (with `--dry-run`).
- `scripts/status.py` — read-only catalog summary and integrity check.
- `references/taxonomy.md`, `references/filename-rules.md`, `references/org-abbreviations.md`, `references/edge-cases.md` — canonical rule sets.
- `/brains-research-process` and `/brains-research-status` slash commands.
- `SKILL.md` behavioural contract.
- One-line installers for Windows (cmd + PowerShell) and macOS / Linux (bash).
- Test suite (`pytest`) covering config, extraction, rename application, and status reporting (21/21 passing, including UTF-8 BOM tolerance for PowerShell-written config.json).

### Migration notes
- The previous `/process-research` slash command (hardcoded to a OneDrive path) has been deprecated. Use `/brains-research-process` from the installed `brains-research` skill instead.
- The three Python scripts on the share at `\\192.168.1.101\Singularity_Backup\Research` (`_extract_all.py`, `_extract_text.py`, `_apply_renames.py`) had their `ROOT` constants patched in place to point at the UNC path. Pre-migration backups stored under `_backup/`.

### End-to-end verification
- Installer runs cleanly on Windows 11 + PowerShell 5.1.
- `/brains-research-process` against the live inbox of 3 PDFs catalogued them into Neurodiversity-General, AI-Neurodiversity-Autism, and AI-Mental-Health respectively. `_catalog.csv` grew from 102 to 105 rows.
- `/brains-research-status` reports 105 catalogued, 0 inbox, 0 missing files, 0 orphans.
