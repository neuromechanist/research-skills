# JSON Authoring Guide

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

These are recommended area assignments. The schema allows any area value, but elements placed in non-standard areas for a layout may not render as expected.

Use `position.order` to control element ordering within an area (0-based).

## Authoring best practices

### Content density
- Keep bullet lists to 6 or fewer items per slide (the validator fires `dense-bullets` at >6)
- Limit text blocks to 2-3 short paragraphs
- One Mermaid diagram per slide (complex diagrams need breathing room)
- The validator flags `dense-copy`, `dense-bullets`, and `dense-media` warnings

### Images
- Always include `alt` text (validator warns on `missing-image-alt`)
- Prefer percentage widths (`55%`) over fixed pixels for responsive sizing (validator warns `fixed-image-sizing` when a slide has multiple media elements and any image uses fixed pixel sizing)
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
- Notes support plain text and basic markdown

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
   # Open http://localhost:3000/?presentation=./presentation.json
   ```

### Advisory warnings

| Warning | Meaning |
|---------|---------|
| `dense-copy` | Too much text on a slide |
| `dense-bullets` | More than 6 bullet items on a slide |
| `dense-media` | Too many media elements |
| `fixed-image-sizing` | Fixed pixel image sizing on a slide with multiple media |
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
| `Home` / `End` | Jump to first / last slide |
| `B` / `.` | Blackout screen |
| Arrow keys / Space | Navigate slides |
