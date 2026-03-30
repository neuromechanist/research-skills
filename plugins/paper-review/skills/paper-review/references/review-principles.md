# Review Principles

This document describes the review philosophy underlying the paper-review skill. The principles are opinionated and reflect a specific reviewer's priorities. Adapt them to your own standards.

## Core Philosophy

A good review serves two purposes: it helps the editor make an informed decision, and it helps the authors improve their work. Both require honesty, specificity, and constructiveness.

## Principle 1: Methods Must Test the Hypothesis

The most common critical flaw in manuscripts is a disconnect between what the introduction promises and what the methods deliver. If the introduction frames a question, the methods must be designed to answer that exact question. If they cannot, the paper has a fundamental problem.

**How to apply:** Trace the logical chain: hypothesis -> experimental design -> analysis -> results -> conclusions. Break at any point means the chain is invalid. A paper that asks about mechanism X but only measures correlate Y cannot conclude about X.

## Principle 2: Statistical Validity is Non-Negotiable

Wrong statistics invalidate conclusions regardless of how interesting the hypothesis is. Common issues include:
- Using parametric tests on non-normal data without testing assumptions
- Using paired tests for unpaired comparisons (or vice versa)
- Performing multiple comparisons without correction
- Drawing population-level conclusions from N=2 or N=3 groups
- Using bar plots with error bars when individual data points would reveal the actual distribution
- Confusing lack of statistical significance with lack of effect
- Confusing correlation with independence (lack of linear correlation does not imply independence)

**How to apply:** For every statistical test in the paper, ask: Is this the right test? Are the assumptions met? Is the sample size adequate? Could the conclusion change with a different (more appropriate) test?

## Principle 3: Claims Must Not Exceed the Data

The discussion section is where overreaching typically happens. Authors may:
- Generalize from a specific population to a broader one
- Attribute causal mechanisms from correlational data
- Draw conclusions about brain regions from scalp recordings without source localization
- Suggest clinical applications from basic science findings without clinical validation

**How to apply:** For every claim in the discussion, check: Is there a result in this paper that directly supports this claim? If the support comes only from cited literature, flag it as speculation, not a finding of this study.

## Principle 4: Be Evidence-Based in Criticism

When challenging a method or claim, cite the literature. Do not rely on "it is well known" or "this is standard practice." The authors deserve to see the evidence behind a reviewer's argument, just as the reviewer demands evidence from the authors.

**How to apply:** If you argue that a method is flawed, cite the paper that demonstrates the flaw. If you argue that a relevant paper is missing, provide the reference. If you argue that a different analysis is more appropriate, cite examples where it was used successfully.

## Principle 5: Acknowledge Strengths Genuinely

A review that only lists weaknesses is not helpful. Genuine acknowledgment of strengths:
- Calibrates the review (shows the reviewer understands what is good)
- Motivates the authors (they know what to preserve during revision)
- Helps the editor weigh the overall contribution

**How to apply:** In the synopsis, explicitly state what the paper does well before transitioning to concerns. Do not manufacture compliments, but do not omit genuine ones either.

## Principle 6: Reproducibility is a Publication Requirement

A paper that cannot be reproduced has limited scientific value. This applies to:
- Experimental methods (sufficient detail for replication)
- Computational methods (code, parameters, software versions)
- Hardware papers (schematics, component specifications, or commercial availability)
- Data (shared or sharing plan addressed)

**How to apply:** Ask: "Could I (or someone in my lab) reproduce this work based solely on what is written here?" If not, identify what is missing.

## Principle 7: Check Conflicts of Interest

Financial and non-financial conflicts must be disclosed. Authors evaluating their own commercial products, patented methods, or institutional tools should disclose these relationships. A paper that is effectively a product validation by the product's creators, without disclosure, has a transparency problem.

**How to apply:** Check author affiliations, acknowledgments, and the relationship between the methods/tools used and the authors' commercial or patent interests. If the connection is not disclosed, flag it.

## Principle 8: Literature Must Be Current and Complete

Missing relevant literature suggests either incomplete scholarship or selective citation. Key checks:
- Are papers from the last 2-3 years included?
- Are competing methods or alternative interpretations cited?
- Do the cited papers actually support the claims they are attached to? (Sometimes a cited paper argues the opposite of what the authors claim.)
- For review papers used as sole references for broad claims, check if more specific primary sources exist.

## Principle 9: Figures Must Not Mislead

Figures are often where misleading presentations hide. Common issues:
- Bar plots with error bars for very small N (N<5), hiding the actual data distribution
- Time or frequency scales that obscure or exaggerate effects
- Missing color legends, axis labels, or units
- Figures that show raw data when the text discusses processed results (or vice versa)
- ERSP or heatmap plots without baseline removal, biasing interpretation

**How to apply:** For every figure, ask: Does this figure accurately represent the data as described in the text? Could a reader be misled by the presentation choice?

## Principle 10: Writing Serves the Science

Clear writing is not optional. Technical terms must be defined before use. Terminology must be consistent (do not introduce synonyms mid-paper). The abstract must accurately reflect the findings. The methods must be complete per the journal's requirements. Redundancy wastes the reader's time and page space.

**How to apply:** Flag instances where unclear writing obscures the science or where inconsistent terminology creates ambiguity about what was actually done.
