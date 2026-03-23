# Plan

## Current Phase: Marketplace structure

### Plugins Status
| Plugin | Version | Status | Notes |
|--------|---------|--------|-------|
| opencite | 0.1.0 | Migrated from opencite repo | Literature search and citation management |
| grant-writing | 0.1.0 | New | Based on grant-proposals repo's rules and templates |
| scientific-figures | 0.1.0 | New (merged) | Unified from icon-generation + pdf-figures; covers icons, plots, composition, QA |
| grant-review | 0.1.0 | New | NIH/NSF scoring criteria-based review |

### Completed
- Converted from single plugin to marketplace structure
- Merged icon-generation + pdf-figures into scientific-figures
- Added plot element support (matplotlib, seaborn, plotly, ggplot2)
- Added curated color palettes (Wong, Tol, Okabe-Ito, domain-specific)
- Added visual QA feedback loop (PDF to PNG, inspect, iterate)
- All execution via uvx/bunx (no permanent installs)
- Each plugin has independent versioning

## Future Ideas
- Paper writing plugin (full manuscript drafting)
- Poster generation plugin
- Conference abstract plugin
- Data visualization plugin
