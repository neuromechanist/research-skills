# Schema Reference

The source of truth is `schema/presentation.schema.json` in the Agentic Presentation Builder repository.

## Presentation metadata

| Field | Type | Notes |
| --- | --- | --- |
| `title` | `string` | Required |
| `author` | `string` | Optional |
| `description` | `string` | Optional |
| `theme` | `string` | `default`, `light`, `dark`, `academic`, `minimal` |
| `aspectRatio` | `string` | `16:9` or `4:3` |
| `controls.slideNumbers` | `boolean` | Slide number visibility |
| `controls.progress` | `boolean` | Progress bar visibility |
| `controls.showNotes` | `boolean` | Enables speaker notes support |
| `customTheme.colors.*` | `string` | Hex colors only |
| `customTheme.fonts.*` | `string` | CSS font-family values |

## Slide fields

| Field | Type | Notes |
| --- | --- | --- |
| `id` | `string` | Stable slide identifier |
| `title` | `string` | Overview label |
| `layout` | `string` | `single-column`, `two-column`, `title`, `blank` |
| `background` | `string` | Hex color or image path |
| `transition` | `string` | `slide`, `fade`, `convex`, `concave`, `zoom` |
| `speakerNotes` | `string` | Presenter notes |
| `elements` | `array` | Slide content |

## Shared element fields

### `style`

| Field | Type | Allowed values |
| --- | --- | --- |
| `fontSize` | `string` | `small`, `medium`, `large`, `xl`, `xxl` |
| `alignment` | `string` | `left`, `center`, `right`, `justify` |
| `color` | `string` | Hex color |
| `fontWeight` | `string` | `normal`, `bold`, `light` |

### `position`

| Field | Type | Allowed values |
| --- | --- | --- |
| `area` | `string` | `header`, `content`, `footer`, `left`, `right`, `center` |
| `order` | `integer` | `0` or greater |

### `animation`

| Field | Type | Allowed values |
| --- | --- | --- |
| `type` | `string` | `fade`, `slide-up`, `slide-down`, `zoom`, `none` |
| `fragment` | `boolean` | Progressive reveal toggle |
| `index` | `integer` | Reveal order |

## Element types

### `text`

- Required: `type`, `content`
- Supports Markdown, GitHub-style alerts (`> [!TIP]`), and inline/display LaTeX math
- Use for headings (`# Title`), prose, and formatted text

### `bullets`

- Required: `type`, `items`
- `bulletStyle`: `disc`, `circle`, `square`, `number`, `none`
- Items can be plain strings or nested `{ text, children }` objects
- Each item supports Markdown

### `image`

- Required: `type`, `src`
- Optional: `alt`, `width`, `height`, `caption`
- Width and height support `%`, `px`, or `auto`
- Prefer percentage widths (e.g., `55%`) for responsive sizing
- Always include `alt` text

### `mermaid`

- Required: `type`, `diagram`
- `theme`: `default`, `dark`, `forest`, `neutral`
- Supports flowcharts, sequence diagrams, class diagrams, state diagrams, etc.

### `callout`

- Required: `type`, `content`
- `calloutType`: `tip`, `warning`, `important`, `note`, `info`
- Optional `title`
- Content supports Markdown

### `code`

- Required: `type`, `code`
- Optional: `language` (default: `javascript`), `caption`, `lineNumbers` (default: `true`)
- Supports: javascript, python, java, go, rust, typescript, html, css, json, and more

### `table`

- Required: `type`, `headers`, `rows`
- `headers`: array of strings
- `rows`: array of arrays of strings
- Optional `caption`
