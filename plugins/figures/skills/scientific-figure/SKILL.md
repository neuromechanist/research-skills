---
name: scientific-figure
description: This skill should be used when the user asks to "create a figure", "make a scientific figure", "create a paper figure", "make a figure for my paper", "make a figure for my manuscript", "compose figure panels", "assemble figure panels", "combine figure panels", "make a multi-panel figure", "figure composition", "export a figure", "generate a PDF figure", "create a Nature-style figure", "make a journal figure", "make a publication figure", or "create a figure for my grant". The skill composes multi-panel figures at exact journal dimensions (Nature 89/183 mm, Science 55/120 mm, Cell 85/174 mm, PNAS 87/180 mm) using svgutils, validates font sizes against journal minima before export, and writes PDF/PNG via Inkscape when available or cairosvg otherwise.
version: 0.1.0
---

# Scientific Figure

Compose publication-quality multi-panel figures at exact journal dimensions (mm/pt), validate font sizes against journal minima before export, and write PDF/PNG that the journal will accept without resize.

## Why this skill exists

The previous react-pdf workflow had two structural failures:

1. **Composition did not respect physical size.** Flexbox layout shifted dimensions in subtle ways during render.
2. **Fonts shrank below readable thresholds.** When content overflowed, react-pdf uniformly scaled the entire figure, sometimes pushing axis labels under 4 pt.

This skill replaces that workflow. Panels are placed at exact mm coordinates, text is preserved as SVG `<text>` elements so font sizes are inspectable before export, and the validator rescales individual panels rather than the whole figure when a font minimum is violated.

## Pipeline

```
1. Plan        2. Build elements        3. Compose          4. Validate fonts     5. Export
   (journal      (matplotlib/seaborn      (svgutils, at        (per-element pt vs    (Inkscape if
    size, panel   per panel; SVG out;     exact mm/pt;         journal minimum;      present;
    grid)         optional icons)         text preserved)      rescale panel if      cairosvg
                                                               below minimum)        otherwise)
```

Every step uses on-the-fly execution via `uv run --with` so no permanent installs are required for the skill itself.

## Step 1: Plan the figure

Before generating anything, fix the following:

- **Target journal** — sets the canvas width. See `references/journal-specs.md` for the full table; the four most common are summarized below.
- **Panel grid** — 1x1, 1x2, 2x2, wide-top + sub-panels, or freeform mm coordinates.
- **Color palette** — pick from `references/color-palettes.md` and reuse across all panels.

### Journal width / font minimum cheat sheet

| Journal | 1 column | 2 column | Min body font | Notes |
|---|---|---|---|---|
| Nature | 89 mm | 183 mm | 5 pt | 8 pt for panel labels |
| Science | 55 mm | 120 mm | 6 pt | Myriad/Helvetica preferred |
| Cell | 85 or 112 mm | 174 mm | 6 pt | Max 225 mm tall |
| PNAS | 87 mm | 180 mm | 6 pt | No label below 2 mm tall |

The validator in step 4 enforces these. Pick the journal early so the validator can warn early.

## Step 2: Build the elements

Each panel is generated independently as an SVG. Common sources:

- **Plots:** matplotlib/seaborn, saved with `bbox_inches='tight', transparent=True, format='svg'`. See the `figures:plot-styling` skill for the library decision tree and SciencePlots recipes.
- **Icons:** transparent PNGs from the `figures:transparent-icons` skill.
- **Schematics:** for new Python-driven work use `figures:svg-primitives` (auto-fit boxes, validated arrows, layered z-order); for hand-authored SVG patterns see `figures:svg-figure`.

Save each element to a working directory (typically `panels/`), then compose them in step 3.

## Step 3: Compose the figure

The composer is built around [svgutils](https://svgutils.readthedocs.io/) (MIT license; `uv run --with svgutils`). It places panels at exact mm coordinates and preserves text as inspectable SVG `<text>` elements.

Two ways to compose: the `Figure` helper in `scripts/compose.py` (most cases) and direct `svgutils.compose` for full control.

### Recipe A: helper (recommended)

```bash
uv run --with svgutils --with lxml python scripts/compose.py panels-config.json -o figure.svg
```

`panels-config.json` schema:

```json
{
  "width_mm": 183,
  "height_mm": 120,
  "journal": "nature",
  "panels": [
    {"id": "A", "src": "panels/spectrum.svg", "x_mm": 0,  "y_mm": 0, "scale": 0.5, "label": "A"},
    {"id": "B", "src": "panels/topomap.svg",  "x_mm": 92, "y_mm": 0, "scale": 0.5, "label": "B"},
    {"id": "C", "src": "panels/timecourse.svg", "x_mm": 0, "y_mm": 60, "scale": 1.0, "label": "C", "width_mm": 183}
  ]
}
```

Panel labels (A, B, C) are placed at top-left of each panel in 12 pt bold sans-serif.

### Recipe B: direct svgutils (full control)

```python
from svgutils.compose import Figure, SVG, Panel, Text

fig = Figure(
    "183mm", "120mm",
    Panel(
        SVG("panels/spectrum.svg").scale(0.5),
        Text("A", 5, 15, size=12, weight="bold"),
    ).move(0, 0),
    Panel(
        SVG("panels/topomap.svg").scale(0.5),
        Text("B", 5, 15, size=12, weight="bold"),
    ).move(92, 0),
)
fig.save("figure.svg")
```

See `references/composition-workflow.md` for the patterns (panel scaling, label placement, scale bars, multi-panel grid utilities).

## Step 4: Validate fonts before export

This is the step that prevents the journal-rejection scenario. Run:

```bash
uv run --with lxml python scripts/validate_fonts.py figure.svg --journal nature
```

The validator parses every `<text>` and `<tspan>` element with a `font-size`, walks the accumulated transform stack to compute the effective font size at the final physical dimensions, and reports anything below the journal minimum. Output is JSON:

```json
{
  "svg": "figure.svg",
  "journal": "nature",
  "minimum_pt": 5.0,
  "checked_count": 47,
  "skipped_count": 0,
  "issue_count": 1,
  "issues": [
    {
      "text": "Frequency (Hz)",
      "specified_pt": 9.0,
      "effective_pt": 4.5,
      "scale_x": 0.5,
      "scale_y": 0.5,
      "minimum_pt": 5.0,
      "tag_id": ""
    }
  ]
}
```

`skipped_count` counts text elements where no `font-size` could be resolved (CSS class selectors, inherited styles). Exit codes: `0` clean, `1` issues found, `2` script error (malformed SVG, missing file).

If a panel is the culprit (its `.scale()` is too small), three remedies:

1. **Rescale that panel up** (and other panels down) instead of accepting the small text.
2. **Increase the source plot's font size** so that even at panel scale 0.5 it still passes (e.g., 12 pt source → 6 pt at 0.5 scale, which passes Science 6 pt minimum).
3. **Switch to a larger canvas** (e.g., upgrade 1-col to 1.5-col).

See `references/font-validation.md` for the full mechanics and rationale.

## Step 5: Export to PDF/PNG

```bash
uv run --with cairosvg python scripts/export.py figure.svg --out figure.pdf --dpi 300
```

`export.py` detects Inkscape on `$PATH` at runtime. When present, Inkscape produces the highest-fidelity PDF (text remains text, fonts subsetted). When absent, the script falls back to cairosvg with a stderr warning that text without an installed font may be converted to paths or skipped.

### Installing Inkscape (one-time, recommended)

```bash
brew install inkscape    # macOS
sudo apt install inkscape # Debian/Ubuntu
```

`brew install inkscape` is a single line and a ~200 MB one-time cost; once installed the script auto-detects it. The cairosvg fallback works without Inkscape but produces lower-fidelity PDFs when journal-required fonts are not installed.

## Caption guidelines

Generate a figure caption that:

- Starts with a concise title (bold, one sentence).
- Describes each panel: "(A) Description. (B) Description. (C) Description."
- Defines all abbreviations on first use (e.g., "electroencephalography (EEG)").
- States sample sizes, statistical tests, and error bar meanings.
- States scale bar values if present.

## Quality assurance

The `figures:figure-qa` agent proactively runs on the composed SVG to check geometric correctness, alignment, color-palette compliance, and label legibility. The agent invokes `validate_fonts.py` for the font-size pass under the hood and the SVG branch's palette and geometry checks alongside.

## Additional resources

- `references/composition-workflow.md` — svgutils patterns and idioms
- `references/font-validation.md` — pt minimum mechanics, transform-stack math
- `references/journal-specs.md` — full table of journal dimensions and font rules
- `references/color-palettes.md` — colorblind-safe palettes (Wong, Okabe-Ito, viridis, Crameri)
- `scripts/compose.py` — svgutils composer (CLI + library)
- `scripts/validate_fonts.py` — font-size validator
- `scripts/export.py` — Inkscape/cairosvg exporter
- `examples/two-column-figure.py` — end-to-end working example (matplotlib panels → compose → validate → export)
