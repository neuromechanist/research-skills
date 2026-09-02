# Substrate Prompt Patterns

How to ask `gpt-image-2` (via Codex CLI or the OpenAI Images API) for a pictorial substrate or a fully composed AI figure, and what to avoid.

## Text policy: a ladder, not a ban

Earlier guidance here said AI-rendered text was unreliable and should never be requested. That is no longer true of the current image models, and `generate_figure.py` now supports verbatim text as a first-class input. The policy is a three-rung ladder, chosen by what the text is and how it will need to change later, not a blanket prohibition.

1. **Model-rendered text** for panel letters, titles, and short labels at large relative size. Fast, no extra compositing step, and current models render short verbatim strings reliably at generation size.
2. **SVG overlay** (`overlay_labels.py`, see `overlay-recipes.md`) for dense labels, leader-line annotations, scale bars, and anything that must be edited later without a full regeneration.
3. **`figures:plot-styling` or `figures:svg-primitives`** (invoke either with the Skill tool) for data, axes, numerals, and equations. No image model should be asked to render a number, a unit, or an equation; use a real plotting or vector-drawing tool instead.

### Requesting model-rendered text

`generate_figure.py` accepts repeatable `--text ROLE:PLACEMENT:STRING` items, where `ROLE` is one of `title`, `panel-letter`, `label`, or `caption`. A multi-panel spec JSON carries the same information as a `text` array: `[{"role", "text", "placement", "size_class"}, ...]`.

For every text item, the prompt builder emits a dedicated block, following Codex's own `imagegen` guidance for verbatim rendering:

```
Text (verbatim, render exactly, no extra characters): "Panel A"
```

Whenever any text item is present, the builder also requests `quality: high`; verbatim text rendering degrades first at lower quality settings.

### The text ladder's rejection rules

Not every text request belongs on rung 1. `generate_figure.py` rejects, rather than silently mis-rendering:

- a `label` longer than `theme.text.max_words_per_label` words (default 4),
- a `title` longer than 8 words,
- any text containing numerals with units (`"12 mV"`, `"3 Hz"`) or an equation.

Numerals-with-units and equations always route to rung 3 (a real plotting or vector tool); a rejected long label or title should be shortened, split across rungs 1 and 2, or moved to rung 2 outright.

### When the substrate should stay textless

Rung 1 does not apply to every generation. A pictorial substrate destined for a dense rung-2 overlay (an anatomical illustration with many leader-line labels, an apparatus diagram, a scene) should still be generated with no embedded text at all, so the overlay step owns every string and can be corrected without a regeneration. For that case, keep the substrate-only rule below.

**The substrate-only rule** (when no `--text` item is requested for a generation): the substrate must contain no text, no labels, no arrows, no captions, no watermark. All of those are added programmatically in the overlay step. Including them in the substrate guarantees label drift and inconsistency. `generate_figure.py` appends this sentence automatically to any generation with no `--text` items:

> No text, no labels, no arrows, no captions, no watermark.

If a generation does carry `--text` items, this suffix is not appended (it would contradict the verbatim-text request); the text ladder's rejection rules above are the guardrail instead.

## Subject phrasing that works

| Goal | Prompt fragment |
|---|---|
| Anatomical illustration | "a stylized lateral view of a human brain in soft watercolor" |
| Microscope / lab apparatus | "a stylized two-photon microscope as seen from a 30-degree angle, line-art illustration" |
| Cellular / molecular | "a stylized cell membrane with embedded receptor proteins, cross-section view" |
| Scene / setup | "a researcher's hand placing an EEG cap on a stylized head, side view" |
| Conceptual / metaphor | "a stylized labyrinth of neurons, top-down view, line-art" |

Pattern: **subject, viewing angle, medium or style, composition hint**.

Avoid concrete number references ("3 electrodes on the scalp") in a textless substrate prompt; the model will draw something resembling the number, but you cannot rely on it. If the count matters and does not need to be an embedded numeral, draw it in the overlay (rung 2); if it must appear as a number, use rung 3.

## Style tokens that compose well

The theme bible's `style_tokens` are concatenated into the prompt. Tokens that produce coherent style across a set:

- `"photorealistic illustration"`: defaults to a clean illustrative style with some shading.
- `"soft watercolor"`: gentle, scientific-textbook feel.
- `"line-art illustration"`: outline-dominant, sparse fill.
- `"isometric 3D"`: useful for apparatus diagrams.
- `"flat 2D"`: same as transparent-icons; useful when the substrate should match an icon set.
- `"vintage scientific illustration"`: pen-and-ink texture, Victorian-era reference style.

Avoid these tokens; they introduce inconsistency:

- `"realistic"`: too photorealistic, the substrate will have realistic skin or textures that fight labels.
- `"hyperrealistic"`: same problem, magnified.
- `"detailed"`: pushes the model to add small features that clash with overlay simplicity.
- `"4K"` / `"8K"`: the model interprets this as "more detail" and adds noise.

## Composition hints

Set the composition in the theme's `composition.aspect` and `composition.perspective`. For prompts:

- `"centered on a clean white background"`: most useful for the overlay pattern, the substrate's edges are predictable.
- `"on a transparent-appearing background"`: sometimes helps when watercolor or line-art is requested, even though the actual output is opaque.
- `"head-on view"`, `"side view"`, `"three-quarter view"`: fixes the perspective when the subject has a clear orientation.
- `"with 12% padding around the main subject"`: leaves room for overlay arrows and labels at the edges.

## Palette injection

The theme bible's `palette` keys are injected into the prompt as a sentence:

> Palette: primary color #1F3A5F, accent #E07A5F, neutral #F4F1DE.

Current models honor named palette tokens better than raw hex codes. When consistency matters more than an exact hex match, also inject color names:

> Palette: deep navy primary, warm orange accent, cream neutral.

If both forms are present, the model tends to follow the named tokens for tone and the hex codes for specific fills.

## Negative tokens

`negative_tokens` from the theme should always include at least:

```
["text", "labels", "watermark", "arrows", "caption", "gradient", "3D", "shadow"]
```

Drop `"text"` and `"labels"` from this list only for a generation that intentionally carries `--text` items (rung 1). Add domain-specific exclusions when needed:

- For brain illustrations: `"speech bubble", "thought bubble"`.
- For apparatus: `"hands", "fingers"` (unless deliberately included).
- For abstracts: `"realistic skin texture", "photographic background"`.

## Reference images for style consistency

`gpt-image-2` accepts reference images for style transfer and editing. `generate_figure.py` passes them with a repeatable `--ref` flag (the Codex CLI equivalent is `-i`). To keep a set of substrates or figures looking like siblings:

1. Generate the first substrate or figure with the full prompt.
2. Save it as the canonical reference.
3. For the rest of the set, pass `--ref canonical.png` on each generation call and add `"in the same style as the attached reference"` to the prompt.

## Common failure modes

| Failure | Cause | Mitigation |
|---|---|---|
| Random text in the substrate (looks like English but is not) | Model assumes scientific figures have labels | Add "no text, no labels" to negative tokens; if it still appears, generate again, it is single-instance and low cost |
| Requested verbatim text is misspelled or garbled | Long or unusual string at rung 1 | Shorten toward the word caps, spell an uncommon token letter by letter in the text block, or move the string to rung 2 (overlay) |
| Subject too small (sea of background) | Vague composition | Add "centered, fills 80% of the canvas" or "subject is the focal point" |
| Inconsistent style across a set | Each generation samples independently | Use `--ref` (or Codex `-i`) reference-image conditioning |
| Palette ignored | Hex codes ambiguous to the model | Inject named color tokens alongside hex |
| Arrows / lines hallucinated | Subject inherently has arrows (e.g., flow diagram) | Reframe the subject to remove implicit arrows; add "no arrows" to negative tokens; consider `figures:svg-figure` instead |
| Asymmetric where symmetry was implied | Models drift from canonical shapes (brain, cell) | Generate 2 to 3 versions and pick, or specify "symmetric" / "bilaterally symmetric" |

## When to route elsewhere

If, after 2 to 3 generation attempts, the substrate still hallucinates labels, drifts from the requested palette, or produces a subject the overlay cannot reasonably label, route to `figures:svg-figure` (for schematics) or `figures:scientific-figure` (for composing existing assets), invoking either with the Skill tool. Any request for data, axis numerals, or equations belongs on rung 3 (`figures:plot-styling` or `figures:svg-primitives`) from the start; do not spend generation attempts trying to coax an image model into rendering them.
