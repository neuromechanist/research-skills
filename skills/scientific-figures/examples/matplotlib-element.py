#!/usr/bin/env python3
"""Example: Create a publication-quality plot element as SVG.

Usage (on-the-fly, no install):
    uvx --from "matplotlib numpy" python examples/matplotlib-element.py

Output: elements/example_lineplot.svg
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Publication rcParams
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.major.size": 4,
    "ytick.major.size": 4,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 600,
    "savefig.transparent": True,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
})

# Wong colorblind-safe palette
PALETTE = ["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7"]

# Generate example data
np.random.seed(42)
x = np.linspace(0, 2, 100)
y1 = np.sin(2 * np.pi * x) + np.random.normal(0, 0.1, 100)
y2 = np.cos(2 * np.pi * x) + np.random.normal(0, 0.1, 100)

# Smooth for mean lines
window = 10
y1_smooth = np.convolve(y1, np.ones(window) / window, mode="valid")
y2_smooth = np.convolve(y2, np.ones(window) / window, mode="valid")
x_smooth = x[window // 2 : window // 2 + len(y1_smooth)]

# Create figure at single-column width
fig, ax = plt.subplots(figsize=(3.3, 2.5))

ax.plot(x_smooth, y1_smooth, color=PALETTE[3], linewidth=1.2, label="Condition A")
ax.fill_between(x_smooth, y1_smooth - 0.15, y1_smooth + 0.15, alpha=0.2, color=PALETTE[3])

ax.plot(x_smooth, y2_smooth, color=PALETTE[4], linewidth=1.2, label="Condition B")
ax.fill_between(x_smooth, y2_smooth - 0.15, y2_smooth + 0.15, alpha=0.2, color=PALETTE[4])

ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude (uV)")
ax.legend(frameon=False, loc="upper right")

# Save as SVG (vector) for composition
output_dir = Path("elements")
output_dir.mkdir(exist_ok=True)
output = output_dir / "example_lineplot.svg"
plt.savefig(output, bbox_inches="tight", transparent=True)
plt.close()

print(f"Saved: {output}")
