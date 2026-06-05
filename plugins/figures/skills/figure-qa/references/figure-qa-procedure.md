# Figure QA Procedure

The procedure for QA-ing a scientific figure for journal-submission quality. This is the brain loaded by the `figure-qa` skill (inline mode) and by the per-tool QA subagents. It detects the input type, runs the right deterministic checks via the helper scripts, and adds a VLM rubric judgment for aesthetic concerns.

**Strict separation.** Programmatic checks own anything with ground truth (hex codes, pt sizes, pixel positions, alpha values, bbox overlap). VLM judgment owns the aesthetic questions ("does the hierarchy read clearly", "is this layered correctly"). Never assign a VLM score to something a script measured, and never eyeball something a script can compute.

## 0. Honor the no-qa opt-out

If the invocation includes `no-qa` in its prompt or args, return immediately with a one-line note that QA was skipped. Check this before opening any files or spawning subprocesses.

## 1. Locate the helper scripts

The deterministic checks live in the figures plugin at `agents/figure-qa-scripts/` (they stay there; the skill loads them from that path):

```bash
SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/agents/figure-qa-scripts"
if [ -z "${CLAUDE_PLUGIN_ROOT:-}" ] || ! test -d "$SCRIPTS_DIR"; then
    SCRIPTS_DIR="$(find . -type d -name figure-qa-scripts -path '*/figures/agents/*' 2>/dev/null | head -1)"
fi
test -d "$SCRIPTS_DIR" || { echo "FATAL: could not locate figure-qa-scripts; install the figures plugin" >&2; exit 2; }
ls "$SCRIPTS_DIR"  # check_svg.py, check_raster.py, check_plot_script.py
```

If the scripts cannot be found, STOP and report it; do not invent measurements.

## 2. Detect the input type

Branch on extension and content sniff. State which branch ran in the final report so the user can interpret missing sections.

| Extension | Branch | Why |
|---|---|---|
| `.svg` | **SVG** | parse XML, walk transforms, check fonts/geometry/palette |
| `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff` | **Raster** | check alpha, white background, DPI, dominant colors |
| `.py` matching `import matplotlib|seaborn|plotly|plotnine` | **Plot script** | AST analysis: rcParams, savefig, library choice |
| `.ipynb` matching same imports | **Plot script** | extract code cells first, then same AST analysis |
| Directory with `figure.svg`, `compose.py`, or `panels/` | **Composed figure** | run the SVG branch on each component and the composed output |

Sniff content when the extension is ambiguous:
```bash
head -2 path | grep -q '<svg' && BRANCH=svg
grep -q -E 'import (matplotlib|seaborn|plotly|plotnine)' path && BRANCH=plot_script
```

## 3. Run the programmatic checks for the detected branch

Pass `--journal` when the user or upstream skill indicated a target journal; the scripts treat it as authoritative for font-size minima, DPI minima, and palette allow-lists.

**Exit-code contract across all three helpers:**

- `0` -- clean (no findings).
- `1` -- findings present; JSON report on stdout. Surface them in the Programmatic findings section.
- `2` -- script error (missing dependency, malformed input, timeout, internal exception). The JSON may be empty or incomplete. Do **not** treat as "no findings." Mark the affected section as `unavailable (script error)` and cover it with VLM judgment instead.

Capture stderr alongside stdout so the error message is preserved:
```bash
"$@" > /tmp/report.json 2> /tmp/report-err.txt; RC=$?
[ "$RC" -eq 2 ] && { echo "script error:"; cat /tmp/report-err.txt; }
```

Apply this `RC=$?` check after **every** per-branch command below; the per-branch examples omit it only for brevity. Exit 2 is a script error, not "no findings."

### SVG branch
```bash
uv run --with lxml --with svgelements --with shapely \
    python "$SCRIPTS_DIR/check_svg.py" path/to/figure.svg \
    --journal nature --palette okabe-ito > /tmp/svg-report.json 2> /tmp/svg-err.txt
```
Report `checks.fonts.issues`, `checks.palette.off_palette`, and `checks.geometry` (its `bbox_overlaps`, `arrow_tip_issues`, and `text_overflow` lists) separately. Palette compliance is only evaluated when `--palette` is passed; omit it to skip that check. When `checks.geometry.available` is False (missing svgelements/svgpathtools/shapely), do not conclude the figure is geometry-clean: VLM judgment must cover layered-element correctness and overlaps. `text_overflow` uses a heuristic font-size estimate, so an empty `text_overflow` is not a guarantee of sub-mm text fit.

### Raster branch
```bash
uv run --with pillow --with colorthief \
    python "$SCRIPTS_DIR/check_raster.py" path/to/figure.png \
    --journal nature --expect-transparent > /tmp/raster-report.json 2> /tmp/raster-err.txt
```
Set `--expect-transparent` when the upstream skill (transparent-icons, ai-full-figure substrate) intended a transparent background.

### Plot-script branch
```bash
uv run python "$SCRIPTS_DIR/check_plot_script.py" path/to/plot.py \
    --journal nature > /tmp/plotscript-report.json 2> /tmp/plotscript-err.txt
```
Static AST analysis, no execution. Surface any `library_recommendation` as a suggestion, not a blocker. For `.ipynb`, extract code cells first:
```bash
uv run --with nbformat python -c "import nbformat,sys; nb=nbformat.read(sys.argv[1],as_version=4); print('\n'.join(c.source for c in nb.cells if c.cell_type=='code'))" notebook.ipynb > /tmp/extracted.py
uv run python "$SCRIPTS_DIR/check_plot_script.py" /tmp/extracted.py --journal nature > /tmp/plotscript-report.json
```

### Composed-figure branch
Run the SVG branch on the composed output (if present) and on each panel SVG:
```bash
test -f figure.svg && {
    uv run --with lxml --with svgelements --with shapely \
        python "$SCRIPTS_DIR/check_svg.py" figure.svg --journal nature \
        > /tmp/composed-svg.json 2> /tmp/composed-svg-err.txt
    RC=$?; [ "$RC" -eq 2 ] && { echo "script error (composed):"; cat /tmp/composed-svg-err.txt; }
}
for p in panels/*.svg; do
    [ -f "$p" ] || continue   # skip the literal glob when panels/ has no SVGs
    pb="$(basename "$p" .svg)"
    uv run --with lxml --with svgelements --with shapely \
        python "$SCRIPTS_DIR/check_svg.py" "$p" --journal nature \
        > "/tmp/panel-$pb.json" 2> "/tmp/panel-$pb-err.txt"
    RC=$?; [ "$RC" -eq 2 ] && { echo "script error (panel $p):"; cat "/tmp/panel-$pb-err.txt"; }
done
```

## 4. VLM rubric judgment

Read the figure with the Read tool so you can see it. For raster inputs this is a pixel view; for SVG the Read tool returns the source, so reason about layout from the structure, or render to PNG first (e.g. cairosvg) when a pixel-level view matters. Rate five dimensions 1-5, one sentence each:

- **Clarity** -- can a reader infer what each panel shows without the caption?
- **Hierarchy** -- is the primary data the visual focus, or do annotations dominate?
- **Alignment** -- do panels, labels, and gutters look intentional and consistent?
- **Palette coherence** -- do the colors feel like one set?
- **Journal-fit** -- does this read as a Nature/Science/Cell/PNAS figure?

**Never assess via VLM** (these have ground truth and belong to the scripts): exact hex codes, exact pt sizes, exact pixel positions or bbox coordinates, counts above ~5, whether a specific element is "exactly" something. When a script reports a deterministic issue, repeat it as a known finding but do not assign a VLM score for it.

## 5. Synthesize and report

Combine programmatic findings and VLM scores into one report. Use this shape exactly (downstream agents rely on the keys):

```markdown
# Figure QA Report -- <input-name>

**Detected type:** <svg | raster | plot_script | composed>
**Target journal:** <nature | science | cell | pnas | generic | not specified>

## Programmatic findings
- **Fonts:** <X of Y below minimum, Z skipped> -- list offending text with effective pt.
- **Palette:** <N off-palette colors> -- list with nearest allowed distance.
- **Geometry:** <bbox overlaps / arrow-tip issues / text overflow> -- or "unavailable; VLM covered."
- **Alpha / background:** <transparent corners count, white-background detection>.
- **Resolution:** <px size, DPI vs journal minimum>.
- **Plot-library recommendation:** <if applicable>.

## VLM judgment (1-5 each)
| Dimension | Score | Note |
|---|---|---|
| Clarity | <n> | <one sentence> |
| Hierarchy | <n> | <one sentence> |
| Alignment | <n> | <one sentence> |
| Palette coherence | <n> | <one sentence> |
| Journal-fit | <n> | <one sentence> |

## Recommendation
- **Status:** <ship | revise | block>
  - `ship`: zero programmatic issues AND all VLM scores >= 4
  - `revise`: programmatic findings exist but are addressable, or any VLM score is 3
  - `block`: any VLM score is 1-2, or fonts are below journal minimum (will be rejected)
- **Highest-leverage fix:** <one concrete next step>
```

## Examples of expected behavior

- Invoked on `examples/out/figure.svg` from scientific-figure: run the SVG branch; all fonts pass; palette compliance not measured (no `--palette`); VLM scores 4-5 across the board; status `ship`.
- Invoked on a transparent-icons output `brain.png` with `--expect-transparent`: run the raster branch; transparent corners 2/4 with the `threshold` method; note the threshold limitation and suggest `--transparency-method birefnet`; add VLM judgment of the icon itself.
- Invoked on `plot.py` with `font.size: 7`: run the plot-script branch; report the rcParam font sizes against the journal minimum; flag `savefig_missing_bbox_inches` if applicable; surface a `library_recommendation` if the script uses matplotlib for a chart type better served by another library.

## Constraints

- **Never modify the figure.** This procedure is read-only.
- **Never call any image-generation API.** QA is read-only.
- **Always surface the programmatic JSON paths** so the user can re-inspect.
- **Never fabricate measurements.** If a section is unavailable (dependency missing or script error), say so; do not guess.
