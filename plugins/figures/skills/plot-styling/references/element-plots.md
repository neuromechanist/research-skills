# Creating Plot Elements for Scientific Figures

Generate individual plot panels as SVG or transparent PNG for composition into multi-panel figures. All plots run on-the-fly via `uvx` (Python) or `Rscript` (R); no permanent installs.

## General Rules

1. Save as SVG (preferred) or PNG at 600 DPI with `transparent=True`
2. Use `bbox_inches='tight'` to eliminate whitespace
3. Sans-serif font (Helvetica/Arial), 9-10pt for labels, 8-9pt for ticks
4. Remove top and right spines (clean L-shaped axes)
5. Tick marks face outward
6. Match the figure's shared color palette (see `color-palettes.md`)
7. No chart junk: minimal gridlines, no 3D effects, no unnecessary decoration

## matplotlib Setup

### Base Configuration

```python
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 9,
    'axes.titlesize': 10,
    'axes.labelsize': 9,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'axes.linewidth': 0.8,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 150,
    'savefig.dpi': 600,
    'savefig.transparent': True,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.02,
})
```

### Running via uvx

```bash
uvx --from "matplotlib numpy" python -c "
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# rcParams setup (as above, inline)
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})

fig, ax = plt.subplots(figsize=(3.5, 2.5))  # single-column width
# ... plot code ...
plt.savefig('elements/plot.svg', bbox_inches='tight', transparent=True)
plt.close()
"
```

### Common Plot Types

#### Line plot with error bands
```python
fig, ax = plt.subplots(figsize=(3.5, 2.5))
ax.plot(x, y_mean, color='#0072B2', linewidth=1.2, label='Condition A')
ax.fill_between(x, y_mean - y_sem, y_mean + y_sem, alpha=0.2, color='#0072B2')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude (uV)')
ax.legend(frameon=False)
plt.savefig('elements/lineplot.svg', bbox_inches='tight', transparent=True)
```

#### Bar plot with error bars
```python
fig, ax = plt.subplots(figsize=(3.0, 2.5))
bars = ax.bar(categories, values, yerr=errors, color=PALETTE[:len(categories)],
              edgecolor='none', capsize=3, error_kw={'linewidth': 0.8})
ax.set_ylabel('Metric (units)')
plt.savefig('elements/barplot.svg', bbox_inches='tight', transparent=True)
```

#### Scatter plot
```python
fig, ax = plt.subplots(figsize=(3.0, 3.0))
ax.scatter(x, y, c='#0072B2', s=20, alpha=0.7, edgecolors='none')
ax.set_xlabel('Variable X (units)')
ax.set_ylabel('Variable Y (units)')
plt.savefig('elements/scatter.svg', bbox_inches='tight', transparent=True)
```

#### Heatmap
```python
fig, ax = plt.subplots(figsize=(3.5, 3.0))
im = ax.imshow(matrix, cmap='viridis', aspect='auto')
cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.ax.tick_params(labelsize=7)
plt.savefig('elements/heatmap.svg', bbox_inches='tight', transparent=True)
```

#### Box plot
```python
fig, ax = plt.subplots(figsize=(3.5, 2.5))
bp = ax.boxplot(
    [group_a, group_b, group_c],
    labels=['Control', 'Treatment A', 'Treatment B'],
    patch_artist=True,
    widths=0.6,
    medianprops=dict(color='black', linewidth=1.0),
    boxprops=dict(linewidth=0.8),
    whiskerprops=dict(linewidth=0.8),
    capprops=dict(linewidth=0.8),
    flierprops=dict(marker='o', markersize=3, markerfacecolor='#999999', alpha=0.5),
)
for patch, color in zip(bp['boxes'], PALETTE[:3]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_ylabel('Measurement (units)')
plt.savefig('elements/boxplot.svg', bbox_inches='tight', transparent=True)
```

#### Survival curve (Kaplan-Meier)
```python
# Requires: uvx --from "matplotlib numpy lifelines" python -c "..."
from lifelines import KaplanMeierFitter

fig, ax = plt.subplots(figsize=(3.5, 2.5))
kmf = KaplanMeierFitter()

for i, (label, T, E) in enumerate(groups):
    kmf.fit(T, event_observed=E, label=label)
    kmf.plot_survival_function(
        ax=ax, color=PALETTE[i], linewidth=1.2, ci_show=True, ci_alpha=0.15
    )

ax.set_xlabel('Time (months)')
ax.set_ylabel('Survival probability')
ax.set_ylim(0, 1.05)
ax.legend(frameon=False, fontsize=8)
plt.savefig('elements/survival.svg', bbox_inches='tight', transparent=True)
```

#### Volcano plot (genomics/proteomics)
```python
fig, ax = plt.subplots(figsize=(3.5, 3.0))

# Classify points: significant up, significant down, not significant
sig_up = (log2fc > fc_thresh) & (neg_log10p > p_thresh)
sig_down = (log2fc < -fc_thresh) & (neg_log10p > p_thresh)
ns = ~sig_up & ~sig_down

ax.scatter(log2fc[ns], neg_log10p[ns], c='#999999', s=8, alpha=0.4, edgecolors='none', label='NS')
ax.scatter(log2fc[sig_up], neg_log10p[sig_up], c='#D55E00', s=12, alpha=0.7, edgecolors='none', label='Up')
ax.scatter(log2fc[sig_down], neg_log10p[sig_down], c='#0072B2', s=12, alpha=0.7, edgecolors='none', label='Down')

ax.axhline(y=p_thresh, color='#999999', linestyle='--', linewidth=0.5)
ax.axvline(x=fc_thresh, color='#999999', linestyle='--', linewidth=0.5)
ax.axvline(x=-fc_thresh, color='#999999', linestyle='--', linewidth=0.5)

ax.set_xlabel('log2(Fold Change)')
ax.set_ylabel('-log10(p-value)')
ax.legend(frameon=False, fontsize=8, markerscale=1.5)
plt.savefig('elements/volcano.svg', bbox_inches='tight', transparent=True)
```

## seaborn Setup

```bash
uvx --from "matplotlib seaborn numpy pandas" python -c "
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

sns.set_theme(style='ticks', context='paper', font='Helvetica',
              rc={'axes.spines.top': False, 'axes.spines.right': False,
                  'font.size': 9, 'axes.linewidth': 0.8})

# ... plot code ...
sns.despine()
plt.savefig('elements/plot.svg', bbox_inches='tight', transparent=True)
"
```

### Common seaborn Patterns

#### Violin + strip plot
```python
fig, ax = plt.subplots(figsize=(3.5, 2.5))
sns.violinplot(data=df, x='group', y='value', palette=PALETTE, inner=None, ax=ax)
sns.stripplot(data=df, x='group', y='value', color='black', size=2, alpha=0.5, ax=ax)
sns.despine()
```

#### Regression plot
```python
fig, ax = plt.subplots(figsize=(3.0, 3.0))
sns.regplot(data=df, x='x', y='y', color='#0072B2', scatter_kws={'s': 15, 'alpha': 0.6}, ax=ax)
sns.despine()
```

## plotly (Static Export)

```bash
uvx --from "plotly kaleido pandas" python -c "
import plotly.graph_objects as go
import plotly.io as pio

fig = go.Figure()
# ... add traces ...

fig.update_layout(
    font=dict(family='Helvetica', size=9),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    width=250, height=180,
    margin=dict(l=40, r=10, t=10, b=40),
)
fig.write_image('elements/plot.svg')
"
```

## ggplot2 (R)

```bash
Rscript -e '
library(ggplot2)

theme_publication <- function(base_size = 9, base_family = "Helvetica") {
  theme_classic(base_size = base_size, base_family = base_family) %+replace%
    theme(
      axis.line = element_line(linewidth = 0.4, color = "black"),
      axis.ticks = element_line(linewidth = 0.4, color = "black"),
      axis.text = element_text(size = rel(0.9), color = "black"),
      axis.title = element_text(size = rel(1.0)),
      legend.background = element_blank(),
      legend.key = element_blank(),
      legend.text = element_text(size = rel(0.85)),
      panel.background = element_blank(),
      plot.background = element_blank(),
      strip.background = element_blank()
    )
}

wong_colors <- c("#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

p <- ggplot(data, aes(x, y, color = group)) +
  geom_point(size = 1.5) +
  scale_color_manual(values = wong_colors) +
  theme_publication() +
  labs(x = "Variable X (units)", y = "Variable Y (units)")

ggsave("elements/plot.svg", p, width = 3.5, height = 2.5, units = "in")
'
```

## Element Sizing Guidelines

Match element size to its panel allocation in the final figure:

| Figure width | Panel width (2-col) | Element figsize |
|-------------|--------------------|-----------------|
| Single column (3.5in) | 3.5in (full) | (3.3, 2.5) |
| Double column (7.0in) | 3.3in (half) | (3.1, 2.5) |
| Double column (7.0in) | 7.0in (full row) | (6.8, 2.5) |

Leave slight margin (0.1-0.2in) for panel label and spacing in the final composition.

## Output Format Decision

| Format | When to Use |
|--------|------------|
| SVG | Default for all plots (vector, scalable, editable) |
| PNG (600 DPI) | When SVG rendering is inconsistent or for photographic overlays |
| PDF | When going directly into LaTeX or as standalone figure |

Always save SVG first. Convert to PNG only if needed for react-pdf composition (react-pdf supports PNG and JPG for `Image` components).
