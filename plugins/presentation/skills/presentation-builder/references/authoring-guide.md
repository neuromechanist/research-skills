# JSON Authoring Guide

## Top-level structure

Every presentation starts with a `presentation` object containing `metadata` and `slides`:

```json
{
  "presentation": {
    "metadata": {
      "title": "My Presentation",
      "theme": "default"
    },
    "slides": []
  }
}
```

## Slide structure

Each slide has a `layout` and an `elements` array. Use `position.area` to place elements within the layout.

### Layout types

- **`title`**: Centered content, ideal for title slides and section dividers
- **`single-column`**: Top-to-bottom flow, the default for most content slides
- **`two-column`**: Side-by-side layout; use `position.area: "left"` and `"right"` to assign elements
- **`blank`**: No layout constraints; use absolute positioning

### Position areas by layout

| Layout | Available areas |
|--------|----------------|
| `title` | `center` |
| `single-column` | `header`, `content`, `footer` |
| `two-column` | `header`, `left`, `right`, `footer` |
| `blank` | Any (free positioning) |

Use `position.order` to control element ordering within an area (0-based).

## Authoring best practices

### Content density
- Keep bullet lists to 4-6 items per slide
- Limit text blocks to 2-3 short paragraphs
- One Mermaid diagram per slide (complex diagrams need breathing room)
- The validator flags `dense-copy`, `dense-bullets`, and `dense-media` warnings

### Images
- Always include `alt` text (validator warns on `missing-image-alt`)
- Prefer percentage widths (`55%`) over fixed pixels for responsive sizing (validator warns on `fixed-image-sizing`)
- Place images in the `public/assets/` directory of the builder project

### Mermaid diagrams
- Keep diagrams simple; deeply nested graphs are flagged as `complex-mermaid`
- Test rendering at presentation resolution (1920x1080)
- Use the diagram's `theme` property to match the presentation theme

### Animations and fragments
- Use `animation.fragment: true` for progressive reveal
- Set `animation.index` to control reveal order
- Keep fragment counts low per slide (flagged as `fragment-overuse` if excessive)
- Good use case: revealing bullet points one at a time
- Bad use case: animating every element on a dense slide

### Speaker notes
- Use `speakerNotes` for delivery guidance, not content
- Press `S` during presentation to view notes
- Notes support plain text

### Themes
- `default`: Blue primary, clean and professional
- `light`: Bright, high-contrast
- `dark`: Dark background, light text
- `academic`: Serif-influenced, formal (good for research talks)
- `minimal`: Stripped-down, content-focused

For custom branding, use `customTheme.colors` and `customTheme.fonts` in metadata.

## Validation workflow

1. Write or edit the JSON file
2. Run structured validation:
   ```bash
   bun run validate -- path/to/presentation.json --json
   ```
3. Fix schema errors (blocking) and advisory warnings (quality)
4. Serve and visually inspect:
   ```bash
   bun run dev
   # Open http://localhost:3000/?presentation=./public/presentation.json
   ```

### Advisory warnings

| Warning | Meaning |
|---------|---------|
| `dense-copy` | Too much text on a slide |
| `dense-bullets` | Too many bullet items |
| `dense-media` | Too many media elements |
| `fixed-image-sizing` | Use percentage widths instead of px |
| `fragment-overuse` | Too many animated fragments |
| `missing-image-alt` | Image lacks alt text |
| `complex-mermaid` | Mermaid diagram is overly complex |

## Keyboard shortcuts (during presentation)

| Key | Action |
|-----|--------|
| `,` | Open settings |
| `P` | Toggle presentation mode |
| `S` | Open speaker notes |
| `O` | Overview (grid view) |
| `F` | Fullscreen |
| `?` | Keyboard shortcuts help |
| `Esc` | Close overlays |
