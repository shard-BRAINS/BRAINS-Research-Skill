---
description: Catalogue new PDFs in the BRAINS research inbox — extract, dedupe, categorise, rename, file into Completed Review/, append _catalog.csv
---

# /brains-research-process

Process whatever PDFs are currently sitting in the inbox.

**Paths come from `config.json` at the skill root.** Use `python -m scripts.config` to inspect resolved paths if needed. The default `research_root` is `\\192.168.1.101\Singularity_Backup\Research`.

**Locked references — load these before deciding any category, filename, or edge-case treatment:**

- `references/taxonomy.md` — the 10 locked categories
- `references/filename-rules.md` — canonical filename format
- `references/org-abbreviations.md` — institutional author abbreviations
- `references/edge-cases.md` — scanned PDFs, collisions, non-PDFs, duplicates

## Steps

1. **Empty check.** Glob the inbox. If no PDFs, report `No new files.` and stop.

2. **Extract.** Run `python -m scripts.extract_all` from the skill root (or anywhere — the script resolves paths via config). This writes `_extract_all.json` to the Research root with `{filename: {size, text, pages, error}}` for every PDF in the inbox.

3. **Dedupe against existing catalog.** For each new file, compare its byte size against every file already in `Completed Review/**`. If an exact byte match exists, move the new file to `_duplicates/` and skip it (do not include in the rename plan). Use:
   ```powershell
   Get-ChildItem -Recurse '<research_root>\Completed Review' -Filter *.pdf | Where-Object Length -eq <N>
   ```
   or the equivalent `find` on macOS / Linux.

4. **Read and categorise.** Read `_extract_all.json`. If it is larger than 25 KB, split into chunks of approximately 18 entries and read sequentially. For each non-duplicate file, extract from the text:
   - `year` (four-digit, or `nd` if not findable)
   - `author` (first author surname, or organisation abbreviation from `references/org-abbreviations.md`)
   - `title` (5–15 words, descriptive)
   - `category` (must be one of the 10 in `references/taxonomy.md` — never invent new categories silently)
   - `doc_type` (e.g. `Journal article`, `Preprint`, `Conference paper`, `Institutional report`, `Legislation`, `White paper`, `Master thesis`, `PhD thesis`)

5. **Build filenames.** Apply `references/filename-rules.md`. Canonical form: `YYYY - ShortAuthor - Descriptive title.pdf`.

6. **Write `_rename_plan.json`** at the Research root, overwriting any prior plan. Schema:
   ```json
   {
     "<original_filename>": {
       "category": "<one of the 10>",
       "new_name": "YYYY - ShortAuthor - Descriptive title.pdf",
       "year": "YYYY",
       "author": "ShortAuthor",
       "title": "Descriptive title",
       "doc_type": "Journal article"
     }
   }
   ```

7. **Apply.** Run `python -m scripts.apply_renames` (no flags). Moves files and appends to `_catalog.csv`.

8. **Report back.** Concise summary:
   - N moved by category
   - N quarantined as duplicates (with names)
   - Any files where extraction failed or year / author was uncertain (flag these for the user to review)
   - Any new organisation abbreviations added to `references/org-abbreviations.md` during this run

## Dry-run

If the user says "dry run" or "preview", run `python -m scripts.apply_renames --dry-run` instead of step 7. Report what would have moved.
