"""Scaffold a project's figure theme bible (figures/theme.json).

Writes a complete, schema-valid theme.json for one journal/venue profile,
applies any color/typography/prompt overrides from the CLI, validates the
result, and prints a short summary table.

Run from anywhere:

    uv run python init_theme.py --journal nature --out figures/theme.json \\
        [--preset okabe-ito|tol-bright|wong|neuro-flat] \\
        [--primary HEX] [--accent HEX] [--neutral HEX] \\
        [--font Helvetica] [--style "flat vector, minimal"] \\
        [--negative "gradients,shadows"] [--reference img.png ...] \\
        [--codex-model gpt-5.6-luna] [--codex-effort xhigh] [--force]

Add --with jsonschema to get full schema validation; without it, init_theme.py
falls back to lib/theme.py's hand-written structural check.

Exit codes: 0 written and valid, 1 the written theme failed validation
(warnings are printed but do not fail the run), 2 usage/IO error (bad hex,
output exists without --force, unknown journal/preset).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_LIB_DIR = Path(__file__).resolve().parents[3] / "lib"
sys.path.insert(0, str(_LIB_DIR))
try:
    import theme as theme_lib
except ImportError as exc:  # the plugin lib/ directory is missing or broken
    print(
        f"error: cannot import the figures theme library from {_LIB_DIR}: {exc}",
        file=sys.stderr,
    )
    sys.exit(2)

_HEX_RE = re.compile(
    r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$"
)


def _theme_id_from_stem(out: Path) -> str:
    stem = re.sub(r"[^a-z0-9_-]+", "-", out.stem.lower()).strip("-") or "theme"
    if not stem[0].isalnum():
        stem = f"t-{stem}"
    return stem


def _apply_overrides(theme: dict[str, Any], args: argparse.Namespace) -> None:
    palette = theme["palette"]
    for role, value in (
        ("primary", args.primary),
        ("accent", args.accent),
        ("neutral", args.neutral),
    ):
        if value:
            if not _HEX_RE.match(value):
                raise ValueError(f"--{role} '{value}' is not a valid hex color")
            palette[role] = value
    if args.font:
        theme["typography"]["family"] = args.font
    if args.style:
        theme["style_tokens"] = [t.strip() for t in args.style.split(",") if t.strip()]
    if args.negative:
        theme["negative_tokens"] = [
            t.strip() for t in args.negative.split(",") if t.strip()
        ]
    if args.reference:
        theme["reference_images"] = list(args.reference)
    if args.codex_model:
        theme["model_preferences"]["codex_model"] = args.codex_model
    if args.codex_effort:
        theme["model_preferences"]["codex_effort"] = args.codex_effort


def _print_summary(theme: dict[str, Any], out: Path) -> None:
    palette = theme["palette"]
    typography = theme["typography"]
    model_prefs = theme["model_preferences"]
    rows = [
        ("theme_id", theme["theme_id"]),
        ("journal", theme["journal"]),
        (
            "primary / accent / neutral",
            f"{palette['primary']} / {palette['accent']} / {palette['neutral']}",
        ),
        ("categorical", ", ".join(palette.get("categorical", []))),
        ("font / min_pt", f"{typography['family']} / {typography['min_pt']} pt"),
        (
            "codex model / effort / quality",
            f"{model_prefs['codex_model']} / {model_prefs['codex_effort']} / {model_prefs['image_quality']}",
        ),
        ("written to", str(out)),
    ]
    width = max(len(label) for label, _ in rows)
    print(f"figure-bible: wrote {out}")
    for label, value in rows:
        print(f"  {label.ljust(width)} : {value}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a figures/theme.json from a journal profile."
    )
    parser.add_argument(
        "--journal",
        required=True,
        choices=sorted(theme_lib.JOURNAL_PROFILES),
        help="Target venue profile.",
    )
    parser.add_argument(
        "--out", required=True, type=Path, help="Path to write the theme.json."
    )
    parser.add_argument(
        "--preset",
        default="okabe-ito",
        choices=sorted(theme_lib.PALETTE_PRESETS),
        help="Starting palette preset.",
    )
    parser.add_argument("--primary", help="Override the primary color (hex).")
    parser.add_argument("--accent", help="Override the accent color (hex).")
    parser.add_argument("--neutral", help="Override the neutral color (hex).")
    parser.add_argument("--font", help="Typography family, e.g. Helvetica.")
    parser.add_argument(
        "--style", help="Comma-separated style_tokens, replacing the defaults."
    )
    parser.add_argument(
        "--negative", help="Comma-separated negative_tokens, replacing the defaults."
    )
    parser.add_argument(
        "--reference", action="append", help="Reference image path (repeatable)."
    )
    parser.add_argument(
        "--codex-model", default=None, help="Override model_preferences.codex_model."
    )
    parser.add_argument(
        "--codex-effort", default=None, help="Override model_preferences.codex_effort."
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite --out if it already exists."
    )
    args = parser.parse_args(argv)

    if args.out.exists() and not args.force:
        print(
            f"error: {args.out} already exists; pass --force to overwrite.",
            file=sys.stderr,
        )
        return 2

    theme_id = _theme_id_from_stem(args.out)
    try:
        theme = theme_lib.theme_defaults(args.journal, args.preset, theme_id)
        _apply_overrides(theme, args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(theme, indent=2) + "\n")

    problems = theme_lib.validate_theme(theme)
    warnings = [p for p in problems if p.startswith("warning:")]
    errors = [p for p in problems if not p.startswith("warning:")]
    for w in warnings:
        print(f"warning: {w[len('warning: ') :]}", file=sys.stderr)
    if errors:
        print(
            f"error: written theme failed validation ({len(errors)} problem(s)):",
            file=sys.stderr,
        )
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        _print_summary(theme, args.out)
        return 1

    _print_summary(theme, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
