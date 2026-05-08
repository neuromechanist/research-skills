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

Codex supports repository marketplaces at `.agents/plugins/marketplace.json` and can also read Claude-style marketplaces at `.claude-plugin/marketplace.json`. This repo includes the native `.agents/plugins/marketplace.json` so a checkout can be used directly as a Codex marketplace root:

```bash
codex plugin marketplace add neuromechanist/research-skills
codex plugin marketplace add ./path/to/research-skills
```

Codex skills are directories containing `SKILL.md` files with `name` and `description` frontmatter. The native `.codex-plugin/plugin.json` manifests point at the existing `plugins/<name>/skills/` trees. Claude/Copilot-only commands and agents stay declared in the `.claude-plugin/plugin.json` manifests.

## GitHub Copilot CLI

Copilot CLI supports marketplaces through `.github/plugin/marketplace.json` and also looks for `.claude-plugin/marketplace.json`. This repo includes `.github/plugin/marketplace.json` for the native Copilot path:

```bash
copilot plugin marketplace add neuromechanist/research-skills
copilot plugin marketplace browse research-skills
copilot plugin install project@research-skills
```

Copilot CLI reads plugin manifests from `.plugin/plugin.json`, `plugin.json`, `.github/plugin/plugin.json`, or `.claude-plugin/plugin.json`. The existing `.claude-plugin/plugin.json` files are therefore intentionally retained and now declare their `skills`, `agents`, and `commands` component paths where applicable.

## Sources

- OpenAI Codex AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex plugin build guide: https://developers.openai.com/codex/plugins/build
- OpenAI Codex skills guide: https://developers.openai.com/codex/skills
- GitHub Copilot repository instructions: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- GitHub Copilot custom instructions support: https://docs.github.com/en/copilot/reference/custom-instructions-support
- GitHub Copilot CLI plugin reference: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference
