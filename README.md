# BRAINS Research Skill

A Claude Code skill that maintains the BRAINS research library — a curated, categorised corpus of PDFs covering AI, neurodiversity, ethics, mental health, and related domains. Runs the inbox-to-library pipeline (extract → dedupe → categorise → rename → file → append catalog) against a locked 10-category taxonomy.

**An Incubator project from BRAINS — built by neurodivergent minds, for neurodivergent people.**

---

## Status

v1.0.0 — initial release. Two slash commands: `/brains-research-process` (ingest) and `/brains-research-status` (read-only summary).

---

## What it does

- **`/brains-research-process`** — full ingest workflow. Drops new PDFs into the inbox, runs extract → dedupe → categorise → rename → file, appends one row per paper to `_catalog.csv`. **(live)**
- **`/brains-research-status`** — read-only summary: total catalogued, count by category, recent additions, inbox and duplicate counts, plus an integrity check (catalog rows pointing at missing files; files on disk not in the catalog). **(live)**

---

## Install

### One-line installers (recommended)

**Windows (Command Prompt or PowerShell):**
```
.\install\install.cmd
```

This wrapper handles PowerShell's default execution policy automatically — no system setting changed. If you would rather invoke PowerShell directly:

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install.ps1
```

**macOS / Linux:**
```bash
bash install/install.sh
```

### Manual install

```bash
# 1. Clone
git clone https://github.com/shard-BRAINS/BRAINS-Research-Skill.git
cd BRAINS-Research-Skill

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
#    Windows:
.venv\Scripts\activate
#    macOS / Linux:
source .venv/bin/activate

# 4. Install
pip install -e ".[dev]"

# 5. Copy config.json.example to config.json and edit research_root
cp config.json.example config.json
```

Install the skill bundle for Claude Code — copy or symlink:

```bash
# Copy
cp -r . ~/.claude/skills/brains-research/

# Symlink (edits take effect immediately)
ln -s "$(pwd)" ~/.claude/skills/brains-research

# Copy the slash commands into ~/.claude/commands/
cp commands/brains-research-process.md ~/.claude/commands/
cp commands/brains-research-status.md ~/.claude/commands/
```

---

## Configuration

Edit `config.json` to point `research_root` at your Research folder. The default targets the BRAINS share at `\\192.168.1.101\Singularity_Backup\Research`. All other paths are resolved relative to `research_root`.

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

---

## The locked taxonomy

See `references/taxonomy.md`. The ten categories are doctrine — not configuration. The skill will refuse to silently invent a new category; it asks the user first.

---

## Run the tests

```bash
pytest
```

---

## Licence

MIT. See `LICENSE`.
