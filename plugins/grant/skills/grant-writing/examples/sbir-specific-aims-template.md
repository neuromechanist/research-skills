# SBIR/STTR Specific Aims Template (milestone-driven)

> Annotated template for the Specific Aims page of a Small Business Innovation Research (SBIR) or Small Business Technology Transfer (STTR) application.
> Replace all `[PLACEHOLDER]` text. Commentary in `<!-- -->` blocks explains what each block is doing; remove commentary before submission.
> Do **not** use `examples/specific-aims-template.md` for a small-business application. See the contrast table at the end of this file.

## Why this template is shaped differently

A research grant proposes to find something out.
A small-business award buys a defined piece of product development, and the panel scores whether you will deliver it.
So the aims page answers a different question:
not "what will you learn," but "what will exist at the end, and how will everyone know whether you built it."

Three structural consequences, all visible in the funded samples indexed in `references/niaid-sample-applications.md`:

1. **Every aim ends in a number.** The funded Phase I aims pages close each aim with a milestone sentence carrying a quantitative acceptance threshold, not a hypothesis.
2. **Aims carry a schedule.** Funded aims headings state a month range, so a reviewer can see the plan fits the period without turning to the timeline.
3. **The page ends in a product, not a contribution.** The closing block names what reaches customers and what the next phase does, not what the field will understand better.

---

<!-- LABELED OPENING BLOCKS. Funded small-business aims pages run short labeled blocks rather than
     unlabeled paragraphs, so a non-specialist reviewer can find each part. Label the blocks in bold.
     Typical sequence: problem, innovation, feasibility, approach. Keep the whole page to one page. -->

**[Problem / Background and Significance].**
[One or two sentences on the problem, in language a technically strong non-specialist can follow. Quantify the burden: how many people, how much cost, how much time lost.]
[One or two sentences on why current products or methods fail. Name the incumbent approach and its specific limitation, not a general complaint.]
[One sentence stating the consequence of the gap for the customer who feels it.]

<!-- Not all reviewers on a small-business panel work in your field, and all of them score.
     Write the problem, the product, and the milestone in plain language first, and put domain detail after it.
     If a term must appear, define it on first use. -->

**Innovation.**
[What the company has that others do not: the mechanism, the platform, the algorithm, the manufacturing route.]
[One sentence on why this specific innovation dissolves the limitation named above.]

<!-- Innovation here means a defensible technical advantage that a competitor cannot copy quickly,
     not novelty for its own sake. A small-business panel reads it commercially. -->

**Preliminary feasibility.**
[The strongest evidence you already hold, stated with the numbers: sample size, comparison, effect size.]
[One sentence positioning the company as the party that can execute: prior products shipped, prior awards delivered, relevant regulatory clearances.]

<!-- Restate results here. A reviewer scores only what is inside the application.
     A manuscript in press, a preprint referenced by digital object identifier (DOI), or data "available on request"
     contributes nothing to the score unless the result, its sample, and its comparison appear in the application text.
     Phase I does not require preliminary data, but a Fast-Track Phase I portion is expected to include it. -->

**Approach.**
[One sentence naming the product to be built and the path through the aims. End with a colon leading into the aims.]

<!-- AIM 1. Title in bold with a build verb, then the month window. Two to four sentences of method.
     Close with a bold Milestone sentence stating a numeric threshold. Add a go/no-go condition where the
     next aim depends on this one. Keep aims parallel where you can: reviewers criticize aim chains where
     a single failure collapses the rest, and they criticize sub-aim ordering that forces earlier work to be redone. -->

**Aim 1: [Build / Develop / Optimize] [the specific component].** **Months [0 to 6].**
[What will be built and how, in two to four sentences. Name the method, the materials, and the comparator.]
**Milestone:** [Quantity] reaches [threshold with units] on [defined test set or condition], measured by [method], against [named baseline or current standard].

<!-- AIM 2. Same shape. This is where a go/no-go usually sits, because Aim 3 typically depends on Aim 2's output. -->

**Aim 2: [Validate / Extend / Reduce] [the next component].** **Months [6 to 12].**
[Method, in two to four sentences. State the independent data or samples used, and who supplies them.]
**Milestone:** [Quantity] at or above [threshold] on [N] independent [samples / sites / corpora], with [secondary criterion, for example maximum variation across conditions].
**Go/no-go:** [Condition that must hold to proceed, for example: at least two of three test sets clear the threshold]. If not met, [the named alternative: reformulate, narrow the indication, revert to the fallback design].

<!-- AIM 3. In funded Phase II applications the last aim is often regulatory, manufacturing, or customer-facing
     rather than experimental: a submission, a clearance pathway, a pilot deployment, a design transfer to manufacturing.
     In Phase I it is usually the validation aim that establishes feasibility. -->

**Aim 3: [Validate in the intended setting / Prepare the regulatory package / Transfer to manufacturing].** **Months [12 to 18].**
[Method and setting. Name the partner sites, the sample panels, or the regulatory route.]
**Milestone:** [Prototype or package] meeting [full specification: list two or three numeric criteria], demonstrated on [N] [real-world samples / users / runs].

<!-- CLOSING BLOCK. Not "Expected Impact." Name the deliverable, who buys or uses it, and what the next phase does.
     Funded Phase I pages name the Phase II scope here and the regulatory or market endpoint the product heads toward. -->

**Deliverable and next phase.**
At the end of [Phase I / Phase II], [Company] will hold [the concrete artifact: a validated prototype, a locked design, a cleared submission].
[Who uses it and what changes for them, in one sentence.]
[Phase II / Phase III] will [the next block of work: multi-site validation, regulatory submission, manufacturing scale-up, commercial launch], funded by [the named route: Phase II application, strategic partner, private financing].

---

## Contrast with the generic template

`examples/specific-aims-template.md` is built for a hypothesis-driven research grant.
Using it for a small-business application costs points on Approach and Significance.
The differences are not cosmetic.

| Element | Generic research template | This SBIR/STTR template |
|---|---|---|
| Aim's closing line | *Hypothesis 1A:* an italic testable prediction | **Milestone:** a numeric acceptance threshold, plus a go/no-go where an aim gates the next |
| Verbs | determine, investigate, characterize, explore, elucidate | build, develop, validate, reduce to, reach, demonstrate, transfer, clear |
| Success | knowledge gained; a hypothesis supported or refuted | a threshold met or missed, decidable by a reviewer without a judgment call |
| Timing | absent from the aims; lives in the timeline | month window in each aim heading |
| Audience | reviewers who work in your subfield | a panel where only some reviewers know the field, and all of them score |
| Preliminary data | may lean on published or in-press work | restated in full inside the application, because only the application is scored |
| Team and credentials | investigator strength often signaled on the page | belongs in the biosketch and Facilities; the aims page spends its space on milestones |
| Closing block | **Expected Impact**, numbered scientific contributions | **Deliverable and next phase**, the artifact plus who uses it and what funds the next step |
| Aim independence | aims should not depend on each other | same rule, and reviewers additionally criticize sub-aim ordering that would force earlier work to be repeated |
| Risk handling | Potential Problems and Alternatives in the Approach | alternative named in the go/no-go itself, so the decision rule is visible on the aims page |

## Milestone quality checklist

A milestone is doing its job when a reviewer who has never met you can decide, from the milestone alone, whether the aim succeeded.

- [ ] States a **quantity**, a **threshold**, and **units**.
- [ ] Names the **test set, panel, or condition** the threshold is measured on, including how many.
- [ ] Names the **comparator**: current standard of care, incumbent product, published baseline, or a floor registered before the data are opened.
- [ ] Uses a **measurement method** a reviewer can picture.
- [ ] Is **achievable inside the stated month window** with the requested budget.
- [ ] For any aim that gates another, carries a **go/no-go condition** and the action taken if the condition fails.
- [ ] Would be **falsifiable at the end of the award**: no milestone whose achievement is a matter of opinion ("demonstrate promise", "establish a foundation", "show utility").

## Fast-Track and Phase II variants

**Fast-Track.**
Label each aim with the segment it belongs to, for example `Phase 1 Segment: Aim 1` and `Phase 2 Segment: Aim 2`.
The Phase I segment must carry clear, measurable milestones that are achieved before Phase II work begins,
and the application should state the go/no-go threshold that gates the transition in plain numbers.
Reviewers score Fast-Track acceptability separately from the science, and they have judged Fast-Track unacceptable on an application whose milestones were fine
but whose route to private-sector letters of interest, funding commitments, or resources was unclear.

**Phase II.**
Open with what Phase I delivered, milestone by milestone, before proposing anything new.
State the Phase I result with its numbers on the aims page, not only in the Approach.
Expect the last aim to be regulatory, manufacturing, or market-facing rather than experimental.
The Commercialization Plan carries the business case, so the aims page can stay on the technical deliverable.

**Direct to Phase II.**
Same shape as Phase II, except the feasibility evidence that a Phase I would have produced must be shown inside the Research Strategy.
See `references/sbir-sttr-requirements.md` for whether that path is the right choice.

## Formatting notes

- Target: 1 page. Milestone sentences eat space, so the prose blocks run shorter than a research-grant aims page.
- Font, margins, and spacing follow the standard NIH rules in the `grant-writing` skill's Step 6, unless the Notice of Funding Opportunity (NOFO) says otherwise.
- Bold the aim titles, the month windows, and the words `Milestone:` and `Go/no-go:`. Reviewers skim for them.
- Define every abbreviation on first use, once. A panel with non-specialists will not decode a field's shorthand.
- Fit content by cutting background prose, not by cutting milestones.
