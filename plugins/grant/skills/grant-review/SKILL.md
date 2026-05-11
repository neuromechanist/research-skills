---
name: grant-review
description: This skill should be used when the user asks to "review a grant", "review my proposal", "score this grant", "evaluate my specific aims", "critique my research strategy", "review as an NIH reviewer", "review as an NSF panelist", "give me reviewer feedback", "check my grant proposal", "review my R01", "review my K99", "evaluate my CAREER proposal", "run a mock study section", "review my resubmission", "review this PDF", "check my proposal PDF", "analyze my grant layout", or mentions grant review, proposal critique, NIH scoring, NSF panel review, study section feedback, or proposal PDF review.
version: 0.1.2
---

# Grant Proposal Review

Provides structured, actionable grant proposal review in the style of NIH study section or NSF panel reviewers. Evaluates proposals against official scoring criteria and produces feedback from the perspective of senior researchers on scientific review panels.

## When to Use

Activate when the user wants feedback on a grant proposal (specific aims, research strategy, project description) evaluated against NIH or NSF review criteria. The output is a structured review with scores, strengths, weaknesses, and prioritized actionable improvements.

## Review Process

### 1. Identify the mechanism and agency

Determine whether the proposal is NIH or NSF, and which mechanism (R01, R21, DP2, CAREER, etc.). This determines the review criteria, scoring system, and expectations.

When the mechanism is not specified in the proposal or by the user, infer from document structure: presence of Specific Aims indicates NIH; a Project Summary with separate Intellectual Merit and Broader Impacts sections indicates NSF. If the mechanism remains ambiguous, ask the user before proceeding.

Use the following table to select the appropriate criteria reference:

| Mechanism | Criteria Reference |
|-----------|-------------------|
| R01, R21, R03, R15, DP2 | `references/nih-review-criteria.md` |
| K99/R00, K08, K23 | `references/nih-career-training-criteria.md` |
| F31, F32 | `references/nih-career-training-criteria.md` |
| T32 | `references/nih-career-training-criteria.md` |
| NSF Standard, CAREER, RAPID, EAGER | `references/nsf-review-criteria.md` |
| Unknown | Infer from document structure or ask the user |

### 2. Ingest the proposal document

Handle the proposal based on its format:

**Markdown or LaTeX:** Read directly; no conversion needed.

**PDF:** Use a two-track approach:

1. **Text extraction** -- Read the PDF for content review. Use the Read tool directly on the PDF (Claude can read PDFs natively). For large PDFs (>10 pages), read in page ranges (e.g., `pages: "1-10"`, then `pages: "11-20"`). For math-heavy or complex-layout PDFs where native reading struggles, convert to markdown via opencite:
   ```bash
   uvx opencite convert proposal.pdf -o proposal.md
   ```

2. **Visual layout analysis** -- Convert each page to PNG for figure sizing and space utilization review:
   ```bash
   uv run --with pdf2image --with pillow python -c "
   from pdf2image import convert_from_path
   pages = convert_from_path('proposal.pdf', dpi=150)
   for i, page in enumerate(pages):
       page.save(f'proposal_page_{i+1}.png', 'PNG')
   "
   ```
   Note: `pdf2image` requires poppler as a system dependency (`brew install poppler` on macOS, `apt install poppler-utils` on Linux). If poppler is not available, use `pdftoppm -png -r 150 proposal.pdf proposal_page` directly, or fall back to reading the PDF natively with the Read tool.

   Read each page image to assess:
   - Are figures appropriately sized for their content, or oversized with wasted space?
   - Are there large areas of whitespace or underutilized regions?
   - Could any figures be reduced without losing clarity?
   - Are margins and spacing consistent throughout?
   - Is text density appropriate (not too sparse, not too cramped)?

   Include space utilization observations in the review output under a "Layout and Space Utilization" section.

**Read all submitted sections.** For NIH proposals, this typically includes:
- Specific Aims (1 page)
- Research Strategy: Significance, Innovation, Approach
- Any supporting materials (biosketch, facilities, data management plan)

For NSF proposals:
- Project Summary
- Project Description
- Data Management Plan

### 3. Score each criterion

**NIH Scoring (1-9 scale):**

For each of the five review criteria, assign a score and provide justification:

| Criterion | Key Questions |
|-----------|---------------|
| **Significance** | Is the problem important? Will the field advance? |
| **Investigator(s)** | Is the team qualified? Sufficient preliminary data? |
| **Innovation** | Are concepts/methods novel? Does it challenge the status quo? |
| **Approach** | Is the design rigorous? Are methods appropriate? Feasibility? |
| **Environment** | Does the institution support the work? |

Score descriptors:
- 1 (Exceptional): Essentially no weaknesses
- 2 (Outstanding): Extremely minor weaknesses
- 3 (Excellent): Minor weaknesses
- 4 (Very Good): Some moderate weaknesses
- 5 (Good): Moderate weaknesses
- 6 (Satisfactory): Some major weaknesses
- 7 (Fair): Major weaknesses
- 8 (Marginal): Numerous major weaknesses
- 9 (Poor): Fundamentally flawed

**NSF Rating:**
- Excellent / Very Good / Good / Fair / Poor
- Evaluate Intellectual Merit and Broader Impacts separately

### 4. Identify overall strengths and weaknesses

Synthesize across criteria. Focus on:
- **Strengths**: What makes this proposal competitive?
- **Weaknesses**: What would a skeptical reviewer flag?
- **Fatal flaws**: Issues that would prevent funding regardless of other merits

### 5. Produce the review output

Structure the output as described below.

## Review Output Format

Structure the review output according to the appropriate agency template in `references/review-output-templates.md`. Both NIH and NSF templates follow this general structure:

1. **Summary** - 2-3 sentence proposal overview
2. **Criterion scores** - Individual scores (NIH 1-9) or ratings (NSF Excellent-Poor) with strengths/weaknesses for each criterion
3. **Additional review criteria** - Non-scored items (human subjects, data management, rigor)
4. **Layout and space utilization** (when PDF was provided) - Observations on figure sizing, whitespace usage, areas where space could be saved or better utilized, and whether the proposal makes effective use of its page limits
5. **Actionable improvements** - Prioritized as Critical, Important, and Suggested

For a complete worked example, see `examples/sample-nih-r01-review.md`.

## Review Perspective

Adopt the viewpoint of a **senior researcher** on a study section or review panel:

- **Expertise**: Assume deep domain knowledge; do not flag common techniques as novel
- **Skepticism**: Demand evidence for claims; flag unsupported assertions
- **Constructiveness**: Every weakness should include a suggestion for improvement
- **Fairness**: Acknowledge strengths genuinely; do not manufacture weaknesses
- **Calibration**: Score relative to the mechanism (R21 should not be held to R01 preliminary data standards; K awards emphasize career development over research scope; CAREER proposals require genuine research-education integration; DP2 rewards bold, innovative thinking from new investigators)
- **Precision**: Cite specific sections, figures, or claims when identifying issues
- **Impact focus**: Always tie feedback back to how it affects the overall impact score

## Common Issues

For common reviewer comments and their meanings, consult `references/review-best-practices.md`.

When the proposal text triggers reviewer comments about "writing quality", "lack of specificity", "promotional language", or "buzzwords", point the applicant to `manuscript:humanizer`. Patterns most relevant to grant prose: 1 (significance inflation), 4 (promotional language), 7 (AI vocabulary), 8 (copula avoidance), 14 (em-dash overuse), 24 (excessive hedging), 25 (generic positive conclusions).

## Additional Resources

### Reference Files
- **`references/nih-review-criteria.md`** - Complete NIH review criteria, scoring rubric, and study section process
- **`references/nih-career-training-criteria.md`** - Review criteria for K, F, and T32 mechanisms
- **`references/nsf-review-criteria.md`** - Complete NSF review criteria and panel process
- **`references/review-best-practices.md`** - Best practices from experienced reviewers, common reviewer comments, and calibration guidance
- **`references/review-output-templates.md`** - NIH and NSF review output format templates
- **Sister skill `manuscript:humanizer`** - 29 AI-writing patterns to flag when assessing grant prose quality

### Examples
- **`examples/sample-nih-r01-review.md`** - Complete example review demonstrating expected format, tone, and scoring calibration
