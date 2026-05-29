# BRAINS Research Skill v1.1.0 — Plan 2: `/brains-research-review`

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship v1.1.0 of `brains-research` with a new `/brains-research-review` slash command that produces a per-paper review (summary + analytical review + BRAINS commentary) and optional LinkedIn / Bluesky drafts handed off to `brains-content`. Reviews persist to `Reviews/<Category>/<stem>.review.md` on the share, with an append-only `_reviews.csv` ledger.

**Architecture:** Two new Python scripts (`scripts/extract_full.py` for cached full-text extraction, `scripts/review.py` for paper selection + ledger I/O + draft handoff) plus the slash-command markdown that orchestrates Claude's summarisation, analytical review, and BRAINS commentary work through three reference templates. v1.0.0 surface untouched: `_catalog.csv` stays append-only, existing commands and scripts unchanged.

**Tech Stack:** Python 3.10+, `pypdf>=4.0`, `pytest`, existing `scripts.config` module, Claude Code slash-command markdown.

**Spec:** [c:\Brains_Research_Skill\docs\specs\2026-05-29-brains-research-review-design.md](c:\Brains_Research_Skill\docs\specs\2026-05-29-brains-research-review-design.md)

---

## File structure (decomposition lock-in)

| Path | Responsibility | Phase |
|---|---|---|
| `c:\Brains_Research_Skill\tests\fixtures\sample_multipage.pdf` | 3-page fixture for full-text tests | A |
| `c:\Brains_Research_Skill\tests\test_extract_full.py` | Extract-full tests | B |
| `c:\Brains_Research_Skill\scripts\extract_full.py` | Full-text extraction + per-paper JSON cache, mtime-invalidated | B |
| `c:\Brains_Research_Skill\tests\test_review.py` | Selection, ledger I/O, content draft handoff, scanned-PDF stub | C |
| `c:\Brains_Research_Skill\scripts\review.py` | Selection (filename/partial/category/picker), `_reviews.csv` append, review.md write, CT00X.md draft writer | C |
| `c:\Brains_Research_Skill\scripts\config.py` | Extend with optional `content_drafts_dir` key | C |
| `c:\Brains_Research_Skill\tests\test_config.py` | Add a test for optional `content_drafts_dir` | C |
| `c:\Brains_Research_Skill\references\review-template.md` | Skeleton for `.review.md` files | D |
| `c:\Brains_Research_Skill\references\linkedin-template.md` | LinkedIn long-post template for draft handoff | D |
| `c:\Brains_Research_Skill\references\bluesky-template.md` | Bluesky ≤300-char template | D |
| `c:\Brains_Research_Skill\commands\brains-research-review.md` | The slash command that orchestrates the 7-step flow | E |
| `c:\Brains_Research_Skill\SKILL.md` | Add new command to table + new behavioural clauses | F |
| `c:\Brains_Research_Skill\config.json.example` | Add optional `content_drafts_dir` key with Matthew's default | F |
| `c:\Brains_Research_Skill\STATUS.yml` | Bump version to 1.1.0, add new command | G |
| `c:\Brains_Research_Skill\CHANGELOG.md` | Add v1.1.0 section | G |
| `c:\Brains_Research_Skill\README.md` | Add new command to "what it does" list | G |
| `~/.claude/skills/brains-research/` | Re-installed bundle via install.ps1 | H |
| `\\192.168.1.101\Singularity_Backup\Research\Reviews\` | Created by first review run (auto) | H |
| `\\192.168.1.101\Singularity_Backup\Research\_reviews.csv` | Created by first review run (auto) | H |

---

## Phase A — Test fixture: multi-page PDF

Goal: A small fixture with extractable text on multiple pages, used by extract_full tests.

### Task A1: Generate `sample_multipage.pdf`

**Files:**
- Create: `c:\Brains_Research_Skill\tests\fixtures\sample_multipage.pdf`

- [ ] **Step 1: Generate a 3-page PDF with text on each page**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -c @"
from pypdf import PdfWriter, PdfReader
from io import BytesIO
import subprocess, sys

# Use reportlab if available; otherwise fall back to pypdf blank pages plus a stamping trick.
# Try reportlab first.
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import LETTER
    out = r'c:\Brains_Research_Skill\tests\fixtures\sample_multipage.pdf'
    c = canvas.Canvas(out, pagesize=LETTER)
    for i, txt in enumerate(['Page one alpha content', 'Page two bravo content', 'Page three charlie content']):
        c.drawString(72, 720, txt)
        c.showPage()
    c.save()
    print('wrote multipage with reportlab')
except ImportError:
    # Fallback: install reportlab into the venv then retry
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'reportlab'])
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import LETTER
    out = r'c:\Brains_Research_Skill\tests\fixtures\sample_multipage.pdf'
    c = canvas.Canvas(out, pagesize=LETTER)
    for i, txt in enumerate(['Page one alpha content', 'Page two bravo content', 'Page three charlie content']):
        c.drawString(72, 720, txt)
        c.showPage()
    c.save()
    print('wrote multipage with reportlab (after install)')

# Verify
r = PdfReader(out)
print('pages:', len(r.pages))
for i, p in enumerate(r.pages):
    print(f'page {i}:', repr(p.extract_text())[:80])
"@
```

Expected: prints `wrote multipage`, `pages: 3`, and three lines each containing the corresponding "alpha"/"bravo"/"charlie" content. Note: `reportlab` is only a dev / test dependency; it does not need to be in `requirements.txt` (it is not used at runtime).

- [ ] **Step 2: Add reportlab to requirements-dev.txt**

Replace the content of `c:\Brains_Research_Skill\requirements-dev.txt` with:
```
-r requirements.txt
pytest>=7.0
ruff>=0.4
reportlab>=4.0
```

- [ ] **Step 3: Commit the fixture and dev-dep update**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add tests/fixtures/sample_multipage.pdf requirements-dev.txt
git -C 'c:\Brains_Research_Skill' commit -m "Add 3-page multipage fixture for full-text extraction tests"
```

---

## Phase B — `scripts/extract_full.py` (TDD)

Goal: Full-text PDF extraction with per-paper JSON cache, mtime-invalidated.

### Task B1: Write the failing tests

**Files:**
- Create: `c:\Brains_Research_Skill\tests\test_extract_full.py`

- [ ] **Step 1: Write tests**

Content:
```python
"""Tests for scripts.extract_full."""
import json
import time
from pathlib import Path

import pytest

from scripts.extract_full import extract_full, load_or_extract

FIXTURE = Path(__file__).parent / "fixtures" / "sample_multipage.pdf"


def test_extract_full_returns_all_pages(tmp_path):
    """extract_full returns a list of strings, one per page."""
    pages = extract_full(FIXTURE)
    assert isinstance(pages, list)
    assert len(pages) == 3
    assert all(isinstance(p, str) for p in pages)
    assert "alpha" in pages[0]
    assert "bravo" in pages[1]
    assert "charlie" in pages[2]


def test_extract_full_missing_pdf_returns_empty(tmp_path):
    """Missing PDF returns an empty list with an error marker via the caller."""
    pages = extract_full(tmp_path / "nope.pdf")
    assert pages == []


def test_load_or_extract_creates_cache(tmp_path):
    """First call extracts and writes the cache JSON."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    cache_path = cache_dir / "sample.fulltext.json"
    pages = load_or_extract(FIXTURE, cache_path)
    assert cache_path.exists()
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    assert data["pages"] == pages
    assert data["source_mtime"] == FIXTURE.stat().st_mtime
    assert "alpha" in data["pages"][0]


def test_load_or_extract_uses_cache_when_fresh(tmp_path):
    """Second call returns cached pages without re-extracting when PDF mtime unchanged."""
    cache_path = tmp_path / "sample.fulltext.json"
    pages_first = load_or_extract(FIXTURE, cache_path)
    mtime_after_first = cache_path.stat().st_mtime
    time.sleep(0.05)
    pages_second = load_or_extract(FIXTURE, cache_path)
    assert pages_second == pages_first
    assert cache_path.stat().st_mtime == mtime_after_first


def test_load_or_extract_invalidates_when_pdf_newer(tmp_path):
    """Cache is rebuilt when the PDF mtime is newer than the cached source_mtime."""
    cache_path = tmp_path / "sample.fulltext.json"
    cache_path.write_text(json.dumps({
        "pages": ["stale"],
        "source_mtime": 0.0,
    }), encoding="utf-8")
    pages = load_or_extract(FIXTURE, cache_path)
    assert "alpha" in pages[0]
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    assert data["source_mtime"] == FIXTURE.stat().st_mtime


def test_is_scanned_pdf_detection(tmp_path):
    """A PDF with all-empty pages is reported as scanned."""
    from scripts.extract_full import is_scanned
    assert is_scanned(["", "", ""]) is True
    assert is_scanned(["", "some content", ""]) is False
    assert is_scanned([]) is True
```

- [ ] **Step 2: Run, expect fail**

Run:
```powershell
cd 'c:\Brains_Research_Skill'
.\.venv\Scripts\python.exe -m pytest tests/test_extract_full.py -v
```

Expected: all fail with `ModuleNotFoundError: No module named 'scripts.extract_full'`.

### Task B2: Implement `scripts/extract_full.py`

**Files:**
- Create: `c:\Brains_Research_Skill\scripts\extract_full.py`

- [ ] **Step 1: Write the module**

Content:
```python
"""Full-text PDF extraction with per-paper JSON cache."""
from __future__ import annotations

import json
import logging
import warnings
from pathlib import Path

logging.getLogger("pypdf").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

from pypdf import PdfReader  # noqa: E402


def extract_full(pdf_path: Path) -> list[str]:
    """Return a list with one string per page. Empty list on read failure."""
    try:
        reader = PdfReader(str(pdf_path))
    except Exception:
        return []
    pages: list[str] = []
    for i in range(len(reader.pages)):
        try:
            pages.append(reader.pages[i].extract_text() or "")
        except Exception:
            pages.append("")
    return pages


def is_scanned(pages: list[str]) -> bool:
    """True if every page is empty (image-only PDF or read failure)."""
    if not pages:
        return True
    return all(not p.strip() for p in pages)


def load_or_extract(pdf_path: Path, cache_path: Path) -> list[str]:
    """Return full text, using cache_path if fresh, otherwise extracting and caching."""
    pdf_mtime = pdf_path.stat().st_mtime if pdf_path.exists() else 0.0
    if cache_path.exists():
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8-sig"))
            if data.get("source_mtime", 0.0) >= pdf_mtime and pdf_mtime > 0:
                return list(data.get("pages", []))
        except (json.JSONDecodeError, OSError):
            pass
    pages = extract_full(pdf_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps({"pages": pages, "source_mtime": pdf_mtime}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return pages
```

- [ ] **Step 2: Run, expect pass**

Run:
```powershell
cd 'c:\Brains_Research_Skill'
.\.venv\Scripts\python.exe -m pytest tests/test_extract_full.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add scripts/extract_full.py tests/test_extract_full.py
git -C 'c:\Brains_Research_Skill' commit -m "Add scripts/extract_full.py with cache + scanned-PDF detection"
```

---

## Phase C — `scripts/review.py` (TDD)

Goal: Paper selection, `_reviews.csv` ledger I/O, review.md writer, content-draft handoff.

### Task C1: Extend `scripts/config.py` for optional `content_drafts_dir`

**Files:**
- Modify: `c:\Brains_Research_Skill\scripts\config.py`
- Modify: `c:\Brains_Research_Skill\tests\test_config.py`

- [ ] **Step 1: Add a test for the optional key (failing first)**

Append to `c:\Brains_Research_Skill\tests\test_config.py`:
```python


def test_load_config_optional_content_drafts_dir(tmp_path, mock_research_root):
    """content_drafts_dir is optional; when present it is loaded as a Path."""
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({
        "research_root": str(mock_research_root),
        "inbox_dir": "to be reviwed",
        "completed_dir": "Completed Review",
        "duplicates_dir": "_duplicates",
        "catalog_csv": "_catalog.csv",
        "extract_pages": 2,
        "extract_max_chars": 3000,
        "content_drafts_dir": str(tmp_path / "drafts"),
    }))
    loaded = load_config(cfg)
    assert loaded.content_drafts_dir == tmp_path / "drafts"


def test_load_config_missing_content_drafts_dir_is_none(config_file):
    """When content_drafts_dir is absent, the attribute is None."""
    loaded = load_config(config_file)
    assert loaded.content_drafts_dir is None
```

- [ ] **Step 2: Run, confirm those two new tests fail**

Run:
```powershell
cd 'c:\Brains_Research_Skill'
.\.venv\Scripts\python.exe -m pytest tests/test_config.py -v
```

Expected: 2 new tests fail with `AttributeError: 'Config' object has no attribute 'content_drafts_dir'`.

- [ ] **Step 3: Update `scripts/config.py`**

Replace the existing `Config` dataclass and the tail of `load_config` in `c:\Brains_Research_Skill\scripts\config.py`. Find:

```python
@dataclass(frozen=True)
class Config:
    research_root: Path
    inbox_dir: Path
    completed_dir: Path
    duplicates_dir: Path
    catalog_csv: Path
    extract_pages: int
    extract_max_chars: int
```

Replace with:

```python
@dataclass(frozen=True)
class Config:
    research_root: Path
    inbox_dir: Path
    completed_dir: Path
    duplicates_dir: Path
    catalog_csv: Path
    extract_pages: int
    extract_max_chars: int
    content_drafts_dir: Path | None = None
```

Find the existing `return Config(...)` at the end of `load_config`:

```python
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

Replace with:

```python
    content_drafts_dir = None
    if data.get("content_drafts_dir"):
        content_drafts_dir = Path(data["content_drafts_dir"])

    return Config(
        research_root=research_root,
        inbox_dir=research_root / data["inbox_dir"],
        completed_dir=research_root / data["completed_dir"],
        duplicates_dir=research_root / data["duplicates_dir"],
        catalog_csv=research_root / data["catalog_csv"],
        extract_pages=int(data["extract_pages"]),
        extract_max_chars=int(data["extract_max_chars"]),
        content_drafts_dir=content_drafts_dir,
    )
```

- [ ] **Step 4: Run, expect all config tests pass**

Run:
```powershell
cd 'c:\Brains_Research_Skill'
.\.venv\Scripts\python.exe -m pytest tests/test_config.py -v
```

Expected: 8 passed (6 original + 2 new).

### Task C2: Write the review.py failing tests

**Files:**
- Create: `c:\Brains_Research_Skill\tests\test_review.py`

- [ ] **Step 1: Write tests**

Content:
```python
"""Tests for scripts.review."""
import csv
import json
from pathlib import Path

import pytest

from scripts.review import (
    REVIEWS_FIELDNAMES,
    append_review_row,
    list_recent_papers,
    next_ct_id,
    review_path_for,
    select_paper,
    write_content_draft,
    write_review_file,
)


# ---------- helpers ----------

CATALOG_ROW_1 = {
    "original_filename": "x.pdf",
    "new_filename": "2024 - Smith - A study on X.pdf",
    "category": "AI-General",
    "year": "2024",
    "author": "Smith",
    "title": "A study on X",
    "doc_type": "Journal article",
    "byte_size": "1000",
    "new_path": "Completed Review/AI-General/2024 - Smith - A study on X.pdf",
}

CATALOG_ROW_2 = {
    "original_filename": "y.pdf",
    "new_filename": "2025 - Jones - Effects of Y.pdf",
    "category": "AI-Mental-Health",
    "year": "2025",
    "author": "Jones",
    "title": "Effects of Y",
    "doc_type": "Preprint",
    "byte_size": "2000",
    "new_path": "Completed Review/AI-Mental-Health/2025 - Jones - Effects of Y.pdf",
}


def _seed_catalog(root, rows):
    catalog = root / "_catalog.csv"
    fieldnames = [
        "original_filename", "new_filename", "category", "year",
        "author", "title", "doc_type", "byte_size", "new_path",
    ]
    with catalog.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return catalog


# ---------- select_paper ----------

def test_select_paper_by_exact_filename(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _seed_catalog(mock_research_root, [CATALOG_ROW_1, CATALOG_ROW_2])
    paper = select_paper("2024 - Smith - A study on X.pdf")
    assert paper["new_filename"] == CATALOG_ROW_1["new_filename"]


def test_select_paper_by_partial_title(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _seed_catalog(mock_research_root, [CATALOG_ROW_1, CATALOG_ROW_2])
    paper = select_paper("Effects of Y")
    assert paper["new_filename"] == CATALOG_ROW_2["new_filename"]


def test_select_paper_returns_none_when_no_match(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _seed_catalog(mock_research_root, [CATALOG_ROW_1])
    assert select_paper("totally-nonexistent") is None


def test_list_recent_papers_returns_last_n(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    rows = [{**CATALOG_ROW_1, "new_filename": f"row{i}.pdf",
             "new_path": f"Completed Review/AI-General/row{i}.pdf"} for i in range(15)]
    _seed_catalog(mock_research_root, rows)
    recent = list_recent_papers(n=10)
    assert len(recent) == 10
    assert recent[-1]["new_filename"] == "row14.pdf"


def test_list_recent_papers_filtered_by_category(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    _seed_catalog(mock_research_root, [CATALOG_ROW_1, CATALOG_ROW_2])
    only_mh = list_recent_papers(n=10, category="AI-Mental-Health")
    assert len(only_mh) == 1
    assert only_mh[0]["category"] == "AI-Mental-Health"


# ---------- review_path_for ----------

def test_review_path_for_strips_pdf_and_adds_review_md(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    expected = (
        mock_research_root / "Reviews" / "AI-General" /
        "2024 - Smith - A study on X.review.md"
    )
    assert review_path_for(CATALOG_ROW_1) == expected


# ---------- _reviews.csv ----------

def test_append_review_row_creates_file_with_header(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    row = {f: "" for f in REVIEWS_FIELDNAMES}
    row["new_path"] = CATALOG_ROW_1["new_path"]
    row["review_date"] = "2026-05-29"
    append_review_row(row)
    csv_path = mock_research_root / "_reviews.csv"
    assert csv_path.exists()
    text = csv_path.read_text(encoding="utf-8")
    assert "new_path" in text  # header present
    assert CATALOG_ROW_1["new_path"] in text


def test_append_review_row_is_append_only(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    csv_path = mock_research_root / "_reviews.csv"
    for i, date in enumerate(["2026-05-29", "2026-06-01"]):
        row = {f: "" for f in REVIEWS_FIELDNAMES}
        row["new_path"] = CATALOG_ROW_1["new_path"]
        row["review_date"] = date
        append_review_row(row)
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    assert len(rows) == 2
    assert rows[0]["review_date"] == "2026-05-29"
    assert rows[1]["review_date"] == "2026-06-01"


# ---------- write_review_file ----------

def test_write_review_file_writes_markdown(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    rendered = write_review_file(
        paper=CATALOG_ROW_1,
        review_date="2026-05-29",
        focus_criteria="methodology focus",
        sections={
            "objective_summary": "Neutral summary.",
            "analytical_review": "Critical read.",
            "bias_flags_md": "- small_sample",
            "candidate_quotes_md": "> \"A quote.\"",
            "brains_alignment": "Aligns here.",
            "brains_friction": "Friction here.",
            "brains_evidence_base_fit": "Evidence fit.",
            "brains_candidate_quotes_md": "- \"BRAINS-usable quote.\"",
        },
        draft_ids={"linkedin": "CT001", "bluesky": "CT002"},
        next_action="follow up with author",
    )
    out = mock_research_root / "Reviews" / "AI-General" / "2024 - Smith - A study on X.review.md"
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "Neutral summary." in text
    assert "Critical read." in text
    assert "Aligns here." in text
    assert "CT001" in text
    assert "CT002" in text
    assert "methodology focus" in text
    assert "follow up with author" in text


def test_write_review_file_scanned_pdf_stub(mock_research_root, config_file, monkeypatch):
    """A scanned PDF produces a stub review.md with the manual-review note."""
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    from scripts.review import write_scanned_stub
    write_scanned_stub(paper=CATALOG_ROW_1, review_date="2026-05-29")
    out = mock_research_root / "Reviews" / "AI-General" / "2024 - Smith - A study on X.review.md"
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "Scanned PDF" in text
    assert "manual review required" in text


# ---------- next_ct_id ----------

def test_next_ct_id_returns_ct001_when_no_calendar(tmp_path):
    drafts_dir = tmp_path / "drafts"
    drafts_dir.mkdir()
    assert next_ct_id(drafts_dir.parent) == "CT001"


def test_next_ct_id_increments(tmp_path):
    content_root = tmp_path
    drafts = content_root / "drafts"
    drafts.mkdir()
    calendar = content_root / "content_calendar.csv"
    fieldnames = [
        "id", "publish_date", "channel", "brand", "format",
        "topic", "headline", "status", "draft_link", "published_link",
        "author", "notes",
    ]
    with calendar.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerow({"id": "CT005", **{k: "" for k in fieldnames if k != "id"}})
    assert next_ct_id(content_root) == "CT006"


# ---------- write_content_draft ----------

def test_write_content_draft_writes_md_and_appends_calendar(tmp_path):
    content_root = tmp_path
    drafts = content_root / "drafts"
    drafts.mkdir()
    result = write_content_draft(
        content_root=content_root,
        ct_id="CT001",
        channel="LinkedIn",
        brand="BRAINS",
        format_="long post",
        topic="paper X",
        headline="Headline",
        body="Body text.",
        notes_md="- source citation\n",
        author="Matthew",
    )
    assert result["draft_path"].exists()
    text = result["draft_path"].read_text(encoding="utf-8")
    assert "Headline" in text
    assert "Body text." in text
    assert "BRAINS" in text
    calendar = content_root / "content_calendar.csv"
    assert calendar.exists()
    rows = list(csv.DictReader(calendar.open(encoding="utf-8")))
    assert rows[-1]["id"] == "CT001"
    assert rows[-1]["status"] == "drafted"
    assert rows[-1]["channel"] == "LinkedIn"


def test_write_content_draft_silently_skips_when_drafts_dir_missing(tmp_path, capsys):
    """If the drafts dir does not exist, write_content_draft returns None and warns."""
    result = write_content_draft(
        content_root=tmp_path / "does_not_exist",
        ct_id="CT001",
        channel="LinkedIn",
        brand="BRAINS",
        format_="long post",
        topic="paper X",
        headline="Headline",
        body="Body text.",
        notes_md="- source citation\n",
        author="Matthew",
    )
    assert result is None
```

- [ ] **Step 2: Run, expect fail**

Run:
```powershell
cd 'c:\Brains_Research_Skill'
.\.venv\Scripts\python.exe -m pytest tests/test_review.py -v
```

Expected: all 15 fail with `ModuleNotFoundError: No module named 'scripts.review'`.

### Task C3: Implement `scripts/review.py`

**Files:**
- Create: `c:\Brains_Research_Skill\scripts\review.py`

- [ ] **Step 1: Write the module**

Content:
```python
"""Paper selection, _reviews.csv ledger I/O, review.md writer, content-draft handoff."""
from __future__ import annotations

import csv
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

from scripts.config import load_config

REVIEWS_FIELDNAMES = [
    "new_path", "category", "paper_year", "paper_author", "paper_title",
    "review_path", "review_date", "focus_criteria",
    "linkedin_draft_id", "bluesky_draft_id",
    "bias_flags", "tags", "next_action",
]

CONTENT_CALENDAR_FIELDNAMES = [
    "id", "publish_date", "channel", "brand", "format",
    "topic", "headline", "status", "draft_link", "published_link",
    "author", "notes",
]


# ---------- paper selection ----------

def _load_catalog_rows() -> list[dict]:
    cfg = load_config()
    if not cfg.catalog_csv.exists():
        return []
    with cfg.catalog_csv.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def select_paper(arg: str) -> dict | None:
    """Return the catalog row matching arg (exact filename or partial title), else None."""
    rows = _load_catalog_rows()
    needle = arg.strip().lower()
    for r in rows:
        if r.get("new_filename", "").lower() == needle:
            return r
    for r in rows:
        haystack = " ".join([
            r.get("new_filename", ""), r.get("title", ""), r.get("original_filename", ""),
        ]).lower()
        if needle and needle in haystack:
            return r
    return None


def list_recent_papers(n: int = 10, category: str | None = None) -> list[dict]:
    """Return the last n rows from the catalog, optionally filtered by category."""
    rows = _load_catalog_rows()
    if category:
        rows = [r for r in rows if r.get("category") == category]
    return rows[-n:]


# ---------- review path ----------

def review_path_for(paper: dict) -> Path:
    """Reviews/<Category>/<stem>.review.md on the research root."""
    cfg = load_config()
    stem = Path(paper["new_filename"]).stem
    return cfg.research_root / "Reviews" / paper["category"] / f"{stem}.review.md"


def fulltext_cache_path_for(paper: dict) -> Path:
    cfg = load_config()
    stem = Path(paper["new_filename"]).stem
    return cfg.research_root / "Reviews" / paper["category"] / f"{stem}.fulltext.json"


# ---------- _reviews.csv ----------

def _reviews_csv_path() -> Path:
    cfg = load_config()
    return cfg.research_root / "_reviews.csv"


def append_review_row(row: dict) -> None:
    """Append a row to _reviews.csv (creates file with header on first call)."""
    path = _reviews_csv_path()
    existed = path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a" if existed else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEWS_FIELDNAMES)
        if not existed:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in REVIEWS_FIELDNAMES})


# ---------- review.md write ----------

_REVIEW_TEMPLATE = """# {title}

**Authors:** {author}
**Year:** {year}  ·  **Category:** {category}  ·  **Doc type:** {doc_type}
**Source:** [{filename}](../../{source_rel})
**Reviewed:** {review_date}
**Focus criteria:** {focus_display}

---

## Objective summary

{objective_summary}

## Analytical review

{analytical_review}

### Bias and methodology flags
{bias_flags_md}

### Candidate quotes
{candidate_quotes_md}

---

## BRAINS commentary

### Alignment
{brains_alignment}

### Friction
{brains_friction}

### Evidence base fit
{brains_evidence_base_fit}

### Candidate quotes for BRAINS use
{brains_candidate_quotes_md}

---

## Draft posts

- **LinkedIn:** {linkedin_id}
- **Bluesky:** {bluesky_id}

## Next action

{next_action_display}
"""


def write_review_file(
    *,
    paper: dict,
    review_date: str,
    focus_criteria: str,
    sections: dict,
    draft_ids: dict,
    next_action: str,
) -> Path:
    """Render the review.md template to the canonical path; returns the written path."""
    out = review_path_for(paper)
    out.parent.mkdir(parents=True, exist_ok=True)
    source_rel = paper["new_path"]
    text = _REVIEW_TEMPLATE.format(
        title=paper.get("title", paper["new_filename"]),
        author=paper.get("author", ""),
        year=paper.get("year", ""),
        category=paper.get("category", ""),
        doc_type=paper.get("doc_type", ""),
        filename=paper["new_filename"],
        source_rel=source_rel,
        review_date=review_date,
        focus_display=focus_criteria or "balanced review",
        objective_summary=sections.get("objective_summary", ""),
        analytical_review=sections.get("analytical_review", ""),
        bias_flags_md=sections.get("bias_flags_md", "- (none)"),
        candidate_quotes_md=sections.get("candidate_quotes_md", "(none)"),
        brains_alignment=sections.get("brains_alignment", ""),
        brains_friction=sections.get("brains_friction", ""),
        brains_evidence_base_fit=sections.get("brains_evidence_base_fit", ""),
        brains_candidate_quotes_md=sections.get("brains_candidate_quotes_md", "- (none)"),
        linkedin_id=draft_ids.get("linkedin") or "not drafted",
        bluesky_id=draft_ids.get("bluesky") or "not drafted",
        next_action_display=next_action or "-",
    )
    out.write_text(text, encoding="utf-8")
    return out


def write_scanned_stub(*, paper: dict, review_date: str) -> Path:
    """Stub review.md for a scanned PDF with no extractable text."""
    out = review_path_for(paper)
    out.parent.mkdir(parents=True, exist_ok=True)
    text = (
        f"# {paper.get('title', paper['new_filename'])}\n\n"
        f"**Authors:** {paper.get('author', '')}\n"
        f"**Year:** {paper.get('year', '')}  ·  **Category:** {paper.get('category', '')}  ·  "
        f"**Doc type:** {paper.get('doc_type', '')}\n"
        f"**Reviewed:** {review_date}\n\n"
        f"---\n\n"
        f"## Status\n\n"
        f"Scanned PDF — manual review required. No text extraction available.\n"
    )
    out.write_text(text, encoding="utf-8")
    return out


# ---------- content draft handoff ----------

_CT_PATTERN = re.compile(r"^CT(\d{3,})$")


def next_ct_id(content_root: Path) -> str:
    """Return the next CTNNN id by reading content_calendar.csv if present, else CT001."""
    calendar = content_root / "content_calendar.csv"
    if not calendar.exists():
        return "CT001"
    max_n = 0
    with calendar.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            m = _CT_PATTERN.match(row.get("id", "").strip())
            if m:
                max_n = max(max_n, int(m.group(1)))
    return f"CT{max_n + 1:03d}"


_DRAFT_TEMPLATE = """# {headline}

**Channel:** {channel}  ·  **Brand:** {brand}  ·  **Format:** {format_}
**Topic:** {topic}

---

{body}

---

### Notes
{notes_md}
"""


def write_content_draft(
    *,
    content_root: Path,
    ct_id: str,
    channel: str,
    brand: str,
    format_: str,
    topic: str,
    headline: str,
    body: str,
    notes_md: str,
    author: str,
) -> dict | None:
    """Write CT00X.md draft + append a content_calendar.csv row. Returns None if drafts dir missing."""
    drafts_dir = content_root / "drafts"
    if not drafts_dir.exists():
        print(
            f"WARNING: content drafts dir not found at {drafts_dir} - draft handoff skipped",
            file=sys.stderr,
        )
        return None
    draft_path = drafts_dir / f"{ct_id}.md"
    text = _DRAFT_TEMPLATE.format(
        headline=headline, channel=channel, brand=brand, format_=format_,
        topic=topic, body=body, notes_md=notes_md,
    )
    draft_path.write_text(text, encoding="utf-8")

    calendar = content_root / "content_calendar.csv"
    existed = calendar.exists()
    with calendar.open("a" if existed else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CONTENT_CALENDAR_FIELDNAMES)
        if not existed:
            writer.writeheader()
        writer.writerow({
            "id": ct_id, "publish_date": "", "channel": channel, "brand": brand,
            "format": format_, "topic": topic, "headline": headline,
            "status": "drafted",
            "draft_link": str(draft_path.relative_to(content_root)).replace("\\", "/"),
            "published_link": "", "author": author, "notes": "",
        })
    return {"draft_path": draft_path}
```

- [ ] **Step 2: Run, expect all 15 review tests pass**

Run:
```powershell
cd 'c:\Brains_Research_Skill'
.\.venv\Scripts\python.exe -m pytest tests/test_review.py -v
```

Expected: 15 passed.

- [ ] **Step 3: Run the full suite to check nothing regressed**

Run:
```powershell
cd 'c:\Brains_Research_Skill'
.\.venv\Scripts\python.exe -m pytest -v
```

Expected: all passed (21 from v1.0.0 + 2 new config tests + 6 extract_full + 15 review = 44 total).

- [ ] **Step 4: Commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add scripts/config.py scripts/review.py tests/test_config.py tests/test_review.py
git -C 'c:\Brains_Research_Skill' commit -m "Add scripts/review.py + content_drafts_dir config with tests"
```

---

## Phase D — Reference templates

Goal: Three reference files Claude loads on demand during the review flow.

### Task D1: `references/review-template.md`

**Files:**
- Create: `c:\Brains_Research_Skill\references\review-template.md`

- [ ] **Step 1: Write the template guide**

Content:
```markdown
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
- `include in BRAINS evidence base — high-quality empirical work`
- `re-review in 6 months when follow-up study is published`
- `do not draft a post yet — too preliminary`

Defaults to `-` if nothing useful.
```

### Task D2: `references/linkedin-template.md`

**Files:**
- Create: `c:\Brains_Research_Skill\references\linkedin-template.md`

- [ ] **Step 1: Write the LinkedIn template guide**

Content:
```markdown
# LinkedIn draft template (BRAINS long post)

The LinkedIn draft is a `CT00X.md` file handed off to `brains-content` for calendar management. The skill writes it via `scripts.review.write_content_draft`. Below is the body Claude generates and passes as the `body` argument.

## Voice rules (from brains-content)

- 200–400 words
- Open with a specific scene or stat — never "I'm excited to announce" or "Today I want to talk about"
- One specific claim or stat per post
- Build the why
- End with a CTA or question
- 2–3 deliberate hashtags
- No emojis (BRAINS parent default)
- Identity-first language
- No deficit framing
- Always cite the source paper

## Brand rules (from brains-brand — load before drafting)

- Protected phrases used verbatim where applicable (load brains-brand for the list)
- BRAINS, BRAINS Certified, BRAINS Trust, BRAINS Incubator capitalisation
- No italics for emphasis, no justified text (does not apply to plain LinkedIn but stays the brand habit)
- No AI-generated images of people
- Do not reveal BRAINS scoring criteria internals

## Body structure (≈200–400 words)

```
{Specific opening: a stat, a finding, a quote from the paper. One sentence, two max.}

{Two or three short paragraphs that explain what the paper shows and why it matters. Pull one or two of the candidate quotes from the review's "Candidate quotes for BRAINS use" section. Stay close to what the paper actually says — no extrapolation beyond the evidence.}

{A neuro-affirming reframe or BRAINS-aligned implication. One short paragraph.}

{CTA or question to drive engagement. One sentence. Examples:
- "What would you change in how AI tools assess crisis risk for autistic users?"
- "Read the paper here: [link]"
- "If you've seen this play out differently in practice, I'd like to hear it."}

{Hashtags — 2 to 3, deliberate. Examples for BRAINS:
#NeuroaffirmingAI #BRAINSCertified #AIaccountability}
```

## Source citation

Always include the paper attribution at the end of the body, before hashtags, in this format:

```
Source: {Author surnames} ({year}). "{Paper title}". {Venue or arXiv ID}.
```

## CT00X.md fields the skill provides

The skill (`scripts.review.write_content_draft`) sets these fields in the `CT00X.md` frontmatter / header automatically — Claude does not need to write them:

- channel: LinkedIn
- brand: BRAINS (or BRAINS Trust / BRAINS Incubator if specified by focus criteria)
- format: long post
- topic: the paper title
- headline: the same opening line as the post body

## Notes block

Claude provides a `notes_md` argument containing a bulleted list:
- the source citation
- intended hashtags
- any image / asset needed
- "from /brains-research-review of {paper filename}"
```

### Task D3: `references/bluesky-template.md`

**Files:**
- Create: `c:\Brains_Research_Skill\references\bluesky-template.md`

- [ ] **Step 1: Write the Bluesky template guide**

Content:
```markdown
# Bluesky draft template (BRAINS Bluesky account)

The Bluesky draft is a `CT00X.md` file handed off to `brains-content` for calendar management. Bluesky has a 300-character hard limit per post. The skill writes it via `scripts.review.write_content_draft`.

## Voice rules

- Maximum 300 characters total (including the source link). Count carefully.
- One specific claim per post.
- Identity-first language.
- No deficit framing.
- No emojis (BRAINS parent default).
- Always include a source link.
- 1–2 hashtags maximum. Bluesky norms tolerate fewer hashtags than LinkedIn.

## Brand rules (from brains-brand)

- Protected phrases used verbatim if used
- BRAINS, BRAINS Certified, BRAINS Trust, BRAINS Incubator capitalisation
- Do not reveal BRAINS scoring criteria internals

## Body structure

```
{One specific claim or finding from the paper, in plain language. 100–150 chars.}

{Source: short paper attribution + link. ~80–120 chars. Example: "Pichowicz et al., 2025: https://doi.org/..."}

{1–2 hashtags. ~30 chars.}
```

## Character budget

- Claim: 100–150 chars
- Source citation: 80–120 chars
- Hashtags: 20–30 chars
- **Total: ≤300 chars (verified by the skill before writing)**

If the draft exceeds 300 characters, shorten the claim — never truncate the source citation.

## CT00X.md fields

- channel: Bluesky
- brand: BRAINS (or sub-brand)
- format: short post
- topic: paper title
- headline: the claim line (≤150 chars)

## Notes block

`notes_md` includes:
- the source URL (DOI preferred)
- character count of the final draft
- "from /brains-research-review of {paper filename}"
```

### Task D4: Commit reference templates

- [ ] **Step 1: Stage and commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add references/review-template.md references/linkedin-template.md references/bluesky-template.md
git -C 'c:\Brains_Research_Skill' commit -m "Add references/review-template.md, linkedin-template.md, bluesky-template.md"
```

---

## Phase E — Slash command

Goal: The `/brains-research-review` markdown that orchestrates the 7-step flow.

### Task E1: Write `commands/brains-research-review.md`

**Files:**
- Create: `c:\Brains_Research_Skill\commands\brains-research-review.md`

- [ ] **Step 1: Write the command**

Content:
```markdown
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
4. Resolve content root from the config: `cfg.content_drafts_dir.parent` (the drafts subfolder is the actual write target). If `cfg.content_drafts_dir` is None or unreachable, skip with a warning — review still completes; the user is told the draft was not written.
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
```

### Task E2: Commit the slash command

- [ ] **Step 1: Stage and commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add commands/brains-research-review.md
git -C 'c:\Brains_Research_Skill' commit -m "Add /brains-research-review slash command (7-step flow)"
```

---

## Phase F — SKILL.md update + config example

Goal: Update SKILL.md with the new command and clauses; add optional `content_drafts_dir` to config example.

### Task F1: Update `SKILL.md`

**Files:**
- Modify: `c:\Brains_Research_Skill\SKILL.md`

- [ ] **Step 1: Add the new command row to the commands table**

Find:
```markdown
| Command | Purpose |
|---|---|
| `/brains-research-process` | The full ingest workflow. Extract → dedupe → categorise → rename → file → append catalog. |
| `/brains-research-status` | Read-only summary: counts by category, recent additions, integrity check. |
```

Replace with:
```markdown
| Command | Purpose |
|---|---|
| `/brains-research-process` | The full ingest workflow. Extract → dedupe → categorise → rename → file → append catalog. |
| `/brains-research-status` | Read-only summary: counts by category, recent additions, integrity check. |
| `/brains-research-review` | Per-paper review: objective summary, analytical review, BRAINS commentary, optional LinkedIn + Bluesky drafts handed off to `brains-content`. Persists to `Reviews/<Category>/<stem>.review.md` and `_reviews.csv`. |
```

- [ ] **Step 2: Add new behavioural clauses after the existing ones**

Find the line:
```markdown
**Confirm before destructive moves.** The pipeline reports its plan before applying it. If the user says "dry run" or "preview", run with `--dry-run` and report what would have moved.
```

Append directly after it:
```markdown

**Reviews are append-history.** A paper can be re-reviewed; the `.review.md` is overwritten with the latest analysis but a new row is appended to `_reviews.csv` so the history is preserved.

**No publishing.** LinkedIn and Bluesky outputs from `/brains-research-review` are drafts handed off to `brains-content`. The skill never posts.

**Brand fallback.** If `brains-brand` is not installed, `/brains-research-review` writes a generic neuro-affirming commentary and notes the fallback in the review file. The skill still works for non-BRAINS users.
```

- [ ] **Step 3: Add the new reference files to the References section**

Find:
```markdown
- `references/taxonomy.md`
- `references/filename-rules.md`
- `references/org-abbreviations.md`
- `references/edge-cases.md`
```

Replace with:
```markdown
- `references/taxonomy.md`
- `references/filename-rules.md`
- `references/org-abbreviations.md`
- `references/edge-cases.md`
- `references/review-template.md` (loaded during `/brains-research-review`)
- `references/linkedin-template.md` (loaded during `/brains-research-review` if a LinkedIn draft is requested)
- `references/bluesky-template.md` (loaded during `/brains-research-review` if a Bluesky draft is requested)
```

- [ ] **Step 4: Bump the version in frontmatter**

Find:
```markdown
version: 1.0.0
```

Replace with:
```markdown
version: 1.1.0
```

### Task F2: Update `config.json.example`

**Files:**
- Modify: `c:\Brains_Research_Skill\config.json.example`

- [ ] **Step 1: Replace the entire file**

Content:
```json
{
  "research_root": "\\\\192.168.1.101\\Singularity_Backup\\Research",
  "inbox_dir": "to be reviwed",
  "completed_dir": "Completed Review",
  "duplicates_dir": "_duplicates",
  "catalog_csv": "_catalog.csv",
  "extract_pages": 2,
  "extract_max_chars": 3000,
  "content_drafts_dir": "C:\\Users\\matth\\Proton Drive\\Matthew Gell\\Shared with me\\06. Operations\\Admin\\03_Content"
}
```

Note: `content_drafts_dir` points at the content **root** (the parent of `drafts/`), matching how `write_content_draft` resolves the drafts subfolder and `content_calendar.csv` sibling.

### Task F3: Commit Phase F

- [ ] **Step 1: Stage and commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add SKILL.md config.json.example
git -C 'c:\Brains_Research_Skill' commit -m "Update SKILL.md + config.json.example for v1.1.0 (new command, content_drafts_dir)"
```

---

## Phase G — Metadata bumps

Goal: STATUS.yml, CHANGELOG, README updated for v1.1.0.

### Task G1: Update `STATUS.yml`

**Files:**
- Modify: `c:\Brains_Research_Skill\STATUS.yml`

- [ ] **Step 1: Replace the entire file**

Content:
```yaml
name: brains-research
version: 1.1.0
released: 2026-05-29
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
  - /brains-research-review
```

### Task G2: Update `CHANGELOG.md`

**Files:**
- Modify: `c:\Brains_Research_Skill\CHANGELOG.md`

- [ ] **Step 1: Prepend a new v1.1.0 section under the heading**

Find:
```markdown
## [1.0.0] — 2026-05-29
```

Insert above it:
```markdown
## [1.1.0] — 2026-05-29

### Added
- `/brains-research-review` slash command — per-paper review workflow producing an objective summary, an analytical review, BRAINS commentary, and optional LinkedIn and Bluesky drafts handed off to `brains-content`.
- `scripts/extract_full.py` — full-text PDF extraction with per-paper JSON cache, mtime-invalidated.
- `scripts/review.py` — paper selection (filename / partial / category / picker), `_reviews.csv` append-only ledger I/O, `.review.md` writer, content-draft handoff.
- `references/review-template.md`, `references/linkedin-template.md`, `references/bluesky-template.md` — section guides loaded on demand during the review flow.
- Optional `content_drafts_dir` config key (defaults to Matthew's BRAINS content folder). The review command writes `CT00X.md` drafts and appends to `content_calendar.csv`. If the directory is unreachable, the review still completes; only the draft handoff is skipped.
- `_reviews.csv` ledger on the share, 13 columns: `new_path, category, paper_year, paper_author, paper_title, review_path, review_date, focus_criteria, linkedin_draft_id, bluesky_draft_id, bias_flags, tags, next_action`. Append-only.
- Stub `.review.md` + `bias_flags=scanned_pdf` row for scanned image-only PDFs — leaves an audit trail.
- Test fixtures and test files (`tests/test_extract_full.py`, `tests/test_review.py`, two new `test_config.py` cases). New `reportlab` dev dependency for generating the multi-page fixture PDF.

### Changed
- `scripts/config.py` — `Config` dataclass gains optional `content_drafts_dir: Path | None`.

### Migration notes
- v1.0.0 users upgrade by `git pull` and re-running `install.ps1` (or platform equivalent).
- Existing `_catalog.csv` and v1.0.0 commands are untouched.

```

(Note the blank line at the end — it separates v1.1.0 from the existing v1.0.0 section.)

### Task G3: Update `README.md`

**Files:**
- Modify: `c:\Brains_Research_Skill\README.md`

- [ ] **Step 1: Bump the status line**

Find:
```markdown
v1.0.0 — initial release. Two slash commands: `/brains-research-process` (ingest) and `/brains-research-status` (read-only summary).
```

Replace with:
```markdown
v1.1.0 — adds `/brains-research-review`. Three slash commands now live.
```

- [ ] **Step 2: Add the new command to the "what it does" list**

Find:
```markdown
- **`/brains-research-status`** — read-only summary: total catalogued, count by category, recent additions, inbox and duplicate counts, plus an integrity check (catalog rows pointing at missing files; files on disk not in the catalog). **(live)**
```

Append directly after it:
```markdown
- **`/brains-research-review`** — per-paper review workflow. Asks for optional focus criteria, then produces an objective summary, an analytical review (strengths, weaknesses, methodology flags, candidate quotes), and BRAINS-specific commentary via `brains-brand`. Optionally drafts a LinkedIn long post and a Bluesky short post (≤300 chars), handed off to `brains-content`. Persists to `Reviews/<Category>/<stem>.review.md` and `_reviews.csv`. **(live)**
```

### Task G4: Commit Phase G

- [ ] **Step 1: Stage and commit**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' add STATUS.yml CHANGELOG.md README.md
git -C 'c:\Brains_Research_Skill' commit -m "Bump to v1.1.0 (STATUS, CHANGELOG, README)"
```

---

## Phase H — Re-install + end-to-end smoke test

Goal: Re-run the installer so the local skill bundle picks up v1.1.0; verify against the real share.

### Task H1: Re-run the installer

- [ ] **Step 1: Run install.ps1**

Run:
```powershell
& 'c:\Brains_Research_Skill\install\install.ps1' -ResearchRoot '\\192.168.1.101\Singularity_Backup\Research'
```

Expected: prints `config.json already exists — keeping it`, then `Skill installed at: C:\Users\matth\.claude\skills\brains-research`, then `Slash commands installed at: C:\Users\matth\.claude\commands`, then `Done.`.

- [ ] **Step 2: Confirm the new command is registered**

Run:
```powershell
Get-ChildItem 'C:\Users\matth\.claude\commands\brains-research-review.md'
```

Expected: file exists.

- [ ] **Step 3: Confirm the new scripts are installed**

Run:
```powershell
Get-ChildItem 'C:\Users\matth\.claude\skills\brains-research\scripts\extract_full.py','C:\Users\matth\.claude\skills\brains-research\scripts\review.py'
```

Expected: both files exist.

### Task H2: Run full pytest one more time

- [ ] **Step 1: Full suite**

Run:
```powershell
cd 'c:\Brains_Research_Skill'
.\.venv\Scripts\python.exe -m pytest -v
```

Expected: 44 passed (21 v1.0.0 + 2 new config + 6 extract_full + 15 review).

### Task H3: Smoke-test against a real catalogued paper

- [ ] **Step 1: Confirm a target paper exists**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -c @"
from scripts.review import select_paper
p = select_paper('Pichowicz')
print('Found:', p['new_filename'] if p else 'NONE')
print('Category:', p['category'] if p else 'NONE')
print('Path:', p['new_path'] if p else 'NONE')
"@
```

Expected: prints `Found: 2025 - Pichowicz - ... .pdf`, `Category: AI-Mental-Health`, `Path: Completed Review/AI-Mental-Health/2025 - Pichowicz - ... .pdf`.

- [ ] **Step 2: Smoke-test the extract_full cache against the real paper**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -c @"
from scripts.review import select_paper, fulltext_cache_path_for
from scripts.extract_full import load_or_extract
from scripts.config import load_config
cfg = load_config()
p = select_paper('Pichowicz')
pdf = cfg.research_root / p['new_path']
cache = fulltext_cache_path_for(p)
print('PDF exists:', pdf.exists())
print('Cache target:', cache)
pages = load_or_extract(pdf, cache)
print(f'Got {len(pages)} pages; first page first 80 chars: {repr(pages[0][:80])}')
print('Cache exists now:', cache.exists())
"@
```

Expected: prints `PDF exists: True`, then the cache path, then `Got 9 pages` (or whatever the actual page count is), then the first 80 chars of page 1, then `Cache exists now: True`. Verifies the cache write also works against the UNC share.

- [ ] **Step 3: Invoke `/brains-research-review Pichowicz` in a fresh Claude session and verify the artefacts**

In a fresh Claude Code session in `\\192.168.1.101\Singularity_Backup\Research`, invoke `/brains-research-review Pichowicz`. Walk through the prompts (focus = Enter to skip, draft posts = `both`).

Expected:
- `Reviews/AI-Mental-Health/2025 - Pichowicz - ... .review.md` exists with all six template sections populated
- `Reviews/AI-Mental-Health/2025 - Pichowicz - ... .fulltext.json` exists
- `_reviews.csv` exists at the research root with 1 row
- `CT001.md` and `CT002.md` (or whatever IDs were assigned) exist in `06. Operations/Admin/03_Content/drafts/` if the content folder is reachable; otherwise the warning was reported
- `content_calendar.csv` has two new `status=drafted` rows (if drafts wrote)
- BRAINS commentary uses identity-first language, no protected-phrase violations, no rubric-internals references

- [ ] **Step 4: Verify integrity is unaffected**

Run:
```powershell
& 'c:\Brains_Research_Skill\.venv\Scripts\python.exe' -m scripts.status 2>&1 | Select-Object -First 25
```

Expected: still `total: 105`, `missing_files: []`, `orphan_files: []`. The Reviews/ folder does not count as catalog content; `_reviews.csv` is not catalog and is not integrity-checked by `status` in v1.1.0.

### Task H4: Commit any small fixes discovered during smoke test

- [ ] **Step 1: If any issue was found in H3 step 3, fix it inline (in the slash command markdown, a reference file, or a script)**

- [ ] **Step 2: Re-run pytest**

Run:
```powershell
cd 'c:\Brains_Research_Skill'
.\.venv\Scripts\python.exe -m pytest -v
```

Expected: all green.

- [ ] **Step 3: Commit the fix(es)**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' status --short
git -C 'c:\Brains_Research_Skill' add <files>
git -C 'c:\Brains_Research_Skill' commit -m "fix: <one-line description from smoke test>"
```

If no fixes were needed, skip this task entirely.

---

## Phase I — GitHub release v1.1.0

Goal: Tag and push v1.1.0.

### Task I1: Push main + tag v1.1.0

- [ ] **Step 1: Push main**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' push origin main
```

Expected: pushes the v1.1.0 commit chain.

- [ ] **Step 2: Tag and push the tag**

Run:
```powershell
git -C 'c:\Brains_Research_Skill' tag -a v1.1.0 -m "v1.1.0 - /brains-research-review"
git -C 'c:\Brains_Research_Skill' push origin v1.1.0
```

- [ ] **Step 3: Create the release**

Run:
```powershell
gh release create v1.1.0 --repo shard-BRAINS/BRAINS-Research-Skill --title "v1.1.0 - /brains-research-review" --notes "Adds `/brains-research-review` — per-paper review workflow producing an objective summary, an analytical review, and BRAINS commentary, with optional LinkedIn and Bluesky draft handoff to brains-content. Reviews persist to Reviews/<Category>/<stem>.review.md and the new append-only _reviews.csv ledger (13 columns). New scripts/extract_full.py with per-paper JSON cache. Optional content_drafts_dir config. 44/44 tests passing. No breaking changes to v1.0.0."
```

Expected: returns the release URL.

---

## Acceptance criteria (from the spec)

Re-check each before marking the plan complete:

1. `/brains-research-review` runs cleanly on Matthew's Windows machine against any paper in `_catalog.csv`. — verified by Task H3 step 3.
2. Picker mode (no argument) lists the 10 most recent additions and accepts a selection. — covered by the `list_recent_papers` test and the slash command's step 1.
3. Focus-criteria prompt fires every run; Enter / "no" produces a balanced review. — covered by the slash command's step 2 and the review-template guidance.
4. Review file is written at `Reviews/<Category>/<stem>.review.md` with all six template sections populated. — verified by `test_write_review_file_writes_markdown` and Task H3 step 3.
5. `_reviews.csv` exists, schema matches §3.4 of the spec, has one row per review run. — verified by `test_append_review_row_creates_file_with_header` and `test_append_review_row_is_append_only`.
6. Full-text cache is created on first run; second run within a day uses it (verifiable by mtime). — verified by `test_load_or_extract_uses_cache_when_fresh` and Task H3 step 2.
7. LinkedIn / Bluesky drafts (when requested) land as `CT00X.md` files in the configured `content_drafts_dir` with `status=drafted` rows in `content_calendar.csv`. — verified by `test_write_content_draft_writes_md_and_appends_calendar` and Task H3 step 3.
8. BRAINS commentary uses identity-first language and never references BRAINS rubric internals. — enforced by the slash command's air-gap rule and the review-template reference; verified manually in Task H3 step 3.
9. Brand fallback path works: deleting `~/.claude/skills/brains-brand` and re-running produces a generic neuro-affirming commentary with a noted fallback. — covered by the slash command's step 6; can be manually verified post-release.
10. Full pytest passes (existing 21 v1.0.0 tests + new `extract_full` and `review` tests = 44 total). — verified by Task H2.
11. CHANGELOG, README, SKILL.md, STATUS.yml updated for v1.1.0; tagged and released on GitHub. — verified by Phase G + Task I1.
