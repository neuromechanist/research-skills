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


def _export_inkscape(svg: Path, out: Path, dpi: int) -> None:
    cmd = [
        "inkscape",
        str(svg),
        f"--export-filename={out}",
        f"--export-dpi={dpi}",
    ]
    if out.suffix.lower() == ".pdf":
        cmd.append("--export-text-to-path=false")
    subprocess.run(cmd, check=True)


def _export_cairosvg(svg: Path, out: Path, dpi: int) -> None:
    import cairosvg

    if out.suffix.lower() == ".pdf":
        cairosvg.svg2pdf(url=str(svg), write_to=str(out))
    elif out.suffix.lower() == ".png":
        cairosvg.svg2png(url=str(svg), write_to=str(out), dpi=dpi)
    else:
        raise ValueError(f"cairosvg fallback supports .pdf or .png, got {out.suffix}")


def export(svg: Path, out: Path, dpi: int = 300) -> str:
    """Export svg to out (pdf or png) at the given DPI. Returns the exporter used."""
    if not svg.exists():
        raise FileNotFoundError(svg)
    out.parent.mkdir(parents=True, exist_ok=True)

    if shutil.which("inkscape"):
        _export_inkscape(svg, out, dpi)
        return "inkscape"

    print(
        "WARNING: Inkscape not found on PATH. Falling back to cairosvg; text without an installed "
        "font may be converted to paths or skipped. Install Inkscape for journal-quality PDFs: "
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

    backend = export(args.svg, args.out, args.dpi)
    print(f"wrote {args.out} via {backend}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
