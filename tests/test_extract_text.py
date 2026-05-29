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
