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
│   ├── opencite/          # Literature search and citation management
│   ├── grant-writing/     # NIH/NSF grant proposal writing
│   ├── icon-generation/   # Scientific icon generation (Nature/Science style)
│   ├── pdf-figures/       # Paper-ready PDF figures via react-pdf
│   └── grant-review/      # Grant proposal review (NIH/NSF criteria)
└── .context/
    └── plan.md
```

## Skills Overview
- **opencite**: Academic literature search, citation graph, PDF retrieval, BibTeX export via the opencite CLI
- **grant-writing**: NIH/NSF grant proposal drafting with mechanism-specific templates and formatting
- **icon-generation**: Flat scientific icons in Nature/Science style using gpt-image-1.5
- **pdf-figures**: Paper-ready composite figures with standard academic dimensions via react-pdf
- **grant-review**: Structured grant proposal review using NIH/NSF scoring criteria

## Development
- Use Bun for any JS/TS work (react-pdf figures)
- Use UV for any Python work (icon generation scripts)
- No mocks in tests
- No emojis in commits or code
