"""CI coverage for the svg-figure editor_prep.py handoff pass.

Real SVG parsing and real font measurement where a system font exists;
no mocks of business logic. Needs lxml + svgpathtools + fonttools.

Run: uv run --with pytest --with lxml --with svgpathtools --with fonttools \
    pytest tests/test_editor_prep.py -q
"""

from __future__ import annotations

import base64
import math
import sys
import urllib.parse
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

TTC_CANDIDATES = ["/System/Library/Fonts/Helvetica.ttc"]

INNER_SVG = (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
             b'<defs><linearGradient id="grad"/></defs>'
             b'<rect id="r" width="10" height="10" fill="url(#grad)"/></svg>')


def _system_font():
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return path
    return None


def _parse(body: str, w: float = 100, h: float = 100, width_attr: str = "mm"):
    return etree.fromstring(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}{width_attr}" height="{h}{width_attr}" '
        f'viewBox="0 0 {w} {h}">{body}</svg>'.encode())


# --- transform 1: marker baking ----------------------------------------------

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
    assert baked[0].get("transform") == "translate(60.0000 50.0000)"
    head = baked[0].find(f"{SVG}path")
    assert head.get("fill") == "#cc0000", "context-stroke fill inherited"


def test_marker_on_vertical_line_rotates():
    root = _parse(
        '<defs><marker id="head" orient="auto" markerUnits="userSpaceOnUse" '
        'refX="0" refY="0"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/>'
        '</marker></defs>'
        '<line x1="20" y1="10" x2="20" y2="80" stroke="#000" '
        'marker-end="url(#head)"/>')
    ep.bake_markers(root, ep.Report())
    assert "rotate(90.000)" in root.find(f".//{SVG}g").get("transform")


def test_marker_on_cubic_path_uses_end_tangent():
    root = _parse(
        '<defs><marker id="head" orient="auto" markerUnits="userSpaceOnUse" '
        'refX="0" refY="0"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/>'
        '</marker></defs>'
        '<path d="M0,0 C0,10 10,10 10,20" stroke="#000" fill="none" '
        'marker-end="url(#head)"/>')
    ep.bake_markers(root, ep.Report())
    transform = root.find(f".//{SVG}g").get("transform")
    assert "translate(10.0000 20.0000)" in transform
    assert "rotate(90.000)" in transform, "tangent at t=1 is vertical"


def test_marker_on_polyline_uses_last_segment():
    root = _parse(
        '<defs><marker id="head" orient="auto" markerUnits="userSpaceOnUse" '
        'refX="0" refY="0"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/>'
        '</marker></defs>'
        '<polyline points="0,0 10,0 10,10" stroke="#000" fill="none" '
        'marker-end="url(#head)"/>')
    ep.bake_markers(root, ep.Report())
    transform = root.find(f".//{SVG}g").get("transform")
    assert "translate(10.0000 10.0000)" in transform
    assert "rotate(90.000)" in transform


def test_marker_viewbox_scaled_to_marker_width():
    # The svg-figure SKILL.md canonical arrow: 10x10 viewBox in a 3x3 box.
    root = _parse(
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="3" markerHeight="3" markerUnits="userSpaceOnUse" '
        'orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#000"/>'
        '</marker></defs>'
        '<line x1="40" y1="17" x2="55" y2="17" stroke="#000" '
        'marker-end="url(#arrow)"/>')
    ep.bake_markers(root, ep.Report())
    transform = root.find(f".//{SVG}g").get("transform")
    assert transform == ("translate(55.0000 17.0000) "
                         "translate(-2.7000 -1.5000) scale(0.300000)")


def test_marker_svg_primitives_geometry_scale():
    # svg-primitives emits viewBox="-2 -1 2 2" in a 2.4x2.4 box (1.2x).
    root = _parse(
        '<defs><marker id="arrow" viewBox="-2 -1 2 2" refX="0" refY="0" '
        'markerWidth="2.4" markerHeight="2.4" markerUnits="userSpaceOnUse" '
        'orient="auto"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/>'
        '</marker></defs>'
        '<line x1="0" y1="0" x2="10" y2="0" stroke="#000" '
        'marker-end="url(#arrow)"/>')
    ep.bake_markers(root, ep.Report())
    transform = root.find(f".//{SVG}g").get("transform")
    assert transform == "translate(10.0000 0.0000) scale(1.200000)"


def test_marker_fixed_orient_not_rotated_by_tangent():
    # Per spec the default orient is "0", not "auto".
    root = _parse(
        '<defs><marker id="a" markerUnits="userSpaceOnUse" refX="0" refY="0">'
        '<path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/></marker>'
        '<marker id="b" orient="45" markerUnits="userSpaceOnUse" refX="0" '
        'refY="0"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/></marker></defs>'
        '<line x1="20" y1="10" x2="20" y2="80" stroke="#000" '
        'marker-end="url(#a)"/>'
        '<line x1="30" y1="10" x2="30" y2="80" stroke="#000" '
        'marker-end="url(#b)"/>')
    ep.bake_markers(root, ep.Report())
    groups = root.findall(f".//{SVG}g")
    assert "rotate" not in groups[0].get("transform")
    assert "rotate(45.000)" in groups[1].get("transform")


def test_stroke_width_marker_units_scale():
    root = _parse(
        '<defs><marker id="head" orient="auto" refX="0" refY="0">'
        '<path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/></marker></defs>'
        '<line x1="0" y1="0" x2="10" y2="0" stroke="#000" stroke-width="3" '
        'marker-end="url(#head)"/>')
    ep.bake_markers(root, ep.Report())
    assert "scale(3.0000)" in root.find(f".//{SVG}g").get("transform")


def test_stroke_width_with_px_suffix_does_not_crash():
    root = _parse(
        '<defs><marker id="head" orient="auto" refX="0" refY="0">'
        '<path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/></marker></defs>'
        '<line x1="0" y1="0" x2="10" y2="0" stroke="#000" '
        'stroke-width="2px" marker-end="url(#head)"/>')
    report = ep.Report()
    ep.bake_markers(root, report)
    assert report.markers_baked == 1
    assert "scale(2.0000)" in root.find(f".//{SVG}g").get("transform")


def test_marker_fill_inherited_from_ancestor_group():
    root = _parse(
        '<defs><marker id="head" orient="auto" markerUnits="userSpaceOnUse" '
        'refX="0" refY="0"><path d="M-2,-1 L0,0 L-2,1 Z"/></marker></defs>'
        '<g stroke="#123456"><line x1="0" y1="0" x2="10" y2="0" '
        'marker-end="url(#head)"/></g>')
    ep.bake_markers(root, ep.Report())
    head = root.find(f".//{SVG}g/{SVG}g/{SVG}path")
    assert head.get("fill") == "#123456"


def test_marker_def_kept_while_marker_start_references_it():
    root = _parse(
        '<defs><marker id="head" orient="auto" markerUnits="userSpaceOnUse" '
        'refX="0" refY="0"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/>'
        '</marker></defs>'
        '<line x1="0" y1="0" x2="10" y2="0" stroke="#000" '
        'marker-end="url(#head)"/>'
        '<line x1="0" y1="5" x2="10" y2="5" stroke="#000" '
        'marker-start="url(#head)"/>')
    report = ep.Report()
    ep.bake_markers(root, report)
    assert report.markers_baked == 1
    assert root.find(f".//{SVG}marker") is not None, \
        "def still referenced by marker-start must survive"
    assert root.find(f".//{SVG}line[@marker-start]") is not None
    assert any("marker-start" in w for w in report.warnings)


def test_missing_marker_id_warns_and_skips():
    root = _parse('<line x1="0" y1="0" x2="10" y2="0" stroke="#000" '
                  'marker-end="url(#ghost)"/>')
    report = ep.Report()
    ep.bake_markers(root, report)
    assert report.markers_baked == 0
    assert report.markers_skipped == 1
    assert any("missing id 'ghost'" in w for w in report.warnings)


# --- transforms 3+4: viewport flattening -------------------------------------

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


def test_preserve_aspect_ratio_slice_uses_max_scale():
    root = _parse(
        '<svg x="0" y="0" width="100" height="50" viewBox="0 0 100 100" '
        'preserveAspectRatio="xMidYMid slice" overflow="visible">'
        '<rect width="100" height="100"/></svg>')
    ep.flatten_nested_svg(root, ep.Report())
    # slice keeps scale 1 and crops vertically: ty = (50-100)/2 = -25
    assert root.find(f"{SVG}g").get("transform") == "translate(0.0000 -25.0000)"


def test_preserve_aspect_ratio_xmax_alignment_offset():
    root = _parse(
        '<svg x="0" y="0" width="100" height="100" viewBox="0 0 50 100" '
        'preserveAspectRatio="xMaxYMin meet" overflow="visible">'
        '<rect width="50" height="100"/></svg>')
    ep.flatten_nested_svg(root, ep.Report())
    assert root.find(f"{SVG}g").get("transform") == "translate(50.0000 0.0000)"


def test_preserve_aspect_ratio_none_scales_anisotropically():
    root = _parse(
        '<svg x="0" y="0" width="100" height="50" viewBox="0 0 100 100" '
        'preserveAspectRatio="none" overflow="visible">'
        '<rect width="100" height="100"/></svg>')
    ep.flatten_nested_svg(root, ep.Report())
    assert root.find(f"{SVG}g").get("transform") == "scale(1.000000 0.500000)"


def test_nested_svg_with_only_viewbox_still_flattens():
    root = _parse('<svg viewBox="0 0 30 30" overflow="visible">'
                  '<rect width="30" height="30"/></svg>')
    report = ep.Report()
    ep.flatten_nested_svg(root, report)
    assert report.nested_svgs_flattened == 1
    assert root.find(f"{SVG}g").get("transform") is None


def test_default_overflow_clip_loss_is_warned():
    root = _parse('<svg x="0" y="0" width="10" height="10" '
                  'viewBox="0 0 10 10"><rect width="10" height="10"/></svg>')
    report = ep.Report()
    ep.flatten_nested_svg(root, report)
    assert any("no longer clipped" in w for w in report.warnings)


def test_flatten_continues_past_unfixable_element():
    root = _parse(
        '<svg id="bad"><rect width="5" height="5"/></svg>'
        '<svg id="good" x="1" y="2" width="10" height="10" '
        'viewBox="0 0 10 10" overflow="visible">'
        '<rect width="10" height="10"/></svg>')
    report = ep.Report()
    ep.flatten_nested_svg(root, report)
    assert report.nested_svgs_flattened == 1, "good one still flattened"
    assert report.nested_svgs_skipped == 1
    remaining = root.findall(f"{SVG}svg")
    assert len(remaining) == 1 and remaining[0].get("id") == "bad"


def test_percentage_coordinates_skip_with_warning_not_zero():
    root = _parse('<svg x="25%" y="10%" width="20" height="20" '
                  'viewBox="0 0 20 20" overflow="visible">'
                  '<rect width="20" height="20"/></svg>')
    report = ep.Report()
    ep.flatten_nested_svg(root, report)
    assert report.nested_svgs_flattened == 0
    assert report.nested_svgs_skipped == 1
    assert any("unsupported" in w and "25%" in w for w in report.warnings)


def test_svg_datauri_inlined_with_namespaced_ids():
    payload = base64.b64encode(INNER_SVG).decode()
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


def test_percent_encoded_svg_datauri_inlined():
    payload = urllib.parse.quote(INNER_SVG.decode())
    root = _parse(f'<image x="0" y="0" width="10" height="10" '
                  f'href="data:image/svg+xml,{payload}"/>')
    report = ep.Report()
    ep.inline_svg_datauris(root, report)
    assert report.datauris_inlined == 1
    assert root.find(f".//{SVG}rect").get("id") == "emb1-r"


# --- transform 2: text anchors -----------------------------------------------

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


def test_anchor_in_style_attribute_resolved_and_cleaned():
    font = _system_font()
    if font is None:
        pytest.skip("no known system font available for measurement")
    root = _parse('<text x="50" y="20" font-family="AnyFam" font-size="10" '
                  'style="text-anchor:middle;fill:red">Hi</text>')
    report = ep.Report()
    ep.resolve_text_anchors(root, ep.FontMeasurer({"AnyFam": font}), report)
    assert report.anchors_resolved == 1
    text = root.find(f"{SVG}text")
    assert text.get("text-anchor") == "start"
    assert "text-anchor" not in (text.get("style") or "")
    assert "fill:red" in text.get("style")


def test_anchor_inherited_from_ancestor_group_resolved():
    font = _system_font()
    if font is None:
        pytest.skip("no known system font available for measurement")
    root = _parse('<g text-anchor="middle"><text x="50" y="20" '
                  'font-family="AnyFam" font-size="10">Hi</text></g>')
    report = ep.Report()
    ep.resolve_text_anchors(root, ep.FontMeasurer({"AnyFam": font}), report)
    assert report.anchors_resolved == 1
    assert root.find(f".//{SVG}text").get("text-anchor") == "start"


def test_pt_font_size_measures_like_equivalent_user_units():
    font = _system_font()
    if font is None:
        pytest.skip("no known system font available for measurement")
    # In a px-unit document 12pt == 16 user units.
    body = ('<text x="50" y="20" font-family="AnyFam" font-size="12pt" '
            'text-anchor="middle">Hello</text>'
            '<text x="50" y="40" font-family="AnyFam" font-size="16" '
            'text-anchor="middle">Hello</text>')
    root = _parse(body, width_attr="px")
    ep.resolve_text_anchors(root, ep.FontMeasurer({"AnyFam": font}),
                            ep.Report(), uupx=1.0)
    texts = root.findall(f"{SVG}text")
    assert texts[0].get("x") == texts[1].get("x")


def test_letter_spacing_widens_measured_text():
    font = _system_font()
    if font is None:
        pytest.skip("no known system font available for measurement")
    body = ('<text x="50" y="20" font-family="AnyFam" font-size="10" '
            'text-anchor="middle">Hello</text>'
            '<text x="50" y="40" font-family="AnyFam" font-size="10" '
            'letter-spacing="2" text-anchor="middle">Hello</text>')
    root = _parse(body)
    ep.resolve_text_anchors(root, ep.FontMeasurer({"AnyFam": font}),
                            ep.Report())
    plain, spaced = (float(t.get("x")) for t in root.findall(f"{SVG}text"))
    # 4 gaps x 2 units, half on each side of the center
    assert math.isclose(plain - spaced, 4.0, abs_tol=1e-3)


def test_unsupported_letter_spacing_skips_with_warning():
    font = _system_font()
    if font is None:
        pytest.skip("no known system font available for measurement")
    root = _parse('<text x="50" y="20" font-family="AnyFam" font-size="10" '
                  'letter-spacing="0.1em" text-anchor="middle">Hi</text>')
    report = ep.Report()
    ep.resolve_text_anchors(root, ep.FontMeasurer({"AnyFam": font}), report)
    assert report.anchors_resolved == 0
    assert report.anchors_skipped == 1
    assert any("letter-spacing" in w for w in report.warnings)


def test_anchor_left_alone_without_font():
    root = _parse('<text x="50" y="20" font-family="NoSuchFamily12345" '
                  'font-size="10" text-anchor="middle">Hi</text>')
    report = ep.Report()
    ep.resolve_text_anchors(root, ep.FontMeasurer(), report)
    assert report.anchors_resolved == 0
    assert report.anchors_skipped == 1
    assert root.find(f"{SVG}text").get("text-anchor") == "middle"
    assert any("no font file found" in w for w in report.warnings)


def test_corrupt_font_file_reports_load_failure_not_missing(tmp_path):
    bad = tmp_path / "corrupt.ttf"
    bad.write_bytes(b"this is not a font")
    root = _parse('<text x="50" y="20" font-family="Fam" font-size="10" '
                  'text-anchor="middle">Hi</text>')
    report = ep.Report()
    ep.resolve_text_anchors(root, ep.FontMeasurer({"Fam": str(bad)}), report)
    assert report.anchors_resolved == 0
    assert any("failed to load" in w for w in report.warnings)
    assert not any("no font file found" in w for w in report.warnings)


def test_positioned_tspans_block_anchor_resolution():
    root = _parse('<text x="50" y="20" font-size="10" text-anchor="middle">'
                  '<tspan x="50" y="20">a</tspan><tspan x="50" y="30">b</tspan>'
                  '</text>')
    report = ep.Report()
    ep.resolve_text_anchors(root, ep.FontMeasurer(), report)
    assert report.anchors_resolved == 0
    assert any("positioned tspans" in w for w in report.warnings)


def test_mixed_weight_tspan_blocks_anchor_resolution():
    font = _system_font()
    if font is None:
        pytest.skip("no known system font available for measurement")
    root = _parse('<text x="50" y="20" font-family="AnyFam" font-size="10" '
                  'text-anchor="middle">a<tspan font-weight="bold">b</tspan>'
                  '</text>')
    report = ep.Report()
    ep.resolve_text_anchors(root, ep.FontMeasurer({"AnyFam": font}), report)
    assert report.anchors_resolved == 0
    assert any("font-weight" in w for w in report.warnings)


def test_ttc_font_measures():
    ttc = next((p for p in TTC_CANDIDATES if Path(p).exists()), None)
    if ttc is None:
        pytest.skip("no TrueType Collection font available")
    w = ep.FontMeasurer({"Fam": ttc}).width("Hi", "Fam", 10, False)
    assert w is not None and w > 0


# --- transforms 5+6 and warnings ---------------------------------------------

def test_font_normalization_and_href_duplication():
    root = _parse(
        '<text font-family="Lato, Inter, sans-serif" font-size="12px">x</text>'
        '<image width="5" height="5" href="data:image/png;base64,AAAA"/>',
        width_attr="px")
    report = ep.Report()
    ep.normalize_fonts(root, report, uupx=1.0)
    ep.duplicate_image_hrefs(root, report)
    text = root.find(f"{SVG}text")
    assert text.get("font-family") == "Lato"
    assert text.get("font-size") == "12"
    image = root.find(f"{SVG}image")
    assert image.get(ep.XLINK_HREF) == image.get("href")
    assert report.font_stacks_reduced == 1
    assert report.font_sizes_converted == 1
    assert report.hrefs_duplicated == 1


def test_px_font_size_converted_in_mm_viewport_document():
    root = _parse('<text font-size="12px" x="1" y="1">x</text>')  # mm root
    report = ep.prep_tree(root, resolve_anchors=False)
    size = float(root.find(f"{SVG}text").get("font-size"))
    assert math.isclose(size, 12 * 25.4 / 96, rel_tol=1e-4)
    assert report.font_sizes_converted == 1


def test_unit_scale_from_root():
    assert math.isclose(ep._unit_scale(_parse("", width_attr="px")), 1.0)
    assert math.isclose(ep._unit_scale(_parse("")), 25.4 / 96, rel_tol=1e-6)
    assert ep._unit_scale(etree.fromstring(b'<svg/>')) == 1.0


def test_warnings_for_unfixable_constructs():
    root = _parse('<style>@font-face{font-family:X;} .a{fill:red}</style>'
                  '<text dominant-baseline="middle" x="1" y="1">x</text>'
                  '<filter id="f"/>'
                  '<rect style="font: 12px sans-serif" width="1" height="1"/>')
    report = ep.Report()
    ep.collect_warnings(root, report)
    joined = " ".join(report.warnings)
    assert "<style>" in joined
    assert "@font-face" in joined
    assert "dominant-baseline" in joined
    assert "filter" in joined
    assert "shorthand" in joined


# --- driver and CLI -----------------------------------------------------------

def test_full_default_pipeline_end_to_end(tmp_path):
    font = _system_font()
    if font is None:
        pytest.skip("no known system font available for measurement")
    payload = base64.b64encode(INNER_SVG).decode()
    root = _parse(
        '<defs><marker id="head" orient="auto" markerUnits="userSpaceOnUse" '
        'refX="0" refY="0"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/>'
        '</marker></defs>'
        '<g id="section"><line x1="0" y1="0" x2="10" y2="0" stroke="#000" '
        'marker-end="url(#head)"/>'
        '<text x="50" y="20" font-family="AnyFam, serif" font-size="10" '
        'text-anchor="middle">Hello</text></g>'
        '<svg x="1" y="1" width="10" height="10" viewBox="0 0 10 10" '
        'overflow="visible"><rect width="10" height="10"/></svg>'
        f'<image x="0" y="0" width="10" height="10" '
        f'xlink:href="data:image/svg+xml;base64,{payload}"/>')
    report = ep.prep_tree(root, {"AnyFam": font})
    assert report.markers_baked == 1
    assert report.anchors_resolved == 1
    assert report.nested_svgs_flattened == 1
    assert report.datauris_inlined == 1
    assert report.font_stacks_reduced == 1
    second = ep.prep_tree(root, {"AnyFam": font})
    assert second.changes == 0, "default pipeline must be idempotent"


def test_prep_tree_is_idempotent():
    payload = base64.b64encode(INNER_SVG).decode()
    root = _parse(
        '<defs><marker id="head" orient="auto" markerUnits="userSpaceOnUse" '
        'refX="0" refY="0"><path d="M-2,-1 L0,0 L-2,1 Z" fill="#000"/>'
        '</marker></defs>'
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


def test_main_check_fails_on_warnings_only(tmp_path):
    f = tmp_path / "styled.svg"
    f.write_bytes(etree.tostring(_parse("<style>.a{fill:red}</style>")))
    assert ep.main([str(f), "--check", "--keep-anchors"]) == 1


def test_main_in_place(tmp_path):
    f = tmp_path / "figure.svg"
    f.write_bytes(etree.tostring(_parse(
        '<text font-family="A, B" font-size="3">x</text>')))
    assert ep.main([str(f), "--in-place", "--keep-anchors"]) == 0
    assert b'font-family="A"' in f.read_bytes()


def test_main_clean_errors_for_bad_input(tmp_path):
    with pytest.raises(SystemExit) as exc:
        ep.main([str(tmp_path / "missing.svg"), "--check"])
    assert exc.value.code == 2
    broken = tmp_path / "broken.svg"
    broken.write_text("<svg><rect</svg>")
    with pytest.raises(SystemExit) as exc:
        ep.main([str(broken), "--check"])
    assert exc.value.code == 2
    with pytest.raises(SystemExit) as exc:
        ep.main([str(broken), "--font", "no-equals-sign"])
    assert exc.value.code == 2
