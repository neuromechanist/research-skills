# Research Skills

Claude Code marketplace for academic research workflows and development tooling. Install individual plugins for literature search, grant proposals, manuscript preparation, scientific figures, presentations, project lifecycle management, and neuroinformatics.

## Install

In Claude Code, type `/plugin`, select **Add marketplace**, enter:

```
neuromechanist/research-skills
```

Then select which plugins to install. Each plugin is independent.

### Install all plugins via CLI

```bash
claude plugin marketplace add neuromechanist/research-skills
for p in project grant manuscript opencite scientific-figures presentation neuroinformatics; do
  claude plugin install "$p@research-skills"
done
```

## Plugins

Skills auto-trigger on user intent (described per-plugin below). Slash commands are reserved for workflows that need explicit orchestration entry points.

| Plugin | Version | Description | Skills | Commands |
|--------|---------|-------------|--------|----------|
| **project** | 0.3.0 | Project lifecycle: init, rule/config updates, workflow, CI/CD, Docker, security, doc-processing | `init-project`, `update-rules`, `workflow-reference`, `ci-scaffolding`, `docker-packaging`, `security-audit`, `document-processing` | `/init-project`, `/update-rules`, `/epic-dev`, `/epic-status`, `/release-prep` |
| **grant** | 0.3.0 | NIH/NSF grant proposal writing, review, and figure QA | `grant-writing`, `grant-review` | -- |
| **manuscript** | 0.4.0 | Academic manuscript multi-phase + single-pass lit review, peer review, writing, and journal formatting | `lit-review`, `paper-review`, `manuscript-writing`, `manuscript-formatting` | -- |
| **opencite** | 0.3.0 | Literature search, citation management, PDF retrieval | `opencite` | -- |
| **scientific-figures** | 0.2.0 | Full figure pipeline: icons, plots, composition, visual QA | `scientific-figures` | -- |
| **presentation** | 0.2.0 | Interactive Reveal.js presentations from JSON | `presentation-builder` | -- |
| **neuroinformatics** | 0.2.0 | BIDS conversion/validation, HED annotation, PsychoPy experiment design | `bids-conversion`, `experiment-design` | -- |

## Research Plugins

### opencite

Search academic literature, explore citation graphs, download PDFs, and export BibTeX. Wraps the [`opencite`](https://github.com/neuromechanist/opencite) CLI, aggregating Semantic Scholar, OpenAlex, PubMed, arXiv, and bioRxiv.

```
"Find the top 10 most cited papers on brain-computer interfaces"
"Look up DOI 10.1038/nature12373 and download the PDF"
"Convert this PDF to markdown"
```

### grant

Draft and review NIH and NSF grant proposals with mechanism-specific templates (R01, R21, K99, CAREER, etc.). Includes a grant-figure-qa agent that autonomously checks figures for resolution, accessibility, and NIH/NSF compliance. Skills for research strategy guidelines, writing style, budget justification, scoring criteria, and resubmission response.

```
"Write the significance section for an R01 on motor cortex"
"Review my R21 proposal at proposal.pdf as an NIH study section"
```

### manuscript

Academic manuscript toolkit covering the full lifecycle: literature review (both multi-phase citation-traceable corpus protocol and single-pass thematic synthesis), writing guidance (IMRAD structure, section templates), peer review (methodology, statistics, reproducibility), and journal-specific formatting (IEEE, Nature, PNAS, Elsevier, LaTeX/BibTeX management). Includes revision response templates.

The `manuscript:lit-review` skill covers two modes: a rigorous, iterable, citation-traceable multi-phase workflow where every claim in a direction paper links back to a paper-card on disk, plus an express single-pass synthesis pipeline for writing an Introduction or Background section.

```
"Review this manuscript at paper.pdf as a peer reviewer"
"Format my paper for Nature Neuroscience"
"Start a multi-phase lit review on EEG-based BCIs with strands tools, data, science"
"Write a single-pass literature review on motor cortex oscillations"
```

### scientific-figures

Create publication-quality figures for Nature, Science, PNAS, Cell, and other journals:

1. **Plan** -- target journal, panel layout, color palette
2. **Create elements** -- icons (gpt-image-2), plots (matplotlib/seaborn/plotly/ggplot2)
3. **Compose** -- assemble into PDF via react-pdf
4. **Visual QA** -- render to PNG, read the image, verify alignment/labels/overlap, iterate

All elements saved as SVG or transparent PNG. Enforces sans-serif fonts, colorblind-safe palettes, and journal-specific dimensions. Runs on-the-fly via `uvx` and `bunx`.

### presentation

Create interactive Reveal.js presentations from JSON using the [Agentic Presentation Builder](https://github.com/neuromechanist/agentic-presentation-builder). Supports 7 element types (text, bullets, images, Mermaid diagrams, callouts, code blocks, tables), 5 themes, animated progressive reveals, speaker notes, and LaTeX math.

The skill teaches Claude the JSON schema and authoring workflow; the builder repo handles rendering.

```
"Create a 10-slide academic presentation on EEG signal processing"
"Build a conference talk on brain-computer interfaces"
```

### neuroinformatics

Neuroscience data standards, experiment design, and dataset validation:

- **BIDS conversion** -- convert EEG, EMG, and other modalities to Brain Imaging Data Structure (BIDS) format with proper file naming, JSON sidecars, and metadata
- **Experiment design** -- scaffold PsychoPy experiments with stimulus presentation, LSL marker integration, and BIDS-compatible output
- **BIDS validator agent** -- autonomously validate datasets, diagnose errors, and apply fixes

```
"Convert ./raw-data to BIDS format, modality EEG, task rest"
"Validate the BIDS dataset at ./bids-dataset"
"Design a visual oddball ERP paradigm with 2 conditions"
```

## Development Plugin

### project

Complete project lifecycle toolkit combining initialization, epic/sprint workflow, and CI/CD management:

- **init-project** -- scaffold new projects with Claude/Cursor templates, `.rules/`, `.context/`, and config files
- **update-rules** -- non-destructive sync of CLAUDE.md and `.rules/` against latest templates at user or project level
- **workflow** -- multi-phase feature development with git worktrees, GitHub issues, and phased PR delivery
- **CI scaffolding** -- generate GitHub Actions workflows for Python (ruff + pytest) or TypeScript (biome + bun test)
- **Docker packaging** -- multi-stage Dockerfiles with uv/bun, health checks, and security hardening
- **Security audit** -- credential scanning, dependency audit, OWASP checklist, configuration hardening
- **Document processing** -- PDF/image OCR, text extraction, markdown conversion

Includes autonomous agents: **dependency-auditor** (vulnerability scanning) and **release-prep** (pre-release validation).

```
/init-project "Python EEG analysis package"
/update-rules project
/epic-dev "build a community dashboard"
/release-prep --minor
"Set up CI for this Python project with ruff and pytest"
"Process scanned-document.pdf and convert to markdown"
```

## Structure

```
research-skills/
├── .claude-plugin/marketplace.json
├── plugins/
│   ├── project/                   # Project lifecycle (init, workflow, CI, Docker, security, docs)
│   ├── grant/                     # Grant proposals (writing, review, figure QA)
│   ├── manuscript/                # Manuscripts (review, writing, formatting)
│   ├── opencite/                  # Literature search and citation management
│   ├── scientific-figures/        # Icons + plots + composition + QA
│   ├── presentation/             # Interactive Reveal.js slide decks
│   └── neuroinformatics/          # BIDS, HED, experiment design
```

## Requirements

- [Claude Code](https://claude.com/claude-code) CLI
- For opencite: `opencite` CLI (`uvx opencite`)
- For icons: OpenAI API key (gpt-image-2)
- For plots: matplotlib/seaborn/plotly via `uvx` (on-the-fly)
- For figure composition: react-pdf via `bunx` (on-the-fly)
- For PDF conversion: poppler (`brew install poppler` on macOS)
- For presentations: [agentic-presentation-builder](https://github.com/neuromechanist/agentic-presentation-builder) (local clone)
- For BIDS validation: bids-validator (`bunx bids-validator`)
- For OCR: Mistral API key (optional, tesseract as offline fallback)

## Skills vs commands

Per the [official Anthropic plugin guidance](https://docs.claude.com/), skills are the preferred surface for agent-callable capabilities and auto-trigger from their description. Commands are kept only for workflows that benefit from explicit `/command args` orchestration (epic/sprint management, project init, version bumps). Each plugin's skills are listed in the table above; describe your task in natural language and the matching skill will load.

## Versioning

- Each plugin has independent versioning in its `plugin.json`
- Adding a new plugin/skill = marketplace minor bump (0.x.0)
- Version bump within an existing plugin = marketplace patch bump (0.x.y)

## Notes

The `opencite` plugin included here is a snapshot of the standalone [`neuromechanist/opencite`](https://github.com/neuromechanist/opencite) plugin. If you have already installed that standalone plugin, do not install it again from this marketplace; having both installed will create duplicate skills.

## License

BSD-3-Clause
