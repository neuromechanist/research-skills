# NIAID Sample Applications

NIAID publishes funded applications and their summary statements, contributed by the awardees.
The small-business set below covers Small Business Innovation Research (SBIR) and Small Business Technology Transfer (STTR) awards.
For small-business writing they are the single best study material available,
because the summary statements record what a small-business study section actually praised and criticized.

Index page: [NIAID Sample Applications](https://www.niaid.nih.gov/grants-contracts/sample-applications).
Every file below lives at `https://www.niaid.nih.gov/sites/default/files/<filename>.pdf`.

## Copyright and attribution, read first

The text of these applications is copyrighted.
Awardees gave NIAID express permission to post them for educational purposes.
You may use the material for **nonprofit educational purposes only**, provided the material **remains unchanged**
and the **principal investigators, awardee organizations, and NIH NIAID are credited**.

Three consequences for how this plugin treats them:

- The samples are **referenced, never vendored**.
  This repository is public and BSD-3-licensed;
  redistributing copyrighted material licensed for unchanged nonprofit educational use is incompatible with that.
  Fetch your own copies.
- Nothing in this plugin quotes or paraphrases sample text.
  What is recorded here is **structure and pattern**, described in original words.
- If you reuse anything from a sample in your own teaching material, credit the principal investigator, the awardee organization, and NIH NIAID, and do not alter the material.

## Fetching your own copies

`scripts/fetch-niaid-samples.sh` downloads the 18 small-business files listed in `scripts/niaid-samples.txt`
and optionally converts each to markdown.

```bash
# from the grant-writing skill directory
./scripts/fetch-niaid-samples.sh --list             # show manifest, download nothing
./scripts/fetch-niaid-samples.sh                    # all PDFs into ./niaid-samples/pdf
./scripts/fetch-niaid-samples.sh -m MacLeod Brooks  # two PIs, PDFs plus markdown
./scripts/fetch-niaid-samples.sh -o ~/samples -m    # custom output directory
```

Two things the script handles that a naive `curl` does not:

- `niaid.nih.gov` returns HTTP 403 to a default `curl` user agent,
  so the script sends a browser user agent and a `Referer` header pointing at the index page.
- `opencite convert` defaults to the Mistral converter and fails without `MISTRAL_API_KEY`,
  so the script passes `--converter markitdown` explicitly.

The default output directory `niaid-samples/` is in this repository's `.gitignore`.
If you point `-o` somewhere else, ignore that path yourself.
Downloaded samples must not be committed to a public repository.

**Fetch early.**
The index page currently carries a banner stating that,
due to HHS and NIH restructuring, some content on `niaid.nih.gov` is not being updated regularly.
These URLs carry real link-rot risk.
Pull your own copy at the start of a writing project rather than assuming the links resolve on the day you submit.

## Small-business samples (R41, R42, R43, R44)

Thirteen small-business projects are posted, as 18 files: 12 full applications and 6 summary statements.
Six projects have both documents, six have the application only, and the Smith STTR has the summary statement only.
Forms versions run from Forms-B1 through Forms-F, so older samples show retired forms and page rules;
study their argument structure, never their form layout.

Impact scores are reported only when the posted summary statement shows one.
NIAID redacts scores and dollar figures from most of these documents.

| PI | Organization | Mechanism | Forms | Files |
|---|---|---|---|---|
| Ronald Harty | Fox Chase Chemical Diversity Center (PI at University of Pennsylvania) | STTR Phase II, R42 | F | [application](https://www.niaid.nih.gov/sites/default/files/harty-application.pdf), [summary](https://www.niaid.nih.gov/sites/default/files/harty-summary-statement.pdf) |
| Iain James MacLeod | Aldatu Biosciences | SBIR Phase I, R43 | E | [application](https://www.niaid.nih.gov/sites/default/files/R43-Application_MacLeod-1R43AI145704-01.pdf), [summary](https://www.niaid.nih.gov/sites/default/files/R43-Summary-Statement_%20MacLeod-1R43AI145704-01.pdf) |
| Benjamin Delbert Brooks | Wasatch Microfluidics | SBIR Phase I, R43 | D | [application](https://www.niaid.nih.gov/sites/default/files/R43-Brooks-Application.pdf), [summary](https://www.niaid.nih.gov/sites/default/files/R43-Brooks-Summary-Statement.pdf) |
| Yingru Liu | TherapyX | SBIR Phase II, R44 | D | [application](https://www.niaid.nih.gov/sites/default/files/R44-Liu-Application.pdf), [summary](https://www.niaid.nih.gov/sites/default/files/R44-Liu-Summary-Statement.pdf) |
| James Smith | Sano Chemicals | STTR Phase I, R41 | D | [summary only](https://www.niaid.nih.gov/sites/default/files/R41-Smith-Summary-Statement.pdf) |
| David H. Wagner | Op-T-Mune | STTR Phase I, R41 | D | [application](https://www.niaid.nih.gov/sites/default/files/r41-wagner-application.pdf), [summary](https://www.niaid.nih.gov/sites/default/files/R41-Wagner-Summary-Statement.pdf) |
| Timothy C. Fong | Cellerant Therapeutics | STTR Phase I, R41 | B2 | [application](https://www.niaid.nih.gov/sites/default/files/1r41ai10801601_fong_0.pdf) |
| Jose M. Galarza | Technovax | SBIR Phase I, R43 | B2 | [application](https://www.niaid.nih.gov/sites/default/files/1r43ai106145-01a1_galarza.pdf) |
| Michael J. Lochhead | MBio Diagnostics | SBIR Phase II, R44 | B2 | [application](https://www.niaid.nih.gov/sites/default/files/2r44ai093289-02a1_lochhead_0.pdf) |
| Kenneth Coleman | Arietis Corporation | SBIR Fast-Track, R44 | B1 | [application](https://www.niaid.nih.gov/sites/default/files/1r44ai112187-01a1_coleman.pdf) |
| Patricia Garrett | Immunetics | SBIR Phase II, R44 | B1 | [application](https://www.niaid.nih.gov/sites/default/files/2r44ai098567-03_garrett.pdf) |
| Raymond Houghton and David AuCoin | InBios International with University of Nevada School of Medicine | STTR Phase II, R42 | B1 | [application](https://www.niaid.nih.gov/sites/default/files/2r42ai102482-03-houghton.pdf) |
| Mark Poritz (later Andrew Hemmert) | BioFire Diagnostics | SBIR Phase I, R43 | B1 | [application](https://www.niaid.nih.gov/sites/default/files/r43-sample-application-andrew-hemmert.pdf) |

### What to study in each

**MacLeod, Aldatu Biosciences, R43, Forms-E. Impact score 10, the best score in this set.**
Study the Specific Aims page above everything else.
It runs labeled blocks in sequence: background and significance, innovation, preliminary feasibility, approach, three aims, long-term goal.
Each aim heading carries a month range, and each aim closes with a bold `Milestone:` sentence naming a numeric acceptance threshold
(a limit of detection, a maximum cross-lineage sensitivity deviation, a minimum clinical sensitivity).
The three summary statement critiques recorded no weaknesses at all in Significance, Investigators, or Innovation, and only minor ones in Approach.
This is the model for the milestone-driven aims template in `examples/sbir-specific-aims-template.md`.

**Poritz and Hemmert, BioFire Diagnostics, R43, Forms-B1.**
The cleanest example of a Phase I whose aims run in parallel rather than in series:
two of the three aims share a 0 to 18 month window and only the clinical evaluation waits for the others.
Aims are labeled `SA1`, `SA2`, `SA3`; each closes with `Milestones:`, numbered when an aim carries more than one.
The closing paragraph names the Phase II scope and the regulatory endpoint the product is heading toward.
Study it for how a milestone can be phrased as a comparison against current practice rather than an absolute number.

**Brooks, Wasatch Microfluidics, R43, Forms-D.**
A two-aim Phase I from a three-institution team.
Read the application for the aims, then read the summary statement for two criticisms that cost it points despite exceptional enthusiasm:
the accuracy metrics were not defined precisely enough and no baseline method was named for comparison,
and the budget exceeded the mandatory cap without the required justification.
One reviewer also flagged that a Phase II plan was described even though Phase I does not require one, and treated it as a strength.

**Wagner, Op-T-Mune, R41, Forms-D.**
Study this one as a contrast case.
The science reviewed extremely well; the aims page uses a `Goals for Phase I` and `Goals for Phase II` structure with numbered goals rather than milestones with thresholds.
The third reviewer's overall impact paragraph lists three business weaknesses in a row:
no business leadership on the team, no plan for turning the STTR into a viable business, and no letters of interest from industry stakeholders.
That paragraph is the most direct evidence in this set that a small-business panel scores commercial readiness even in Phase I, where no Commercialization Plan is allowed.

**Smith, Sano Chemicals, R41, Forms-D. Summary statement only.**
Read it for how commercial risk enters the science critiques.
Reviewers raised manufacturing purity and scale-up as a threat to commercial development inside the Significance and Approach critiques,
noted that the company would need to add preclinical and clinical development staff before Phase II,
and flagged possible scientific overlap with another active STTR award.

**Liu, TherapyX, R44, Forms-D.**
The reference Phase II application in this set.
Its Research Strategy opens the Approach with a Phase I results subsection before the Phase II project subsection,
and its aims page states which Phase I milestones were met before proposing new ones.
The final aim is regulatory rather than experimental: request a meeting with the Food and Drug Administration (FDA) and prepare the briefing package.
The Commercialization Plan is sectioned as disease overview, market analysis, company overview, intellectual property protection, commercialization strategy, and key operations analysis.
The summary statement praises the plan explicitly, and separately marks the missing Authentication of Key Biological and Chemical Resources attachment and missing Resource Sharing plan as unacceptable.

**Garrett, Immunetics, R44, Forms-B1.**
The strongest example of quantitative acceptance criteria carried down to the sub-aim.
Sub-aims are lettered, and most of them end in a number that decides success:
a maximum false-recency rate, a minimum correlation with the comparator assay, a minimum agreement between specimen types.
The Phase I outcome is summarized on the aims page with the actual sample count and correlation achieved.
The last aim covers regulatory submissions and market entry, not experiments.

**Lochhead, MBio Diagnostics, R44, Forms-B2.**
The Commercialization Plan to read first, because it follows the standard NIH section outline exactly:
value of the project with expected outcomes and impact; company, with leadership, funding history, business strategy, regulatory strategy, and reimbursement strategy;
market, customer, and competition; intellectual property protection; finance plan; production and marketing plan.
The competition subsection is a table of named competitor products with one stated advantage per competitor.
See `commercialization-plan-guide.md`.

**Harty, Fox Chase Chemical Diversity Center, R42, Forms-F.**
The most recent forms version in the set, and the best Phase II Commercialization Plan.
It carries a target product profile table with preferred and minimally acceptable columns,
a dated development timeline that names each regulatory step with its expected quarter, participant count, and cost,
and three explicitly named alternative commercialization models rather than a single assumed exit.
The finance plan states the prior award history and the intellectual property management agreement between the small business and the university,
which is the STTR-specific document a reviewer will look for.
The summary statement calls out the screening cascade, target product profile, and go/no-go decisions as reasons for confidence,
and flags one Phase II-specific risk: the Phase I award was still under a no-cost extension, so it was unclear whether Phase I objectives would be met before Phase II began.

**Coleman, Arietis Corporation, R44 Fast-Track, Forms-B1.**
The only Fast-Track sample, and it is a resubmission, so it teaches two things at once.
The aims page labels aims by segment: `Phase 1 Segment` for the feasibility aim, `Phase 2 Segment` for the development aims,
with a milestone sentence on each and a numeric go/no-go threshold that gates entry into Phase II.
The resubmission Introduction reproduces parts of the prior summary statement, including a reviewer who judged the Phase I milestones clear and measurable
but still found the Fast-Track itself unacceptable because the application could not say when private-sector letters of interest,
funding commitments, or resources would materialize.
Read that exchange before deciding to submit a Fast-Track.

**Houghton and AuCoin, InBios International with the University of Nevada, R42, Forms-B1.**
Read the Letters of Support section.
These are end-user letters, not collaborator courtesies:
laboratories that had already tested prototypes, requested specific quantities of the device for a planned evaluation, and described the diagnostic gap in their own setting,
plus a letter from a global health organization stating interest in the product.
This is the concrete form of the reviewer expectation that customers, not only academics, speak for the product.

**Fong, Cellerant Therapeutics, R41, Forms-B2** and **Galarza, Technovax, R43, Forms-B2.**
Older Phase I applications useful for range.
Galarza is a good counterexample on milestones:
the aims describe what will be assessed but do not put an acceptance threshold in the aim itself,
deferring the numbers to an activities and milestones chart in the timeline section.
Compare it with MacLeod to see how much a threshold in the aim buys.

## Other NIAID samples, for completeness

These are not small-business samples.
They are useful for the rest of the `grant-writing` skill and for the `grant-review` skill.
All are on the same index page with both application and summary statement unless noted.

| Mechanism | Samples posted (PI, forms version) |
|---|---|
| R01 | George Liu (H), Emily Troemel (G), Vernita Gordon (D), Monica Gandhi (D), Tom Muir (D), William Faubion (C), Chengwen Li and Richard Samulski (C), Mengxi Jiang (C) |
| R03 | Martin Karplus (B2, application only), Chad Rappleye (B2) |
| R15 | Artem Domashevskiy (D), Rahul Raghavan (D) |
| R21 | Steven Dow (B), Joseph McCune (B), Peter Myler and Marilyn Parsons (B), Howard Petrie (B), Michael Starnbach (B) |
| R21/R33 | Stephen Dewhurst (B), a two-phase award whose transition depends on negotiated milestones |
| K01 | Jennifer Ross (E), Lilliam Ambroggio (D), Peter Rebeiro (D) |
| K08 | David Al-Adra (F), Annukka Antar (E), Lenette Lu (D), Tuan Manh Tran (D) |
| K23 | DeAnna Friedman-Klabanoff (F, summary statement only) |
| F31 | Nicole Putnam, Nico Contreras, Samantha Schwartz |
| G11 | Oye Nana Akuffo (E), Andres Jaramillo Zuluaga (E), Stella Kakeeto (E) |
| U01 | Aaron Meyer and Falk Nimmerjahn (E) |

The R21/R33 is worth a look even for a small-business writer:
it is the closest research-grant analogue to a Fast-Track, in that a negotiated milestone gates the transition between phases.

The index page also links sample model organism sharing plans, a sample letter documenting human subjects training, and a withdrawal request letter.

## Reading order

If you are writing your first small-business application, read in this order:

1. MacLeod summary statement, then MacLeod application. See what an exceptional Phase I looks like from both sides.
2. Wagner summary statement. See what a strong science package loses on business readiness.
3. Your own phase's reference sample: Poritz and Hemmert or Brooks for Phase I, Liu or Garrett for Phase II, Coleman for Fast-Track.
4. Lochhead and Harty Commercialization Plans, if you are writing one.
5. Houghton letters of support, before you start asking for letters.
