# Figure QA Procedure

The procedure for QA-ing a scientific figure for journal-submission quality. This is the brain loaded by the `figure-qa` skill (inline mode) and by the per-tool QA subagents. It detects the input type, runs the right deterministic checks via the helper scripts, and adds a vision-language model (VLM) rubric judgment for aesthetic concerns.

**Strict separation.** Programmatic checks own anything with ground truth (hex codes, pt sizes, pixel positions, alpha values, bbox overlap, detected text). VLM judgment owns the aesthetic questions ("does the hierarchy read clearly", "is this layered correctly"). Never assign a VLM score to something a script measured, and never eyeball something a script can compute.

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
| `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff` | **Raster** | check alpha, white background, DPI, dominant colors, verbatim text |
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
uv run --with pillow --with pytesseract \
    python "$SCRIPTS_DIR/check_raster.py" path/to/figure.png \
    --journal nature --expect-transparent > /tmp/raster-report.json 2> /tmp/raster-err.txt
```
Set `--expect-transparent` when the upstream skill (transparent-icons, ai-full-figure substrate) intended a transparent background.

When the upstream generation requested verbatim text (a `--text` item on `generate_figure.py`, or a spec JSON `text[]` entry), run the same script's text check once, passing every expected string, and ask for the merged JSON verdict directly:

```bash
uv run --with pillow --with pytesseract \
    python "$SCRIPTS_DIR/check_raster.py" path/to/figure.png \
    --journal nature --width-mm 89 --palette theme.json \
    --expect-text "Panel A" --expect-text "lateral sulcus" \
    --json > /tmp/raster-text-report.json 2> /tmp/raster-text-err.txt
```

- Pass one `--expect-text` per verbatim string the generation was asked to render (panel letters, titles, short labels). No `--expect-text` means the text check does not run; report the text row as "not checked, no verbatim text requested," not as a pass.
- Pass `--width-mm` whenever the figure's physical size is known, so a `text_too_small` finding reports a measured cap height in mm against the journal minimum rather than a bare pixel count.
- Pass `--palette theme.json` (or an allow-list name) to fold palette compliance into the same verdict instead of a separate call.
- `--json` switches the script's stdout to the merged verdict document used in step 5 (`status`, `findings[]`, `measurements`); use it whenever the installed `check_raster.py` supports it, so step 5 has one shape to merge across checks. Fall back to translating the legacy flat report into that shape by hand when it does not.

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

**Never assess via VLM** (these have ground truth and belong to the scripts): exact hex codes, exact pt sizes, exact pixel positions or bbox coordinates, whether requested text is present and correctly spelled, counts above ~5, whether a specific element is "exactly" something. When a script reports a deterministic issue, repeat it as a known finding but do not assign a VLM score for it.

## 5. Synthesize and report

Combine programmatic findings and VLM scores into one report. Keep the markdown shape exactly as before (downstream agents rely on the keys), and append one fenced `json` code block carrying the same verdict shape every check script emits, merged across every check that ran, plus a `vlm` object holding the five 1-5 scores. A caller that only needs to branch on the outcome parses that block alone and can ignore the markdown.

````markdown
# Figure QA Report -- <input-name>

**Detected type:** <svg | raster | plot_script | composed>
**Target journal:** <nature | science | cell | pnas | generic | not specified>

## Programmatic findings
- **Fonts:** <X of Y below minimum, Z skipped> -- list offending text with effective pt.
- **Palette:** <N off-palette colors> -- list with nearest allowed distance.
- **Geometry:** <bbox overlaps / arrow-tip issues / text overflow> -- or "unavailable; VLM covered."
- **Text:** <expected vs. detected strings, missing/garbled, measured cap height vs. journal minimum> -- or "not checked; no verbatim text requested."
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
  - `block`: any VLM score is 1-2, or fonts or text are below journal minimum (will be rejected)
- **Highest-leverage fix:** <one concrete next step>

```json
{
  "file": "<input path>",
  "type": "<svg | raster | plot_script | composed>",
  "journal": "<nature | science | cell | pnas | generic | null>",
  "status": "<ship | revise | block>",
  "findings": [
    {
      "check": "<fonts | palette | geometry | text | alpha | resolution | plot_library>",
      "severity": "<block | warn | info>",
      "message": "<what was found>",
      "action": "<regenerate | edit | overlay | rescale | recolor | none>",
      "hint": "<the exact instruction the orchestrator should apply next>"
    }
  ],
  "measurements": {},
  "vlm": {
    "clarity": "<1-5>",
    "hierarchy": "<1-5>",
    "alignment": "<1-5>",
    "palette_coherence": "<1-5>",
    "journal_fit": "<1-5>"
  }
}
```
````

`findings` merges every check's list (fonts, palette, geometry, text, alpha, resolution, plot-library) into one array in the shape each helper script's `--json` output already uses; when a helper does not yet support `--json`, translate its legacy findings into this shape by hand rather than omitting them. `measurements` carries whatever numeric detail matters for the checks that ran (effective pt sizes, DPI, edit distances); leave it `{}` when nothing applies. When two actions could both fix a finding (see the table in step 6), pick the single one that fits this figure and put the other option nowhere; `action` is always exactly one of the six values, never a list.

## 6. Finding-to-action map

Fill `action` and `hint` for each finding from this table, and use it to choose the single highest-leverage fix in the Recommendation section. `figures:ai-full-figure`'s `iterate-loop.md` reads a finding's `action` and `hint` verbatim to decide the next iteration; do not invent a different action vocabulary or leave `hint` generic.

| Finding | Action | Hint |
|---|---|---|
| `text_missing` (an expected string was not detected) | `regenerate` | Spell the string letter by letter in the verbatim text block and re-request at the same size class or larger. |
| `text_too_small` (detected but under the journal's cap-height minimum) | `regenerate` (prefer this when the string is short and fixed) or `overlay` (prefer this when the label must stay independently editable) | State which: "regenerate with size_class=large for '<string>'", or "move '<string>' to overlay_labels.py as a label". |
| `palette_off` (a color falls outside the theme or allow-list) | `recolor` | "recolor <element> to #<hex>" for a local mismatch (apply it with `generate_figure.py --edit`); for a pervasive mismatch, say so and put the palette's hex lines first in the prompt on the next regeneration. |
| Font below the journal minimum in an SVG overlay | `rescale` | Raise the label's `font_size_pt` (see overlay-recipes.md's headroom guidance), or scale the panel up before composing. |
| Resolution below the journal DPI minimum | `regenerate` | Re-request at a larger pixel size, respecting the model's max-edge and multiple-of-16 constraints; do not upscale the existing raster. |
| Alpha / transparency problem (opaque corners, wrong mode) | `regenerate` | Rerun the transparency pass (chroma-key removal or the Pillow/BiRefNet post-process); never hand-edit the alpha channel. |
| `bbox_overlap` (two elements' bounding boxes collide) | `overlay` | Move the colliding label's `x`, `y`, or `arrow_to` in the labels JSON and re-run `overlay_labels.py`. |

## Examples of expected behavior

- Invoked on `examples/out/figure.svg` from scientific-figure: run the SVG branch; all fonts pass; palette compliance not measured (no `--palette`); VLM scores 4-5 across the board; status `ship`.
- Invoked on a transparent-icons output `brain.png` with `--expect-transparent`: run the raster branch; transparent corners 2/4 with the `threshold` method; note the threshold limitation and suggest `--transparency-method birefnet`; add VLM judgment of the icon itself.
- Invoked on an ai-full-figure output that requested `--text panel-letter:top-left:"A"`: run the raster branch's text check with `--expect-text "A"`; report a `text_missing` or `text_too_small` finding with `action` and `hint` filled from the table if it fails, or an empty `findings` text row if it passes.
- Invoked on `plot.py` with `font.size: 7`: run the plot-script branch; report the rcParam font sizes against the journal minimum; flag `savefig_missing_bbox_inches` if applicable; surface a `library_recommendation` if the script uses matplotlib for a chart type better served by another library.

## Constraints

- **The reviewer never edits files.** It reads the figure, the theme, and any reference images, and writes only its own report; it never touches the figure under review, the theme, or any script.
- **The reviewer never runs generation.** It never calls `generate_figure.py`, `overlay_labels.py` (other than to read output that already exists), or any image-generation API. Deciding whether to apply a finding's `action` and actually running it belongs to the orchestrating skill (`figures:ai-full-figure`'s `iterate-loop.md`), not to this procedure.
- **Always surface the programmatic JSON paths** so the user can re-inspect.
- **Never fabricate measurements.** If a section is unavailable (dependency missing or script error), say so; do not guess.
