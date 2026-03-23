# Research Skills

Claude Code marketplace for academic research workflows. Install individual plugins for literature search, grant writing, scientific figure creation, and grant proposal review.

## Install

In Claude Code, type `/plugin`, select **Add marketplace**, enter:

```
neuromechanist/research-skills
```

Then select which plugins to install. Each plugin is independent.

## Plugins

| Plugin | Version | Description |
|--------|---------|-------------|
| **opencite** | 0.1.0 | Literature search, citation graph, PDF retrieval, BibTeX export |
| **grant-writing** | 0.1.0 | NIH/NSF grant proposal drafting with mechanism-specific templates |
| **scientific-figures** | 0.1.0 | Full figure pipeline: icons, plots, composition, visual QA |
| **grant-review** | 0.1.0 | Structured grant proposal review using NIH/NSF scoring criteria |

## Scientific Figures Pipeline

The `scientific-figures` plugin covers the entire workflow:

1. **Plan** -- target journal, panel layout, color palette
2. **Create elements** -- icons (gpt-image-1.5), plots (matplotlib/seaborn/plotly/ggplot2), diagrams
3. **Compose** -- assemble into publication-ready PDF via react-pdf
4. **Visual QA** -- render to PNG, inspect, iterate until pixel-perfect

All elements saved as SVG or transparent PNG. Final output is a precisely-sized PDF matching journal specs (Nature, Science, PNAS, Cell, IEEE, PLoS). Enforces 9-10pt sans-serif fonts, clean panel labels, colorblind-safe palettes.

Everything runs on-the-fly via `uvx` (Python) and `bunx` (JS/TS); no permanent installs needed.

## Usage Examples

```
# Literature search
/opencite search "motor cortex oscillations"

# Or just ask naturally
"Find the top 10 most cited papers on brain-computer interfaces"
"Draft the significance section for my NSF CAREER proposal"
"Review my R01 specific aims page"
"Create a 4-panel figure for my Nature submission"
"Plot the EEG power spectrum as a figure element"
```

## Structure

```
research-skills/
├── .claude-plugin/marketplace.json     # Marketplace manifest
├── plugins/
│   ├── opencite/                       # /opencite command + auto-trigger skill
│   ├── grant-writing/                  # Grant drafting skill + references
│   ├── scientific-figures/             # Icons + plots + composition + QA
│   │   └── skills/scientific-figures/
│   │       ├── SKILL.md
│   │       ├── references/             # Standards, palettes, element guides
│   │       ├── examples/               # Working figure examples
│   │       └── scripts/               # Icon generation script
│   └── grant-review/                   # NIH/NSF review criteria
```

## Requirements

- [Claude Code](https://claude.com/claude-code) CLI
- For opencite: `opencite` CLI (`uvx opencite`)
- For icons: OpenAI API key (gpt-image-1.5)
- For plots: matplotlib/seaborn/plotly via `uvx` (on-the-fly)
- For figure composition: react-pdf via `bunx` (on-the-fly)

## License

BSD-3-Clause
