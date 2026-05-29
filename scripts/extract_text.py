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
