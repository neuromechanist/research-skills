# Library Decision Tree

Which Python plotting library should I use for *this* chart type? The decision tree below mirrors the logic in `figure-qa`'s `check_plot_script.py` (which suggests a library switch when matplotlib is being used for a chart type that has a better-defaults alternative).

## Step 1: the chart type

Decide before opening Python. The chart type is the strongest signal.

### Line plots, scatter plots, custom bar plots, anything with a layout you control

**matplotlib + SciencePlots.** Apply `plt.style.use(['science', 'nature'])` and start with `fig, ax = plt.subplots(figsize=(3.5, 2.5))`.

```python
import numpy as np
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401

plt.style.use(["science", "nature"])
fig, ax = plt.subplots(figsize=(3.5, 2.5))
ax.plot(np.arange(10), np.arange(10) ** 0.5, label="sqrt")
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(frameon=False)
fig.savefig("panel.svg", bbox_inches="tight", transparent=True)
```

### Statistical plots: box, violin, regression, swarm, faceted distributions

**seaborn.** Much less code than matplotlib for the same result; defaults to colorblind-safe palettes; built on matplotlib so SciencePlots still applies.

```python
import seaborn as sns
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401

plt.style.use(["science", "nature"])
penguins = sns.load_dataset("penguins")
fig, ax = plt.subplots(figsize=(3.5, 2.5))
sns.violinplot(data=penguins, x="species", y="body_mass_g", ax=ax)
ax.set_xlabel(""); ax.set_ylabel("body mass (g)")
fig.savefig("panel.svg", bbox_inches="tight", transparent=True)
```

When `figure-qa` sees `matplotlib.boxplot` / `matplotlib.violinplot` / `seaborn.regplot` etc. without a seaborn import, it suggests the switch. Take the suggestion.

### Grammar-of-graphics / R-style faceted plots

**plotnine.** Same `geom_*` API as ggplot2 with no R bridge.

```python
from plotnine import ggplot, aes, geom_point, geom_smooth, theme_minimal, facet_wrap
import pandas as pd

df = pd.DataFrame({"x": [...], "y": [...], "group": [...]})
p = (
    ggplot(df, aes(x="x", y="y", color="group"))
    + geom_point()
    + geom_smooth(method="loess")
    + facet_wrap("group")
    + theme_minimal()
)
p.save("panel.svg", width=3.5, height=2.5, dpi=300)
```

If a script uses `geom_*` calls or contains the literal string `"ggplot"`, `check_plot_script.py` recommends plotnine. Avoid rpy2 + ggplot2 unless the team is already in an R workflow.

### Interactive HTML companion (slide deck, dashboard, supplement)

**plotly.** Generate the interactive version for HTML and a matplotlib version for print:

```python
import plotly.express as px
fig = px.scatter(df, x="x", y="y", color="group")
fig.write_html("supplement.html")
# Print version: re-author with matplotlib + SciencePlots
```

Don't ship plotly's static export to a print journal — its default fonts and chart-junk profile aren't what reviewers expect.

### 3D, volumetric, mesh

**PyVista** when the user *interacts* with the rendering (rotation, slicing); **matplotlib 3d** for static panels.

```python
# Static print panel
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401
plt.style.use(["science"])
fig = plt.figure(figsize=(3.5, 3.0))
ax = fig.add_subplot(projection="3d")
# ... plot ...
fig.savefig("panel.svg", bbox_inches="tight", transparent=True)
```

```python
# Interactive
import pyvista as pv
plotter = pv.Plotter()
# ... plotter.add_mesh, plotter.show ...
plotter.export_html("supplement.html")
```

`check_plot_script.py` detects `pyvista` imports but does not (yet) flag missing journal-print sibling — author both yourself.

### Heatmap with row/column annotations

**seaborn.clustermap** is the canonical journal heatmap. Even when not clustering, it produces tidier defaults than `matplotlib.imshow` + manual colorbar.

```python
import seaborn as sns
g = sns.clustermap(df.corr(), cmap="vlag", vmin=-1, vmax=1, figsize=(3.5, 3.5),
                   cbar_pos=(0.02, 0.8, 0.05, 0.18))
g.savefig("panel.svg", bbox_inches="tight", transparent=True)
```

### Specialty: brain plots, EEG topographies

Use a domain-specific library: `MNE-Python` for EEG topographies, `nilearn.plotting` for fMRI projections, `wordcloud` for text corpus visualization. These are out of scope for the decision tree here — author with the canonical domain plotter, save as SVG, and compose with `scientific-figure`.

## Step 2: stay vs switch

When `check_plot_script.py` recommends a library switch, weigh:

- **Switching is cheap** when the chart is < 20 lines of matplotlib that can be replaced by 4 lines of seaborn or plotnine.
- **Switching is expensive** when there are custom annotations, multi-axis layouts, or specific tick/grid behavior that the higher-level library doesn't expose directly.
- **Staying** is fine if matplotlib + SciencePlots already produces a journal-acceptable result — the recommendation is advice, not a blocker.

The skill flags the choice; the user makes the call.

## Step 3: don't ignore the journal's style

A `plotly` plot exported to SVG with default Times fonts will be rejected by Nature (sans-serif required). A matplotlib plot without SciencePlots will pass technical review but read as undergraduate-quality next to a properly-styled neighbor panel. The journal style sheet (`science`, `nature`, `ieee`) carries this weight automatically — applying it is a one-line cost for a several-paragraph quality gain.

See `references/sciplots-recipes.md` for per-journal style sheets and the rcParams they set.
