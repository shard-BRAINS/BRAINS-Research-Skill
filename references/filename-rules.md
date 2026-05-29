# Canonical filename format

`YYYY - ShortAuthor - Descriptive title.pdf`

## Components

- **YYYY** — four-digit publication year. If not derivable from the text, use `nd` (no date). Do not guess.
- **ShortAuthor** — first author surname. For institutional reports without a personal author, use an organisation abbreviation from `org-abbreviations.md`.
- **Descriptive title** — five to fifteen words, lowercase except proper nouns and acronyms. Do not repeat the year inside the title.

## Forbidden characters in the title

Strip: `: / \ * ? " < > |`

## Examples

- `2024 - Jain - Source awareness alters perceptions of AI mental health responses.pdf`
- `2025 - Rizvi - Beyond keywords evaluating LLM classification of nuanced ableism.pdf`
- `2023 - WHO - Guidance on regulatory considerations for AI for health.pdf`
- `nd - PennState - Workforce inclusion brief.pdf`

## Collision handling

If a target filename already exists in the destination category folder, append ` (v2).pdf`, ` (v3).pdf` etc. The apply step reports collisions; it does not overwrite.
