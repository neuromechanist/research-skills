# Grant Review Best Practices

## Reviewer Calibration

### Score Calibration (NIH)
Based on analysis of publicly available NIH review data and reviewer guidance:

- **Score 1-2 (Exceptional/Outstanding)**: Reserved for proposals that are clearly fundable. Strong preliminary data, expert team, clear significance, innovative approach, minimal weaknesses.
- **Score 3 (Excellent)**: Very strong proposal with minor, addressable weaknesses. Would be competitive for funding.
- **Score 4-5 (Very Good/Good)**: Solid proposal with moderate weaknesses that could be addressed in revision. Often the "encourage resubmission" range.
- **Score 6-7 (Satisfactory/Fair)**: Significant concerns about feasibility, significance, or approach. Major revision needed.
- **Score 8-9 (Marginal/Poor)**: Fundamental flaws in concept, design, or feasibility. Likely needs complete reconceptualization.

### Mechanism-Appropriate Expectations
- **R01**: Expect substantial preliminary data. Approach should be detailed and feasible. Budget should match ambition.
- **R03**: Small grant mechanism with limited scope (2 years, ~$50K/year direct). Do not expect preliminary data at the level of an R01. Focus on whether the question is well-defined and the approach is feasible within the constrained budget and timeline.
- **R15/AREA**: Designed for institutions that do not receive substantial NIH funding. Environment expectations differ from R01; evaluate relative to the institution's resources. Emphasis on undergraduate student involvement in research, training potential, and impact on the institutional research environment.
- **R21**: High-risk/high-reward is the point. Do not penalize for limited preliminary data. Focus on innovation and potential impact.
- **DP2**: Emphasis on PI creativity and innovation. Broader audience. Risk tolerance higher than R01.
- **K99/R00**: Evaluate candidate development alongside science. Mentoring plan quality matters. Transition plan from mentored to independent phase is a key element.
- **K08/K23**: Career development plan is paramount. The research plan should serve as a training vehicle. Evaluate whether the candidate genuinely needs additional mentored experience versus being ready for an R01.
- **F31/F32**: Training-focused evaluation. Assess the quality of the mentoring plan, the sponsor's track record of training successful researchers, and the training potential of both the applicant and the proposed research. Research plan complexity should match the trainee's career stage.
- **CAREER (NSF)**: Research-education integration is critical, not an add-on. Evaluate whether the educational plan is original and whether integration is genuinely bidirectional.

### Resubmission Handling
- NIH allows one amended application (A1); there is no A2 resubmission
- Resubmissions include a 1-page Introduction summarizing changes in response to prior critiques
- Evaluate whether the Introduction clearly and concisely addresses each prior concern
- Assess the quality of the response: a superficial or dismissive response to valid critiques is a weakness
- The revised application should stand on its own merit; do not score solely based on how well prior concerns were addressed
- New weaknesses may arise from changes made in response to prior critiques; flag these clearly
- If the prior review identified a fundamental flaw (e.g., wrong model system), evaluate whether the revision genuinely resolves it or merely adjusts the framing

## Common Reviewer Comments

The comment groups below are organized by topic (Significance, Innovation, Approach, Investigator) for ease of lookup. Under the NIH RPG Simplified Review Framework these topics roll into factors: Significance + Innovation into **Factor 1 (Importance)**, Approach into **Factor 2 (Rigor and Feasibility)**, and Investigator (with Environment) into **Factor 3 (Expertise and Resources, assessed not scored)**. See `nih-review-criteria.md`.

### Specific Aims
| Comment | What It Means | How to Fix |
|---------|--------------|-----------|
| "Aims are too interdependent" | If Aim 1 fails, 2 and 3 collapse | Restructure so each aim has independent value |
| "Overarching goal is vague" | Not clear what success looks like | Sharpen to a testable, measurable statement |
| "Hypotheses are not testable" | Predictions too vague to confirm/refute | State specific, quantifiable predictions |
| "Too ambitious for the timeline" | More work than can be done in the period | Reduce scope or extend timeline |
| "Missing impact statement" | No clear articulation of what changes | Add explicit "Expected Impact" section |

### Significance
| Comment | What It Means | How to Fix |
|---------|--------------|-----------|
| "Incremental advance" | Not enough impact for the investment | Articulate how this changes the field, not just adds data |
| "Not connected to NIH mission" | Significance framed too narrowly | Connect to health outcomes or NIH IC priorities |
| "Gap not established" | Literature review doesn't convincingly show what's missing | Cite specific failed attempts or knowledge gaps |

### Innovation
| Comment | What It Means | How to Fix |
|---------|--------------|-----------|
| "Not clear what's new" | Innovations buried or poorly articulated | Lead with explicit innovation statements |
| "Similar work by [lab]" | Novelty claim is incorrect | Acknowledge prior work and differentiate |
| "Innovation only in application" | Methods are standard, just applied to new question | Frame as methodological advancement or acknowledge |

### Approach
| Comment | What It Means | How to Fix |
|---------|--------------|-----------|
| "Missing power analysis" | Can't assess if study is adequately powered | Add formal power calculation with effect sizes |
| "No alternative approaches" | What happens when things go wrong? | Add "Potential Problems and Alternatives" for each aim |
| "Methods too vague" | Reviewer can't assess feasibility | Add specific protocols, parameters, analysis steps |
| "SABV not addressed" | Sex as a Biological Variable missing | Add sex-based analysis plan (NIH requirement since 2016) |
| "Rigor concerns" | Missing blinding, randomization, or controls | Add explicit rigor section with these elements |
| "Timeline unrealistic" | Too much work, too little time | Revise Gantt chart with realistic task durations |

### Investigator
| Comment | What It Means | How to Fix |
|---------|--------------|-----------|
| "Insufficient preliminary data" | Claims not supported by evidence | Add pilot data figures, even if small-scale |
| "Team missing [expertise]" | Gap in required skills | Add consultant or collaborator with that expertise |
| "PI effort insufficient" | Not enough time committed | Increase calendar months on budget |

## Crafting Actionable Feedback

### Good Feedback Pattern
```
[Specific issue]: [Evidence from the proposal] -> [Why it matters for the score] -> [Specific suggestion]
```

**Example 1 (Approach):**
"The power analysis (Approach, p.8) assumes a large effect size (d=0.8) but the preliminary data (Figure 3) suggest a moderate effect (d=0.5). This raises concerns about whether the proposed N=30 will be sufficient to detect the predicted differences. Consider either: (a) increasing sample size to N=50 based on the observed effect, or (b) providing additional justification for the expected effect size from the literature."

**Example 2 (Significance):**
"The proposal frames the gap as 'no studies have examined X in population Y' (Significance, p.2), but does not explain why this gap matters clinically or mechanistically. Two recent papers (Smith 2023, Jones 2024) have examined related populations with null results. Address why the proposed population would yield different outcomes, or reframe the significance around the mechanistic question rather than the population gap."

**Example 3 (Innovation):**
"The proposed use of single-cell RNA-seq (Innovation, p.5) is described as innovative, but this technique is now standard in the field with over 200 published studies in this tissue type. Reframe the innovation around the computational pipeline for integrating spatial transcriptomics with functional imaging data, which is genuinely novel and represents the actual methodological advance."

**Example 4 (Investigator):**
"The biosketch lists 15 publications in the proposed area, but none include the quantitative modeling approach central to Aim 3. Adding a co-investigator or named consultant with published modeling expertise would strengthen the team and address feasibility concerns for the computational aims."

### Bad Feedback Patterns to Avoid
- "The approach is weak" (too vague)
- "I don't find this interesting" (subjective without justification)
- "This has been done before" (without citation)
- "The budget is too high" (not a scientific critique)
- "The writing is poor" (unless it genuinely impedes understanding)

## Review Checklist

### Before Writing the Review
- [ ] Read the entire proposal, including supplementary materials
- [ ] Note the mechanism and its expectations
- [ ] Identify the 2-3 most important strengths
- [ ] Identify the 2-3 most important weaknesses
- [ ] Check if the proposal addresses known requirements (SABV, rigor, DMS)

### During the Review
- [ ] Score each factor independently (don't let one dominate prematurely); assess Factor 3 (Expertise and Resources) rather than scoring it 1-9
- [ ] Cite specific pages, figures, or sections in feedback
- [ ] Provide at least one actionable suggestion per weakness
- [ ] Acknowledge genuine strengths, especially in innovative proposals
- [ ] Consider: "Would this proposal improve with revision?"

### After Writing the Review
- [ ] Check that overall impact score reflects the balance of strengths and weaknesses
- [ ] Verify that every weakness includes a constructive suggestion
- [ ] Ensure the review is professional and respectful
- [ ] Confirm the review would be useful to the PI regardless of funding outcome

## Avoiding Bias in Review

NIH reviewer training and NSF panel orientation both emphasize the following principles:

- **Evaluate the science, not the scientist**: Focus on the proposed work, methodology, and feasibility. Do not let institutional prestige, PI demographics, or personal familiarity with the investigator influence the score.
- **Avoid halo/horns effects**: A strong Importance (Factor 1) assessment does not automatically mean Rigor and Feasibility (Factor 2) is strong. Evaluate each factor independently based on the evidence for that factor.
- **Guard against confirmation bias**: Do not selectively seek evidence to support an initial impression. Read the entire proposal before forming a judgment.
- **Separate novelty from quality**: An unconventional approach is not inherently better or worse than a conventional one. Evaluate whether the approach is appropriate for the question.
- **Acknowledge uncertainty**: If expertise is insufficient to evaluate a specific method or analysis, state this limitation rather than penalizing or ignoring the section.
- **Be aware of scope creep in expectations**: Do not hold an R21 to R01 standards, a K award to R01 research scope, or a new investigator to the track record of an established PI.

## Score Distribution Notes

- Score distributions vary by study section; some sections cluster around 3-5, while others use the full 1-9 range
- The same proposal may receive different scores in different study sections due to reviewer expertise, section culture, and competition
- When calibrating scores for this review tool, aim for the center of the expected distribution: reserve 1-2 for genuinely outstanding proposals and 7-9 for proposals with fundamental flaws
- Most competitive, fundable R01s cluster in the 2-4 range; proposals scoring 5+ are typically not discussed or not funded

## NIH Summary Statement Structure

For reference, an NIH summary statement typically contains:

1. **Resume and Summary of Discussion** - Brief narrative of the panel discussion
2. **Critique 1 (Primary Reviewer)** - Detailed review with factor scores (RPG: Factor 1 and Factor 2 scored, Factor 3 assessed)
3. **Critique 2 (Secondary Reviewer)** - Additional perspective
4. **Critique 3 (if assigned)** - Often focused on methodology/statistics
5. **Overall Impact Score** - From all voting members
6. **Budget Recommendations** - Any suggested adjustments
7. **Administrative Notes** - Human subjects, animal welfare, etc.
