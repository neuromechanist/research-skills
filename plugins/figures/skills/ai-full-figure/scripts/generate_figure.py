"""Generate an AI substrate image (full figure pictorial layer).

Targets full-HD-ish dimensions for posters/presentations. Unlike the
transparent-icons generator, this script does NOT post-process for
transparency — substrates are opaque by design and form the bottom
layer that overlay_labels.py places text/arrows on.

Two backends:
  1. codex  -- Codex CLI image_gen tool. Preferred when `codex login` is
              configured. No OPENAI_API_KEY needed.
  2. api    -- OpenAI Images API. Requires OPENAI_API_KEY.

Usage:
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_figure.py \\
        "a stylized lateral view of a human brain in soft watercolor on a clean white background" \\
        -o out/brain_substrate.png \\
        --size 1920x1080 --backend codex \\
        [--theme path/to/theme.json]

Size accepts `WxH` strings. The OpenAI Images API quantizes to a closed
set of sizes (1024x1024, 1024x1536, 1536x1024, 2048x2048); we snap to
the nearest supported size and warn if the requested size differs.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    print(
        "Missing dependency: python-dotenv. Re-run with --with python-dotenv.",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # api backend unavailable; codex backend may still work


load_dotenv()
load_dotenv(Path.home() / ".env")


# OpenAI Images API accepts these size strings; we snap requests to the nearest.
API_SIZES = {
    "1024x1024",
    "1024x1536",
    "1536x1024",
    "2048x2048",
}


def _parse_size(s: str) -> tuple[int, int]:
    """Parse a 'WxH' string into a (width, height) tuple."""
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except (ValueError, AttributeError) as exc:
        raise ValueError(
            f"size must be in 'WxH' form (e.g. '1920x1080'), got '{s}'"
        ) from exc


def _snap_to_api_size(w: int, h: int) -> str:
    """Pick the nearest OpenAI-Images-accepted size string by area + aspect."""
    target_ratio = w / h
    best = "1024x1024"
    best_score = float("inf")
    for s in API_SIZES:
        sw, sh = (int(x) for x in s.split("x"))
        ratio_diff = abs(sw / sh - target_ratio)
        area_diff = abs(sw * sh - w * h) / (sw * sh)
        score = ratio_diff + 0.5 * area_diff
        if score < best_score:
            best_score = score
            best = s
    return best


def _build_prompt(subject: str, theme: dict | None) -> str:
    """Compose the final prompt from the subject and optional theme bible."""
    parts = [subject.strip(".") + "."]
    if not theme:
        return " ".join(parts)
    palette = theme.get("palette") or {}
    style = theme.get("style_tokens") or []
    negative = theme.get("negative_tokens") or []
    stroke = theme.get("stroke") or {}
    composition = theme.get("composition") or {}

    if style:
        parts.append("Style: " + ", ".join(style) + ".")
    if stroke.get("weight_px"):
        parts.append(f"Stroke weight ~{stroke['weight_px']} px where lines are visible.")
    if palette.get("primary") or palette.get("accent"):
        bits = []
        if palette.get("primary"):
            bits.append(f"primary color {palette['primary']}")
        if palette.get("accent"):
            bits.append(f"accent {palette['accent']}")
        if palette.get("neutral"):
            bits.append(f"neutral {palette['neutral']}")
        parts.append("Palette: " + ", ".join(bits) + ".")
    if composition.get("perspective"):
        parts.append(f"Perspective: {composition['perspective']}.")
    if negative:
        parts.append("Do not include: " + ", ".join(negative) + ".")
    # Substrates must not contain text; reinforce regardless of theme content.
    parts.append("No text, no labels, no arrows, no captions, no watermark.")
    parts.append("Clean white or transparent-appearing background.")
    return " ".join(parts)


def _codex_available() -> bool:
    if shutil.which("codex") is None:
        return False
    home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
    return (home / "auth.json").exists()


def _resolve_backend(requested: str) -> str:
    if requested == "auto":
        if _codex_available():
            return "codex"
        if OpenAI is not None:
            return "api"
        print(
            "No usable backend found. Either run `codex login` or re-run with "
            "--with openai (also requires OPENAI_API_KEY).",
            file=sys.stderr,
        )
        sys.exit(2)
    if requested == "codex":
        if not _codex_available():
            print("Backend 'codex' requested but no Codex CLI / auth found. Run: codex login", file=sys.stderr)
            sys.exit(2)
        return "codex"
    if requested == "api":
        if OpenAI is None:
            print("Backend 'api' requested but `openai` is not installed.", file=sys.stderr)
            sys.exit(2)
        return "api"
    print(f"unknown backend: {requested}", file=sys.stderr)
    sys.exit(2)


def _generate_api(prompt: str, w: int, h: int) -> bytes:
    """Call the OpenAI Images API; return PNG bytes."""
    assert OpenAI is not None
    try:
        from openai import OpenAIError  # type: ignore[import-not-found]
    except ImportError:
        OpenAIError = Exception  # type: ignore[assignment,misc]
    try:
        client = OpenAI()
    except OpenAIError as exc:
        raise RuntimeError(
            f"OpenAI client init failed (likely missing OPENAI_API_KEY): {exc}"
        ) from exc

    size = _snap_to_api_size(w, h)
    if size != f"{w}x{h}":
        print(
            f"warning: requested size {w}x{h} not supported by the API; "
            f"snapping to {size}.",
            file=sys.stderr,
        )
    result = client.images.generate(
        model="gpt-image-2",
        prompt=prompt,
        n=1,
        size=size,
        quality="high",
        output_format="png",
        background="opaque",
        moderation="auto",
    )
    b64 = result.data[0].b64_json if result.data else None
    if not b64:
        url = getattr(result.data[0], "url", None) if result.data else None
        raise RuntimeError(
            f"OpenAI Images API returned no base64 payload (url={url!r}). "
            "Confirm output_format='png' is still accepted and that the model is reachable."
        )
    return base64.b64decode(b64)


def _generate_codex(prompt: str, w: int, h: int, timeout_s: int = 600) -> bytes:
    """Invoke the Codex CLI image_gen tool; return PNG bytes from ./output.png."""
    workdir = Path(tempfile.mkdtemp(prefix="codex_figure_"))
    target = workdir / "output.png"
    codex_prompt = (
        f"Use your platform-native image_gen tool to generate exactly one image. "
        f"Prompt: {prompt} "
        f"Target dimensions {w}x{h}. "
        f"Save the final selected image to ./output.png in the current working directory. "
        f"Do not display the image inline. "
        f"Reply with only the absolute path on success or ERROR on failure."
    )
    try:
        proc = subprocess.run(
            [
                "codex", "exec",
                "--sandbox", "workspace-write",
                "--skip-git-repo-check",
                codex_prompt,
            ],
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"codex exec exit {proc.returncode}. stderr tail: {(proc.stderr or '')[-300:]}"
            )
        if not target.exists():
            raise RuntimeError(
                "codex exec succeeded but did not produce ./output.png; "
                f"stderr tail: {(proc.stderr or '')[-300:]}"
            )
        return target.read_bytes()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate an AI substrate image (opaque, no transparency post-process)."
    )
    parser.add_argument("prompt", help="Subject of the substrate (e.g. 'a stylized brain in watercolor')")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output PNG path")
    parser.add_argument(
        "--size", default="1920x1080",
        help="WxH in pixels. The API snaps to its supported set; Codex respects the request best-effort. Default: 1920x1080.",
    )
    parser.add_argument(
        "--backend", choices=["auto", "codex", "api"], default="auto",
        help="Image-generation backend (default: auto; prefers codex when authenticated).",
    )
    parser.add_argument(
        "--theme", type=Path,
        help="Path to a theme.json (see transparent-icons/references/theme.schema.json).",
    )
    args = parser.parse_args(argv)

    try:
        w, h = _parse_size(args.size)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if w <= 0 or h <= 0:
        print(f"error: size dimensions must be positive, got {w}x{h}", file=sys.stderr)
        return 2

    theme: dict[str, Any] | None = None
    if args.theme:
        try:
            theme = json.loads(args.theme.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: could not load theme '{args.theme}': {exc}", file=sys.stderr)
            return 2

    prompt = _build_prompt(args.prompt, theme)
    backend = _resolve_backend(args.backend)
    print(f"backend: {backend}", file=sys.stderr)
    print(f"prompt: {prompt}", file=sys.stderr)

    try:
        if backend == "codex":
            data = _generate_codex(prompt, w, h)
        else:
            data = _generate_api(prompt, w, h)
    except RuntimeError as exc:
        print(f"error: generation failed: {exc}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    print(f"wrote {args.output} ({len(data)} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
