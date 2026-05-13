# Composition Workflow

How to compose multi-panel scientific figures with [svgutils](https://svgutils.readthedocs.io/) at exact mm dimensions.

## Why svgutils

The composer in this skill is built on `svgutils.compose` because it gets three things right that browser-PDF and HTML-flexbox composers do not:

1. **Native mm/pt dimensions.** `Figure("183mm", "120mm", ...)` produces an SVG whose root width/height attributes match the journal column exactly. No browser viewport rounding (Puppeteer/Playwright rounding bugs add ~0.5-1 mm; WeasyPrint has SVG `<symbol>`/`<use>` gaps).
2. **Text preserved as `<text>` elements.** Font sizes are inspectable before export, which is what makes `validate_fonts.py` work.
3. **Per-panel control.** Each panel is its own scaled SVG positioned at known mm coordinates. When a font validation fails, the remedy is to rescale the specific panel, not to uniformly shrink the whole figure.

## The svgutils.compose primitives

```python
from svgutils.compose import Figure, SVG, Panel, Text, Line, Grid
```

| Primitive | Purpose |
|---|---|
| `Figure(width, height, *elements)` | Root container; width/height accept mm/pt/px strings |
| `SVG(path)` | Load an SVG file as an element |
| `Panel(*elements)` | Group elements so they can be moved/scaled together |
| `Text(text, x, y, size, weight, font)` | Inline text element |
| `Line(points, width=1, color="black")` | Decorative line; `points` is a list of `(x, y)` tuples |
| `Grid(dx, dy, size=8)` | Visible grid overlay for layout debugging; `dx`/`dy` are spacings, `size` is text size |

Every primitive inherits the following methods from `svgutils.transform.FigureElement` and returns `self`, so they chain:

- `.scale(x, y=None)` — multiply current scale (compounds with parent panel scale; `y` defaults to `x`)
- `.move(x, y)` — translate
- `.rotate(angle, x=0, y=0)` — rotate around the given pivot
- `.find_id(id)` — locate a sub-element by id

## Recipe 1: two-panel side-by-side (Nature 2-column)

```python
from svgutils.compose import Figure, SVG, Panel, Text

fig = Figure(
    "183mm", "120mm",
    Panel(
        SVG("panels/spectrum.svg").scale(0.5),
        Text("A", 2, 4, size=12, weight="bold"),
    ).move(0, 0),
    Panel(
        SVG("panels/topomap.svg").scale(0.5),
        Text("B", 2, 4, size=12, weight="bold"),
    ).move(92, 0),
)
fig.save("figure.svg")
```

Notes:

- 183 mm total, 92 mm per panel start with ~1 mm gutter; tune to taste.
- Panel labels (A, B) placed 2 mm right and 4 mm down from each panel's origin in 12 pt bold.
- The `0.5` scale assumes the source SVGs are sized 2x the target. If your matplotlib panels are saved at 6 inches wide and you want them at 89 mm in the figure, scale accordingly: `89 mm / (6 in * 25.4 mm/in) ≈ 0.585`.

## Recipe 2: 2x2 grid

```python
import itertools
from svgutils.compose import Figure, SVG, Panel, Text

PANEL_W, PANEL_H, GUTTER = 90.0, 70.0, 3.0
labels = iter("ABCD")
panels = []
for (row, col), src in zip(
    itertools.product(range(2), range(2)),
    ["panels/a.svg", "panels/b.svg", "panels/c.svg", "panels/d.svg"],
):
    label = next(labels)
    panels.append(
        Panel(
            SVG(src).scale(0.5),
            Text(label, 2, 4, size=12, weight="bold"),
        ).move(col * (PANEL_W + GUTTER), row * (PANEL_H + GUTTER))
    )

Figure("183mm", "143mm", *panels).save("grid.svg")
```

## Recipe 3: wide top + two below

```python
from svgutils.compose import Figure, SVG, Panel, Text

fig = Figure(
    "183mm", "120mm",
    Panel(SVG("panels/wide_top.svg").scale(0.75), Text("A", 2, 4, size=12, weight="bold")).move(0, 0),
    Panel(SVG("panels/bottom_left.svg").scale(0.5), Text("B", 2, 4, size=12, weight="bold")).move(0, 65),
    Panel(SVG("panels/bottom_right.svg").scale(0.5), Text("C", 2, 4, size=12, weight="bold")).move(92, 65),
)
fig.save("figure.svg")
```

## Sizing convention

The most reliable workflow is:

1. **Choose the source plot dimensions** to match the final panel size at scale 1.0. For a Nature 1-column panel (89 mm), save matplotlib at `figsize=(89/25.4, 60/25.4)` inches. No scaling needed in compose.
2. **If you must scale** (e.g., shrinking a wider source panel), check the font validator after compose. A 9 pt source font becomes 4.5 pt at scale 0.5, which fails Nature 5 pt and fails Science 6 pt.

Practical font sizes for source plots, by target scale:

| Source font (matplotlib) | Scale 1.0 (Nature passes) | Scale 0.5 (Nature passes) | Scale 0.5 (Science passes) |
|---|---|---|---|
| 7 pt | yes | no (3.5) | no |
| 9 pt | yes | yes (4.5)? | no (4.5) |
| 10 pt | yes | yes | no (5.0) |
| 12 pt | yes | yes (6.0) | yes (6.0) |

Pick source font 10-12 pt by default so you have headroom for shrinkage.

## Scale bars

If a panel needs a scale bar at a known physical length, add it as a `Line` plus `Text` after the SVG:

```python
Panel(
    SVG("panels/microscopy.svg").scale(0.5),
    Line([(2, 60), (12, 60)], width=1.0, color="black"),
    Text("10 μm", 4, 64, size=8),
).move(0, 0)
```

## Debugging layout

Drop in a `Grid` for layout verification:

```python
fig = Figure(
    "183mm", "120mm",
    Grid(10, 10),  # 10mm grid lines
    *panels,
)
```

Remove the grid before final export.

## When to bypass svgutils

For figures with complex annotations (curved arrows, brackets, gradient overlays), build the schematic in the `[[svg-figure]]` skill (Phase 5) and `SVG()`-import the result here as one of the panels. svgutils is a positioning composer, not an SVG editor.

## See also

- `references/font-validation.md` — how `validate_fonts.py` reads the composed SVG
- `references/journal-specs.md` — full table of journal dimensions and font rules
- `references/color-palettes.md` — palette selections for cross-panel consistency
- `scripts/compose.py` — the wrapper around svgutils with a JSON-config CLI
- [svgutils documentation](https://svgutils.readthedocs.io/en/latest/compose.html)
