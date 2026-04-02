---
name: literature-review
description: "Use this skill for \"write a literature review\", \"synthesize papers\", \"review the literature\", \"summarize research findings\", \"identify research trends\", \"gap analysis\", \"thematic review\", \"systematic review\", \"scoping review\", \"narrative review\", \"compare studies\", \"research synthesis\", or when the user wants to synthesize multiple papers into a cohesive literature review."
version: 0.1.0
---

# Literature Review Writing

Synthesize multiple academic papers into a cohesive literature review with thematic organization, trend identification, gap analysis, and proper citation weaving.

## When to Use

- Writing the Introduction or Background section of a manuscript or grant
- Creating a standalone literature review paper
- Synthesizing findings from an opencite search session
- Identifying gaps in the literature to justify new research
- Preparing a systematic or scoping review

## Review Types

| Type | Purpose | Method | Output |
|------|---------|--------|--------|
| **Narrative** | Summarize and interpret a body of literature | Selective, thematic | Flowing prose with arguments |
| **Systematic** | Exhaustive, reproducible search with defined criteria | PRISMA protocol, inclusion/exclusion | Structured report with methodology |
| **Scoping** | Map the extent of literature on a topic | Broad search, categorization | Overview of themes and gaps |
| **Mini-review** | Focused review for a specific question | Targeted search | Brief, focused synthesis |

## Review Pipeline

### Step 1: Gather Papers

Use the `opencite` skill to find relevant literature:

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

### Step 2: Read and Annotate

For each paper, extract:
- **Key finding** (1-2 sentences)
- **Method** (approach/technique used)
- **Population/context** (who/what was studied)
- **Limitations** noted by authors
- **How it connects** to other papers in the set

Create a synthesis matrix:

| Paper | Finding | Method | Supports | Contradicts |
|-------|---------|--------|----------|-------------|
| Smith 2024 | X increases Y | RCT, N=200 | Jones 2023 | Lee 2022 |
| Jones 2023 | X correlates with Y | Survey, N=1000 | Smith 2024 | -- |
| Lee 2022 | No effect of X on Y | Meta-analysis | -- | Smith 2024, Jones 2023 |

### Step 3: Identify Themes

Group papers by theme, not chronologically. Common organizing structures:

- **By methodology**: group studies using similar approaches
- **By finding**: group studies with converging/diverging results
- **By population**: group by subject type or context
- **By theoretical framework**: group by underlying model
- **Chronological evolution**: trace how understanding changed over time (use sparingly)

### Step 4: Write the Review

#### Structure Per Section/Paragraph

Each paragraph in a literature review should:
1. **Topic sentence**: State the theme or claim this paragraph addresses
2. **Evidence**: Cite 2-5 papers supporting or nuancing this claim
3. **Synthesis**: Compare, contrast, and connect the cited works
4. **Transition**: Lead to the next theme or the gap

#### Citation Weaving Patterns

**Integral citation** (author as subject):
"Smith et al. (2024) demonstrated that X increases Y using a randomized controlled trial with 200 participants."

**Non-integral citation** (finding as subject):
"Recent evidence suggests that X increases Y in controlled settings (Smith et al., 2024; Jones et al., 2023), although this effect may be population-dependent (Lee et al., 2022)."

**Synthesis citation** (multiple sources for one claim):
"Several studies have converged on the finding that X modulates Y through mechanism Z (Smith et al., 2024; Jones et al., 2023; Chen et al., 2021), with effect sizes ranging from d = 0.3 to d = 0.8."

**Contrast citation**:
"While Smith et al. (2024) found significant effects using direct measurement, Lee et al. (2022) reported null results in a meta-analysis of self-report studies, suggesting that measurement approach may moderate the effect."

#### Avoid Common Pitfalls

- **Annotated bibliography**: Don't just summarize each paper sequentially. Synthesize.
- **String-of-pearls**: Don't write "Smith found X. Jones found Y. Lee found Z." Connect them.
- **Overclaiming**: Don't say "proves" or "definitively shows." Use "suggests," "indicates," "provides evidence for."
- **Recency bias**: Include foundational/seminal work, not just the last 2 years.
- **Confirmation bias**: Include contradictory findings and explain discrepancies.

### Step 5: Identify the Gap

After synthesizing existing literature, articulate what is missing:

**Gap statement patterns:**
- "Despite these advances, no study has examined {specific question}."
- "While X has been established for {context A}, it remains unclear whether this extends to {context B}."
- "Existing studies are limited by {methodological issue}, and {new approach} could address this."
- "The relationship between X and Y has been studied in isolation, but their interaction under {condition} is unexplored."

### Step 6: Generate Bibliography

```bash
# Export BibTeX for all cited papers
for doi in $(cat cited_dois.txt); do
  uvx opencite lookup "$doi" -f bibtex --append-bib review_refs.bib
done
```

## Output Format

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

## Quality Checklist

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

## Additional Resources

- Reference: [references/review-frameworks.md](references/review-frameworks.md) - PRISMA, PICO, and other review frameworks
