"""Extract first N pages of text from every PDF in the inbox, write to JSON."""
from __future__ import annotations

import io
import json
import logging
import sys
import warnings
from pathlib import Path

logging.getLogger("pypdf").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

from pypdf import PdfReader  # noqa: E402

from scripts.config import load_config  # noqa: E402


def _extract_one(pdf_path: Path, pages: int, max_chars: int) -> dict:
    info = {"size": pdf_path.stat().st_size, "text": "", "pages": 0, "error": None}
    try:
        reader = PdfReader(str(pdf_path))
        info["pages"] = len(reader.pages)
        n = min(pages, len(reader.pages))
        parts = []
        for i in range(n):
            try:
                parts.append(reader.pages[i].extract_text() or "")
            except Exception as e:
                parts.append(f"[page {i} error: {e}]")
        info["text"] = ("\n".join(parts).strip())[:max_chars]
    except Exception as e:
        info["error"] = str(e)
    return info


def build_extract_dict() -> dict:
    cfg = load_config()
    files = sorted(cfg.inbox_dir.glob("*.pdf"))
    return {
        p.name: _extract_one(p, cfg.extract_pages, cfg.extract_max_chars)
        for p in files
    }


def write_extracts() -> Path:
    cfg = load_config()
    data = build_extract_dict()
    out = cfg.research_root / "_extract_all.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> int:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    out = write_extracts()
    data = json.loads(out.read_text(encoding="utf-8"))
    print(f"Found {len(data)} PDFs", file=sys.stderr)
    print(f"Wrote {out}", file=sys.stderr)
    print(f"Total: {len(data)} entries, {out.stat().st_size:,} bytes", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
