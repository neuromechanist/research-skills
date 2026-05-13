"""SciencePlots-styled matplotlib panel.

Demonstrates the recommended pattern:
- Nature column width (89 mm = 3.5 in)
- science + nature style sheet for journal defaults
- bright palette for colorblind-safe series colors
- svg.fonttype = 'none' so validate_fonts.py can inspect every <text>
- transparent=True, bbox_inches='tight' on savefig

Run:

    uv run --with matplotlib --with numpy --with scienceplots \\
        python sciplots_panel.py

Output: ./out/sciplots_panel.svg
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import scienceplots  # noqa: F401  (registers the style sheet)

HERE = Path(__file__).parent
OUT = HERE / "out"

WIDTH_IN = 3.5    # 89 mm
HEIGHT_IN = 2.5   # ~63 mm


def main() -> int:
    OUT.mkdir(exist_ok=True)

    # `no-latex` is critical here: SciencePlots' `science` style sets
    # text.usetex=True by default, which makes matplotlib render SVG text as
    # paths even when svg.fonttype="none". validate_fonts.py can only inspect
    # <text> elements, so paths bypass font validation silently. `no-latex`
    # switches to matplotlib's built-in mathtext (no LaTeX install required)
    # and preserves text-as-<text> in the SVG output.
    plt.style.use(["science", "nature", "bright", "no-latex"])
    plt.rcParams.update({
        "svg.fonttype": "none",   # keep <text> elements for validate_fonts.py
    })

    fig, ax = plt.subplots(figsize=(WIDTH_IN, HEIGHT_IN))

    t = np.linspace(0, 1, 400)
    for k, label in enumerate(("control", "drug A", "drug B")):
        ax.plot(
            t,
            np.sin(2 * np.pi * (k + 1) * t) * np.exp(-1.0 * t),
            label=label,
            linewidth=1.0,
        )
    ax.set_xlabel("time (s)")
    ax.set_ylabel("response (a.u.)")
    ax.set_xlim(0, 1)
    ax.legend(frameon=False, loc="upper right")

    out = OUT / "sciplots_panel.svg"
    fig.savefig(out, bbox_inches="tight", transparent=True)
    plt.close(fig)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
