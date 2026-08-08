# NIH SBIR and STTR Requirements

Small Business Innovation Research (SBIR) and Small Business Technology Transfer (STTR) applications are scored by a different kind of panel, against a different standard, than an R01.
Most of the advice in `nih-requirements.md` and `research-strategy-guidelines.md` still applies, but three habits carried over from research-grant writing will actively lose points here.
Those three are covered first because they are the common failure mode.

## What is different from a research grant

### 1. Milestones, not hypotheses

**SBIR and STTR projects are not hypothesis-driven or exploratory.**
Each aim and sub-aim states a concrete, quantitative milestone that defines what success looks like, so a reviewer can tell without judgment calls whether the aim was met.

Do not write, in an SBIR aim:

> *Hypothesis 2A: Grounding transfers across corpora.*
> We will determine whether the representation generalizes.

Write instead:

> **Milestone 2:** Frozen-encoder accuracy on three held-out corpora reaches at least 70% balanced accuracy, against a 46.4% floor registered before the data are opened. **Go/no-go:** two of three corpora must clear the floor to proceed to Aim 3.

The `examples/sbir-specific-aims-template.md` file carries the full milestone-driven aims structure.
This is the single most common piece of feedback NIH program staff give on first-time small-business aims pages, and it is the reason the generic `examples/specific-aims-template.md` should not be used unmodified for a small-business application.

Verb choice follows from this. "Determine whether," "investigate," "explore," and "characterize" signal an exploratory project. "Build," "validate," "demonstrate," "reach," and "reduce to" signal a development project with a defined endpoint.

The funded applications indexed in `niaid-sample-applications.md` show what this looks like in practice.
Aim headings carry a month window.
Each aim closes with a bold milestone sentence naming a quantity, a threshold with units, the test set it is measured on, and the comparator.
Where one aim gates the next, the go/no-go threshold appears in the aim, and in the strongest examples again in the Research Strategy with the alternative that fires if the threshold is missed.
The review criteria ask for exactly this: for Phase I and for the Phase I portion of a Fast-Track, reviewers are asked whether there are clear, appropriate, measurable goals, that is, milestones, to be achieved before Phase II begins.

### 2. The panel is not made of domain experts

Every reviewer on a small-business study section scores the application, and only some of them will know the field.
The Specific Aims page and the Research Strategy must be understandable to a reviewer who is technically strong but works in a different area.
Write the problem, the product, and the milestone in plain language first, and put the domain-specific detail after it rather than in place of it.

### 3. The application is the whole record

Reviewers evaluate only what is inside the application.
A manuscript that is "available on request," a preprint referenced by digital object identifier (DOI), or preliminary data that lives in a paper under review contributes nothing to the score unless the relevant content is reproduced in the Research Strategy.
If a result matters to the argument, restate the result, the sample, the comparison, and the effect size in the Research Strategy itself.

### 4. Personal credentials belong in the biosketch

Award histories, key-personnel roles, standards-body positions, and advisor names belong in the biosketch and in Facilities, not on the Specific Aims page.
Space on the aims page buys milestones.

### 5. Business capability is scored, in every phase

The panel scores whether the company can commercialize, not only whether it can do the science.
The scored criteria on the current parent Notice of Funding Opportunity (NOFO) ask whether the project has commercial potential to lead to a marketable product,
whether the principal investigator and team hold commercialization expertise,
and whether the small business has, or has identified, appropriate business expertise and resources.
This applies to Phase I, where no Commercialization Plan is permitted.
A funded STTR Phase I in the sample set drew three business criticisms in a single reviewer's overall-impact paragraph:
no business leadership on the team, no plan for turning the award into a viable business, and no letters of interest from industry.
That same reviewer recorded no weaknesses at all under any of the five scored criteria.

Name a commercialization lead in the biosketches, state the business route somewhere in the Research Strategy or Facilities, and collect customer letters, even for Phase I.

## Program structure

| | SBIR | STTR |
|---|---|---|
| Share of the agency research and development budget | 3.2% | 0.45% |
| Research partnership | Allowed | **Required**, with a non-profit research institution |
| Outsourcing limit | 33% of Phase I, 50% of Phase II | Minimum 40% by the small business, 30% by the research institution |
| Principal investigator (PI) employment | Primary employment, above 50%, must be with the small business | May be employed by either the small business or the partnering institution |

Funds always go to the small business in both programs.

### Application types

| Type | Activity code | What it is for |
|---|---|---|
| Phase I | R43 (SBIR), R41 (STTR) | Establish feasibility, technical merit, and commercial potential |
| Phase II | R44 (SBIR), R42 (STTR) | Continue research and development begun in Phase I, against Phase I milestones already met |
| Fast-Track | R44 / R42 | Phase I and Phase II submitted and reviewed together; requires a fully developed Phase II plan at submission |
| Direct to Phase II | R44 / R42 | Feasibility already demonstrated **without a prior Phase I SBIR or STTR award for that project** |
| Phase IIB Strategic Breakthrough | R44 / R42 | Projects needing time and effort beyond a standard two-year Phase II; offered by some Institutes and Centers only |
| Commercialization Readiness Pilot (CRP) | | Late-stage development support for existing Phase II and Phase IIB awardees |

### Budgets and timelines

Verified against NIH SEED on 2026-08-07. These figures are adjusted periodically, so confirm against the live page before relying on them.

| Phase | Budget guideline | Project period |
|---|---|---|
| Phase I | $323,090 | 6 months to 2 years |
| Phase II | $2,153,927 | 1 to 3 years |
| CRP | $4,191,495 | up to 3 years |

Individual Institutes and Centers may set their own limits below these.
NIH holds a Small Business Administration waiver allowing larger awards on approved topics for Phase I and Phase II; check the Institute, Center, and Office funding considerations page.
Contact program staff before submitting a budget above the guideline.

Note that Phase I runs **up to two years**, which is longer than most applicants assume.
A project scoped at 24 to 30 months is often a Phase I plus a Phase II, not a single Direct-to-Phase-II.

**The NOFO and the Institute override these figures in both directions.**
The current parent SBIR NOFO states that total support normally may not exceed the current Small Business Administration budgetary guidelines,
while listing per-component budget ceilings that exceed them for many Institutes under approved waivers.
The same NOFO states that award periods normally may not exceed 6 months for Phase I and 2 years for Phase II.
These are statutory guidelines rather than hard ceilings; deviations are permitted but must be justified in the application.
That justification is not optional in practice.
A Phase I in the sample set went over the mandatory cap without the required justification, and the committee said so in the budget recommendations;
a Phase II in the same set went over the statutory guideline and stated plainly that the budget waiver was elected, and drew no criticism.
Read the budget and project period sections of your own NOFO, check the Institute's funding considerations page, and talk to program staff before choosing either number.

Note that these are also the figures most likely to be stale in any document you read, including this one.
Verify them at the source every cycle.

## The Commercialization Plan

**Maximum 12 pages. Required for Fast-Track, Phase II, Phase IIB, and Direct to Phase II.**
It is not required for, and cannot be submitted with, a standalone Phase I.

This is a business plan, and it is scored.
NIH prescribes its six section headings: value of the project with expected outcomes and impact; company; market, customer, and competition; intellectual property protection; finance plan; production and marketing plan with revenue stream.

The 12-page requirement is a real gate on mechanism choice.
An applicant who has not yet done customer discovery, has no signed customer commitments, and cannot size a market from primary evidence will struggle to write a compelling one, and a weak Commercialization Plan drags the overall impact score on an application whose science is strong.

`commercialization-plan-guide.md` in this directory covers the plan section by section, with the structures funded plans use and the criticisms weak ones draw.

## Letters of support

Reviewers expect **letters from potential customers** stating interest in the product, not only letters from academic collaborators and consultants.
A letter that says a customer would evaluate, pilot, purchase, or integrate the product is worth more than one praising the science.
Collect these early; they take longer to obtain than internal documents, and their absence is a recurring, specific reviewer criticism.

The customer letters in the funded sample set share a shape worth requesting explicitly:
the writer states the gap in their own setting with numbers, reports what they have already done with a prototype,
and commits to a next step with a quantity attached, for example a named number of units for a planned evaluation.
A letter from an organization that would buy or mandate the product, such as a public health body, carries more weight than another letter from a scientific collaborator.

## Attachments that quietly cost points

Small-business summary statements repeatedly mark administrative attachments **Unacceptable**, on applications the same reviewers scored highly on science.
The recurring offenders in the sample set are the Authentication of Key Biological and Chemical Resources attachment, which was missing entirely on several applications, and the Resource Sharing plan.
These are cheap to write and are judged acceptable or unacceptable rather than scored, but the finding sits in the summary statement and follows the application to council.

Check off, against the current NOFO and the SF424 (R&R) SBIR/STTR Application Guide:
Authentication of Key Biological and Chemical Resources; Resource Sharing and Data Management and Sharing plans; Vertebrate Animals and Select Agent sections where applicable;
inclusion plans and sex as a biological variable, stated explicitly even when the model only supports one sex, with the justification written down;
biosketches in the current required format, since a non-compliant biosketch draws a scientific review officer note and NIH may withdraw the application;
and the SBIR/STTR Information Form certifications, including the STTR work-percentage certification.

## STTR-specific requirements

- The partnership with a single United States non-profit research institution is required, in Phase I and Phase II, and the work split is statutory: at least 40% by the small business and at least 30% by the research institution.
- The two parties must have a written agreement allocating intellectual property rights and revenue between them. Funded STTR Commercialization Plans name that agreement explicitly. Negotiate it early; university technology transfer offices are not fast.
- The principal investigator may sit at either organization. In the most recent STTR sample in the set, the principal investigator is a university professor and the applicant is the small business.
- Minimum effort requirements for the STTR principal investigator have changed across reauthorizations. Take the number from the current NOFO, not from a slide deck.

## Program status is unusually volatile right now

The SBIR and STTR programs run on periodic congressional reauthorization, and the authority lapsed on 2025-10-01.
NIH expired all SBIR and STTR NOFOs on 2025-11-17 (NOT-OD-26-006) and stopped issuing noncompeting continuation awards until reauthorization.
The programs were reauthorized in April 2026, and NIH released new parent NOFOs on 2026-05-28:
PA-27-100 for the parent SBIR (R43/R44), PA-27-102 for the parent STTR (R41/R42), PA-27-101 for the SBIR Phase IIB Strategic Breakthrough Award, and PAR-27-098 for the Commercialization Readiness Pilot.
Verified 2026-08-07 and 2026-08-08.

Two practical implications.
Do not reuse a NOFO number from an older document, including an older version of this file.
And when a lapse is in progress, ask program staff what happens to an application already in the queue before building a submission calendar around it.

## Choosing the path: Phase I versus Direct to Phase II

Direct to Phase II is attractive because it skips a funding round, but it is the harder application, and the wrong choice is expensive.

Choose **Direct to Phase II** when all of the following hold:

- Feasibility is genuinely complete and can be shown entirely inside the Research Strategy.
- No SBIR or STTR Phase I award was made for this project. Feasibility work funded from any other source, including internal funds, other federal awards, or partner cost-share, does not disqualify the application.
- The product needs no further feature definition to reach customers beyond the beachhead market.
- Customer discovery is far enough along to support a compelling 12-page Commercialization Plan.

Choose **Phase I** when any of the following hold:

- Further product development will be needed after the proposed work to reach customers beyond the beachhead market. Phase I preserves a Phase II in which to do that, informed by what customers ask for.
- The feature set is still open to customer input.
- Customer discovery is thin. A Phase I application may state an intent to participate in the **I-Corps at NIH** program, which funds extensive customer discovery and business planning, and which then strengthens the Phase II Commercialization Plan.
- The scope runs past what fits a single award cleanly. Define the minimum viable product, build it in Phase I, and expand in Phase II.

Program staff will discuss the choice before submission and are the right people to ask.
Their read on mechanism fit is more reliable than any general rule here.

### Fast-Track

A Fast-Track submits Phase I and Phase II together and is reviewed as one application, closing the funding gap between phases.
It costs more to write than a Phase I and is judged on an extra axis: reviewers rate Fast-Track acceptability separately, and can find the mechanism unacceptable while praising the science.

Two conditions the reviewer guidance and the sample set both point at:

- The Phase I portion must carry clear, measurable milestones to be achieved before Phase II work starts, and the application should state the go/no-go threshold in numbers.
- The Phase I portion is expected to include preliminary data, unlike a standalone Phase I, where preliminary data are not required.

On the first submission of the Fast-Track in the sample set, a reviewer judged the mechanism unacceptable, not for weak milestones, which that reviewer called clear and measurable,
but because the application could not say when private-sector letters of interest, funding commitments, or other non-SBIR resources would appear.
If the honest answer is that a partner will only engage once Phase II data exist, that is an argument for a Phase I followed by a Phase II, and the application should say so rather than assert a commitment it cannot evidence.

### Phase II after a Phase I

A Phase II is evaluated on the results of Phase I as well as on the new plan.
Funded Phase II applications open the Approach with a Phase I results subsection before the Phase II project subsection,
and state on the aims page which Phase I milestones were met, with the numbers.
Reviewers ask directly how well the application demonstrates progress toward meeting the Phase I objectives.

If the Phase I award is still running, say so and state what happens if the remaining objectives are not met.
A reviewer in the sample set raised exactly that: the Phase I was under a no-cost extension and it was unclear whether Phase II would be contingent on completing Phase I objectives.

## Eligibility essentials

- The applicant is a United States small business concern, generally 500 employees or fewer.
- Ownership requirements apply and differ between SBIR and STTR; verify the current rules, which have changed with reauthorizations.
- The PI's primary employment must be with the small business for SBIR. STTR allows the PI to sit at either the business or the research institution.
- Registrations are serial and slow: Employer Identification Number, then System for Award Management (SAM.gov) Unique Entity ID, then eRA Commons. The Small Business Administration Company Registry issues an SBC Control ID and can run in parallel. Budget several weeks; SAM registration for a new entity is the usual long pole.

## How the application is reviewed

Small-business applications are **not** reviewed under the Simplified Review Framework that governs research project grants from January 2025.
R41, R42, R43, and R44 are absent from the activity codes listed in NOT-OD-24-010, and the small-business summary statements continue to show the five classic criteria scored separately:
Significance, Investigator(s), Innovation, Approach, Environment, each 1 to 9, plus an overall impact score.
Do not write a small-business application to the three-factor framework.

Each of those five criteria carries small-business-specific questions about commercial potential, and additional criteria apply by application type:
Phase I milestones, Phase I progress for a Phase II, Fast-Track acceptability, and the Commercialization Plan.
`../../grant-review/references/sbir-sttr-review-criteria.md` in the `grant-review` skill covers the full rubric and the criticism patterns behind it.
Read it before writing, not only before reviewing.

Study sections for these applications are special emphasis panels grouped by technology area rather than by disease,
with names of the form "Small Business: Non-HIV Diagnostics" or "Small Business Applications: Drug Discovery and Development".
That grouping is why a reviewer who knows your field may not be in the room, and why the aims page has to work for a technically strong outsider.

## Sources

Verify each against the live page before filing; figures and policies change between reauthorizations.

- [NIH SEED, Understanding SBIR and STTR](https://seed.nih.gov/small-business-funding/small-business-program-basics/understanding-sbir-sttr) for program comparison, application types, budgets, and timelines
- [NIH SEED Frequently Asked Questions](https://seed.nih.gov/faqs) for page limits including the 12-page Commercialization Plan
- [NIH SEED Institute, Center, and Office funding considerations](https://seed.nih.gov/) for per-Institute budget limits and waiver topics
- [NIH SEED, SBIR and STTR funding opportunities](https://seed.nih.gov/small-business-funding/find-funding/sbir-sttr-funding-opportunities) for the current parent NOFO numbers and due dates
- [NIH SBIR/STTR Information Form instructions](https://grants.nih.gov/grants/how-to-apply-application-guide/forms-i/general/g.440-sbir-sttr-information-form.htm) for the Commercialization Plan headings and the Company Commercialization History
- [NOT-OD-24-010](https://grants.nih.gov/grants/guide/notice-files/NOT-OD-24-010.html) for the activity codes the Simplified Review Framework covers, which exclude R41, R42, R43, and R44
- The SF424 (R&R) SBIR/STTR Application Guide for form-level instructions
- The specific Notice of Funding Opportunity, which overrides all general guidance
- `commercialization-plan-guide.md` in this directory for the 12-page plan
- `niaid-sample-applications.md` in this directory for funded SBIR and STTR applications with their summary statements, and a script that fetches them
