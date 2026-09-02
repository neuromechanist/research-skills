"""Validate a figures/theme.json against schemas/theme.schema.json.

Run from anywhere:

    uv run --with jsonschema python validate_theme.py figures/theme.json [--json]

Without --with jsonschema, falls back to lib/theme.py's hand-written
structural check (still catches missing required keys, bad hex colors, and
unknown enum values; only misses schema-level nuances like extra pattern
constraints).

Exit codes: 0 valid (problems list is empty, or contains only
'warning:'-prefixed contrast notes), 1 invalid (at least one non-warning
problem), 2 usage/IO error (file not found, not valid JSON).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import theme as theme_lib


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a theme.json against the figure-bible schema."
    )
    parser.add_argument("theme", type=Path, help="Path to theme.json.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit {'valid': bool, 'problems': [...], 'checked': [...]}.",
    )
    args = parser.parse_args(argv)

    if not args.theme.exists():
        print(f"error: theme file not found: {args.theme}", file=sys.stderr)
        return 2
    try:
        theme = theme_lib.load_theme(args.theme)
    except (json.JSONDecodeError, TypeError) as exc:
        print(f"error: {args.theme} is not a valid theme.json: {exc}", file=sys.stderr)
        return 2

    problems = theme_lib.validate_theme(theme)
    errors = [p for p in problems if not p.startswith("warning:")]
    warnings = [p for p in problems if p.startswith("warning:")]
    checked = [
        "required keys",
        "hex colors",
        "journal enum",
        "postprocess.bg_removal enum",
        "background/primary contrast",
    ]

    if args.json:
        json.dump(
            {"valid": not errors, "problems": problems, "checked": checked}, sys.stdout, indent=2
        )
        print(file=sys.stdout)
        return 1 if errors else 0

    if errors:
        print(f"INVALID: {args.theme} ({len(errors)} problem(s)):")
        for e in errors:
            print(f"  - {e}")
        for w in warnings:
            print(f"  - {w}")
        return 1

    print(f"OK: {args.theme} is valid. Checked: {', '.join(checked)}.")
    for w in warnings:
        print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
