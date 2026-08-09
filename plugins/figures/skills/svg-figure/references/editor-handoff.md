# Editor handoff: authoring SVG for Illustrator and Affinity Designer

Rules for generating Scalable Vector Graphics (SVG) files
that a human can open in Adobe Illustrator or Affinity Designer
and actually edit: live text, named groups, vector sub-figures.
Also covers the companion question:
which Portable Document Format (PDF) export path to use for print,
and why the PDF is never the editable handoff.
Findings were researched against Adobe HelpX and UserVoice,
Serif staff posts on the Affinity forum,
and converter documentation (cairo, Inkscape, Skia, Scribus);
confidence per claim is noted where it matters.
Source links are collected at the end.

## The three-artifact model

Ship three artifacts per figure or poster, each with one job:

1. **Editable master: the SVG itself.**
   Both Illustrator and Affinity open SVG directly into native editable objects.
   Hand this to collaborators together with the fonts it uses.
2. **Print PDF: a derived, throwaway artifact.**
   Generate it from the SVG at build time,
   preferably with text outlined (see below).
   Print shops want PDF, commonly PDF/X; they do not want SVG.
3. **Preview raster (PNG) for quick review.**

Never treat a converted PDF as the editable deliverable.
PDF content streams have no paragraph or story model,
only positioned glyph-show operations emitted per line or per kerning run,
so every editor reconstructs text heuristically:
Illustrator maps each run to a separate point-text fragment,
and Affinity merges fragments back into frames with its
"favour editable text over fidelity" import heuristic.
The only PDFs whose text survives as live paragraphs in Illustrator
are those saved by Illustrator itself with
"Preserve Illustrator Editing Capabilities",
which embeds a second, private copy of the native document
(PieceInfo/PGF data) that no external tool can write.
Confirmed; see sources.

## How the two editors map SVG structure

| Construct | Illustrator (File > Open) | Affinity Designer (File > Open) |
|---|---|---|
| `<g id="...">` | Named **group** inside a single "Layer 1"; nothing in SVG maps to an Illustrator layer | **Group** in the Layers panel; `id` naming on import unconfirmed |
| `inkscape:groupmode="layer"` | Ignored (private namespace) | No evidence it promotes to a layer; treat as ignored |
| `<text>` | Editable point text (when the font resolves) | Editable artistic text |
| `<tspan>` lines | Shattered into separate text objects; buys nothing | Coordinate lists inside one text element stack glyphs on top of each other (confirmed matplotlib bug #20910) |
| `text-anchor` | **Ignored on import**; centered text arrives left-aligned (open UserVoice bug) | Unconfirmed; assume unsafe |
| `dominant-baseline` | `middle` ignored | Unconfirmed; avoid |
| Nested `<svg viewBox>` | Nested groups plus clipping masks at best; community-reported failures | Staff-acknowledged bugs with related constructs; avoid |
| `<image>` with SVG data URI | **Fails**; content missing (confirmed forum thread) | Dropped on import in V1 (staff-confirmed); V2 untested |
| `<image>` with PNG data URI | Version-dependent bugs; `xlink:href` more reliable than bare `href` | Same V1 drop risk; test before relying on it |
| `<marker>` arrowheads | Filed bug: paths with markers render only the markers | No reports; Affinity has no native marker feature |
| `<style>` blocks, classes, `font` shorthand | Parsed but baked in; complex CSS (Cascading Style Sheets) rules have crashed Illustrator | `font` shorthand **ignored** (staff-logged bug) |
| Plain 2-stop gradients, simple clip paths | Survive (clip paths add wrapper groups) | Reported working |
| SVG filters (`<filter>`) | Only Illustrator's own 18-effect subset; arbitrary chains unreliable | Assume dropped |

## The mechanical prep pass

`scripts/editor_prep.py` (in this skill) applies every fixable rule below
to an already-generated SVG and reports what it could not fix:

```bash
uv run --with lxml --with svgpathtools --with fonttools \
    python scripts/editor_prep.py figure.svg    # -> figure-editable.svg
```

Use it as the handoff step for new figures
(the design master keeps QA-verifiable markers and anchors)
and as a converter for legacy or foreign SVGs
(matplotlib exports, Inkscape saves, hand-authored files).
`--check` mode reports violations without writing, for CI.

## Authoring checklist for the generator

Structure:

- Wrap each logical region (header, each column or panel, footer)
  in a top-level `<g id="section-name">`.
  That is the best organization either editor can receive:
  named groups in Illustrator, groups in Affinity's Layers panel.
  A flat file with no groups arrives as one pile of 150+ sibling objects.
- Do not emit nested `<svg x y viewBox>` elements for sub-figures.
  Inline the child's elements as
  `<g id="fig-name" transform="translate(x y) scale(s)">`,
  after namespacing its internal `id`s and `url(#...)` references.
  Clip only if the content actually overflows its slot.
- Never embed vector sub-figures as base64 `<image>` data URIs;
  they are not editable anywhere and fail outright in Illustrator.
  Raster images: prefer separate linked files,
  or base64 PNG via `xlink:href` (declare `xmlns:xlink`), and test.

Text:

- One `<text>` element per visual line, single absolute `x`/`y`,
  no `tspan` children, no `dy`, no per-glyph coordinate lists.
  This is also the ceiling:
  neither editor reconstructs wrapped area text from SVG,
  SVG 2 `inline-size` is unsupported,
  and `foreignObject` is not rendered.
- Resolve alignment in the generator:
  compute the left edge from measured text width
  and emit `text-anchor="start"` (or no anchor).
  Illustrator ignores `text-anchor` on import,
  so centered or right-anchored text silently becomes left-aligned
  and drifts as soon as anyone edits it.
- Position by computed baseline `y`; never use `dominant-baseline`.
- Style with presentation attributes only
  (`font-family`, `font-size`, `font-weight`, `fill`),
  never `<style>` blocks, classes, or the `font` shorthand.
- Avoid `letter-spacing` unless tested (unconfirmed in both editors).

Fonts:

- Emit a single concrete installed family name
  (`font-family="Lato"`), not a fallback stack;
  neither editor is documented to walk a comma stack,
  and Affinity substitutes missing fonts silently.
- Use `font-weight="700"`, not hyphenated face names like `Lato-Bold`;
  face-name families are not recognized by font matchers and get substituted.
- `@font-face` and webfonts are ignored by both editors.
  Ship the font files or install instructions with the master.

Geometry and units:

- `width`/`height` in mm with a matching `viewBox="0 0 W H"`,
  origin at zero (nonzero origins displace content in Affinity).
- Absolute units sidestep the classic mismatch
  where Illustrator treats unitless user units as points (1/72 in)
  while the SVG specification says 1 px = 1/96 in.
  Still, verify the document size once after opening
  (Affinity's unit conversion is its weakest area, staff-acknowledged).
- Bake arrowheads as explicit filled `<path>` geometry,
  never `<marker>`/`marker-end`.
- Size limits are not a concern for posters:
  Illustrator artboards go to 227.54 in per side,
  Affinity documents to roughly 21,600 mm.

Handoff instructions to include with the file:

- Open with File > Open, not File > Place.
  Place links or embeds a locked sub-document in both editors.
- Install the shipped fonts first, then verify document size,
  then check the missing-fonts panel (Illustrator)
  or Font Manager (Affinity) before editing.

## Print PDF: derivation recipes

Every SVG-to-PDF converter that keeps text as text
(cairosvg, rsvg-convert, Inkscape, Chrome headless via Skia)
embeds subset fonts with per-glyph positioning:
fine for viewing, searching, and printing,
fragmented and font-substituted when opened in an editor.
So derive the print PDF and stop worrying about its editability:

- **Outlined text (safest for print):**
  `inkscape --export-type=pdf --export-text-to-path in.svg`,
  or post-process any PDF with Ghostscript:
  `gs -o out.pdf -sDEVICE=pdfwrite -dNoOutputFonts in.pdf`.
  Larger file, no searchable text, immune to font problems at the shop.
- **Embedded-font PDF (some shops prefer it, keeps text searchable):**
  Inkscape default export, or cairosvg when filters are simple
  (cairo supports only feBlend, feFlood, feOffset;
  everything else is dropped, and unsupported constructs
  fall back to 300 ppi raster patches).
- **PDF layers (Optional Content Groups, OCG):**
  mostly a dead end from SVG.
  Inkscape cannot write them, cairosvg does not,
  Scribus writes them only at PDF 1.5 but imports SVG single-layer
  and converts text to outlines on the way in.
  Illustrator ignores OCG when opening a PDF (everything flattens);
  Affinity does read OCG layers.
  Not worth building for; structure lives in the SVG groups instead.

## Five-minute empirical tests before trusting a new pipeline

These are the load-bearing behaviors that could not be confirmed
from documentation and are cheap to verify locally:

1. Open the mm-sized SVG and check the artboard/document reads the same mm.
2. Check whether a comma font stack falls through to an installed fallback,
   or substitutes immediately (author a single family either way).
3. Affinity V2 only: whether base64 PNG `<image>` survives import.
4. `letter-spacing` fidelity, if the design needs tracking.
5. The installed Inkscape version's PDF export default
   (a 1.3-era issue questioned whether text-to-path became the default).

## Key sources

- Illustrator groups vs layers: <https://community.adobe.com/questions-652/how-to-create-g-elements-in-svg-that-are-recognized-as-layers-in-illustrator-817756>
- Illustrator tspan shattering: <https://community.adobe.com/t5/illustrator-discussions/svg-text-and-tspans-import/td-p/11418608>
- Illustrator ignores `text-anchor` on import: <https://illustrator.uservoice.com/forums/333657-illustrator-feature-requests/suggestions/37728868-support-svg-text-anchor-styling-on-import>
- Illustrator marker bug: <https://illustrator.uservoice.com/forums/601447-illustrator-bugs/suggestions/38634631-svg-paths-with-marker-endings-render-only-the-mark>
- Illustrator cannot read SVG-as-`<image>`: <https://community.adobe.com/t5/illustrator-discussions/illustrator-does-not-support-my-svg-file-that-contains-svg-image-elements/td-p/9651571>
- Hyphenated face names break font matching: <https://phabricator.wikimedia.org/T25643>
- Affinity PDF text-fragment reconstruction (staff): <https://forum.affinity.serif.com/index.php?/topic/8784-editable-text-option-when-opening-ai-file/>
- Affinity `font` shorthand and px-as-pt bugs (staff-logged): <https://forum.affinity.serif.com/index.php?/topic/173734-font-sizes-in-imported-svg-documents-are-sometimes-interpreted-incorrectly/>
- Affinity drops base64 `<image>` in V1 (staff): <https://forum.affinity.serif.com/index.php?/topic/105461-also-import-image-tags-with-base64-bitmap-data-when-importing-svg-in-designer/>
- Affinity coordinate-list glyph stacking: <https://github.com/matplotlib/matplotlib/issues/20910> and fix <https://github.com/matplotlib/matplotlib/pull/28504>
- Affinity ignores fonts embedded in PDFs: <https://forum.affinity.serif.com/index.php?/topic/178531-designer-cannot-open-pdf-files-containing-embedded-fonts-correctly/>
- Illustrator PGF/PieceInfo private data: <https://helpx.adobe.com/illustrator/kb/optimize-native-pdf-file-sizes.html>
- Illustrator flattens OCG layers on open: <https://illustrator.uservoice.com/forums/333657-illustrator-desktop-feature-requests/suggestions/35852185-keep-layers-from-pdf-when-opening-the-file-in-illu>
- cairosvg support matrix (filters, text selection): <https://cairosvg.org/svg_support/>
- Inkscape PDF export options: <https://inkscape-manuals.readthedocs.io/en/latest/export-pdf.html>
- Ghostscript text outlining: <https://ghostscript.readthedocs.io/en/latest/VectorDevices.html>
- Scribus SVG import limits: <https://fossies.org/linux/scribus/doc/en/scribus-svg.html>
- Illustrator large canvas limits: <https://helpx.adobe.com/illustrator/using/large-sized-artwork.html>
