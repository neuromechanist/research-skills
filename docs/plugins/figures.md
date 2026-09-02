# Figures

The `figures` plugin composes publication-quality figures at exact journal dimensions (Nature, Science, PNAS, Cell, and others) and QAs them before they go anywhere near a submission.

## The figure pipeline

A figure moves through five steps, each with its own mechanical defense against the most common failure at that step, and a boomerang from validation straight back to building when a font fails:

![Figure pipeline: Plan, Build, Compose, Validate, Export, with a boomerang from Validate back to Build on font failure](../assets/diagrams/figures-pipeline.svg)

1. **Plan**: journal, size, panel grid, and the bible. `figure-bible` scaffolds and validates one `figures/theme.json` per project (palette, typography, text limits, Codex model settings) that every other skill and the QA scripts read
2. **Build**: `plot-styling` for data plots, `svg-figure`/`svg-primitives` for schematics, `transparent-icons` for icons, or `ai-full-figure` for single panels and whole multi-panel figures rendered by gpt-image-2 through the Codex CLI, with large verbatim titles and panel letters
3. **Compose**: `svgutils` places panels at exact mm coordinates, with text preserved as inspectable `<text>` elements
4. **Validate**: `validate_fonts.py` reports the effective point size against the journal minimum
5. **Export**: Inkscape when available on `$PATH`, `cairosvg` fallback otherwise

When the validator fails, the fix is mechanical: rescale the panel up, increase the source point size, or widen the canvas, not a redesign.

## The plugin map

The plugin is a composer at the center, four element-builder skills that feed it, and a QA agent that runs on every figure regardless of how it was built:

![Figures plugin map: scientific-figure composer at the center, fed by plot-styling, svg-figure, transparent-icons, and ai-full-figure, with figure-qa running on every output](../assets/diagrams/figures-plugin-map.svg)

## How figure-qa decides what to check

`figure-qa` dispatches on input type, runs the matching deterministic check script, then always adds a VLM aesthetic pass on top:

![Figure QA dispatch: detects SVG, raster, plot-script, or composed-figure-directory input, runs the matching check script, then a VLM aesthetic pass on every input type](../assets/diagrams/figure-qa-dispatch.svg)

- **SVG** → `check_svg.py` (bbox / arrow-tip-to-target / point size / palette against the theme)
- **Raster** (PNG/JPG/TIFF) → `check_raster.py` (DPI / alpha channel / palette against the theme / OCR of the expected strings with their measured point size)
- **Plot script** → `check_plot_script.py` (`savefig` kwargs / rcParams)
- **Composed-figure directory** → all of the above, per panel

Programmatic checks own anything with ground truth (font minima, palette compliance, geometry, rendered text); the VLM judgment pass is reserved for "does this look balanced": hierarchy, alignment, palette coherence, journal fit.
Every report ends with a JSON verdict (`status`, `findings[].action`, `hint`) that generation skills branch on.

## The generate, QA, fix loop

AI-generated figures follow a bounded loop defined in `figure-qa/references/iterate-loop.md`: generate N candidates in parallel, QA all of them in one parallel dispatch of Sonnet-tier reviewers, rank by status and findings, apply exactly one targeted change (a Codex edit, a regenerated prompt, or moving a string to the overlay), re-QA, and stop at `ship` or after three iterations.
Text placement follows a ladder: the model renders panel letters, titles, and short labels at large size; dense labels go to the SVG overlay; numerals, axes, and equations go to the plot or vector skills.

## Skills

- **figure-bible**: step zero; scaffolds and validates `figures/theme.json`, the single palette and model-settings source for every other skill and for QA
- **scientific-figure**: the composer (the sink): `svgutils`-based, exact mm coordinates, `validate_fonts.py` before export, Inkscape/cairosvg backend
- **plot-styling**: data plots via matplotlib, seaborn, plotnine, plotly, or PyVista, with SciencePlots recipes for Nature/IEEE/Science/Cell/PNAS/APS
- **svg-figure** / **svg-primitives**: hand-authored or programmatic schematics: boxes, arrows, and labels in SVG, with `svg-primitives` preferred for new work (mm-precise, auto-fit text, tangent-correct arrows, in-process validation)
- **transparent-icons**: flat scientific icons through the shared Codex or API backend, keeping the model's native alpha
- **ai-full-figure**: single panels or whole multi-panel figures rendered by gpt-image-2 (Codex CLI, default `gpt-5.6-luna` at max effort) with verbatim text, panels generated in parallel with reference-image consistency and composed at journal width, plus the SVG overlay for dense labels
- **figure-qa**: the QA agent described above, run against every figure regardless of how it was built

## Try it

```
"Set up a figure bible for my Nature paper"
"Generate a two-panel AI figure: EEG headset and a foundation model, with titles"
"Create a Nature 2-column figure with 3 panels showing EEG spectrograms"
"QA this figure for Science submission requirements"
"Generate a transparent icon of a neuron for my poster"
```

## Learn more

The [Agentic Research Course](https://courses.osc.earth/agentic-research/) week 8, "Scientific Figures," covers this plugin hands-on.
