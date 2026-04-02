# Research Skills Marketplace

## Purpose
Claude Code marketplace providing plugins for academic research workflows and development tooling: literature search and review, grant writing and review, manuscript preparation, scientific figures, project lifecycle management, and neuroinformatics.

## Marketplace Structure
```
research-skills/
├── .claude-plugin/marketplace.json   # Marketplace manifest
├── plugins/
│   ├── project/                      # Project lifecycle toolkit
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/{init-project,epic-dev,epic-status,setup-ci,release-prep,doc-process}.md
│   │   ├── skills/{init-project,workflow-reference,ci-scaffolding,docker-packaging,security-audit,document-processing}/
│   │   ├── agents/{dependency-auditor,release-prep}.md
│   │   ├── templates/               # Claude, Cursor, context, config, CI/CD
│   │   └── scripts/
│   ├── grant/                        # Grant proposal toolkit
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/{grant-write,grant-review}.md
│   │   ├── skills/{grant-writing,grant-review}/
│   │   └── agents/grant-figure-qa.md
│   ├── manuscript/                   # Academic manuscript toolkit
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/{paper-review,manuscript-prep}.md
│   │   └── skills/{paper-review,manuscript-writing,manuscript-formatting}/
│   ├── opencite/                     # Literature search and review
│   │   ├── .claude-plugin/plugin.json
│   │   ├── commands/opencite.md
│   │   └── skills/{opencite,literature-review}/
│   ├── scientific-figures/           # Icons + plots + composition + QA
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/scientific-figures/
│   └── neuroinformatics/             # Neuro data standards + experiments
│       ├── .claude-plugin/plugin.json
│       ├── commands/{convert-bids,validate-bids,design-experiment}.md
│       ├── skills/{bids-conversion,experiment-design}/
│       └── agents/bids-validator.md
└── .context/
    └── plan.md
```

## Plugins
- **project** (v0.2.0): Project lifecycle toolkit with initialization, epic/sprint workflow, CI/CD scaffolding, Docker packaging, security audit, and document processing
- **grant** (v0.2.0): NIH/NSF grant proposal writing, structured review with scoring criteria, and figure quality assurance
- **manuscript** (v0.2.0): Academic manuscript peer review, writing guidance, and journal-specific formatting for submission
- **opencite** (v0.2.0): Academic literature search, citation management, PDF retrieval, and literature review synthesis
- **scientific-figures** (v0.1.1): Publication-quality figures covering icons, plots, composition, and QA
- **neuroinformatics** (v0.1.0): Neuroscience data standards (BIDS, HED), experiment design (PsychoPy, LSL), and dataset validation

## Development
- Use Bun for any JS/TS work (react-pdf figures)
- Use UV for any Python work (icon generation scripts)
- Prefer uvx/bunx for on-the-fly execution
- Each plugin has independent versioning in its own plugin.json
- No mocks in tests
- No emojis in commits or code
