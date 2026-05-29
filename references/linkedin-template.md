# LinkedIn draft template (BRAINS long post)

The LinkedIn draft is a `CT00X.md` file handed off to `brains-content` for calendar management. The skill writes it via `scripts.review.write_content_draft`. Below is the body Claude generates and passes as the `body` argument.

## Voice rules (from brains-content)

- 200–400 words
- Open with a specific scene or stat — never "I'm excited to announce" or "Today I want to talk about"
- One specific claim or stat per post
- Build the why
- End with a CTA or question
- 2–3 deliberate hashtags
- No emojis (BRAINS parent default)
- Identity-first language
- No deficit framing
- Always cite the source paper

## Brand rules (from brains-brand — load before drafting)

- Protected phrases used verbatim where applicable (load brains-brand for the list)
- BRAINS, BRAINS Certified, BRAINS Trust, BRAINS Incubator capitalisation
- No italics for emphasis, no justified text (does not apply to plain LinkedIn but stays the brand habit)
- No AI-generated images of people
- Do not reveal BRAINS scoring criteria internals

## Body structure (≈200–400 words)

```
{Specific opening: a stat, a finding, a quote from the paper. One sentence, two max.}

{Two or three short paragraphs that explain what the paper shows and why it matters. Pull one or two of the candidate quotes from the review's "Candidate quotes for BRAINS use" section. Stay close to what the paper actually says - no extrapolation beyond the evidence.}

{A neuro-affirming reframe or BRAINS-aligned implication. One short paragraph.}

{CTA or question to drive engagement. One sentence. Examples:
- "What would you change in how AI tools assess crisis risk for autistic users?"
- "Read the paper here: [link]"
- "If you've seen this play out differently in practice, I'd like to hear it."}

{Hashtags - 2 to 3, deliberate. Examples for BRAINS:
#NeuroaffirmingAI #BRAINSCertified #AIaccountability}
```

## Source citation

Always include the paper attribution at the end of the body, before hashtags, in this format:

```
Source: {Author surnames} ({year}). "{Paper title}". {Venue or arXiv ID}.
```

## CT00X.md fields the skill provides

The skill (`scripts.review.write_content_draft`) sets these fields in the `CT00X.md` frontmatter / header automatically — Claude does not need to write them:

- channel: LinkedIn
- brand: BRAINS (or BRAINS Trust / BRAINS Incubator if specified by focus criteria)
- format: long post
- topic: the paper title
- headline: the same opening line as the post body

## Notes block

Claude provides a `notes_md` argument containing a bulleted list:
- the source citation
- intended hashtags
- any image / asset needed
- "from /brains-research-review of {paper filename}"
