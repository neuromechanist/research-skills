# Direction Paper Template

A direction paper is a focused, citation-rich essay that defends a thesis, surveys the landscape, and proposes a roadmap. One per strand or per gap cluster.

## File location

`direction-papers/<topic>-direction.md`.

## Structure

```markdown
# <Strand or Topic> Direction, <Headline Thesis>

A focused review on the <strand> strand of <project>. <One-paragraph thesis statement that names what is missing in the literature and what this paper argues should fill the gap.> The argument was first articulated in <upstream issue or prior-work pointer>; this paper develops it into a literature-grounded position by surveying the <K> themes catalogued in the Phase 1 corpus and the Phase 2 [`<domain>-map`](../research/synthesis/<domain>-map.md).

Abbreviations: <Define every abbreviation on first use, comma-separated, in this paragraph.>

## 1. Introduction

### 1.1 The arc

<2-4 paragraphs locating the topic historically. Cite the establishing works:>
[<slug>](../research/collection/<strand>/<slug>/card.md), [<slug>](...).

### 1.2 Gap statement

<1-2 paragraphs naming what is missing. Anchor the gap with citations to corpus cards. Mirror the gap as it appears in `../research/synthesis/gap-analysis.md`, do not invent a new framing.>

### 1.3 Thesis

<1 paragraph articulating the direction this paper argues for. State the structure of the remainder.>

## 2. Background, the <K> themes

The Phase 1 corpus organizes <N> entries into <K> themes; the Phase 2 [`<domain>-map`](../research/synthesis/<domain>-map.md) inventories each theme. This section summarizes the prior-work landscape that the rest of the paper draws on.

**Theme 1, <name>.** <2-4 sentence summary citing card paths: [<slug>](../research/collection/<strand>/<slug>/card.md).>

**Theme 2, <name>.** <...>

...

## 3. <Argument body>

### 3.1 <Argument node 1>

<Each subsection advances one beat of the thesis. Every claim cites a card path. Counter-evidence is named, not omitted.>

### 3.2 <Argument node 2>

...

## 4. <Existence proof or anchor case>

<One concrete case from the corpus that demonstrates the thesis is buildable. Cite the card.>

## 5. Roadmap

<Phased commitments derived from `../research/synthesis/gap-analysis.md`. Each commitment names the artifacts it would produce.>

## 6. Coordination with adjacent efforts

<How this direction relates to sister grants, parallel labs, or adjacent efforts. Cite cards or external pointers.>

## 7. Discussion

### 7.1 Interpretation

<What the direction paper changes about the field if adopted.>

### 7.2 Limitations

<Honest limitations. What corpus entries do not support this thesis? Name them.>

### 7.3 Counterarguments

<Steelman the strongest objection. Cite the cards that ground the objection. Then respond.>

## 8. Conclusion

<1-2 paragraphs.>

## References

<Flat list keyed to the strand .bib. One entry per BibTeX key, in the order first cited or alphabetical, by convention.>
```

## The cite-card cross-link convention

Every concrete claim in a direction paper must include a cross-link of the form:

```markdown
[<slug>](../research/collection/<strand>/<slug>/card.md)
```

This is the load-bearing convention. It serves three purposes:

1. **Traceability**: a reader (or a later self) can land on the card and check the claim against `source.md`.
2. **Falsifiability**: a claim that does not link to a card has not yet been grounded. Either ground it (add a card) or drop it.
3. **Bias hygiene**: links force engagement with the actual corpus instead of the author's prior beliefs.

A direction paper is *complete* when every paragraph contains at least one cross-link to a card, and every cited card actually supports the claim.

## Style discipline

Apply `manuscript:manuscript-writing`:

- No em-dashes; commas or semicolons.
- Abbreviations defined on first use within the document. The Abbreviations paragraph after the thesis is the canonical first-use site.
- Descriptive voice, not exhortatory. "<Project> argues" rather than "<Project> must"; "the corpus reveals" rather than "we should".
- Active voice for actions the paper takes. Past tense for what prior work did.
- One idea per sentence. Topic sentence then evidence then interpretation per paragraph.

## Length guide

| Section | Target |
|---|---|
| Introduction (1) | 1.5-3 pages |
| Background (2) | 2-4 pages |
| Argument (3) | 4-7 pages |
| Anchor case (4) | 1-2 pages |
| Roadmap (5) | 1-2 pages |
| Coordination (6) | 1 page |
| Discussion (7) | 2-3 pages |
| Conclusion (8) | 0.5 page |

Total target: 12-22 pages of dense markdown, before the References section.

## When the paper feels unfinished

Diagnostic checklist:

- A section reads as opinion rather than synthesis -> add card cross-links to ground each beat.
- The argument cites the same 3-4 cards repeatedly -> corpus is too narrow; loop to Phase 1.
- Counterarguments section is generic -> read the cards tagged as contrary; the strongest objection is in there.
- Roadmap reads as wish list -> tie each commitment to a specific gap from gap-analysis.md.
- Storyline does not flow -> apply `manuscript:manuscript-writing` revision pass focused on transitions and topic sentences.

## Export to LaTeX

Markdown is the base format. To export for a journal review template, delegate to `manuscript:manuscript-formatting` with the target journal. Cite-card cross-links typically convert to footnotes or in-text citations against the strand `.bib`.
