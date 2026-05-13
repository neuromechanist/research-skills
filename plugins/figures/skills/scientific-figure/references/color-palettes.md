# Color Palettes for Scientific Figures

Curated, publication-quality color palettes. All palettes are colorblind-safe unless noted.

## Choosing a Palette

| Data Type | Palette Type | When to Use |
|-----------|-------------|-------------|
| Categories (groups, conditions) | Qualitative | Distinct groups, no inherent order |
| Ordered values (low to high) | Sequential | Heatmaps, intensity, continuous data |
| Diverging values (below/above center) | Diverging | Correlation, change from baseline |
| Two conditions | Binary | Control vs. treatment, pre vs. post |

## Qualitative Palettes (Categorical Data)

### Wong/Okabe-Ito (Nature standard, colorblind-safe)

This palette, published by Bang Wong (Nature Methods 2011) and based on Okabe and Ito (2008), is the standard for scientific figures.

| Name | Hex | Use |
|------|-----|-----|
| Orange | #E69F00 | Category 1 |
| Sky blue | #56B4E9 | Category 2 |
| Bluish green | #009E73 | Category 3 |
| Yellow | #F0E442 | Category 4 |
| Blue | #0072B2 | Category 5 |
| Vermilion | #D55E00 | Category 6 |
| Reddish purple | #CC79A7 | Category 7 |
| Black | #000000 | Reference/control |

```python
WONG_OKABE_ITO = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7', '#000000']
```

### Tol Bright (colorblind-safe, high contrast)

From Paul Tol's color schemes. Excellent for presentations and print.

| Name | Hex |
|------|-----|
| Blue | #4477AA |
| Cyan | #66CCEE |
| Green | #228833 |
| Yellow | #CCBB44 |
| Red | #EE6677 |
| Purple | #AA3377 |
| Grey | #BBBBBB |

```python
TOL_BRIGHT = ['#4477AA', '#66CCEE', '#228833', '#CCBB44', '#EE6677', '#AA3377', '#BBBBBB']
```

### Paired (for matched conditions)

For before/after, control/treatment pairs. Light and dark versions of the same hue.

| Pair | Light | Dark |
|------|-------|------|
| Blue | #A6CEE3 | #1F78B4 |
| Green | #B2DF8A | #33A02C |
| Red | #FB9A99 | #E31A1C |
| Orange | #FDBF6F | #FF7F00 |
| Purple | #CAB2D6 | #6A3D9A |

```python
PAIRED_LIGHT = ['#A6CEE3', '#B2DF8A', '#FB9A99', '#FDBF6F', '#CAB2D6']
PAIRED_DARK  = ['#1F78B4', '#33A02C', '#E31A1C', '#FF7F00', '#6A3D9A']
```

## Sequential Palettes (Continuous Data)

### Viridis (default for heatmaps)

Perceptually uniform, colorblind-safe, prints well in grayscale.

```python
# Use via matplotlib
import matplotlib.pyplot as plt
cmap = plt.cm.viridis  # or 'inferno', 'magma', 'plasma'
```

### Blue-White-Red (diverging alternative for sequential)

5-stop gradient for intensity maps:

```python
BLUE_SEQ = ['#F7FBFF', '#C6DBEF', '#6BAED6', '#2171B5', '#084594']
```

## Diverging Palettes (Centered Data)

### Blue-White-Red (correlation, change)

```python
DIVERGING_BWR = ['#2166AC', '#67A9CF', '#F7F7F7', '#EF8A62', '#B2182B']
```

### Purple-White-Green

```python
DIVERGING_PWG = ['#7B3294', '#C2A5CF', '#F7F7F7', '#A6DBA0', '#008837']
```

## Domain-Specific Palettes

### Neuroscience

| Name | Primary | Secondary | Accent | Neutral |
|------|---------|-----------|--------|---------|
| EEG/MEG | #2D7D9A | #E8734A | #F5C242 | #4A4A4A |
| fMRI | #1A5276 | #E74C3C | #F39C12 | #7F8C8D |
| Behavioral | #2E86C1 | #28B463 | #F4D03F | #566573 |

### Molecular Biology

| Name | Primary | Secondary | Accent | Neutral |
|------|---------|-----------|--------|---------|
| Genomics | #5B8C5A | #D94F4F | #F5A623 | #333333 |
| Proteomics | #2980B9 | #8E44AD | #F39C12 | #2C3E50 |

### Clinical/Medical

| Name | Primary | Secondary | Accent | Neutral |
|------|---------|-----------|--------|---------|
| Clinical trial | #2980B9 | #E74C3C | #27AE60 | #7F8C8D |
| Imaging | #1A5276 | #D4AC0D | #884EA0 | #566573 |

### Engineering

| Name | Primary | Secondary | Accent | Neutral |
|------|---------|-----------|--------|---------|
| Devices | #34495E | #E67E22 | #3498DB | #2C3E50 |
| Signals | #1ABC9C | #E74C3C | #F39C12 | #2C3E50 |

## Usage in matplotlib/seaborn

```python
# Set a palette globally
import matplotlib.pyplot as plt
PALETTE = ['#E69F00', '#56B4E9', '#009E73', '#0072B2', '#D55E00', '#CC79A7']
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=PALETTE)

# Or per-plot in seaborn
import seaborn as sns
sns.set_palette(PALETTE)
```

## Usage in ggplot2

```r
# Wong palette
wong_colors <- c('#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7')
scale_color_manual(values = wong_colors)
```

## Palette object (JS/TS composition)

```js
const PALETTE = {
  primary: '#0072B2',
  secondary: '#D55E00',
  accent: '#009E73',
  neutral: '#4A4A4A',
  background: '#FFFFFF',
  lightGray: '#F5F5F5',
};
```

## Colorblind Simulation Check

Before finalizing a figure, verify it is accessible:

```bash
# Using matplotlib's colorblind simulation
uvx --from "matplotlib numpy" python -c "
from matplotlib import pyplot as plt
from matplotlib.colors import to_rgba
# Plot your palette swatches and view under simulated CVD
"
```

Online tools: Coblis (color blindness simulator), Color Oracle (desktop app).

## Rules

1. Never rely on color alone; combine with shape, pattern, or label
2. Maximum 7 categorical colors per figure; use shape/marker differentiation beyond that
3. Maintain consistent color assignment across all panels and figures in a paper
4. Test grayscale printability: colors should remain distinguishable in grayscale
5. Avoid pure red (#FF0000) and pure green (#00FF00); use the shifted versions above
