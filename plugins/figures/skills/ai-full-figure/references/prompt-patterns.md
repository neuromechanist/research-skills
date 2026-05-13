# Substrate Prompt Patterns

How to ask `gpt-image-2` (via Codex CLI or OpenAI Images API) for a pictorial substrate that the overlay step will then label, and what to avoid.

## The substrate-only rule

The single most important rule: **the substrate must contain no text, no labels, no arrows, no captions, no watermark.** All of those are added programmatically in step 2 (overlay). Including them in the substrate guarantees label drift and inconsistency.

Always include in the prompt:

> No text, no labels, no arrows, no captions, no watermark.

This single sentence dramatically reduces hallucinated labels in the output.

## Subject phrasing that works

| Goal | Prompt fragment |
|---|---|
| Anatomical illustration | "a stylized lateral view of a human brain in soft watercolor" |
| Microscope / lab apparatus | "a stylized two-photon microscope as seen from a 30-degree angle, line-art illustration" |
| Cellular / molecular | "a stylized cell membrane with embedded receptor proteins, cross-section view" |
| Scene / setup | "a researcher's hand placing an EEG cap on a stylized head, side view" |
| Conceptual / metaphor | "a stylized labyrinth of neurons, top-down view, line-art" |

Pattern: **subject + viewing angle + medium / style + composition hint**.

Avoid concrete number references ("3 electrodes on the scalp") — the model will draw something resembling the number but you cannot rely on it. If the count matters, draw it in the overlay.

## Style tokens that compose well

The theme bible's `style_tokens` are concatenated into the prompt. Tokens that produce coherent style across a set:

- `"photorealistic illustration"` — defaults to a clean illustrative style with some shading
- `"soft watercolor"` — gentle, scientific-textbook feel
- `"line-art illustration"` — outline-dominant, sparse fill
- `"isometric 3D"` — useful for apparatus diagrams
- `"flat 2D"` — same as transparent-icons; useful when the substrate should match icon set
- `"vintage scientific illustration"` — pen-and-ink texture, Victorian-era reference style

Avoid these tokens — they introduce inconsistency:

- `"realistic"` — too photorealistic; the substrate will have realistic skin / textures that fight labels
- `"hyperrealistic"` — same problem, magnified
- `"detailed"` — pushes the model to add small features that clash with overlay simplicity
- `"4K"` / `"8K"` — model interprets as "more detail" and adds noise

## Composition hints

Set the composition in the theme's `composition.aspect` and `composition.perspective`. For prompts:

- `"centered on a clean white background"` — most useful for the overlay pattern; the substrate's edges are predictable
- `"on a transparent-appearing background"` — sometimes helps when watercolor / line-art is requested, even though the actual output is opaque
- `"head-on view"`, `"side view"`, `"three-quarter view"` — fixes the perspective when the subject has clear orientation
- `"with 12% padding around the main subject"` — leaves room for overlay arrows and labels at the edges

## Palette injection

The theme bible's `palette` keys are injected into the prompt as a sentence:

> Palette: primary color #1F3A5F, accent #E07A5F, neutral #F4F1DE.

Models in 2026 honor named palette tokens better than raw hex codes — when consistency matters more than exact hex match, also inject color names:

> Palette: deep navy primary, warm orange accent, cream neutral.

If both forms are present, the model tends to follow the named tokens for tone and the hex codes for specific fills.

## Negative tokens

`negative_tokens` from the theme should always include at least:

```
["text", "labels", "watermark", "arrows", "caption", "gradient", "3D", "shadow"]
```

Add domain-specific exclusions when needed:

- For brain illustrations: `"speech bubble", "thought bubble"`
- For apparatus: `"hands", "fingers"` (unless deliberately included)
- For abstracts: `"realistic skin texture", "photographic background"`

## Reference images for style consistency

`gpt-image-2` accepts up to 16 reference images for style transfer. When generating a set of substrates that need to look like siblings:

1. Generate the first substrate with the full prompt.
2. Save it as the canonical reference.
3. For the rest of the set, attach the canonical reference to each generation call and prompt: `"in the same style as the attached reference"`.

The Codex CLI image_gen tool does not yet support multi-reference attachment in v0.130 (May 2026); use the OpenAI Images API directly when set-wide consistency is critical.

## Common failure modes

| Failure | Cause | Mitigation |
|---|---|---|
| Random text in the substrate (looks like English but isn't) | Model assumes scientific figures have labels | Add "no text, no labels" to negative tokens; if it still appears, generate again — single-instance, low cost |
| Subject too small (sea of background) | Vague composition | Add "centered, fills 80% of the canvas" or "subject is the focal point" |
| Inconsistent style across a set | Each generation samples independently | Use reference-image conditioning (OpenAI API path) |
| Palette ignored | Hex codes ambiguous to the model | Inject named color tokens alongside hex |
| Arrows / lines hallucinated | Subject inherently has arrows (e.g., flow diagram) | Reframe the subject to remove implicit arrows; add "no arrows" to negative tokens; consider switching to `[[svg-figure]]` |
| Asymmetric where symmetry was implied | Models drift from canonical shapes (brain, cell) | Generate 2-3 versions and pick; or specify "symmetric" / "bilaterally symmetric" |

## When to give up on AI substrate

If after 2-3 generation attempts the substrate still hallucinates labels, drifts from the requested palette, or produces a subject the overlay can't reasonably label, route to `[[svg-figure]]` (for schematics) or `[[scientific-figure]]` (for composing existing assets). The hard ceiling described in SKILL.md applies here too: don't burn cost generating substrates for figures that need precise text.
