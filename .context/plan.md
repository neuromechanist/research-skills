# Plan

## Current Phase: Marketplace v0.8.0 — figures plugin redesign (epic #31)

### Plugins Status

| Plugin | Version | Status |
|--------|---------|--------|
| project | 0.3.3 | Stable. Lifecycle toolkit (init, workflow, CI, Docker, security, doc processing). |
| grant | 0.3.4 | Stable. NIH/NSF writing + review + figure QA agent. |
| manuscript | 0.5.0 | Stable. Lit review (multi-phase + single-pass), peer review, writing, formatting, humanizer. |
| opencite | 0.3.1 | Stable. Literature search and citation management. |
| figures | 0.7.0 | **Epic #31 in progress.** Phases 1–5 merged (scaffold, `scientific-figure`, `transparent-icons`, `figure-qa` agent, `svg-figure` schematic skill). Phases 6–7 pending. |
| presentation | 0.2.1 | Stable. Interactive Reveal.js slide decks. |
| neuroinformatics | 0.2.3 | Stable. BIDS, HED, experiment design, bids-validator agent. |

### Active epic: figures plugin redesign (#31)

Multi-phase replacement of `scientific-figures` (v0.2.1, react-pdf based) with a redesigned `figures` plugin built around `svgutils` programmatic composition, type-dispatching `figure-qa` agent, and split-out skills for scientific figures, transparent icons, SVG figures, AI-generated full figures, and plot styling.

- Research: `.context/figures-research.md`
- Design: `.context/figures-design.md`
- Sub-issues: #32 (scaffold), #33 (scientific-figure), #34 (transparent-icons), #35 (figure-qa), #36 (svg-figure), #37 (ai-full-figure), #38 (plot-styling)

### Recent history (summarized)

- Converted from single plugin to marketplace structure (v0.4.0): 7 plugins consolidated to 6 domain-grouped plugins
- Added paper-review, manuscript writing/formatting, init-project, workflow, CI/CD, Docker, security audit, doc-processing
- Added dependency-auditor, release-prep, grant-figure-qa, bids-validator agents
- Added literature-review skill to opencite, then moved single-pass synthesis into manuscript:lit-review (v0.5.0)
- Added neuroinformatics plugin (BIDS, experiment design)
- Added humanizer skill in manuscript (v0.5.0, PR #30)

## Future Ideas

- Poster generation plugin
- Conference abstract plugin
- HED annotation skills in neuroinformatics (hedit integration)
- OpenNeuro/NEMAR upload workflows in neuroinformatics
