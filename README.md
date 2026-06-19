# Research Skills

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20696515.svg)](https://doi.org/10.5281/zenodo.20696515)

Cross-agent marketplace for academic research workflows and development tooling. Install individual plugins for literature search, grant proposals, manuscript preparation, figures, presentations, project lifecycle management, and neuroinformatics.

## Install

### Claude Code

In Claude Code, type `/plugin`, select **Add marketplace**, enter:

```
neuromechanist/research-skills
```

Then select which plugins to install. Each plugin is independent.

Install all plugins via CLI:

```bash
claude plugin marketplace add neuromechanist/research-skills
for p in project grant manuscript opencite figures presentation neuroinformatics; do
  claude plugin install "$p@research-skills"
done
```

### Codex

Codex can use the native repo marketplace at `.agents/plugins/marketplace.json`; the Claude-compatible `.claude-plugin/marketplace.json` remains for legacy-compatible installs.

```bash
codex plugin marketplace add neuromechanist/research-skills
codex plugin marketplace add ./path/to/research-skills
```

Each plugin also has a native `.codex-plugin/plugin.json` manifest. Then open `/plugins` in Codex and install the plugins you need.

### GitHub Copilot CLI

Copilot CLI can use the native marketplace at `.github/plugin/marketplace.json`. Each plugin also has a native `.github/plugin/plugin.json` manifest.

```bash
copilot plugin marketplace add neuromechanist/research-skills
copilot plugin marketplace browse research-skills
copilot plugin install project@research-skills
```

See [docs/cross-agent-compatibility.md](docs/cross-agent-compatibility.md) for the researched registration paths and source links.

## Plugins

Skills auto-trigger on user intent (described per-plugin below). Slash commands are reserved for workflows that need explicit orchestration entry points.

| Plugin | Version | Description | Skills | Commands |
|--------|---------|-------------|--------|----------|
| **project** | 0.4.2 | Project lifecycle: init (with ADR scaffold and optional GitHub labels), rule/config updates, epic workflow, PR review, CI/CD, Docker, security, doc-processing | `init-project`, `update-rules`, `workflow-reference`, `epic-dev`, `pr-review-toolkit`, `ci-scaffolding`, `docker-packaging`, `security-audit`, `document-processing` | `/init-project`, `/update-rules`, `/epic-dev`, `/epic-status`, `/release-prep` |
| **grant** | 0.3.6 | NIH/NSF grant proposal writing, review, and figure QA | `grant-writing`, `grant-review`, `grant-figure-qa` | -- |
| **manuscript** | 0.5.2 | Academic manuscript multi-phase + single-pass lit review, peer review, writing, journal formatting, and humanizer pass | `lit-review`, `paper-review`, `manuscript-writing`, `manuscript-formatting`, `humanizer` | -- |
| **opencite** | 0.3.2 | Literature search, citation management, PDF retrieval | `opencite` | -- |
| **figures** | 0.10.5 | Publication-quality figures plugin (seven skills + QA agent) | `scientific-figure`, `transparent-icons`, `svg-figure`, `svg-primitives`, `ai-full-figure`, `plot-styling`, `figure-qa` | -- |
| **presentation** | 0.2.4 | Interactive Reveal.js presentations from JSON | `presentation-builder` | -- |
| **neuroinformatics** | 0.2.4 | BIDS conversion/validation, HED annotation, PsychoPy experiment design | `bids-conversion`, `experiment-design` | -- |

## Research Plugins

### opencite

Search academic literature, explore citation graphs, download PDFs, and export BibTeX. Wraps the [`opencite`](https://github.com/neuromechanist/opencite) CLI, aggregating Semantic Scholar, OpenAlex, PubMed, arXiv, and bioRxiv.

```
"Find the top 10 most cited papers on brain-computer interfaces"
"Look up DOI 10.1038/nature12373 and download the PDF"
"Convert this PDF to markdown"
```

### grant

Draft and review NIH and NSF grant proposals with mechanism-specific templates (R01, R21, K99, CAREER, etc.). Includes a `grant-figure-qa` skill that checks figures for resolution, accessibility, and NIH/NSF compliance. As of epic #61, `grant-review` and `grant-figure-qa` use thin-dispatch skills with Claude-bundled fresh-context agents, Codex agent templates, and Copilot plugin-agent templates; when those agents are not configured, the skills run the same reference procedure inline. Skills for research strategy guidelines, writing style, budget justification, scoring criteria, and resubmission response.

```
"Write the significance section for an R01 on motor cortex"
"Review my R21 proposal at proposal.pdf as an NIH study section"
```

### manuscript

Academic manuscript toolkit covering the full lifecycle: literature review (both multi-phase citation-traceable corpus protocol and single-pass thematic synthesis), writing guidance (IMRAD structure, section templates), peer review (methodology, statistics, reproducibility), and journal-specific formatting (IEEE, Nature, PNAS, Elsevier, LaTeX/BibTeX management). Includes revision response templates. As of epic #61, `paper-review` is a thin-dispatch skill with a Claude-bundled fresh-context agent, a Codex agent template, and a Copilot plugin-agent template; when those agents are not configured, the skill runs the same reference procedure inline.

The `manuscript:lit-review` skill covers two modes: a rigorous, iterable, citation-traceable multi-phase workflow where every claim in a direction paper links back to a paper-card on disk, plus an express single-pass synthesis pipeline for writing an Introduction or Background section. The multi-phase workflow can delegate phase orchestration (epic issue, sub-issues, worktrees, state file) to `project:epic-dev` for git-tracked reviews.

```
"Review this manuscript at paper.pdf as a peer reviewer"
"Format my paper for Nature Neuroscience"
"Start a multi-phase lit review on EEG-based BCIs with strands tools, data, science"
"Write a single-pass literature review on motor cortex oscillations"
```

### figures

Publication-quality figures plugin (Nature, Science, PNAS, Cell, and other journals). v0.10.5 adds native Copilot plugin metadata for the QA agent template. v0.10.4 makes `validate_fonts.py` viewBox-aware so it reports the physical point size (a bare font-size in an mm-viewBox is mm, not pt), which lets svg-primitives output pass figure-qa's font check, and completes the svg-figure examples migration to svg-primitives (issue [#52](https://github.com/neuromechanist/research-skills/issues/52)). v0.10.3 implements the `figure-qa` SVG-branch geometry section (text-overflow, arrow-tip-to-target, sibling bbox-overlap; issue [#47](https://github.com/neuromechanist/research-skills/issues/47)). v0.10.2 makes `figure-qa` a cross-agent thin-dispatch skill over the existing QA agent (epic [#61](https://github.com/neuromechanist/research-skills/issues/61)). v0.10.1 closed epics [#31](https://github.com/neuromechanist/research-skills/issues/31) (plugin redesign) and [#48](https://github.com/neuromechanist/research-skills/issues/48) (svg-primitives): seven skills and the unified QA agent.

- `scientific-figure` skill — svgutils-based composer that places panels at exact mm coordinates and preserves text as SVG `<text>` elements so font sizes are inspectable. `validate_fonts.py` walks the transform stack and folds in the root width/viewBox scale to report the physical point size (a bare font-size in an mm-viewBox is mm, not pt; explicit units are absolute), flagging anything below the journal minimum (Nature 5 pt, Science/Cell/PNAS 6 pt). `export.py` detects Inkscape on `$PATH` and uses it when present, falling back to cairosvg. End-to-end example: `examples/two-column-figure.py`.
- `transparent-icons` skill — flat scientific icons (brain, neuron, EEG cap, DNA, etc.) via the Codex CLI `image_gen` tool (preferred when `codex login` is configured) or the OpenAI Images API (fallback). Transparency post-process: fast Pillow threshold by default or opt-in `rembg` + BiRefNet for cleaner edges on complex foregrounds. Shares a `theme.json` schema with the `ai-full-figure` skill for cross-skill style consistency.
- `svg-figure` skill — hand-authoring conventions for SVG schematics and the SVG-spec reference for `figure-qa`. Reference docs cover element-consistency rules, arrow patterns with proper marker geometry, text alignment with bbox arithmetic, and palette compliance (with near-gray exemption for axis chrome). For new Python-driven schematics, prefer `svg-primitives` instead — `svg-figure`'s SKILL.md leads with that recommendation and each pattern carries a "done automatically by svg-primitives" callout.
- `svg-primitives` skill — mm-precise SVG builder in Python on drawsvg + svgpathtools + fontTools. Auto-fits text boxes from measured font metrics, snaps arrow endpoints to box edges via path intersection, emits `<marker orient='auto'>` for tangent-correct arrowheads on straight/cubic/orthogonal/multi-waypoint paths, and uses named layers for deterministic paint order. In-process validation via `Canvas.save(validate='warn'|'strict'|'off')` and `Canvas.validate()` runs four checks (text-overflow, arrow-tip-distance, marker-orient, sibling-overlap). Ships `LabeledBox`, `Pill`, `Diamond`, `Arrow.connect`, `Bracket`, `Annotation`, `Group`, `Shape` Protocol, and a 68-test E2E suite asserting the invariants on rendered SVGs.
- `ai-full-figure` skill — AI-generated pictorial substrate via Codex CLI or OpenAI Images API, plus programmatic label / arrow / scale-bar overlay producing a composable SVG. The substrate-only rule keeps the model from hallucinating labels; the overlay step places text deterministically. Hard-ceiling rules route figures that need data plots, equations, multi-arrow flows, or more than ~5 labels back to `scientific-figure` or `svg-primitives`. Theme.json bible shared with `transparent-icons`.
- `plot-styling` skill — library decision tree across matplotlib, seaborn, plotnine, plotly, and PyVista, with SciencePlots recipes for Nature, IEEE, Science, Cell, PNAS, and APS journals. End-to-end example `sciplots_panel.py` produces a Nature 1-column panel using `science + nature + bright + no-latex` that passes the `figure-qa` plot-script and SVG branches.
- `figure-qa` skill + agent — a thin dispatch skill (epic #61) that routes to a fresh-context Claude agent when available, with a Codex agent template, a Copilot plugin-agent template, and an inline fallback using the same reference procedure. Type-dispatches across SVG / raster / plot-script / composed-figure inputs. Helper scripts (`check_svg.py`, `check_raster.py`, `check_plot_script.py`) handle programmatic checks (font minima, palette compliance, SVG-branch geometry [text-overflow, arrow-tip-to-target, sibling bbox-overlap], alpha-channel correctness, DPI, library recommendations) with strict separation from VLM rubric scoring (clarity, hierarchy, alignment, palette coherence, journal-fit). Programmatic checks own anything with ground truth; VLM judgment is reserved for "does this look balanced." Complementary to `svg-primitives`' in-process validators: figure-qa validates arbitrary SVGs (including hand-authored ones); svg-primitives validates SVGs it produced, before they hit disk.

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
- **BIDS validator agent** -- autonomously validate datasets, diagnose errors, and apply fixes. Claude has the bundled agent shell, Codex has an agent template, and Copilot exposes the `.agent.md` template through the native plugin manifest.

```
"Convert ./raw-data to BIDS format, modality EEG, task rest"
"Validate the BIDS dataset at ./bids-dataset"
"Design a visual oddball ERP paradigm with 2 conditions"
```

## Development Plugin

### project

Complete project lifecycle toolkit combining initialization, epic/sprint workflow, and CI/CD management:

- **init-project** -- scaffold new projects with AGENTS.md, a Claude Code CLAUDE.md import wrapper, `.rules/`, `.context/`, and config files
- **update-rules** -- non-destructive sync of AGENTS.md, the CLAUDE.md adapter, and `.rules/` against latest templates at user or project level
- **epic-dev** -- Codex-facing entrypoint for the `/epic-dev` multi-phase feature workflow with git worktrees, GitHub issues, and phased PR delivery
- **workflow-reference** -- branch, state-file, worktree, and GitHub command reference for epic/sprint workflows
- **pr-review-toolkit** -- PR and recent-change review across code quality, tests, error handling, comments/docs, type design, and simplification. Inspired by Anthropic's [`pr-review-toolkit`](https://github.com/anthropics/claude-code/tree/main/plugins/pr-review-toolkit) implementation; the upstream plugin README identifies it as MIT licensed. The project skill is an original cross-agent adaptation with shared rubrics in `references/`.
- **CI scaffolding** -- generate GitHub Actions workflows for Python (ruff + pytest) or TypeScript (biome + bun test)
- **Docker packaging** -- multi-stage Dockerfiles with uv/bun, health checks, and security hardening
- **Security audit** -- credential scanning, dependency audit, OWASP checklist, configuration hardening
- **Document processing** -- PDF/image OCR, text extraction, markdown conversion

Includes autonomous agents: **dependency-auditor** (vulnerability scanning), **release-prep** (pre-release validation), and a Claude-bundled **pr-review-toolkit** reviewer. Codex gets an opt-in TOML agent template under `plugins/project/agents/templates/`; Copilot exposes the `.agent.md` template through the native plugin manifest. The skill remains the portable fallback when a fresh-context agent is unavailable.

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
├── .agents/plugins/marketplace.json
├── .github/plugin/marketplace.json
├── plugins/
│   ├── project/                   # Project lifecycle (init, workflow, CI, Docker, security, docs)
│   ├── grant/                     # Grant proposals (writing, review, figure QA)
│   ├── manuscript/                # Manuscripts (review, writing, formatting)
│   ├── opencite/                  # Literature search and citation management
│   ├── figures/                   # Publication-quality figures + QA
│   ├── presentation/             # Interactive Reveal.js slide decks
│   └── neuroinformatics/          # BIDS, HED, experiment design
```

## Requirements

- [Claude Code](https://claude.com/claude-code), [Codex](https://developers.openai.com/codex), or [GitHub Copilot CLI](https://docs.github.com/en/copilot)
- For opencite: `opencite` CLI (`uvx opencite`)
- For icons: OpenAI API key for the OpenAI Images API, or `codex login` for the Codex CLI fallback (preferred). The active `generate_icon.py` uses the latest available OpenAI image model. Optional: `rembg` + `onnxruntime` for the BiRefNet transparency post-process (one-time ~400 MB model download).
- For figure composition: `svgutils` plus an exporter — Inkscape is detected at runtime (`brew install inkscape`) and `cairosvg` is the no-system-deps fallback.
- For figure QA: `lxml`, `svgelements`, `svgpathtools`, `shapely` for the SVG branch; `pillow`, `colorthief` for the raster branch; AST analysis for the plot-script branch (no extra deps).
- For plot styling: matplotlib, seaborn, plotly, plotnine, and SciencePlots via `uv run --with` (on-the-fly).
- For PDF conversion: poppler (`brew install poppler` on macOS)
- For presentations: [agentic-presentation-builder](https://github.com/neuromechanist/agentic-presentation-builder) (local clone)
- For BIDS validation: bids-validator (`bunx bids-validator`)
- For OCR: Mistral API key (optional, tesseract as offline fallback)

## Skills vs commands

Skills are the preferred surface for agent-callable capabilities and auto-trigger from their description in Claude Code, Codex, and Copilot CLI. Commands are kept only for workflows that benefit from explicit `/command args` orchestration (epic/sprint management, project init, version bumps). Each plugin's skills are listed in the table above; describe your task in natural language and the matching skill will load.

## Cross-agent instructions

Use `AGENTS.md` as the shared instruction file. `CLAUDE.md` imports it with `@AGENTS.md`, then leaves room for Claude Code-only plugin, skill, command, or MCP notes. The project plugin's `init-project` workflow now generates that layout for new projects.

## Versioning

- Each plugin has independent versioning in its `plugin.json`
- Adding a new plugin/skill = marketplace minor bump (0.x.0)
- Version bump within an existing plugin = marketplace patch bump (0.x.y)

## Notes

The `opencite` plugin included here is a snapshot of the standalone [`neuromechanist/opencite`](https://github.com/neuromechanist/opencite) plugin. If you have already installed that standalone plugin, do not install it again from this marketplace; having both installed will create duplicate skills.

## License

BSD-3-Clause
