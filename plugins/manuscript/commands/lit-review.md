---
description: Orchestrate a multi-phase, citation-grounded literature review
argument-hint: [--phase brief|collect|synthesize|direct|review] [--strand <name>] [--init <path>]
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---

# Multi-Phase Literature Review

Orchestrate a rigorous lit-review workflow across phases. Load the `manuscript:lit-review` skill for the full protocol, schemas, and templates.

## Process

### 1. Identify intent

!echo "Args: $ARGUMENTS"

Parse arguments:
- `--init <path>`: bootstrap a new lit-review root at `<path>` (or current dir if omitted). Create `_briefs/`, `research/collection/_schema/`, `research/synthesis/`, `direction-papers/` on demand. Drop `paper-card.md` schema as `research/collection/_schema/paper-card.md` (copy from skill references).
- `--phase brief`: route to Phase 0 guidance. Inputs: prior work, gap statement, epic-dev findings. Output: one brief per strand in `_briefs/strand-<name>.md`.
- `--phase collect [--strand <name>]`: route to Phase 1. Inputs: a brief. Output: paper-cards under `research/collection/<strand>/`. Use `opencite:opencite` for paper ops.
- `--phase synthesize`: route to Phase 2. Inputs: full collection. Outputs in `research/synthesis/`: `<strand>-ontology.md`, `<domain>-map.md`, `gap-analysis.md`, `scope-diagram.md`.
- `--phase direct`: route to Phase 3. Inputs: synthesis + briefs. Output: `direction-papers/<topic>-direction.md`.
- `--phase review`: route to Phase 4. Self-review the latest direction paper using `manuscript:paper-review`. Loop back to prior phases as needed.

If no argument, infer phase from current directory state:
- No `_briefs/` -> Phase 0 (suggest `--init` first if root is empty).
- `_briefs/` populated, `research/collection/` empty or partial -> Phase 1.
- `research/collection/` complete per brief acceptance, `research/synthesis/` empty -> Phase 2.
- `research/synthesis/` populated, `direction-papers/` empty -> Phase 3.
- `direction-papers/` populated -> Phase 4.

### 2. Locate state

!ls -d _briefs research/collection research/synthesis direction-papers 2>/dev/null
!find _briefs -name 'strand-*.md' 2>/dev/null | head -20
!find research/collection -mindepth 2 -maxdepth 2 -type d 2>/dev/null | head -20
!ls research/synthesis 2>/dev/null
!ls direction-papers 2>/dev/null

### 3. Route to phase

Load the `manuscript:lit-review` skill and apply its phase-specific guidance:

- Phase 0 (Briefs): use `references/brief-template.md`.
- Phase 1 (Collection): use `references/paper-card-schema.md` and `references/license-rules.md`. Dispatch parallel strand agents if multiple briefs exist.
- Phase 2 (Synthesis): use `references/synthesis-templates.md`. Apply bias rules.
- Phase 3 (Direction): use `references/direction-paper-template.md`. Delegate review-paper IMRAD structuring and prose discipline to `manuscript:manuscript-writing`. Delegate journal LaTeX export to `manuscript:manuscript-formatting`.
- Phase 4 (Review): invoke `manuscript:paper-review` on the latest direction paper. Disposition each concern (ground / restructure / drop). Loop back as needed.

### 4. Apply rigor checklist

Before declaring a phase done, walk `references/rigor-checklist.md` for the active phase. Loop back if any item fails.

### 5. Report

Summarize:
- Active phase
- Acceptance criteria met / outstanding
- Suggested next phase
- Outstanding loop-backs (if any)
