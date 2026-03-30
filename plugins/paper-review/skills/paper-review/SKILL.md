---
name: paper-review
description: "Use this skill for \"review this paper\", \"review this manuscript\", \"peer review\", \"review my paper\", \"critique this manuscript\", \"review this submission\", \"give me feedback on my paper\", \"check my methods\", \"review my statistics\", \"review as a peer reviewer\", \"evaluate this manuscript\", \"review this PDF\", or mentions manuscript review, peer review, paper critique, or methodological review."
version: 0.1.0
---

# Academic Manuscript Review

Provides structured, rigorous peer review of academic manuscripts. Reviews prioritize methodological soundness, statistical validity, logical consistency, and reproducibility.

> **Note on review calibration:** This skill reflects an opinionated review style that prioritizes methodological precision, statistical rigor, and reproducibility. It is direct, evidence-based, and holds manuscripts to high standards. The severity calibration (Critical, Major, Minor) follows a strict hierarchy: Critical issues block publication; Major issues require significant revision; Minor issues improve polish. Reviewers using this skill should adapt the tone and depth to their own standards and the target journal's expectations.

## When to Use

Activate when the user wants peer-review feedback on a manuscript (journal article, conference paper, preprint) evaluated for methodological soundness, statistical validity, and clarity of presentation. The output is a structured review with categorized concerns and constructive suggestions.

## Manuscript Intake

Manuscripts for peer review are typically provided as PDFs from journal submission systems. Convert to markdown first for reliable text extraction, then read figures from the PDF directly.

**PDF (most common):** Convert to markdown using opencite, then read the markdown for the full text review:
```bash
uvx opencite convert manuscript.pdf -o manuscript.md
```
After conversion, read `manuscript.md` for the text-based review. Also read the original PDF using the Read tool to inspect figures, tables, and layout that may not convert cleanly to markdown. For large PDFs (>10 pages), read in page ranges (e.g., `pages: "1-10"`, then `pages: "11-20"`).

**Markdown or LaTeX:** Read directly; no conversion needed.

Read all sections including supplementary materials, appendices, and figures. Note the target journal if known, as expectations differ across venues (transactions vs. letters vs. conference proceedings).

## Review Process

### 1. Read the full manuscript

Read everything: abstract, introduction, methods, results, discussion, conclusion, figures, tables, supplementary materials. Take note of:
- The stated hypothesis or research question
- The methods used to test the hypothesis
- The statistical approach and sample size
- The claims made in the discussion and conclusion
- Whether figures and tables support the narrative

### 2. Assess methodological soundness

This is the core of the review. Evaluate using the checklist in `references/methodology-checklist.md`. Key areas:

**Experimental design:**
- Is the design appropriate for the research question?
- Are controls adequate?
- Is the sample size justified (power analysis, or at minimum acknowledged)?
- Are inclusion/exclusion criteria clearly stated and justified?
- Are there potential confounds that are not addressed?

**Signal processing and data analysis (when applicable):**
- Are filtering parameters appropriate? Check Nyquist constraints: the analysis bandwidth must not exceed half the sampling rate or half the filter cutoff.
- Are artifact rejection/correction methods validated for the specific data type?
- Are analysis parameters (e.g., window lengths, frequency bands) justified?
- Is there any "double-dipping" where the same data features used for selection/clustering are also the analysis target?

**Statistical methods:**
- Are the chosen tests appropriate for the data distribution and design?
- Are parametric assumptions tested (normality, homogeneity of variance)?
- For paired vs. unpaired comparisons, is the correct test variant used?
- Are main effects tested before post-hoc comparisons?
- Are multiple comparisons corrected?
- Are effect sizes reported, not just p-values?
- Do small sample sizes warrant the statistical conclusions drawn?
- Are figures appropriate for the data? (Bar plots with error bars for N<5 are misleading; use individual data points instead.)

### 3. Check logical consistency

Trace the argument from introduction through methods to results and discussion:
- Do the methods actually test the stated hypothesis?
- Do the results support the claims made in the discussion?
- Are conclusions proportional to the evidence? (Do not overreach.)
- If the introduction frames a problem, do the methods address that exact problem?
- Are terms and definitions used consistently throughout?
- If a concept is introduced in the introduction, is it operationalized the same way in the methods?

Watch for contradictions: claims in the introduction that the authors' own methods cannot test, or discussion points that go beyond what the data show.

### 4. Evaluate literature coverage

- Is the literature review current? (Check if key papers from the last 2-3 years are missing.)
- Are the authors' claims supported by the cited literature, or do the cited papers actually argue otherwise?
- Is related work from other groups or approaches acknowledged?
- For the specific techniques used, are validation/limitation papers cited?
- Are there relevant studies the authors should compare their results against?

Use opencite to verify literature claims and search for potentially missing references:
```bash
uvx opencite search "topic keywords" --max 10 --sort citations
uvx opencite canonical "field or method" --max 5
```
When citing references in the review to support a methodological argument, include the full citation so the authors can verify the claim.

### 5. Check reproducibility and transparency

- Are methods described in sufficient detail to reproduce?
- Are data, code, and materials shared or is sharing addressed?
- Are custom tools, software versions, and parameters specified?
- For hardware or device papers: is enough detail provided (schematics, component lists, block diagrams) for independent reproduction?
- Are conflicts of interest disclosed? Check author affiliations, patents, and commercial products related to the work.

### 6. Evaluate figures and tables

Read each figure and table carefully:
- Do figures accurately represent the data?
- Are axes labeled, legends present, and units specified?
- Are statistical annotations (significance stars, error bars) defined?
- Are bar plots used appropriately? (For small N, show individual data points.)
- Is the time/frequency scale appropriate for the data shown?
- Do the figures match what is described in the text?
- Are color scales defined with legends?

### 7. Assess writing quality

- Are technical terms defined before or immediately after first use?
- Is terminology consistent throughout? (Do not introduce synonyms mid-paper.)
- Is the writing concise? Flag unnecessary repetition.
- Are abbreviations defined on first use and not redefined?
- Does the abstract accurately reflect the paper's content and findings?
- Is the methods section complete per the target journal's guidelines?

## Review Output Format

Structure the review according to the template in `references/review-output-template.md`:

1. **Synopsis** - 1 paragraph summarizing the paper's goal, methods, findings, strengths, and overall assessment
2. **Critical Issues** - Numbered list of issues that would prevent publication (methodological flaws, invalid statistics, unsupported claims)
3. **Major Concerns** - Numbered list of significant issues requiring revision (incomplete analysis, missing comparisons, overreached conclusions)
4. **Minor Concerns** - Numbered list of issues that improve clarity and polish (writing, figures, references)
5. **Editor Note** (optional) - Brief summary for the editor with recommendation

Every concern must:
- Cite the specific location (page, line, figure, or section)
- Explain what the problem is and why it matters
- Provide a constructive suggestion or alternative approach
- Cite supporting references when arguing a methodological point

## Review Principles

Consult `references/review-principles.md` for the full rationale. Summary:

1. **Be direct but constructive** - Every weakness must include a suggestion for improvement
2. **Be evidence-based** - Cite literature when challenging methods or claims; do not rely on authority alone
3. **Be proportional** - Calibrate severity to actual impact on the paper's validity
4. **Acknowledge strengths genuinely** - Do not manufacture weaknesses; recognize good work
5. **Question logical consistency** - If the intro says X, the methods must test X, and the discussion must conclude about X
6. **Demand statistical appropriateness** - Wrong tests invalidate conclusions regardless of significance
7. **Insist on reproducibility** - Papers that cannot be reproduced have limited scientific value
8. **Check the literature** - Missing relevant work suggests incomplete understanding of the field
9. **Scrutinize figures** - Figures are often where misleading presentations hide
10. **Hold claims to the data** - The discussion must not exceed what the results demonstrate

## Additional Resources

### Reference Files
- **`references/review-output-template.md`** - Complete review output format with examples
- **`references/methodology-checklist.md`** - Detailed methodological assessment checklist
- **`references/review-principles.md`** - Review philosophy and calibration guidance
- **`references/statistical-review-guide.md`** - Common statistical issues and how to identify them
- **`references/figure-review-guide.md`** - Figure quality assessment criteria
