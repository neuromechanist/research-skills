"""End-to-end demo: generate a small AI substrate and overlay labels.

The smoke configuration uses a 1024x1024 size (smallest the OpenAI API accepts
and a reasonable Codex output) and a single label so the API cost is minimal
when api backend is selected. Use --backend codex to skip API costs entirely.

Run from this directory:

    uv run --with openai --with python-dotenv --with pillow \\
        python poster_substrate.py [--backend codex] [--full]

`--full` enlarges the substrate to 1920x1080 and adds three labels — closer
to the real poster-scale workflow but more expensive when using the API.

Output files (created in `out/` next to this script):
    out/brain_substrate.png  AI-generated substrate (opaque PNG)
    out/brain_labeled.svg    overlay SVG with embedded substrate
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SCRIPTS = HERE.parent / "scripts"
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
        "bg": "white",
    },
    "stroke": {"weight_px": 3, "linejoin": "round", "linecap": "round"},
    "style_tokens": [
        "soft watercolor",
        "stylized scientific illustration",
        "centered subject",
    ],
    "negative_tokens": ["text", "labels", "watermark", "arrows", "caption", "3D"],
    "composition": {"aspect": "1:1", "padding_pct": 12, "perspective": "side view"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else "")
    parser.add_argument(
        "--backend", choices=["auto", "codex", "api"], default="auto",
        help="Substrate backend (default: auto; prefers codex).",
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Larger 1920x1080 substrate with three labels (more expensive on API).",
    )
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    substrate = OUT / "brain_substrate.png"
    theme_path = OUT / "theme.json"
    theme_path.write_text(json.dumps(THEME, indent=2))

    size = "1920x1080" if args.full else "1024x1024"
    print(f"\n--- generating substrate ({size}) ---", file=sys.stderr)
    rc = subprocess.run(
        [
            sys.executable, str(SCRIPTS / "generate_figure.py"),
            SUBJECT,
            "-o", str(substrate),
            "--size", size,
            "--backend", args.backend,
            "--theme", str(theme_path),
        ],
        check=False,
    ).returncode
    if rc != 0:
        print(f"substrate generation failed (rc={rc})", file=sys.stderr)
        return rc

    if args.full:
        labels = [
            {"text": "frontal lobe", "x": 380, "y": 320,
             "arrow_to": [560, 420], "font_size_pt": 10, "color": "#1F3A5F"},
            {"text": "parietal lobe", "x": 1000, "y": 200,
             "arrow_to": [900, 360], "font_size_pt": 10, "color": "#1F3A5F"},
            {"text": "cerebellum", "x": 1500, "y": 850,
             "arrow_to": [1350, 760], "font_size_pt": 10, "color": "#E07A5F"},
        ]
        width_mm = 150.0
    else:
        labels = [
            {"text": "primary motor cortex", "x": 700, "y": 200,
             "arrow_to": [560, 380], "font_size_pt": 10, "color": "#1F3A5F"},
        ]
        width_mm = 89.0
    labels_doc = {"width_mm": width_mm, "labels": labels, "scale_bars": []}
    labels_file = OUT / "labels.json"
    labels_file.write_text(json.dumps(labels_doc, indent=2))

    print("\n--- composing overlay SVG ---", file=sys.stderr)
    out_svg = OUT / "brain_labeled.svg"
    rc = subprocess.run(
        [
            sys.executable, str(SCRIPTS / "overlay_labels.py"),
            str(substrate),
            "--labels-file", str(labels_file),
            "-o", str(out_svg),
        ],
        check=False,
    ).returncode
    if rc != 0:
        print(f"overlay failed (rc={rc})", file=sys.stderr)
        return rc

    print(f"\ndone: {out_svg}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
