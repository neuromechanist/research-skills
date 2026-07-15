# Cross-Agent Compatibility

Every marketplace or plugin update must consider all supported surfaces:
Claude Code, Codex, and GitHub Copilot CLI. Do not update one surface's
manifest, skill, command, agent, documentation, or version without checking the
equivalent surfaces and either updating them or documenting why they do not
apply.

## Manifests

- Keep the top-level marketplace manifests in sync:
  `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, and
  `.github/plugin/marketplace.json`.
- Keep per-plugin manifests in sync where they exist:
  `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, and
  `.github/plugin/plugin.json`.
- Adding a skill or another backward-compatible capability to an existing
  plugin requires a plugin minor bump across every per-plugin manifest and
  marketplace entry. Compatible fixes and updates to existing capabilities use
  a plugin patch bump. Breaking plugin changes use a major bump.
- When any marketplace entry changes, bump the top-level marketplace patch
  version in both Claude and Copilot marketplace metadata.

## Skills, Commands, And Agents

- Skills are the portable install-time artifact. Prefer shared
  `skills/*/SKILL.md` directories for capabilities that should work across all
  three tools.
- Commands are for explicit orchestration workflows. Do not reintroduce thin
  command wrappers around skills.
- Claude Code can bundle plugin agents from `agents/*.md`.
- Codex plugin installation exposes skills, not custom subagents. Codex agent
  templates belong in `agents/templates/*.toml` and must be copied to
  `.codex/agents/` or `~/.codex/agents/` before use as custom agents.
- Copilot CLI plugin manifests can expose plugin agent directories through the
  `agents` component path. Copilot custom-agent files are `.agent.md`; for this
  repo, use `agents/templates/` as the plugin `agents` path when a plugin ships
  Copilot agent templates.

## User-Level Instructions

- Ask which systems the user wants configured; detection is not permission to
  write every supported target.
- Claude Code: `${CLAUDE_CONFIG_DIR:-~/.claude}/CLAUDE.md`.
- Codex: `${CODEX_HOME:-~/.codex}/AGENTS.md`; detect a global
  `AGENTS.override.md` because it takes precedence.
- Copilot CLI: `${COPILOT_HOME:-~/.copilot}/copilot-instructions.md`.
- Cursor: User Rules in **Cursor Settings > Rules**. Do not invent an
  undocumented user-level file path.
- Preview every change and preserve unowned content. Keep general personal
  defaults at user scope, shared repository rules in `AGENTS.md`, and
  tool-specific project files limited to deltas so instructions are not
  repeated downstream.

## Review And QA Surfaces

- Review and QA skills own natural-language triggers and load shared
  `references/` procedures or rubrics.
- Agent shells must stay thin and fresh-context: they load the shared
  references, review only the caller-provided scope, and avoid competing with
  the skill's trigger description.
- If a fresh-context agent is not available in the current tool, the skill must
  provide an inline fallback that follows the same reference procedure.
