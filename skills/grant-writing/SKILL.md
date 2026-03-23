---
name: grant-writing
description: This skill should be used when the user asks to "write a grant proposal", "draft specific aims", "write a research strategy", "create an NIH proposal", "create an NSF proposal", "write a significance section", "write an innovation section", "write an approach section", "draft a DP2 essay", "write an R01", "write an R21", "write a K99", "format grant text", or mentions grant writing, proposal drafting, specific aims, or research strategy sections.
version: 0.1.0
---

# Grant Writing Skill

Provides procedural knowledge for drafting NIH and NSF grant proposals with mechanism-specific formatting, section structure, and scientific writing best practices.

## When to Use

Activate when the user needs to draft, revise, or format any component of an NIH or NSF grant proposal, including specific aims pages, research strategy sections (significance, innovation, approach), project descriptions, or budget justifications.

## Supported Mechanisms

| Agency | Mechanism | Key Format |
|--------|-----------|------------|
| NIH | R01 | 1p aims + 12p strategy |
| NIH | R21 | 1p aims + 6p strategy |
| NIH | DP2 | 10p essay (no aims page) |
| NIH | K99/R00 | 1p aims + 12p strategy + 6p candidate + 6p mentoring |
| NIH | R24 | 1p aims + 12p strategy (resource-focused) |
| NSF | Standard | 1p summary + 15p project description |
| NSF | CAREER | Integrates research + education |

## Core Workflow

### 1. Identify the mechanism and gather context

Determine the funding mechanism and read the Notice of Funding Opportunity (NOFO). Each mechanism has specific page limits, required sections, and review criteria. Consult `references/nih-requirements.md` or `references/nsf-requirements.md` for mechanism details.

### 2. Draft the Specific Aims page (NIH) or Project Summary (NSF)

**NIH Specific Aims (1 page, <650 words):**

1. **Opening** (2-3 sentences): State the problem and critical gap concisely
2. **Bold overarching goal**: One sentence in bold stating the ultimate objective, followed by innovation/methodology explanation
3. **Brief scope statement**: Recruitment/context (can merge with goal if space is tight)
4. **Aims** (2-3): Each titled in bold with an action verb
   - Sub-hypotheses: *Italic labels* (Hypothesis 1A:), one sentence each
   - After each hypothesis: "We will..." with **bold key methodological innovations**
5. **Expected Impact**: Bold header, numbered list of concrete deliverables

**NSF Project Summary (1 page):**
- Overview paragraph
- Intellectual Merit paragraph
- Broader Impacts paragraph

### 3. Draft the Research Strategy (NIH) or Project Description (NSF)

**NIH Research Strategy (Significance -> Innovation -> Approach):**

- **Significance** (1.5-2p for R01): Problem -> Gap -> Why it matters -> What success enables
- **Innovation** (1-1.5p for R01): What's new -> Why current approaches fail -> Field advancement. Distinguish conceptual, technical, and methodological innovations
- **Approach** (7-9p for R01): Preliminary data -> Aim-by-aim breakdown (Rationale -> Methods -> Hypothesis -> Analyses -> Expected outcomes -> Problems/Alternatives) -> Rigor & Reproducibility -> Timeline

Consult `references/research-strategy-guidelines.md` for detailed section guidance.

**NSF Project Description (15 pages):**
- Results from Prior NSF Support (within the 15 pages)
- Research Plan
- Broader Impacts activities

### 4. Apply writing style

Consult `references/writing-style-guide.md` and `references/tone-guide.md` for the PI's established voice. Key principles:

- Direct, active voice ("We will demonstrate" not "It will be demonstrated")
- Strategic bolding: overarching goal, aim titles, one key innovation per aim, memorable phrases
- *Italic* hypothesis labels
- No em-dashes; use commas, semicolons, or parentheses
- Define abbreviations on first use (once per document)
- Quantify when possible (N=24, 6-month, etc.)
- Bold claims backed by technical precision
- First person for vision ("I propose"), "we" for team work

### 5. Format for submission

**NIH LaTeX formatting:**
- Arial 11pt body, 12pt title
- 0.5in margins all sides
- No indentation; 4pt space between paragraphs
- Justified text
- Fit on page limits by trimming content, not reducing spacing

**NSF formatting:**
- Arial/Helvetica 10pt+, Times 11pt+, or Palatino 10pt+
- 1 inch margins minimum
- Single-spaced

## Special Cases

### DP2 (New Innovator Award)
- NO specific aims page; write a 10-page essay instead
- Emphasize PI creativity and innovation
- Written for broad audience
- Use catchy component names
- Include "What If" contingency section

### Resubmissions
- Address reviewer concerns point-by-point in an Introduction (1 page)
- Bold changes or mark with change bars
- Keep reviews in a `reviews/` directory for reference

## Proposal Directory Structure

When creating a new proposal, follow this structure:
```
proposals/{mechanism}/{year}-{short-name}/
├── README.md
├── NOFO.md (with URL link)
├── ideas.md
├── research.md
├── lit-review/
├── submission/
│   ├── specific-aims.md
│   ├── research-strategy/
│   │   ├── significance.md
│   │   ├── innovation.md
│   │   └── approach.md
│   ├── budget/
│   └── biosketches/
├── drafts/
├── reviews/
└── figures/
```

## Additional Resources

### Reference Files

For detailed guidance, consult:
- **`references/nih-requirements.md`** - NIH mechanisms, page limits, review criteria, deadlines
- **`references/nsf-requirements.md`** - NSF mechanisms, formatting, review criteria
- **`references/research-strategy-guidelines.md`** - Detailed section-by-section writing guide for NIH research strategy
- **`references/writing-style-guide.md`** - Comprehensive scientific writing style guide
- **`references/tone-guide.md`** - PI's established voice characteristics and patterns

### Literature Search

Use the **opencite** skill for literature searches to support proposals:
```bash
uvx opencite search "topic" --max 20 -f bibtex -o refs.bib
uvx opencite canonical "field" --max 10
```
