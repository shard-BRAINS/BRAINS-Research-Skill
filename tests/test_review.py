"""Tests for scripts.review."""
import csv
import json
from pathlib import Path

from scripts.review import (
    REVIEWS_FIELDNAMES,
    append_review_row,
    list_recent_papers,
    next_ct_id,
    review_path_for,
    select_paper,
    write_content_draft,
    write_review_file,
    write_scanned_stub,
)


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


def test_review_path_for_strips_pdf_and_adds_review_md(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    expected = (
        mock_research_root / "Reviews" / "AI-General" /
        "2024 - Smith - A study on X.review.md"
    )
    assert review_path_for(CATALOG_ROW_1) == expected


def test_append_review_row_creates_file_with_header(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    row = {f: "" for f in REVIEWS_FIELDNAMES}
    row["new_path"] = CATALOG_ROW_1["new_path"]
    row["review_date"] = "2026-05-29"
    append_review_row(row)
    csv_path = mock_research_root / "_reviews.csv"
    assert csv_path.exists()
    text = csv_path.read_text(encoding="utf-8")
    assert "new_path" in text
    assert CATALOG_ROW_1["new_path"] in text


def test_append_review_row_is_append_only(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    csv_path = mock_research_root / "_reviews.csv"
    for date in ["2026-05-29", "2026-06-01"]:
        row = {f: "" for f in REVIEWS_FIELDNAMES}
        row["new_path"] = CATALOG_ROW_1["new_path"]
        row["review_date"] = date
        append_review_row(row)
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    assert len(rows) == 2
    assert rows[0]["review_date"] == "2026-05-29"
    assert rows[1]["review_date"] == "2026-06-01"


def test_write_review_file_writes_markdown(mock_research_root, config_file, monkeypatch):
    monkeypatch.setenv("BRAINS_RESEARCH_CONFIG", str(config_file))
    write_review_file(
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
    write_scanned_stub(paper=CATALOG_ROW_1, review_date="2026-05-29")
    out = mock_research_root / "Reviews" / "AI-General" / "2024 - Smith - A study on X.review.md"
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "Scanned PDF" in text
    assert "manual review required" in text


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
