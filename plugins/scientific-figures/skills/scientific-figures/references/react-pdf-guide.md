# react-pdf Quick Reference

## Setup

```bash
bunx --bun create-bun@latest . --yes 2>/dev/null
bunx --bun add @react-pdf/renderer react
```

## Core Components

### Document and Page
```tsx
import { Document, Page, View, Text, Image, StyleSheet } from '@react-pdf/renderer';
import { renderToFile } from '@react-pdf/renderer';

const Figure = () => (
  <Document>
    <Page size={[504, 324]} style={{ padding: 0, backgroundColor: 'white' }}>
      {/* content */}
    </Page>
  </Document>
);

// Render to file
await renderToFile(<Figure />, 'figure.pdf');
```

### Page Size
- Array format: `[width, height]` in points
- Named sizes: `"A4"`, `"LETTER"`, etc.
- Custom: `{ width: 504, height: 324 }`

### View (Layout Container)
```tsx
<View style={{
  flexDirection: 'row',    // 'row' | 'column' (default)
  justifyContent: 'space-between',
  alignItems: 'center',
  width: '50%',
  height: 200,
  padding: 10,
  margin: 5,
  border: '1pt solid #ccc',
}}>
  {children}
</View>
```

### Text
```tsx
<Text style={{
  fontSize: 10,
  fontFamily: 'Helvetica-Bold',
  color: '#333333',
  textAlign: 'center',
}}>
  Panel Label
</Text>
```

### Image
```tsx
<Image
  src="path/to/icon.png"
  style={{ width: 80, height: 80, objectFit: 'contain' }}
/>
```

Supports: PNG, JPG, base64 data URIs, and URLs.

## Layout System (Yoga/Flexbox)

react-pdf uses Yoga (Facebook's flexbox implementation):

### Flex Direction
```tsx
// Horizontal row
<View style={{ flexDirection: 'row' }}>
  <View style={{ flex: 1 }} />  {/* Takes 50% */}
  <View style={{ flex: 1 }} />  {/* Takes 50% */}
</View>

// Vertical stack (default)
<View style={{ flexDirection: 'column' }}>
  <View style={{ height: 100 }} />
  <View style={{ flex: 1 }} />  {/* Takes remaining space */}
</View>
```

### Grid-like Layout
```tsx
// 2x2 grid
<View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
  <View style={{ width: '50%', height: 200 }}>{/* Panel A */}</View>
  <View style={{ width: '50%', height: 200 }}>{/* Panel B */}</View>
  <View style={{ width: '50%', height: 200 }}>{/* Panel C */}</View>
  <View style={{ width: '50%', height: 200 }}>{/* Panel D */}</View>
</View>
```

### Absolute Positioning
```tsx
<View style={{ position: 'relative', width: 504, height: 324 }}>
  {/* Background */}
  <Image src="bg.png" style={{ width: '100%', height: '100%' }} />
  {/* Overlay label */}
  <Text style={{
    position: 'absolute',
    top: 5,
    left: 5,
    fontSize: 14,
    fontWeight: 'bold',
  }}>
    A
  </Text>
</View>
```

## Available Fonts

Built-in (no registration needed):
- `Courier`, `Courier-Bold`, `Courier-Oblique`, `Courier-BoldOblique`
- `Helvetica`, `Helvetica-Bold`, `Helvetica-Oblique`, `Helvetica-BoldOblique`
- `Times-Roman`, `Times-Bold`, `Times-Italic`, `Times-BoldItalic`
- `Symbol`
- `ZapfDingbats`

### Custom Fonts
```tsx
import { Font } from '@react-pdf/renderer';

Font.register({
  family: 'Arial',
  src: '/path/to/Arial.ttf',
});
```

## StyleSheet

```tsx
const styles = StyleSheet.create({
  page: {
    padding: 0,
    backgroundColor: 'white',
  },
  panelLabel: {
    position: 'absolute',
    top: 4,
    left: 4,
    fontSize: 14,
    fontFamily: 'Helvetica-Bold',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  panel: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    width: 72,   // 1 inch
    height: 72,
    objectFit: 'contain',
  },
  arrow: {
    width: 20,
    height: 20,
    objectFit: 'contain',
  },
  caption: {
    fontSize: 8,
    fontFamily: 'Helvetica',
    textAlign: 'center',
    marginTop: 4,
  },
});
```

## Common Patterns

### Panel with label and icon
```tsx
const Panel = ({ label, iconSrc, caption }) => (
  <View style={styles.panel}>
    <Text style={styles.panelLabel}>{label}</Text>
    <Image src={iconSrc} style={styles.icon} />
    <Text style={styles.caption}>{caption}</Text>
  </View>
);
```

### Arrow between elements
```tsx
<View style={styles.row}>
  <Image src="brain.png" style={styles.icon} />
  <Text style={{ fontSize: 20, alignSelf: 'center' }}>→</Text>
  <Image src="analysis.png" style={styles.icon} />
  <Text style={{ fontSize: 20, alignSelf: 'center' }}>→</Text>
  <Image src="result.png" style={styles.icon} />
</View>
```

### Scale bar
```tsx
<View style={{ flexDirection: 'row', alignItems: 'center' }}>
  <View style={{ width: 36, height: 2, backgroundColor: 'black' }} />
  <Text style={{ fontSize: 7, marginLeft: 2 }}>100 μm</Text>
</View>
```

## Rendering Script Template

```tsx
// render.tsx
import React from 'react';
import { renderToFile } from '@react-pdf/renderer';
import { Figure } from './figure';

const outputPath = process.argv[2] || 'figure.pdf';

async function main() {
  await renderToFile(<Figure />, outputPath);
  console.log(`Rendered: ${outputPath}`);
}

main().catch(console.error);
```

Run with: `bun run render.tsx`
