# Research Skills Marketplace

## Purpose
Claude Code marketplace providing plugins for academic research workflows and development tooling: literature search, grant writing, scientific figures, grant review, paper review, project initialization, and epic/sprint workflow automation.

## Marketplace Structure
```
research-skills/
├── .claude-plugin/marketplace.json   # Marketplace manifest
├── plugins/
│   ├── opencite/                     # Literature search and citation management
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/opencite.md
│   │   └── skills/opencite/
│   ├── grant-writing/                # NIH/NSF grant proposal writing
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/grant-writing/
│   ├── scientific-figures/           # Icons + plots + composition + QA
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/scientific-figures/
│   ├── grant-review/                 # Grant proposal review (NIH/NSF criteria)
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/grant-review/
│   ├── paper-review/                 # Academic manuscript peer review
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/paper-review.md
│   │   └── skills/paper-review/
│   ├── init-project/                 # Project initialization templates
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/init-project.md
│   │   ├── skills/init-project/
│   │   └── templates/               # Claude, Cursor, context, config, CI/CD
│   └── workflow/                     # Epic/sprint workflow automation
│       ├── .claude-plugin/plugin.json
│       ├── commands/{epic-dev,epic-status}.md
│       ├── skills/workflow-reference/
│       └── scripts/
└── .context/
    └── plan.md
```

## Plugins
- **opencite** (v0.1.0): Academic literature search, citation graph, PDF retrieval, BibTeX export
- **grant-writing** (v0.1.0): NIH/NSF grant proposal drafting with mechanism-specific templates
- **scientific-figures** (v0.1.1): Publication-quality figures covering icons, plots, composition, and QA
- **grant-review** (v0.1.1): Structured grant proposal review using NIH/NSF scoring criteria
- **paper-review** (v0.1.0): Academic manuscript peer review emphasizing methodological rigor, statistical validity, and reproducibility
- **init-project** (v0.1.0): Project initialization with Claude/Cursor templates, .rules/, .context/, and config scaffolding (consolidates vibe-rules-templates)
- **workflow** (v0.1.0): Epic/sprint development with git worktrees, GitHub issues, and phased PR delivery

## Development
- Use Bun for any JS/TS work (react-pdf figures)
- Use UV for any Python work (icon generation scripts)
- Prefer uvx/bunx for on-the-fly execution
- Each plugin has independent versioning in its own plugin.json
- No mocks in tests
- No emojis in commits or code
