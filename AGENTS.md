# Research Skills Marketplace

## Purpose
Cross-agent marketplace providing plugins and skills for academic research workflows and development tooling: literature search and review, grant writing and review, manuscript preparation, figures, presentations, project lifecycle management, neuroinformatics, and cloud GPU provisioning for model training.

## Skills-first model
This marketplace follows a skills-first surface. Skills auto-trigger from natural-language intent (description matching). Commands are kept only for workflows that need explicit `/command args` orchestration: project init, epic/sprint management, version bumps. Thin command wrappers around skills have been removed; do not reintroduce them.

## Marketplace Structure
```
research-skills/
├── .claude-plugin/marketplace.json  # Claude Code marketplace manifest; legacy-compatible for Codex/Copilot
├── .agents/plugins/marketplace.json # Native Codex repo marketplace manifest
├── .github/plugin/marketplace.json  # Native Copilot CLI marketplace manifest
├── plugins/
│   ├── project/                      # Project lifecycle toolkit
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── .github/plugin/plugin.json
│   │   ├── commands/{init-project,update-rules,epic-dev,epic-status,release-prep}.md
│   │   ├── skills/{init-project,update-rules,install-user-instructions,workflow-reference,epic-dev,pr-review-toolkit,codebase-onboarding,implementation-planning,engineering-loop,debugging,agent-fanout,ci-scaffolding,docker-packaging,security-audit,document-processing}/
│   │   ├── agents/{dependency-auditor,release-prep,pr-review-toolkit}.md
│   │   ├── agents/templates/pr-review-toolkit.{toml,agent.md}
│   │   ├── templates/               # AGENTS, Claude, Cursor, context, config, CI/CD
│   │   └── bin/                     # project-init-templates, project-diff-rules, project-templates-path
│   ├── grant/                        # Grant proposal toolkit
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── .github/plugin/plugin.json
│   │   ├── skills/{grant-writing,grant-review,grant-figure-qa}/
│   │   ├── agents/{grant-figure-qa,grant-review}.md
│   │   └── agents/templates/{grant-review,grant-figure-qa}.{toml,agent.md}
│   ├── manuscript/                   # Academic manuscript toolkit
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── .github/plugin/plugin.json
│   │   ├── skills/{paper-review,manuscript-writing,manuscript-formatting,lit-review,humanizer}/
│   │   ├── agents/paper-review.md
│   │   └── agents/templates/paper-review.{toml,agent.md}
│   ├── opencite/                     # Literature search and citation management
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── .github/plugin/plugin.json
│   │   └── skills/opencite/
│   ├── figures/                      # Publication-quality figures (v0.11.0)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── .github/plugin/plugin.json
│   │   ├── skills/{scientific-figure,transparent-icons,svg-figure,svg-primitives,ai-full-figure,plot-styling,figure-qa}/
│   │   ├── agents/figure-qa.md + figure-qa-scripts/{check_svg,check_raster,check_plot_script}.py
│   │   └── agents/templates/figure-qa.{toml,agent.md}
│   ├── presentation/                 # Interactive slide decks
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── .github/plugin/plugin.json
│   │   └── skills/presentation-builder/
│   ├── neuroinformatics/             # Neuro data standards + experiments
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── .github/plugin/plugin.json
│   │   ├── skills/{bids-conversion,experiment-design}/
│   │   └── agents/bids-validator.md + agents/templates/bids-validator.{toml,agent.md}
│   └── ml-training/                  # Cloud GPU provisioning for training/benchmarks
│       ├── .claude-plugin/plugin.json
│       ├── .codex-plugin/plugin.json
│       ├── .github/plugin/plugin.json
│       └── skills/runpod/ + references/ + templates/
└── .context/
    └── plan.md
```

## Plugins
- **project** (v0.6.0): Project lifecycle toolkit with initialization, cross-agent user-instruction installation, rule/config updates, epic/sprint workflow, PR review toolkit, CI/CD scaffolding, Docker packaging, security audit, and document processing. Commands: `/init-project`, `/update-rules`, `/epic-dev`, `/epic-status`, `/release-prep`. `install-user-instructions` configures Claude Code, Codex, Copilot CLI, and Cursor at their supported user surfaces without duplicating general rules downstream. Model routing keeps design, observation, supervision, and synthesis on Claude Fable/Opus or Codex Sol; uses Codex Terra for approved phase-plan elaboration; and delegates detailed implementation to Claude Sonnet or Codex Luna with mechanical gates. Completed one-off agents must be closed/removed after their reports are incorporated. GitHub issue and PR bodies keep each paragraph on one source line, while semantic line breaks remain the default elsewhere.
- **grant** (v0.3.6): NIH/NSF grant proposal writing, structured review with scoring criteria, and figure quality assurance. The `grant-review` NIH rubric follows the three-factor Simplified Review Framework (NOT-OD-24-010) for RPG mechanisms (Factor 1 Importance and Factor 2 Rigor & Feasibility scored 1-9; Factor 3 Expertise & Resources assessed, not scored); F fellowships (NOT-OD-24-107) and T training grants (NOT-OD-24-129) have their own separately revised frameworks, and K scored criteria are unchanged for 2025, so K/F/T stay out of the RPG three-factor structure. Cross-references `manuscript:humanizer` from grant-writing and grant-review for natural-writing passes. Both review surfaces follow the review-subagent pattern (epic #61): `grant-review` and `grant-figure-qa` are thin dispatch skills with Claude-bundled fresh-context agents, Codex templates, Copilot plugin-agent templates, and inline fallback through the same `references/` procedures when no configured subagent is available.
- **manuscript** (v0.5.2): Literature review (multi-phase citation-traceable corpus protocol + single-pass thematic synthesis), peer review, writing guidance, journal-specific formatting for submission, and the `humanizer` skill for a final natural-writing pass (adapted from [blader/humanizer](https://github.com/blader/humanizer), MIT, Siqi Chen). `paper-review` follows the same pattern: thin dispatch skill, Claude-bundled fresh-context agent, Codex template, Copilot plugin-agent template, and inline fallback through `references/`.
- **opencite** (v0.3.2): Academic literature search, citation management, PDF retrieval, identifier conversion, and BibTeX export. Skills only. (Single-pass literature-review synthesis moved to `manuscript:lit-review`.)
- **figures** (v0.11.0): Replaces the retired `scientific-figures` plugin. Active skills: `scientific-figure` (svgutils-based programmatic composition at exact mm/pt dimensions with pre-export font-size validation against Nature/Science/Cell/PNAS minima; runtime-detected Inkscape exporter with cairosvg fallback); `transparent-icons` (flat scientific icons via Codex CLI image_gen by default, OpenAI Images API fallback, with Pillow-threshold or opt-in rembg+BiRefNet transparency post-process, theme.json bible shared with ai-full-figure); `svg-figure` (hand-authoring conventions and the SVG-spec reference for figure-qa; recommends `svg-primitives` for new programmatic work; ships an editor-handoff reference covering Illustrator/Affinity SVG import behavior, editable-master authoring rules, and print-PDF derivation, plus scripts/editor_prep.py, an idempotent handoff pass that bakes markers, resolves text anchors via font metrics, flattens nested viewports, and inlines SVG data URIs on any SVG); `svg-primitives` (mm-precise SVG builder in Python on drawsvg + svgpathtools + fontTools; auto-fits text boxes from measured font metrics, snaps arrow endpoints to box edges via path intersection, emits `<marker orient='auto'>` for tangent-correct arrowheads on curves, and uses named layers for deterministic paint order; ships an E2E pytest suite that asserts text containment, arrow-tip distance, and layer paint order on rendered SVGs); `ai-full-figure` (AI-generated pictorial substrate via Codex CLI or OpenAI Images API plus programmatic label/arrow/scale-bar overlay producing a composable SVG; hard-ceiling rules route complex figures back to `scientific-figure` or `svg-figure`); `plot-styling` (library decision tree across matplotlib / seaborn / plotnine / plotly / PyVista with SciencePlots recipes for Nature, IEEE, Science, Cell, PNAS, and APS). `figure-qa` follows the review-subagent pattern: thin dispatch skill, Claude-bundled fresh-context QA agent, Codex template, Copilot plugin-agent template, inline fallback, SVG/raster/plot-script/composed-figure branches, and helper scripts at `agents/figure-qa-scripts/check_{svg,raster,plot_script}.py` with strict programmatic-vs-VLM separation.
- **presentation** (v0.2.4): Interactive Reveal.js presentations from JSON via the Agentic Presentation Builder. The skill runs the engine through its `apb` CLI (`bunx`/`npx github:neuromechanist/agentic-presentation-builder#<tag> validate|present|export`, or a managed cache clone for iterative authoring) instead of a hardcoded local path, and ships a `references/course-style.md` house-style guide (incremental bullet animations, code sections, two-column image layouts, callouts, title block) distilled from the Open Science Collective (OSC) Agentic Research Course decks. Skills only.
- **neuroinformatics** (v0.2.4): Neuroscience data standards (BIDS, HED), experiment design (PsychoPy, LSL), and dataset validation. Skills plus a Claude-bundled BIDS validator agent, a Codex template, and a Copilot plugin-agent template.
- **ml-training** (v0.1.0): Cloud GPU provisioning for training, distillation, benchmark grids, and short-lived serving. The `runpod` skill is the prebaked-image workflow: every install, download, and compile happens once in a locally built container image, so boot-to-verified is 16 s on a warm host and 64 s on a cold host (1.9 GB pull) instead of the 8-10 min a stock image spends on pod-side installs (measured 2026-08-12, RunPod secure cloud). Ships parameterized lifecycle templates (`Dockerfile`, `start.sh`, `pod-up.sh`, `pod-run.sh`, `pod-down.sh`) with stage markers and detached `tmux` runs, plus three references: the provisioning pitfall catalog (glibc/base-image mismatch, `ssh` not inheriting Docker `ENV`, no auto-injected key on REST-created pods, `rsync` chown failures, broken host pools, fire-and-forget launches), GPU selection (GraphQL stock queries, the non-monotonic pricing ladder, the single-card to multi-node scale ladder), and job execution (sync, detach, verify, fetch, terminate). Skills only.

## Development
- Detailed project rules live in `.rules/`; check the relevant rule file before
  changing manifests, skills, agents, tests, CI, or language tooling.
- Use Bun for any JS/TS work. See `.rules/javascript.md`.
- Use UV for any Python work (svgutils composition, icon generation, figure QA).
  See `.rules/python.md`.
- Each plugin has independent versioning in its own plugin.json
- No mocks in tests. See `.rules/testing.md`.
- No emojis in commits or code. See `.rules/git.md`.

## Releases & Citation
- The marketplace version lives in `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json` (the Codex `.agents/plugins/marketplace.json` carries no top-level version).
- The repository is archived to Zenodo on every GitHub release, minting a versioned DOI under a stable concept DOI. When you bump the marketplace version for a release, also bump `version` (and `date-released`) in `CITATION.cff` and keep `.zenodo.json` in sync, then tag `vX.Y.Z` and create the GitHub release.
- The concept DOI, added to `CITATION.cff` (`doi:`) and the README badge after the first Zenodo deposit, is stable across versions and does not change.

## Cross-agent compatibility
- Keep shared project and marketplace instructions in AGENTS.md; detailed
  cross-agent update rules live in `.rules/cross-agent-compatibility.md`.
- Keep CLAUDE.md as `@AGENTS.md`, followed only by Claude Code-specific additions.
- Any plugin update must check Claude Code, Codex, and GitHub Copilot CLI
  manifests and install surfaces together.
- Prefer shared `skills/*/SKILL.md` directories for portable capabilities; keep
  tool-specific agent shells thin and backed by shared `references/`.
