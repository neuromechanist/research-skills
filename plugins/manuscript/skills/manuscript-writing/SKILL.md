---
name: manuscript-writing
description: "Use this skill for \"write a paper\", \"draft manuscript\", \"write introduction\", \"write methods section\", \"write results\", \"write discussion\", \"write abstract\", \"structure a paper\", \"academic writing\", \"write for journal\", or when the user wants to draft or revise sections of an academic manuscript."
version: 0.2.2
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
- Active voice with the authors as the actor and the named noun instead of a pronoun ("We measured..." not "Measurements were taken..."; see Habits to avoid while drafting); follow the journal where it prefers passive Methods
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

### Habits to avoid while drafting

These habits make research prose read as machine-written, and reviewers and editors notice them.
Avoid them while drafting; the humanizer pass (patterns 30 to 45) then catches what slips through.
The quoted phrases are examples of each habit, not the full list: a sentence that does the same job in other words breaks the same rule.

- **Show, do not announce.** State the limitation or the result and let it stand. Do not certify your own honesty or rigor ("and we say so", "we say it first", "to be transparent", "we are careful to").
- **Say it once.** Each sentence adds a fact. Drop tails that restate the purpose (", so a gain must come from what the tags say"), closing sentences that repeat the paragraph, and a second gloss of a defined term. Lead with a purpose ("To separate X from Y, ...") only where a reader would ask why.
- **People act, and data do not speak.** Write "We registered the test before seeing any fMRI value", not "The test was registered" or "Hypothesis 1B tests ..."; results predict, differ, or agree, and do not "say", "tell", or "decide". Follow the journal where it prefers passive Methods.
- **Name the noun.** When the referent is a sentence back or two nouns could fit, repeat the noun ("CLIP's prediction", not "its prediction"); "this" needs its noun ("this test"), and the noun must appear just before.
- **Literal claims, not slogans.** No mirrored contrasts ("fMRI shows where, EEG shows when"), contest metaphors ("beat the null"), colon reveals ("The answer is simple: ..."), or verbs of standing ("rests on", "reads as").
- **Answer an objection once, where it arises.** Do not concede and rebut in every paragraph ("X is not the only limit, but ...").
- **Plain time and scope.** Use "now" or "currently" only to contrast with a stated earlier version, and state a real constraint ("only", "never") once.
- **One idea per sentence.** Split chains of "and"; list results strongest first, each with its label.

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
- Sister skill: `manuscript:humanizer` (invoke through the host's skill-invocation mechanism) - Removes 45 categories of AI-writing tells, including sentence-shape tells, hidden actors, and unanchored pronouns in research prose, while respecting academic conventions (e.g., passive voice in Methods, hedging in Discussion). Run after drafting and before peer review.
