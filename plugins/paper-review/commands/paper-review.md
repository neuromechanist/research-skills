---
description: Review an academic manuscript for methodological rigor, statistical validity, and clarity
argument-hint: <path-to-manuscript or description>
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Paper Review

Review an academic manuscript using the paper-review skill.

## Routing

Based on `$ARGUMENTS`:

1. If a file path is provided, read the manuscript using the Read tool (supports PDF, markdown, LaTeX)
2. If a description is provided, ask the user to provide the manuscript file
3. If empty, ask what manuscript to review

## Execution

Load the `paper-review` skill for the full review workflow, methodology checklist, and output template.

Use `opencite` to verify literature claims and search for potentially missing references:
```bash
uvx opencite search "relevant topic" --max 10 --sort citations
uvx opencite canonical "field or method" --max 5
```

For PDF manuscripts, follow the hybrid intake in the paper-review skill: convert to markdown (via `uvx opencite convert`) for text analysis and to PNG for page/line citations. Read the original PDF for figures as needed.

After completing the review, present it in the structured format from `references/review-output-template.md`.
