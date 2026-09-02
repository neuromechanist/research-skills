"""Generate an AI figure or figure panel via the shared image backend.

Unlike a plain substrate script, this generator can render verbatim text
(titles, panel letters, short labels) directly through the Codex/gpt-image-2
`Text (verbatim)` prompt contract -- see `lib/prompting.py`. Long labels,
numerals, units, and equations are rejected by the text ladder and must go
through the SVG overlay (`overlay_labels.py`) or a plotting library instead.

Usage:
    uv run --with pillow python generate_figure.py \\
        "a stylized lateral view of a human brain in soft watercolor" \\
        --out fig.png --size 2048x1024 --theme theme.json \\
        --text "title:top-center:Cortical Recording Setup" \\
        --text "panel-letter:top-left:a"

Edit mode (SUBJECT becomes the edit instruction):
    uv run --with pillow python generate_figure.py \\
        "make the background lighter" --edit fig.png --out fig_v2.png

Exit codes: 0 success, 1 generation failure, 2 usage or text-ladder error.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parents[3]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib import image_backend, prompting


def _parse_text_arg(raw: str) -> prompting.TextItem:
    """Parse '--text ROLE:PLACEMENT:STRING' (STRING may itself contain colons)."""
    parts = raw.split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"--text must be ROLE:PLACEMENT:STRING, got {raw!r}")
    role, placement, text = (p.strip() for p in parts)
    if role not in prompting.VALID_ROLES:
        raise ValueError(f"--text role must be one of {prompting.VALID_ROLES}, got {role!r}")
    if not text:
        raise ValueError(f"--text string must not be empty, got {raw!r}")
    return prompting.TextItem(text=text, role=role, placement=placement or "center")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _resolve_theme_path(
    explicit: Path | None, spec_doc: dict | None, spec_path: Path | None
) -> Path | None:
    if explicit is not None:
        return explicit
    if spec_doc is not None and spec_doc.get("theme"):
        raw = Path(spec_doc["theme"])
        if not raw.is_absolute() and spec_path is not None:
            raw = (spec_path.parent / raw).resolve()
        return raw
    return None


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate an AI figure or figure panel with optional verbatim text."
    )
    parser.add_argument(
        "subject",
        nargs="?",
        default=None,
        help="Figure subject, or the edit instruction when --edit is given.",
    )
    parser.add_argument("--out", type=Path, required=True, help="Output PNG path")
    parser.add_argument(
        "--spec", type=Path, help="Single-panel spec JSON (build_figure schema, first panel)"
    )
    parser.add_argument("--theme", type=Path, help="Path to a theme.json")
    parser.add_argument(
        "--size", default=None, help="'auto' or WIDTHxHEIGHT (edges multiples of 16)"
    )
    parser.add_argument("--quality", default=None, choices=["low", "medium", "high", "auto"])
    parser.add_argument(
        "--text",
        action="append",
        default=[],
        metavar="ROLE:PLACEMENT:STRING",
        help="Repeatable verbatim text item; ROLE is title|panel-letter|label|caption.",
    )
    parser.add_argument(
        "--background",
        choices=["opaque", "transparent", "chroma"],
        default="opaque",
        help="'chroma' is a legacy alias for 'transparent'.",
    )
    parser.add_argument("--layout", default=None, help="Free-text composition/layout hint")
    parser.add_argument("--backend", choices=["auto", "codex", "api", "fake"], default="auto")
    parser.add_argument(
        "--codex-bin",
        default=None,
        help="Explicit codex executable path (else $CODEX_BIN, then PATH)",
    )
    parser.add_argument("--model", default=None)
    parser.add_argument("--effort", default=None)
    parser.add_argument("--n", type=int, default=1, help="Number of candidates to generate")
    parser.add_argument(
        "--ref",
        action="append",
        default=[],
        dest="refs",
        type=Path,
        help="Reference image (repeatable)",
    )
    parser.add_argument(
        "--edit",
        type=Path,
        default=None,
        help="Previous image to edit; SUBJECT becomes the instruction",
    )
    parser.add_argument(
        "--timeout", type=int, default=600, help="Generation timeout in seconds (default: 600)"
    )
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--print-prompt", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    spec_doc: dict | None = None
    if args.spec:
        try:
            spec_doc = _load_json(args.spec)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: could not load spec '{args.spec}': {exc}", file=sys.stderr)
            return 2

    theme_path = _resolve_theme_path(args.theme, spec_doc, args.spec)
    theme: dict | None = None
    if theme_path is not None:
        try:
            theme = _load_json(theme_path)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: could not load theme '{theme_path}': {exc}", file=sys.stderr)
            return 2

    panel: dict | None = None
    if spec_doc is not None:
        panels = spec_doc.get("panels") or []
        if not panels:
            print(f"error: spec '{args.spec}' has no panels", file=sys.stderr)
            return 2
        panel = panels[0]

    if args.edit:
        if not args.subject:
            print("error: --edit requires SUBJECT to be the edit instruction", file=sys.stderr)
            return 2
        instruction = args.subject
        subject = None
    else:
        instruction = None
        subject = (
            args.subject
            or (panel.get("subject") if panel else None)
            or (spec_doc.get("subject") if spec_doc else None)
        )
        if not subject:
            print("error: a subject is required (positional argument or --spec)", file=sys.stderr)
            return 2

    text_items: list[prompting.TextItem] = []
    try:
        for raw in args.text:
            text_items.append(_parse_text_arg(raw))
        if panel is not None:
            for t in panel.get("text", []):
                text_items.append(
                    prompting.TextItem(
                        text=t["text"],
                        role=t.get("role", "label"),
                        placement=t.get("placement", "center"),
                        size_class=t.get("size_class"),
                        style=t.get("style"),
                    )
                )
    except (ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.edit:
        try:
            prompting.enforce_text_ladder(text_items, theme)
        except prompting.TextLadderError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    model_prefs = (theme or {}).get("model_preferences") or {}
    size_req = (
        args.size
        or (panel.get("size") if panel else None)
        or (spec_doc.get("size") if spec_doc else None)
        or "auto"
    )
    try:
        size = image_backend.validate_size(size_req)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    quality = (
        args.quality
        or (spec_doc.get("quality") if spec_doc else None)
        or model_prefs.get("image_quality")
        or "high"
    )
    model = args.model or model_prefs.get("codex_model") or image_backend.DEFAULT_MODEL
    effort = args.effort or model_prefs.get("codex_effort") or image_backend.DEFAULT_EFFORT

    if args.edit:
        prompt_text = instruction
    else:
        layout = args.layout or (panel.get("layout") if panel else None)
        prompt_text = prompting.build_figure_prompt(
            subject,
            theme=theme,
            text=text_items,
            size=size,
            quality=quality,
            background=args.background,
            layout=layout,
            extra_avoid=[],
        )

    if args.print_prompt:
        print(prompt_text)

    background_color = ((theme or {}).get("palette") or {}).get("background") or "#FFFFFF"

    start = time.monotonic()
    try:
        if args.edit:
            result = image_backend.edit(
                args.edit,
                instruction,
                args.out,
                backend=args.backend,
                model=model,
                effort=effort,
                timeout_s=args.timeout,
                verbose=args.verbose,
                size=size,
                quality=quality,
                codex_bin=args.codex_bin,
            )
        else:
            req = image_backend.GenerationRequest(
                prompt=prompt_text,
                out=args.out,
                size=size,
                quality=quality,
                n=max(1, args.n),
                references=list(args.refs),
                model=model,
                effort=effort,
                timeout_s=args.timeout,
                background=args.background,
                background_color=background_color,
                verbose=args.verbose,
                backend=args.backend,
                codex_bin=args.codex_bin,
            )
            result = image_backend.generate(req)
    except image_backend.BackendUnavailable as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except image_backend.GenerationFailed as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    elapsed = time.monotonic() - start
    for p in result.paths:
        print(p)
    print(f"elapsed: {elapsed:.1f}s ({result.backend})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
