---
description: Format and prepare a manuscript for journal submission
argument-hint: <journal-name> [--checklist]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Manuscript Preparation

Format a manuscript for a specific journal and run the submission checklist. Load the `manuscript:manuscript-formatting` skill for reference.

## Process

### 1. Identify Target Journal
!echo "Target: $ARGUMENTS"

### 2. Locate Manuscript Files
!ls -la *.md *.tex *.docx *.bib 2>/dev/null || echo "No manuscript files found"
!ls -la figures/ 2>/dev/null || echo "No figures directory"

### 3. Check Journal Requirements
Using the journal-requirements reference, verify:
- Word/page limits
- Required sections
- Reference style
- Figure format and resolution requirements
- Required statements (data availability, ethics, conflicts)

### 4. Format
Apply journal-specific formatting:
- Set correct template/class
- Format references per journal style
- Check figure dimensions and resolution
- Verify section ordering

### 5. Submission Checklist
Run the full checklist from the manuscript-formatting skill:
- Title page complete
- Abstract within limits
- All required sections present
- Figures as separate high-resolution files
- Cover letter drafted
- Required statements included
- Author information complete

### 6. Report
Present a checklist summary with pass/fail for each item.
