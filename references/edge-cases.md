# Edge cases

## Scanned or image-only PDFs (empty text extraction)

If `_extract_all.json` shows an empty `text` field for a file, do not guess at the title. Use:

- `year` — `nd`
- `author` — derived from filename if possible, otherwise the literal string `Unknown`
- `title` — taken from the original filename (cleaned), prefixed with `(text extraction failed - manual review needed)`
- `doc_type` — `Scanned PDF (manual review needed)`

Surface every such file to the user at the end of the run.

## Filename collisions in the destination

If `Completed Review/<Category>/<new_name>` already exists, `apply_renames.py` skips the move and reports the collision. Resolution is manual.

## Non-PDF files in the inbox

`.htm`, `.docx`, `.txt`, etc. are left in place. This skill only processes PDFs. Mention them in the report.

## Cross-cutting papers

See `taxonomy.md`. Pick the dominant axis.

## Byte-exact duplicates

If a new file matches an existing file in `Completed Review/**` by byte size, it is moved to `_duplicates/`. No fuzzy matching. False negatives are acceptable; false positives are not.

## Catalog repair

If the status report shows `missing_files` (catalog rows pointing at files that no longer exist) or `orphan_files` (files on disk not in the catalog), do not silently rewrite the catalog. Surface the integrity report to the user and let them decide.
