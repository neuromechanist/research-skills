---
description: Review and score a grant proposal using NIH/NSF criteria
argument-hint: <file-path> [--mechanism R01|R21|K99|NSF-CAREER|...]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Grant Review

Review a grant proposal using agency-specific scoring criteria. Load the `grant:grant-review` skill for reference.

## Process

### 1. Load Proposal
Read the specified file or find proposal documents in the current directory.
!echo "Reviewing: $ARGUMENTS"

### 2. Identify Mechanism
Determine the funding mechanism from arguments or proposal content to apply the correct review criteria.

### 3. Score
Follow the grant-review skill's scoring process:
- NIH: 1-9 scale across Significance, Investigator, Innovation, Approach, Environment
- NSF: Intellectual Merit and Broader Impacts

### 4. Output
Generate a structured review using the review output template.
