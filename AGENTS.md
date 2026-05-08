# Research Skills Marketplace

## Purpose
Cross-agent marketplace providing plugins and skills for academic research workflows and development tooling: literature search and review, grant writing and review, manuscript preparation, scientific figures, presentations, project lifecycle management, and neuroinformatics.

## Skills-first model
This marketplace follows a skills-first surface. Skills auto-trigger from natural-language intent (description matching). Commands are kept only for workflows that need explicit `/command args` orchestration: project init, epic/sprint management, version bumps. Thin command wrappers around skills have been removed; do not reintroduce them.

## Marketplace Structure
```
research-skills/
├── .claude-plugin/marketplace.json  # Claude Code marketplace manifest; also read by Codex and Copilot
├── .agents/plugins/marketplace.json # Native Codex repo marketplace manifest
├── .github/plugin/marketplace.json  # Native Copilot CLI marketplace manifest
├── plugins/
│   ├── project/                      # Project lifecycle toolkit
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── commands/{init-project,update-rules,epic-dev,epic-status,release-prep}.md
│   │   ├── skills/{init-project,update-rules,workflow-reference,ci-scaffolding,docker-packaging,security-audit,document-processing}/
│   │   ├── agents/{dependency-auditor,release-prep}.md
│   │   ├── templates/               # AGENTS, Claude, Cursor, context, config, CI/CD
│   │   └── bin/                     # project-init-templates, project-diff-rules, project-templates-path
│   ├── grant/                        # Grant proposal toolkit
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── skills/{grant-writing,grant-review}/
│   │   └── agents/grant-figure-qa.md
│   ├── manuscript/                   # Academic manuscript toolkit
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   └── skills/{paper-review,manuscript-writing,manuscript-formatting,lit-review}/
│   ├── opencite/                     # Literature search and citation management
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   └── skills/opencite/
│   ├── scientific-figures/           # Icons + plots + composition + QA
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   └── skills/scientific-figures/
│   ├── presentation/                 # Interactive slide decks
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   └── skills/presentation-builder/
│   └── neuroinformatics/             # Neuro data standards + experiments
│       ├── .claude-plugin/plugin.json
│       ├── .codex-plugin/plugin.json
│       ├── skills/{bids-conversion,experiment-design}/
│       └── agents/bids-validator.md
└── .context/
    └── plan.md
```

## Plugins
- **project** (v0.3.1): Project lifecycle toolkit with initialization, rule/config updates, epic/sprint workflow, CI/CD scaffolding, Docker packaging, security audit, and document processing. Commands: `/init-project`, `/update-rules`, `/epic-dev`, `/epic-status`, `/release-prep`.
- **grant** (v0.3.1): NIH/NSF grant proposal writing, structured review with scoring criteria, and figure quality assurance. Skills only.
- **manuscript** (v0.4.2): Literature review (multi-phase citation-traceable corpus protocol + single-pass thematic synthesis), peer review, writing guidance, and journal-specific formatting for submission. Skills only.
- **opencite** (v0.3.1): Academic literature search, citation management, PDF retrieval, identifier conversion, and BibTeX export. Skills only. (Single-pass literature-review synthesis moved to `manuscript:lit-review`.)
- **scientific-figures** (v0.2.1): Publication-quality figures covering icons, plots, composition, and QA. Icon generation auto-selects between Codex CLI (`codex login`) and OpenAI API (`OPENAI_API_KEY`).
- **presentation** (v0.2.1): Interactive Reveal.js presentations from JSON via the Agentic Presentation Builder. Skills only.
- **neuroinformatics** (v0.2.1): Neuroscience data standards (BIDS, HED), experiment design (PsychoPy, LSL), and dataset validation. Skills only.

## Development
- Use Bun for any JS/TS work (react-pdf figures)
- Use UV for any Python work (icon generation scripts)
- Prefer uvx/bunx for on-the-fly execution
- Each plugin has independent versioning in its own plugin.json
- No mocks in tests
- No emojis in commits or code

## Cross-agent compatibility
- Keep shared project and marketplace instructions in AGENTS.md.
- Keep CLAUDE.md as `@AGENTS.md`, followed only by Claude Code-specific additions.
- Prefer shared `skills/*/SKILL.md` directories across Claude Code, Codex, and Copilot CLI. Keep `agents/*` declared only in manifests for agents that support them.
