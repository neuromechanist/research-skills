"""Generate a small, style-consistent icon set with a shared theme.

Run from the example directory:

    uv run --with pillow python icon_set.py

Generates three transparent PNG icons (brain, neuron, DNA) in `out/` next to
this script, from a single `theme.json`. Subjects and the theme are passed
straight through to `generate_icon.py`, which builds the actual verbatim
prompt via `lib.prompting.build_icon_prompt` -- this script does not
pre-build a prompt string itself, so the theme is applied exactly once.

The Codex CLI backend is used by default (preferred when `codex login` is
configured); the script falls back to the OpenAI Images API when Codex is
unavailable, or to the offline fake backend with `--backend fake`.

Smoke-test variant: pass --smoke to generate only the first icon (cheaper for
verification runs).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SCRIPTS = HERE.parent / "scripts"
OUT = HERE / "out"

THEME = {
    "theme_id": "neuro-flat-v1",
    "palette": {
        "primary": "#1F3A5F",
        "accent": "#E07A5F",
        "neutral": "#F4F1DE",
        "background": "transparent",
    },
    "stroke": {"weight_px": 4, "linejoin": "round", "linecap": "round"},
    "style_tokens": [
        "flat 2D",
        "single continuous line",
        "two-color palette",
        "no shading",
        "centered",
    ],
    "negative_tokens": ["text", "labels", "watermark", "gradient", "3D", "shadow"],
    "composition": {"aspect": "1:1", "padding_pct": 12, "perspective": "orthographic"},
    "model_preferences": {
        "codex_model": "gpt-5.6-luna",
        "codex_effort": "xhigh",
        "image_quality": "high",
    },
}

ICONS = [
    ("brain.png", "a human brain, simple anatomical outline"),
    ("neuron.png", "a single neuron with cell body, axon, and three dendrites"),
    ("dna.png", "a double-helix DNA strand seen from the side"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a style-consistent icon set.")
    parser.add_argument(
        "--smoke", action="store_true", help="Generate only the first icon (smoke test)"
    )
    parser.add_argument(
        "--transparency-method",
        choices=["auto", "threshold", "birefnet"],
        default="auto",
        help="Background-removal method (default: auto).",
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "codex", "api", "fake"],
        default="auto",
        help="Image generation backend (default: auto; prefers codex when authenticated).",
    )
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    theme_path = OUT / "theme.json"
    try:
        theme_path.write_text(json.dumps(THEME, indent=2))
    except OSError as exc:
        print(f"error: could not write theme file {theme_path}: {exc}", file=sys.stderr)
        return 1
    print(f"wrote theme: {theme_path}")

    targets = ICONS[:1] if args.smoke else ICONS
    failures = 0
    for filename, subject in targets:
        out_path = OUT / filename
        print(f"\ngenerating {filename} (subject: {subject})")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "generate_icon.py"),
                subject,
                "-o",
                str(out_path),
                "--theme",
                str(theme_path),
                "--transparency-method",
                args.transparency_method,
                "--backend",
                args.backend,
            ],
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ},
        )
        if result.stdout.strip():
            print(result.stdout.rstrip())
        if result.stderr.strip():
            print(result.stderr.rstrip(), file=sys.stderr)
        if result.returncode != 0:
            print(f"  failed (rc={result.returncode})", file=sys.stderr)
            failures += 1

    print()
    print(f"{len(targets) - failures}/{len(targets)} icons generated; outputs in {OUT}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
