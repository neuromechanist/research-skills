# Getting Started

## Install

### Claude Code

In Claude Code, type `/plugin`, select **Add marketplace**, enter:

```
neuromechanist/research-skills
```

Then select which plugins to install. Each plugin is independent.

Install all plugins via CLI:

```bash
claude plugin marketplace add neuromechanist/research-skills
for p in project grant manuscript opencite figures presentation neuroinformatics; do
  claude plugin install "$p@research-skills"
done
```

### Codex

Codex can use the native repo marketplace at `.agents/plugins/marketplace.json`; the Claude-compatible `.claude-plugin/marketplace.json` remains for legacy-compatible installs.

```bash
codex plugin marketplace add neuromechanist/research-skills
codex plugin marketplace add ./path/to/research-skills
```

Each plugin also has a native `.codex-plugin/plugin.json` manifest. Open `/plugins` in Codex and install the plugins you need.

### GitHub Copilot CLI

Copilot CLI can use the native marketplace at `.github/plugin/marketplace.json`. Each plugin also has a native `.github/plugin/plugin.json` manifest.

```bash
copilot plugin marketplace add neuromechanist/research-skills
copilot plugin marketplace browse research-skills
copilot plugin install project@research-skills
```

### Optional personal defaults

After installing the project plugin, ask it to install user-level instructions:

```text
Install my user instructions for Claude Code, Codex, Copilot CLI, and Cursor.
```

The `install-user-instructions` skill asks which systems you actually want,
previews each change, and uses the documented user surface for each tool.
General personal defaults stay at user scope; repository `AGENTS.md` and
tool-specific adapters keep only project facts and deltas.

See [Cross-Agent Compatibility](cross-agent-compatibility.md) for the researched registration paths and source links behind each of these install commands.

## Skills vs. commands

This marketplace follows a skills-first surface: skills auto-trigger from natural-language intent, described by matching the task you describe against each skill's frontmatter. There is no explicit invocation step for most work. Commands exist only where a workflow needs an explicit `/command args` entry point: project init, epic/sprint management, and version bumps.

For example, once the `manuscript` plugin is installed, saying "review this manuscript at paper.pdf as a peer reviewer" triggers the `paper-review` skill directly. There is no `/review-paper` command to remember or look up.

## Requirements

Each plugin's runtime tooling requirements (the `opencite` CLI, Inkscape/cairosvg, PsychoPy, `bids-validator`, and so on) are noted on that plugin's own page. See the [README's Requirements section](https://github.com/neuromechanist/research-skills#requirements) for the full consolidated list.
