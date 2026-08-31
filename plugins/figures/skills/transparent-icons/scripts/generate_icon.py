#!/usr/bin/env python3
"""Generate flat scientific icons using gpt-image-2.

Three backends are supported. The first two are auto-selected by default:

  1. codex   - Uses the Codex CLI's platform-native image_gen tool. Requires a
               valid `codex login` (ChatGPT subscription or API key in
               ~/.codex/auth.json). No OPENAI_API_KEY needed.
  2. api     - Calls the OpenAI Images API directly. Requires OPENAI_API_KEY
               via environment, .env, or ~/.env.
  3. atlas   - Calls Atlas Cloud directly with ATLASCLOUD_API_KEY. This backend
               is explicit-only and never changes the default routing.

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
    uv run --with openai --with python-dotenv --with pillow python scripts/generate_icon.py --template neuron --backend atlas -o neuron.png

    # List available templates
    uv run --with python-dotenv python scripts/generate_icon.py --list-templates

Environment:
    OPENAI_API_KEY - Required for the api backend. Read from .env file or environment.
    ATLASCLOUD_API_KEY - Required for the explicit atlas backend.
    CODEX_HOME     - Optional; defaults to ~/.codex. Auth probed at $CODEX_HOME/auth.json.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

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

ATLAS_API_BASE = "https://api.atlascloud.ai/api/v1"
ATLAS_DEFAULT_MODEL = "black-forest-labs/flux-schnell"
ATLAS_TERMINAL_SUCCESS = {"completed", "succeeded", "success"}
ATLAS_TERMINAL_FAILURE = {"failed", "canceled", "cancelled"}


def load_templates() -> dict[str, Any]:
    """Load icon templates from the icon bible JSON."""
    if not TEMPLATES_PATH.exists():
        print(f"Warning: templates file not found at {TEMPLATES_PATH}", file=sys.stderr)
        return {}
    with open(TEMPLATES_PATH) as f:
        data = json.load(f)
    return {t["id"]: t for t in data.get("templates", [])}


def template_to_prompt(
    template: dict[str, Any], color_override: str | None = None
) -> str:
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
        parts.append(
            "On a transparent/white background (will be removed in post-processing)."
        )
    else:
        parts.append("On a clean white background.")

    # Additional hints
    hints = template.get("prompt_hints", [])
    if hints:
        parts.append("Additional: " + ", ".join(hints) + ".")

    return " ".join(parts)


def build_prompt(
    subject: str, colors: str | None = None, transparent: bool = False
) -> str:
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
        if codex_available():
            return "codex"
        if OpenAI is not None:
            return "api"
        print(
            "No usable backend found. Either:\n"
            "  - Run `codex login` to enable the Codex backend, or\n"
            "  - Re-run with `--with openai` to enable the API backend "
            "(also requires OPENAI_API_KEY).",
            file=sys.stderr,
        )
        sys.exit(1)
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
                "Backend 'api' requested but `openai` is not installed. "
                "Re-run with `--with openai`.",
                file=sys.stderr,
            )
            sys.exit(1)
        return "api"
    if requested == "atlas":
        if not os.environ.get("ATLASCLOUD_API_KEY", "").strip():
            print(
                "Backend 'atlas' requires ATLASCLOUD_API_KEY in the environment or .env.",
                file=sys.stderr,
            )
            sys.exit(1)
        return "atlas"
    print(f"Unknown backend: {requested}", file=sys.stderr)
    sys.exit(1)


def build_openai_client() -> Any:
    """Construct the OpenAI client with a friendly error if no API key is set."""
    assert OpenAI is not None  # caller routes via resolve_backend()
    # OpenAIError covers missing key, invalid key, and configuration errors. We narrow to
    # this class rather than `except Exception` so unrelated bugs (TypeError from a future
    # SDK signature change, etc.) surface with their real traceback.
    try:
        from openai import OpenAIError  # type: ignore[import-not-found]
    except ImportError:
        OpenAIError = Exception  # type: ignore[assignment,misc]
    try:
        return OpenAI()  # reads OPENAI_API_KEY from env
    except OpenAIError as exc:
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

    if transparent:
        image_data = _apply_transparency(image_data, method=transparency_method)

    return image_data


def _atlas_base_url() -> str:
    """Normalize an optional OpenAI-style Atlas base URL to the media API."""
    base = os.environ.get("ATLASCLOUD_API_BASE", ATLAS_API_BASE).rstrip("/")
    if base.endswith("/v1") and not base.endswith("/api/v1"):
        return base[:-3] + "/api/v1"
    return base


def _atlas_json(
    url: str,
    api_key: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    timeout_s: int = 60,
) -> dict[str, Any]:
    """Make one Atlas request. Billable POSTs are intentionally never retried."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 research-skills-transparent-icons/0.11.1",
        },
    )
    try:
        with urlopen(request, timeout=timeout_s) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Atlas Cloud HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Atlas Cloud request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Atlas Cloud returned invalid JSON") from exc

    if not isinstance(payload, dict):
        raise TypeError("Atlas Cloud returned a non-object response")
    code = payload.get("code")
    if code not in (None, 0, 200, "200"):
        raise RuntimeError(
            f"Atlas Cloud API error {code}: {payload.get('msg') or payload.get('message')}"
        )
    result = payload.get("data", payload)
    if not isinstance(result, dict):
        raise TypeError("Atlas Cloud response is missing an object payload")
    return result


def _atlas_output_url(prediction: dict[str, Any]) -> str | None:
    outputs = prediction.get("outputs") or prediction.get("output")
    if isinstance(outputs, str):
        return outputs
    if isinstance(outputs, list) and outputs:
        first = outputs[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict) and isinstance(first.get("url"), str):
            return first["url"]
    return None


def _ensure_png(image_data: bytes) -> bytes:
    """Normalize Atlas output to PNG so the CLI's output contract stays stable."""
    if image_data.startswith(b"\x89PNG\r\n\x1a\n"):
        return image_data
    if not HAS_PILLOW:
        raise RuntimeError(
            "The Atlas backend requires Pillow to normalize model output to PNG. "
            "Re-run with `--with pillow`."
        )
    image = Image.open(io.BytesIO(image_data))
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def generate_icon_atlas(
    prompt: str,
    model: str = ATLAS_DEFAULT_MODEL,
    size: int = 1024,
    transparent: bool = False,
    transparency_method: str = "threshold",
    timeout_s: int = 300,
) -> bytes:
    """Generate one icon through Atlas Cloud with one submission and bounded polling."""
    api_key = os.environ.get("ATLASCLOUD_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ATLASCLOUD_API_KEY is required for the atlas backend")
    base_url = _atlas_base_url()
    accepted = _atlas_json(
        f"{base_url}/model/generateImage",
        api_key,
        method="POST",
        body={
            "model": model,
            "prompt": prompt,
            "size": f"{size}*{size}",
            "num_images": 1,
            "seed": -1,
        },
    )
    prediction_id = str(accepted.get("id") or accepted.get("request_id") or "").strip()
    if not prediction_id:
        raise RuntimeError("Atlas Cloud submission did not return a prediction id")

    deadline = time.monotonic() + timeout_s
    consecutive_get_errors = 0
    while True:
        try:
            prediction = _atlas_json(
                f"{base_url}/model/prediction/{quote(prediction_id, safe='')}",
                api_key,
                timeout_s=30,
            )
            consecutive_get_errors = 0
        except RuntimeError:
            consecutive_get_errors += 1
            if consecutive_get_errors >= 3 or time.monotonic() >= deadline:
                raise
            time.sleep(2 ** (consecutive_get_errors - 1))
            continue

        status = str(prediction.get("status", "")).lower()
        if status in ATLAS_TERMINAL_SUCCESS:
            output_url = _atlas_output_url(prediction)
            if not output_url:
                raise RuntimeError(
                    "Atlas Cloud prediction succeeded without an output URL"
                )
            break
        if status in ATLAS_TERMINAL_FAILURE:
            detail = (
                prediction.get("error") or prediction.get("logs") or "unknown error"
            )
            raise RuntimeError(f"Atlas Cloud prediction {status}: {detail}")
        if time.monotonic() >= deadline:
            raise RuntimeError(
                f"Atlas Cloud prediction timed out after {timeout_s}s: {prediction_id}"
            )
        time.sleep(3)

    try:
        request = Request(
            output_url,
            headers={
                "Accept": "image/*",
                "User-Agent": "Mozilla/5.0 research-skills-transparent-icons/0.11.1",
            },
        )
        with urlopen(request, timeout=60) as response:
            image_data = response.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Atlas Cloud image download failed: {exc}") from exc
    if not image_data:
        raise RuntimeError("Atlas Cloud returned an empty image")
    image_data = _ensure_png(image_data)
    if transparent:
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
                    "codex",
                    "exec",
                    "--sandbox",
                    "workspace-write",
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
        if transparent:
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
    client: Any | None,
    prompt: str,
    size: int = 1024,
    transparent: bool = False,
    transparency_method: str = "threshold",
    atlas_model: str = ATLAS_DEFAULT_MODEL,
) -> bytes:
    """Dispatch to the selected backend."""
    if backend == "codex":
        return generate_icon_codex(
            prompt,
            size=size,
            transparent=transparent,
            transparency_method=transparency_method,
        )
    if backend == "api":
        if client is None:
            raise RuntimeError("OpenAI client unavailable for api backend")
        return generate_icon_api(
            client,
            prompt,
            size=size,
            transparent=transparent,
            transparency_method=transparency_method,
        )
    if backend == "atlas":
        return generate_icon_atlas(
            prompt,
            model=atlas_model,
            size=size,
            transparent=transparent,
            transparency_method=transparency_method,
        )
    raise ValueError(f"Unknown backend: {backend}")


def _apply_transparency_threshold(png_bytes: bytes, threshold: int = 240) -> bytes:
    """Remove near-white pixels from PNG, making them transparent. Fast (Pillow only).
    Works well for flat icons on a clean white background; can leave fringes on anti-aliased
    edges and may erase highlights where the foreground itself is near-white."""
    if not HAS_PILLOW:
        raise RuntimeError(
            "Transparency method 'threshold' requires Pillow. Re-run with: "
            "`uv run --with openai --with python-dotenv --with pillow "
            "python scripts/generate_icon.py ...`"
        )
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
    try:
        session = new_session("birefnet-general")
    except Exception as exc:
        # One-time BiRefNet ONNX model download can fail on network, disk, proxy, or
        # cache-permission errors. Surface an actionable hint rather than the raw
        # onnxruntime/urllib traceback.
        raise RuntimeError(
            "BiRefNet model download failed. Check your network connection and that "
            "$U2NET_HOME (or ~/.u2net) is writable; alternatively re-run with "
            f"`--transparency-method threshold` to skip the model. Underlying: {exc}"
        ) from exc
    # alpha_matting_erode_size defaults to 10 px (rembg default); reasonable for 1024 px
    # icons. Increase if foreground edges show halos after matting.
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate flat scientific icons using OpenAI gpt-image-2"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Icon description or template with {item} placeholder",
    )
    parser.add_argument(
        "-o", "--output", help="Output file path or directory (for batch)"
    )
    parser.add_argument(
        "--template", help="Template ID from icon bible (e.g., brain-eeg)"
    )
    parser.add_argument("--category", help="Generate all templates in a category")
    parser.add_argument(
        "--transparent", action="store_true", help="Remove background (requires Pillow)"
    )
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
    parser.add_argument(
        "--colors", help="Color palette override (e.g., 'teal,coral' or hex codes)"
    )
    parser.add_argument(
        "--size", type=int, default=1024, help="Icon size in pixels (default: 1024)"
    )
    parser.add_argument(
        "--batch",
        help="Comma-separated items for batch generation (use {item} in prompt)",
    )
    parser.add_argument(
        "--list-templates", action="store_true", help="List available icon templates"
    )
    parser.add_argument(
        "--templates-file", type=Path, help="Custom templates JSON file"
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "codex", "api", "atlas"],
        default="auto",
        help="Image generation backend (default: auto; prefers codex when authenticated)",
    )
    parser.add_argument(
        "--atlas-model",
        default=ATLAS_DEFAULT_MODEL,
        help="Atlas Cloud image model used only with --backend atlas",
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
        return 0

    # Validate arguments
    if not args.prompt and not args.template and not args.category:
        parser.error("Provide a prompt, --template, or --category")
    if not args.output and not args.list_templates:
        parser.error("--output is required")

    # Transparency dependency checks are performed at the use site (raise from
    # _apply_transparency_*) so the user sees the actionable error AFTER they have
    # confirmed which method they want, not as a coarse early-exit warning.

    backend = resolve_backend(args.backend)
    client: Any = build_openai_client() if backend == "api" else None
    print(f"Backend: {backend}")

    # Category batch mode
    if args.category:
        cat_templates = [
            t for t in templates.values() if t.get("category") == args.category
        ]
        if not cat_templates:
            print(f"No templates found for category: {args.category}", file=sys.stderr)
            print(
                "Available categories: "
                + ", ".join(
                    sorted({t.get("category", "") for t in templates.values()})
                ),
                file=sys.stderr,
            )
            return 1

        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        for t in cat_templates:
            prompt = template_to_prompt(t, color_override=args.colors)
            transparent = (
                args.transparent
                or t.get("composition", {}).get("background") == "transparent"
            )
            print(f"Generating: {t['id']}...")
            data = generate_icon(
                backend,
                client,
                prompt,
                size=args.size,
                transparent=transparent,
                transparency_method=args.transparency_method,
                atlas_model=args.atlas_model,
            )
            save_icon(data, output_dir / f"{t['id']}.png")
        return 0

    # Template mode
    if args.template:
        if args.template not in templates:
            print(f"Template not found: {args.template}", file=sys.stderr)
            print("Available: " + ", ".join(sorted(templates.keys())), file=sys.stderr)
            return 1
        t = templates[args.template]
        prompt = template_to_prompt(t, color_override=args.colors)
        transparent = (
            args.transparent
            or t.get("composition", {}).get("background") == "transparent"
        )
        print(f"Generating from template: {args.template}")
        print(f"Prompt: {prompt[:200]}...")
        data = generate_icon(
            backend,
            client,
            prompt,
            size=args.size,
            transparent=transparent,
            transparency_method=args.transparency_method,
            atlas_model=args.atlas_model,
        )
        save_icon(data, Path(args.output))
        return 0

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
                backend,
                client,
                prompt,
                size=args.size,
                transparent=args.transparent,
                transparency_method=args.transparency_method,
                atlas_model=args.atlas_model,
            )
            save_icon(data, output_dir / f"{item.replace(' ', '_')}.png")
        return 0

    # Single free-form prompt mode
    prompt = build_prompt(args.prompt, colors=args.colors, transparent=args.transparent)
    print("Generating icon...")
    print(f"Prompt: {prompt}")
    data = generate_icon(
        backend,
        client,
        prompt,
        size=args.size,
        transparent=args.transparent,
        transparency_method=args.transparency_method,
        atlas_model=args.atlas_model,
    )
    save_icon(data, Path(args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
