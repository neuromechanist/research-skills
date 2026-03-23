---
name: grant-review
description: This skill should be used when the user asks to "review a grant", "review my proposal", "score this grant", "evaluate my specific aims", "critique my research strategy", "review as an NIH reviewer", "review as an NSF panelist", "give me reviewer feedback", "check my grant proposal", or mentions grant review, proposal critique, NIH scoring, NSF panel review, or study section feedback.
version: 0.1.0
---

# Grant Proposal Review

Provides structured, actionable grant proposal review in the style of NIH study section or NSF panel reviewers. Evaluates proposals against official scoring criteria and produces feedback from the perspective of senior researchers on scientific review panels.

## When to Use

Activate when the user wants feedback on a grant proposal (specific aims, research strategy, project description) evaluated against NIH or NSF review criteria. The output is a structured review with scores, strengths, weaknesses, and prioritized actionable improvements.

## Review Process

### 1. Identify the mechanism and agency

Determine whether the proposal is NIH or NSF, and which mechanism (R01, R21, DP2, CAREER, etc.). This determines the review criteria, scoring system, and expectations. Consult `references/nih-review-criteria.md` or `references/nsf-review-criteria.md` for details.

### 2. Read the full proposal

Read all submitted sections. For NIH proposals, this typically includes:
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

### NIH-Style Review

```
## Summary of Proposal
[2-3 sentence summary of what the proposal aims to do]

## Overall Impact Score: [1-9]
[Brief justification for overall impact score]

---

## Criterion Scores

### Significance: [1-9]
**Strengths:**
- [Bullet points]

**Weaknesses:**
- [Bullet points]

### Investigator(s): [1-9]
**Strengths:**
- [Bullet points]

**Weaknesses:**
- [Bullet points]

### Innovation: [1-9]
**Strengths:**
- [Bullet points]

**Weaknesses:**
- [Bullet points]

### Approach: [1-9]
**Strengths:**
- [Bullet points]

**Weaknesses:**
- [Bullet points]

### Environment: [1-9]
**Strengths:**
- [Bullet points]

**Weaknesses:**
- [Bullet points]

---

## Additional Review Criteria
- **Protections for Human Subjects:** [Acceptable / Concerns]
- **Data Management Plan:** [Acceptable / Needs revision]
- **Rigor and Reproducibility:** [Addressed / Needs strengthening]
- **Budget:** [Appropriate / Concerns]

---

## Actionable Improvements (Priority Order)

### Critical (would likely prevent funding)
1. [Specific, actionable improvement with rationale]
2. [...]

### Important (would significantly improve score)
1. [Specific, actionable improvement with rationale]
2. [...]

### Suggested (would strengthen the proposal)
1. [Specific, actionable improvement with rationale]
2. [...]
```

### NSF-Style Review

```
## Summary of Proposal
[2-3 sentence summary]

---

## Intellectual Merit: [Excellent/Very Good/Good/Fair/Poor]
**Strengths:**
- [Bullet points]

**Weaknesses:**
- [Bullet points]

## Broader Impacts: [Excellent/Very Good/Good/Fair/Poor]
**Strengths:**
- [Bullet points]

**Weaknesses:**
- [Bullet points]

## Summary Assessment: [Excellent/Very Good/Good/Fair/Poor]
[Paragraph synthesizing the evaluation]

---

## Actionable Improvements (Priority Order)

### Critical
1. [Specific improvement]

### Important
1. [Specific improvement]

### Suggested
1. [Specific improvement]
```

## Review Perspective

Adopt the viewpoint of a **senior researcher** on a study section or review panel:

- **Expertise**: Assume deep domain knowledge; do not flag common techniques as novel
- **Skepticism**: Demand evidence for claims; flag unsupported assertions
- **Constructiveness**: Every weakness should include a suggestion for improvement
- **Fairness**: Acknowledge strengths genuinely; do not manufacture weaknesses
- **Calibration**: Score relative to the mechanism (R21 should not be held to R01 preliminary data standards)
- **Precision**: Cite specific sections, figures, or claims when identifying issues
- **Impact focus**: Always tie feedback back to how it affects the overall impact score

## Common Issues to Watch For

### Specific Aims
- Aims too interdependent (if Aim 1 fails, Aims 2-3 collapse)
- Overarching goal too vague or too narrow
- Hypotheses not testable or too obvious
- Missing expected impact statement

### Significance
- Problem not connected to broader field or NIH/NSF mission
- Gaps not clearly identified
- Incremental advance presented as transformative

### Innovation
- Claims of novelty without evidence ("for the first time" without citation search)
- Confusing "nobody has done this" with "this is innovative and valuable"
- Innovation only in application, not acknowledged as such

### Approach
- Insufficient power analysis or sample size justification
- Missing potential problems and alternatives
- Methods too vague (suggests the PI hasn't piloted)
- Overly ambitious timeline
- Preliminary data doesn't support feasibility
- Sex as a Biological Variable (SABV) not addressed (NIH)
- Rigor and reproducibility section missing or superficial

### Budget
- Personnel effort doesn't match proposed work
- Equipment requests without justification
- Travel without scientific rationale

## Additional Resources

### Reference Files
- **`references/nih-review-criteria.md`** - Complete NIH review criteria, scoring rubric, and study section process
- **`references/nsf-review-criteria.md`** - Complete NSF review criteria and panel process
- **`references/review-best-practices.md`** - Best practices from experienced reviewers, common reviewer comments, and calibration guidance
