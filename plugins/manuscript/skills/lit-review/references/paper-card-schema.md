# Paper-Card Schema

Each entry lives in its own folder under the strand:

```
research/collection/<strand>/<slug>/
├── card.md         this paper-card; required
├── source.pdf      full PDF; only when redistributable
├── source.md       markdown extraction or canonical README; always required
└── meta.json       provenance: source URL, retrieval date, license, hash, redistribution flag
```

Rationale: synthesis and direction-paper drafting must be able to re-read primary text without re-fetching. Summaries are derived; sources are persisted.

## card.md template

```yaml
---
slug: <kebab-case-short-id>             # matches folder name
type: paper | dataset | tool | platform | standard
strand: <strand-name>                   # matches the parent folder
year: <YYYY>
authors: [<surname1>, <surname2>, ...]
venue: <journal / conference / org>
doi: <doi or null>
url: <canonical url or null>
license: <license or null>
modalities: [<domain-specific tags>]
tags: [<5-12 short tags>]
relevance: high | medium | low
imported_from: <relative path or null>
added: <YYYY-MM-DD>

# Archival fields
pdf_status: archived | not-redistributable | not-available | not-applicable
pdf_path: source.pdf | null
md_path: source.md | null
md_quality: clean | rough | partial | abstract-only
---
```

### relevance calibration anchors

To keep the field discriminative for downstream filtering:

- **high**: direct dependency for the project's deliverables. The thing the work is built on or against.
- **medium**: standard within scope but not a direct dependency. Context that informs but does not constrain.
- **low**: tangential or background. Reference-only.

If more than ~40% of entries land in `high`, the field has lost discriminative power. Rebalance.

### Sections

- **TL;DR**: one or two sentences capturing the *thesis*, not duplicating the Summary opening.
- **Summary**: 3-6 sentences covering core contribution, method, scope, key numbers.
- **Relevance to the review**: concrete connection to the project / thesis. Cite specific mechanisms or claims. Avoid generic prose.
- **Notable details**: bullet list of facts worth pulling forward to synthesis.
- **Open questions / limitations**: paper-specific only. Phase 2 gap analysis depends on this; generic boilerplate is harmful.
- **Citations**: primary BibTeX key plus up to 5 related works as one-liners.

## meta.json template

```json
{
  "doi": "10.xxxx/xxxxx",
  "source_url": "https://...",
  "retrieved_at": "YYYY-MM-DD",
  "pdf_sha256": "<sha256 hex if archived; null otherwise>",
  "pdf_license": "<see vocabulary below>",
  "redistribution_ok": true,
  "notes": "<retrieval notes, e.g. 'arXiv preprint used; published version paywalled'>"
}
```

### pdf_license vocabulary

- `CC-BY`, `CC-BY-2.0`, `CC-BY-3.0`, `CC-BY-4.0`, `CC-BY-NC`, `CC0`
- `preprint-cc-arxiv`, `preprint-cc-biorxiv`, `preprint-cc-osf`
- `author-accepted-manuscript` (institutional repository copy)
- `publisher-paywall`
- `not-applicable` (e.g. tool with only a README)
- `unknown`

Values may include a parenthetical qualifier when needed, e.g. `publisher-paywall (NeuroImage); university repository copy archived`.

`redistribution_ok` must align with the license. Any `*-paywall` value implies `redistribution_ok: false`.

## Storage rules

The `pdf_status` enum semantics are:

- `archived`: `source.pdf` is committed; `pdf_sha256` populated. Used when `redistribution_ok: true` and a PDF is available.
- `not-redistributable`: paywalled or otherwise non-redistributable. `pdf_path: null`, `pdf_sha256: null`. `source.md` is still committed.
- `not-applicable`: no paper exists (tool / dataset / standard with only a README). `source.md` is the snapshot.
- `not-available`: download failed. Document the failure mode in `meta.json.notes` and re-attempt later.

The `redistribution_ok` field is the single source of truth for whether `source.pdf` may exist in the repo. License-to-redistribution policy and the CI rule live in [license-rules.md](license-rules.md).

## INDEX.md per strand

Plain markdown index, grouped by category, one line per entry:

```markdown
# <Strand name> Collection Index

## Category 1
- [<slug>](./<slug>/card.md): one-line description (`relevance: high`, year)

## Category 2
- ...
```

## .bib per strand

Append the BibTeX returned by `opencite` for each entry:

```bibtex
@article{slug2024key,
  ...
}
```

Keep the citation key consistent with the slug where possible.

## Tooling

Use `opencite:opencite` to:

1. Resolve DOI / canonical URL
2. Download PDF where licensing permits
3. Convert PDF to markdown (`source.md`)
4. Export BibTeX

For tools or platforms without papers, snapshot the canonical README / docs landing as `source.md`. Link the repo URL in `meta.json.source_url`.
