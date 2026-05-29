"""Tests for scripts.apply_renames."""
import csv
import json

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
