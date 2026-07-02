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
- When a plugin is touched for a release-visible change, bump that plugin's
  patch version across all per-plugin manifests and marketplace entries.
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

## Review And QA Surfaces

- Review and QA skills own natural-language triggers and load shared
  `references/` procedures or rubrics.
- Agent shells must stay thin and fresh-context: they load the shared
  references, review only the caller-provided scope, and avoid competing with
  the skill's trigger description.
- If a fresh-context agent is not available in the current tool, the skill must
  provide an inline fallback that follows the same reference procedure.
