"""Tests for scripts.extract_all."""
import json

from scripts.extract_all import build_extract_dict, write_extracts


def test_build_extract_dict_handles_empty_inbox(
    mock_research_root, config_file, monkeypatch
):
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
