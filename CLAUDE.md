# Research Skills Plugin

## Purpose
Claude Code plugin providing skills for academic research workflows: literature search, grant writing, scientific figure creation, and grant proposal review.

## Plugin Structure
```
research-skills/
├── .claude-plugin/plugin.json
├── commands/
│   └── opencite.md
├── skills/
│   ├── opencite/              # Literature search and citation management
│   ├── grant-writing/         # NIH/NSF grant proposal writing
│   ├── scientific-figures/    # Full pipeline: elements + composition + QA
│   └── grant-review/          # Grant proposal review (NIH/NSF criteria)
└── .context/
    └── plan.md
```

## Skills Overview
- **opencite**: Academic literature search, citation graph, PDF retrieval, BibTeX export via the opencite CLI
- **grant-writing**: NIH/NSF grant proposal drafting with mechanism-specific templates and formatting
- **scientific-figures**: Publication-quality figures (Nature/Science/PNAS style) covering icon generation, data plots (matplotlib/seaborn/ggplot2/plotly), react-pdf composition, and visual QA feedback loop
- **grant-review**: Structured grant proposal review using NIH/NSF scoring criteria

## Development
- Use Bun for any JS/TS work (react-pdf figures)
- Use UV for any Python work (icon generation scripts)
- Prefer uvx/bunx for on-the-fly execution
- No mocks in tests
- No emojis in commits or code
