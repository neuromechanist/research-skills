---
name: lit-review
description: "Use this skill for \"literature review workflow\", \"multi-phase lit review\", \"direction paper\", \"review paper protocol\", \"strand-based literature review\", \"citation-grounded review\", \"systematic lit review with paper cards\", \"build a lit review corpus\", \"lit review pipeline\", \"orchestrate a literature review\", \"research directions document\", or when the user wants a rigorous multi-phase, citation-traceable literature review with parallel strand collection, taxonomic synthesis, and direction papers (not a single-pass synthesis; for that use opencite:literature-review)."
version: 0.1.0
---

# Multi-Phase Literature Review Workflow

Orchestrate a rigorous, citation-grounded literature review across phases: angles to briefs, parallel paper collection, taxonomic synthesis, direction papers, and self-review loops. Every claim in a final document is traceable back to a paper-card.

## When to Use

- Building a corpus-grounded review paper or a set of direction documents
- Multi-strand reviews where breadth + depth must be coordinated across distinct angles (e.g. tools strand, data strand, science strand)
- Reviews where claim-to-evidence traceability matters (grant lit reviews, position papers, white papers)
- Iterative reviews where new papers, refined angles, or updated synthesis must roll forward without losing prior work

## When NOT to Use

- Single-pass thematic synthesis for a manuscript Introduction or Background section. Use `opencite:literature-review` instead.
- Original research IMRAD writing. Use `manuscript:manuscript-writing`.
- Peer review of a submitted manuscript. Use `manuscript:paper-review`.
- Journal formatting. Use `manuscript:manuscript-formatting`.

## Workflow Phases

```
Phase 0: Briefs            -> _briefs/strand-*.md (one brief per strand)
Phase 1: Collection        -> research/collection/<strand>/<slug>/{card.md, source.{pdf,md}, meta.json}
                              + INDEX.md + <strand>.bib per strand
Phase 2: Synthesis         -> research/synthesis/{<strand>-ontology, gap-analysis, scope-diagram, <domain>-map}.md
Phase 3: Direction papers  -> direction-papers/<topic>-direction.md
Phase 4: Review loop       -> revised direction; may reopen Phase 1 with new gaps
```

Each angle is realized as a strand; the brief is the strand's dispatch document. Iteration is expected: loop back from any phase. The directory layout is the persistence layer; treat it as the source of truth between sessions.

### Phase 0: Define angles and write briefs

Inputs: prior work, gap statement, epic-dev findings (if any), grant call or thesis question.

Output: one brief per strand in `_briefs/strand-<name>.md`.

Each brief defines:
- Goal (one sentence)
- Scope categories (numbered list, breadth first)
- Per-entry deliverable (cards + source + bib + index)
- Seed material (existing prior-work documents to import)
- Acceptance criteria (count thresholds, breadth thresholds, completeness gates)
- Out-of-scope items
- Sister skills to use (`opencite:opencite`, `manuscript:manuscript-writing`)

See [references/brief-template.md](references/brief-template.md) for the full structure.

If the user names a project domain (neuro tools, clinical trials, ML methods, etc.), generate strands by partitioning the topic on dimensions that *cannot be merged later without information loss*. Common partitions: methods vs. infrastructure vs. application; tools vs. data vs. theory; modality A vs. modality B.

### Phase 1: Collection (parallel strand agents)

For each strand, build a corpus of paper-cards under `research/collection/<strand>/`. Each entry is a folder with `card.md` plus `source.md` plus `meta.json`, and `source.pdf` only when redistributable. Per-strand aggregates are `INDEX.md` and `<strand>.bib`. Use `opencite:opencite` for all paper operations.

Schema and storage rules: [references/paper-card-schema.md](references/paper-card-schema.md). License-to-redistribution policy and CI rule: [references/license-rules.md](references/license-rules.md).

When parallelizing strands, dispatch one agent per strand. Use the brief as the agent's full context. Do not let strand agents synthesize across strands; that is Phase 2's job.

### Phase 2: Synthesis (whole-corpus integration)

Inputs: full collection across all strands.

Outputs (in `research/synthesis/`):
- `<strand>-ontology.md` per strand: hierarchical category tree of corpus entries
- `<domain>-map.md` (e.g. `science-map.md`): theme-by-theme inventory of analytic / methodological themes
- `<data>-hierarchy.md` (e.g. `dataset-hierarchy.md`): the data layer, when applicable
- `gap-analysis.md`: three-column comparison of what is covered by prior efforts vs. what the synthesis reveals as uncovered. The third column is the input to Phase 3
- `scope-diagram.md`: prose plus optional Mermaid/ASCII diagram of corpus boundaries

Bias rules (enforced):
- Gap analysis must list *what the corpus does NOT support*, not just what it does
- Inter-strand contradictions must be named, not papered over
- Frequency-of-mention is not evidence weight; cite single primary sources where appropriate

See [references/synthesis-templates.md](references/synthesis-templates.md).

### Phase 3: Direction papers (citation-grounded essays)

Output: `direction-papers/<topic>-direction.md` per direction (typically one per strand or per gap cluster).

Each direction paper:
- Defends a thesis grounded in the corpus
- Cites every claim back to a specific card path: `[<slug>](../research/collection/<strand>/<slug>/card.md)`
- Closes with a flat references section keyed to BibTeX in the strand `.bib`
- Follows review-paper IMRAD structure and prose discipline (delegate to `manuscript:manuscript-writing`): no em-dashes, abbreviations defined on first use, descriptive voice not exhortatory

The cite-card cross-link is the load-bearing convention. A claim that does not link to a card is a claim that has not yet been grounded; either ground it (add the card) or remove the claim.

See [references/direction-paper-template.md](references/direction-paper-template.md).

For LaTeX export of a direction paper to a journal review template, delegate to `manuscript:manuscript-formatting`. The base format is markdown.

### Phase 4: Review loop

Self-review the direction paper using `manuscript:paper-review`. Treat it as a peer review of one's own draft.

Common loop-back triggers:
- Reviewer (self or other) names a claim as ungrounded -> Phase 1 (add cards) or Phase 3 (drop claim)
- Reviewer flags a missing theme -> Phase 0 (new strand or expanded scope) -> Phase 1 (collect)
- Reviewer flags a contradiction in synthesis -> Phase 2 (revise gap analysis or ontology)
- Reviewer flags storyline incoherence -> Phase 3 (restructure with `manuscript:manuscript-writing`)

Apply [references/rigor-checklist.md](references/rigor-checklist.md) before declaring a direction paper done.

## Bootstrapping a new lit review

When the user starts fresh, propose a top-level layout in the working directory or a subdirectory:

```
<root>/
├── _briefs/
├── research/
│   ├── collection/
│   │   ├── _schema/paper-card.md
│   │   └── <strand>/
│   └── synthesis/
└── direction-papers/
```

Create directories on demand as work progresses; do not pre-create empty trees. The `_schema/paper-card.md` should be a copy of [references/paper-card-schema.md](references/paper-card-schema.md) so that strand agents have a local reference.

## Sister skills

| Skill | Used for |
|---|---|
| `opencite:opencite` | DOI lookup, PDF retrieval, PDF -> markdown, BibTeX export |
| `opencite:literature-review` | Single-pass thematic synthesis, useful as a Phase 2 seed |
| `manuscript:manuscript-writing` | IMRAD / review-paper structure plus prose discipline (abbreviations, voice, transitions) |
| `manuscript:manuscript-formatting` | Journal formatting / LaTeX export |
| `manuscript:paper-review` | Self-review loops on direction-paper drafts |
| `project:epic-dev` | Upstream source of research angles when reviewing one's own project |

## References

- [references/paper-card-schema.md](references/paper-card-schema.md): card.md frontmatter + sections, meta.json schema, license vocabulary, storage rules
- [references/brief-template.md](references/brief-template.md): per-strand dispatch brief structure
- [references/synthesis-templates.md](references/synthesis-templates.md): ontology, gap-analysis, map, scope-diagram patterns
- [references/direction-paper-template.md](references/direction-paper-template.md): essay structure with cite-card cross-link convention
- [references/license-rules.md](references/license-rules.md): redistribution discipline and CI rules
- [references/rigor-checklist.md](references/rigor-checklist.md): cohesion, storyline, bias-neutrality, traceability acceptance criteria
