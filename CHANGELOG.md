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
- Test suite (`pytest`) covering config, extraction, rename application, and status reporting.
