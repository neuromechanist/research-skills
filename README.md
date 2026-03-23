# Research Skills

Claude Code plugin for academic research workflows: literature search, grant writing, scientific figure creation, and grant proposal review.

## Install

In Claude Code, type `/plugin`, select **Add marketplace**, enter:

```
neuromechanist/research-skills
```

Then restart Claude Code. All skills become available automatically.

## Skills

| Skill | Description | Trigger |
|-------|-------------|---------|
| **opencite** | Literature search, citation graph, PDF retrieval, BibTeX export | `/opencite` or ask about papers, citations, DOIs |
| **grant-writing** | NIH/NSF grant proposal drafting with mechanism-specific templates | Ask to write or draft a grant |
| **scientific-figures** | Full figure pipeline: icons, plots, composition, visual QA | Ask to create figures, plot data, make icons, compose panels |
| **grant-review** | Structured grant proposal review using NIH/NSF scoring criteria | Ask to review a grant proposal |

## Scientific Figures Pipeline

The `scientific-figures` skill covers the entire workflow:

1. **Plan** -- target journal, panel layout, color palette
2. **Create elements** -- icons (gpt-image-1.5), plots (matplotlib/seaborn/plotly/ggplot2), diagrams
3. **Compose** -- assemble into publication-ready PDF via react-pdf
4. **Visual QA** -- render to PNG, inspect, iterate until pixel-perfect

All elements saved as SVG or transparent PNG. Final output is a precisely-sized PDF matching journal specs (Nature, Science, PNAS, Cell, IEEE, PLoS). Enforces 9-10pt sans-serif fonts, clean panel labels, colorblind-safe palettes, and proper tick/axis formatting.

Everything runs on-the-fly via `uvx` (Python) and `bunx` (JS/TS); no permanent installs needed.

## Usage Examples

```
# Literature search
/opencite search "motor cortex oscillations"

# Or just ask naturally
"Find the top 10 most cited papers on brain-computer interfaces"
"Draft the significance section for my NSF CAREER proposal"
"Review my R01 specific aims page"

# Scientific figures
"Create a 4-panel figure for my Nature submission"
"Generate a flat icon of a neuron for my graphical abstract"
"Plot the EEG power spectrum data as a figure element"
"Compose a double-column figure with workflow diagram"
```

## Structure

```
research-skills/
├── .claude-plugin/plugin.json
├── commands/
│   └── opencite.md               # /opencite slash command
├── skills/
│   ├── opencite/                 # Literature search and citation management
│   ├── grant-writing/            # NIH/NSF grant proposal writing
│   ├── scientific-figures/       # Icons + plots + composition + QA
│   │   ├── SKILL.md
│   │   ├── references/           # Standards, palettes, element guides
│   │   ├── examples/             # Working figure examples
│   │   └── scripts/              # Icon generation script
│   └── grant-review/             # Grant proposal review
└── .context/
    └── plan.md
```

## Requirements

- [Claude Code](https://claude.com/claude-code) CLI
- For opencite: `opencite` CLI (`uvx opencite`)
- For icons: OpenAI API key (gpt-image-1.5)
- For plots: matplotlib/seaborn/plotly via `uvx` (on-the-fly)
- For figure composition: react-pdf via `bunx` (on-the-fly)

## License

BSD-3-Clause
