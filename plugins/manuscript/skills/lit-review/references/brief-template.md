# Strand Brief Template

A brief is the dispatch document for a single strand. It is the only context a parallel collection agent should need.

## File location

`_briefs/strand-<short-name>.md`, e.g. `_briefs/strand-A-tools.md`.

## Structure

```markdown
# Strand <X>, <Strand Title> (Phase 1 brief)

**Goal:** populate `research/collection/<strand>/` with at least <N> paper-cards covering <topic>.

## Scope

Cover <K> categories. Aim for breadth first, depth where it matters for the thesis.

### 1. <Category 1>
- <Bullet seed list of canonical works, tools, datasets, or standards>
- <Include explicit names, version pins where helpful>

### 2. <Category 2>
- ...

### <K>. <Category K>
- ...

## Per-entry deliverable

Create folder `research/collection/<strand>/<slug>/` containing:
- `card.md` from the schema (`type` ∈ {paper, dataset, tool, platform, standard}; `strand: <strand>`)
- `source.pdf` only if redistributable (open access, preprint, repo copy)
- `source.md` always required; markdown extraction or canonical README
- `meta.json` with provenance (DOI / URL, retrieved_at, license, sha256 if PDF archived, redistribution_ok)
- BibTeX entry appended to `research/collection/<strand>/<strand>.bib`
- One-line entry in `research/collection/<strand>/INDEX.md` under the right category heading

Use `opencite:opencite` for DOI lookup, PDF retrieval (where licensing permits), and PDF -> markdown conversion.

## Seed material

<Point to existing prior-work documents the agent should mine for entries, e.g.>
- `<path/to/existing-lit-review.md>`
- `<path/to/grant-strategy.tex>`

Imported entries must set `imported_from: <relative path>` in card.md.

## Skills to use

- `opencite:opencite` for paper retrieval, DOI lookup, BibTeX export
- `manuscript:manuscript-writing` for prose discipline (no em-dashes, abbreviations on first use)

## Acceptance criteria

- [ ] >= <N> entries across all <K> categories
- [ ] Each category has >= <M> entries
- [ ] Every entry folder has `card.md`, `source.md`, and `meta.json`
- [ ] `source.pdf` archived for >= 60% of entries with a redistributable paper
- [ ] All entries have BibTeX in <strand>.bib
- [ ] INDEX.md fully populated with categorized one-liners
- [ ] No prose synthesis in this phase; that is Phase 2

## Out of scope

- <Topics adjacent but outside the thesis>
- Drafting the direction paper or other synthesis prose
- Comparing or ranking entries; collection only
```

## Authoring notes

- The brief is opinionated. Vague briefs produce vague corpora.
- Numerical thresholds (>= N entries, >= M per category) should be set high enough to force breadth and low enough to ship in one parallel agent run. Typical: N = 20-40, M = 3-6.
- Seed material is critical. If no prior-work documents exist, the brief must enumerate canonical entries explicitly, otherwise the agent will return a generic survey rather than a thesis-aligned corpus.
- "Out of scope" lines save more wasted work than any other section. Be specific.
