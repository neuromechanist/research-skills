"""svgutils-based figure composer for scientific-figure skill.

Two interfaces:

1. Library: import the Figure helper.

       from compose import Figure
       (Figure(width_mm=183, height_mm=120, journal="nature")
           .add_panel("panels/a.svg", x_mm=0,  y_mm=0,  scale=0.5, label="A")
           .add_panel("panels/b.svg", x_mm=92, y_mm=0,  scale=0.5, label="B")
           .save("figure.svg"))

2. CLI: a JSON config file describes the figure.

       uv run --with svgutils --with lxml python compose.py config.json -o figure.svg

   Config schema:
       {
         "width_mm": 183,
         "height_mm": 120,
         "journal": "nature",                       # optional; informs validator hint in SVG
         "panels": [
           {"src": "panels/a.svg", "x_mm": 0,  "y_mm": 0, "scale": 0.5, "label": "A"},
           {"src": "panels/b.svg", "x_mm": 92, "y_mm": 0, "scale": 0.5, "label": "B"}
         ]
       }

Panel labels are placed at top-left of each panel in 12 pt bold sans-serif.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from svgutils.compose import SVG, Figure as SvgFigure, Panel, Text


PANEL_LABEL_PT = 12
PANEL_LABEL_OFFSET_MM = (2.0, 4.0)  # x, y from panel origin


@dataclass
class Figure:
    """High-level wrapper around svgutils.compose.Figure with mm units and panel labels."""

    width_mm: float
    height_mm: float
    journal: str | None = None
    _panels: list[Panel] = field(default_factory=list)

    def add_panel(
        self,
        src: str | Path,
        x_mm: float,
        y_mm: float,
        scale: float = 1.0,
        label: str | None = None,
    ) -> Figure:
        """Place an SVG at (x_mm, y_mm) with the given scale; optionally add a panel label."""
        src_path = Path(src)
        if not src_path.exists():
            raise FileNotFoundError(f"panel source not found: {src_path}")

        elements = [SVG(str(src_path)).scale(scale)]
        if label:
            lx, ly = PANEL_LABEL_OFFSET_MM
            elements.append(Text(label, lx, ly, size=PANEL_LABEL_PT, weight="bold"))

        panel = Panel(*elements).move(x_mm, y_mm)
        self._panels.append(panel)
        return self

    def save(self, out_path: str | Path) -> Path:
        out_path = Path(out_path)
        fig = SvgFigure(f"{self.width_mm}mm", f"{self.height_mm}mm", *self._panels)
        if self.journal:
            # Embed a hint the validator can read back without inspecting the config.
            fig.root.set("data-journal", self.journal)
        fig.save(str(out_path))
        return out_path


def from_config(config: dict) -> Figure:
    fig = Figure(
        width_mm=float(config["width_mm"]),
        height_mm=float(config["height_mm"]),
        journal=config.get("journal"),
    )
    for panel in config.get("panels", []):
        fig.add_panel(
            src=panel["src"],
            x_mm=float(panel["x_mm"]),
            y_mm=float(panel["y_mm"]),
            scale=float(panel.get("scale", 1.0)),
            label=panel.get("label"),
        )
    return fig


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compose a multi-panel SVG figure at exact mm dimensions.")
    parser.add_argument("config", type=Path, help="JSON config file describing the figure")
    parser.add_argument("-o", "--out", type=Path, required=True, help="Output SVG path")
    args = parser.parse_args(argv)

    with args.config.open() as fh:
        config = json.load(fh)

    fig = from_config(config)
    out = fig.save(args.out)
    print(f"wrote {out} ({fig.width_mm}mm x {fig.height_mm}mm, {len(fig._panels)} panel(s))", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
