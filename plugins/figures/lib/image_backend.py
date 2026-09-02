"""Shared AI image-generation backend for the figures plugin.

Three backends behind one API:

  1. codex  -- Codex CLI's built-in `image_gen` tool (preferred; no
              OPENAI_API_KEY needed, just `codex login`).
  2. api    -- OpenAI Images API (`gpt-image-2` via the `openai` package).
  3. fake   -- offline Pillow-rendered stand-in for tests and CI. Forced via
              `FIGURES_IMAGE_BACKEND=fake` or `--backend fake`.

`preflight()` probes the environment (codex binary, the code-mode host
sibling binary, auth, API key) with short timeouts so a broken install fails
fast with an actionable message instead of hanging for the full generation
timeout. `resolve_backend()` turns a requested backend plus a Preflight into
a concrete backend name. `generate()` and `edit()` dispatch to the resolved
backend and return a uniform `GenerationResult`.
"""

from __future__ import annotations

import base64
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_MODEL = "gpt-5.6-luna"
DEFAULT_EFFORT = "xhigh"

# Emitted by codex when the code-mode host (needed to reach the built-in
# image_gen tool) fails to come up in time, most often because the host
# binary or codex itself is still quarantined after a cask upgrade.
CODE_MODE_HANG_MARKER = "timed out negotiating with the code-mode host"

MIN_TOTAL_PIXELS = 655_360
MAX_TOTAL_PIXELS = 8_294_400
MAX_EDGE = 3840
MAX_RATIO = 3.0

_SIZE_RE = re.compile(r"^(\d+)x(\d+)$")


class BackendUnavailable(Exception):
    """Raised by resolve_backend() when the requested backend cannot be used."""


class GenerationFailed(Exception):
    """Raised when generation exhausts its retries without producing output."""


@dataclass
class Preflight:
    """Result of probing the environment for usable image-generation backends."""

    backend_requested: str
    codex_path: str | None = None
    codex_realpath: str | None = None
    codex_version: str | None = None
    codex_ok: bool = False
    codex_hang: bool = False
    host_path: str | None = None
    host_quarantined: bool = False
    auth_present: bool = False
    api_key_present: bool = False
    messages: list[str] = field(default_factory=list)

    @property
    def codex_usable(self) -> bool:
        return (
            self.codex_ok
            and self.auth_present
            and not self.codex_hang
            and not self.host_quarantined
        )


@dataclass
class GenerationRequest:
    prompt: str
    out: Path
    size: str = "auto"
    quality: str = "high"
    n: int = 1
    references: list[Path] = field(default_factory=list)
    model: str = DEFAULT_MODEL
    effort: str = DEFAULT_EFFORT
    timeout_s: int = 600
    background: str = (
        "opaque"  # "opaque" | "transparent" ("chroma" accepted as a legacy alias)
    )
    background_color: str = "#FFFFFF"  # flatten target when background == "opaque"
    verbose: bool = False
    log_path: Path | None = None
    backend: str = "auto"  # "auto" | "codex" | "api" | "fake"
    codex_bin: str | None = (
        None  # explicit codex executable path; else $CODEX_BIN, else PATH
    )

    def __post_init__(self) -> None:
        if self.background == "chroma":
            self.background = "transparent"


@dataclass
class GenerationResult:
    paths: list[Path]
    backend: str
    elapsed_s: float
    log_path: Path | None
    workdir: Path | None
    final_message: str | None


def _codex_version_probe(codex_path: str) -> tuple[bool, bool, str | None]:
    """Return (ok, hung, version_string) for `codex --version` under a 10s timeout."""
    try:
        proc = subprocess.run(
            [codex_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, True, None
    except OSError:
        return False, False, None
    if proc.returncode != 0:
        return False, False, None
    return True, False, (proc.stdout.strip() or proc.stderr.strip() or None)


def preflight(backend: str = "auto", codex_bin: str | None = None) -> Preflight:
    """Probe the environment for codex and API-key availability.

    Always checks both paths regardless of `backend_requested` so
    `resolve_backend()` can report every relevant fix hint at once.

    `codex_bin` (falling back to the `CODEX_BIN` env var, then `PATH`) names
    an explicit codex executable. This matters on machines where the
    Homebrew cask binary hangs forever under a non-interactive launch even
    after clearing `com.apple.quarantine`, because macOS also stamps a
    system-managed `com.apple.provenance` attribute on it: the workaround is
    a byte-identical copy of `codex` and its sibling `codex-code-mode-host`
    into a directory the user owns, `xattr -c` on both, and CODEX_BIN
    pointed at the copy.
    """
    pf = Preflight(backend_requested=backend)

    codex_path = codex_bin or os.environ.get("CODEX_BIN") or shutil.which("codex")
    pf.codex_path = codex_path
    if codex_path is None:
        pf.messages.append(
            "codex not found on PATH; install it (e.g. `brew install --cask codex`) "
            "and run `codex login`, or set CODEX_BIN to an explicit binary path"
        )
    elif not Path(codex_path).exists():
        pf.messages.append(
            f"codex binary does not exist at {codex_path} (from CODEX_BIN or --codex-bin)"
        )
    else:
        realpath = os.path.realpath(codex_path)
        pf.codex_realpath = realpath
        ok, hung, version = _codex_version_probe(codex_path)
        pf.codex_ok = ok
        pf.codex_hang = hung
        pf.codex_version = version
        if hung:
            pf.messages.append(
                "codex hangs, likely quarantined, fix: launch codex once from "
                "Terminal.app so Gatekeeper approves it; if it still hangs "
                "headless, copy bin/codex and bin/codex-code-mode-host from the "
                "cask directory to a folder you own, run `xattr -c` on both, "
                "and set CODEX_BIN=<that folder>/codex"
            )
        elif not ok:
            pf.messages.append(
                f"`codex --version` failed at {codex_path}; check the install"
            )

        host_path = Path(realpath).parent / "codex-code-mode-host"
        if host_path.exists():
            pf.host_path = str(host_path)
            if sys.platform == "darwin":
                try:
                    xattr_proc = subprocess.run(
                        ["xattr", "-p", "com.apple.quarantine", str(host_path)],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False,
                    )
                except (subprocess.TimeoutExpired, OSError):
                    xattr_proc = None
                if xattr_proc is not None and xattr_proc.returncode == 0:
                    pf.host_quarantined = True
                    pf.messages.append(
                        "codex-code-mode-host is quarantined, fix: "
                        f"xattr -d com.apple.quarantine {host_path}"
                    )

        codex_home = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
        auth_path = codex_home / "auth.json"
        pf.auth_present = auth_path.exists()
        if not pf.auth_present:
            pf.messages.append(f"{auth_path} not found; run `codex login`")

    pf.api_key_present = bool(os.environ.get("OPENAI_API_KEY"))
    if not pf.api_key_present:
        pf.messages.append("OPENAI_API_KEY is not set; the api backend is unavailable")

    return pf


def resolve_backend(requested: str, pf: Preflight) -> str:
    """Resolve `requested` ("auto"|"codex"|"api"|"fake") to a concrete backend."""
    if os.environ.get("FIGURES_IMAGE_BACKEND") == "fake" or requested == "fake":
        return "fake"

    if requested == "codex":
        if not pf.codex_usable:
            raise BackendUnavailable(
                "\n".join(pf.messages) or "codex backend unavailable"
            )
        return "codex"

    if requested == "api":
        if not pf.api_key_present:
            raise BackendUnavailable(
                "\n".join(pf.messages) or "api backend unavailable"
            )
        return "api"

    if requested == "auto":
        if pf.codex_usable:
            return "codex"
        if pf.api_key_present:
            return "api"
        raise BackendUnavailable(
            "\n".join(pf.messages) or "no usable image backend found"
        )

    raise BackendUnavailable(f"unknown backend requested: {requested!r}")


def validate_size(size: str) -> str:
    """Validate a gpt-image-2 size string ("auto" or "WIDTHxHEIGHT")."""
    if size == "auto":
        return size
    m = _SIZE_RE.match(size.strip().lower())
    if not m:
        raise ValueError(f"size must be 'auto' or 'WIDTHxHEIGHT', got {size!r}")
    w, h = int(m.group(1)), int(m.group(2))
    if w <= 0 or h <= 0:
        raise ValueError(f"size dimensions must be positive, got {w}x{h}")
    if w % 16 != 0 or h % 16 != 0:
        raise ValueError(f"size edges must be multiples of 16, got {w}x{h}")
    if max(w, h) > MAX_EDGE:
        raise ValueError(f"max edge is {MAX_EDGE}, got {max(w, h)}")
    if max(w, h) / min(w, h) > MAX_RATIO:
        raise ValueError(f"long/short edge ratio must be <= {MAX_RATIO}, got {w}x{h}")
    total = w * h
    if not (MIN_TOTAL_PIXELS <= total <= MAX_TOTAL_PIXELS):
        raise ValueError(
            f"total pixels must be between {MIN_TOTAL_PIXELS:,} and "
            f"{MAX_TOTAL_PIXELS:,}, got {total:,} for {w}x{h}"
        )
    return f"{w}x{h}"


def snap_size(w: float, h: float) -> str:
    """Round each edge to a multiple of 16 and clamp within the gpt-image-2 rules."""
    if w <= 0 or h <= 0:
        raise ValueError(f"width and height must be positive, got {w}x{h}")

    def round16(v: float) -> int:
        return max(16, min(MAX_EDGE, round(v / 16.0) * 16))

    aspect = w / h
    if aspect > MAX_RATIO:
        h = w / MAX_RATIO
    elif aspect < 1 / MAX_RATIO:
        w = h / MAX_RATIO

    # Two passes: scale to the pixel-count band, round to 16px, and repeat
    # once more since rounding can nudge the total back out of band.
    for _ in range(2):
        total = w * h
        if total < MIN_TOTAL_PIXELS:
            scale = (MIN_TOTAL_PIXELS / total) ** 0.5
            w, h = w * scale, h * scale
        elif total > MAX_TOTAL_PIXELS:
            scale = (MAX_TOTAL_PIXELS / total) ** 0.5
            w, h = w * scale, h * scale
        w, h = float(round16(w)), float(round16(h))

    sw, sh = round16(w), round16(h)
    if max(sw, sh) / min(sw, sh) > MAX_RATIO:
        if sw >= sh:
            sh = round16(sw / MAX_RATIO)
        else:
            sw = round16(sh / MAX_RATIO)

    # 16px rounding can leave the total just outside the pixel band even
    # after the scaling passes above (e.g. 640x480 rounds to 928x704, whose
    # area is a hair under the minimum); nudge both edges by one 16px step
    # at a time until back in band. Bounded so a pathological input can
    # never loop forever; validate_size() below is the final authority.
    for _ in range(2 * (MAX_EDGE // 16)):
        total = sw * sh
        if total < MIN_TOTAL_PIXELS and max(sw, sh) < MAX_EDGE:
            sw, sh = min(MAX_EDGE, sw + 16), min(MAX_EDGE, sh + 16)
        elif total > MAX_TOTAL_PIXELS and min(sw, sh) > 16:
            sw, sh = max(16, sw - 16), max(16, sh - 16)
        else:
            break

    return validate_size(f"{sw}x{sh}")


def _candidate_paths(out: Path, n: int) -> list[Path]:
    if n <= 1:
        return [out]
    stem = out.stem
    suffix = out.suffix or ".png"
    parent = out.parent
    return [parent / f"{stem}_{i}{suffix}" for i in range(1, n + 1)]


_TEXT_BLOCK_RE = re.compile(
    r"Text \(verbatim[^)]*\):\s*(?P<body>.*?)(?:\n\s*\n|\nAvoid:|\Z)", re.DOTALL
)
_QUOTED_RE = re.compile(r'"([^"]*)"')


def _extract_verbatim_strings(prompt: str) -> list[str]:
    """Pull every quoted string out of the prompt's `Text (verbatim...)` block."""
    m = _TEXT_BLOCK_RE.search(prompt)
    if not m:
        return []
    return [s for s in _QUOTED_RE.findall(m.group("body")) if s.strip()]


def _fake_image_size(size: str) -> tuple[int, int]:
    if size == "auto":
        return 1024, 1024
    w, h = size.lower().split("x")
    return int(w), int(h)


def _generate_fake(req: GenerationRequest) -> tuple[list[Path], str | None]:
    from PIL import Image, ImageDraw, ImageFont

    w, h = _fake_image_size(req.size)
    n = max(1, req.n)
    out_paths = _candidate_paths(req.out, n)
    texts = _extract_verbatim_strings(req.prompt)
    is_transparent = req.background == "transparent"
    mode = "RGBA" if is_transparent else "RGB"
    bg = (0, 0, 0, 0) if is_transparent else (245, 245, 245)
    fill = (0, 0, 0, 255) if is_transparent else (0, 0, 0)

    font_size = max(24, h // 12)
    try:
        font = ImageFont.load_default(size=font_size)
    except TypeError:
        font = ImageFont.load_default()

    for out_path in out_paths:
        img = Image.new(mode, (w, h), bg)
        draw = ImageDraw.Draw(img)
        y = h // 10
        for text in texts:
            draw.text((w // 10, y), text, fill=fill, font=font)
            y += font_size + 10
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)

    return out_paths, f"wrote {len(out_paths)} fake image(s)"


def _edit_fake(image: Path, instruction: str, out: Path) -> tuple[list[Path], str]:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(image).convert("RGBA")
    draw = ImageDraw.Draw(img)
    font_size = max(16, img.height // 20)
    try:
        font = ImageFont.load_default(size=font_size)
    except TypeError:
        font = ImageFont.load_default()
    draw.text((10, 10), f"EDIT: {instruction}"[:200], fill=(200, 0, 0, 255), font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return [out], f"edited (fake): {instruction}"


def _stream_process(
    proc: subprocess.Popen, log_fh, timeout_s: float, verbose: bool
) -> None:
    """Stream proc's combined stdout/stderr into log_fh, heartbeat every 20s
    when verbose, and raise TimeoutError once timeout_s elapses."""
    q: queue.Queue[str | None] = queue.Queue()

    def reader() -> None:
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                q.put(line)
        finally:
            q.put(None)

    reader_thread = threading.Thread(target=reader, daemon=True)
    reader_thread.start()

    start = time.monotonic()
    last_heartbeat = start
    while True:
        elapsed = time.monotonic() - start
        if elapsed > timeout_s:
            proc.kill()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            raise TimeoutError(f"codex exec exceeded {timeout_s}s timeout")
        try:
            line = q.get(timeout=1.0)
        except queue.Empty:
            line = "__poll__"
        if line is None:
            break
        if line != "__poll__":
            log_fh.write(line)
            log_fh.flush()
        now = time.monotonic()
        if verbose and now - last_heartbeat >= 20:
            print(f"[image_backend] {int(now - start)} s elapsed ...", file=sys.stderr)
            last_heartbeat = now
    proc.wait(timeout=max(1, int(timeout_s)))


def _discover_output(workdir: Path) -> Path | None:
    last_txt = workdir / "last.txt"
    if last_txt.is_file():
        content = last_txt.read_text(encoding="utf-8", errors="replace").strip()
        if content and content != "ERROR":
            candidate = Path(content)
            if candidate.is_file():
                return candidate
    pngs = sorted(workdir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pngs[0] if pngs else None


def _codex_command(
    executable: str,
    prompt: str,
    workdir: Path,
    model: str,
    effort: str,
    references: list[Path],
) -> list[str]:
    cmd = [
        executable,
        "exec",
        "-m",
        model,
        "-c",
        f'model_reasoning_effort="{effort}"',
        "--sandbox",
        "workspace-write",
        "--skip-git-repo-check",
        "--ephemeral",
        "-C",
        str(workdir),
        "-o",
        str(workdir / "last.txt"),
    ]
    for ref in references:
        cmd += ["-i", str(ref)]
    # The prompt is written to stdin by the caller: codex's -i flag is variadic and would
    # swallow a trailing positional prompt as another image path.
    return cmd


def _codex_attempt(
    req: GenerationRequest, workdir: Path, log_path: Path, prompt: str, executable: str
) -> Path | None:
    (workdir / "prompt.txt").write_text(prompt, encoding="utf-8")
    cmd = _codex_command(
        executable, prompt, workdir, req.model, req.effort, req.references
    )

    with log_path.open("a", encoding="utf-8") as log_fh:
        log_fh.write(f"--- attempt at {time.strftime('%Y-%m-%dT%H:%M:%S')} ---\n")
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            cwd=workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdin is not None
        proc.stdin.write(prompt)
        proc.stdin.close()
        try:
            _stream_process(proc, log_fh, req.timeout_s, req.verbose)
        except TimeoutError:
            log_fh.write("ERROR: attempt timed out\n")
            return None

    return _discover_output(workdir)


def _generate_codex(
    req: GenerationRequest, pf: Preflight
) -> tuple[list[Path], str | None]:
    workdir = Path(tempfile.mkdtemp(prefix="codex_figure_"))
    log_path = req.log_path or req.out.with_name(req.out.name + ".codex.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    n = max(1, req.n)
    out_paths = _candidate_paths(req.out, n)
    final_message: str | None = None
    executable = pf.codex_path or "codex"

    try:
        for out_path in out_paths:
            discovered = None
            last_log_lines: list[str] = []
            for _attempt in range(2):  # one retry on any failure
                discovered = _codex_attempt(
                    req, workdir, log_path, req.prompt, executable
                )
                if log_path.exists():
                    last_log_lines = log_path.read_text(
                        encoding="utf-8", errors="replace"
                    ).splitlines()[-20:]
                if discovered is not None:
                    break

            if discovered is None:
                hints = "\n".join(pf.messages)
                raise GenerationFailed(
                    f"codex image generation failed for {out_path} after retry. "
                    f"Workdir preserved at {workdir}.\n"
                    "Last log lines:\n"
                    + "\n".join(last_log_lines)
                    + (f"\nPreflight hints:\n{hints}" if hints else "")
                )

            out_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(discovered), str(out_path))
            last_txt = workdir / "last.txt"
            if last_txt.exists():
                final_message = last_txt.read_text(
                    encoding="utf-8", errors="replace"
                ).strip()
                last_txt.unlink()  # avoid re-discovering a stale path for the next candidate
    except GenerationFailed:
        print(f"workdir preserved: {workdir}", file=sys.stderr)
        raise
    else:
        shutil.rmtree(workdir, ignore_errors=True)

    return out_paths, final_message


def _generate_api(req: GenerationRequest) -> tuple[list[Path], str | None]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise BackendUnavailable(
            "api backend requires the `openai` package (re-run with --with openai)"
        ) from exc

    client = OpenAI()
    n = max(1, req.n)
    size = validate_size(req.size if req.size != "auto" else "1024x1024")
    result = client.images.generate(
        model="gpt-image-2",
        prompt=req.prompt,
        n=n,
        size=size,
        quality=req.quality,
        output_format="png",
        background="opaque",
        moderation="auto",
    )

    out_paths = _candidate_paths(req.out, n)
    data_items = result.data or []
    if len(data_items) < len(out_paths):
        raise GenerationFailed(
            f"OpenAI Images API returned {len(data_items)} image(s), expected {len(out_paths)}"
        )
    for data_item, out_path in zip(data_items, out_paths, strict=False):
        b64 = getattr(data_item, "b64_json", None)
        if not b64:
            raise GenerationFailed("OpenAI Images API returned no base64 payload")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(base64.b64decode(b64))
    return out_paths, None


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    s = value.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        return 255, 255, 255
    try:
        return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    except ValueError:
        return 255, 255, 255


def _flatten_to_opaque(path: Path, background_color: str) -> None:
    """Flatten an RGBA/LA/PA PNG onto a solid background color and re-save as
    opaque RGB. gpt-image-2 sometimes returns a transparent PNG even when the
    prompt explicitly asked for an opaque background; a caller requesting
    background="opaque" always wants a flattened RGB result, never a
    surprise alpha channel."""
    from PIL import Image

    img = Image.open(path)
    if img.mode not in ("RGBA", "LA", "PA"):
        return
    rgba = img.convert("RGBA")
    canvas = Image.new("RGB", rgba.size, _hex_to_rgb(background_color))
    canvas.paste(rgba, mask=rgba.split()[-1])
    canvas.save(path)


def _finalize_opacity(
    paths: list[Path], background: str, background_color: str
) -> None:
    if background != "opaque":
        return
    for p in paths:
        if p.exists():
            _flatten_to_opaque(p, background_color)


def generate(req: GenerationRequest) -> GenerationResult:
    pf = preflight(req.backend, req.codex_bin)
    resolved = resolve_backend(req.backend, pf)
    start = time.monotonic()
    workdir: Path | None = None
    log_path = req.log_path

    if resolved == "fake":
        paths, final_message = _generate_fake(req)
    elif resolved == "codex":
        log_path = req.log_path or req.out.with_name(req.out.name + ".codex.log")
        paths, final_message = _generate_codex(req, pf)
    elif resolved == "api":
        paths, final_message = _generate_api(req)
    else:  # pragma: no cover - resolve_backend already validates this
        raise BackendUnavailable(f"unhandled backend: {resolved}")

    _finalize_opacity(paths, req.background, req.background_color)
    elapsed = time.monotonic() - start
    return GenerationResult(
        paths=paths,
        backend=resolved,
        elapsed_s=elapsed,
        log_path=log_path,
        workdir=workdir,
        final_message=final_message,
    )


def _edit_api(
    image: Path, instruction: str, out: Path, *, size: str, quality: str
) -> tuple[list[Path], str | None]:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise BackendUnavailable(
            "api backend requires the `openai` package (re-run with --with openai)"
        ) from exc

    client = OpenAI()
    resolved_size = validate_size(size if size != "auto" else "1024x1024")
    with image.open("rb") as fh:
        result = client.images.edit(
            model="gpt-image-2",
            image=fh,
            prompt=instruction,
            size=resolved_size,
            quality=quality,
            n=1,
        )
    data_items = result.data or []
    if not data_items:
        raise GenerationFailed("OpenAI Images API edit returned no data")
    b64 = getattr(data_items[0], "b64_json", None)
    if not b64:
        raise GenerationFailed("OpenAI Images API edit returned no base64 payload")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(b64))
    return [out], None


def edit(
    image: Path,
    instruction: str,
    out: Path,
    *,
    backend: str = "auto",
    model: str = DEFAULT_MODEL,
    effort: str = DEFAULT_EFFORT,
    timeout_s: int = 600,
    verbose: bool = False,
    log_path: Path | None = None,
    quality: str = "high",
    size: str = "auto",
    codex_bin: str | None = None,
) -> GenerationResult:
    pf = preflight(backend, codex_bin)
    resolved = resolve_backend(backend, pf)
    start = time.monotonic()
    workdir: Path | None = None

    if resolved == "fake":
        paths, final_message = _edit_fake(image, instruction, out)
    elif resolved == "codex":
        edit_prompt = (
            f"Edit the attached image. Change only: {instruction}. "
            "Preserve everything else in the image exactly as-is: composition, "
            "colors, style, proportions, and every other element. "
            "Use your built-in image_gen tool to produce the edited image. "
            "Do not display the image inline. Copy the final edited image to "
            "./output.png in the current working directory. Reply with only "
            "the absolute path to that file on success, or the single word "
            "ERROR on failure."
        )
        req = GenerationRequest(
            prompt=edit_prompt,
            out=out,
            size=size,
            quality=quality,
            n=1,
            references=[image],
            model=model,
            effort=effort,
            timeout_s=timeout_s,
            verbose=verbose,
            log_path=log_path,
            backend="codex",
            codex_bin=codex_bin,
        )
        log_path = req.log_path or req.out.with_name(req.out.name + ".codex.log")
        paths, final_message = _generate_codex(req, pf)
    elif resolved == "api":
        paths, final_message = _edit_api(
            image, instruction, out, size=size, quality=quality
        )
    else:  # pragma: no cover - resolve_backend already validates this
        raise BackendUnavailable(f"unhandled backend: {resolved}")

    elapsed = time.monotonic() - start
    return GenerationResult(
        paths=paths,
        backend=resolved,
        elapsed_s=elapsed,
        log_path=log_path,
        workdir=workdir,
        final_message=final_message,
    )
