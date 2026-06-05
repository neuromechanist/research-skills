# Grant Figure QA Procedure

The procedure for reviewing all figures in a grant proposal for NIH/NSF compliance, publication quality, and accessibility. This is the brain loaded by the `grant-figure-qa` skill (inline mode) and by the per-tool QA subagents.

## 1. Locate figures

Find all figure files in the proposal directory:
```bash
find . -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.pdf" -o -name "*.tiff" -o -name "*.svg" -o -name "*.eps" \) | sort
```

## 2. Check resolution and dimensions

For each figure:
```bash
identify -verbose figure.png | grep -E '(Resolution|Geometry|Print size)'
# or with Python
python3 -c "from PIL import Image; img=Image.open('figure.png'); print(f'Size: {img.size}, DPI: {img.info.get(\"dpi\", \"unknown\")}')"
```

**NIH requirements:**
- Minimum 300 DPI for photographs
- Minimum 600 DPI for line art
- Maximum page dimensions: 7.5" x 10" (within margins)
- Acceptable formats: PNG, TIFF, JPG, PDF

**NSF requirements:**
- PDF figures embedded in the proposal
- Readable when printed in grayscale

## 3. Check font consistency

- [ ] Font size >= 8pt (readable when printed)
- [ ] Consistent font family across all figures
- [ ] Axis labels and legends readable
- [ ] No fonts smaller than axis tick labels

## 4. Check color accessibility

- [ ] Figures distinguishable in grayscale (print-friendly)
- [ ] Colorblind-safe palette used (avoid red-green only distinctions)
- [ ] Sufficient contrast between elements
- [ ] Colors consistent across related figures

## 5. Check content quality

- [ ] All axes labeled with units
- [ ] Scale bars present where needed
- [ ] Panel labels (A, B, C) consistent style
- [ ] No pixelation or compression artifacts
- [ ] Legends complete and accurate
- [ ] Statistical annotations clear (*, **, p-values)
- [ ] Error bars defined in caption (SEM, SD, CI)

## 6. Check caption quality

Read the proposal text to find figure captions:
- [ ] Each figure has a caption
- [ ] Captions are self-contained (understandable without reading body text)
- [ ] Statistical methods mentioned in caption match the figure
- [ ] All panels referenced in caption
- [ ] Abbreviations defined in caption

## 7. Generate report

```
## Grant Figure QA Report

### Figure 1: {filename}
- Resolution: {W}x{H} @ {DPI} DPI [PASS/FAIL]
- Format: {format} [PASS/FAIL]
- Font size: >= 8pt [PASS/FAIL]
- Grayscale readable: [PASS/FAIL]
- Colorblind safe: [PASS/FAIL]
- Axes labeled: [PASS/FAIL]
- Caption complete: [PASS/FAIL]
- Issues: {list of specific issues}

### Summary
- Figures reviewed: N
- Passing: N
- Issues found: N
- Critical (must fix): {list}
- Recommended: {list}
```

## Constraints

- Read-only. Never modify the figures or the proposal.
- If a tool (`identify`, Pillow) is unavailable, report which checks could not be run rather than skipping them silently; do not fabricate DPI or dimensions.
