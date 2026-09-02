"""End-to-end demo: generate an AI substrate, overlay labels, and compose the
final figure.

The smoke configuration uses a 1024x1024 substrate and a single label so the
run is cheap when using the API. Use --backend codex to skip API costs
entirely, or --backend fake for a fully offline run.

Run from this directory:

    uv run --with pillow --with svgutils --with lxml --with cairosvg \\
        python poster_substrate.py [--backend codex] [--full]

`--full` enlarges the substrate to 1920x1088 (nearest 16px-multiple to
1920x1080) and adds three labels -- closer to the real poster-scale workflow
but more expensive when using the API.

Output files (created in `out/` next to this script):
    out/theme.json           shared theme bible
    out/brain_substrate.png  AI-generated substrate (opaque PNG)
    out/brain_labeled.svg    overlay SVG with embedded substrate
    out/figure.svg           final composed single-panel figure (mm-exact)
    out/figure.png           rasterized composed figure
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).parent
SCRIPTS = HERE.parent / "scripts"
SCIENTIFIC_FIGURE_SCRIPTS = HERE.parents[1] / "scientific-figure" / "scripts"
OUT = HERE / "out"

SUBJECT = (
    "a stylized lateral view of a human brain in soft watercolor, "
    "subject centered with 12% padding, no labels, no arrows, no text"
)
THEME = {
    "theme_id": "neuro-watercolor-v1",
    "palette": {
        "primary": "#1F3A5F",
        "accent": "#E07A5F",
        "neutral": "#F4F1DE",
        "background": "#FFFFFF",
    },
    "stroke": {"weight_px": 3, "linejoin": "round", "linecap": "round"},
    "style_tokens": [
        "soft watercolor",
        "stylized scientific illustration",
        "centered subject",
    ],
    "negative_tokens": ["text", "labels", "watermark", "arrows", "caption", "3D"],
    "composition": {"aspect": "4:3", "padding_pct": 12, "perspective": "side view"},
    "model_preferences": {
        "codex_model": "gpt-5.6-luna",
        "codex_effort": "xhigh",
        "image_quality": "high",
    },
}


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module {name!r} from {path}")
    module = importlib.util.module_from_spec(spec)
    # Register before exec_module: CPython 3.14's dataclasses implementation
    # looks the module up via sys.modules[cls.__module__] while decorating a
    # @dataclass at import time, which fails with an opaque AttributeError
    # on a module that was never inserted into sys.modules.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _svg_mm_dims(svg_path: Path) -> tuple[float, float]:
    m = re.search(r'width="([\d.]+)mm"\s+height="([\d.]+)mm"', svg_path.read_text())
    if not m:
        raise ValueError(f"could not parse mm dimensions from {svg_path}")
    return float(m.group(1)), float(m.group(2))


def main() -> int:
    import subprocess

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument(
        "--backend",
        choices=["auto", "codex", "api", "fake"],
        default="auto",
        help="Substrate backend (default: auto; prefers codex).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Larger 1920x1088 substrate with three labels (more expensive on API).",
    )
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    substrate = OUT / "brain_substrate.png"
    theme_path = OUT / "theme.json"
    theme_path.write_text(json.dumps(THEME, indent=2))

    size = "1920x1088" if args.full else "1024x1024"
    print(f"\n--- generating substrate ({size}) ---", file=sys.stderr)
    rc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "generate_figure.py"),
            SUBJECT,
            "--out",
            str(substrate),
            "--size",
            size,
            "--backend",
            args.backend,
            "--theme",
            str(theme_path),
        ],
        check=False,
    ).returncode
    if rc != 0:
        print(f"substrate generation failed (rc={rc})", file=sys.stderr)
        return rc

    if args.full:
        labels = [
            {
                "text": "frontal lobe",
                "x": 380,
                "y": 320,
                "arrow_to": [560, 420],
                "font_size_pt": 10,
                "color": "#1F3A5F",
            },
            {
                "text": "parietal lobe",
                "x": 1000,
                "y": 200,
                "arrow_to": [900, 360],
                "font_size_pt": 10,
                "color": "#1F3A5F",
            },
            {
                "text": "cerebellum",
                "x": 1500,
                "y": 850,
                "arrow_to": [1350, 760],
                "font_size_pt": 10,
                "color": "#E07A5F",
            },
        ]
        width_mm = 150.0
    else:
        labels = [
            {
                "text": "primary motor cortex",
                "x": 700,
                "y": 200,
                "arrow_to": [560, 380],
                "font_size_pt": 10,
                "color": "#1F3A5F",
            },
        ]
        width_mm = 89.0
    labels_doc = {"width_mm": width_mm, "labels": labels, "scale_bars": []}
    labels_file = OUT / "labels.json"
    labels_file.write_text(json.dumps(labels_doc, indent=2))

    print("\n--- composing overlay SVG ---", file=sys.stderr)
    out_svg = OUT / "brain_labeled.svg"
    rc = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "overlay_labels.py"),
            str(substrate),
            "--labels-file",
            str(labels_file),
            "-o",
            str(out_svg),
        ],
        check=False,
    ).returncode
    if rc != 0:
        print(f"overlay failed (rc={rc})", file=sys.stderr)
        return rc

    print("\n--- composing final figure ---", file=sys.stderr)
    try:
        w_mm, h_mm = _svg_mm_dims(out_svg)
        compose_mod = _load_module("_poster_compose", SCIENTIFIC_FIGURE_SCRIPTS / "compose.py")
        export_mod = _load_module("_poster_export", SCIENTIFIC_FIGURE_SCRIPTS / "export.py")
        fig = compose_mod.Figure(width_mm=w_mm, height_mm=h_mm)
        fig.add_panel(str(out_svg), x_mm=0, y_mm=0, scale=1.0)
        figure_svg = OUT / "figure.svg"
        fig.save(figure_svg)
    except (ImportError, ValueError, OSError) as exc:
        print(f"compose failed: {exc}", file=sys.stderr)
        return 1

    figure_png = OUT / "figure.png"
    try:
        export_mod.export(figure_svg, figure_png, dpi=300)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"warning: raster export skipped: {exc}", file=sys.stderr)
        print(f"\ndone (without raster export): {figure_svg}", file=sys.stderr)
        return 0

    print(f"\ndone: {figure_png}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
