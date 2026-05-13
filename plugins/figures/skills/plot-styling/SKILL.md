---
name: plot-styling
description: This skill should be used when the user asks to "plot data", "make a plot for a paper", "make a publication plot", "create a journal-quality plot", "matplotlib for a figure", "use seaborn", "use plotnine", "use ggplot in Python", "improve plot quality", "fix matplotlib defaults", "use SciencePlots", "make a Nature-style plot", "make an IEEE-style plot", "make a paper-ready chart", "which plotting library should I use", or wants guidance on choosing between matplotlib / seaborn / plotnine / plotly / pyvista and applying journal-quality defaults. Produces SVG-output Python scripts whose panels are consumed by the scientific-figure composer.
version: 0.1.0
---

# Plot Styling

Choose the right Python plotting library for the chart type, then apply journal-quality defaults so the panel that comes out of `savefig` is ready for the `[[scientific-figure]]` composer — no manual cleanup, no font-size firefighting, no chart junk.

## Two questions, two minutes

1. **What chart type am I drawing?** That answer picks the library (`references/library-decision-tree.md`).
2. **Which journal am I targeting?** That answer picks the style sheet and font minimum (`references/sciplots-recipes.md`).

Run those choices through the export conventions below and the output SVG should pass `figure-qa`'s plot-script branch and feed `scientific-figure` without scale-down surprises.

## Library decision tree (summary)

| Chart type | Library | Why |
|---|---|---|
| Line / scatter / bar with custom layout | **matplotlib** | Most control; the lingua franca. Pair with SciencePlots styles to fix defaults. |
| Statistical (box, violin, regression, faceted) | **seaborn** | Better defaults than matplotlib; less code for the common cases. Built on top of matplotlib so the SciencePlots style still applies. |
| Grammar-of-graphics / R-style faceting | **plotnine** | Same `geom_*` API as ggplot2 without the rpy2 bridge. |
| Interactive HTML supplement (deck / dashboard) | **plotly** | Use plotly for the interactive companion; ship a matplotlib version for print. |
| 3D / volumetric / mesh | **PyVista** (when interactive matters) or **matplotlib 3d** (for static print) | matplotlib 3d is acceptable for simple panels; PyVista when the figure is the interaction. |
| Already in matplotlib, output looks ugly | **stay matplotlib + SciencePlots** | `plt.style.use(['science', 'nature'])` fixes 80% of "ugly defaults" complaints without rewriting. |

Full decision tree with concrete code snippets per branch: `references/library-decision-tree.md`.

## Journal-quality defaults (matplotlib / seaborn)

The cleanest path is to install [SciencePlots](https://github.com/garrettj403/SciencePlots) and apply its style sheet at the top of every plot script. The relevant style names:

- `science` — base style (sans-serif, no chart junk, tight margins)
- `nature` — Nature column dimensions and font sizing
- `ieee` — IEEE narrow-column with grayscale-safe palette
- `vibrant` / `bright` / `high-contrast` — colorblind-safe palettes from Paul Tol
- `notebook` — slightly larger fonts for screen reading (avoid for paper)

```python
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401  (registers the styles)

plt.style.use(["science", "nature"])
```

For a Nature panel at 1-column width with three lines:

```python
import numpy as np
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401

plt.style.use(["science", "nature"])

fig, ax = plt.subplots(figsize=(3.5, 2.5))  # 89 mm x ~63 mm
t = np.linspace(0, 1, 200)
for k, label in enumerate(("control", "drug A", "drug B")):
    ax.plot(t, np.sin(2 * np.pi * (k + 1) * t), label=label, linewidth=1.0)
ax.set_xlabel("time (s)")
ax.set_ylabel("amplitude (a.u.)")
ax.legend(frameon=False, loc="upper right")
fig.savefig("panel_a.svg", bbox_inches="tight", transparent=True)
```

That single style declaration sets sans-serif fonts at journal-appropriate sizes (Nature 5–7 pt range), removes the right and top spines, applies tight margin defaults, and picks a colorblind-safe palette. See `references/sciplots-recipes.md` for IEEE, Science, and APS variants.

## Export conventions

Every plot panel that will be composed by `[[scientific-figure]]` should:

1. **Save as SVG.** `savefig("panel.svg", ...)`. SVG preserves text as `<text>` so `validate_fonts.py` can inspect every label.
2. **Use `transparent=True`.** The composer expects panels with transparent backgrounds so they composite cleanly onto the figure canvas. `figure-qa`'s plot-script branch flags `transparent=False` and missing-`transparent` as issues.
3. **Use `bbox_inches='tight'`.** Trim whitespace at save time so the panel's bounding box matches its visual extent. The composer's `add_panel(..., scale=...)` math assumes this.
4. **Embed text, not paths.** Default matplotlib SVG output embeds text. If you ever set `svg.fonttype = 'path'`, font validation breaks because there are no `<text>` elements to inspect.
5. **Size the figure in inches to match the final mm panel size.** A Nature 1-column panel is 89 mm = ~3.5 in. `figsize=(3.5, ...)` produces a panel that the composer can place at scale 1.0 with no font-size shrinkage.

The `figure-qa` plot-script branch (`check_plot_script.py`) checks all of these statically from the script's AST. It reports `savefig_not_transparent`, `savefig_missing_bbox_inches`, and any `rcparam_font_sizes` below the journal minimum. See `examples/sciplots_panel.py` for a script that passes the QA branch cleanly.

## When matplotlib defaults bite you

Common matplotlib output failures and the SciencePlots-style fix:

| Failure | Cause | Fix |
|---|---|---|
| Axis labels are 12pt sans-serif by default — fine on screen, oversized for a Nature panel | matplotlib default `font.size` is 10 in the source, scaled to 12 at SVG export | Apply `plt.style.use(['science', 'nature'])` which sets 7 pt body |
| Top and right spines visible | matplotlib default | SciencePlots removes them; or manually `ax.spines[['top','right']].set_visible(False)` |
| Legend has a heavy black frame | matplotlib default | `ax.legend(frameon=False)` |
| Tick marks point inward, hard to read | matplotlib default `xtick.direction = 'in'` | SciencePlots overrides; or `plt.rcParams['xtick.direction'] = 'out'` |
| Color cycle uses default tableau colors (not colorblind-safe) | matplotlib default | SciencePlots' `bright` palette (Paul Tol), or `['#0072B2', '#D55E00', '#009E73', '#CC79A7']` (Okabe-Ito) |
| Tick labels render at different sizes than axis labels | matplotlib defaults differ across rcparams | SciencePlots harmonizes; or set `xtick.labelsize` / `ytick.labelsize` explicitly |
| Saved PNG is at 100 DPI | matplotlib default | `savefig(..., dpi=300)` for raster output; prefer SVG for print |
| Math text uses Computer Modern by default | matplotlib default `text.usetex=False, mathtext.fontset='dejavusans'` | `plt.style.use(['science'])` sets serif math via mathtext; or `text.usetex=True` if you have a LaTeX install |

## Quality assurance

After authoring a plot script, run `[[figure-qa]]`:

```bash
uv run python "$FIGURE_QA_SCRIPTS/check_plot_script.py" panel.py --journal nature
```

The plot-script branch detects the libraries used, reports rcParams font sizes (numeric and dynamic), inspects every `savefig` call, and offers a library-switch recommendation when the chart type would benefit. After running the script for real and producing the SVG, the raster/SVG branches verify the output too.

## Additional resources

- `references/library-decision-tree.md` — full decision tree with concrete snippets per branch (statistical, grammar-of-graphics, interactive, 3D, R-bridge)
- `references/sciplots-recipes.md` — Nature, IEEE, Science, APS style recipes; per-journal font and color setup
- `references/element-plots.md` — original matplotlib / seaborn / plotly / ggplot2 element guide ported from the legacy plugin
- `examples/matplotlib-element.py` — canonical matplotlib panel
- `examples/sciplots_panel.py` — SciencePlots-styled panel passing `figure-qa`'s plot-script branch
