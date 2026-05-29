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
