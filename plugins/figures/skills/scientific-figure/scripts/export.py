"""Export a composed SVG to PDF or PNG.

Runtime exporter detection:

- **Inkscape** when `inkscape` is on `$PATH`. Best text fidelity; fonts are subsetted and remain
  text in the PDF. Install once with `brew install inkscape` (macOS) or `sudo apt install inkscape`.
- **cairosvg** as a fallback. Pure-Python via uv; text without an installed font is converted to
  paths or skipped, which is acceptable for sanity-check renders but not for journal submission.

Usage:

    uv run --with cairosvg python export.py figure.svg --out figure.pdf
    uv run --with cairosvg python export.py figure.svg --out figure.png --dpi 600
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


SUPPORTED_SUFFIXES = {".pdf", ".png"}


def _export_inkscape(svg: Path, out: Path, dpi: int) -> None:
    # Inkscape 1.x: --export-filename infers format from the suffix. Text is preserved by
    # default in pre-1.3; on 1.3+ text may be converted to paths during PDF export.
    cmd = [
        "inkscape",
        str(svg),
        f"--export-filename={out}",
        f"--export-dpi={dpi}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(
            f"inkscape exited {result.returncode} exporting '{svg}'.\n{stderr}"
        )


def _export_cairosvg(svg: Path, out: Path, dpi: int) -> None:
    try:
        import cairosvg
    except ImportError as exc:
        raise RuntimeError(
            "cairosvg is not installed and inkscape is not on PATH. Install one: "
            "`brew install inkscape` (macOS), `sudo apt install inkscape` (Debian/Ubuntu), "
            "or `uv pip install cairosvg`."
        ) from exc

    suffix = out.suffix.lower()
    if suffix == ".pdf":
        cairosvg.svg2pdf(url=str(svg), write_to=str(out))
    elif suffix == ".png":
        cairosvg.svg2png(url=str(svg), write_to=str(out), dpi=dpi)
    else:
        # Defensive: should be caught upstream in export().
        raise ValueError(f"cairosvg supports .pdf or .png, got {out.suffix}")


def export(svg: Path, out: Path, dpi: int = 300) -> str:
    """Export svg to out (pdf or png) at the given DPI. Returns the exporter used."""
    if not svg.exists():
        raise FileNotFoundError(svg)
    if out.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(
            f"output suffix must be one of {sorted(SUPPORTED_SUFFIXES)}, got '{out.suffix}'"
        )
    out.parent.mkdir(parents=True, exist_ok=True)

    if shutil.which("inkscape"):
        _export_inkscape(svg, out, dpi)
        return "inkscape"

    print(
        "WARNING: inkscape not found on PATH. Falling back to cairosvg; text without an installed "
        "font may be converted to paths or skipped. Install inkscape for journal-quality PDFs: "
        "`brew install inkscape` (macOS) or `sudo apt install inkscape` (Debian/Ubuntu).",
        file=sys.stderr,
    )
    _export_cairosvg(svg, out, dpi)
    return "cairosvg"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export a composed SVG to PDF or PNG (Inkscape preferred, cairosvg fallback)."
    )
    parser.add_argument("svg", type=Path, help="Input SVG path")
    parser.add_argument("--out", type=Path, required=True, help="Output path (.pdf or .png)")
    parser.add_argument("--dpi", type=int, default=300, help="Raster DPI (PNG only; default 300)")
    args = parser.parse_args(argv)

    try:
        backend = export(args.svg, args.out, args.dpi)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"wrote {args.out} via {backend}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
