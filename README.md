# Research Skills

Claude Code marketplace for academic research workflows and development tooling. Install individual plugins for literature search, grant writing, scientific figures, grant review, manuscript peer review, project initialization, and epic/sprint workflow automation.

## Install

In Claude Code, type `/plugin`, select **Add marketplace**, enter:

```
neuromechanist/research-skills
```

Then select which plugins to install. Each plugin is independent.

## Plugins

| Plugin | Version | Description | Commands |
|--------|---------|-------------|----------|
| **opencite** | 0.1.0 | Literature search, citation graph, PDF retrieval, BibTeX export | `/opencite` |
| **grant-writing** | 0.1.0 | NIH/NSF grant proposal drafting with mechanism-specific templates | -- |
| **scientific-figures** | 0.1.1 | Full figure pipeline: icons, plots, composition, visual QA | -- |
| **grant-review** | 0.1.1 | Structured grant proposal review using NIH/NSF scoring criteria | -- |
| **paper-review** | 0.1.0 | Academic manuscript peer review: methodology, statistics, reproducibility | `/paper-review` |
| **init-project** | 0.1.0 | Project scaffolding with Claude/Cursor templates, .rules/, .context/, CI/CD | `/init-project` |
| **workflow** | 0.1.0 | Epic/sprint development with git worktrees and phased PR delivery | `/epic-dev`, `/epic-status` |

## Research Plugins

### opencite

Search academic literature, explore citation graphs, download PDFs, and export BibTeX. Wraps the [`opencite`](https://github.com/neuromechanist/opencite) CLI, aggregating Semantic Scholar, OpenAlex, PubMed, arXiv, and bioRxiv.

```
/opencite search "motor cortex oscillations"
"Find the top 10 most cited papers on brain-computer interfaces"
```

### grant-writing

Draft NIH and NSF grant proposals with mechanism-specific templates (R01, R21, K99, CAREER, etc.). Includes references for research strategy guidelines, writing style, and budget justification.

### scientific-figures

Create publication-quality figures for Nature, Science, PNAS, Cell, and other journals:

1. **Plan** -- target journal, panel layout, color palette
2. **Create elements** -- icons (gpt-image-1.5), plots (matplotlib/seaborn/plotly/ggplot2)
3. **Compose** -- assemble into PDF via react-pdf
4. **Visual QA** -- render to PNG, read the image, verify alignment/labels/overlap, iterate

All elements saved as SVG or transparent PNG. Enforces sans-serif fonts, colorblind-safe palettes, and journal-specific dimensions. Runs on-the-fly via `uvx` and `bunx`.

### grant-review

Structured grant proposal review using NIH study section and NSF panel criteria. Scores each criterion, identifies strengths/weaknesses, and provides prioritized actionable improvements. Supports PDF intake with visual layout analysis for figure sizing and space utilization.

### paper-review

Academic manuscript peer review calibrated toward methodological rigor, statistical validity, logical consistency, and reproducibility. Reviews prioritize:

- Experimental design and signal processing validity
- Statistical test appropriateness (paired vs. unpaired, assumptions, corrections)
- Logical consistency (hypothesis -> methods -> results -> conclusions)
- Literature completeness (uses opencite for verification)
- Reproducibility and conflict of interest transparency
- Figure quality (bar plots for small N, baseline correction, scale appropriateness)

Outputs structured reviews with Critical/Major/Minor severity calibration. Uses hybrid PDF intake: markdown for text analysis, PNG for page/line citations.

## Development Plugins

### init-project

Initialize new projects with Claude/Cursor templates, `.rules/` development standards, `.context/` documentation scaffolding, config files, and GitHub Actions workflows. Consolidates the archived [vibe-rules-templates](https://github.com/neuromechanist/vibe-rules-templates) repository.

```
/init-project "Python EEG analysis package"
```

### workflow

Multi-phase feature development using git worktrees, GitHub issues with sub-issues, and phased PR delivery. Supports epic setup, sprint execution, and finalization with automatic state tracking.

```
/epic-dev "build a community dashboard"
/epic-status
/epic-dev --resume
```

## Structure

```
research-skills/
├── .claude-plugin/marketplace.json
├── plugins/
│   ├── opencite/                  # /opencite command + skill
│   ├── grant-writing/             # Grant drafting skill + references
│   ├── scientific-figures/        # Icons + plots + composition + QA
│   ├── grant-review/              # NIH/NSF review criteria + templates
│   ├── paper-review/              # Manuscript review + methodology checklist
│   ├── init-project/              # Project templates (Claude, Cursor, CI/CD)
│   └── workflow/                  # Epic/sprint automation + scripts
```

## Requirements

- [Claude Code](https://claude.com/claude-code) CLI
- For opencite: `opencite` CLI (`uvx opencite`)
- For icons: OpenAI API key (gpt-image-1.5)
- For plots: matplotlib/seaborn/plotly via `uvx` (on-the-fly)
- For figure composition: react-pdf via `bunx` (on-the-fly)
- For PDF conversion: poppler (`brew install poppler` on macOS)

## Versioning

- Each plugin has independent versioning in its `plugin.json`
- Adding a new plugin/skill = marketplace minor bump (0.x.0)
- Version bump within an existing plugin = marketplace patch bump (0.x.y)

## Notes

The `opencite` plugin included here is a snapshot of the standalone [`neuromechanist/opencite`](https://github.com/neuromechanist/opencite) plugin. If you have already installed that standalone plugin, do not install it again from this marketplace; having both installed will create duplicate skills.

## License

BSD-3-Clause
