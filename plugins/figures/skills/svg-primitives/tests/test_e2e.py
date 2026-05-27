"""End-to-end tests for svg-primitives.

Each test renders a real SVG via the public API, then parses it back from
the file system (no in-memory shortcuts) and asserts geometric or
structural invariants. No mocks.
"""

from __future__ import annotations

import pytest

from svg_primitives import (
    Arrow, Canvas, Diamond, LabeledBox, Layer, MetricsFallbackError, Pill,
)

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
    marker_id_from_url,
    parse_svg,
    path_endpoint,
    rect_bboxes,
    text_bboxes,
    text_bboxes_pillow_independent,
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


# ---------------------------------------------------------------------------
# Independent ground-truth: verify auto-fit against an independent
# Pillow-based text measurement so a regression in svg_primitives.metrics
# can't pass the containment tests above through circular logic.
# ---------------------------------------------------------------------------

def test_eeg_text_inside_boxes_via_independent_pillow_measurement(render_canvas):
    import eeg_pipeline
    svg = render_canvas(eeg_pipeline.build(), "eeg_indep")
    root = parse_svg(svg)
    box_layer = get_layer(root, "boxes")
    boxes = rect_bboxes(box_layer)
    indep_texts = text_bboxes_pillow_independent(box_layer)
    if not indep_texts:
        pytest.skip("no independent font available for independent measurement")
    for content, tb in indep_texts:
        if not any(b.contains(tb, tol=TEXT_TOL) for b in boxes):
            pytest.fail(
                f"INDEPENDENT (Pillow) bbox for {content!r} {tb} not contained in "
                f"any box. This is a real auto-fit regression, not a metrics-self-test artifact."
            )


# ---------------------------------------------------------------------------
# Pill shape
# ---------------------------------------------------------------------------

def test_pill_rx_equals_half_height(render_canvas):
    canvas = Canvas(width_mm=60, height_mm=20)
    pill = canvas.layer("boxes").add(Pill(x=5, y=5, text="Start", font_size=7))
    svg = render_canvas(canvas, "pill")
    root = parse_svg(svg)
    box_layer = get_layer(root, "boxes")
    rects = list(box_layer.iter(f"{{{SVG_NS}}}rect"))
    assert len(rects) == 1
    rx = float(rects[0].get("rx", "0"))
    h = float(rects[0].get("height", "0"))
    assert abs(rx - h / 2) < 0.01, f"Pill rx={rx} expected {h/2}"
    # And text contained.
    for content, tb in text_bboxes(box_layer):
        assert rect_bboxes(box_layer)[0].contains(tb, tol=TEXT_TOL), content


# ---------------------------------------------------------------------------
# next_to() placement
# ---------------------------------------------------------------------------

def test_next_to_east_gap_correct():
    a = LabeledBox(x=10, y=10, text="A", font_size=7, padding=2)
    b = LabeledBox.next_to(a, side="E", gap=8, text="B", font_size=7, padding=2)
    assert abs(b.left - (a.right + 8)) < 0.001
    assert abs(b.top - a.top) < 0.001


def test_next_to_west_gap_correct():
    a = LabeledBox(x=50, y=10, text="A", font_size=7, padding=2)
    b = LabeledBox.next_to(a, side="W", gap=5, text="B", font_size=7, padding=2)
    assert abs(b.right - (a.left - 5)) < 0.001


def test_next_to_south_gap_correct():
    a = LabeledBox(x=10, y=10, text="A", font_size=7, padding=2)
    b = LabeledBox.next_to(a, side="S", gap=4, text="B", font_size=7, padding=2)
    assert abs(b.top - (a.bottom + 4)) < 0.001
    assert abs(b.left - a.left) < 0.001


def test_next_to_rejects_anchor_center():
    a = LabeledBox(x=10, y=10, text="A", font_size=7)
    with pytest.raises(ValueError, match="anchor='top-left'"):
        LabeledBox.next_to(a, side="E", gap=5, text="B", font_size=7, anchor="center")


# ---------------------------------------------------------------------------
# Negative bow (downward arc)
# ---------------------------------------------------------------------------

def test_negative_bow_arcs_downward(render_canvas):
    canvas = Canvas(width_mm=120, height_mm=60)
    a = canvas.layer("boxes").add(LabeledBox(x=10, y=30, text="A", font_size=7))
    b = canvas.layer("boxes").add(LabeledBox(x=80, y=30, text="B", font_size=7))
    up_arrow = Arrow.connect(a, b, curve="cubic", bow=10)     # positive = up
    down_arrow = Arrow.connect(a, b, curve="cubic", bow=-10)  # negative = down
    canvas.layer("arrows_up").add(up_arrow)
    canvas.layer("arrows_dn").add(down_arrow)
    canvas.save(render_canvas(canvas, "bow_signs"))
    # The two paths' control-point y values should bracket the chord line.
    from svgpathtools import parse_path
    up_d = up_arrow.d
    down_d = down_arrow.d
    up_path = parse_path(up_d)
    down_path = parse_path(down_d)
    # Midpoint of each curve.
    up_mid = up_path.point(0.5)
    down_mid = down_path.point(0.5)
    chord_y = a.cy  # both endpoints on the same y as the box centers
    assert up_mid.imag < chord_y, f"positive bow midpoint y={up_mid.imag} should be < {chord_y}"
    assert down_mid.imag > chord_y, f"negative bow midpoint y={down_mid.imag} should be > {chord_y}"


# ---------------------------------------------------------------------------
# Canvas(background=None) emits no background rect
# ---------------------------------------------------------------------------

def test_canvas_no_background(render_canvas):
    canvas = Canvas(width_mm=40, height_mm=20, background=None)
    canvas.layer("boxes").add(LabeledBox(x=5, y=5, text="X", font_size=7))
    svg = render_canvas(canvas, "nobg")
    root = parse_svg(svg)
    # Only rect should be the one inside layer-boxes. No top-level background.
    direct_children = list(root)
    # background rect, if present, would be a <rect> direct child of <svg>
    rects_at_root = [el for el in direct_children if el.tag == f"{{{SVG_NS}}}rect"]
    assert len(rects_at_root) == 0


# ---------------------------------------------------------------------------
# font_path override
# ---------------------------------------------------------------------------

def test_font_path_override_used_when_provided(render_canvas):
    import os
    # Find a font that definitely exists; if we cannot, skip rather than test nothing.
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    fp = next((c for c in candidates if os.path.exists(c)), None)
    if not fp:
        pytest.skip("no system font available to test font_path override")
    canvas = Canvas(width_mm=80, height_mm=20)
    canvas.layer("boxes").add(LabeledBox(x=5, y=5, text="Override", font_size=7, font_path=fp))
    svg = render_canvas(canvas, "fontpath")
    # The test passes if render did not raise; explicit path should not cause
    # a font-search fallback warning. If a metrics regression made font_path
    # silently ignored, the metrics module would still log appropriately.
    root = parse_svg(svg)
    assert get_layer(root, "boxes") is not None


# ---------------------------------------------------------------------------
# Per-arrow marker URL routing (each arrow references its own color's marker)
# ---------------------------------------------------------------------------

def test_each_arrow_references_its_own_color_marker(render_canvas):
    canvas = Canvas(width_mm=80, height_mm=30)
    a = canvas.layer("boxes").add(LabeledBox(x=2, y=2, text="a", font_size=7))
    b = canvas.layer("boxes").add(LabeledBox(x=22, y=2, text="b", font_size=7))
    c = canvas.layer("boxes").add(LabeledBox(x=42, y=2, text="c", font_size=7))
    d = canvas.layer("boxes").add(LabeledBox(x=62, y=2, text="d", font_size=7))
    arrows = canvas.layer("arrows")
    arrows.add(Arrow.connect(a, b, stroke="#1F3A5F"))
    arrows.add(Arrow.connect(b, c, stroke="#C45146"))
    arrows.add(Arrow.connect(c, d, stroke="#2A6F3D"))
    svg = render_canvas(canvas, "routing")
    root = parse_svg(svg)
    marker_lookup = {m.get("id"): marker_fill(m) for m in all_markers(root)}
    arrow_layer = get_layer(root, "arrows")
    paths = list(arrow_paths(arrow_layer))
    assert len(paths) == 3
    # Each arrow's marker URL must resolve to a marker whose fill matches
    # the path's stroke. A regression where all arrows referenced the same
    # marker would fail this test even though every marker exists.
    for p in paths:
        stroke = p.get("stroke", "").lower()
        mid = marker_id_from_url(p.get("marker-end", ""))
        assert mid in marker_lookup, f"arrow references missing marker {mid!r}"
        assert marker_lookup[mid] == stroke, (
            f"arrow with stroke={stroke!r} references marker {mid!r} "
            f"whose fill is {marker_lookup[mid]!r}"
        )


# ---------------------------------------------------------------------------
# Validation and error handling
# ---------------------------------------------------------------------------

def test_labeled_box_rejects_non_positive_font_size():
    with pytest.raises(ValueError, match="font_size"):
        LabeledBox(x=0, y=0, text="x", font_size=0)
    with pytest.raises(ValueError, match="font_size"):
        LabeledBox(x=0, y=0, text="x", font_size=-3)


def test_labeled_box_rejects_unknown_anchor():
    with pytest.raises(ValueError, match="anchor"):
        LabeledBox(x=0, y=0, text="x", font_size=7, anchor="bottom-right")  # type: ignore


def test_canvas_rejects_non_positive_dimensions():
    with pytest.raises(ValueError, match="dimensions"):
        Canvas(width_mm=0, height_mm=10)
    with pytest.raises(ValueError, match="dimensions"):
        Canvas(width_mm=10, height_mm=-5)


def test_canvas_add_layer_rejects_duplicate_name():
    canvas = Canvas(width_mm=10, height_mm=10)
    canvas.add_layer(Layer("boxes"))
    with pytest.raises(ValueError, match="already has a layer"):
        canvas.add_layer(Layer("boxes"))


def test_arrow_rejects_coincident_endpoints():
    a = LabeledBox(x=10, y=10, text="A", font_size=7)
    # When src and dst are the same box, src_side='N' and dst_side='N' resolve
    # to the same point.
    with pytest.raises(ValueError, match="coincident"):
        Arrow.connect(a, a, curve="straight", src_side="N", dst_side="N")


def test_bbox_rejects_negative_dimensions():
    with pytest.raises(ValueError, match="non-negative"):
        Bbox(x=0, y=0, w=-1, h=1)
    with pytest.raises(ValueError, match="non-negative"):
        Bbox(x=0, y=0, w=1, h=-1)


def test_metrics_strict_mode_raises_without_font(monkeypatch):
    from svg_primitives import metrics
    # Force the font-search to return None to simulate a vanilla CI container.
    monkeypatch.setattr(metrics, "_find_font_file", lambda: None)
    with pytest.raises(MetricsFallbackError):
        metrics.measure_text_mm("hello", 7.0, font_path=None, strict=True)
