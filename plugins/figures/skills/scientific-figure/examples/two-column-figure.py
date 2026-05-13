"""End-to-end example: two matplotlib panels composed into a Nature 2-column figure.

Run from the example directory:

    uv run \\
        --with matplotlib --with numpy --with svgutils --with lxml --with cairosvg \\
        python two-column-figure.py

Output files (created in `out/` next to this script):
    panels/spectrum.svg   matplotlib panel A
    panels/timeseries.svg matplotlib panel B
    figure.svg            composed figure (183mm x 70mm)
    figure.pdf            exported PDF (Inkscape if available, cairosvg otherwise)
    font_report.json      validate_fonts.py output

The panels are tuned so that everything passes Nature's 5 pt font minimum. To
intentionally trigger a validation failure, set SOURCE_FONT_PT below to 6
(produces 3 pt effective at scale 0.5).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).parent
SCRIPTS = HERE.parent / "scripts"
OUT = HERE / "out"
PANELS = OUT / "panels"

WIDTH_MM = 183.0          # Nature 2-column
HEIGHT_MM = 70.0
PANEL_W_MM = 90.0
PANEL_H_MM = 70.0
GUTTER_MM = 3.0
SOURCE_FONT_PT = 12.0     # Panels saved at 12 pt; scaled by 0.5 -> 6 pt effective (passes Nature/Science)
PANEL_SCALE = 0.5


def _mpl_setup() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
            "font.size": SOURCE_FONT_PT,
            "axes.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "svg.fonttype": "none",  # keep <text> elements in SVG so validate_fonts.py can read them
        }
    )


def _save_spectrum(path: Path) -> None:
    # Source panel sized at 2 x final panel (svgutils will scale by 0.5)
    fig, ax = plt.subplots(figsize=(PANEL_W_MM * 2 / 25.4, PANEL_H_MM * 2 / 25.4))
    freqs = np.linspace(0.5, 50, 500)
    psd = 10 / (freqs + 1) + 0.5 * np.exp(-((freqs - 10) ** 2) / 8)
    ax.plot(freqs, psd, color="#0072B2", linewidth=1.2)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power (dB)")
    ax.set_xlim(0, 50)
    fig.tight_layout()
    fig.savefig(path, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)


def _save_timeseries(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(PANEL_W_MM * 2 / 25.4, PANEL_H_MM * 2 / 25.4))
    t = np.linspace(0, 2, 500)
    signal = np.sin(2 * np.pi * 4 * t) * np.exp(-t) + np.random.RandomState(0).normal(0, 0.05, size=t.size)
    ax.plot(t, signal, color="#D55E00", linewidth=0.8)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_xlim(0, 2)
    fig.tight_layout()
    fig.savefig(path, format="svg", bbox_inches="tight", transparent=True)
    plt.close(fig)


def _compose() -> Path:
    sys.path.insert(0, str(SCRIPTS))
    from compose import Figure  # type: ignore[import-not-found]

    out_svg = OUT / "figure.svg"
    (
        Figure(width_mm=WIDTH_MM, height_mm=HEIGHT_MM, journal="nature")
        .add_panel(PANELS / "spectrum.svg", x_mm=0, y_mm=0, scale=PANEL_SCALE, label="A")
        .add_panel(
            PANELS / "timeseries.svg",
            x_mm=PANEL_W_MM + GUTTER_MM,
            y_mm=0,
            scale=PANEL_SCALE,
            label="B",
        )
        .save(out_svg)
    )
    return out_svg


def _validate(svg: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_fonts.py"), str(svg), "--journal", "nature"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    report = json.loads(result.stdout)
    (OUT / "font_report.json").write_text(json.dumps(report, indent=2))
    return report


def _export(svg: Path) -> Path:
    out_pdf = OUT / "figure.pdf"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "export.py"), str(svg), "--out", str(out_pdf)],
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    return out_pdf


def main() -> int:
    OUT.mkdir(exist_ok=True)
    PANELS.mkdir(exist_ok=True)

    _mpl_setup()
    _save_spectrum(PANELS / "spectrum.svg")
    _save_timeseries(PANELS / "timeseries.svg")
    print(f"wrote {PANELS}/spectrum.svg and timeseries.svg")

    svg = _compose()
    print(f"composed {svg}")

    report = _validate(svg)
    if report["issue_count"]:
        print(f"font validation: {report['issue_count']} issue(s); see {OUT}/font_report.json", file=sys.stderr)
    else:
        print(f"font validation: all {report['checked_count']} text elements pass Nature 5 pt minimum")

    pdf = _export(svg)
    print(f"exported {pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
