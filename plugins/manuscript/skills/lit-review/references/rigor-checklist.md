# Rigor Checklist

Apply before declaring a phase done. The checklist is per-phase; do not skip ahead.

## Phase 0: Briefs

- [ ] One brief per strand, in `_briefs/strand-<name>.md`.
- [ ] Strands partition the topic on a dimension that cannot be merged later (methods vs. data, tools vs. theory, modality vs. modality).
- [ ] Each brief has explicit scope categories (numbered list), per-entry deliverable, seed material, acceptance criteria, and out-of-scope items.
- [ ] Acceptance criteria are quantified: minimum entry count overall and per category.
- [ ] No prose synthesis is implied by the brief; collection only.

## Phase 1: Collection

- [ ] Per-entry artifact set complete: `card.md`, `source.md`, `meta.json`. `source.pdf` iff `redistribution_ok: true`.
- [ ] Every entry's `card.md` has all required frontmatter fields populated, no nulls except where allowed.
- [ ] `relevance` is calibrated: less than ~40% of entries are `high`.
- [ ] `INDEX.md` per strand is fully populated, grouped by category.
- [ ] `<strand>.bib` has a BibTeX record for every entry.
- [ ] License rules are not violated: no `source.pdf` exists where `redistribution_ok: false`.
- [ ] Acceptance thresholds from the brief are met (entry count overall and per category).
- [ ] No cross-strand synthesis has crept in; cards summarize one work each.

## Phase 2: Synthesis

- [ ] One ontology per strand in `research/synthesis/<strand>-ontology.md`. Each leaf links to a card.
- [ ] Domain map (`<domain>-map.md`) inventories themes; each theme cites establishing cards and lists open questions.
- [ ] Data hierarchy or domain equivalent if applicable.
- [ ] `gap-analysis.md` is three-column with the third column as the load-bearing one. Gap count exceeds the brief's bar.
- [ ] Each gap is established by listing the cards that collectively define the negative space.
- [ ] Inter-strand contradictions are named in the map under "Open questions", not flattened into gaps.
- [ ] `scope-diagram.md` states in-scope and adjacent-out-of-scope explicitly, with rationale for exclusions.
- [ ] Every concrete claim in synthesis prose cites a card path. No ungrounded assertions.

## Phase 3: Direction papers

- [ ] One direction paper per strand or per gap cluster, in `direction-papers/<topic>-direction.md`.
- [ ] Headline thesis is articulated in the opening paragraph and the Introduction.
- [ ] Every concrete claim includes a cite-card cross-link of the form `[<slug>](../research/collection/<strand>/<slug>/card.md)`.
- [ ] Every paragraph in argument sections (3, 4, 5) contains at least one cite-card cross-link.
- [ ] Every cited card actually supports the claim. Spot-check by clicking through and reading the card's TL;DR and Notable details sections.
- [ ] Counterargument section is corpus-grounded, not generic. The strongest objection is named with cite-card links.
- [ ] Roadmap commitments tie to specific gaps in `gap-analysis.md`.
- [ ] Style discipline is enforced: no em-dashes; abbreviations defined on first use in the Abbreviations paragraph; descriptive voice not exhortatory.
- [ ] References section is keyed to the strand `.bib`.

## Phase 4: Review loop

- [ ] Self-review pass via `manuscript:paper-review` is recorded as comments or a sibling review document.
- [ ] Each reviewer concern is dispositioned: ground (Phase 1), restructure (Phase 2 or 3), or drop (Phase 3 with explicit removal).
- [ ] Loop-backs are atomic: a single concern produces a single revision pass; do not bundle revisions across concerns until the final polish.
- [ ] After the final revision pass, re-run Phase 3 checklist completely.

## Whole-project quality gates

These are the gates that distinguish a rigorous review from a pretty one.

### Traceability

Pick five claims at random from the direction paper. For each:

- [ ] Click the cite-card link. Does the card load?
- [ ] Does the card's TL;DR or Summary support the claim?
- [ ] Does `source.md` (or `source.pdf` if redistributable) actually contain the supporting text?

If any of the three fails, the claim is ungrounded. Fix it.

### Storyline cohesion

Read the direction paper section openings only (Section 1.1, 1.2, ..., 7.1, 7.2, 8). 

- [ ] Do the section openings, read in order, narrate a coherent argument?
- [ ] Does each section's opening reference what the prior section established?
- [ ] Is there a single thesis sentence that the whole paper drives toward, recoverable from reading openings only?

If reading openings only yields fragments rather than an argument, restructure with `manuscript:manuscript-writing`.

### Bias balance

- [ ] Counterargument section names the strongest objection, not a strawman.
- [ ] Limitations section names corpus entries that do not support the thesis (not just generic methodological caveats).
- [ ] Gap analysis lists what the corpus does NOT support. Frequency-of-mention is not weight.
- [ ] If results favor the thesis on every dimension, the corpus is probably too small or too aligned. Loop to Phase 1 and add adversarial entries.

### Reproducibility

- [ ] A reader who clones the corpus and reads `_briefs/`, `research/collection/<strand>/INDEX.md`, `research/synthesis/`, and `direction-papers/` in order can reconstruct the argument without further context.
- [ ] No load-bearing claims live only in conversation history or scratch notes. Persist them to the layout.

## Final acceptance

The review is done when:

- All Phase 3 checks pass.
- All whole-project quality gates pass.
- The user (or self) has read the direction paper end to end and would defend each cite-card link in a hostile review.

Anything less is a draft, not a release.
