"""Tests for scripts.config."""
import json

import pytest

from scripts.config import Config, ConfigError, load_config


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
    """If no path passed, the env var BRAINS_RESEARCH_CONFIG steers the lookup."""
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
