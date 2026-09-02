"""Multi-panel figure orchestrator.

Reads a `figure.json` spec, generates panel images (or a single whole-figure
image) via the shared image backend, composes panel PNGs into an SVG grid
with `scientific-figure/scripts/compose.py`, exports PNG/PDF with
`export.py`, and writes a `manifest.json` with the exact figure-qa
`check_raster.py` commands to run next.

Spec schema:
    {
      "theme": "theme.json",
      "layout": "single" | "panels",
      "size": "2048x1024",
      "quality": "high",
      "consistency": "first-panel" | "none",
      "parallel": 3,
      "panels": [
        {
          "id": "a",
          "subject": "...",
          "size": "1024x1024",
          "text": [
            {"role": "panel-letter", "text": "a", "placement": "top-left"},
            {"role": "title", "text": "EEG recording", "placement": "bottom-center", "size_class": "large"}
          ]
        }
      ],
      "compose": {"journal": "nature", "width": "single" | "double", "columns": 2, "gap_mm": 3, "label_style": "lowercase"}
    }

Usage:
    uv run --with pillow --with svgutils --with lxml --with cairosvg python build_figure.py \\
        --spec figure.json --out figures/fig1/ --backend fake

Exit codes: 0 success, 1 one or more panels failed to generate, 2 usage/spec/text-ladder error.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import importlib.util
import json
import math
import sys
import time
from pathlib import Path
from types import ModuleType

_PLUGIN_ROOT = Path(__file__).resolve().parents[3]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib import image_backend, prompting

_SCIENTIFIC_FIGURE_SCRIPTS = _PLUGIN_ROOT / "skills" / "scientific-figure" / "scripts"

# Journal single/double-column widths in mm, mirrored from lib/theme.py's
# JOURNAL_PROFILES so this script has no import-time coupling to a module
# another worker is actively editing.
JOURNAL_WIDTHS_MM: dict[str, dict[str, float]] = {
    "nature": {"single": 89.0, "double": 183.0},
    "science": {"single": 55.0, "double": 120.0},
    "cell": {"single": 85.0, "double": 174.0},
    "pnas": {"single": 87.0, "double": 180.0},
    "generic": {"single": 89.0, "double": 183.0},
}


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module {name!r} from {path}")
    module = importlib.util.module_from_spec(spec)
    # Register before exec_module: CPython 3.14's dataclasses implementation
    # looks the module up via sys.modules[cls.__module__] while decorating a
    # @dataclass at import time, which fails with an opaque AttributeError
    # on a module that was never inserted into sys.modules.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _png_size(path: Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(path) as img:
        return img.size


def _wrap_png_as_svg(png_path: Path, width_mm: float) -> Path:
    """Embed a PNG panel as a minimal mm-sized SVG so compose.py can place it."""
    import base64

    pw, ph = _png_size(png_path)
    height_mm = width_mm * (ph / pw)
    b64 = base64.b64encode(png_path.read_bytes()).decode("ascii")
    # The viewBox is in millimetres so svgutils places the panel at scale 1.0 on the
    # mm canvas; a pixel viewBox would be placed one user unit per mm.
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_mm}mm" '
        f'height="{height_mm:.3f}mm" viewBox="0 0 {width_mm} {height_mm:.3f}">\n'
        f'  <image href="data:image/png;base64,{b64}" x="0" y="0" '
        f'width="{width_mm}" height="{height_mm:.3f}"/>\n'
        "</svg>\n"
    )
    wrapper_path = png_path.with_suffix(".svg")
    wrapper_path.write_text(svg)
    return wrapper_path


def _panel_label(panel_id: str, style: str) -> str:
    if style == "uppercase":
        return panel_id.upper()
    if style == "lowercase":
        return panel_id.lower()
    return panel_id


def _qa_command(
    plugin_root: Path,
    png: Path,
    journal: str,
    width_mm: float,
    theme_path: Path | None,
    texts: list[str],
) -> str:
    check_script = plugin_root / "agents" / "figure-qa-scripts" / "check_raster.py"
    parts = [
        "uv run --with pillow --with colorthief --with pytesseract python",
        str(check_script),
        str(png),
        "--json",
        "--journal",
        journal,
        "--width-mm",
        str(width_mm),
    ]
    if theme_path is not None:
        parts += ["--palette", str(theme_path)]
    for t in texts:
        parts += ["--expect-text", f'"{t}"']
    return " ".join(parts)


def _text_items_from_spec(entries: list[dict]) -> list[prompting.TextItem]:
    return [
        prompting.TextItem(
            text=t["text"],
            role=t.get("role", "label"),
            placement=t.get("placement", "center"),
            size_class=t.get("size_class"),
            style=t.get("style"),
        )
        for t in entries
    ]


def _build_single_prompt(
    spec_doc: dict, theme: dict | None, size: str, quality: str, background: str
) -> tuple[str, list[str]]:
    panels = spec_doc.get("panels", [])
    subjects = []
    all_text_items: list[prompting.TextItem] = []
    for p in panels:
        pid = p["id"]
        subjects.append(f"panel {pid}: {p['subject']}")
        for t in p.get("text", []):
            all_text_items.append(
                prompting.TextItem(
                    text=t["text"],
                    role=t.get("role", "label"),
                    placement=f"panel {pid}, {t.get('placement', 'center')}",
                    size_class=t.get("size_class"),
                    style=t.get("style"),
                )
            )
    prompting.enforce_text_ladder(all_text_items, theme)

    compose_cfg = spec_doc.get("compose") or {}
    columns = compose_cfg.get("columns", 2)
    combined_subject = (
        f"A single composed figure image containing {len(panels)} panels: "
        + "; ".join(subjects)
        + "."
    )
    layout = (
        f"{len(panels)}-panel grid arranged in {columns} column(s); each panel "
        "visually separated with clear boundaries; panel letters and titles "
        "placed exactly as described in the text list below"
    )
    prompt = prompting.build_figure_prompt(
        combined_subject,
        theme=theme,
        text=all_text_items,
        size=size,
        quality=quality,
        background=background,
        layout=layout,
        extra_avoid=[],
    )
    return prompt, [t.text for t in all_text_items]


def _generate_panel(
    panel_spec: dict,
    *,
    out_dir: Path,
    theme: dict | None,
    default_size: str,
    default_quality: str,
    background: str,
    background_color: str,
    backend: str,
    codex_bin: str | None,
    model: str,
    effort: str,
    timeout_s: int,
    verbose: bool,
    references: list[Path],
) -> dict:
    pid = panel_spec["id"]
    text_items = _text_items_from_spec(panel_spec.get("text", []))
    size = image_backend.validate_size(panel_spec.get("size", default_size))
    quality = panel_spec.get("quality", default_quality)
    prompt = prompting.build_figure_prompt(
        panel_spec["subject"],
        theme=theme,
        text=text_items,
        size=size,
        quality=quality,
        background=background,
        layout=panel_spec.get("layout"),
        extra_avoid=[],
    )
    out_path = out_dir / f"panel_{pid}.png"
    report: dict = {
        "id": pid,
        "prompt": prompt,
        "texts": [t.text for t in text_items],
        "size": size,
    }
    try:
        req = image_backend.GenerationRequest(
            prompt=prompt,
            out=out_path,
            size=size,
            quality=quality,
            n=1,
            references=references,
            model=model,
            effort=effort,
            timeout_s=timeout_s,
            background=background,
            background_color=background_color,
            verbose=verbose,
            backend=backend,
            codex_bin=codex_bin,
        )
        result = image_backend.generate(req)
        report.update(
            success=True,
            path=str(result.paths[0]),
            backend=result.backend,
            elapsed_s=result.elapsed_s,
            error=None,
        )
    except (image_backend.BackendUnavailable, image_backend.GenerationFailed) as exc:
        report.update(
            success=False, path=None, backend=None, elapsed_s=None, error=str(exc)
        )
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multi-panel AI figure orchestrator.")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument(
        "--backend", choices=["auto", "codex", "api", "fake"], default="auto"
    )
    parser.add_argument(
        "--codex-bin",
        default=None,
        help="Explicit codex executable path (else $CODEX_BIN, then PATH)",
    )
    parser.add_argument(
        "--parallel", type=int, default=None, help="Override spec.parallel"
    )
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--print-prompts", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        spec_doc = json.loads(args.spec.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: could not load spec '{args.spec}': {exc}", file=sys.stderr)
        return 2

    theme_path: Path | None = None
    theme: dict | None = None
    if spec_doc.get("theme"):
        theme_path = Path(spec_doc["theme"])
        if not theme_path.is_absolute():
            theme_path = (args.spec.parent / theme_path).resolve()
        try:
            theme = json.loads(theme_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: could not load theme '{theme_path}': {exc}", file=sys.stderr)
            return 2

    layout = spec_doc.get("layout", "panels")
    if layout not in ("single", "panels"):
        print(
            f"error: spec layout must be 'single' or 'panels', got {layout!r}",
            file=sys.stderr,
        )
        return 2

    panels = spec_doc.get("panels") or []
    if not panels:
        print(f"error: spec '{args.spec}' has no panels", file=sys.stderr)
        return 2

    model_prefs = (theme or {}).get("model_preferences") or {}
    default_size_req = spec_doc.get("size", "auto")
    default_quality = (
        spec_doc.get("quality") or model_prefs.get("image_quality") or "high"
    )
    model = model_prefs.get("codex_model") or image_backend.DEFAULT_MODEL
    effort = model_prefs.get("codex_effort") or image_backend.DEFAULT_EFFORT
    background = spec_doc.get("background", "opaque")
    background_color = ((theme or {}).get("palette") or {}).get(
        "background"
    ) or "#FFFFFF"
    consistency = spec_doc.get("consistency", "none")
    parallel = args.parallel or int(spec_doc.get("parallel", 3))

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    compose_cfg = spec_doc.get("compose") or {}
    journal = compose_cfg.get("journal", "generic")
    default_width_key = "double" if compose_cfg.get("columns", 1) > 1 else "single"
    width_key = compose_cfg.get("width", default_width_key)
    journal_widths = JOURNAL_WIDTHS_MM.get(journal, JOURNAL_WIDTHS_MM["generic"])
    fig_width_mm = journal_widths.get(width_key, journal_widths["single"])

    start = time.monotonic()

    if layout == "single":
        try:
            size = image_backend.validate_size(default_size_req)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        try:
            prompt, texts = _build_single_prompt(
                spec_doc, theme, size, default_quality, background
            )
        except prompting.TextLadderError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        if args.print_prompts:
            print(prompt)

        out_path = out_dir / "figure.png"
        try:
            req = image_backend.GenerationRequest(
                prompt=prompt,
                out=out_path,
                size=size,
                quality=default_quality,
                n=1,
                references=[],
                model=model,
                effort=effort,
                timeout_s=args.timeout,
                background=background,
                background_color=background_color,
                verbose=args.verbose,
                backend=args.backend,
                codex_bin=args.codex_bin,
            )
            result = image_backend.generate(req)
        except (
            image_backend.BackendUnavailable,
            image_backend.GenerationFailed,
        ) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        elapsed = time.monotonic() - start
        qa_cmd = _qa_command(
            _PLUGIN_ROOT, result.paths[0], journal, fig_width_mm, theme_path, texts
        )
        manifest = {
            "spec": spec_doc,
            "layout": "single",
            "backend": result.backend,
            "elapsed_s": elapsed,
            "prompt": prompt,
            "path": str(result.paths[0]),
            "qa_commands": [qa_cmd],
        }
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        print(str(result.paths[0]))
        print(f"elapsed: {elapsed:.1f}s ({result.backend})", file=sys.stderr)
        return 0

    # --- panels mode ---
    ladder_errors = []
    for p in panels:
        items = _text_items_from_spec(p.get("text", []))
        try:
            prompting.enforce_text_ladder(items, theme)
        except prompting.TextLadderError as exc:
            ladder_errors.append(f"panel {p['id']}: {exc}")
    if ladder_errors:
        print(
            "error: text ladder violation(s):\n" + "\n".join(ladder_errors),
            file=sys.stderr,
        )
        return 2

    common_kwargs = {
        "out_dir": out_dir,
        "theme": theme,
        "default_size": default_size_req,
        "default_quality": default_quality,
        "background": background,
        "background_color": background_color,
        "backend": args.backend,
        "codex_bin": args.codex_bin,
        "model": model,
        "effort": effort,
        "timeout_s": args.timeout,
        "verbose": args.verbose,
    }

    reports: list[dict] = []

    def _print_prompt(r: dict) -> None:
        if args.print_prompts and r.get("prompt"):
            print(f"[{r['id']}]\n{r['prompt']}\n")

    if consistency == "first-panel":
        first, *rest = panels
        first_report = _generate_panel(first, references=[], **common_kwargs)
        reports.append(first_report)
        _print_prompt(first_report)
        if not first_report["success"]:
            for p in rest:
                reports.append(
                    {
                        "id": p["id"],
                        "prompt": None,
                        "texts": [],
                        "success": False,
                        "path": None,
                        "error": "skipped: first panel (consistency reference) failed to generate",
                    }
                )
        else:
            ref_path = Path(first_report["path"])
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max(1, parallel)
            ) as pool:
                futures = [
                    pool.submit(
                        _generate_panel, p, references=[ref_path], **common_kwargs
                    )
                    for p in rest
                ]
                for fut in concurrent.futures.as_completed(futures):
                    r = fut.result()
                    reports.append(r)
                    _print_prompt(r)
    else:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max(1, parallel)
        ) as pool:
            futures = [
                pool.submit(_generate_panel, p, references=[], **common_kwargs)
                for p in panels
            ]
            for fut in concurrent.futures.as_completed(futures):
                r = fut.result()
                reports.append(r)
                _print_prompt(r)

    order = {p["id"]: i for i, p in enumerate(panels)}
    reports.sort(key=lambda r: order.get(r["id"], 0))
    failed = [r["id"] for r in reports if not r["success"]]

    if failed:
        print(
            f"error: panel generation failed for: {', '.join(failed)}", file=sys.stderr
        )
        for r in reports:
            if not r["success"]:
                print(f"  {r['id']}: {r['error']}", file=sys.stderr)
        manifest = {
            "spec": spec_doc,
            "layout": "panels",
            "panels": reports,
            "elapsed_s": time.monotonic() - start,
            "qa_commands": [],
        }
        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2, default=str)
        )
        return 1

    # --- compose ---
    columns = compose_cfg.get("columns", min(len(panels), 2))
    gap_mm = float(compose_cfg.get("gap_mm", 3.0))
    label_style = compose_cfg.get("label_style", "lowercase")
    panel_width_mm = (fig_width_mm - gap_mm * (columns - 1)) / columns

    panel_heights_mm = []
    for r in reports:
        pw, ph = _png_size(Path(r["path"]))
        panel_heights_mm.append(panel_width_mm * ph / pw)

    rows = math.ceil(len(reports) / columns)
    row_heights = [0.0] * rows
    for idx, h in enumerate(panel_heights_mm):
        row = idx // columns
        row_heights[row] = max(row_heights[row], h)
    row_y = [0.0] * rows
    for r_idx in range(1, rows):
        row_y[r_idx] = row_y[r_idx - 1] + row_heights[r_idx - 1] + gap_mm
    fig_height_mm = (row_y[-1] + row_heights[-1]) if rows else 0.0

    compose_mod = _load_module(
        "_build_figure_compose", _SCIENTIFIC_FIGURE_SCRIPTS / "compose.py"
    )
    export_mod = _load_module(
        "_build_figure_export", _SCIENTIFIC_FIGURE_SCRIPTS / "export.py"
    )

    fig = compose_mod.Figure(
        width_mm=fig_width_mm, height_mm=fig_height_mm, journal=journal
    )
    for idx, r in enumerate(reports):
        col = idx % columns
        row = idx // columns
        x_mm = col * (panel_width_mm + gap_mm)
        y_mm = row_y[row]
        # The model already rendered the panel letter when the spec asked for one;
        # do not stamp a second letter from the composer.
        spec_panel = next((sp for sp in panels if sp.get("id") == r["id"]), {})
        has_letter = any(
            t.get("role") == "panel-letter" for t in spec_panel.get("text", [])
        )
        label = (
            None
            if (has_letter or label_style == "none")
            else _panel_label(r["id"], label_style)
        )
        svg_src = _wrap_png_as_svg(Path(r["path"]), panel_width_mm)
        fig.add_panel(str(svg_src), x_mm=x_mm, y_mm=y_mm, scale=1.0, label=label)

    svg_path = out_dir / "figure.svg"
    fig.save(svg_path)

    png_path = out_dir / "figure.png"
    export_mod.export(svg_path, png_path, dpi=300)

    pdf_path = out_dir / "figure.pdf"
    pdf_written = True
    try:
        export_mod.export(svg_path, pdf_path, dpi=300)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        pdf_written = False
        print(f"warning: PDF export skipped: {exc}", file=sys.stderr)

    qa_commands = [
        _qa_command(
            _PLUGIN_ROOT,
            Path(r["path"]),
            journal,
            panel_width_mm,
            theme_path,
            r["texts"],
        )
        for r in reports
    ]
    qa_commands.append(
        _qa_command(
            _PLUGIN_ROOT,
            png_path,
            journal,
            fig_width_mm,
            theme_path,
            [t for r in reports for t in r["texts"]],
        )
    )

    elapsed = time.monotonic() - start
    manifest = {
        "spec": spec_doc,
        "layout": "panels",
        "backend": reports[0]["backend"] if reports else None,
        "elapsed_s": elapsed,
        "panels": reports,
        "compose": {
            "svg": str(svg_path),
            "png": str(png_path),
            "pdf": str(pdf_path) if pdf_written else None,
            "width_mm": fig_width_mm,
            "height_mm": fig_height_mm,
        },
        "qa_commands": qa_commands,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    print(str(png_path))
    print(f"elapsed: {elapsed:.1f}s", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
