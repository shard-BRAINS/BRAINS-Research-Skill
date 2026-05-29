# Changelog

All notable changes to BRAINS Research Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
