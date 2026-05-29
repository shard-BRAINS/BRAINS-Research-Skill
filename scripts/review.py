"""Paper selection, _reviews.csv ledger I/O, review.md writer, content-draft handoff."""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from scripts.config import load_config

REVIEWS_FIELDNAMES = [
    "new_path", "category", "paper_year", "paper_author", "paper_title",
    "review_path", "review_date", "focus_criteria",
    "linkedin_draft_id", "bluesky_draft_id",
    "bias_flags", "tags", "next_action",
]

CONTENT_CALENDAR_FIELDNAMES = [
    "id", "publish_date", "channel", "brand", "format",
    "topic", "headline", "status", "draft_link", "published_link",
    "author", "notes",
]


def _load_catalog_rows() -> list[dict]:
    cfg = load_config()
    if not cfg.catalog_csv.exists():
        return []
    with cfg.catalog_csv.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def select_paper(arg: str) -> dict | None:
    """Return the catalog row matching arg (exact filename or partial title), else None."""
    rows = _load_catalog_rows()
    needle = arg.strip().lower()
    for r in rows:
        if r.get("new_filename", "").lower() == needle:
            return r
    for r in rows:
        haystack = " ".join([
            r.get("new_filename", ""), r.get("title", ""), r.get("original_filename", ""),
        ]).lower()
        if needle and needle in haystack:
            return r
    return None


def list_recent_papers(n: int = 10, category: str | None = None) -> list[dict]:
    """Return the last n rows from the catalog, optionally filtered by category."""
    rows = _load_catalog_rows()
    if category:
        rows = [r for r in rows if r.get("category") == category]
    return rows[-n:]


def review_path_for(paper: dict) -> Path:
    """Reviews/<Category>/<stem>.review.md on the research root."""
    cfg = load_config()
    stem = Path(paper["new_filename"]).stem
    return cfg.research_root / "Reviews" / paper["category"] / f"{stem}.review.md"


def fulltext_cache_path_for(paper: dict) -> Path:
    cfg = load_config()
    stem = Path(paper["new_filename"]).stem
    return cfg.research_root / "Reviews" / paper["category"] / f"{stem}.fulltext.json"


def _reviews_csv_path() -> Path:
    cfg = load_config()
    return cfg.research_root / "_reviews.csv"


def append_review_row(row: dict) -> None:
    """Append a row to _reviews.csv (creates file with header on first call)."""
    path = _reviews_csv_path()
    existed = path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a" if existed else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REVIEWS_FIELDNAMES)
        if not existed:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in REVIEWS_FIELDNAMES})


_REVIEW_TEMPLATE = """# {title}

**Authors:** {author}
**Year:** {year}  ·  **Category:** {category}  ·  **Doc type:** {doc_type}
**Source:** [{filename}](../../{source_rel})
**Reviewed:** {review_date}
**Focus criteria:** {focus_display}

---

## Objective summary

{objective_summary}

## Analytical review

{analytical_review}

### Bias and methodology flags
{bias_flags_md}

### Candidate quotes
{candidate_quotes_md}

---

## BRAINS commentary

### Alignment
{brains_alignment}

### Friction
{brains_friction}

### Evidence base fit
{brains_evidence_base_fit}

### Candidate quotes for BRAINS use
{brains_candidate_quotes_md}

---

## Draft posts

- **LinkedIn:** {linkedin_id}
- **Bluesky:** {bluesky_id}

## Next action

{next_action_display}
"""


def write_review_file(
    *,
    paper: dict,
    review_date: str,
    focus_criteria: str,
    sections: dict,
    draft_ids: dict,
    next_action: str,
) -> Path:
    """Render the review.md template to the canonical path; returns the written path."""
    out = review_path_for(paper)
    out.parent.mkdir(parents=True, exist_ok=True)
    source_rel = paper["new_path"]
    text = _REVIEW_TEMPLATE.format(
        title=paper.get("title", paper["new_filename"]),
        author=paper.get("author", ""),
        year=paper.get("year", ""),
        category=paper.get("category", ""),
        doc_type=paper.get("doc_type", ""),
        filename=paper["new_filename"],
        source_rel=source_rel,
        review_date=review_date,
        focus_display=focus_criteria or "balanced review",
        objective_summary=sections.get("objective_summary", ""),
        analytical_review=sections.get("analytical_review", ""),
        bias_flags_md=sections.get("bias_flags_md", "- (none)"),
        candidate_quotes_md=sections.get("candidate_quotes_md", "(none)"),
        brains_alignment=sections.get("brains_alignment", ""),
        brains_friction=sections.get("brains_friction", ""),
        brains_evidence_base_fit=sections.get("brains_evidence_base_fit", ""),
        brains_candidate_quotes_md=sections.get("brains_candidate_quotes_md", "- (none)"),
        linkedin_id=draft_ids.get("linkedin") or "not drafted",
        bluesky_id=draft_ids.get("bluesky") or "not drafted",
        next_action_display=next_action or "-",
    )
    out.write_text(text, encoding="utf-8")
    return out


def write_scanned_stub(*, paper: dict, review_date: str) -> Path:
    """Stub review.md for a scanned PDF with no extractable text."""
    out = review_path_for(paper)
    out.parent.mkdir(parents=True, exist_ok=True)
    text = (
        f"# {paper.get('title', paper['new_filename'])}\n\n"
        f"**Authors:** {paper.get('author', '')}\n"
        f"**Year:** {paper.get('year', '')}  ·  **Category:** {paper.get('category', '')}  ·  "
        f"**Doc type:** {paper.get('doc_type', '')}\n"
        f"**Reviewed:** {review_date}\n\n"
        f"---\n\n"
        f"## Status\n\n"
        f"Scanned PDF - manual review required. No text extraction available.\n"
    )
    out.write_text(text, encoding="utf-8")
    return out


_CT_PATTERN = re.compile(r"^CT(\d{3,})$")


def next_ct_id(content_root: Path) -> str:
    """Return the next CTNNN id by reading content_calendar.csv if present, else CT001."""
    calendar = content_root / "content_calendar.csv"
    if not calendar.exists():
        return "CT001"
    max_n = 0
    with calendar.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            m = _CT_PATTERN.match(row.get("id", "").strip())
            if m:
                max_n = max(max_n, int(m.group(1)))
    return f"CT{max_n + 1:03d}"


_DRAFT_TEMPLATE = """# {headline}

**Channel:** {channel}  ·  **Brand:** {brand}  ·  **Format:** {format_}
**Topic:** {topic}

---

{body}

---

### Notes
{notes_md}
"""


def write_content_draft(
    *,
    content_root: Path,
    ct_id: str,
    channel: str,
    brand: str,
    format_: str,
    topic: str,
    headline: str,
    body: str,
    notes_md: str,
    author: str,
) -> dict | None:
    """Write CT00X.md draft + append a content_calendar.csv row. Returns None if drafts dir missing."""
    drafts_dir = content_root / "drafts"
    if not drafts_dir.exists():
        print(
            f"WARNING: content drafts dir not found at {drafts_dir} - draft handoff skipped",
            file=sys.stderr,
        )
        return None
    draft_path = drafts_dir / f"{ct_id}.md"
    text = _DRAFT_TEMPLATE.format(
        headline=headline, channel=channel, brand=brand, format_=format_,
        topic=topic, body=body, notes_md=notes_md,
    )
    draft_path.write_text(text, encoding="utf-8")

    calendar = content_root / "content_calendar.csv"
    existed = calendar.exists()
    with calendar.open("a" if existed else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CONTENT_CALENDAR_FIELDNAMES)
        if not existed:
            writer.writeheader()
        writer.writerow({
            "id": ct_id, "publish_date": "", "channel": channel, "brand": brand,
            "format": format_, "topic": topic, "headline": headline,
            "status": "drafted",
            "draft_link": str(draft_path.relative_to(content_root)).replace("\\", "/"),
            "published_link": "", "author": author, "notes": "",
        })
    return {"draft_path": draft_path}
