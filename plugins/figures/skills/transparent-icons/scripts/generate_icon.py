#!/usr/bin/env python3
"""Generate flat scientific icons using gpt-image-2.

Two backends are supported and auto-selected by default:

  1. codex   - Uses the Codex CLI's platform-native image_gen tool. Requires a
               valid `codex login` (ChatGPT subscription or API key in
               ~/.codex/auth.json). No OPENAI_API_KEY needed.
  2. api     - Calls the OpenAI Images API directly. Requires OPENAI_API_KEY
               via environment, .env, or ~/.env.

Auto selection prefers codex when both `codex` is on PATH and
~/.codex/auth.json exists; otherwise it falls back to the API.

Recommended runner (declares all deps via --with):
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py ...

Usage:
    # Free-form prompt
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py "a human brain with EEG electrodes" -o brain_eeg.png

    # From template (icon bible)
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --template brain-eeg -o brain_eeg.png

    # Override template colors
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --template neuron --colors "#3498DB,#E74C3C" -o neuron.png

    # With transparency
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --template dna-helix -o dna.png --transparent

    # Batch from template category
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --category neuroscience -o icons/neuro/

    # Batch from free-form prompt
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py "a flat icon of a {item}" -o icons/ --batch "brain,heart,lung"

    # Force a backend
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --template neuron --backend codex -o neuron.png
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --template neuron --backend api   -o neuron.png

    # List available templates
    uv run --with python-dotenv python scripts/generate_icon.py --list-templates

Environment:
    OPENAI_API_KEY - Required for the api backend. Read from .env file or environment.
    CODEX_HOME     - Optional; defaults to ~/.codex. Auth probed at $CODEX_HOME/auth.json.
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
from typing import Any, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    print(
        "Missing dependency: python-dotenv. Run via: "
        "uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # api backend unavailable; codex backend may still work

try:
    from PIL import Image
    import io

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# Load .env from current directory, then home directory
load_dotenv()
load_dotenv(Path.home() / ".env")

# Path to icon templates relative to this script
TEMPLATES_PATH = Path(__file__).parent / "icon-templates.json"

BASE_STYLE = (
    "flat minimalist scientific icon, Nature/Science journal figure style, "
    "simple geometric shapes, no gradients, no shadows, no 3D effects, "
    "no text, no labels, clean edges, centered"
)


def load_templates() -> dict[str, Any]:
    """Load icon templates from the icon bible JSON."""
    if not TEMPLATES_PATH.exists():
        print(f"Warning: templates file not found at {TEMPLATES_PATH}")
        return {}
    with open(TEMPLATES_PATH) as f:
        data = json.load(f)
    return {t["id"]: t for t in data.get("templates", [])}


def template_to_prompt(template: dict[str, Any], color_override: str | None = None) -> str:
    """Convert a template JSON to a detailed generation prompt."""
    parts = [f"A {BASE_STYLE}."]
    parts.append(f"Subject: {template['description']}.")

    # Describe each element
    parts.append("Elements:")
    for elem in template.get("elements", []):
        desc = elem["description"]
        fill = elem.get("fill", "")
        if fill and fill != "none":
            desc += f" (color: {fill})"
        parts.append(f"- {desc}")

    # Apply palette
    palette = template.get("palette", {})
    if color_override:
        parts.append(f"Color palette: {color_override}.")
    elif palette:
        colors = ", ".join(f"{k}: {v}" for k, v in palette.items())
        parts.append(f"Color palette: {colors}.")

    # Composition hints
    comp = template.get("composition", {})
    style = comp.get("style", "flat-minimalist")
    parts.append(f"Style: {style}.")

    bg = comp.get("background", "white")
    if bg == "transparent":
        parts.append("On a transparent/white background (will be removed in post-processing).")
    else:
        parts.append("On a clean white background.")

    # Additional hints
    hints = template.get("prompt_hints", [])
    if hints:
        parts.append("Additional: " + ", ".join(hints) + ".")

    return " ".join(parts)


def build_prompt(subject: str, colors: str | None = None, transparent: bool = False) -> str:
    """Build the full prompt from a free-form subject description."""
    parts = [f"A {BASE_STYLE} of {subject}"]

    if colors:
        parts.append(f"using {colors} color palette")

    if transparent:
        parts.append("on a transparent background")
    else:
        parts.append("on a clean white background")

    return ", ".join(parts) + "."


def codex_available() -> bool:
    """Detect a usable Codex CLI install with valid auth.

    Auth is gated on the Codex CLI auth file (`$CODEX_HOME/auth.json`, default
    `~/.codex/auth.json`). Env-var-only paths are intentionally NOT treated as
    Codex auth: a user with `OPENAI_API_KEY` set but no `codex login` would
    otherwise be silently routed through `codex exec` and hit a runtime auth
    error instead of the OpenAI Images API.
    """
    if shutil.which("codex") is None:
        return False
    codex_home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
    return (codex_home / "auth.json").exists()


def resolve_backend(requested: str) -> str:
    """Resolve `auto` to a concrete backend; validate explicit choices."""
    if requested == "auto":
        return "codex" if codex_available() else "api"
    if requested == "codex":
        if not codex_available():
            print(
                "Backend 'codex' requested but no Codex CLI/auth found. "
                "Run: codex login",
                file=sys.stderr,
            )
            sys.exit(1)
        return "codex"
    if requested == "api":
        if OpenAI is None:
            print(
                "Backend 'api' requested but `openai` is not installed.",
                file=sys.stderr,
            )
            sys.exit(1)
        return "api"
    print(f"Unknown backend: {requested}", file=sys.stderr)
    sys.exit(1)


def build_openai_client() -> Any:
    """Construct the OpenAI client with a friendly error if no API key is set."""
    assert OpenAI is not None  # caller routes via resolve_backend()
    try:
        return OpenAI()  # reads OPENAI_API_KEY from env
    except Exception as exc:  # OpenAI raises OpenAIError when key is missing
        print(
            "Backend 'api' requires OPENAI_API_KEY. "
            "Set it in your environment, .env, or ~/.env, "
            f"or use --backend codex if you have run `codex login`. ({exc})",
            file=sys.stderr,
        )
        sys.exit(1)


def generate_icon_api(
    client: Any,
    prompt: str,
    size: int = 1024,
    transparent: bool = False,
    transparency_method: str = "threshold",
) -> bytes:
    """Generate a single icon via the OpenAI Images API."""
    size_str = f"{size}x{size}"

    # gpt-image-2 supports flexible sizes (multiples of 16, max edge 3840, aspect <=3:1)
    if size_str not in ("1024x1024", "1024x1536", "1536x1024", "2048x2048"):
        size_str = "1024x1024"

    # gpt-image-2 (April 2026) rejects `background="transparent"`, so we always generate
    # opaque and apply transparency in post when requested.
    result = client.images.generate(
        model="gpt-image-2",
        prompt=prompt,
        n=1,
        size=size_str,
        quality="high",
        output_format="png",
        background="opaque",
        moderation="auto",
    )

    image_data = base64.b64decode(result.data[0].b64_json)

    if transparent and HAS_PILLOW:
        image_data = _apply_transparency(image_data, method=transparency_method)

    return image_data


def generate_icon_codex(
    prompt: str,
    size: int = 1024,
    transparent: bool = False,
    transparency_method: str = "threshold",
    timeout_s: int = 300,
) -> bytes:
    """Generate a single icon by invoking the Codex CLI's image_gen tool.

    The CLI runs in a temp workspace with `--sandbox workspace-write`; the
    selected image is saved to ./output.png inside that workspace, which we
    then read back as bytes.
    """
    workdir = Path(tempfile.mkdtemp(prefix="codex_icon_"))
    target = workdir / "output.png"
    try:
        # The user-supplied `prompt` is concatenated into a natural-language
        # instruction below. We trust the prompt because it originates from
        # the same shell session that runs this script; if you ever surface
        # this script over an untrusted boundary, sanitize `prompt` first.
        codex_prompt = (
            f"Use your platform-native image_gen tool to generate exactly one image. "
            f"Prompt: {prompt} "
            f"Square aspect, target {size}x{size}. "
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
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stderr_tail = _safe_tail(exc.stderr, 300)
            raise RuntimeError(
                f"Codex exec timed out after {timeout_s}s. "
                f"Try --backend api or raise the timeout. "
                f"stderr tail: {stderr_tail}"
            ) from exc

        # Surface non-zero exits explicitly. Codex emits an unrelated
        # "failed to record rollout items" stderr line on success too, so we
        # rely on returncode rather than stderr scanning.
        if proc.returncode != 0:
            raise RuntimeError(
                f"Codex exec exited rc={proc.returncode}. "
                f"stderr tail: {_safe_tail(proc.stderr, 300)}"
            )
        if not target.exists():
            raise RuntimeError(
                "Codex exec succeeded but did not produce ./output.png. "
                f"stderr tail: {_safe_tail(proc.stderr, 300)}"
            )
        image_data = target.read_bytes()
        if transparent and HAS_PILLOW:
            image_data = _apply_transparency(image_data, method=transparency_method)
        return image_data
    finally:
        # Best-effort cleanup; tempfile.mkdtemp guarantees an isolated path,
        # so a stale dir at most leaks a few MB into $TMPDIR.
        shutil.rmtree(workdir, ignore_errors=True)


def _safe_tail(s: Any, n: int) -> str:
    """Tail-truncate stderr for error messages without echoing the
    user-supplied prompt. Codex echoes the prompt into stdout but not stderr,
    so we never use stdout for diagnostics. Accepts str/bytes/None because
    subprocess.TimeoutExpired carries bytes even under text=True."""
    if not s:
        return "(empty)"
    if isinstance(s, bytes):
        s = s.decode("utf-8", errors="replace")
    return s[-n:]


def generate_icon(
    backend: str,
    client: Optional[Any],
    prompt: str,
    size: int = 1024,
    transparent: bool = False,
    transparency_method: str = "threshold",
) -> bytes:
    """Dispatch to the selected backend."""
    if backend == "codex":
        return generate_icon_codex(
            prompt, size=size, transparent=transparent, transparency_method=transparency_method
        )
    if backend == "api":
        if client is None:
            raise RuntimeError("OpenAI client unavailable for api backend")
        return generate_icon_api(
            client, prompt, size=size, transparent=transparent, transparency_method=transparency_method
        )
    raise ValueError(f"Unknown backend: {backend}")


def _apply_transparency_threshold(png_bytes: bytes, threshold: int = 240) -> bytes:
    """Remove near-white pixels from PNG, making them transparent. Fast and dependency-free
    (just Pillow). Works well for flat icons on a clean white background; can leave fringes
    on anti-aliased edges and may erase highlights where the foreground itself is near-white."""
    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    data = img.getdata()

    new_data = []
    for r, g, b, a in data:
        if r > threshold and g > threshold and b > threshold:
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)
    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()


def _apply_transparency_birefnet(png_bytes: bytes) -> bytes:
    """Remove background via rembg + BiRefNet (cleaner edges than threshold). Requires a
    one-time ONNX model download (~400 MB on first run) and `rembg` + `onnxruntime` deps."""
    try:
        from rembg import new_session, remove  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "Transparency method 'birefnet' requires rembg. Re-run with: "
            "`uv run --with openai --with python-dotenv --with pillow "
            "--with rembg --with onnxruntime python scripts/generate_icon.py ...`"
        ) from exc
    session = new_session("birefnet-general")
    return remove(
        png_bytes,
        session=session,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
    )


def _apply_transparency(png_bytes: bytes, method: str = "threshold") -> bytes:
    """Dispatch to the requested transparency method."""
    if method == "threshold":
        return _apply_transparency_threshold(png_bytes)
    if method == "birefnet":
        return _apply_transparency_birefnet(png_bytes)
    raise ValueError(
        f"unknown transparency method '{method}'; expected 'threshold' or 'birefnet'"
    )


def save_icon(data: bytes, path: Path) -> None:
    """Save icon bytes to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"Saved: {path} ({len(data)} bytes)")


def list_templates(templates: dict[str, Any]) -> None:
    """Print available templates grouped by category."""
    categories: dict[str, list[dict[str, Any]]] = {}
    for t in templates.values():
        cat = t.get("category", "uncategorized")
        categories.setdefault(cat, []).append(t)

    for cat in sorted(categories):
        print(f"\n  {cat}:")
        for t in sorted(categories[cat], key=lambda x: x["id"]):
            print(f"    {t['id']:25s} {t['name']}")
            print(f"    {'':25s} {t['description'][:70]}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate flat scientific icons using OpenAI gpt-image-2"
    )
    parser.add_argument(
        "prompt", nargs="?", default=None,
        help="Icon description or template with {item} placeholder"
    )
    parser.add_argument("-o", "--output", help="Output file path or directory (for batch)")
    parser.add_argument("--template", help="Template ID from icon bible (e.g., brain-eeg)")
    parser.add_argument("--category", help="Generate all templates in a category")
    parser.add_argument("--transparent", action="store_true", help="Remove background (requires Pillow)")
    parser.add_argument(
        "--transparency-method",
        choices=["threshold", "birefnet"],
        default="threshold",
        help=(
            "Background-removal method when --transparent is set. 'threshold' (default) uses "
            "Pillow to drop near-white pixels (fast, dep-free). 'birefnet' uses rembg + BiRefNet "
            "for cleaner edges (one-time ~400 MB model download; pass --with rembg --with onnxruntime)."
        ),
    )
    parser.add_argument("--colors", help="Color palette override (e.g., 'teal,coral' or hex codes)")
    parser.add_argument("--size", type=int, default=1024, help="Icon size in pixels (default: 1024)")
    parser.add_argument("--batch", help="Comma-separated items for batch generation (use {item} in prompt)")
    parser.add_argument("--list-templates", action="store_true", help="List available icon templates")
    parser.add_argument("--templates-file", type=Path, help="Custom templates JSON file")
    parser.add_argument(
        "--backend",
        choices=["auto", "codex", "api"],
        default="auto",
        help="Image generation backend (default: auto; prefers codex when authenticated)",
    )
    args = parser.parse_args()

    # Load templates
    templates_path = args.templates_file or TEMPLATES_PATH
    if templates_path.exists():
        with open(templates_path) as f:
            data = json.load(f)
        templates = {t["id"]: t for t in data.get("templates", [])}
    else:
        templates = {}

    # List templates mode
    if args.list_templates:
        if not templates:
            print("No templates found.")
        else:
            print("Available icon templates:")
            list_templates(templates)
        return

    # Validate arguments
    if not args.prompt and not args.template and not args.category:
        parser.error("Provide a prompt, --template, or --category")
    if not args.output and not args.list_templates:
        parser.error("--output is required")

    if args.transparent and not HAS_PILLOW:
        print("Warning: --transparent requires Pillow. Ensure pillow is included in the uv run --with dependencies.")
        print("Generating without transparency.")
        args.transparent = False

    backend = resolve_backend(args.backend)
    client: Any = build_openai_client() if backend == "api" else None
    print(f"Backend: {backend}")

    # Category batch mode
    if args.category:
        cat_templates = [t for t in templates.values() if t.get("category") == args.category]
        if not cat_templates:
            print(f"No templates found for category: {args.category}")
            print("Available categories:", ", ".join(sorted(set(t.get("category", "") for t in templates.values()))))
            return

        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        for t in cat_templates:
            prompt = template_to_prompt(t, color_override=args.colors)
            transparent = args.transparent or t.get("composition", {}).get("background") == "transparent"
            print(f"Generating: {t['id']}...")
            data = generate_icon(
                backend, client, prompt,
                size=args.size,
                transparent=transparent,
                transparency_method=args.transparency_method,
            )
            save_icon(data, output_dir / f"{t['id']}.png")
        return

    # Template mode
    if args.template:
        if args.template not in templates:
            print(f"Template not found: {args.template}")
            print("Available:", ", ".join(sorted(templates.keys())))
            return
        t = templates[args.template]
        prompt = template_to_prompt(t, color_override=args.colors)
        transparent = args.transparent or t.get("composition", {}).get("background") == "transparent"
        print(f"Generating from template: {args.template}")
        print(f"Prompt: {prompt[:200]}...")
        data = generate_icon(
            backend, client, prompt,
            size=args.size,
            transparent=transparent,
            transparency_method=args.transparency_method,
        )
        save_icon(data, Path(args.output))
        return

    # Free-form batch mode
    if args.batch:
        items = [item.strip() for item in args.batch.split(",")]
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        for item in items:
            prompt = build_prompt(
                args.prompt.replace("{item}", item),
                colors=args.colors,
                transparent=args.transparent,
            )
            print(f"Generating: {item}...")
            data = generate_icon(
                backend, client, prompt,
                size=args.size,
                transparent=args.transparent,
                transparency_method=args.transparency_method,
            )
            save_icon(data, output_dir / f"{item.replace(' ', '_')}.png")
        return

    # Single free-form prompt mode
    prompt = build_prompt(args.prompt, colors=args.colors, transparent=args.transparent)
    print(f"Generating icon...")
    print(f"Prompt: {prompt}")
    data = generate_icon(
        backend, client, prompt,
        size=args.size,
        transparent=args.transparent,
        transparency_method=args.transparency_method,
    )
    save_icon(data, Path(args.output))


if __name__ == "__main__":
    main()
