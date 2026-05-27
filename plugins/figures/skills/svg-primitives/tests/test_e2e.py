"""End-to-end tests for svg-primitives.

Each test renders a real SVG via the public API, then parses it back from
the file system (no in-memory shortcuts) and asserts geometric or
structural invariants. No mocks.
"""

from __future__ import annotations

import pytest

from svg_primitives import Arrow, Canvas, LabeledBox

from conftest import (
    Bbox,
    SVG_NS,
    all_markers,
    arrow_paths,
    diamond_bboxes,
    dist_to_rect_edge,
    get_layer,
    get_layer_ids_in_order,
    marker_fill,
    parse_svg,
    path_endpoint,
    rect_bboxes,
    text_bboxes,
)

# Tolerances (mm). The 0.5 mm box-containment tolerance accommodates the
# approximate text-bbox calculation in the metrics layer (visual extent is
# tighter than the line-box). Arrow tip tolerance is 0.6 mm to allow for
# rounded-corner snapping vs. the sharp-corner outline path.
TEXT_TOL = 0.5
ARROW_TIP_TOL = 0.6


# ---------------------------------------------------------------------------
# 1. Text containment in canonical figures
# ---------------------------------------------------------------------------

def test_eeg_pipeline_text_inside_boxes(render_canvas):
    import eeg_pipeline
    svg = render_canvas(eeg_pipeline.build(), "eeg")
    root = parse_svg(svg)
    box_layer = get_layer(root, "boxes")
    assert box_layer is not None
    boxes = rect_bboxes(box_layer)
    texts = text_bboxes(box_layer)
    assert len(boxes) == 5
    assert len(texts) >= 5  # ICA + Bandpass + Artifact are multi-line
    for content, tb in texts:
        if not any(b.contains(tb, tol=TEXT_TOL) for b in boxes):
            pytest.fail(f"text {content!r} bbox {tb} not contained in any box {boxes}")


def test_stress_test_text_inside_boxes(render_canvas):
    import stress_test
    svg = render_canvas(stress_test.build(), "stress")
    root = parse_svg(svg)
    box_layer = get_layer(root, "boxes")
    assert box_layer is not None
    boxes = rect_bboxes(box_layer)
    texts = text_bboxes(box_layer)
    # 10 boxes including chunky/min-size; texts >= 10 (multi-line adds extra).
    assert len(boxes) == 10
    for content, tb in texts:
        if not any(b.contains(tb, tol=TEXT_TOL) for b in boxes):
            pytest.fail(f"text {content!r} bbox {tb} not contained in any box")


# ---------------------------------------------------------------------------
# 2. Arrow tips kiss target box edges
# ---------------------------------------------------------------------------

def test_arrow_tip_within_target_edge(render_canvas):
    import eeg_pipeline
    svg = render_canvas(eeg_pipeline.build(), "eeg")
    root = parse_svg(svg)
    boxes = rect_bboxes(get_layer(root, "boxes"))
    arrows = list(arrow_paths(get_layer(root, "connectors")))
    assert len(arrows) == 5  # 4 forward + 1 feedback
    for path_el in arrows:
        d = path_el.get("d", "")
        tip = path_endpoint(d)
        nearest = min(dist_to_rect_edge(tip, b) for b in boxes)
        assert nearest < ARROW_TIP_TOL, (
            f"arrow tip at {tip} is {nearest:.3f} mm from nearest box edge "
            f"(tolerance {ARROW_TIP_TOL} mm)"
        )


# ---------------------------------------------------------------------------
# 3. Arrow markers use orient='auto' (no hand-rotated triangles allowed)
# ---------------------------------------------------------------------------

def test_arrowhead_uses_marker_orient_auto(render_canvas):
    import eeg_pipeline
    svg = render_canvas(eeg_pipeline.build(), "eeg")
    root = parse_svg(svg)
    markers = all_markers(root)
    assert len(markers) >= 1
    for m in markers:
        assert m.get("orient") == "auto", (
            f"marker {m.get('id')!r} has orient={m.get('orient')!r}, "
            "expected 'auto' for tangent-correct rendering"
        )


# ---------------------------------------------------------------------------
# 4. Layer paint order matches registration order
# ---------------------------------------------------------------------------

def test_layer_paint_order_matches_registration(render_canvas):
    canvas = Canvas(width_mm=60, height_mm=30)
    a = canvas.layer("background").add(LabeledBox(x=2, y=2, text="A", font_size=7))
    canvas.layer("connectors")  # registered second
    b = canvas.layer("boxes").add(LabeledBox(x=20, y=2, text="B", font_size=7))
    canvas.layer("connectors").add(Arrow.connect(a, b))
    svg = render_canvas(canvas, "layers")
    root = parse_svg(svg)
    assert get_layer_ids_in_order(root) == [
        "layer-background", "layer-connectors", "layer-boxes",
    ]


# ---------------------------------------------------------------------------
# 5. Per-color markers, one per unique arrow stroke
# ---------------------------------------------------------------------------

def test_per_color_markers(render_canvas):
    canvas = Canvas(width_mm=80, height_mm=30)
    a = canvas.layer("boxes").add(LabeledBox(x=2, y=2, text="a", font_size=7))
    b = canvas.layer("boxes").add(LabeledBox(x=22, y=2, text="b", font_size=7))
    c = canvas.layer("boxes").add(LabeledBox(x=42, y=2, text="c", font_size=7))
    d = canvas.layer("boxes").add(LabeledBox(x=62, y=2, text="d", font_size=7))
    arrows = canvas.layer("arrows")
    arrows.add(Arrow.connect(a, b, stroke="#1F3A5F"))
    arrows.add(Arrow.connect(b, c, stroke="#C45146"))
    arrows.add(Arrow.connect(c, d, stroke="#2A6F3D"))
    svg = render_canvas(canvas, "colors")
    root = parse_svg(svg)
    fills = {marker_fill(m) for m in all_markers(root)}
    assert "#1f3a5f" in fills
    assert "#c45146" in fills
    assert "#2a6f3d" in fills


# ---------------------------------------------------------------------------
# 6. font-size is emitted in mm equal to pt * 25.4/72
# ---------------------------------------------------------------------------

def test_font_size_emitted_in_mm(render_canvas):
    canvas = Canvas(width_mm=40, height_mm=15)
    canvas.layer("boxes").add(LabeledBox(x=5, y=5, text="x", font_size=7))
    svg = render_canvas(canvas, "fontsize")
    root = parse_svg(svg)
    text_el = next(root.iter(f"{{{SVG_NS}}}text"))
    fs = float(text_el.get("font-size"))
    expected = 7 * 25.4 / 72
    assert abs(fs - expected) < 0.001, f"font-size={fs}, expected {expected}"


# ---------------------------------------------------------------------------
# 7. No text overflow at extreme label lengths (parametrized)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", ["A", "x" * 50, "y" * 200])
def test_no_text_overflow_extreme(render_canvas, text):
    canvas = Canvas(width_mm=400, height_mm=20)
    canvas.layer("boxes").add(LabeledBox(x=2, y=2, text=text, font_size=7))
    svg = render_canvas(canvas, f"overflow_{len(text)}")
    root = parse_svg(svg)
    box_layer = get_layer(root, "boxes")
    boxes = rect_bboxes(box_layer)
    texts = text_bboxes(box_layer)
    assert len(boxes) == 1
    for content, tb in texts:
        assert boxes[0].contains(tb, tol=TEXT_TOL), (
            f"text of length {len(content)} overflows box {boxes[0]} (text bbox {tb})"
        )


# ---------------------------------------------------------------------------
# 8. Diamond shape: text contained inside the diamond's bounding rect
# ---------------------------------------------------------------------------

def test_diamond_text_inside_bbox(render_canvas):
    from svg_primitives import Diamond
    canvas = Canvas(width_mm=80, height_mm=40)
    canvas.layer("boxes").add(Diamond(x=10, y=5, text="branch?", font_size=7))
    svg = render_canvas(canvas, "diamond")
    root = parse_svg(svg)
    box_layer = get_layer(root, "boxes")
    diamonds = diamond_bboxes(box_layer)
    texts = text_bboxes(box_layer)
    assert len(diamonds) == 1
    for content, tb in texts:
        assert diamonds[0].contains(tb, tol=TEXT_TOL), (
            f"text {content!r} not inside diamond bbox"
        )
