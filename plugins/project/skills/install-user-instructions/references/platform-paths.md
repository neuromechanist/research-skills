# User Instruction Surfaces

Use only documented user-level surfaces. Resolve environment overrides before
the default paths.

The installer follows the same precedence. Its `--home` option changes only
the fallback base; `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, and `COPILOT_HOME` still
win when set. For an isolated preview or test, unset those variables or point
all of them at the isolated tree explicitly.

## Claude Code

- Target: `${CLAUDE_CONFIG_DIR:-~/.claude}/CLAUDE.md`
- Composition: user and project `CLAUDE.md` files are additive. Avoid conflicts;
  use `@AGENTS.md` in a project `CLAUDE.md` instead of copying shared project
  rules.
- User agents: `${CLAUDE_CONFIG_DIR:-~/.claude}/agents/`
- Verify: run `/memory` for loaded instructions, `/agents` for agents, and
  `/status` for the active model.
- Source: https://code.claude.com/docs/en/memory
- Agent source: https://code.claude.com/docs/en/sub-agents

## OpenAI Codex

- Target: `${CODEX_HOME:-~/.codex}/AGENTS.md`
- Override caveat: a non-empty `AGENTS.override.md` at Codex home replaces the
  global `AGENTS.md`. Detect and report it; do not write the override by
  default.
- Composition: Codex loads global guidance, then one file per directory from
  project root toward the working directory. Nearer project guidance wins.
- User agents: `${CODEX_HOME:-~/.codex}/agents/*.toml`
- Verify: start a fresh run with
  `codex --ask-for-approval never "Summarize the current instructions."` and
  use `/agent` to inspect agent threads.
- Source: https://developers.openai.com/codex/guides/agents-md
- Agent source: https://developers.openai.com/codex/subagents

## GitHub Copilot CLI

- Target: `${COPILOT_HOME:-~/.copilot}/copilot-instructions.md`
- Additional personal modules:
  `${COPILOT_HOME:-~/.copilot}/instructions/*.instructions.md`
- Composition: user and repository sources can be combined. Keep personal
  defaults in the user file, shared project rules in `AGENTS.md`, and
  `.github/copilot-instructions.md` for Copilot-specific deltas.
- User agents: `${COPILOT_HOME:-~/.copilot}/agents/*.agent.md`
- Verify: use `/instructions`, `/agent`, and `/model`.
- Source: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions
- Config source: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference

## Cursor

- Target: **Cursor Settings > Rules** (User Rules).
- Do not create a guessed user instruction file. Cursor documents `.cursor/rules`
  as project scope and `.cursorrules` as legacy.
- Composition: User Rules apply globally; use repository `AGENTS.md` for shared
  project guidance and `.cursor/rules` only for Cursor-specific/path-scoped
  deltas.
- Verify: open **Cursor Settings > Rules**, confirm the User Rule, then start a
  fresh Agent chat and inspect the applied rules.
- Source: https://docs.cursor.com/context/rules
