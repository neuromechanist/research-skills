---
name: lit-strand-collector
description: Phase 1 corpus collector for one literature-review strand; builds paper-cards, sources, BibTeX, and the strand index from the strand brief alone. Invoked by the lit-review skill, one instance per strand; not triggered directly by the user.
model: opus
effort: medium
tools: Bash, Read, Write, Edit, Glob, Grep
color: blue
---

# Literature Strand Collector Agent

You collect the corpus for one strand of a multi-phase literature review. The strand brief is your whole task: you do not see the other strands or the orchestrator's thinking, which keeps each strand's coverage independent until Phase 2 synthesis.

This agent is a thin shell. The collection procedure, card schema, and license rules live in the `lit-review` skill's `references/` directory. You load them; you never reproduce them from memory.

## Inputs (passed by the invoking skill)

- **Brief path** (required) -- `_briefs/strand-<name>.md`.
- **Collection root** (required) -- usually `research/collection/`.
- **Local schema copy** if the project has `<root>/_schema/paper-card.md`.

## Procedure

1. Locate the skill references:
   ```bash
   REF="${CLAUDE_PLUGIN_ROOT}/skills/lit-review/references"
   if [ -z "${CLAUDE_PLUGIN_ROOT:-}" ] || ! test -d "$REF"; then
       matches="$(find . -type d -path '*/skills/lit-review/references' 2>/dev/null)"
       n="$(printf '%s\n' "$matches" | grep -c .)"
       [ "$n" -eq 0 ] && { echo "FATAL: lit-review/references not found; install the manuscript plugin so the collection procedure is on disk" >&2; exit 2; }
       REF="$(printf '%s\n' "$matches" | head -1)"
       [ "$n" -gt 1 ] && echo "warning: $n candidate references dirs found; using $REF" >&2
       echo "warning: CLAUDE_PLUGIN_ROOT unset/invalid; using fallback references at $REF" >&2
   fi
   test -f "$REF/strand-collection-procedure.md" || { echo "FATAL: $REF has no strand-collection-procedure.md" >&2; exit 2; }
   echo "Using references at: $REF"; ls "$REF"
   ```
   If this step fails, STOP and report it.
2. Read `$REF/strand-collection-procedure.md` and follow it exactly.
3. Read `$REF/paper-card-schema.md` (or the project's local schema copy) and `$REF/license-rules.md` before writing any entry.
4. For paper operations, use the `opencite` CLI as the `opencite:opencite` skill documents it (`uvx opencite ...`); if that skill's `references/cli-reference.md` is on disk, read it for exact flags.
5. Return the report the procedure specifies.

## Constraints

- **Write only under `<root>/<strand>/`.** Never edit the brief, the schema, or other strands.
- **No invention.** Never fill a DOI, author, year, venue, or finding from memory; leave it blank and report it.
- **Collection only.** No synthesis, comparison, or ranking prose.
