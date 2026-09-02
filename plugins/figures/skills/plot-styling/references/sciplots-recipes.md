# SciencePlots Recipes

Per-journal style recipes built on [SciencePlots](https://github.com/garrettj403/SciencePlots) (`uv run --with scienceplots ...`). Apply at the top of every plot script and the panel will pass `figure-qa`'s plot-script branch and feed `scientific-figure` without scale-down surprises.

## Install on the fly

```bash
uv run --with matplotlib --with scienceplots python panel.py
```

`scienceplots` is imported once with `import scienceplots  # noqa: F401` (the import registers the styles into matplotlib's stylesheet table — flake8 will mark it unused, hence the `noqa`).

## Available style names

| Style | What it does |
|---|---|
| `science` | Base style. Sans-serif fonts, no top/right spines, tight margins, no chart junk. |
| `nature` | Adds Nature-specific font sizes (~7 pt body), narrow tick spacing, Nature column widths. |
| `ieee` | IEEE conference / journal narrow-column. Grayscale-safe palette by default. |
| `aps` | American Physical Society (PRL, PRX, etc.). Times-leaning math. |
| `vibrant` | Paul Tol's "vibrant" colorblind-safe palette. Stack with `science`. |
| `bright` | Paul Tol's "bright" qualitative palette. Stack with `science`. |
| `high-contrast` | Three-color palette for absolute clarity (intended for posters / large screens). |
| `muted` | Tol's muted qualitative palette; for figures with many categories. |
| `retro` | Aesthetic but lower-contrast; for non-academic contexts. |
| `notebook` | Slightly larger fonts for screen reading. Avoid for paper-ready plots. |
| `grid` | Adds light gridlines. Stack with the journal style. |
| `no-latex` | Forces non-LaTeX math rendering. Use when LaTeX is not installed. |

## Recipes by journal

### Nature

```python
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401

plt.style.use(["science", "nature", "no-latex"])
fig, ax = plt.subplots(figsize=(3.5, 2.5))  # 89 mm x ~63 mm (1-column)
# ... plot ...
fig.savefig("panel.svg", bbox_inches="tight", transparent=True)
```

`science + nature` sets `font.size: 7`, `axes.labelsize: 7`, `xtick.labelsize: 6`, `ytick.labelsize: 6`, `legend.fontsize: 6`. All above Nature's 5 pt floor; the validator will be happy.

**Why `no-latex`** — the `science` style enables `text.usetex=True`. When matplotlib renders math via LaTeX it converts every `<text>` element in the SVG output to vector paths, which `validate_fonts.py` cannot inspect (it walks `<text>` elements only). Adding `no-latex` switches to matplotlib's built-in mathtext (no system LaTeX install needed) and preserves text as `<text>`. Drop `no-latex` only when you have real LaTeX math and have verified the font sizes manually.

2-column panel: `figsize=(7.0, 4.0)` (183 mm x ~100 mm).

### Science

```python
plt.style.use(["science", "no-latex"])
plt.rcParams["font.family"] = ["Myriad Pro", "Helvetica", "Arial", "DejaVu Sans"]
plt.rcParams["font.size"] = 7  # Science 6-8 pt range; 7 is a safe middle
fig, ax = plt.subplots(figsize=(3.40, 2.5))  # 86 mm x ~63 mm (1-column, AAAS)
```

Science prefers Myriad Pro. If you don't have it installed, the fallback list keeps the SVG portable.

### Cell

```python
plt.style.use(["science", "no-latex"])
plt.rcParams["font.size"] = 7
fig, ax = plt.subplots(figsize=(3.35, 2.5))  # 85 mm x ~63 mm
```

Cell allows 85 mm 1-column and 114 mm 1.5-column (per scientific-figure's `journal-specs.md`). For 1.5-col, `figsize=(4.49, 3.0)`.

### PNAS

```python
plt.style.use(["science", "no-latex"])
plt.rcParams["font.size"] = 7
fig, ax = plt.subplots(figsize=(3.43, 2.5))  # 87 mm x ~63 mm
```

PNAS allows labels down to 2 mm physical height; SciencePlots' defaults stay above this.

### IEEE

```python
plt.style.use(["science", "ieee", "no-latex"])
fig, ax = plt.subplots(figsize=(3.5, 2.5))
```

IEEE applies a grayscale-safe palette by default — important because IEEE often prints in black-and-white for cost reasons. Test by `plt.style.use(["science", "ieee", "grayscale"])` and verify the chart still differentiates the series.

### APS (PRL, PRX, etc.)

```python
plt.style.use(["science", "aps"])  # APS journals are math-heavy; keep usetex
fig, ax = plt.subplots(figsize=(3.4, 2.5))  # 86 mm x ~63 mm
```

APS journals lean toward Times-style math. APS style preserves SciencePlots' sans-serif body text but routes math through `\mathrm` and serif fonts. APS submissions often use real LaTeX math; if you keep `text.usetex=True` you'll need to verify font sizes manually rather than via `validate_fonts.py` (which sees only `<text>` elements). Use `no-latex` if you can substitute mathtext for the journal's math expressions.

## Stacking color palettes

Append a palette style after the journal style:

```python
plt.style.use(["science", "nature", "bright"])     # Tol bright on top of Nature
plt.style.use(["science", "ieee", "high-contrast"]) # IEEE narrow with high-contrast
```

The journal style's font/size choices win; the palette style overrides the color cycle only.

For Okabe-Ito specifically (not in SciencePlots by default), set explicitly:

```python
plt.rcParams["axes.prop_cycle"] = plt.cycler(color=[
    "#000000", "#E69F00", "#56B4E9", "#009E73",
    "#F0E442", "#0072B2", "#D55E00", "#CC79A7",
])
```

## LaTeX math vs mathtext

By default SciencePlots' `science` style uses LaTeX for math rendering (`text.usetex=True`). This requires a LaTeX install on the system. To use matplotlib's built-in mathtext (no LaTeX needed):

```python
plt.style.use(["science", "no-latex"])
```

Mathtext is a reasonable approximation; the result is slightly less polished but works without LaTeX. For Nature submissions where math is rare, `no-latex` is fine. For physics journals with heavy equations, install LaTeX.

## Common rcParams overrides (when SciencePlots isn't enough)

```python
plt.rcParams.update({
    "axes.linewidth": 0.5,        # default 0.8; thinner for very small panels
    "lines.linewidth": 0.8,       # default 1.5; tighter for many overlaid lines
    "lines.markersize": 3,        # default 6; smaller for dense scatter
    "legend.markerscale": 1.5,    # legend markers larger than plot markers
    "savefig.dpi": 300,           # raster fallback; SVG ignores
    "figure.constrained_layout.use": True,  # newer than tight_layout, fewer edge cases
    "svg.fonttype": "none",       # keep <text> elements — required for validate_fonts.py
})
```

`svg.fonttype = "none"` is the load-bearing one. If matplotlib converts text to paths during SVG export, `validate_fonts.py` cannot inspect anything and the figure ships with no font check. The `examples/sciplots_panel.py` example sets this explicitly; SciencePlots leaves it at matplotlib's default of `"path"` for some styles — override after `plt.style.use`.

## Verifying with figure-qa

```bash
SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/agents/figure-qa-scripts"
[ -d "$SCRIPTS_DIR" ] || SCRIPTS_DIR="$(find . -type d -name figure-qa-scripts -path '*/figures/agents/*' | head -1)"
uv run python "$SCRIPTS_DIR/check_plot_script.py" panel.py --journal nature
```

A well-formed script under SciencePlots produces:

- `libraries_detected: ["matplotlib"]` (plus seaborn/plotnine if applicable)
- `rcparam_font_sizes` shows the journal-appropriate sizes (or empty if SciencePlots set them via style sheet; in that case the static analyzer can't see them but they're applied at runtime)
- `savefig_calls` includes `transparent=True` and `bbox_inches='tight'`
- `library_recommendation: null` (or a sensible switch suggestion)
- `issues: []`

If the script defines font sizes via variables (`SOURCE_FONT_PT = 12`), they appear in `rcparam_font_sizes_skipped` rather than `rcparam_font_sizes` (dynamic values aren't resolved statically). The runtime is correct; the static analyzer just can't see the value.

## When to bail to manual matplotlib

SciencePlots is opinionated. If your figure needs:

- Custom multi-axis layouts (e.g., shared x-axis with offset y-scales)
- Inset axes with their own style
- Non-standard tick locators / formatters
- Custom colormaps (use `cmcrameri` for the Crameri scientific colour maps)

…apply the journal style sheet, *then* override the specific rcparams you need. Avoid resetting back to matplotlib defaults; the style sheet still does most of the work even if you fight it on five rcparams.
