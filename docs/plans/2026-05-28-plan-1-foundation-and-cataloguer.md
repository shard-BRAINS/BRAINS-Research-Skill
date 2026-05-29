# BRAINS Research Skill — Plan 1: Foundation and Cataloguer

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship v1 of `brains-research` — a public, MIT-licensed Claude Code skill on `shard-BRAINS/BRAINS-Research-Skill` that maintains the BRAINS research library via two slash commands (`/brains-research-process`, `/brains-research-status`) driven by per-machine `config.json`. Existing 102-row corpus on the share is preserved untouched.

**Architecture:** Build the config-driven Python package (`scripts/`) with full pytest coverage in a new local repo `c:\Brains_Research_Skill`. Extract the locked taxonomy, filename rules, organisation abbreviations, and edge-case handling into `references/*.md` files loaded on demand by the slash commands. Wrap as a Claude Code skill with one-line installers (cmd / PowerShell / bash) that scaffold `config.json` and register the commands. Patch the existing share scripts in place as a Phase 0 quick fix so the user has working cataloging against the new UNC path immediately. After the new skill is verified end-to-end, push to GitHub and deprecate the old `/process-research` slash command.

**Tech Stack:** Python 3.10+, `pypdf>=4.0`, `pytest`, Claude Code skill format (markdown + frontmatter), git, GitHub CLI (`gh`).

**Spec:** [c:\Brains_Research_Skill\docs\specs\2026-05-28-brains-research-skill-design.md](c:\Brains_Research_Skill\docs\specs\2026-05-28-brains-research-skill-design.md)

---

## File structure (decomposition lock-in)

| Path | Responsibility | Phase |
|---|---|---|
| `\\192.168.1.101\...\Research\_extract_all.py` | Existing — patch ROOT in place | A |
| `\\192.168.1.101\...\Research\_extract_text.py` | Existing — patch ROOT in place | A |
| `\\192.168.1.101\...\Research\_apply_renames.py` | Existing — patch ROOT in place | A |
| `c:\Brains_Research_Skill\.gitignore` | Excludes config.json, corpus, build artefacts | B |
| `c:\Brains_Research_Skill\LICENSE` | MIT | B |
| `c:\Brains_Research_Skill\pyproject.toml` | Package metadata, dev extras | B |
| `c:\Brains_Research_Skill\requirements.txt` | `pypdf>=4.0` | B |
| `c:\Brains_Research_Skill\requirements-dev.txt` | `pytest`, `ruff` | B |
| `c:\Brains_Research_Skill\config.json.example` | Template for per-machine config | B |
| `c:\Brains_Research_Skill\scripts\__init__.py` | Package marker | B |
| `c:\Brains_Research_Skill\scripts\config.py` | Loads + validates config.json | C |
| `c:\Brains_Research_Skill\scripts\extract_text.py` | First-N-pages extractor (single file) | D |
| `c:\Brains_Research_Skill\scripts\extract_all.py` | Batch extract → _extract_all.json | E |
| `c:\Brains_Research_Skill\scripts\apply_renames.py` | Plan → move → append catalog | F |
| `c:\Brains_Research_Skill\scripts\status.py` | Catalog summary + integrity check | G |
| `c:\Brains_Research_Skill\tests\fixtures\sample.pdf` | Tiny single-page PDF for tests | C |
| `c:\Brains_Research_Skill\tests\fixtures\research_root\` | Mock Research folder for integration tests | C |
| `c:\Brains_Research_Skill\tests\test_config.py` | Config loader tests | C |
| `c:\Brains_Research_Skill\tests\test_extract_text.py` | Extract-text tests | D |
| `c:\Brains_Research_Skill\tests\test_extract_all.py` | Extract-all tests | E |
| `c:\Brains_Research_Skill\tests\test_apply_renames.py` | Rename + dry-run tests | F |
| `c:\Brains_Research_Skill\tests\test_status.py` | Status + integrity tests | G |
| `c:\Brains_Research_Skill\references\taxonomy.md` | 10 locked categories + scope rules | H |
| `c:\Brains_Research_Skill\references\filename-rules.md` | YYYY - Author - Title.pdf rules | H |
| `c:\Brains_Research_Skill\references\org-abbreviations.md` | WHO, OECD, etc. (appendable) | H |
| `c:\Brains_Research_Skill\references\edge-cases.md` | Scanned PDFs, collisions, non-PDFs, cross-cutting | H |
| `c:\Brains_Research_Skill\commands\brains-research-process.md` | Ingest workflow command | I |
| `c:\Brains_Research_Skill\commands\brains-research-status.md` | Status command | I |
| `c:\Brains_Research_Skill\SKILL.md` | Skill entry + behavioural contract | J |
| `c:\Brains_Research_Skill\README.md` | GitHub-facing overview | K |
| `c:\Brains_Research_Skill\CHANGELOG.md` | Version history | K |
| `c:\Brains_Research_Skill\CONTRIBUTING.md` | Contributor guide | K |
| `c:\Brains_Research_Skill\STATUS.yml` | Version + supported platforms | K |
| `c:\Brains_Research_Skill\install\install.ps1` | PowerShell installer | L |
| `c:\Brains_Research_Skill\install\install.cmd` | Windows cmd wrapper | L |
| `c:\Brains_Research_Skill\install\install.sh` | bash installer | L |
| `c:\Brains_Research_Skill\research-data\` | Empty scaffold for new installs | L |
| `~/.claude/commands/process-research.md` | Existing — deprecate after verification | N |

---

## Phase A — Immediate fix (patch existing share scripts)

Goal: Get the user's current `/process-research` workflow working against the new UNC path within minutes, before any larger refactor. This is a defensive backup of the working state.

### Task A1: Back up the three existing scripts

**Files:**
- Read: `\\192.168.1.101\Singularity_Backup\Research\_extract_all.py`
- Read: `\\192.168.1.101\Singularity_Backup\Research\_extract_text.py`
- Read: `\\192.168.1.101\Singularity_Backup\Research\_apply_renames.py`
- Create: `\\192.168.1.101\Singularity_Backup\Research\_backup\_extract_all.py.pre-migration`
- Create: `\\192.168.1.101\Singularity_Backup\Research\_backup\_extract_text.py.pre-migration`
- Create: `\\192.168.1.101\Singularity_Backup\Research\_backup\_apply_renames.py.pre-migration`

- [ ] **Step 1: Create the backup folder and copy the three files**

Run (PowerShell):
```powershell
New-Item -ItemType Directory -Force -Path '\\192.168.1.101\Singularity_Backup\Research\_backup'
Copy-Item '\\192.168.1.101\Singularity_Backup\Research\_extract_all.py' '\\192.168.1.101\Singularity_Backup\Research\_backup\_extract_all.py.pre-migration'
Copy-Item '\\192.168.1.101\Singularity_Backup\Research\_extract_text.py' '\\192.168.1.101\Singularity_Backup\Research\_backup\_extract_text.py.pre-migration'
Copy-Item '\\192.168.1.101\Singularity_Backup\Research\_apply_renames.py' '\\192.168.1.101\Singularity_Backup\Research\_backup\_apply_renames.py.pre-migration'
```

Expected: three files exist under `_backup/` matching the originals byte-for-byte.

### Task A2: Patch `_extract_all.py` ROOT and OUT

**Files:**
- Modify: `\\192.168.1.101\Singularity_Backup\Research\_extract_all.py:16-17`

- [ ] **Step 1: Edit ROOT and OUT to use the UNC path**

Replace:
```python
ROOT = Path(r"C:\Users\matth\OneDrive\Documents\Atlas\Projects\Code\Research\to be reviwed")
OUT = Path(r"C:\Users\matth\OneDrive\Documents\Atlas\Projects\Code\Research\_extract_all.json")
```

With:
```python
ROOT = Path(r"\\192.168.1.101\Singularity_Backup\Research\to be reviwed")
OUT = Path(r"\\192.168.1.101\Singularity_Backup\Research\_extract_all.json")
```

### Task A3: Patch `_extract_text.py` ROOT

**Files:**
- Modify: `\\192.168.1.101\Singularity_Backup\Research\_extract_text.py:15`

- [ ] **Step 1: Edit ROOT to use the UNC path**

Replace:
```python
ROOT = Path(r"C:\Users\matth\OneDrive\Documents\Atlas\Projects\Code\Research\to be reviwed")
```

With:
```python
ROOT = Path(r"\\192.168.1.101\Singularity_Backup\Research\to be reviwed")
```

### Task A4: Patch `_apply_renames.py` ROOT

**Files:**
- Modify: `\\192.168.1.101\Singularity_Backup\Research\_apply_renames.py:12`

- [ ] **Step 1: Edit ROOT to use the UNC path**

Replace:
```python
ROOT = Path(r"C:\Users\matth\OneDrive\Documents\Atlas\Projects\Code\Research")
```

With:
```python
ROOT = Path(r"\\192.168.1.101\Singularity_Backup\Research")
```

### Task A5: Verify the patched scripts run

- [ ] **Step 1: Run `_extract_all.py` against the current inbox**

Run (PowerShell, from any working directory):
```powershell
python '\\192.168.1.101\Singularity_Backup\Research\_extract_all.py'
```

Expected: stderr reports `Found 3 PDFs` and `Wrote \\192.168.1.101\Singularity_Backup\Research\_extract_all.json`. The output JSON file exists at that path.

- [ ] **Step 2: Verify the JSON contains the three inbox PDFs**

Run (PowerShell):
```powershell
Get-Content '\\192.168.1.101\Singularity_Backup\Research\_extract_all.json' | python -c "import json,sys; d=json.load(sys.stdin); print(list(d.keys()))"
```

Expected: a list containing `2408.04500v2.pdf`, `A scoping review of inclusive and adaptive human AI interaction design for neurodivergent users.pdf`, `s41598-025-17242-4.pdf`.

- [ ] **Step 3: Run `_apply_renames.py --dry-run`**

Run (PowerShell):
```powershell
# This will only work if _rename_plan.json exists; if not, expected to fail with a clear "no plan" message.
python '\\192.168.1.101\Singularity_Backup\Research\_apply_renames.py' --dry-run
```

Expected: either prints "Plan: 0 entries" / "Will move: 0" if no plan exists, or reports the contents of an existing plan. Either is fine — we are only verifying the script loads against the new path.

Phase A complete — the user's existing workflow now works against the share. The proper skill build continues in the new repo.

---

## Phase B — Repo scaffold

Goal: Create the local skill repo skeleton, initialise git, commit the spec and skeleton in one initial commit.

### Task B1: Create the directory skeleton

**Files:**
- Create: `c:\Brains_Research_Skill\scripts\`
- Create: `c:\Brains_Research_Skill\tests\fixtures\`
- Create: `c:\Brains_Research_Skill\references\`
- Create: `c:\Brains_Research_Skill\commands\`
- Create: `c:\Brains_Research_Skill\install\`
- Create: `c:\Brains_Research_Skill\research-data\to be reviwed\`
- Create: `c:\Brains_Research_Skill\research-data\Completed Review\`
- Create: `c:\Brains_Research_Skill\research-data\_duplicates\`

(`docs\specs\` and `docs\plans\` already exist from the brainstorming + writing-plans steps.)

- [ ] **Step 1: Create all directories**

Run (PowerShell):
```powershell
$root = 'c:\Brains_Research_Skill'
foreach ($d in @('scripts','tests\fixtures','references','commands','install','research-data\to be reviwed','research-data\Completed Review','research-data\_duplicates')) {
  New-Item -ItemType Directory -Force -Path (Join-Path $root $d) | Out-Null
}
```

Expected: all directories exist.

### Task B2: Write `.gitignore`

**Files:**
- Create: `c:\Brains_Research_Skill\.gitignore`

- [ ] **Step 1: Write the .gitignore**

Content:
```gitignore
# Per-machine config
config.json

# Research corpus — never committed
research-data/to be reviwed/*
research-data/Completed Review/*
research-data/_duplicates/*
!research-data/to be reviwed/.gitkeep
!research-data/Completed Review/.gitkeep
!research-data/_duplicates/.gitkeep
_catalog.csv
_rename_plan.json
_extract_all.json
_backup/

# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.pytest_cache/
.ruff_cache/
dist/
build/

# IDE / OS
.vscode/
.idea/
.DS_Store
Thumbs.db
```

### Task B3: Add `.gitkeep` files to the empty research-data subfolders

**Files:**
- Create: `c:\Brains_Research_Skill\research-data\to be reviwed\.gitkeep`
- Create: `c:\Brains_Research_Skill\research-data\Completed Review\.gitkeep`
- Create: `c:\Brains_Research_Skill\research-data\_duplicates\.gitkeep`

- [ ] **Step 1: Create empty .gitkeep files**

Run (PowerShell):
```powershell
$root = 'c:\Brains_Research_Skill\research-data'
foreach ($d in @('to be reviwed','Completed Review','_duplicates')) {
  New-Item -ItemType File -Force -Path (Join-Path $root "$d\.gitkeep") | Out-Null
}
```

Expected: three empty `.gitkeep` files exist.

### Task B4: Write `LICENSE` (MIT)

**Files:**
- Create: `c:\Brains_Research_Skill\LICENSE`

- [ ] **Step 1: Write the MIT licence text**

Content:
```
MIT License

Copyright (c) 2026 BRAINS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Task B5: Write `pyproject.toml`

**Files:**
- Create: `c:\Brains_Research_Skill\pyproject.toml`

- [ ] **Step 1: Write the pyproject.toml**

Content:
```toml
[project]
name = "brains-research"
version = "1.0.0"
description = "Catalogue PDFs into the BRAINS research library — Claude Code skill"
readme = "README.md"
requires-python = ">=3.10"
license = { file = "LICENSE" }
authors = [{ name = "BRAINS" }]
dependencies = [
    "pypdf>=4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.4",
]

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["scripts"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 100
target-version = "py310"
```

### Task B6: Write `requirements.txt` and `requirements-dev.txt`

**Files:**
- Create: `c:\Brains_Research_Skill\requirements.txt`
- Create: `c:\Brains_Research_Skill\requirements-dev.txt`

- [ ] **Step 1: Write requirements.txt**

Content:
```
pypdf>=4.0
```

- [ ] **Step 2: Write requirements-dev.txt**

Content:
```
-r requirements.txt
pytest>=7.0
ruff>=0.4
```

### Task B7: Write `config.json.example`

**Files:**
- Create: `c:\Brains_Research_Skill\config.json.example`

- [ ] **Step 1: Write the example config**

Content:
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

### Task B8: Create the `scripts/__init__.py` and `tests/__init__.py`

**Files:**
- Create: `c:\Brains_Research_Skill\scripts\__init__.py`
- Create: `c:\Brains_Research_Skill\tests\__init__.py`

- [ ] **Step 1: Write `scripts/__init__.py`**

Content:
```python
"""BRAINS Research Skill — cataloguing scripts."""
__version__ = "1.0.0"
```

- [ ] **Step 2: Write `tests/__init__.py`**

Content (empty file is fine; create it explicitly so pytest discovery is reliable):
```python
```

### Task B9: Initialise git and create an initial commit

- [ ] **Step 1: Initialise the repo**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' init -b main
```

Expected: `Initialized empty Git repository in c:/Brains_Research_Skill/.git/`.

- [ ] **Step 2: Stage everything created so far**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add .gitignore LICENSE pyproject.toml requirements.txt requirements-dev.txt config.json.example scripts/__init__.py tests/__init__.py docs/specs/2026-05-28-brains-research-skill-design.md docs/plans/2026-05-28-plan-1-foundation-and-cataloguer.md research-data/
```

- [ ] **Step 3: Initial commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' commit -m "Initial repo scaffold: spec, plan, licence, packaging, gitignore"
```

Expected: commit created on `main`. `git log --oneline` shows one commit.

### Task B10: Create the Python virtualenv and install dev dependencies

- [ ] **Step 1: Create the venv**

Run:
```powershell
python -m venv 'c:\Brains_Research_Skill\.venv'
```

- [ ] **Step 2: Install the package with dev extras**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pip install --upgrade pip
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pip install -e 'c:\Brains_Research_Skill[dev]'
```

Expected: install succeeds. `pip list` includes `pypdf`, `pytest`, `ruff`, and `brains-research` (editable install).

- [ ] **Step 3: Smoke-check pytest discovery**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest 'c:\Brains_Research_Skill' --collect-only -q
```

Expected: `no tests ran` (or similar) — pytest works, just nothing to collect yet.

---

## Phase C — `scripts/config.py` (TDD)

Goal: Per-machine `config.json` loader with path resolution and validation.

### Task C1: Add a tiny PDF fixture for downstream tests

**Files:**
- Create: `c:\Brains_Research_Skill\tests\fixtures\sample.pdf`
- Create: `c:\Brains_Research_Skill\tests\conftest.py`

- [ ] **Step 1: Generate a tiny single-page PDF programmatically**

Run (PowerShell, one-off — produces the fixture):
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -c @"
from pypdf import PdfWriter
from pypdf.generic import RectangleObject
w = PdfWriter()
w.add_blank_page(width=612, height=792)
with open(r'c:\Brains_Research_Skill\tests\fixtures\sample.pdf','wb') as f:
    w.write(f)
print('wrote sample.pdf')
"@
```

Expected: prints `wrote sample.pdf`. File exists and is a valid PDF (~1 KB).

- [ ] **Step 2: Write `tests/conftest.py` with a `mock_research_root` fixture**

Content:
```python
"""Shared pytest fixtures."""
import json
import shutil
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_PDF = FIXTURES / "sample.pdf"


@pytest.fixture
def mock_research_root(tmp_path):
    """A temporary Research root mirroring the production folder layout."""
    root = tmp_path / "Research"
    (root / "to be reviwed").mkdir(parents=True)
    (root / "Completed Review").mkdir(parents=True)
    (root / "_duplicates").mkdir(parents=True)
    return root


@pytest.fixture
def config_file(tmp_path, mock_research_root):
    """A config.json pointing at mock_research_root."""
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({
        "research_root": str(mock_research_root),
        "inbox_dir": "to be reviwed",
        "completed_dir": "Completed Review",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
    }))
    return cfg


@pytest.fixture
def sample_pdf_in_inbox(mock_research_root):
    """A copy of sample.pdf placed in the mock inbox."""
    dst = mock_research_root / "to be reviwed" / "sample.pdf"
    shutil.copy(SAMPLE_PDF, dst)
    return dst
```

### Task C2: Write the failing config tests

**Files:**
- Create: `c:\Brains_Research_Skill\tests\test_config.py`

- [ ] **Step 1: Write the tests**

Content:
```python
"""Tests for scripts.config."""
import json
from pathlib import Path

import pytest

from scripts.config import Config, load_config, ConfigError


def test_load_config_resolves_paths(config_file, mock_research_root):
    cfg = load_config(config_file)
    assert isinstance(cfg, Config)
    assert cfg.research_root == mock_research_root
    assert cfg.inbox_dir == mock_research_root / "to be reviwed"
    assert cfg.completed_dir == mock_research_root / "Completed Review"
    assert cfg.duplicates_dir == mock_research_root / "_duplicates"
    assert cfg.catalog_csv == mock_research_root / "_catalog.csv"
    assert cfg.extract_pages == 2
    assert cfg.extract_max_chars == 3000


def test_load_config_missing_file_raises(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nonexistent.json")


def test_load_config_missing_required_key_raises(tmp_path):
    bad = tmp_path / "config.json"
    bad.write_text(json.dumps({"inbox_dir": "to be reviwed"}))
    with pytest.raises(ConfigError, match="research_root"):
        load_config(bad)


def test_load_config_unreachable_root_raises(tmp_path):
    bad = tmp_path / "config.json"
    bad.write_text(json.dumps({
        "research_root": str(tmp_path / "does_not_exist"),
        "inbox_dir": "to be reviwed",
        "completed_dir": "Completed Review",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
    }))
    with pytest.raises(ConfigError, match="research_root"):
        load_config(bad)


def test_load_config_default_location(monkeypatch, tmp_path, mock_research_root):
    """If no path passed, looks for config.json next to the repo root."""
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps({
        "research_root": str(mock_research_root),
        "inbox_dir": "to be reviwed",
        "completed_dir": "Completed Review",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
    }))
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(cfg_path))
    cfg = load_config()
    assert cfg.research_root == mock_research_root
```

- [ ] **Step 2: Run tests to confirm they fail**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_config.py -v
```
*(run from `c:\Brains_Research_Skill`)*

Expected: all 5 tests fail with `ImportError` / `ModuleNotFoundError` on `scripts.config`.

### Task C3: Implement `scripts/config.py`

**Files:**
- Create: `c:\Brains_Research_Skill\scripts\config.py`

- [ ] **Step 1: Write the module**

Content:
```python
"""Per-machine config loader for the BRAINS Research skill."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

REQUIRED_KEYS = (
    "research_root", "inbox_dir", "completed_dir",
    "duplicates_dir", "catalog_csv", "extract_pages", "extract_max_chars",
)


class ConfigError(Exception):
    """Raised when config.json is missing, malformed, or points at unreachable paths."""


@dataclass(frozen=True)
class Config:
    research_root: Path
    inbox_dir: Path
    completed_dir: Path
    duplicates_dir: Path
    catalog_csv: Path
    extract_pages: int
    extract_max_chars: int


def _default_config_path() -> Path:
    env = os.environ.get("BRAINS_RESEARCH_CONFIG")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "config.json"


def load_config(path: Path | None = None) -> Config:
    cfg_path = Path(path) if path else _default_config_path()
    if not cfg_path.exists():
        raise ConfigError(f"config.json not found at {cfg_path}")
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigError(f"config.json malformed: {e}") from e

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise ConfigError(f"config.json missing keys: {', '.join(missing)}")

    research_root = Path(data["research_root"])
    if not research_root.exists():
        raise ConfigError(f"research_root does not exist: {research_root}")

    return Config(
        research_root=research_root,
        inbox_dir=research_root / data["inbox_dir"],
        completed_dir=research_root / data["completed_dir"],
        duplicates_dir=research_root / data["duplicates_dir"],
        catalog_csv=research_root / data["catalog_csv"],
        extract_pages=int(data["extract_pages"]),
        extract_max_chars=int(data["extract_max_chars"]),
    )
```

- [ ] **Step 2: Run tests, expect all pass**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_config.py -v
```

Expected: 5 passed.

- [ ] **Step 3: Commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add tests/conftest.py tests/fixtures/sample.pdf tests/test_config.py scripts/config.py
git -C 'c:\Brains_Research_Skill' commit -m "Add scripts/config.py with tests"
```

---

## Phase D — `scripts/extract_text.py` (TDD)

Goal: Single-file PDF text extractor, refactored from the original `_extract_text.py`.

### Task D1: Write the failing test

**Files:**
- Create: `c:\Brains_Research_Skill\tests\test_extract_text.py`

- [ ] **Step 1: Write tests**

Content:
```python
"""Tests for scripts.extract_text."""
from scripts.extract_text import extract


def test_extract_returns_string_for_valid_pdf(sample_pdf_in_inbox):
    result = extract(sample_pdf_in_inbox, pages=1, max_chars=3000)
    assert isinstance(result, str)


def test_extract_truncates_to_max_chars(sample_pdf_in_inbox):
    result = extract(sample_pdf_in_inbox, pages=1, max_chars=10)
    assert len(result) <= 10


def test_extract_missing_file_returns_error_string(tmp_path):
    result = extract(tmp_path / "nope.pdf", pages=1, max_chars=3000)
    assert result.startswith("[ERROR")
```

- [ ] **Step 2: Run, confirm fail**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_extract_text.py -v
```

Expected: all fail with `ModuleNotFoundError`.

### Task D2: Implement `scripts/extract_text.py`

**Files:**
- Create: `c:\Brains_Research_Skill\scripts\extract_text.py`

- [ ] **Step 1: Write the module**

Content:
```python
"""Extract first N pages of text from a PDF."""
from __future__ import annotations

import io
import logging
import sys
import warnings
from pathlib import Path

logging.getLogger("pypdf").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

from pypdf import PdfReader  # noqa: E402

from scripts.config import load_config  # noqa: E402


def extract(pdf_path: Path, pages: int, max_chars: int) -> str:
    try:
        reader = PdfReader(str(pdf_path))
        n = min(pages, len(reader.pages))
        parts = []
        for i in range(n):
            try:
                parts.append(reader.pages[i].extract_text() or "")
            except Exception as e:
                parts.append(f"[page {i} error: {e}]")
        return ("\n".join(parts).strip())[:max_chars]
    except Exception as e:
        return f"[ERROR: {e}]"


def main(argv: list[str] | None = None) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    cfg = load_config()
    argv = argv if argv is not None else sys.argv[1:]
    files = argv if argv else [p.name for p in cfg.inbox_dir.glob("*.pdf")]
    for fname in files:
        path = cfg.inbox_dir / fname
        print(f"=== {fname} ===")
        print(extract(path, pages=cfg.extract_pages, max_chars=cfg.extract_max_chars))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run, expect pass**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_extract_text.py -v
```

Expected: 3 passed.

- [ ] **Step 3: Commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add scripts/extract_text.py tests/test_extract_text.py
git -C 'c:\Brains_Research_Skill' commit -m "Add scripts/extract_text.py with tests"
```

---

## Phase E — `scripts/extract_all.py` (TDD)

Goal: Batch extract every inbox PDF to `_extract_all.json`.

### Task E1: Write the failing test

**Files:**
- Create: `c:\Brains_Research_Skill\tests\test_extract_all.py`

- [ ] **Step 1: Write tests**

Content:
```python
"""Tests for scripts.extract_all."""
import json
import shutil

import pytest

from scripts.extract_all import build_extract_dict, write_extracts


def test_build_extract_dict_handles_empty_inbox(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    result = build_extract_dict()
    assert result == {}


def test_build_extract_dict_processes_inbox_pdfs(
    mock_research_root, config_file, sample_pdf_in_inbox, monkeypatch
):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    result = build_extract_dict()
    assert "sample.pdf" in result
    entry = result["sample.pdf"]
    assert "size" in entry
    assert "text" in entry
    assert "pages" in entry
    assert "error" in entry
    assert entry["size"] > 0


def test_write_extracts_writes_json_to_research_root(
    mock_research_root, config_file, sample_pdf_in_inbox, monkeypatch
):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    write_extracts()
    out = mock_research_root / "_extract_all.json"
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert "sample.pdf" in data
```

- [ ] **Step 2: Run, expect fail**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_extract_all.py -v
```

Expected: 3 fail with ImportError.

### Task E2: Implement `scripts/extract_all.py`

**Files:**
- Create: `c:\Brains_Research_Skill\scripts\extract_all.py`

- [ ] **Step 1: Write the module**

Content:
```python
"""Extract first N pages of text from every PDF in the inbox, write to JSON."""
from __future__ import annotations

import io
import json
import logging
import sys
import warnings
from pathlib import Path

logging.getLogger("pypdf").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

from pypdf import PdfReader  # noqa: E402

from scripts.config import load_config  # noqa: E402


def _extract_one(pdf_path: Path, pages: int, max_chars: int) -> dict:
    info = {"size": pdf_path.stat().st_size, "text": "", "pages": 0, "error": None}
    try:
        reader = PdfReader(str(pdf_path))
        info["pages"] = len(reader.pages)
        n = min(pages, len(reader.pages))
        parts = []
        for i in range(n):
            try:
                parts.append(reader.pages[i].extract_text() or "")
            except Exception as e:
                parts.append(f"[page {i} error: {e}]")
        info["text"] = ("\n".join(parts).strip())[:max_chars]
    except Exception as e:
        info["error"] = str(e)
    return info


def build_extract_dict() -> dict:
    cfg = load_config()
    files = sorted(cfg.inbox_dir.glob("*.pdf"))
    return {
        p.name: _extract_one(p, cfg.extract_pages, cfg.extract_max_chars)
        for p in files
    }


def write_extracts() -> Path:
    cfg = load_config()
    data = build_extract_dict()
    out = cfg.research_root / "_extract_all.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    out = write_extracts()
    data = json.loads(out.read_text(encoding="utf-8"))
    print(f"Found {len(data)} PDFs", file=sys.stderr)
    print(f"Wrote {out}", file=sys.stderr)
    print(f"Total: {len(data)} entries, {out.stat().st_size:,} bytes", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run, expect pass**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_extract_all.py -v
```

Expected: 3 passed.

- [ ] **Step 3: Commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add scripts/extract_all.py tests/test_extract_all.py
git -C 'c:\Brains_Research_Skill' commit -m "Add scripts/extract_all.py with tests"
```

---

## Phase F — `scripts/apply_renames.py` (TDD)

Goal: Apply a rename plan — move files into category folders, append rows to `_catalog.csv`. Dry-run supported.

### Task F1: Write the failing tests

**Files:**
- Create: `c:\Brains_Research_Skill\tests\test_apply_renames.py`

- [ ] **Step 1: Write tests**

Content:
```python
"""Tests for scripts.apply_renames."""
import csv
import json

import pytest

from scripts.apply_renames import apply_plan


def _write_plan(root, entries):
    plan_path = root / "_rename_plan.json"
    plan_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return plan_path


def test_apply_plan_moves_file_and_writes_catalog(
    mock_research_root, config_file, sample_pdf_in_inbox, monkeypatch
):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _write_plan(mock_research_root, {
        "sample.pdf": {
            "category": "AI-General",
            "new_name": "2026 - Test - Sample paper.pdf",
            "year": "2026",
            "author": "Test",
            "title": "Sample paper",
            "doc_type": "Test fixture",
        }
    })
    result = apply_plan(dry_run=False)
    assert result["moved"] == 1
    assert result["missing"] == []
    assert result["skipped"] == []
    target = mock_research_root / "Completed Review" / "AI-General" / "2026 - Test - Sample paper.pdf"
    assert target.exists()
    assert not sample_pdf_in_inbox.exists()
    catalog = mock_research_root / "_catalog.csv"
    assert catalog.exists()
    rows = list(csv.DictReader(catalog.open(encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["category"] == "AI-General"
    assert rows[0]["new_filename"] == "2026 - Test - Sample paper.pdf"


def test_apply_plan_dry_run_does_not_move(
    mock_research_root, config_file, sample_pdf_in_inbox, monkeypatch
):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _write_plan(mock_research_root, {
        "sample.pdf": {
            "category": "AI-General",
            "new_name": "2026 - Test - Sample paper.pdf",
            "year": "2026",
            "author": "Test",
            "title": "Sample paper",
            "doc_type": "Test fixture",
        }
    })
    result = apply_plan(dry_run=True)
    assert result["moved"] == 0
    assert result["would_move"] == 1
    assert sample_pdf_in_inbox.exists()
    assert not (mock_research_root / "_catalog.csv").exists()


def test_apply_plan_reports_missing_sources(
    mock_research_root, config_file, monkeypatch
):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _write_plan(mock_research_root, {
        "ghost.pdf": {
            "category": "AI-General",
            "new_name": "2026 - Ghost - Missing file.pdf",
            "year": "2026",
            "author": "Ghost",
            "title": "Missing file",
            "doc_type": "Test fixture",
        }
    })
    result = apply_plan(dry_run=False)
    assert result["missing"] == ["ghost.pdf"]
    assert result["moved"] == 0


def test_apply_plan_skips_existing_targets(
    mock_research_root, config_file, sample_pdf_in_inbox, monkeypatch
):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    target_dir = mock_research_root / "Completed Review" / "AI-General"
    target_dir.mkdir(parents=True)
    (target_dir / "2026 - Test - Sample paper.pdf").write_text("existing")
    _write_plan(mock_research_root, {
        "sample.pdf": {
            "category": "AI-General",
            "new_name": "2026 - Test - Sample paper.pdf",
            "year": "2026",
            "author": "Test",
            "title": "Sample paper",
            "doc_type": "Test fixture",
        }
    })
    result = apply_plan(dry_run=False)
    assert result["moved"] == 0
    assert len(result["skipped"]) == 1
    assert sample_pdf_in_inbox.exists()  # not moved
```

- [ ] **Step 2: Run, expect fail**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_apply_renames.py -v
```

Expected: 4 fail with ImportError.

### Task F2: Implement `scripts/apply_renames.py`

**Files:**
- Create: `c:\Brains_Research_Skill\scripts\apply_renames.py`

- [ ] **Step 1: Write the module**

Content:
```python
"""Apply a rename plan: move PDFs into Completed Review/<Category>/ and append _catalog.csv."""
from __future__ import annotations

import csv
import io
import json
import shutil
import sys
from pathlib import Path

from scripts.config import load_config

FIELDNAMES = [
    "original_filename", "new_filename", "category", "year",
    "author", "title", "doc_type", "byte_size", "new_path",
]


def apply_plan(dry_run: bool = False) -> dict:
    cfg = load_config()
    plan_path = cfg.research_root / "_rename_plan.json"
    if not plan_path.exists():
        return {"moved": 0, "would_move": 0, "missing": [], "skipped": [], "no_plan": True}

    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    moves: list[tuple[Path, Path, dict]] = []
    missing: list[str] = []
    skipped: list[str] = []

    for orig, info in plan.items():
        src_path = cfg.inbox_dir / orig
        if not src_path.exists():
            missing.append(orig)
            continue
        dst_dir = cfg.completed_dir / info["category"]
        dst_path = dst_dir / info["new_name"]
        if dst_path.exists():
            skipped.append(f"{orig} -> {dst_path} (target exists)")
            continue
        moves.append((src_path, dst_path, info))

    if dry_run:
        return {
            "moved": 0,
            "would_move": len(moves),
            "missing": missing,
            "skipped": skipped,
        }

    catalog_exists = cfg.catalog_csv.exists()
    rows_to_append = []
    for src_path, dst_path, info in moves:
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        size = src_path.stat().st_size
        shutil.move(str(src_path), str(dst_path))
        rows_to_append.append({
            "original_filename": src_path.name,
            "new_filename": dst_path.name,
            "category": info["category"],
            "year": info["year"],
            "author": info["author"],
            "title": info["title"],
            "doc_type": info["doc_type"],
            "byte_size": size,
            "new_path": str(dst_path.relative_to(cfg.research_root)).replace("\\", "/"),
        })

    if rows_to_append:
        mode = "a" if catalog_exists else "w"
        with cfg.catalog_csv.open(mode, newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if not catalog_exists:
                writer.writeheader()
            writer.writerows(rows_to_append)

    return {
        "moved": len(rows_to_append),
        "would_move": 0,
        "missing": missing,
        "skipped": skipped,
    }


def main(argv: list[str] | None = None) -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    argv = argv if argv is not None else sys.argv[1:]
    dry = "--dry-run" in argv
    result = apply_plan(dry_run=dry)
    if result.get("no_plan"):
        print("No _rename_plan.json found. Run /brains-research-process first.")
        return 0
    print(f"Plan: {result['moved'] + result['would_move'] + len(result['missing']) + len(result['skipped'])} entries")
    if dry:
        print(f"Would move: {result['would_move']}")
    else:
        print(f"Moved: {result['moved']}")
    print(f"Missing source files: {len(result['missing'])}")
    print(f"Skipped (target exists): {len(result['skipped'])}")
    if result["missing"]:
        print("MISSING:", *result["missing"], sep="\n  ")
    if result["skipped"]:
        print("SKIPPED:", *result["skipped"], sep="\n  ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run, expect pass**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_apply_renames.py -v
```

Expected: 4 passed.

- [ ] **Step 3: Commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add scripts/apply_renames.py tests/test_apply_renames.py
git -C 'c:\Brains_Research_Skill' commit -m "Add scripts/apply_renames.py with tests"
```

---

## Phase G — `scripts/status.py` (TDD)

Goal: Read-only catalog summary + integrity check.

### Task G1: Write the failing tests

**Files:**
- Create: `c:\Brains_Research_Skill\tests\test_status.py`

- [ ] **Step 1: Write tests**

Content:
```python
"""Tests for scripts.status."""
import csv
import shutil

from scripts.status import status_report

TAXONOMY = [
    "AI-General", "AI-Ethics-Governance", "AI-Mental-Health",
    "AI-Neurodiversity-Autism", "AI-Education", "Neurodiversity-General",
    "Autism", "Suicide", "Mental-Health-General", "HCI-Cognitive-Theory",
]


def _seed_catalog(root, rows):
    catalog = root / "_catalog.csv"
    with catalog.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "original_filename","new_filename","category","year",
            "author","title","doc_type","byte_size","new_path",
        ])
        writer.writeheader()
        writer.writerows(rows)
    return catalog


def _place_file(root, relpath, content=b"x"):
    p = root / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    return p


def test_status_empty_corpus(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    report = status_report()
    assert report["total"] == 0
    assert report["by_category"] == {cat: 0 for cat in TAXONOMY}
    assert report["inbox_count"] == 0
    assert report["duplicates_count"] == 0
    assert report["missing_files"] == []
    assert report["orphan_files"] == []


def test_status_counts_catalog_and_categories(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _place_file(mock_research_root, "Completed Review/AI-General/a.pdf")
    _place_file(mock_research_root, "Completed Review/Autism/b.pdf")
    _seed_catalog(mock_research_root, [
        {"original_filename":"x.pdf","new_filename":"a.pdf","category":"AI-General",
         "year":"2024","author":"X","title":"a","doc_type":"Test",
         "byte_size":"1","new_path":"Completed Review/AI-General/a.pdf"},
        {"original_filename":"y.pdf","new_filename":"b.pdf","category":"Autism",
         "year":"2025","author":"Y","title":"b","doc_type":"Test",
         "byte_size":"1","new_path":"Completed Review/Autism/b.pdf"},
    ])
    report = status_report()
    assert report["total"] == 2
    assert report["by_category"]["AI-General"] == 1
    assert report["by_category"]["Autism"] == 1
    assert report["missing_files"] == []
    assert report["orphan_files"] == []


def test_status_detects_missing_files(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _seed_catalog(mock_research_root, [
        {"original_filename":"x.pdf","new_filename":"ghost.pdf","category":"AI-General",
         "year":"2024","author":"X","title":"ghost","doc_type":"Test",
         "byte_size":"1","new_path":"Completed Review/AI-General/ghost.pdf"},
    ])
    report = status_report()
    assert "Completed Review/AI-General/ghost.pdf" in report["missing_files"]


def test_status_detects_orphan_files(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _place_file(mock_research_root, "Completed Review/AI-General/orphan.pdf")
    _seed_catalog(mock_research_root, [])  # empty catalog
    report = status_report()
    assert any("orphan.pdf" in p for p in report["orphan_files"])


def test_status_inbox_and_duplicates_count(
    mock_research_root, config_file, sample_pdf_in_inbox, monkeypatch
):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _place_file(mock_research_root, "_duplicates/dup1.pdf")
    _place_file(mock_research_root, "_duplicates/dup2.pdf")
    report = status_report()
    assert report["inbox_count"] == 1
    assert report["duplicates_count"] == 2
```

- [ ] **Step 2: Run, expect fail**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_status.py -v
```

Expected: 5 fail with ImportError.

### Task G2: Implement `scripts/status.py`

**Files:**
- Create: `c:\Brains_Research_Skill\scripts\status.py`

- [ ] **Step 1: Write the module**

Content:
```python
"""Read-only catalog status + integrity report."""
from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

from scripts.config import load_config

TAXONOMY = [
    "AI-General", "AI-Ethics-Governance", "AI-Mental-Health",
    "AI-Neurodiversity-Autism", "AI-Education", "Neurodiversity-General",
    "Autism", "Suicide", "Mental-Health-General", "HCI-Cognitive-Theory",
]


def _load_catalog_rows(catalog: Path) -> list[dict]:
    if not catalog.exists():
        return []
    with catalog.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def status_report(recent_n: int = 10) -> dict:
    cfg = load_config()
    rows = _load_catalog_rows(cfg.catalog_csv)

    by_category = {cat: 0 for cat in TAXONOMY}
    for r in rows:
        cat = r.get("category", "")
        if cat in by_category:
            by_category[cat] += 1

    missing_files: list[str] = []
    catalog_paths: set[str] = set()
    for r in rows:
        rel = r.get("new_path", "")
        catalog_paths.add(rel)
        abs_path = cfg.research_root / rel
        if not abs_path.exists():
            missing_files.append(rel)

    orphan_files: list[str] = []
    if cfg.completed_dir.exists():
        for p in cfg.completed_dir.rglob("*.pdf"):
            rel = str(p.relative_to(cfg.research_root)).replace("\\", "/")
            if rel not in catalog_paths:
                orphan_files.append(rel)

    inbox_count = sum(1 for _ in cfg.inbox_dir.glob("*.pdf")) if cfg.inbox_dir.exists() else 0
    duplicates_count = (
        sum(1 for _ in cfg.duplicates_dir.glob("*.pdf"))
        if cfg.duplicates_dir.exists() else 0
    )

    recent = rows[-recent_n:] if rows else []

    return {
        "total": len(rows),
        "by_category": by_category,
        "inbox_count": inbox_count,
        "duplicates_count": duplicates_count,
        "missing_files": missing_files,
        "orphan_files": orphan_files,
        "recent": recent,
    }


def main() -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    report = status_report()
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run, expect pass**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest tests/test_status.py -v
```

Expected: 5 passed.

- [ ] **Step 3: Run full test suite**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m pytest -v
```

Expected: 20 passed (5 config + 3 extract_text + 3 extract_all + 4 apply_renames + 5 status).

- [ ] **Step 4: Commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add scripts/status.py tests/test_status.py
git -C 'c:\Brains_Research_Skill' commit -m "Add scripts/status.py with tests"
```

---

## Phase H — Reference files

Goal: Move the locked taxonomy, filename rules, organisation abbreviations, and edge-case handling out of the slash-command body into reusable reference files.

### Task H1: Write `references/taxonomy.md`

**Files:**
- Create: `c:\Brains_Research_Skill\references\taxonomy.md`

- [ ] **Step 1: Write the taxonomy**

Content:
```markdown
# Locked taxonomy — the 10 categories

Do NOT add new categories without explicit user approval.

| Category | Scope |
|---|---|
| `AI-General` | LLM theory, benchmarks, persona vectors, AI Index, hallucination, AGI |
| `AI-Ethics-Governance` | WHO, EU AI Act, OECD, UNESCO, hiring bias, data governance, source disclosure, fairness, accountability |
| `AI-Mental-Health` | LLMs as therapists, chatbots in MH, AI triage, AI for wellbeing, AI emotional support |
| `AI-Neurodiversity-Autism` | LLMs for ND / autistic users, ableism datasets, autism therapy LLMs, ND bias in AI |
| `AI-Education` | Generative AI in learning, K-12, STEM, educational transformation |
| `Neurodiversity-General` | ND theory, frameworks, occupational therapy, workforce, resilience, origins of the concept |
| `Autism` | Clinical, comorbidities, prevalence, employment, policy / strategy, ethics of advocacy |
| `Suicide` | Suicide mitigation, triage, online suicidal ideation, autism × suicidality |
| `Mental-Health-General` | Depression, social isolation, smartphone addiction, executive function, ADHD economics, crisis intervention |
| `HCI-Cognitive-Theory` | Cognitive Load Theory, Self-Determination Theory, Hawthorne effect, Technology Acceptance Model |

## Cross-cutting papers

If a paper sits across two categories (e.g. AI × autism × education): pick the dominant axis. When in doubt, prefer the more specific intersection (`AI-Neurodiversity-Autism` over `AI-Education` for a paper on LLMs for ND students).

## When a paper genuinely does not fit

Surface it to the user. Do not silently invent a new category. The user may decide to add a new category — at which point this file is updated and the change is committed.
```

### Task H2: Write `references/filename-rules.md`

**Files:**
- Create: `c:\Brains_Research_Skill\references\filename-rules.md`

- [ ] **Step 1: Write the filename rules**

Content:
```markdown
# Canonical filename format

`YYYY - ShortAuthor - Descriptive title.pdf`

## Components

- **YYYY** — four-digit publication year. If not derivable from the text, use `nd` (no date). Do not guess.
- **ShortAuthor** — first author surname. For institutional reports without a personal author, use an organisation abbreviation from `org-abbreviations.md`.
- **Descriptive title** — five to fifteen words, lowercase except proper nouns and acronyms. Do not repeat the year inside the title.

## Forbidden characters in the title

Strip: `: / \ * ? " < > |`

## Examples

- `2024 - Jain - Source awareness alters perceptions of AI mental health responses.pdf`
- `2025 - Rizvi - Beyond keywords evaluating LLM classification of nuanced ableism.pdf`
- `2023 - WHO - Guidance on regulatory considerations for AI for health.pdf`
- `nd - PennState - Workforce inclusion brief.pdf`

## Collision handling

If a target filename already exists in the destination category folder, append ` (v2).pdf`, ` (v3).pdf` etc. The apply step reports collisions; it does not overwrite.
```

### Task H3: Write `references/org-abbreviations.md`

**Files:**
- Create: `c:\Brains_Research_Skill\references\org-abbreviations.md`

- [ ] **Step 1: Write the seed list**

Content:
```markdown
# Organisation abbreviations (institutional reports)

When the first author is an organisation rather than a person, use one of these abbreviations as `ShortAuthor`. Add new ones as you encounter them and report the addition to the user — the addition is a committed change to this file.

| Abbreviation | Full name |
|---|---|
| `WHO` | World Health Organization |
| `OECD` | Organisation for Economic Co-operation and Development |
| `UNESCO` | United Nations Educational, Scientific and Cultural Organization |
| `EU` | European Union |
| `Stanford-HAI` | Stanford Institute for Human-Centered Artificial Intelligence |
| `McKinsey` | McKinsey & Company |
| `Deloitte` | Deloitte |
| `AU-DSS` | Australian Department of Social Services |
| `UK-Govt` | United Kingdom Government |
| `WEF` | World Economic Forum |
| `UNICEF-WHO` | UNICEF and WHO joint report |
| `Lancet-GBD` | The Lancet — Global Burden of Disease |
| `BRAINS` | BRAINS |
| `PennState` | Pennsylvania State University |
```

### Task H4: Write `references/edge-cases.md`

**Files:**
- Create: `c:\Brains_Research_Skill\references\edge-cases.md`

- [ ] **Step 1: Write the edge case handling**

Content:
```markdown
# Edge cases

## Scanned or image-only PDFs (empty text extraction)

If `_extract_all.json` shows an empty `text` field for a file, do not guess at the title. Use:

- `year` — `nd`
- `author` — derived from filename if possible, otherwise the literal string `Unknown`
- `title` — taken from the original filename (cleaned), prefixed with `(text extraction failed - manual review needed)`
- `doc_type` — `Scanned PDF (manual review needed)`

Surface every such file to the user at the end of the run.

## Filename collisions in the destination

If `Completed Review/<Category>/<new_name>` already exists, `apply_renames.py` skips the move and reports the collision. Resolution is manual.

## Non-PDF files in the inbox

`.htm`, `.docx`, `.txt`, etc. are left in place. This skill only processes PDFs. Mention them in the report.

## Cross-cutting papers

See `taxonomy.md`. Pick the dominant axis.

## Byte-exact duplicates

If a new file matches an existing file in `Completed Review/**` by byte size, it is moved to `_duplicates/`. No fuzzy matching. False negatives are acceptable; false positives are not.

## Catalog repair

If the status report shows `missing_files` (catalog rows pointing at files that no longer exist) or `orphan_files` (files on disk not in the catalog), do not silently rewrite the catalog. Surface the integrity report to the user and let them decide.
```

### Task H5: Commit reference files

- [ ] **Step 1: Stage and commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add references/
git -C 'c:\Brains_Research_Skill' commit -m "Add references/ (taxonomy, filename rules, org abbreviations, edge cases)"
```

---

## Phase I — Slash commands

Goal: Two markdown command files that Claude executes on `/brains-research-process` and `/brains-research-status`.

### Task I1: Write `commands/brains-research-process.md`

**Files:**
- Create: `c:\Brains_Research_Skill\commands\brains-research-process.md`

- [ ] **Step 1: Write the command**

Content:
```markdown
---
description: Catalogue new PDFs in the BRAINS research inbox — extract, dedupe, categorise, rename, file into Completed Review/, append _catalog.csv
---

# /brains-research-process

Process whatever PDFs are currently sitting in the inbox.

**Paths come from `config.json` at the skill root.** Use `python -m scripts.config` to inspect resolved paths if needed. The default `research_root` is `\\192.168.1.101\Singularity_Backup\Research`.

**Locked references — load these before deciding any category, filename, or edge-case treatment:**

- `references/taxonomy.md` — the 10 locked categories
- `references/filename-rules.md` — canonical filename format
- `references/org-abbreviations.md` — institutional author abbreviations
- `references/edge-cases.md` — scanned PDFs, collisions, non-PDFs, duplicates

## Steps

1. **Empty check.** Glob the inbox. If no PDFs, report `No new files.` and stop.

2. **Extract.** Run `python -m scripts.extract_all` from the skill root (or anywhere — the script resolves paths via config). This writes `_extract_all.json` to the Research root with `{filename: {size, text, pages, error}}` for every PDF in the inbox.

3. **Dedupe against existing catalog.** For each new file, compare its byte size against every file already in `Completed Review/**`. If an exact byte match exists, move the new file to `_duplicates/` and skip it (do not include in the rename plan). Use:
   ```powershell
   Get-ChildItem -Recurse '<research_root>\Completed Review' -Filter *.pdf | Where-Object Length -eq <N>
   ```
   or the equivalent `find` on macOS / Linux.

4. **Read and categorise.** Read `_extract_all.json`. If it is larger than 25 KB, split into chunks of approximately 18 entries and read sequentially. For each non-duplicate file, extract from the text:
   - `year` (four-digit, or `nd` if not findable)
   - `author` (first author surname, or organisation abbreviation from `references/org-abbreviations.md`)
   - `title` (5–15 words, descriptive)
   - `category` (must be one of the 10 in `references/taxonomy.md` — never invent new categories silently)
   - `doc_type` (e.g. `Journal article`, `Preprint`, `Conference paper`, `Institutional report`, `Legislation`, `White paper`, `Master thesis`, `PhD thesis`)

5. **Build filenames.** Apply `references/filename-rules.md`. Canonical form: `YYYY - ShortAuthor - Descriptive title.pdf`.

6. **Write `_rename_plan.json`** at the Research root, overwriting any prior plan. Schema:
   ```json
   {
     "<original_filename>": {
       "category": "<one of the 10>",
       "new_name": "YYYY - ShortAuthor - Descriptive title.pdf",
       "year": "YYYY",
       "author": "ShortAuthor",
       "title": "Descriptive title",
       "doc_type": "Journal article"
     }
   }
   ```

7. **Apply.** Run `python -m scripts.apply_renames` (no flags). Moves files and appends to `_catalog.csv`.

8. **Report back.** Concise summary:
   - N moved by category
   - N quarantined as duplicates (with names)
   - Any files where extraction failed or year / author was uncertain (flag these for the user to review)
   - Any new organisation abbreviations added to `references/org-abbreviations.md` during this run

## Dry-run

If the user says "dry run" or "preview", run `python -m scripts.apply_renames --dry-run` instead of step 7. Report what would have moved.
```

### Task I2: Write `commands/brains-research-status.md`

**Files:**
- Create: `c:\Brains_Research_Skill\commands\brains-research-status.md`

- [ ] **Step 1: Write the command**

Content:
```markdown
---
description: Read-only summary of the BRAINS research catalog — counts by category, recent additions, inbox and duplicate counts, integrity check
---

# /brains-research-status

Print a concise status report of the BRAINS research library. Read-only — never moves files or rewrites the catalog.

## Steps

1. Run `python -m scripts.status` from the skill root.

2. Format the JSON output as a human-readable summary:

   ```
   BRAINS Research Library — status

   Total catalogued:    <total>
   Inbox (pending):     <inbox_count>
   Duplicates folder:   <duplicates_count>

   By category:
     AI-General                    <n>
     AI-Ethics-Governance          <n>
     AI-Mental-Health              <n>
     AI-Neurodiversity-Autism      <n>
     AI-Education                  <n>
     Neurodiversity-General        <n>
     Autism                        <n>
     Suicide                       <n>
     Mental-Health-General         <n>
     HCI-Cognitive-Theory          <n>

   Most recent additions (last 10):
     <YYYY> — <Author> — <title>          <category>
     ...

   Integrity:
     Catalog rows pointing at missing files: <n>
     Files on disk not in catalog:           <n>
   ```

3. If `missing_files` or `orphan_files` is non-empty, list each one and recommend the user inspect them. Do not auto-repair.

4. If the inbox count is non-zero, suggest running `/brains-research-process`.
```

### Task I3: Commit the slash commands

- [ ] **Step 1: Stage and commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add commands/
git -C 'c:\Brains_Research_Skill' commit -m "Add slash commands: brains-research-process, brains-research-status"
```

---

## Phase J — `SKILL.md`

Goal: The skill entry point and behavioural contract. Modelled on `brains-resume`'s SKILL.md.

### Task J1: Write `SKILL.md`

**Files:**
- Create: `c:\Brains_Research_Skill\SKILL.md`

- [ ] **Step 1: Write SKILL.md**

Content:
```markdown
---
name: brains-research
description: Use when Matthew says "process research", "catalogue these papers", "new PDFs", or drops files into the BRAINS research inbox. Maintains the BRAINS research library — extracts, dedupes, categorises, renames, and files PDFs into a locked 10-category taxonomy, appending each entry to _catalog.csv. Read-only status command also available. A BRAINS Incubator project.
version: 1.0.0
license: MIT
---

# BRAINS Research Skill

This skill maintains the BRAINS research library — a curated, categorised corpus of PDFs covering AI, neurodiversity, ethics, mental health, and related domains. The skill runs the inbox-to-library pipeline (extract → dedupe → categorise → rename → file → append catalog) against a locked 10-category taxonomy, producing an append-only `_catalog.csv` that is the canonical record of what has been read and where it lives.

This is a BRAINS Incubator project, v1.0.0.

---

## How this skill operates

This section describes the behavioural contract — how Claude should behave across all turns within a session after the skill is invoked.

**Locked taxonomy.** Never silently add a category. The 10 categories live in `references/taxonomy.md` and are canonical. If a paper genuinely does not fit one of the ten, surface it and ask the user before proceeding.

**Locked dedupe rule.** Byte-exact match against `Completed Review/**` is the only dedupe signal. No fuzzy matching, no near-duplicate inference. False negatives are acceptable; false positives are not.

**Append-only catalog.** `_catalog.csv` is never rewritten. Corrections to past entries are out of scope for this skill and must be done manually.

**No silent renames.** A file already in `Completed Review/` is not renamed by this skill. If the user wants to rename, that is a separate explicit task.

**Plain, direct tone.** Status reports and error messages are plain and direct. Use identity-first language by default (`autistic researcher`, `neurodivergent participant`). No deficit framing of neurodivergence in any reference, command, or output.

**Air-gap awareness.** The library backs the BRAINS Certified evidence base. This skill never reveals, summarises, or speculates on BRAINS scoring criteria, calibration vignettes, or rubric mechanics from within the papers it catalogues. That concern is handled by the `brains-weekly-intel` skill.

**Confirm before destructive moves.** The pipeline reports its plan before applying it. If the user says "dry run" or "preview", run with `--dry-run` and report what would have moved.

---

## Available commands

| Command | Purpose |
|---|---|
| `/brains-research-process` | The full ingest workflow. Extract → dedupe → categorise → rename → file → append catalog. |
| `/brains-research-status` | Read-only summary: counts by category, recent additions, integrity check. |

---

## Configuration

The skill reads `config.json` from the skill root. Paths are per-machine — `config.json` is gitignored. To override the location of `config.json`, set the `BRAINS_RESEARCH_CONFIG` environment variable.

Schema (see `config.json.example`):

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

## References

When deciding category, filename, organisation abbreviation, or edge-case treatment, load the relevant reference file rather than reconstructing the rule from memory:

- `references/taxonomy.md`
- `references/filename-rules.md`
- `references/org-abbreviations.md`
- `references/edge-cases.md`

The reference files are the canonical source for this skill's rules. Do not paraphrase them.

---

## Scope

In scope: cataloguing the inbox into the locked taxonomy; producing the catalog row; producing a status report.

Out of scope (for now — separate skills will handle these): per-paper review or summarisation, cross-paper synthesis, search across the corpus, mirroring the corpus to the BRAINS website, suggesting LinkedIn or Bluesky posts from new additions, OCR of scanned PDFs, live fetching of papers from journal portals.
```

### Task J2: Commit `SKILL.md`

- [ ] **Step 1: Stage and commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add SKILL.md
git -C 'c:\Brains_Research_Skill' commit -m "Add SKILL.md (entry point + behavioural contract)"
```

---

## Phase K — GitHub-facing docs

Goal: README, CHANGELOG, CONTRIBUTING, STATUS — modelled on `BRAINS-resume-skill`.

### Task K1: Write `README.md`

**Files:**
- Create: `c:\Brains_Research_Skill\README.md`

- [ ] **Step 1: Write the README**

Content:
```markdown
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
```

### Task K2: Write `CHANGELOG.md`

**Files:**
- Create: `c:\Brains_Research_Skill\CHANGELOG.md`

- [ ] **Step 1: Write the changelog**

Content:
```markdown
# Changelog

All notable changes to BRAINS Research Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-28

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
```

### Task K3: Write `CONTRIBUTING.md`

**Files:**
- Create: `c:\Brains_Research_Skill\CONTRIBUTING.md`

- [ ] **Step 1: Write the contributing guide**

Content:
```markdown
# Contributing to BRAINS Research Skill

Thanks for your interest. BRAINS is an Incubator and Trust focused on neuro-affirming AI; contributions that align with that mission are very welcome.

## Ground rules

- Identity-first language by default (`autistic researcher`, `neurodivergent participant`). Switch to person-first only if a contributor explicitly states that preference for their own content.
- No deficit framing of neurodivergence anywhere in code, comments, references, or docs.
- The locked taxonomy is doctrine. PRs that add a new category must come with rationale and a user-visible decision; do not add silently.
- The catalog is append-only. PRs that retroactively rewrite catalog rows will be rejected.

## Development setup

```bash
git clone https://github.com/shard-BRAINS/BRAINS-Research-Skill.git
cd BRAINS-Research-Skill
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
cp config.json.example config.json
# Edit config.json for your local Research folder
```

## Running tests

```bash
pytest -v
```

All tests must pass before a PR is reviewed.

## Linting

```bash
ruff check scripts tests
```

## Reporting bugs

Open an issue on the GitHub repository with:

- A description of what happened versus what you expected.
- The exact command you ran.
- The relevant section of `_catalog.csv` or `_extract_all.json` if applicable (redact any private content).

## Code of conduct

Be decent. Disrespect — particularly ableism, dehumanisation of neurodivergent people, or hostility toward contributors — is not tolerated.
```

### Task K4: Write `STATUS.yml`

**Files:**
- Create: `c:\Brains_Research_Skill\STATUS.yml`

- [ ] **Step 1: Write the status file**

Content:
```yaml
name: brains-research
version: 1.0.0
released: 2026-05-28
status: stable
supported_platforms:
  - Windows 10/11 (PowerShell, Command Prompt)
  - macOS (bash, zsh)
  - Linux (bash)
python: ">=3.10"
dependencies:
  - pypdf>=4.0
commands:
  - /brains-research-process
  - /brains-research-status
```

### Task K5: Commit GitHub-facing docs

- [ ] **Step 1: Stage and commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add README.md CHANGELOG.md CONTRIBUTING.md STATUS.yml
git -C 'c:\Brains_Research_Skill' commit -m "Add README, CHANGELOG, CONTRIBUTING, STATUS.yml"
```

---

## Phase L — Install scripts

Goal: One-line installers for Windows (cmd + PowerShell) and macOS / Linux.

### Task L1: Write `install/install.ps1`

**Files:**
- Create: `c:\Brains_Research_Skill\install\install.ps1`

- [ ] **Step 1: Write the PowerShell installer**

Content:
```powershell
# BRAINS Research Skill — PowerShell installer
[CmdletBinding()]
param(
    [string]$ResearchRoot = "",
    [string]$ClaudeHome = (Join-Path $env:USERPROFILE ".claude")
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "BRAINS Research Skill installer" -ForegroundColor Cyan
Write-Host "Repo root:    $RepoRoot"
Write-Host "Claude home:  $ClaudeHome"
Write-Host ""

# 1. config.json
$cfgPath = Join-Path $RepoRoot "config.json"
$cfgExample = Join-Path $RepoRoot "config.json.example"
if (-not (Test-Path $cfgPath)) {
    Copy-Item $cfgExample $cfgPath
    Write-Host "Created config.json from config.json.example."
    if ($ResearchRoot -eq "") {
        $ResearchRoot = Read-Host "Research root path (Enter to keep default '\\192.168.1.101\Singularity_Backup\Research')"
    }
    if ($ResearchRoot -ne "") {
        $cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json
        $cfg.research_root = $ResearchRoot
        $cfg | ConvertTo-Json -Depth 5 | Set-Content $cfgPath -Encoding utf8
        Write-Host "research_root set to: $($cfg.research_root)"
    }
} else {
    Write-Host "config.json already exists — keeping it."
}

# 2. Validate research_root
$cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json
if (-not (Test-Path $cfg.research_root)) {
    Write-Warning "research_root does not exist or is unreachable: $($cfg.research_root)"
    Write-Warning "The skill will not run until this path is reachable."
}

# 3. Create venv and install
$venv = Join-Path $RepoRoot ".venv"
if (-not (Test-Path $venv)) {
    Write-Host "Creating virtualenv..."
    python -m venv $venv
}
$pip = Join-Path $venv "Scripts\python.exe"
& $pip -m pip install --upgrade pip | Out-Null
& $pip -m pip install -e "${RepoRoot}[dev]"

# 4. Install skill bundle (whitelist — only copy what the skill needs at runtime)
$skillDir = Join-Path $ClaudeHome "skills\brains-research"
if (Test-Path $skillDir) { Remove-Item -Recurse -Force $skillDir }
New-Item -ItemType Directory -Force -Path $skillDir | Out-Null
$skillFiles = @("SKILL.md", "config.json", "config.json.example", "LICENSE", "README.md", "pyproject.toml")
foreach ($f in $skillFiles) {
    $src = Join-Path $RepoRoot $f
    if (Test-Path $src) { Copy-Item -Force $src (Join-Path $skillDir $f) }
}
foreach ($d in @("scripts", "references", "commands")) {
    Copy-Item -Recurse -Force (Join-Path $RepoRoot $d) (Join-Path $skillDir $d)
}
Write-Host "Skill installed at: $skillDir"

# 5. Install slash commands
$cmdsDir = Join-Path $ClaudeHome "commands"
New-Item -ItemType Directory -Force -Path $cmdsDir | Out-Null
Copy-Item -Force (Join-Path $RepoRoot "commands\brains-research-process.md") $cmdsDir
Copy-Item -Force (Join-Path $RepoRoot "commands\brains-research-status.md") $cmdsDir
Write-Host "Slash commands installed at: $cmdsDir"

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host "Try: /brains-research-status"
```

### Task L2: Write `install/install.cmd`

**Files:**
- Create: `c:\Brains_Research_Skill\install\install.cmd`

- [ ] **Step 1: Write the cmd wrapper**

Content:
```bat
@echo off
REM BRAINS Research Skill — cmd wrapper for install.ps1
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
```

### Task L3: Write `install/install.sh`

**Files:**
- Create: `c:\Brains_Research_Skill\install\install.sh`

- [ ] **Step 1: Write the bash installer**

Content:
```bash
#!/usr/bin/env bash
# BRAINS Research Skill — bash installer (macOS / Linux / WSL)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
RESEARCH_ROOT="${RESEARCH_ROOT:-}"

echo "BRAINS Research Skill installer"
echo "Repo root:    $REPO_ROOT"
echo "Claude home:  $CLAUDE_HOME"
echo ""

# 1. config.json
if [ ! -f "$REPO_ROOT/config.json" ]; then
    cp "$REPO_ROOT/config.json.example" "$REPO_ROOT/config.json"
    echo "Created config.json from config.json.example."
    if [ -z "$RESEARCH_ROOT" ]; then
        read -r -p "Research root path (Enter to keep default): " RESEARCH_ROOT
    fi
    if [ -n "$RESEARCH_ROOT" ]; then
        python -c "
import json, sys
p = '$REPO_ROOT/config.json'
d = json.load(open(p))
d['research_root'] = '$RESEARCH_ROOT'
json.dump(d, open(p, 'w'), indent=2)
print('research_root set to:', d['research_root'])
"
    fi
else
    echo "config.json already exists — keeping it."
fi

# 2. Validate
ROOT=$(python -c "import json; print(json.load(open('$REPO_ROOT/config.json'))['research_root'])")
if [ ! -d "$ROOT" ]; then
    echo "WARNING: research_root does not exist or is unreachable: $ROOT" >&2
fi

# 3. venv + install
if [ ! -d "$REPO_ROOT/.venv" ]; then
    python -m venv "$REPO_ROOT/.venv"
fi
"$REPO_ROOT/.venv/bin/python" -m pip install --upgrade pip >/dev/null
"$REPO_ROOT/.venv/bin/python" -m pip install -e "$REPO_ROOT[dev]"

# 4. Skill bundle
SKILL_DIR="$CLAUDE_HOME/skills/brains-research"
rm -rf "$SKILL_DIR"
mkdir -p "$SKILL_DIR"
rsync -a --exclude '.venv' --exclude '.git' --exclude 'research-data' --exclude 'tests' "$REPO_ROOT/" "$SKILL_DIR/"
echo "Skill installed at: $SKILL_DIR"

# 5. Slash commands
mkdir -p "$CLAUDE_HOME/commands"
cp "$REPO_ROOT/commands/brains-research-process.md" "$CLAUDE_HOME/commands/"
cp "$REPO_ROOT/commands/brains-research-status.md" "$CLAUDE_HOME/commands/"
echo "Slash commands installed at: $CLAUDE_HOME/commands"

echo ""
echo "Done."
echo "Try: /brains-research-status"
```

- [ ] **Step 2: Mark install.sh executable**

Run (PowerShell — this is metadata-only on Windows, but we record the intent in git):
```powershell
# No-op on Windows; the chmod is set when committing under bash/WSL.
# We rely on the install.sh shebang and tell users to `bash install/install.sh` directly.
```

### Task L4: Local install dry-run

- [ ] **Step 1: Run the PowerShell installer**

Run:
```powershell
powershell -ExecutionPolicy Bypass -File 'c:\Brains_Research_Skill\install\install.ps1' -ResearchRoot '\\192.168.1.101\Singularity_Backup\Research'
```

Expected:
- `config.json` exists at the repo root with `research_root` set to the UNC path.
- `~/.claude/skills/brains-research/` exists and contains `SKILL.md`, `scripts/`, `references/`, `commands/`, etc.
- `~/.claude/commands/brains-research-process.md` exists.
- `~/.claude/commands/brains-research-status.md` exists.
- Final line: `Done. Try: /brains-research-status`.

- [ ] **Step 2: Verify by running status from the installed skill**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m scripts.status
```

Expected: JSON report with `total: 102`, `by_category` summing to 102, `inbox_count: 3`, integrity fields empty (or surfaced if real mismatches exist).

### Task L5: Commit install scripts

- [ ] **Step 1: Stage and commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add install/
git -C 'c:\Brains_Research_Skill' commit -m "Add one-line installers for Windows, macOS, Linux"
```

---

## Phase M — GitHub release

Goal: Push the repo to `shard-BRAINS/BRAINS-Research-Skill`, public, MIT.

### Task M1: Create the GitHub repo

- [ ] **Step 1: Verify gh CLI is authenticated**

Run:
```powershell
gh auth status
```

Expected: shows authenticated user with `shard-BRAINS` access. If not, run `gh auth login` first.

- [ ] **Step 2: Create the repo**

Run:
```powershell
gh repo create shard-BRAINS/BRAINS-Research-Skill --public --description "A Claude Code skill for maintaining the BRAINS research library — extract, dedupe, categorise, rename, file PDFs into a locked 10-category taxonomy. An Incubator project from BRAINS."
```

Expected: `https://github.com/shard-BRAINS/BRAINS-Research-Skill` created.

### Task M2: Push the repo

- [ ] **Step 1: Add the remote**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' remote add origin https://github.com/shard-BRAINS/BRAINS-Research-Skill.git
```

- [ ] **Step 2: Push main**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' push -u origin main
```

Expected: `main` pushed; remote tracking set.

- [ ] **Step 3: Verify on GitHub**

Run:
```powershell
gh repo view shard-BRAINS/BRAINS-Research-Skill --web
```

Expected: browser opens to the repo. README renders. LICENSE shows MIT. Commit history matches the local repo.

### Task M3: Tag v1.0.0

- [ ] **Step 1: Tag and push**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' tag -a v1.0.0 -m "v1.0.0 — initial release"
git -C 'c:\Brains_Research_Skill' push origin v1.0.0
```

- [ ] **Step 2: Create the GitHub release**

Run:
```powershell
gh release create v1.0.0 --repo shard-BRAINS/BRAINS-Research-Skill --title "v1.0.0 — initial release" --notes "Initial release of brains-research. Two slash commands (/brains-research-process, /brains-research-status). Config-driven paths, locked 10-category taxonomy, byte-exact dedupe, append-only catalog, full pytest coverage."
```

Expected: release visible at `https://github.com/shard-BRAINS/BRAINS-Research-Skill/releases`.

---

## Phase N — End-to-end verification and deprecation

Goal: Run the full new pipeline against the real 3-PDF inbox, confirm parity with the patched share scripts, deprecate the old `/process-research`.

### Task N1: End-to-end test against the real inbox

- [ ] **Step 1: Confirm the inbox still has 3 PDFs**

Run:
```powershell
Get-ChildItem '\\192.168.1.101\Singularity_Backup\Research\to be reviwed\*.pdf' | Select-Object Name
```

Expected: three filenames.

- [ ] **Step 2: Run extract_all from the installed skill**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m scripts.extract_all
```

Expected: stderr reports `Found 3 PDFs`. `_extract_all.json` appears at the Research root.

- [ ] **Step 3: Invoke `/brains-research-process` in a fresh Claude session**

Open a new Claude Code session in `\\192.168.1.101\Singularity_Backup\Research` and run `/brains-research-process`. Claude reads `_extract_all.json`, categorises against `references/taxonomy.md`, writes `_rename_plan.json`, runs `apply_renames`.

Expected: three PDFs end up in the correct category folders under `Completed Review/`; `_catalog.csv` grows by three rows; report flags any uncertain attributions.

- [ ] **Step 4: Invoke `/brains-research-status`**

Run `/brains-research-status` in the same session.

Expected: `total: 105`, integrity fields empty, recent additions show the three new entries.

### Task N2: Deprecate the old `/process-research` slash command

**Files:**
- Modify: `C:\Users\matth\.claude\commands\process-research.md`

- [ ] **Step 1: Replace the command body with a redirect notice**

Replace the entire file contents with:
```markdown
---
description: DEPRECATED — use /brains-research-process instead
---

# /process-research (deprecated)

This command has been replaced by `/brains-research-process` from the `brains-research` skill.

See: https://github.com/shard-BRAINS/BRAINS-Research-Skill

The new command does the same work plus:
- per-machine `config.json` for paths
- locked taxonomy and rules in `references/*.md`
- a companion `/brains-research-status` for read-only catalog summaries
- full pytest coverage
```

- [ ] **Step 2: Confirm the new command works, then delete the deprecation shim**

Once the user has confirmed `/brains-research-process` is working for at least one ingest cycle, remove the deprecated file entirely:

Run:
```powershell
Remove-Item 'C:\Users\matth\.claude\commands\process-research.md'
```

### Task N3: Final commit and documentation update

- [ ] **Step 1: Update CHANGELOG with the deprecation note**

Append to `c:\Brains_Research_Skill\CHANGELOG.md`:

```markdown
### Migration notes
- The previous `/process-research` slash command (hardcoded to a OneDrive path) has been deprecated and removed from `~/.claude/commands/`. Use `/brains-research-process` from the installed `brains-research` skill instead.
```

- [ ] **Step 2: Commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add CHANGELOG.md
git -C 'c:\Brains_Research_Skill' commit -m "Document deprecation of old /process-research command"
git -C 'c:\Brains_Research_Skill' push origin main
```

---

## Acceptance criteria (from the spec)

Re-check each before marking the plan complete:

1. **Repo `shard-BRAINS/BRAINS-Research-Skill` exists, public, MIT licensed.** — verified by Task M2 step 3.
2. **README is brand-compliant and modelled on `BRAINS-resume-skill`'s README.** — verified by Task K1.
3. **`install.ps1` runs cleanly on Matthew's Windows machine, produces a working `config.json` and registers both slash commands.** — verified by Task L4.
4. **`/brains-research-process` against the current inbox produces the same outcome as the old `/process-research` (three PDFs catalogued into the correct categories, `_catalog.csv` extended by three rows).** — verified by Task N1 step 3.
5. **`/brains-research-status` against the current corpus reports the correct count (102 existing rows pre-migration, 105 post) and zero integrity violations.** — verified by Task N1 step 4.
6. **`pytest` passes against the bundled test fixtures.** — verified by Task G2 step 3.
7. **The existing share is untouched apart from the in-place script update plus normal inbox processing.** — Phase A only edits ROOT constants; Phase N only adds new catalog rows and moves the 3 inbox PDFs.
8. **No corpus data is committed to the repo.** — verified by `.gitignore` in Task B2 and by inspecting the GitHub repo file tree at Task M2 step 3.
