---
name: install-user-instructions
description: "Install, update, or audit general user-level AI coding instructions across Claude Code, OpenAI Codex, GitHub Copilot CLI, and Cursor. Use when the user asks to set up global instructions, personal AGENTS.md or CLAUDE.md defaults, configure instructions for multiple agent systems, avoid repeated downstream project rules, install model-routing defaults, or migrate Claude-only user rules to cross-agent user scope."
---

# Install User Instructions

Install shared personal defaults at each selected system's supported user
surface without overwriting custom content or copying global rules into every
repository.

## Workflow

1. Detect available systems with read-only checks (`command -v` plus existing
   target files). Do not infer that every detected system should be modified.
2. Ask the user which of Claude Code, Codex, Copilot CLI, and Cursor to
   configure. This selection is required before any user-home write.
3. Read `references/platform-paths.md` for the selected systems. Resolve
   documented home overrides before default paths.
4. Choose the instruction content:
   - use `assets/global-instructions.md` for the project defaults;
   - use a user-supplied file with `--template` when requested;
   - never silently copy a repository's project-specific instructions into
     user scope.
5. Run `scripts/install_user_instructions.py --systems <csv>` without
   `--apply`. This is the mandatory dry-run and diff preview.
6. Show every destination and diff. For Cursor, show the copy/paste block for
   **Cursor Settings > Rules**; do not invent a filesystem destination.
7. Ask for confirmation of the exact selected destinations and changes.
8. After confirmation, rerun with `--apply`. Writing outside the workspace may
   require the runtime's normal filesystem approval.
9. Verify each selected system using the command or UI check in
   `references/platform-paths.md`.
10. Audit the current repository for duplicated general rules. Report exact
    duplicates or conflicts, but remove project content only with separate
    user approval.

## Non-destructive contract

- Manage only the block between
  `<!-- research-skills:global-instructions:start -->` and
  `<!-- research-skills:global-instructions:end -->`.
- Preserve all content outside the managed block byte-for-byte.
- Fail on unmatched or repeated markers instead of guessing.
- Default to preview mode. `--apply` is required for writes.
- Write only explicitly selected systems.
- Keep Cursor manual until its official User Rules surface exposes a stable,
  supported file path.
- Keep general personal defaults at user scope. Repository `AGENTS.md`,
  `CLAUDE.md`, `.github/copilot-instructions.md`, and `.cursor/rules` contain
  only project facts or system-specific/path-scoped deltas.
- Do not duplicate shared project rules in `CLAUDE.md`; import `AGENTS.md` and
  append Claude-only deltas.

## Script examples

Preview Claude, Codex, and Copilot targets:

```bash
uv run python scripts/install_user_instructions.py \
  --systems claude,codex,copilot
```

Apply the approved preview:

```bash
uv run python scripts/install_user_instructions.py \
  --systems claude,codex,copilot --apply
```

Preview Cursor's manual User Rules block:

```bash
uv run python scripts/install_user_instructions.py --systems cursor
```

Use absolute paths to the skill script when the current working directory is
not this skill directory.

## Content policy

The bundled defaults encode the central `agent-fanout` routing contract:
strongest-tier lead judgment, intermediate approved-plan elaboration, and
worker-tier implementation with explicit tests and gates. They also require
closing/removing completed one-off agents.

Use semantic line breaks in prose source generally. GitHub issue and
pull-request bodies are the exception: keep each paragraph on one source line,
separate paragraphs with blank lines, and do not insert sentence- or
clause-level newlines inside a paragraph.
