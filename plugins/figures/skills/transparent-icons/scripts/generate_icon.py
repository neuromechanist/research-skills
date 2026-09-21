#!/usr/bin/env python3
"""Generate flat scientific icons via the shared image backend.

Icons always request a transparent background (`prompting.build_icon_prompt`,
which asks for a real alpha channel and falls back to a chroma-key
background only when the model cannot produce transparency directly). After
generation, `--transparency-method auto` (the default) skips local
background removal whenever the returned PNG already has a usable alpha
channel with transparent corners, and otherwise falls back to a Pillow
near-white threshold. `birefnet` (rembg + BiRefNet) remains available as an
opt-in, higher-quality alternative.

Usage:
    # Free-form prompt
    uv run --with pillow python generate_icon.py "a human brain with EEG electrodes" -o brain_eeg.png

    # From template (icon bible), with a shared theme
    uv run --with pillow python generate_icon.py --template brain-eeg -o brain_eeg.png --theme theme.json

    # Batch from template category
    uv run --with pillow python generate_icon.py --category neuroscience -o icons/neuro/

    # Batch from free-form prompt
    uv run --with pillow python generate_icon.py "a flat icon of a {item}" -o icons/ --batch "brain,heart,lung"

    # Force a backend
    uv run --with pillow python generate_icon.py --template neuron --backend codex -o neuron.png

    # List available templates
    uv run --with pillow python generate_icon.py --list-templates

Exit codes: 0 success, 1 generation failure (any icon in a batch), 2 usage error.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path
from typing import Any

_PLUGIN_ROOT = Path(__file__).resolve().parents[3]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib import image_backend, prompting

TEMPLATES_PATH = Path(__file__).parent / "icon-templates.json"


def load_templates(path: Path = TEMPLATES_PATH) -> dict[str, Any]:
    """Load icon templates from the icon bible JSON."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    return {t["id"]: t for t in data.get("templates", [])}


def _template_subject(template: dict[str, Any], color_override: str | None) -> str:
    """Compose the template's structured description into a free-text subject."""
    parts = [template["description"]]
    elems = template.get("elements", [])
    if elems:
        parts.append("Elements: " + "; ".join(e["description"] for e in elems) + ".")
    if color_override:
        parts.append(f"Use exactly this color palette: {color_override}.")
    return " ".join(parts)


def _template_theme(theme: dict | None, template: dict[str, Any]) -> dict:
    """Merge a template's bible palette under a caller theme, without overwriting it."""
    merged = dict(theme or {})
    if not merged.get("palette") and template.get("palette"):
        merged = {**merged, "palette": template["palette"]}
    return merged


def _apply_colors(subject: str, colors: str | None) -> str:
    if colors:
        return f"{subject} Use exactly this color palette: {colors}."
    return subject


def list_templates(templates: dict[str, Any]) -> None:
    categories: dict[str, list[dict[str, Any]]] = {}
    for t in templates.values():
        categories.setdefault(t.get("category", "uncategorized"), []).append(t)
    for cat in sorted(categories):
        print(f"\n  {cat}:")
        for t in sorted(categories[cat], key=lambda x: x["id"]):
            print(f"    {t['id']:25s} {t['name']}")
            print(f"    {'':25s} {t['description'][:70]}")


def _has_real_alpha(png_bytes: bytes) -> bool:
    """True if the PNG already has an alpha channel that is transparent at
    all four corners -- i.e. Codex already returned a clean cutout and any
    further local processing would only damage light strokes."""
    from PIL import Image

    img = Image.open(io.BytesIO(png_bytes))
    if img.mode not in ("RGBA", "LA", "PA"):
        return False
    rgba = img.convert("RGBA")
    w, h = rgba.size
    corners = [
        rgba.getpixel((0, 0)),
        rgba.getpixel((w - 1, 0)),
        rgba.getpixel((0, h - 1)),
        rgba.getpixel((w - 1, h - 1)),
    ]
    return all(c[3] == 0 for c in corners)


def _apply_transparency_threshold(png_bytes: bytes, threshold: int = 240) -> bytes:
    """Drop near-white pixels to transparent. Fast, Pillow-only; can leave a
    fringe on anti-aliased edges and erase near-white foreground highlights."""
    from PIL import Image

    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    data = img.getdata()
    new_data = [
        (r, g, b, 0) if (r > threshold and g > threshold and b > threshold) else (r, g, b, a)
        for r, g, b, a in data
    ]
    img.putdata(new_data)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def _apply_transparency_birefnet(png_bytes: bytes) -> bytes:
    """Remove the background via rembg + BiRefNet (cleaner edges than
    threshold). Requires a one-time ONNX model download (~400 MB)."""
    try:
        from rembg import new_session, remove
    except ImportError as exc:
        raise RuntimeError(
            "Transparency method 'birefnet' requires rembg. Re-run with "
            "--with rembg --with onnxruntime."
        ) from exc
    try:
        session = new_session("birefnet-general")
    except OSError as exc:
        raise RuntimeError(
            "BiRefNet model download failed. Check your network connection and "
            "that $U2NET_HOME (or ~/.u2net) is writable, or re-run with "
            "--transparency-method threshold to skip the model. "
            f"Underlying: {exc}"
        ) from exc
    return remove(
        png_bytes,
        session=session,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
    )


def finalize_transparency(png_path: Path, method: str) -> None:
    """Apply transparency post-processing to png_path in place."""
    data = png_path.read_bytes()
    resolved = method
    if resolved == "auto":
        if _has_real_alpha(data):
            return  # already a clean cutout; re-thresholding would damage light strokes
        resolved = "threshold"
    if resolved == "threshold":
        png_path.write_bytes(_apply_transparency_threshold(data))
    elif resolved == "birefnet":
        png_path.write_bytes(_apply_transparency_birefnet(data))
    else:
        raise ValueError(f"unknown transparency method: {resolved!r}")


def generate_one(
    subject: str,
    out_path: Path,
    *,
    theme: dict | None,
    size: str,
    backend: str,
    codex_bin: str | None,
    transparency_method: str,
    timeout_s: int,
    verbose: bool,
    print_prompt: bool,
) -> float:
    """Generate one icon and apply transparency post-processing. Returns elapsed seconds."""
    prompt = prompting.build_icon_prompt(subject, theme=theme, size=size, chroma=True)
    if print_prompt:
        print(prompt)
    model_prefs = (theme or {}).get("model_preferences") or {}
    req = image_backend.GenerationRequest(
        prompt=prompt,
        out=out_path,
        size=size,
        quality=model_prefs.get("image_quality", "high"),
        n=1,
        model=model_prefs.get("codex_model", image_backend.DEFAULT_MODEL),
        effort=model_prefs.get("codex_effort", image_backend.DEFAULT_EFFORT),
        timeout_s=timeout_s,
        background="transparent",
        verbose=verbose,
        backend=backend,
        codex_bin=codex_bin,
    )
    start = time.monotonic()
    result = image_backend.generate(req)
    finalize_transparency(result.paths[0], transparency_method)
    elapsed = time.monotonic() - start
    print(f"Saved: {result.paths[0]} ({result.backend}, {elapsed:.1f}s)")
    return elapsed


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate flat scientific icons via gpt-image-2.")
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Icon description or template with {item} placeholder",
    )
    parser.add_argument("-o", "--output", help="Output file path or directory (for batch/category)")
    parser.add_argument("--template", help="Template ID from the icon bible (e.g. brain-eeg)")
    parser.add_argument("--category", help="Generate all templates in a category")
    parser.add_argument("--theme", type=Path, help="Path to a theme.json")
    parser.add_argument("--colors", help="Color palette override (e.g. 'teal,coral' or hex codes)")
    parser.add_argument(
        "--size", type=int, default=1024, help="Icon size in pixels (square; default 1024)"
    )
    parser.add_argument(
        "--batch", help="Comma-separated items for batch generation (use {item} in prompt)"
    )
    parser.add_argument("--list-templates", action="store_true")
    parser.add_argument("--templates-file", type=Path, help="Custom templates JSON file")
    parser.add_argument(
        "--transparent",
        action="store_true",
        help="Deprecated no-op: icons always request a transparent background now.",
    )
    parser.add_argument(
        "--transparency-method",
        choices=["auto", "threshold", "birefnet"],
        default="auto",
        help=(
            "'auto' (default) skips local removal when the PNG already has a clean alpha "
            "cutout, else falls back to 'threshold'. 'birefnet' uses rembg (opt-in, "
            "--with rembg --with onnxruntime)."
        ),
    )
    parser.add_argument("--backend", choices=["auto", "codex", "api", "fake"], default="auto")
    parser.add_argument(
        "--codex-bin",
        default=None,
        help="Explicit codex executable path (else $CODEX_BIN, then PATH)",
    )
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--print-prompt", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    templates_path = args.templates_file or TEMPLATES_PATH
    templates = load_templates(templates_path)

    if args.list_templates:
        if not templates:
            print("No templates found.")
        else:
            print("Available icon templates:")
            list_templates(templates)
        return 0

    if not args.prompt and not args.template and not args.category:
        parser.error("Provide a prompt, --template, or --category")
    if not args.output:
        parser.error("--output is required")

    theme: dict | None = None
    if args.theme:
        try:
            theme = json.loads(args.theme.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: could not load theme '{args.theme}': {exc}", file=sys.stderr)
            return 2

    try:
        size = image_backend.validate_size(f"{args.size}x{args.size}")
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    common = {
        "size": size,
        "backend": args.backend,
        "codex_bin": args.codex_bin,
        "transparency_method": args.transparency_method,
        "timeout_s": args.timeout,
        "verbose": args.verbose,
        "print_prompt": args.print_prompt,
    }
    failures = 0

    if args.category:
        cat_templates = [t for t in templates.values() if t.get("category") == args.category]
        if not cat_templates:
            categories = sorted({t.get("category", "") for t in templates.values()})
            print(f"No templates found for category: {args.category}", file=sys.stderr)
            print(f"Available categories: {', '.join(categories)}", file=sys.stderr)
            return 1
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        for t in cat_templates:
            subject = _apply_colors(_template_subject(t, args.colors), None)
            t_theme = _template_theme(theme, t)
            print(f"generating {t['id']}...")
            try:
                generate_one(subject, output_dir / f"{t['id']}.png", theme=t_theme, **common)
            except (image_backend.BackendUnavailable, image_backend.GenerationFailed) as exc:
                print(f"  failed: {exc}", file=sys.stderr)
                failures += 1
        print(f"{len(cat_templates) - failures}/{len(cat_templates)} icons generated")
        return 0 if failures == 0 else 1

    if args.template:
        if args.template not in templates:
            print(f"Template not found: {args.template}", file=sys.stderr)
            print(f"Available: {', '.join(sorted(templates.keys()))}", file=sys.stderr)
            return 1
        t = templates[args.template]
        subject = _template_subject(t, args.colors)
        t_theme = _template_theme(theme, t)
        try:
            generate_one(subject, Path(args.output), theme=t_theme, **common)
        except (image_backend.BackendUnavailable, image_backend.GenerationFailed) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    if args.batch:
        items = [item.strip() for item in args.batch.split(",")]
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        for item in items:
            subject = _apply_colors(args.prompt.replace("{item}", item), args.colors)
            print(f"generating {item}...")
            try:
                generate_one(
                    subject, output_dir / f"{item.replace(' ', '_')}.png", theme=theme, **common
                )
            except (image_backend.BackendUnavailable, image_backend.GenerationFailed) as exc:
                print(f"  failed: {exc}", file=sys.stderr)
                failures += 1
        print(f"{len(items) - failures}/{len(items)} icons generated")
        return 0 if failures == 0 else 1

    subject = _apply_colors(args.prompt, args.colors)
    try:
        generate_one(subject, Path(args.output), theme=theme, **common)
    except (image_backend.BackendUnavailable, image_backend.GenerationFailed) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
