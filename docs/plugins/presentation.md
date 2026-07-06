# Presentation

The `presentation` plugin creates interactive Reveal.js presentations from a JSON spec, using the [Agentic Presentation Builder](https://github.com/neuromechanist/agentic-presentation-builder) engine. It supports 7 element types (text, bullets, images, Mermaid diagrams, callouts, code blocks, tables), 5 themes, animated progressive reveals, speaker notes, and LaTeX math.

The skill teaches the agent the JSON schema and authoring workflow; the builder repo handles rendering, so you describe the deck and the skill produces a spec the builder can render, present, or export.

## Skills

- **presentation-builder**: JSON-schema authoring for Reveal.js decks: slide structure, element types, themes, progressive reveals, speaker notes, and math

## Try it

```
"Create a 10-slide academic presentation on EEG signal processing"
"Build a conference talk on brain-computer interfaces"
```

## Learn more

There's no dedicated course week for `presentation-builder`; instead, the [Agentic Research Course](https://courses.osc.earth/agentic-research/) itself is built with it. Every slide deck across all ten weeks of the course is a `presentation-builder` JSON spec rendered through the same engine this plugin ships, so the course site is itself a working example of the plugin end to end.
