# Contributing to BRAINS Research Skill

Thanks for your interest. BRAINS is an Incubator and Trust focused on neuro-affirming AI; contributions that align with that mission are very welcome.

## Ground rules

- Identity-first language by default (`autistic researcher`, `neurodivergent participant`). Switch to person-first only if a contributor explicitly states that preference for their own content.
- No deficit framing of neurodivergence anywhere in code, comments, references, or docs.
- The locked taxonomy is doctrine. PRs that add a new category must come with rationale and a user-visible decision; do not add silently.
- The catalog is append-only. PRs that retroactively rewrite catalog rows will be rejected.

## Development setup

```bash
git clone https://github.com/shard-BRAINS/BRAINS-research-skill.git
cd BRAINS-research-skill
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
cp config.json.example config.json
# Edit config.json for your local Research folder
```

## Running tests

```bash
pytest -v
```

All tests must pass before a PR is reviewed.

## Linting

```bash
ruff check scripts tests
```

## Reporting bugs

Open an issue on the GitHub repository with:

- A description of what happened versus what you expected.
- The exact command you ran.
- The relevant section of `_catalog.csv` or `_extract_all.json` if applicable (redact any private content).

## Code of conduct

Be decent. Disrespect — particularly ableism, dehumanisation of neurodivergent people, or hostility toward contributors — is not tolerated.
