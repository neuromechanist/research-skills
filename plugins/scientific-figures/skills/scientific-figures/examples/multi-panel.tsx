/**
 * Layout template: 2x2 multi-panel figure (double-column width, half-page height).
 *
 * This file is a structural template with placeholder panels. Each placeholder
 * View should be replaced with an Image component pointing to actual icon/plot
 * files when building a real figure.
 *
 * Usage:
 *   bunx --bun add @react-pdf/renderer react
 *   bun run examples/multi-panel.tsx
 *
 * Output: figure-example.pdf
 */
import React from "react";
import {
  Document,
  Page,
  View,
  Text,
  Image,
  StyleSheet,
  renderToFile,
} from "@react-pdf/renderer";

// Double-column, half-page: 7.0 x 4.5 inches = 504 x 324 points
const PAGE_WIDTH = 504;
const PAGE_HEIGHT = 324;
const PANEL_WIDTH = PAGE_WIDTH / 2;
const PANEL_HEIGHT = PAGE_HEIGHT / 2;

const PALETTE = {
  primary: "#2D7D9A",
  secondary: "#E8734A",
  accent: "#F5C242",
  text: "#333333",
  lightGray: "#F5F5F5",
};

const styles = StyleSheet.create({
  page: {
    width: PAGE_WIDTH,
    height: PAGE_HEIGHT,
    backgroundColor: "white",
    flexDirection: "row",
    flexWrap: "wrap",
  },
  panel: {
    width: PANEL_WIDTH,
    height: PANEL_HEIGHT,
    position: "relative",
    alignItems: "center",
    justifyContent: "center",
    padding: 16,
  },
  panelLabel: {
    position: "absolute",
    top: 6,
    left: 8,
    fontSize: 14,
    fontFamily: "Helvetica-Bold",
    color: PALETTE.text,
  },
  icon: {
    width: 80,
    height: 80,
    objectFit: "contain",
  },
  caption: {
    fontSize: 8,
    fontFamily: "Helvetica",
    color: PALETTE.text,
    textAlign: "center",
    marginTop: 8,
    maxWidth: PANEL_WIDTH - 40,
  },
  separator: {
    position: "absolute",
    backgroundColor: "#E0E0E0",
  },
  hLine: {
    left: 10,
    right: 10,
    top: PANEL_HEIGHT,
    height: 0.5,
  },
  vLine: {
    top: 10,
    bottom: 10,
    left: PANEL_WIDTH,
    width: 0.5,
  },
});

// Replace these paths with actual icon files
const ICONS = {
  brain: "icons/brain.png",
  analysis: "icons/analysis.png",
  network: "icons/network.png",
  result: "icons/result.png",
};

const Panel = ({
  label,
  iconSrc,
  caption,
}: {
  label: string;
  iconSrc: string;
  caption: string;
}) => (
  <View style={styles.panel}>
    <Text style={styles.panelLabel}>{label}</Text>
    {/* Uncomment when icon files are available:
    <Image src={iconSrc} style={styles.icon} />
    */}
    <View
      style={{
        width: 80,
        height: 80,
        backgroundColor: PALETTE.lightGray,
        borderRadius: 8,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Text style={{ fontSize: 10, color: PALETTE.primary }}>
        Placeholder: replace with Image component
      </Text>
    </View>
    <Text style={styles.caption}>{caption}</Text>
  </View>
);

const Figure = () => (
  <Document>
    <Page size={[PAGE_WIDTH, PAGE_HEIGHT]} style={styles.page}>
      <Panel
        label="A"
        iconSrc={ICONS.brain}
        caption="EEG recording with 64-channel montage during bimanual coordination task"
      />
      <Panel
        label="B"
        iconSrc={ICONS.analysis}
        caption="Source-resolved ICA decomposition identifies cortical components"
      />
      <Panel
        label="C"
        iconSrc={ICONS.network}
        caption="Corticomuscular coherence analysis reveals frequency-specific coupling"
      />
      <Panel
        label="D"
        iconSrc={ICONS.result}
        caption="Age-related differences in beta-band CMC during precision grip"
      />
    </Page>
  </Document>
);

async function main() {
  const output = process.argv[2] || "figure-example.pdf";
  await renderToFile(<Figure />, output);
  console.log(`Rendered: ${output}`);
}

main().catch(console.error);
