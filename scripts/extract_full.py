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
