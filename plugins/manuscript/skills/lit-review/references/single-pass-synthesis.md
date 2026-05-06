# Single-Pass Thematic Synthesis (Express Mode)

Use this lightweight workflow when the multi-phase corpus protocol is overkill: drafting an Introduction or Background section, writing a mini-review for a grant aim, or producing a quick standalone narrative review. For citation-traceable, multi-strand reviews, use the full Phase 0-4 protocol in SKILL.md.

## Review Types

| Type | Purpose | Method | Output |
|------|---------|--------|--------|
| Narrative | Summarize and interpret a body of literature | Selective, thematic | Flowing prose with arguments |
| Systematic | Exhaustive, reproducible search with defined criteria | PRISMA protocol, inclusion/exclusion | Structured report with methodology |
| Scoping | Map the extent of literature on a topic | Broad search, categorization | Overview of themes and gaps |
| Mini-review | Focused review for a specific question | Targeted search | Brief, focused synthesis |

For systematic and scoping reviews, also see [review-frameworks.md](review-frameworks.md) (PRISMA, PICO, SPIDER, scoping protocol, risk-of-bias tools).

## Pipeline

### Step 1: Gather papers

Use the `opencite:opencite` skill for retrieval:

```bash
# Foundational papers
uvx opencite canonical "topic" --max 15

# Recent work
uvx opencite search "specific query" --max 30 --sort date

# Citation network
uvx opencite cite "key-paper-DOI" --direction both

# Download and convert for reading
uvx opencite batch-fetch --from-json results.json --convert -o ./papers --summary report.json
```

### Step 2: Read and annotate

For each paper extract:
- Key finding (1-2 sentences)
- Method (approach/technique used)
- Population/context (who/what was studied)
- Limitations noted by authors
- How it connects to other papers in the set

Build a synthesis matrix:

| Paper | Finding | Method | Supports | Contradicts |
|-------|---------|--------|----------|-------------|
| Smith 2024 | X increases Y | RCT, N=200 | Jones 2023 | Lee 2022 |
| Jones 2023 | X correlates with Y | Survey, N=1000 | Smith 2024 | -- |
| Lee 2022 | No effect of X on Y | Meta-analysis | -- | Smith 2024, Jones 2023 |

### Step 3: Identify themes

Group papers by theme, not chronologically. Common organizing structures:

- By methodology: studies using similar approaches
- By finding: studies with converging or diverging results
- By population: subject type or context
- By theoretical framework: underlying model
- Chronological evolution: how understanding changed over time (use sparingly)

### Step 4: Write the review

Each paragraph should:
1. Topic sentence stating the theme or claim
2. Evidence citing 2-5 papers supporting or nuancing the claim
3. Synthesis comparing, contrasting, connecting the cited works
4. Transition to the next theme or to the gap

#### Citation weaving patterns

**Integral citation** (author as subject):
"Smith et al. (2024) demonstrated that X increases Y using a randomized controlled trial with 200 participants."

**Non-integral citation** (finding as subject):
"Recent evidence suggests that X increases Y in controlled settings (Smith et al., 2024; Jones et al., 2023), although this effect may be population-dependent (Lee et al., 2022)."

**Synthesis citation** (multiple sources for one claim):
"Several studies have converged on the finding that X modulates Y through mechanism Z (Smith et al., 2024; Jones et al., 2023; Chen et al., 2021), with effect sizes ranging from d = 0.3 to d = 0.8."

**Contrast citation**:
"While Smith et al. (2024) found significant effects using direct measurement, Lee et al. (2022) reported null results in a meta-analysis of self-report studies, suggesting that measurement approach may moderate the effect."

#### Common pitfalls

- Annotated bibliography: don't summarize each paper sequentially; synthesize.
- String-of-pearls: don't write "Smith found X. Jones found Y. Lee found Z." Connect them.
- Overclaiming: avoid "proves" or "definitively shows." Use "suggests," "indicates," "provides evidence for."
- Recency bias: include foundational/seminal work, not just the last 2 years.
- Confirmation bias: include contradictory findings and explain discrepancies.

### Step 5: Identify the gap

After synthesis, articulate what is missing.

Gap statement patterns:
- "Despite these advances, no study has examined {specific question}."
- "While X has been established for {context A}, it remains unclear whether this extends to {context B}."
- "Existing studies are limited by {methodological issue}, and {new approach} could address this."
- "The relationship between X and Y has been studied in isolation, but their interaction under {condition} is unexplored."

### Step 6: Generate bibliography

```bash
# Export BibTeX for all cited papers
while IFS= read -r doi; do
  [ -z "$doi" ] && continue
  uvx opencite lookup "$doi" -f bibtex --append-bib review_refs.bib
done < cited_dois.txt
```

## Output skeleton

```markdown
# Literature Review: {Topic}

## {Theme 1 Title}
{Synthesized paragraphs with citations}

## {Theme 2 Title}
{Synthesized paragraphs with citations}

## {Theme 3 Title}
{Synthesized paragraphs with citations}

## Current Gaps and Future Directions
{Gap analysis and research opportunities}

## References
{BibTeX file or formatted reference list}
```

## Quality checklist

- [ ] Organized thematically (not paper-by-paper)
- [ ] Each paragraph synthesizes multiple sources
- [ ] Citations woven into prose (not parenthetical dumps)
- [ ] Contradictory findings acknowledged and explained
- [ ] Seminal/foundational work included
- [ ] Recent work (last 2-3 years) included
- [ ] Gap statement clearly articulated
- [ ] Transition sentences connect paragraphs and sections
- [ ] No overclaiming (appropriate hedging)
- [ ] All cited papers in reference list
