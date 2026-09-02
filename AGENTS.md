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
│   ├── figures/                      # Publication-quality figures (v0.12.0)
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .codex-plugin/plugin.json
│   │   ├── .github/plugin/plugin.json
│   │   ├── skills/{figure-bible,scientific-figure,transparent-icons,svg-figure,svg-primitives,ai-full-figure,plot-styling,figure-qa}/
│   │   ├── lib/{image_backend,prompting,theme}.py + schemas/theme.schema.json + tests/
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
- **project** (v0.6.1): Project lifecycle toolkit with initialization, cross-agent user-instruction installation, rule/config updates, epic/sprint workflow, PR review toolkit, CI/CD scaffolding, Docker packaging, security audit, and document processing. Commands: `/init-project`, `/update-rules`, `/epic-dev`, `/epic-status`, `/release-prep`. `install-user-instructions` configures Claude Code, Codex, Copilot CLI, and Cursor at their supported user surfaces without duplicating general rules downstream. Model routing keeps design, observation, supervision, and synthesis on Claude Fable/Opus or Codex Sol; uses Codex Terra for approved phase-plan elaboration; and delegates detailed implementation to Claude Sonnet or Codex Luna with mechanical gates. Completed one-off agents must be closed/removed after their reports are incorporated. GitHub issue and PR bodies keep each paragraph on one source line, while semantic line breaks remain the default elsewhere.
- **grant** (v0.4.1): NIH/NSF grant proposal writing, structured review with scoring criteria, and figure quality assurance. The `grant-review` NIH rubric follows the three-factor Simplified Review Framework (NOT-OD-24-010) for RPG mechanisms (Factor 1 Importance and Factor 2 Rigor & Feasibility scored 1-9; Factor 3 Expertise & Resources assessed, not scored); F fellowships (NOT-OD-24-107) and T training grants (NOT-OD-24-129) have their own separately revised frameworks, and K scored criteria are unchanged for 2025, so K/F/T stay out of the RPG three-factor structure. Cross-references `manuscript:humanizer` from grant-writing and grant-review for natural-writing passes. Both review surfaces follow the review-subagent pattern (epic #61): `grant-review` and `grant-figure-qa` are thin dispatch skills with Claude-bundled fresh-context agents, Codex templates, Copilot plugin-agent templates, and inline fallback through the same `references/` procedures when no configured subagent is available.
- **manuscript** (v0.5.3): Literature review (multi-phase citation-traceable corpus protocol + single-pass thematic synthesis), peer review, writing guidance, journal-specific formatting for submission, and the `humanizer` skill for a final natural-writing pass (adapted from [blader/humanizer](https://github.com/blader/humanizer), MIT, Siqi Chen). `paper-review` follows the same pattern: thin dispatch skill, Claude-bundled fresh-context agent, Codex template, Copilot plugin-agent template, and inline fallback through `references/`.
- **opencite** (v0.3.2): Academic literature search, citation management, PDF retrieval, identifier conversion, and BibTeX export. Skills only. (Single-pass literature-review synthesis moved to `manuscript:lit-review`.)
- **figures** (v0.12.0): Bible-first, AI-capable figure toolkit. `figure-bible` scaffolds and validates the per-project `figures/theme.json` (palette, typography, text limits, Codex model settings) that every other figures skill and the QA scripts read; `ai-full-figure` renders single panels or whole multi-panel figures with gpt-image-2 through the Codex CLI (default `gpt-5.6-luna` at `xhigh` effort; OpenAI Images API when a key exists) with large verbatim titles and panel letters, generates panels in parallel with reference-image consistency, composes them at journal width, and follows a text ladder (model text for titles and short labels, SVG overlay for dense labels, plot or vector skills for numerals and equations); `transparent-icons` uses the same shared backend (`plugins/figures/lib/image_backend.py`, with `CODEX_BIN` override and a 10 s hang-detecting preflight) and keeps the model's native alpha; `scientific-figure` (svgutils composition with font validation and Inkscape/cairosvg export), `svg-primitives` (mm-precise SVG builder), `svg-figure` (hand-authoring conventions and editor handoff), and `plot-styling` (library decision tree with SciencePlots recipes) are unchanged in role. `figure-qa` follows the review-subagent pattern (`Agent(subagent_type: "figures:figure-qa")`, Codex and Copilot templates, inline fallback); its raster branch now OCRs expected strings and measures their point size, both branches accept `--palette theme.json`, and every report ends with a JSON verdict (`status`, `findings[].action`) that drives the generate, QA, fix loop in `figure-qa/references/iterate-loop.md` (N candidates in parallel, QA in one parallel Sonnet dispatch, one targeted change per iteration, three iterations max).
- **presentation** (v0.2.4): Interactive Reveal.js presentations from JSON via the Agentic Presentation Builder. The skill runs the engine through its `apb` CLI (`bunx`/`npx github:neuromechanist/agentic-presentation-builder#<tag> validate|present|export`, or a managed cache clone for iterative authoring) instead of a hardcoded local path, and ships a `references/course-style.md` house-style guide (incremental bullet animations, code sections, two-column image layouts, callouts, title block) distilled from the Open Science Collective (OSC) Agentic Research Course decks. Skills only.
- **neuroinformatics** (v0.2.4): Neuroscience data standards (BIDS, HED), experiment design (PsychoPy, LSL), and dataset validation. Skills plus a Claude-bundled BIDS validator agent, a Codex template, and a Copilot plugin-agent template.
- **ml-training** (v0.1.0): Cloud GPU provisioning for training, distillation, benchmark grids, and short-lived serving. The `runpod` skill is the prebaked-image workflow: every install, download, and compile happens once in a locally built container image, so boot-to-verified is 16 s on a warm host and 64 s on a cold host (1.9 GB pull) instead of the 8-10 min a stock image spends on pod-side installs (measured 2026-08-12, RunPod secure cloud). Ships parameterized lifecycle templates (`Dockerfile`, `start.sh`, `pod-up.sh`, `pod-run.sh`, `pod-down.sh`) with stage markers and detached `tmux` runs, plus four references: the 19-entry provisioning pitfall catalog (glibc/base-image mismatch, `ssh` not inheriting Docker `ENV`, no auto-injected key on REST-created pods, `rsync` chown failures, broken host pools, fire-and-forget launches, plus three fleet-orchestration traps: stdin-eating `ssh` in loops, zsh not word-splitting command chains, and `pkill -f` killing its own `ssh` session; and two monitoring traps: Python block-buffering stdout under a pipe, and a zero-match `grep` reading as an unreachable pod), GPU selection (GraphQL stock queries, the non-monotonic pricing ladder, the single-card to multi-node scale ladder), job execution (sync, detach, verify, fetch, terminate), and fan-out (independent single-GPU pods rather than multi-node clusters, duration-based slicing, partial-stock queueing, verify-one-then-replicate, retry-with-backoff launchers, fleet monitoring with ETA calibration, reap-on-completion, and startup anatomy). Skills only.

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
