---
name: manuscript-writing
description: "Use this skill for \"write a paper\", \"draft manuscript\", \"write introduction\", \"write methods section\", \"write results\", \"write discussion\", \"write abstract\", \"structure a paper\", \"academic writing\", \"write for journal\", or when the user wants to draft or revise sections of an academic manuscript."
version: 0.2.1
---

# Academic Manuscript Writing

Guide the drafting and revision of academic manuscripts following journal conventions and scientific writing best practices.

## When to Use

- Drafting a new manuscript from scratch
- Writing or revising specific sections (Introduction, Methods, Results, Discussion)
- Structuring a paper from experimental results
- Converting a conference paper to a journal submission
- Responding to reviewer comments with revised text

## Manuscript Structure

### Standard IMRAD Format

| Section | Purpose | Tense | Length Guide |
|---------|---------|-------|-------------|
| Title | Convey main finding | N/A | 10-15 words |
| Abstract | Self-contained summary | Past (methods/results), Present (conclusions) | 150-300 words |
| Introduction | Context, gap, hypothesis | Present (known facts), Past (prior work) | 3-5 paragraphs |
| Methods | Reproducibility | Past | As needed |
| Results | Report findings | Past | Parallel to Methods |
| Discussion | Interpret findings | Present (interpretation), Past (what was found) | 4-6 paragraphs |
| Conclusion | Key takeaways | Present | 1-2 paragraphs |

### Section-by-Section Guidance

#### Introduction
Structure as a funnel:
1. **Broad context** - Establish the field and importance (1-2 paragraphs)
2. **Narrow focus** - What is known about the specific topic (1-2 paragraphs)
3. **Gap statement** - What remains unknown or problematic
4. **Objective/hypothesis** - What this paper addresses and how

#### Methods
- Enough detail for replication
- Subsections mirror Results sections
- Include: participants/subjects, materials, procedures, analysis
- Statistical methods: specify tests, software, significance thresholds
- Ethics: IRB/IACUC approval statement

#### Results
- Present findings without interpretation
- Start each subsection with the analysis performed, then the outcome
- Report effect sizes, confidence intervals (not just p-values)
- Reference figures and tables in order
- Use "significant" only for statistical significance

#### Discussion
Structure:
1. **Summary of key findings** (1 paragraph)
2. **Interpretation in context** of prior literature (2-3 paragraphs)
3. **Limitations** (1 paragraph, honest but not self-defeating)
4. **Future directions** (1 paragraph)
5. **Conclusion** (1 paragraph)

## Writing Principles

### Clarity
- One idea per sentence
- Active voice preferred ("We measured..." not "Measurements were taken...")
- Define abbreviations on first use
- Avoid jargon unless writing for a specialist audience

### Precision
- Quantify claims ("increased by 23%" not "significantly increased")
- Cite sources for factual claims
- Distinguish correlation from causation
- Use hedging appropriately ("suggests" vs "proves")

### Flow
- Each paragraph: topic sentence, evidence, interpretation
- Transitions between paragraphs connect ideas
- Logical progression within and across sections
- Consistent terminology (don't alternate between synonyms for key concepts)

### Citations
- Cite primary sources, not reviews (when possible)
- Recent citations show awareness of current literature
- Cite competing or contradictory findings
- Self-citation should be relevant, not gratuitous

## Revision Checklist

After drafting, check:
- [ ] Abstract accurately reflects the paper content
- [ ] Introduction gap statement matches the study objective
- [ ] Methods are sufficient for replication
- [ ] Results match Methods (parallel structure)
- [ ] Discussion addresses all major findings
- [ ] Figures are referenced in text in order
- [ ] All abbreviations defined on first use
- [ ] References complete and consistently formatted
- [ ] Word/page count within journal limits
- [ ] Run `manuscript:humanizer` as a final natural-writing pass (strips AI tells like significance inflation, em-dashes, "evolving landscape" filler, rule-of-three padding) before review

## Additional Resources

- Reference: [references/section-templates.md](references/section-templates.md) - Templates for each manuscript section
- Reference: [references/revision-response.md](references/revision-response.md) - How to write point-by-point responses to reviewers
- Sister skill: `manuscript:humanizer` (invoke with the Skill tool by that name) - Removes 29 categories of AI-writing tells while respecting academic conventions (e.g., passive voice in Methods, hedging in Discussion). Run after drafting and before peer review.
