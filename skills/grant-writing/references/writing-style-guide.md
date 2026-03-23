# Scientific Writing Style Guide

## Core Principles

1. **Direct, active voice** - "We will demonstrate" not "It will be demonstrated"
2. **Professional objectivity over validation** - Technical accuracy and truthfulness over confirming beliefs
3. **Strategic bolding** - Bold key statements reviewers should remember; not liberal use
4. **No em-dashes** - Use commas, semicolons, or parentheses instead
5. **Define abbreviations on first use** - Full term before acronym, once per document

## Grant Proposal Structure

### Specific Aims Page (1 page, <650 words)
- **Opening paragraph** (2-3 sentences): Problem + critical gap
- **Bold overarching goal**: Ultimate objective + innovation/methodology explanation
- **Brief scope statement**: Recruitment/context (can merge with goal if space tight)
- **Aims**: Bold title with action verb
  - Sub-hypotheses: *Italic labels* (Hypothesis 1A:), very concise (one sentence)
  - Hypothesis can continue inline with explanation if space tight
  - After each hypothesis: "We will..." with **bold key methodological innovations**
- **Expected Impact**: Bold header, numbered deliverables

### Specific Aims Formatting (LaTeX)
- No indentation; 4pt space between paragraphs
- Arial 11pt body, 12pt title
- 0.5in margins all sides
- Justified text
- Fit on 1 page by trimming content, not reducing spacing below readability

### Research Strategy Sections

**Significance:**
- Problem -> Gap -> Why it matters -> What success enables
- Bold for key problem statements and barriers
- Use section headers (##) to guide reviewers
- Quantify when possible (N=X, Y datasets, Z dollars invested)

**Innovation:**
- What's new -> Why current approaches fail -> How this advances the field
- Distinguish conceptual, technical, and methodological innovations
- Avoid overstating; let innovations speak for themselves

**Approach:**
- Preliminary data first (establishes credibility)
- Aim-by-aim breakdown:
  - Rationale (why this aim matters)
  - Approach (detailed methods)
  - Hypothesis -> Analyses -> Expected outcomes
  - Potential problems/alternatives (in tables when possible)
- **Tables for potential problems**: Problem | Detection | Alternative
- Rigor section: cross-validation, null models, minimum effect sizes, failure criteria
- Timeline: realistic, with milestones

## Style Elements

### Bold Usage
**Bold these:**
- Overarching goal statement
- Aim titles
- One key innovation per aim
- Key memorable phrases ("The critical barrier is annotation poverty")
- Expected impact header
- Tool/method names on first mention
- Key findings in preliminary data

**Do not bold:**
- Entire sentences
- Common terms
- Everything (if everything is bold, nothing is)

### Hypothesis Format
- *Italic label*: Hypothesis 1A:
- **Concise statement** (one sentence if possible)
- Follow immediately with methodology if space is tight

### Evidence and Citations
- Weave credentials naturally into narrative (not a separate qualifications section)
- Mention relevant leadership roles, first-author papers, standards work where they demonstrate capability
- Reference by number after periods: "This is a statement.1"

### Figures
- Integrate throughout text, not clustered at end
- Caption format: **Figure X.** Description
- Reference in text as "Figure X shows..." or "(Figure X)"

## Common Patterns

### Introducing a dataset
"The **Natural Scenes Dataset (NSD; Allen 2022)** provides 8 subjects with ultra-high-field 7T fMRI recordings..."
- Bold name on first mention
- Include citation
- Key specs immediately

### Describing a gap
"**The critical barrier is X:** description of the barrier and consequences."
- Bold the problem statement
- Colon to transition to explanation

### Presenting team expertise
"**Our multi-site collaboration unites the expertise needed:** PI1 (role, institution) brings X; PI2 (role, institution) contributes Y..."
- Bold the team framing
- Parallel structure for each member
- Active verbs (brings, contributes, provides)

### Stating aims
"**Aim 1: Verb phrase describing the aim.**"
- Bold with action-oriented title
- Number aims sequentially
- Keep title under 10 words

## Technical Writing

### Abbreviations
- Brain Imaging Data Structure (BIDS) -> then "BIDS"
- Hierarchical Event Descriptors (HED) -> then "HED"
- Only define once per document

### Numbers
- Sample sizes: N=24 or N~3,000 (use ~ for approximate)
- Ranges: ages 5-21 (not 5-21 with en-dash in markdown)
- Statistics: p < 0.05, R^2 > 0.3

### Cross-references
- Section references: "as described in Aim 1"
- Figure references: "(Figure 2)" or "Figure 2 shows"

## Things to Avoid

- Em-dashes (use commas, semicolons, parentheses)
- Time estimates ("this will take 3 weeks")
- Liberal bolding (strategic only)
- Validation without substance ("You're absolutely right")
- Using abbreviations before defining them
- Hedging language: "might", "could potentially", "we hope to"
- Vague claims without specifics
- Excessive jargon without explanation
- Overly humble framing
