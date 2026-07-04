# Exploration Prompt Templates

Templates for delegated read-only exploration. The agent-fanout skill's
`references/fanout-prompts.md` holds the general library; these are the
onboarding-specific variants.

## Architecture-domain explorer (one per domain, parallel)

```
Explore [absolute repo path] ([one-line description of the system]). Search
breadth: very thorough. READ-ONLY analysis; do not modify any files.
Your domain: [backend | CLI | website | data/storage | ops/infra]. Own these
paths and nothing else: [explicit dir list].

Goal: an architecture audit feeding a strategic review. Report:
1. Module/target layout: what components exist in your domain, how they
   depend on each other, where they are composed or mounted.
2. [Domain-specific question naming suspected files/symbols, e.g. "how does a
   request pick which model/backend runs; is there ONE registry or per-module
   ad-hoc lists?"]
3. [State management: where does persistent state live; one source of truth
   or several?]
4. [Interfaces to other domains: what is exposed and consumed?]
5. Pain points and smells: duplicated types, inconsistent patterns, hardcoded
   values, TODOs, anything in .context/plan.md marked unfinished.

Return a structured report with file:line references for the load-bearing
facts. Be conclusion-oriented; no file dumps. Send the FULL report as your
final message text.
```

## Reference-implementation extractor (numerical/algorithm ports)

```
Read [reference source, e.g. the Fortran implementation at path] and produce
a precise technical summary of the core algorithm math and control flow.
READ-ONLY. Specifically:
1. Main iteration loop structure and update ORDER.
2. The exact per-sample [objective] computation: each term, each
   normalization divisor (divided by N? by N*k? log-determinant included?).
3. Each parameter update rule, exactly as coded.
4. Reparameterization/rescaling steps and when they run.
5. Numerical guards (clamps, epsilons, posdef checks).
6. Data layout and default parameter values.
Quote the actual source lines (with line numbers) for the key formulas. Be
exact about signs, factors of 1/2, logs, and which count divides which sum.
Your final message is the deliverable: a self-contained technical reference
document.
```

While this agent runs, independently re-derive the single most load-bearing
formula yourself (one grep of the reference) so your synthesis does not rest
solely on the extraction.

## Literature-survey worker (one per topic family)

```
You are surveying [family name] for [project goal]. Today is [date]; prefer
the latest evidence.
YOUR FAMILY: [precise sub-scope]. Hard reading list: [IDs/DOIs/URLs].
TOOLS: [search CLI and syntax]; a pre-fetched corpus is at [path]; use web
fetch only for items not in the corpus.
DELIVERABLES: write [research/aN-family.md] with exactly these sections:
[headers]; write BibTeX to [path].
STYLE: no em-dashes; define abbreviations at first use; no emojis; cite every
quantitative claim; keep paper claims separate from your analysis.
RETURN (final message, 10-15 lines): top 3 takeaways, recommendation, and the
single most promising option for our constraints.
```

## Feasibility follow-up to a live scout (reuse, do not respawn)

```
Follow-up task, same repo. We are scoping [the new question]. I need an
implementation-feasibility read:
1. Find [the existing implementation] and summarize its actual mechanism.
2. Locate where [the prior measurement/claim] was made; quote it.
3. From [the pinned configs], report [the concrete parameters].
4. Assess concretely: to do [the change], what would have to change and
   where?
5. Report any existing config knobs that already touch this.
Return a compact engineering-feasibility memo with file:line references. Do
not modify any files.
```
