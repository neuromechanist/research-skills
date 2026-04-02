---
description: Draft or revise a grant proposal section
argument-hint: <section-name> [--mechanism R01|R21|K99|NSF-CAREER|...]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Grant Writing

Draft or revise a grant proposal section. Load the `grant:grant-writing` skill for reference.

## Process

### 1. Identify Context
Determine:
- Which section to write (specific aims, significance, innovation, approach, budget, biosketch)
- Funding mechanism (R01, R21, K99, K08, F31, F32, NSF CAREER, etc.)
- Whether this is a new draft or revision/resubmission

### 2. Gather Existing Material
!ls -la *.md *.docx *.pdf *.tex 2>/dev/null || echo "No existing documents found"
!ls -la .context/ 2>/dev/null || echo "No .context directory"

### 3. Write Section
Using the grant-writing skill's templates and guidelines:
- Follow mechanism-specific page limits and formatting
- Use the appropriate tone and style for the agency
- Reference the research strategy guidelines for section structure
- For resubmissions, follow the resubmission guide

### 4. Self-Review
After drafting, invoke the `grant:grant-review` skill to score the section and identify weaknesses before presenting to the user.
