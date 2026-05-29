"""Tests for scripts.extract_full."""
import json
import time
from pathlib import Path

from scripts.extract_full import extract_full, is_scanned, load_or_extract

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
    """Missing PDF returns an empty list."""
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
    assert is_scanned(["", "", ""]) is True
    assert is_scanned(["", "some content", ""]) is False
    assert is_scanned([]) is True
