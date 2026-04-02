# Plan

## Current Phase: Marketplace v0.4.0 - Domain-grouped plugins

### Plugins Status
| Plugin | Version | Status | Notes |
|--------|---------|--------|-------|
| project | 0.2.0 | Merged init-project + workflow + new | Project lifecycle: init, workflow, CI, Docker, security, doc-processing |
| grant | 0.2.0 | Merged grant-writing + grant-review | Grant proposals: writing, review, figure QA agent |
| manuscript | 0.2.0 | Merged paper-review + new | Manuscripts: peer review, writing, formatting |
| opencite | 0.2.0 | Updated | Literature search + new literature-review skill |
| scientific-figures | 0.1.1 | Unchanged | Icons, plots, composition, QA |
| neuroinformatics | 0.1.0 | New | BIDS, HED, experiment design, bids-validator agent |

### Completed
- Converted from single plugin to marketplace structure
- Merged icon-generation + pdf-figures into scientific-figures
- Added plot element support (matplotlib, seaborn, plotly, ggplot2)
- Added curated color palettes (Wong, Tol, Okabe-Ito, domain-specific)
- Added visual QA feedback loop (PDF to PNG, inspect, iterate)
- All execution via uvx/bunx (no permanent installs)
- Each plugin has independent versioning
- Restructured 7 plugins into 6 domain-grouped plugins (v0.4.0)
- Added paper-review, manuscript writing/formatting, init-project, workflow
- Added CI/CD, Docker, security audit, doc-processing skills
- Added dependency-auditor, release-prep, grant-figure-qa, bids-validator agents
- Added literature-review skill to opencite
- Created neuroinformatics plugin (BIDS, experiment design)

## Future Ideas
- Poster generation plugin
- Conference abstract plugin
- HED annotation skills in neuroinformatics (hedit integration)
- OpenNeuro/NEMAR upload workflows in neuroinformatics
