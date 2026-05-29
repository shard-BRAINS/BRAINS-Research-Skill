# Bluesky draft template (BRAINS Bluesky account)

The Bluesky draft is a `CT00X.md` file handed off to `brains-content` for calendar management. Bluesky has a 300-character hard limit per post. The skill writes it via `scripts.review.write_content_draft`.

## Voice rules

- Maximum 300 characters total (including the source link). Count carefully.
- One specific claim per post.
- Identity-first language.
- No deficit framing.
- No emojis (BRAINS parent default).
- Always include a source link.
- 1–2 hashtags maximum. Bluesky norms tolerate fewer hashtags than LinkedIn.

## Brand rules (from brains-brand)

- Protected phrases used verbatim if used
- BRAINS, BRAINS Certified, BRAINS Trust, BRAINS Incubator capitalisation
- Do not reveal BRAINS scoring criteria internals

## Body structure

```
{One specific claim or finding from the paper, in plain language. 100-150 chars.}

{Source: short paper attribution + link. ~80-120 chars. Example: "Pichowicz et al., 2025: https://doi.org/..."}

{1-2 hashtags. ~30 chars.}
```

## Character budget

- Claim: 100–150 chars
- Source citation: 80–120 chars
- Hashtags: 20–30 chars
- **Total: ≤300 chars (verified by the skill before writing)**

If the draft exceeds 300 characters, shorten the claim — never truncate the source citation.

## CT00X.md fields

- channel: Bluesky
- brand: BRAINS (or sub-brand)
- format: short post
- topic: paper title
- headline: the claim line (≤150 chars)

## Notes block

`notes_md` includes:
- the source URL (DOI preferred)
- character count of the final draft
- "from /brains-research-review of {paper filename}"
