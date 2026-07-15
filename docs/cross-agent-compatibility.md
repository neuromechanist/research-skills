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

General personal defaults belong at user scope, not copied into every
repository. The project plugin's `install-user-instructions` skill asks which
systems to configure, previews each destination, and manages only a marked
block while preserving surrounding content.

| System | Supported user instruction surface | Verification |
| --- | --- | --- |
| Claude Code | `${CLAUDE_CONFIG_DIR:-~/.claude}/CLAUDE.md` | `/memory` |
| OpenAI Codex | `${CODEX_HOME:-~/.codex}/AGENTS.md` | Start a fresh Codex run and ask it to summarize current instructions |
| GitHub Copilot CLI | `${COPILOT_HOME:-~/.copilot}/copilot-instructions.md` | `/instructions` |
| Cursor | **Cursor Settings > Rules** (User Rules) | Inspect User Rules, then start a fresh Agent chat |

Cursor does not document a stable editable file path for UI User Rules, so the
installer provides a copy/paste block instead of fabricating a home-directory
file. Repository `.cursor/rules` remains project-scoped, while `.cursorrules`
is legacy.

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

Codex custom subagents are separate from plugin skills. Current Codex docs define custom agents as standalone TOML files under `~/.codex/agents/` for personal scope or `.codex/agents/` for project scope, with required `name`, `description`, and `developer_instructions` fields. Optional fields include `model`, `model_reasoning_effort`, sandbox settings, MCP servers, and skills. `/agent` inspects and switches active threads. For review/QA surfaces in this marketplace, keep `agents/templates/*.toml` as opt-in Codex custom-agent templates.

The project workflow routes Codex roles by capability: Sol for architecture,
observation, supervision, and synthesis; Terra for bounded phase-plan
elaboration after architecture approval; and Luna for clear, repeatable
implementation, focused tests, routine review, and validation. Exact aliases
are used only when the current account exposes them. The project plugin ships
opt-in `phase-planner.toml` and `implementation-worker.toml` templates that pin
Terra and Luna for local Codex custom agents.

## GitHub Copilot CLI

Copilot CLI supports marketplaces through `.github/plugin/marketplace.json` and also looks for `.claude-plugin/marketplace.json`. This repo includes `.github/plugin/marketplace.json` for the native Copilot path:

```bash
copilot plugin marketplace add neuromechanist/research-skills
copilot plugin marketplace browse research-skills
copilot plugin install project@research-skills
```

Copilot CLI plugin manifests support component path fields including `skills`, `commands`, and `agents`; `agents` points to directories containing `.agent.md` files. Every plugin in this repo now has a native per-plugin `.github/plugin/plugin.json` manifest. Plugins with review/QA agents expose `agents/templates/` as the Copilot `agents` component path. The `agents/*.md` files remain Claude Code agent shells; `agents/templates/*.agent.md` are the Copilot custom-agent files.

Copilot custom-agent files use YAML frontmatter where `description` is required and the Markdown body defines the agent behavior. Optional frontmatter includes `name`, `tools`, `model`, `target`, `disable-model-invocation`, and `user-invocable`. Keep review/QA agent descriptions scoped to "invoked by the `<skill>` skill" so the skill remains the cross-agent trigger owner.

The native project plugin also exposes phase-planner and
implementation-worker Copilot profiles. They use capability-class language
instead of hard-coded model names because available Copilot model identifiers
vary by environment.

## Claude Code model routing

Claude Code uses Fable when available, otherwise Opus or `best`, for macro
design, observation, supervision, and synthesis. Sonnet implements approved,
detailed plans and performs routine focused review. Any unresolved architecture
or high-risk invariant escalates back to the lead model.

## Agent lifecycle

All supported systems should close/remove completed one-off agents after their
reports are incorporated. Retain an agent only for a named recurring role with
a concrete next task. This avoids stale agent fleets and makes the active
workflow observable.

## GitHub Markdown bodies

Semantic line breaks remain the default for prose source. GitHub issue and
pull-request bodies are the exception because physical newlines can affect
rendering: keep each paragraph on one source line, separate paragraphs with
blank lines, and do not insert sentence- or clause-level newlines inside a
paragraph.

## Sources

- OpenAI Codex AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex plugin build guide: https://developers.openai.com/codex/plugins/build
- OpenAI Codex skills guide: https://developers.openai.com/codex/skills
- OpenAI Codex subagents guide: https://developers.openai.com/codex/subagents
- Anthropic Claude Code memory guide: https://code.claude.com/docs/en/memory
- Anthropic Claude Code subagents guide: https://code.claude.com/docs/en/sub-agents
- GitHub Copilot repository instructions: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- GitHub Copilot CLI user instructions: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions
- GitHub Copilot CLI config directory: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference
- GitHub Copilot custom instructions support: https://docs.github.com/en/copilot/reference/custom-instructions-support
- GitHub Copilot custom agents configuration: https://docs.github.com/en/copilot/reference/custom-agents-configuration
- GitHub Copilot CLI plugin reference: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference
- Cursor rules: https://docs.cursor.com/context/rules
