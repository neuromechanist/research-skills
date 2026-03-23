# Research Skills Marketplace

## Purpose
Claude Code marketplace providing plugins for academic research workflows: literature search, grant writing, scientific figure creation, and grant proposal review.

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
│   └── grant-review/                 # Grant proposal review (NIH/NSF criteria)
│       ├── .claude-plugin/plugin.json
│       └── skills/grant-review/
└── .context/
    └── plan.md
```

## Plugins
- **opencite** (v0.1.0): Academic literature search, citation graph, PDF retrieval, BibTeX export
- **grant-writing** (v0.1.0): NIH/NSF grant proposal drafting with mechanism-specific templates
- **scientific-figures** (v0.1.0): Publication-quality figures covering icons, plots, composition, and QA
- **grant-review** (v0.1.0): Structured grant proposal review using NIH/NSF scoring criteria

## Development
- Use Bun for any JS/TS work (react-pdf figures)
- Use UV for any Python work (icon generation scripts)
- Prefer uvx/bunx for on-the-fly execution
- Each plugin has independent versioning in its own plugin.json
- No mocks in tests
- No emojis in commits or code
