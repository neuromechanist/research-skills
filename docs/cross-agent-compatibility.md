# Cross-Agent Compatibility

This marketplace keeps Claude Code support while adding documented registration paths for Codex and GitHub Copilot CLI.

## Shared Instructions

Use `AGENTS.md` as the shared source of truth for repository instructions. Codex reads `AGENTS.md` before work and layers global, project, and nested instructions by directory precedence. GitHub Copilot supports repository agent instructions through `AGENTS.md`; Copilot cloud agent also supports root `CLAUDE.md` and `GEMINI.md`.

`CLAUDE.md` should remain a Claude Code adapter:

```markdown
@AGENTS.md

## Claude Code Specific Instructions

Append Claude-only plugin, skill, command, or MCP guidance here.
```

## Claude Code

Claude Code uses the existing marketplace manifest:

```bash
claude plugin marketplace add neuromechanist/research-skills
claude plugin install project@research-skills
```

The canonical Claude marketplace file remains `.claude-plugin/marketplace.json`.

## Codex

Codex supports repository marketplaces at `.agents/plugins/marketplace.json` and legacy-compatible marketplaces at `.claude-plugin/marketplace.json`. This repo includes the native `.agents/plugins/marketplace.json` so a checkout can be used directly as a Codex marketplace root:

```bash
codex plugin marketplace add neuromechanist/research-skills
codex plugin marketplace add ./path/to/research-skills
```

Codex skills are directories containing `SKILL.md` files with `name` and `description` frontmatter. The native `.codex-plugin/plugin.json` manifests point at the existing `plugins/<name>/skills/` trees. Claude-specific commands and agents stay declared in the `.claude-plugin/plugin.json` manifests; Copilot agent templates are exposed through native `.github/plugin/plugin.json` manifests.

Codex custom subagents are separate from plugin skills. Current Codex docs define custom agents as standalone TOML files under `~/.codex/agents/` for personal scope or `.codex/agents/` for project scope, with required `name`, `description`, and `developer_instructions` fields. Codex only spawns subagents when explicitly asked, and `/agent` is used in the CLI to inspect or switch active agent threads. For review/QA surfaces in this marketplace, keep `agents/templates/*.toml` as opt-in Codex custom-agent templates; installing the plugin exposes the skill, not the subagent.

## GitHub Copilot CLI

Copilot CLI supports marketplaces through `.github/plugin/marketplace.json` and also looks for `.claude-plugin/marketplace.json`. This repo includes `.github/plugin/marketplace.json` for the native Copilot path:

```bash
copilot plugin marketplace add neuromechanist/research-skills
copilot plugin marketplace browse research-skills
copilot plugin install project@research-skills
```

Copilot CLI plugin manifests support component path fields including `skills`, `commands`, and `agents`; `agents` points to directories containing `.agent.md` files. Every plugin in this repo now has a native per-plugin `.github/plugin/plugin.json` manifest. Plugins with review/QA agents expose `agents/templates/` as the Copilot `agents` component path. The `agents/*.md` files remain Claude Code agent shells; `agents/templates/*.agent.md` are the Copilot custom-agent files.

Copilot custom-agent files use YAML frontmatter where `description` is required and the Markdown body defines the agent behavior. Optional frontmatter includes `name`, `tools`, `model`, `target`, `disable-model-invocation`, and `user-invocable`. Keep review/QA agent descriptions scoped to "invoked by the `<skill>` skill" so the skill remains the cross-agent trigger owner.

## Sources

- OpenAI Codex AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex plugin build guide: https://developers.openai.com/codex/plugins/build
- OpenAI Codex skills guide: https://developers.openai.com/codex/skills
- OpenAI Codex subagents guide: https://developers.openai.com/codex/subagents
- GitHub Copilot repository instructions: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- GitHub Copilot custom instructions support: https://docs.github.com/en/copilot/reference/custom-instructions-support
- GitHub Copilot custom agents configuration: https://docs.github.com/en/copilot/reference/custom-agents-configuration
- GitHub Copilot CLI plugin reference: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference
