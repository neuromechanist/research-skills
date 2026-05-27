# Research Skills Marketplace

## Purpose
Cross-agent marketplace providing plugins and skills for academic research workflows and development tooling: literature search and review, grant writing and review, manuscript preparation, figures, presentations, project lifecycle management, and neuroinformatics.

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
│   │   └── skills/{paper-review,manuscript-writing,manuscript-formatting,lit-review,humanizer}/
│   ├── opencite/                     # Literature search and citation management
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   └── skills/opencite/
│   ├── figures/                      # Publication-quality figures (v0.10.0)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── skills/{scientific-figure,transparent-icons,svg-figure,svg-primitives,ai-full-figure,plot-styling}/
│   │   └── agents/figure-qa.md + figure-qa-scripts/{check_svg,check_raster,check_plot_script}.py
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
- **project** (v0.3.3): Project lifecycle toolkit with initialization, rule/config updates, epic/sprint workflow, CI/CD scaffolding, Docker packaging, security audit, and document processing. Commands: `/init-project`, `/update-rules`, `/epic-dev`, `/epic-status`, `/release-prep`.
- **grant** (v0.3.4): NIH/NSF grant proposal writing, structured review with scoring criteria, and figure quality assurance. Cross-references `manuscript:humanizer` from grant-writing and grant-review for natural-writing passes. Skills only.
- **manuscript** (v0.5.0): Literature review (multi-phase citation-traceable corpus protocol + single-pass thematic synthesis), peer review, writing guidance, journal-specific formatting for submission, and the `humanizer` skill for a final natural-writing pass (adapted from [blader/humanizer](https://github.com/blader/humanizer), MIT, Siqi Chen). Skills only.
- **opencite** (v0.3.1): Academic literature search, citation management, PDF retrieval, identifier conversion, and BibTeX export. Skills only. (Single-pass literature-review synthesis moved to `manuscript:lit-review`.)
- **figures** (v0.10.0, epic #31 complete, epic #48 in progress): Replaces the retired `scientific-figures` plugin. Active skills: `scientific-figure` (svgutils-based programmatic composition at exact mm/pt dimensions with pre-export font-size validation against Nature/Science/Cell/PNAS minima; runtime-detected Inkscape exporter with cairosvg fallback); `transparent-icons` (flat scientific icons via Codex CLI image_gen by default, OpenAI Images API fallback, with Pillow-threshold or opt-in rembg+BiRefNet transparency post-process, theme.json bible shared with ai-full-figure); `svg-figure` (hand-authoring conventions and the SVG-spec reference for figure-qa; recommends `svg-primitives` for new programmatic work); `svg-primitives` (mm-precise SVG builder in Python on drawsvg + svgpathtools + fontTools; auto-fits text boxes from measured font metrics, snaps arrow endpoints to box edges via path intersection, emits `<marker orient='auto'>` for tangent-correct arrowheads on curves, and uses named layers for deterministic paint order; ships an E2E pytest suite that asserts text containment, arrow-tip distance, and layer paint order on rendered SVGs); `ai-full-figure` (AI-generated pictorial substrate via Codex CLI or OpenAI Images API plus programmatic label/arrow/scale-bar overlay producing a composable SVG; hard-ceiling rules route complex figures back to `scientific-figure` or `svg-figure`); `plot-styling` (library decision tree across matplotlib / seaborn / plotnine / plotly / PyVista with SciencePlots recipes for Nature, IEEE, Science, Cell, PNAS, and APS). Active agent: `figure-qa` (type-dispatches across SVG / raster / plot-script / composed-figure branches; helper scripts at `agents/figure-qa-scripts/check_{svg,raster,plot_script}.py` with strict programmatic-vs-VLM separation). Full design in `.context/figures-design.md`.
- **presentation** (v0.2.1): Interactive Reveal.js presentations from JSON via the Agentic Presentation Builder. Skills only.
- **neuroinformatics** (v0.2.3): Neuroscience data standards (BIDS, HED), experiment design (PsychoPy, LSL), and dataset validation. Skills only.

## Development
- Use Bun for any JS/TS work
- Use UV for any Python work (svgutils composition, icon generation, figure QA)
- Prefer uvx/bunx for on-the-fly execution
- Each plugin has independent versioning in its own plugin.json
- No mocks in tests
- No emojis in commits or code

## Cross-agent compatibility
- Keep shared project and marketplace instructions in AGENTS.md.
- Keep CLAUDE.md as `@AGENTS.md`, followed only by Claude Code-specific additions.
- Prefer shared `skills/*/SKILL.md` directories across Claude Code, Codex, and Copilot CLI. Keep `agents/*` declared only in manifests for agents that support them.
