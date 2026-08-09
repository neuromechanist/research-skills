"""CI coverage for the svg-figure editor_prep.py handoff pass.

Real SVG parsing and real font measurement where a system font exists;
no mocks of business logic. Needs lxml + svgpathtools + fonttools.

Run: uv run --with pytest --with lxml --with svgpathtools --with fonttools \
    pytest tests/test_editor_prep.py -q
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "figures" / "skills" / "svg-figure" / "scripts"
sys.path.insert(0, str(SCRIPTS))

pytest.importorskip("lxml")
pytest.importorskip("svgpathtools")
pytest.importorskip("fontTools")

import editor_prep as ep
from lxml import etree

SVG = ep.SVG

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
]


def _system_font():
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return path
    return None


def _parse(body: str, w: float = 100, h: float = 100):
    return etree.fromstring(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">{body}</svg>'
        .encode())


def test_marker_end_is_baked_at_endpoint():
    root = _parse(
        '<defs><marker id="head" orient="auto" markerUnits="userSpaceOnUse" '
        'refX="0" refY="0"><path d="M-2,-1 L0,0 L-2,1 Z"/></marker></defs>'
        '<path d="M10,50 L60,50" stroke="#cc0000" stroke-width="0.5" '
        'fill="none" marker-end="url(#head)"/>')
    report = ep.Report()
    ep.bake_markers(root, report)
    assert report.markers_baked == 1
    assert root.find(f".//{SVG}marker") is None, "unreferenced def removed"
    path = root.find(f".//{SVG}path[@d='M10,50 L60,50']")
    assert path is not None and path.get("marker-end") is None
    baked = root.findall(f".//{SVG}g")
    assert len(baked) == 1
    transform = baked[0].get("transform")
    assert "translate(60.0000 50.0000)" in transform
    assert "rotate(0.000)" in transform
    head = baked[0].find(f"{SVG}path")
    assert head.get("fill") == "#cc0000", "context-stroke fill inherited"


def test_marker_on_vertical_line_rotates():
    root = _parse(
        '<defs><marker id="head" markerUnits="userSpaceOnUse" refX="0" '
        'refY="0"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/></marker></defs>'
        '<line x1="20" y1="10" x2="20" y2="80" stroke="#000" '
        'marker-end="url(#head)"/>')
    ep.bake_markers(root, ep.Report())
    transform = root.find(f".//{SVG}g").get("transform")
    assert "rotate(90.000)" in transform


def test_stroke_width_marker_units_scale():
    root = _parse(
        '<defs><marker id="head" refX="0" refY="0">'
        '<path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/></marker></defs>'
        '<line x1="0" y1="0" x2="10" y2="0" stroke="#000" stroke-width="3" '
        'marker-end="url(#head)"/>')
    ep.bake_markers(root, ep.Report())
    assert "scale(3.0000)" in root.find(f".//{SVG}g").get("transform")


def test_nested_svg_flattened_to_transformed_group():
    root = _parse(
        '<svg x="10" y="20" width="50" height="25" viewBox="0 0 100 50" '
        'id="panel" overflow="visible"><rect x="0" y="0" width="100" '
        'height="50"/></svg>')
    report = ep.Report()
    ep.flatten_nested_svg(root, report)
    assert report.nested_svgs_flattened == 1
    assert root.find(f"{SVG}svg") is None
    g = root.find(f"{SVG}g")
    assert g.get("id") == "panel"
    assert g.get("transform") == "translate(10.0000 20.0000) scale(0.500000)"
    assert g.find(f"{SVG}rect") is not None


def test_nested_svg_nonzero_viewbox_origin_folded_in():
    root = _parse(
        '<svg x="0" y="0" width="40" height="40" viewBox="10 10 20 20" '
        'overflow="visible"><circle cx="20" cy="20" r="5"/></svg>')
    ep.flatten_nested_svg(root, ep.Report())
    transform = root.find(f"{SVG}g").get("transform")
    # scale 2, so the viewBox origin (10,10) maps to canvas (0,0)
    assert transform == "translate(-20.0000 -20.0000) scale(2.000000)"


def test_svg_datauri_inlined_with_namespaced_ids():
    import base64
    inner = (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
             b'<defs><linearGradient id="grad"/></defs>'
             b'<rect id="r" width="10" height="10" fill="url(#grad)"/></svg>')
    payload = base64.b64encode(inner).decode()
    root = _parse(
        f'<image x="5" y="5" width="20" height="20" '
        f'xlink:href="data:image/svg+xml;base64,{payload}"/>')
    report = ep.Report()
    ep.inline_svg_datauris(root, report)
    assert report.datauris_inlined == 1
    assert root.find(f"{SVG}image") is None
    g = root.find(f"{SVG}g")
    assert "translate(5.0000 5.0000)" in g.get("transform")
    rect = g.find(f".//{SVG}rect")
    assert rect.get("id") == "emb1-r"
    assert rect.get("fill") == "url(#emb1-grad)"


def test_anchor_resolution_with_real_font():
    font = _system_font()
    if font is None:
        pytest.skip("no known system font available for measurement")
    root = _parse('<text x="50" y="20" font-family="AnyFam, sans-serif" '
                  'font-size="10" text-anchor="middle">Hello</text>')
    report = ep.Report()
    ep.resolve_text_anchors(root, ep.FontMeasurer({"AnyFam": font}), report)
    assert report.anchors_resolved == 1
    text = root.find(f"{SVG}text")
    assert text.get("text-anchor") == "start"
    new_x = float(text.get("x"))
    assert new_x < 50, "middle anchor moves the left edge leftward"
    # end anchor moves twice as far as middle for the same string
    root2 = _parse('<text x="50" y="20" font-family="AnyFam" font-size="10" '
                   'text-anchor="end">Hello</text>')
    ep.resolve_text_anchors(root2, ep.FontMeasurer({"AnyFam": font}),
                            ep.Report())
    end_x = float(root2.find(f"{SVG}text").get("x"))
    assert math.isclose(50 - end_x, 2 * (50 - new_x), abs_tol=1e-3)


def test_anchor_left_alone_without_font(caplog):
    root = _parse('<text x="50" y="20" font-family="NoSuchFamily12345" '
                  'font-size="10" text-anchor="middle">Hi</text>')
    report = ep.Report()
    measurer = ep.FontMeasurer()
    measurer.font_map = {}
    measurer._resolve_path = lambda family, bold: None
    ep.resolve_text_anchors(root, measurer, report)
    assert report.anchors_resolved == 0
    assert root.find(f"{SVG}text").get("text-anchor") == "middle"
    assert any("no font file" in w for w in report.warnings)


def test_positioned_tspans_block_anchor_resolution():
    root = _parse('<text x="50" y="20" font-size="10" text-anchor="middle">'
                  '<tspan x="50" y="20">a</tspan><tspan x="50" y="30">b</tspan>'
                  '</text>')
    report = ep.Report()
    ep.resolve_text_anchors(root, ep.FontMeasurer(), report)
    assert report.anchors_resolved == 0
    assert any("positioned tspans" in w for w in report.warnings)


def test_font_normalization_and_href_duplication():
    root = _parse(
        '<text font-family="Lato, Inter, sans-serif" font-size="12px">x</text>'
        '<image width="5" height="5" href="data:image/png;base64,AAAA"/>')
    report = ep.Report()
    ep.normalize_fonts(root, report)
    ep.duplicate_raster_hrefs(root, report)
    text = root.find(f"{SVG}text")
    assert text.get("font-family") == "Lato"
    assert text.get("font-size") == "12"
    image = root.find(f"{SVG}image")
    assert image.get(ep.XLINK_HREF) == image.get("href")
    assert report.font_stacks_reduced == 1
    assert report.font_sizes_unitless == 1
    assert report.hrefs_duplicated == 1


def test_prep_tree_is_idempotent():
    import base64
    inner = (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
             b'<rect width="10" height="10"/></svg>')
    payload = base64.b64encode(inner).decode()
    root = _parse(
        '<defs><marker id="head" markerUnits="userSpaceOnUse" refX="0" '
        'refY="0"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/></marker></defs>'
        '<g id="section"><line x1="0" y1="0" x2="10" y2="0" stroke="#000" '
        'marker-end="url(#head)"/>'
        '<text x="5" y="5" font-family="A, B" font-size="4">t</text></g>'
        f'<image x="0" y="0" width="10" height="10" '
        f'xlink:href="data:image/svg+xml;base64,{payload}"/>')
    first = ep.prep_tree(root, resolve_anchors=False)
    assert first.changes > 0
    frozen = etree.tostring(root)
    second = ep.prep_tree(root, resolve_anchors=False)
    assert second.changes == 0
    assert etree.tostring(root) == frozen


def test_warnings_for_unfixable_constructs():
    root = _parse('<style>.a{fill:red}</style>'
                  '<text dominant-baseline="middle" x="1" y="1">x</text>'
                  '<filter id="f"/>')
    report = ep.Report()
    ep.collect_warnings(root, report)
    joined = " ".join(report.warnings)
    assert "<style>" in joined
    assert "dominant-baseline" in joined
    assert "filter" in joined


def test_main_check_mode_exit_codes(tmp_path):
    dirty = tmp_path / "dirty.svg"
    dirty.write_bytes(etree.tostring(_parse(
        '<text font-family="A, B" font-size="3">x</text>')))
    assert ep.main([str(dirty), "--check", "--keep-anchors"]) == 1
    clean = tmp_path / "clean.svg"
    out = tmp_path / "out.svg"
    assert ep.main([str(dirty), "-o", str(out), "--keep-anchors"]) == 0
    assert out.exists()
    clean.write_bytes(out.read_bytes())
    assert ep.main([str(clean), "--check", "--keep-anchors"]) == 0
