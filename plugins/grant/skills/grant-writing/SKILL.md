---
name: grant-writing
description: This skill should be used when the user asks to "write a grant proposal", "draft specific aims", "write a research strategy", "create an NIH proposal", "create an NSF proposal", "write a significance section", "write an innovation section", "write an approach section", "draft a DP2 essay", "write an R01", "write an R21", "write a K99", "write an R03", "write a K08", "write a K23", "write an F31", "write an F32", "write a CAREER proposal", "write an SBIR", "write an STTR", "write an R43, R44, R41, or R42", "write a Phase I or Phase II application", "write a Fast-Track application", "write a commercialization plan", "write SBIR milestones", "write preliminary data", "write rigor and reproducibility", "draft potential problems and alternatives", "write a budget justification", "respond to reviewer comments", "write a resubmission introduction", "strengthen my specific aims", or mentions grant writing, proposal drafting, specific aims, research strategy, small business grants, or any NIH/NSF mechanism.
version: 0.2.0
---

# Grant Writing Skill

Provides procedural knowledge for drafting NIH and NSF grant proposals with mechanism-specific formatting, section structure, and scientific writing best practices.

## Supported Mechanisms

| Agency | Mechanism | Key Format |
|--------|-----------|------------|
| NIH | R01 | 1p aims + 12p strategy |
| NIH | R21 | 1p aims + 6p strategy |
| NIH | R03 | 1p aims + 6p strategy (2 years, $50K/year) |
| NIH | DP2 | 10p essay (no aims page) |
| NIH | K99/R00 | 1p aims + 12p strategy + 6p candidate + 6p mentoring |
| NIH | K08/K23 | 1p aims + 12p strategy + candidate section + career goals + mentoring plan |
| NIH | F31/F32 | 1p aims + 6p strategy + applicant background + sponsor info + training plan |
| NIH | R24 | 1p aims + 12p strategy (resource-focused) |
| NIH | R43/R41 (SBIR/STTR Phase I) | 1p milestone-driven aims + 6p strategy; no Commercialization Plan allowed |
| NIH | R44/R42 (SBIR/STTR Phase II, Fast-Track, Direct to Phase II) | 1p milestone-driven aims + 12p strategy + 12p Commercialization Plan |
| NSF | Standard | 1p summary + 15p project description |
| NSF | CAREER | Integrates research + education (see `references/career-award-guide.md`) |

## Core Workflow

### Step 0: Parse the NOFO/FOA

Before writing anything, read the Notice of Funding Opportunity (NOFO) or Funding Opportunity Announcement (FOA) thoroughly. Extract and record:

- **Mechanism and agency:** Determines page limits, required sections, and review criteria
- **Specific objectives:** Many NOFOs list required research areas, populations, or methods
- **Page limits:** Verify per-section limits (they vary by mechanism and can change between cycles)
- **Review criteria and weights:** Identify how the review panel will score the application
- **Special requirements:** Data sharing plans, milestones, letters of support, human subjects provisions
- **Eligible PIs:** Career stage, citizenship, institutional requirements
- **Budget constraints:** Direct cost caps, duration limits, cost-sharing restrictions
- **Submission deadline and receipt date:** Plan backward from the deadline

Store the NOFO URL and key extracted details in `NOFO.md` within the proposal directory. Flag any requirements that deviate from the standard mechanism template.

### Step 1: Plan the page budget

Before drafting, allocate pages across sections. Staying within limits while giving each section adequate space is a critical constraint. Use these as starting points and adjust based on the specific aims and preliminary data available:

**R01 (12 pages total strategy):**
- Significance: ~2 pages
- Innovation: ~1.5 pages
- Approach: ~8.5 pages (including ~1.5-2p preliminary data, ~5-6p aims, ~1p rigor, ~0.5p timeline)

**R21 (6 pages total strategy):**
- Significance: ~1 page
- Innovation: ~0.75 pages
- Approach: ~4.25 pages

**R03 (6 pages total strategy):**
- Significance: ~1 page
- Innovation: ~0.5 pages
- Approach: ~4.5 pages (focus on methods; preliminary data less critical)

**K99/R00 (12 pages strategy + 6p candidate + 6p mentoring):**
- Research strategy follows R01 proportions
- Candidate section: training background, career trajectory, independence plan
- Mentoring plan: structured activities, timeline, evaluation

**F31/F32 (6 pages strategy):**
- Follows R21 proportions for strategy
- Applicant background and goals: training rationale, career objectives
- Sponsor and institutional environment: mentor qualifications, training plan, resources

### Step 2: Draft the Specific Aims page (NIH) or Project Summary (NSF)

**Branch first: is this a small-business application?**

If the mechanism is SBIR or STTR (R41, R42, R43, R44), stop and use `examples/sbir-specific-aims-template.md` instead of the hypothesis-driven template below. Small-business aims are milestone-driven: each aim carries a month window and closes with a quantitative acceptance threshold, with go/no-go conditions where one aim gates the next. Using the hypothesis-driven structure on a small-business application loses points on Approach. See `references/sbir-sttr-requirements.md`.

**NIH Specific Aims (1 page, <650 words):**

1. **Opening** (2-3 sentences): State the problem and critical gap concisely
2. **Bold overarching goal**: One sentence in bold stating the ultimate objective, followed by innovation/methodology explanation
3. **Brief scope statement**: Recruitment/context (can merge with goal if space is tight)
4. **Aims** (2-3): Each titled in bold with an action verb
   - Sub-hypotheses: *Italic labels* (Hypothesis 1A:), one sentence each
   - After each hypothesis: "We will..." with **bold key methodological innovations**
5. **Expected Impact**: Bold header, numbered list of concrete deliverables

See `examples/specific-aims-template.md` for an annotated template.

**NSF Project Summary (1 page):**
- Overview paragraph
- Intellectual Merit paragraph
- Broader Impacts paragraph

### Step 3: Draft the Research Strategy (NIH) or Project Description (NSF)

**NIH Research Strategy (Significance -> Innovation -> Approach):**

- **Significance** (~2p for R01): Problem -> Gap -> Why it matters -> What success enables
- **Innovation** (~1.5p for R01): What is new -> Why current approaches fail -> Field advancement. Distinguish conceptual, technical, and methodological innovations
- **Approach** (~8.5p for R01): Preliminary data -> Aim-by-aim breakdown (Rationale -> Methods -> Hypothesis -> Analyses -> Expected outcomes -> Problems/Alternatives) -> Rigor & Reproducibility -> Timeline

Consult `references/research-strategy-guidelines.md` for detailed section guidance.

**NSF Project Description (15 pages):**
- Results from Prior NSF Support (within the 15 pages)
- Research Plan
- Broader Impacts activities

**NSF CAREER:** Research and education plans must be bidirectionally integrated. See `references/career-award-guide.md`.

### Step 4: Draft supporting sections

After the core strategy is drafted, prepare the remaining required documents:

- **Facilities & Other Resources:** Describe lab space, equipment, computational infrastructure, core facilities, and collaborating sites. Emphasize resources that directly enable the proposed work.
- **Equipment:** List major equipment available for the project. Distinguish from equipment requested in the budget.
- **Data Management & Sharing Plan** (DMS, typically 2 pages): Describe what data will be generated, how it will be stored, standards for formatting, timeline for sharing, and any access restrictions. Follow the 2023 NIH DMS Policy or NSF DMP requirements.
- **Budget Justification:** Justify every budget category. See `references/budget-justification-guide.md` and `examples/budget-justification-template.md`.
- **Letters of Support:** Request from collaborators, consultants, and core facility directors. Each letter should confirm the specific contribution described in the proposal.

For fellowship and career development mechanisms (F31, F32, K08, K23, K99):
- **Candidate/Applicant Section:** Training history, skills acquired, career goals, and how this award fills gaps
- **Mentoring/Training Plan:** Structured mentoring activities, timeline, and evaluation criteria
- **Sponsor Statement:** Mentor's qualifications, commitment, and training record

### Step 5: Apply writing style

Consult `references/writing-style-guide.md` and `references/tone-guide.md` for established voice conventions. Key principles:

- Direct, active voice ("We will demonstrate" not "It will be demonstrated")
- Strategic bolding: overarching goal, aim titles, one key innovation per aim, memorable phrases
- *Italic* hypothesis labels
- No em-dashes (PI style preference, not a universal standard); use commas, semicolons, or parentheses
- Define abbreviations on first use (once per document)
- Quantify when possible (N=24, 6-month, etc.)
- Bold claims backed by technical precision
- First person for vision ("I propose"), "we" for team work

After drafting, run `manuscript:humanizer` as a final natural-writing pass. Pay particular attention to:

- Pattern 1 (significance inflation): strip filler ("pivotal moment", "evolving landscape") but keep evidence-backed importance ("affects 1.2M patients annually").
- Pattern 4 (promotional language): "groundbreaking", "transformative", "paradigm-shifting" read as red flags in Innovation sections. Let the methods carry the claim.
- Pattern 24 (excessive hedging): tighten stacked hedges, but keep appropriate uncertainty in Approach risks/alternatives.
- Patterns 17 and 19 (title case, curly quotes): for NIH/NSF, defer to mechanism formatting in Step 6.

### Step 6: Format for submission

**NIH LaTeX formatting:**
- Arial 11pt body, 12pt title. Note: Arial is not available in standard LaTeX distributions; use the `helvet` package for Helvetica, which is an accepted substitute.
- 0.5in margins all sides
- No indentation; 4pt space between paragraphs
- Justified text
- Fit within page limits by trimming content, not reducing spacing

**NSF formatting:**
- Arial/Helvetica 10pt+, Times New Roman 11pt+, or Palatino 10pt+
- 1 inch margins minimum
- Single-spaced

### Step 7: Pre-submission checklist

Before submitting, verify every item:

**Content completeness:**
- [ ] All required sections present per the NOFO
- [ ] Page limits respected for every section
- [ ] All aims referenced in both the Specific Aims page and the Approach
- [ ] Rigor and reproducibility addressed (biological variables, authentication, blinding)
- [ ] Timeline with milestones included
- [ ] All abbreviations defined on first use
- [ ] All figures referenced in text and legible at printed size
- [ ] Citations complete and formatted per agency requirements

**Budget and administrative:**
- [ ] Budget matches the narrative (effort levels, equipment, travel consistent with text)
- [ ] Budget justification covers every line item
- [ ] Biosketches current and formatted correctly (SciENcv for NIH)
- [ ] Letters of support included for all named collaborators and consultants
- [ ] Data Management and Sharing Plan included
- [ ] Facilities and Equipment documents included
- [ ] Human subjects or vertebrate animals sections complete (if applicable)

**Formatting:**
- [ ] Font, margins, and spacing meet agency requirements
- [ ] No text extends beyond page limits
- [ ] PDF renders correctly (no font substitution, no clipped figures)
- [ ] File naming follows agency conventions

**For resubmissions (A1):**
- [ ] Introduction page present and within 1-page limit
- [ ] All reviewer critiques addressed
- [ ] Changes marked in the body of the application
- [ ] See `references/resubmission-guide.md` for detailed guidance

## Special Cases

### DP2 (New Innovator Award)
- NO specific aims page; write a 10-page essay instead
- Emphasize PI creativity and innovation
- Written for broad audience
- Use catchy component names
- Include "What If" contingency section

### Fellowship Mechanisms (F31/F32)
- Applicant background and goals section replaces the standard biosketch narrative
- Sponsor and co-sponsor statements are critical; coordinate closely with mentors
- Training plan must describe specific skills to be acquired
- Institutional environment section should demonstrate access to resources and training opportunities
- See `references/nih-requirements.md` for page limits and section details

### Career Development (K08/K23)
- Candidate section describes prior training and career goals
- Career development plan outlines specific training activities and timeline
- Mentoring plan must name mentors and describe their expertise and roles
- Research plan follows standard structure but is evaluated in the context of career development
- See `references/nih-requirements.md` for details

### SBIR/STTR (R41, R42, R43, R44)
- Milestone-driven aims, not hypotheses: use `examples/sbir-specific-aims-template.md`
- Reviewed on the five classic criteria (Significance, Investigator(s), Innovation, Approach, Environment), **not** the RPG Simplified Review Framework
- Commercial potential is scored inside those criteria, in every phase, including Phase I
- Write for a panel where only some reviewers know the field; all of them score
- Restate every result that matters inside the Research Strategy; referenced manuscripts and preprints score nothing
- Phase II, Direct to Phase II, Phase IIB, Fast-Track, and the Commercialization Readiness Pilot require a 12-page Commercialization Plan; a standalone Phase I cannot include one
- Collect letters of interest from potential customers early, not only from academic collaborators
- Phase I runs up to 2 years, so a 24 to 30 month scope is often Phase I plus Phase II rather than a Direct to Phase II
- A Phase I may state an intent to join I-Corps at NIH for customer discovery, which strengthens a later Commercialization Plan
- See `references/sbir-sttr-requirements.md`, `references/commercialization-plan-guide.md`, and `references/niaid-sample-applications.md`

### Resubmissions
- Address reviewer concerns point-by-point in an Introduction (1 page)
- Bold changes or mark with change bars
- Keep reviews in a `reviews/` directory for reference
- See `references/resubmission-guide.md` for detailed strategy

## Proposal Directory Structure

When creating a new proposal, follow this structure:

```
proposals/{mechanism}/{year}-{short-name}/
├── README.md            # Proposal overview: title, mechanism, PI, deadline, status
├── NOFO.md              # Extracted NOFO requirements with URL link to the original
├── ideas.md             # Early brainstorming, concept development, design decisions
├── research.md          # Background research notes, key references, field context
├── lit-review/          # Literature review materials: search results, annotated bibliographies
├── submission/          # Final submission-ready documents
│   ├── specific-aims.md
│   ├── research-strategy/
│   │   ├── significance.md
│   │   ├── innovation.md
│   │   └── approach.md
│   ├── budget/          # Budget spreadsheets, justification narrative, subaward budgets
│   └── biosketches/     # PI and co-investigator biosketches (SciENcv exports)
├── drafts/              # Working drafts and intermediate versions (not submission-ready)
├── reviews/             # Summary statements, reviewer comments, resubmission notes
└── figures/             # All figures: conceptual diagrams, preliminary data, methods workflows
```

## Additional Resources

### Reference Files

For detailed guidance, consult:
- **`references/nih-requirements.md`** - NIH mechanisms, page limits, review criteria, deadlines
- **`references/nsf-requirements.md`** - NSF mechanisms, formatting, review criteria
- **`references/research-strategy-guidelines.md`** - Detailed section-by-section writing guide for NIH research strategy
- **`references/writing-style-guide.md`** - Comprehensive scientific writing style guide
- **`references/tone-guide.md`** - Narrative tone patterns and voice conventions
- **`references/budget-justification-guide.md`** - Budget categories, modular vs detailed, common pitfalls
- **`references/career-award-guide.md`** - NSF CAREER award requirements and integration guidance
- **`references/resubmission-guide.md`** - Resubmission strategy, Introduction page format, change marking
- **`references/sbir-sttr-requirements.md`** - SBIR/STTR program structure, budgets, phase choice, Fast-Track, eligibility, and how small-business review differs
- **`references/commercialization-plan-guide.md`** - The 12-page Commercialization Plan, section by section, with the criticisms weak plans draw
- **`references/niaid-sample-applications.md`** - Curated index of the NIAID funded sample applications and summary statements, with what to study in each

### Example Templates

- **`examples/specific-aims-template.md`** - Annotated specific aims page with placeholders (hypothesis-driven; **not** for SBIR/STTR)
- **`examples/sbir-specific-aims-template.md`** - Milestone-driven specific aims for SBIR/STTR, with a contrast table against the generic template
- **`examples/budget-justification-template.md`** - Modular and detailed budget formats

### Scripts

- **`scripts/fetch-niaid-samples.sh`** - Downloads the NIAID small-business sample applications and summary statements, optionally converting them to markdown. The samples are copyrighted and licensed for nonprofit educational use only, so they are fetched on demand rather than bundled. Manifest: `scripts/niaid-samples.txt`.

### Literature Search

Use the **opencite** skill for literature searches to support proposals:
```bash
uvx opencite search "topic" --max 20 -f bibtex -o refs.bib
uvx opencite canonical "field" --max 10
```
