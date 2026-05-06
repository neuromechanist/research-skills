# Synthesis Templates

Phase 2 outputs live in `research/synthesis/`. Each document integrates the full corpus across strands. Synthesis is bias-disciplined: gaps are stated explicitly, contradictions are named, frequency is not weight.

## File set

| File | Purpose | Required? |
|---|---|---|
| `<strand>-ontology.md` | Hierarchical category tree per strand (one file per strand) | Yes |
| `<domain>-map.md` | Theme-by-theme inventory of analytic / methodological themes | Yes |
| `<data>-hierarchy.md` | The data layer (datasets, modalities, sample sizes); rename per domain | Iff strand has data |
| `gap-analysis.md` | Three-column accounting: prior-effort coverage, current-thesis coverage, uncovered scope | Yes |
| `scope-diagram.md` | Prose plus optional Mermaid/ASCII diagram of corpus boundaries | Yes |

## Ontology template

```markdown
# <Strand> Ontology

A hierarchical view of the <strand> corpus. Each entry links to its paper-card.

## Top-level categories

### Category A: <name>
- Sub-category A.1: <name>
  - [<slug>](../collection/<strand>/<slug>/card.md): one-line role statement
  - ...
- Sub-category A.2: <name>
  - ...

### Category B: <name>
- ...

## Cross-cutting tags

Tags that apply across categories (e.g. open-source, deprecated, paywalled, GPU-required):
- `<tag>`: [<slug>](../collection/<strand>/<slug>/card.md), ...
```

Sub-category leaves should not duplicate the brief's category headings; the ontology is allowed to refactor categories as the corpus reveals natural joints.

## Map template (theme-by-theme inventory)

```markdown
# <Domain> Map

Theme-by-theme inventory of the analytic and methodological themes the corpus addresses. Each theme cites the establishing paper-cards.

## Theme 1: <name>

**Defining works**: [<slug>](../collection/<strand>/<slug>/card.md), [<slug>](...).

<2-4 sentence prose summary of the theme: what it studies, what method, what scope.>

**Open questions**: <named questions the corpus surfaces but does not answer. These feed gap-analysis.>

## Theme 2: <name>

...
```

The map is the connective tissue between collection and direction papers. A direction paper that does not draw on the map is probably ungrounded; a theme in the map that no direction paper draws on is probably noise.

## Gap analysis template

Three-column structure. The third column is the load-bearing one.

```markdown
# Gap Analysis

| Topic | <Prior effort A> covers | <Prior effort B> covers | Uncovered, our distinctive scope |
|---|---|---|---|
| <Topic 1> | <coverage> | <coverage> | <gap> |
| <Topic 2> | <coverage> | <coverage> | <gap> |
| ... | ... | ... | ... |

## Concrete gap list

### Gap 1: <name>

**Established by**: [<slug>](../collection/<strand>/<slug>/card.md), [<slug>](...).

<2-3 sentence prose: what the corpus reveals as missing, why it matters.>

**Proposed Phase 3 commitment**: <what the direction paper will say about this gap.>

### Gap 2: <name>

...
```

Bias rules:

1. **Gaps are about absence, not preference.** "We could do X" is not a gap; "the corpus does not contain a single entry that does X" is a gap.
2. **Cite the absence.** A gap is established by listing the cards that establish the boundary; the gap itself is the negative space those cards collectively define.
3. **Acceptance bar exceeds the brief.** If the brief asked for >= 5 gaps, the synthesis should return >= 6-8. Phase 3 will prioritize.
4. **Contradictions are not gaps.** When two corpus entries disagree, name the contradiction in the map under "Open questions"; do not flatten it into a gap.

## Scope diagram template

```markdown
# Scope Diagram

A prose-plus-diagram statement of what this corpus covers and what it deliberately excludes.

## In scope

- <Topic>: covered by <N> entries across <strand A> and <strand B>
- ...

## Adjacent but out of scope

- <Topic>: explicitly out of scope per [brief A](../_briefs/strand-A.md) and [brief B](../_briefs/strand-B.md). Rationale: <why>.
- ...

## Boundaries diagram

```
<ASCII or Mermaid diagram showing nested or overlapping scopes>
```
```

If using Mermaid, prefer `flowchart TD` or `mindmap`. Keep it under 30 nodes; otherwise the diagram has stopped being a summary.

## Authoring discipline

- Synthesis prose follows `manuscript:manuscript-writing` discipline: no em-dashes, abbreviations defined on first use, descriptive voice not exhortatory.
- Every concrete claim cites a card path. The synthesis is a summary of the corpus, not a summary of the author's prior knowledge.
- If a synthesis claim cannot be cited to a card, it is a hint that a card is missing from the corpus. Either add the card (loop to Phase 1) or drop the claim.
