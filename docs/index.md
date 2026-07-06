# Research Skills

Research Skills is a cross-agent plugin marketplace for academic research and development workflows. It ships **skills**, agent-callable capabilities that auto-trigger from natural-language intent, covering the parts of a research group's work that AI coding agents are good at automating: literature search, grant writing, manuscript preparation, publication figures, presentations, project lifecycle management, and neuroinformatics data standards.

It targets three agent runtimes from one shared set of skill definitions: [Claude Code](https://claude.com/claude-code), [OpenAI Codex](https://developers.openai.com/codex), and [GitHub Copilot CLI](https://docs.github.com/en/copilot).

!!! tip "Learn it hands-on"
    This marketplace is taught week-by-week in the free [Agentic Research Course](https://courses.osc.earth/agentic-research/) from the Open Science Collective.

## Plugins

| Plugin | What it does |
|---|---|
| [Project](plugins/project.md) | Epics/worktrees, PR review, CI/CD, debugging, agent fan-out |
| [Grant](plugins/grant.md) | NIH/NSF proposal writing, review, figure QA |
| [Manuscript](plugins/manuscript.md) | Literature review, peer review, writing, journal formatting |
| [Opencite](plugins/opencite.md) | Literature search, citation management, PDF retrieval |
| [Figures](plugins/figures.md) | Publication-quality figure composition and QA |
| [Presentation](plugins/presentation.md) | Interactive Reveal.js slide decks |
| [Neuroinformatics](plugins/neuroinformatics.md) | BIDS conversion, HED annotation, experiment design |

Start with [Getting Started](getting-started.md) to install a plugin, or [Architecture](architecture.md) to see how skills, commands, agents, and MCP servers fit together.
