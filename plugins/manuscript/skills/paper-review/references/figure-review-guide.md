# Figure Review Guide

Criteria for evaluating figures in academic manuscripts. Figures are often where misleading presentations hide; scrutinize them carefully.

## General Quality

- **Axes:** Both axes must be labeled with units. Font must be readable at print size.
- **Legends:** All elements (colors, symbols, line styles) must be defined.
- **Consistency:** Style (fonts, colors, line weights) should be consistent across all figures.
- **Self-contained:** A reader should be able to understand the figure from its caption alone without reading the main text.
- **Accessibility:** Color choices should be distinguishable to colorblind readers. Prefer colorblind-safe palettes; avoid red-green-only encoding.

## Data Representation

### Bar Plots and Error Bars
- For N >= 10: bar plots with error bars are acceptable if the error measure is defined (SD, SEM, 95% CI).
- For N = 5-9: strongly prefer showing individual data points overlaid on the bar or using box plots.
- For N < 5: bar plots are unacceptable. Show individual data points. For paired data, connect points with lines. The mean and error bars of 2-4 points create a false impression of a distribution.

### Scatter Plots
- Should show individual data points, not just regression lines.
- If a regression line is shown, report R-squared and p-value.
- Check if the apparent trend is driven by a few outlier points.

### Spectral Plots (ERSP, power spectra, coherence)
- For event-related spectral analysis (ERSP), must show baseline-corrected data (change from pre-event baseline), not absolute values. For resting-state or continuous analyses, absolute spectral values may be appropriate.
- Color scale must be defined with a legend showing the units (e.g., dB, percent change).
- Frequency and time axes must be labeled with appropriate resolution.
- Statistical masking (significance overlay) should be described in the caption.

### Heatmaps
- Color bar with defined scale is mandatory.
- The color palette should not obscure or exaggerate differences (avoid jet colormap; prefer perceptually uniform colormaps like viridis).

### Time Series
- Time scale must be in appropriate units (do not use milliseconds for data spanning minutes).
- If multiple traces are overlaid, they must be distinguishable (different colors, offsets, or panels).
- If artifact rejection was performed, the figure should not show obvious artifacts that contradict the described preprocessing.

## Common Figure Issues

1. **Figure contradicts the text:** The figure shows something different from what the methods or results describe. For example, "filtered data" that still shows obvious artifacts, or "baseline-corrected" spectra that clearly have not been baseline-corrected.

2. **Redundant figures:** Two figures showing the same information in different formats. Recommend removing the less informative one.

3. **Missing statistical annotations:** If the text discusses significant differences, the figure should indicate them (brackets, stars, or shading). If significance annotations are present, they must be defined in the caption.

4. **Inappropriate scale:** Axes that exaggerate or minimize effects. Check if the y-axis starts at zero (or if a non-zero start is justified). Check if the time/frequency range is appropriate for the phenomenon being shown.

5. **Undeclared processing:** Figures showing "raw" data that appears too clean (likely filtered or processed), or figures showing processed data described as raw.

## Figure Captions

A complete figure caption should include:
- What the figure shows (not just "Results of experiment 1" but "Mean response time across conditions for N=20 participants")
- Definition of all visual elements (colors, symbols, error bars)
- Statistical details (tests used, significance thresholds)
- Sample size
- Abbreviation definitions (if not defined in the main text)

## Questions to Ask for Each Figure

1. Does this figure accurately represent the data as described in the text?
2. Could a reader be misled by the presentation choice?
3. Is this the most appropriate visualization for this data?
4. Would a different visualization reveal something the current one hides?
5. Is the figure necessary, or does it duplicate information from another figure or table?
