# Course "house style" reference

This is the stable slide style converged on across the ten Open Science Collective (OSC) Agentic
Research Course decks. It is an opinionated layer on top of `authoring-guide.md` (which stays the
generic guide). Follow it when a deck should match that course look; deviate deliberately, not by
accident.

The full-slide and element snippets below are copy-paste-ready and validate against the schema.
The `metadata` and `speakerNotes` excerpts are field-shape fragments, not standalone documents:
drop them into a deck (or slide) to validate. All snippets are real shapes pulled from the course
decks.

## Deck defaults

```json
"metadata": {
  "title": "Agentic Research Course",
  "author": "Seyed Yahya Shirazi, Ph.D.",
  "theme": "default",
  "aspectRatio": "16:9",
  "controls": { "slideNumbers": true, "progress": true }
}
```

- **Theme is `default`** for every deck (not `academic`/`dark`). Accent color is applied per
  element, not via theme.
- Slide numbers and progress bar on.
- Per-slide `transition`: `"fade"` for the title, `"slide"` for content slides.

## Title slide

A `title` layout with a stacked center block, ordered top to bottom:

```json
{
  "id": "title",
  "layout": "title",
  "transition": "fade",
  "elements": [
    { "type": "text", "content": "# Agentic Research Course",
      "style": { "fontSize": "xxl", "alignment": "center", "fontWeight": "bold" },
      "position": { "area": "center" } },
    { "type": "text", "content": "Week 8: Scientific Figures",
      "style": { "fontSize": "large", "alignment": "center", "color": "#2563EB" },
      "position": { "area": "center", "order": 1 } },
    { "type": "text",
      "content": "**Seyed Yahya Shirazi, Ph.D.**\nAssistant Project Scientist, Swartz Center for Computational Neuroscience\nUC San Diego\n\n[Open Science Collective](https://osc.earth)",
      "style": { "fontSize": "medium", "alignment": "center", "color": "#475569" },
      "position": { "area": "center", "order": 2 } },
    { "type": "text",
      "content": "Course: [courses.osc.earth/agentic-research](https://courses.osc.earth/agentic-research/) | Discord: [discord.gg/...](https://discord.gg/...) | Recording: published to YouTube within 48 h",
      "style": { "fontSize": "small", "alignment": "center", "color": "#64748B" },
      "position": { "area": "center", "order": 3 } }
  ]
}
```

Block order: H1 title (`xxl`, bold) → session subtitle (`large`, accent `#2563EB`) →
author/affiliation (`medium`, `#475569`) → a links line (course / Discord / recording, `small`,
`#64748B`). Use `order` to stack within `center`.

## Layout discipline

- `single-column` is the default for content slides (the large majority).
- `two-column` for comparisons and for the image+text pattern below.
- `title` only for the title slide and section dividers.

Headers are an H2 (`## …`) in `area: "header"` at `fontSize: "xl"`.

## Incremental bullets (the signature pattern)

Bullets are **objects** (`{ text, animation }`), not plain strings, so each item reveals on its
own click. Use sequential `index` values; lead each item with a **bold** phrase. Reveal type is
`"fade"` for the list, and the final/punchline item switches to `"slide-up"`.

```json
{
  "type": "bullets",
  "items": [
    { "text": "**Week 1 -- Git and GitHub.** The safety net.",
      "animation": { "fragment": true, "type": "fade", "index": 0 } },
    { "text": "**Week 2 -- Claude Code.** The agent that reads, plans, writes, runs.",
      "animation": { "fragment": true, "type": "fade", "index": 1 } },
    { "text": "**Today.** The payoff: figures that ship next to the manuscript.",
      "animation": { "fragment": true, "type": "slide-up", "index": 2 } }
  ],
  "bulletStyle": "disc",
  "style": { "fontSize": "large" },
  "position": { "area": "content" }
}
```

Keep to <= 6 items (the validator fires `dense-bullets` above that), and watch
`fragment-overuse` if nearly every element animates.

## Code sections

A `code` element with an explicit `language`, placed in `content` with an `order`, and a fragment
animation so it reveals on cue. Two-up ASCII alignment (command on the left, effect on the right)
is a recurring trick:

```json
{
  "type": "code",
  "language": "bash",
  "code": "# git: version control        # gh: GitHub from CLI\ngit add .                     gh issue create\ngit commit -m \"update\"        gh pr create\ngit push                      gh repo clone user/repo",
  "position": { "area": "content", "order": 2 },
  "animation": { "fragment": true, "type": "fade", "index": 4 }
}
```

## Two-column image + bullets

The standard "concept on the left, points on the right" slide: header spans the top, an SVG icon
in `area: "left"` at `width: "95%"` with a descriptive `alt`, animated bullets in `area: "right"`.

```json
{
  "id": "stage1-direction",
  "layout": "two-column",
  "transition": "slide",
  "elements": [
    { "type": "text", "content": "## Stage 1 -- Direction with /project:epic-dev",
      "style": { "fontSize": "xl" }, "position": { "area": "header" } },
    { "type": "image", "src": "../../assets/icons/strand-fanout.svg",
      "alt": "An epic node fanning into four parallel strand sub-issues",
      "width": "95%", "position": { "area": "left" } },
    { "type": "bullets",
      "items": [
        { "text": "Plan-mode the topic into an epic + parallel **strand** sub-issues.",
          "animation": { "fragment": true, "type": "fade", "index": 0 } },
        { "text": "Each strand: own brief, own branch, own PR.",
          "animation": { "fragment": true, "type": "fade", "index": 1 } }
      ],
      "bulletStyle": "disc", "style": { "fontSize": "xl" },
      "position": { "area": "right" } }
  ]
}
```

Image `src` paths are relative to the deck JSON (e.g. `../../assets/icons/foo.svg`); `present`
resolves them automatically. Always give `image` an `alt` (the validator warns `missing-image-alt`).

## Callouts carry the thesis

Use a `callout` with `calloutType: "important"` for the slide's one-sentence core message; the
other types (`tip`, `note`, `warning`, `info`) for asides.

```json
{
  "type": "callout",
  "calloutType": "important",
  "content": "A one-off script is a commit. A study-level analysis is a project.",
  "position": { "area": "content", "order": 3 }
}
```

## Speaker notes

Set `speakerNotes` on substantive slides. The course convention opens with a delivery cue for the
animated reveals, then dashed talking points:

```json
"speakerNotes": "[Press right 3x to reveal fragments]\n\n- The Week 3 pattern, applied to research output.\n\n- Strands are horizontally parallel: scope before searching."
```

## Quick checklist

- [ ] `theme: "default"`, `16:9`, slide numbers + progress on
- [ ] Title block: H1 → accent subtitle → author block → links line
- [ ] Bullets are objects with per-item `fragment` animation; sequential `index`; bold lead-ins
- [ ] Final bullet uses `type: "slide-up"`; the rest use `"fade"`
- [ ] Code blocks have a `language` and a fragment animation
- [ ] Two-column image slides: header on top, image `left` (95%, with `alt`), bullets `right`
- [ ] Core message lives in a `calloutType: "important"`
- [ ] `speakerNotes` lead with the reveal cue, then talking points
- [ ] Validate with `apb validate deck.json --json`; clear `dense-bullets` / `fragment-overuse`
