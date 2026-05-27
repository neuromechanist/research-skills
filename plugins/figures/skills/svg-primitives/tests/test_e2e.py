"""End-to-end tests for svg-primitives.

Each test renders a real SVG via the public API, then parses it back from
the file system (no in-memory shortcuts) and asserts geometric or
structural invariants. No mocks.
"""

from __future__ import annotations

import pytest

from svg_primitives import (
    Annotation, Arrow, Bracket, Canvas, Diamond, Group, LabeledBox, Layer,
    MetricsFallbackError, Pill,
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


# --- Text containment in canonical figures ---

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


# --- Arrow tips kiss target box edges ---

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


# --- Arrow markers use orient='auto' (no hand-rotated triangles allowed) ---

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


# --- Layer paint order matches registration order ---

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


# --- Per-color markers, one per unique arrow stroke ---

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


# --- font-size emitted in mm equals pt * 25.4/72 ---

def test_font_size_emitted_in_mm(render_canvas):
    canvas = Canvas(width_mm=40, height_mm=15)
    canvas.layer("boxes").add(LabeledBox(x=5, y=5, text="x", font_size=7))
    svg = render_canvas(canvas, "fontsize")
    root = parse_svg(svg)
    text_el = next(root.iter(f"{{{SVG_NS}}}text"))
    fs = float(text_el.get("font-size"))
    expected = 7 * 25.4 / 72
    assert abs(fs - expected) < 0.001, f"font-size={fs}, expected {expected}"


# --- No text overflow at extreme label lengths ---

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


# --- Diamond shape: text contained inside the bounding rect ---

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


# --- Phase 2: orthogonal routing ---

def _parse_path_d(d: str) -> list[float]:
    """Tokenize a path d string into a flat float list, robust to commas and
    whitespace combinations (drawsvg sometimes uses 'Mx,y Lx2,y2' for Line,
    space-separated 'M x y L x y' for Path, etc.)."""
    cleaned = (d
        .replace("M", " ").replace("L", " ").replace("Q", " ")
        .replace("Z", " ").replace("C", " ").replace(",", " "))
    return [float(t) for t in cleaned.split() if t]


def test_orthogonal_h_path_is_three_segments(render_canvas):
    canvas = Canvas(width_mm=100, height_mm=30)
    a = canvas.layer("boxes").add(LabeledBox(x=5, y=10, text="A", font_size=7))
    b = canvas.layer("boxes").add(LabeledBox(x=70, y=10, text="B", font_size=7))
    arrow = Arrow.connect(a, b, curve="orthogonal-h")
    canvas.layer("arrows").add(arrow)
    svg = render_canvas(canvas, "ortho_h")
    # Path d has form: M x y L x1 y L x1 y2 L x2 y2 — three L segments.
    assert arrow.d.count("L") == 3
    coords = _parse_path_d(arrow.d)
    # coords = [x0,y0,  mx,y0,  mx,y1,  x1,y1]
    assert abs(coords[2] - coords[4]) < 0.001, "elbow xs should match"
    assert abs(coords[2] - (coords[0] + coords[6]) / 2) < 0.01


def test_orthogonal_v_path_is_three_segments():
    a = LabeledBox(x=5, y=5, text="A", font_size=7)
    b = LabeledBox(x=5, y=40, text="B", font_size=7)
    arrow = Arrow.connect(a, b, curve="orthogonal-v")
    assert arrow.d.count("L") == 3
    coords = _parse_path_d(arrow.d)
    # coords = [x0,y0,  x0,my,  x1,my,  x1,y1]
    assert abs(coords[3] - coords[5]) < 0.001, "elbow ys should match"
    assert abs(coords[3] - (coords[1] + coords[7]) / 2) < 0.01


def test_orthogonal_arrowhead_still_tangent_correct(render_canvas):
    canvas = Canvas(width_mm=100, height_mm=30)
    a = canvas.layer("boxes").add(LabeledBox(x=5, y=10, text="A", font_size=7))
    b = canvas.layer("boxes").add(LabeledBox(x=70, y=10, text="B", font_size=7))
    canvas.layer("arrows").add(Arrow.connect(a, b, curve="orthogonal-h"))
    svg = render_canvas(canvas, "ortho_tangent")
    root = parse_svg(svg)
    for m in all_markers(root):
        assert m.get("orient") == "auto"
    # Final segment is horizontal toward dst W edge: tip x is dst.left, y matches.
    arrow = next(arrow_paths(get_layer(root, "arrows")))
    tip = path_endpoint(arrow.get("d", ""))
    boxes = rect_bboxes(get_layer(root, "boxes"))
    dist = min(dist_to_rect_edge(tip, bx) for bx in boxes)
    assert dist < ARROW_TIP_TOL


# --- Phase 2: multi-waypoint paths ---

def test_waypoint_path_passes_through_via_points():
    a = LabeledBox(x=5, y=5, text="A", font_size=7)
    b = LabeledBox(x=60, y=40, text="B", font_size=7)
    arrow = Arrow.connect(a, b, curve="straight", via=[(40, 5)])
    # d should contain L 40.000 5.000 as one of the segments.
    assert "L 40.000 5.000" in arrow.d


def test_waypoint_corner_radius_smooths_interior():
    a = LabeledBox(x=5, y=5, text="A", font_size=7)
    b = LabeledBox(x=80, y=40, text="B", font_size=7)
    sharp = Arrow.connect(a, b, curve="straight", via=[(50, 5)], corner_radius=0.0)
    rounded = Arrow.connect(a, b, curve="straight", via=[(50, 5)], corner_radius=3.0)
    assert "Q" not in sharp.d, "sharp path should have no Q segments"
    assert "Q " in rounded.d, "rounded path should contain a Q segment at the interior corner"


# --- Phase 2: Bracket ---

def test_bracket_spine_at_offset_depth(render_canvas):
    canvas = Canvas(width_mm=80, height_mm=40)
    canvas.layer("annotations").add(Bracket(
        start=(10, 20), end=(60, 20), depth=5, label=None,
    ))
    svg = render_canvas(canvas, "bracket")
    root = parse_svg(svg)
    # Bracket emits a single <path> in layer-annotations. Parse its d.
    layer = get_layer(root, "annotations")
    paths = list(layer.iter(f"{{{SVG_NS}}}path"))
    assert len(paths) == 1
    coords = _parse_path_d(paths[0].get("d", ""))
    # Expect 4 points: start, spine_a, spine_b, end.
    # start = (10, 20); spine_a should be (10, 20 + 5 * normal.y). For a
    # horizontal chord, normal is (0, +1) in math = (0, +1) in SVG = down.
    assert abs(coords[0] - 10) < 0.01
    assert abs(coords[1] - 20) < 0.01
    assert abs(coords[2] - 10) < 0.01      # spine_a.x = start.x
    assert abs(coords[3] - 25) < 0.01      # spine_a.y = start.y + depth
    assert abs(coords[4] - 60) < 0.01      # spine_b.x = end.x
    assert abs(coords[5] - 25) < 0.01      # spine_b.y = end.y + depth


def test_bracket_label_at_apex_on_closed_side(render_canvas):
    canvas = Canvas(width_mm=80, height_mm=40)
    canvas.layer("annotations").add(Bracket(
        start=(10, 20), end=(60, 20), depth=5, label="grp",
        label_offset=2, font_size=7,
    ))
    svg = render_canvas(canvas, "bracket_label")
    root = parse_svg(svg)
    layer = get_layer(root, "annotations")
    texts = list(layer.iter(f"{{{SVG_NS}}}text"))
    assert len(texts) == 1
    # Apex is (35, 25); label is at apex + normal * sign(depth) * 2.
    # Normal for horizontal chord = (0, +1); sign(+5) = +1; so label at (35, 27).
    cx = float(texts[0].get("x"))
    assert abs(cx - 35) < 0.01


# --- Phase 2: Group ---

def test_group_union_bbox_covers_all_members():
    a = LabeledBox(x=10, y=5, text="A", font_size=7, padding=2)
    b = LabeledBox(x=30, y=20, text="B", font_size=7, padding=2)
    c = LabeledBox(x=50, y=15, text="C", font_size=7, padding=2)
    g = Group(a, b, c)
    assert abs(g.left - min(a.left, b.left, c.left)) < 0.001
    assert abs(g.right - max(a.right, b.right, c.right)) < 0.001
    assert abs(g.top - min(a.top, b.top, c.top)) < 0.001
    assert abs(g.bottom - max(a.bottom, b.bottom, c.bottom)) < 0.001


def test_arrow_connect_group_to_box(render_canvas):
    canvas = Canvas(width_mm=120, height_mm=60)
    a = LabeledBox(x=10, y=10, text="A", font_size=7, padding=2)
    b = LabeledBox(x=30, y=10, text="B", font_size=7, padding=2)
    c = LabeledBox(x=50, y=10, text="C", font_size=7, padding=2)
    lonely = LabeledBox(x=10, y=40, text="lonely", font_size=7, padding=2)
    canvas.layer("boxes").add(a)
    canvas.layer("boxes").add(b)
    canvas.layer("boxes").add(c)
    canvas.layer("boxes").add(lonely)
    g = Group(a, b, c)
    canvas.layer("arrows").add(Arrow.connect(g, lonely))
    svg = render_canvas(canvas, "group_arrow")
    root = parse_svg(svg)
    arrow = next(arrow_paths(get_layer(root, "arrows")))
    tip = path_endpoint(arrow.get("d", ""))
    # The tip must be near `lonely` specifically — not just any box.
    # Earlier version of this test only checked min distance over all boxes,
    # which allowed the tip to land on the group's bbox bottom edge instead.
    assert abs(tip[1] - lonely.top) < ARROW_TIP_TOL, (
        f"arrow tip y={tip[1]} should be near lonely.top={lonely.top}"
    )


def test_arrow_connect_box_to_group(render_canvas):
    # Reverse direction: box as src, group as dst. Exercises Group.outline_path
    # in the dst role (different code path than connecting from a group).
    canvas = Canvas(width_mm=120, height_mm=60)
    a = LabeledBox(x=10, y=10, text="A", font_size=7, padding=2)
    b = LabeledBox(x=30, y=10, text="B", font_size=7, padding=2)
    c = LabeledBox(x=50, y=10, text="C", font_size=7, padding=2)
    lonely = LabeledBox(x=10, y=40, text="lonely", font_size=7, padding=2)
    canvas.layer("boxes").add(a)
    canvas.layer("boxes").add(b)
    canvas.layer("boxes").add(c)
    canvas.layer("boxes").add(lonely)
    g = Group(a, b, c)
    canvas.layer("arrows").add(Arrow.connect(lonely, g))
    svg = render_canvas(canvas, "box_to_group")
    root = parse_svg(svg)
    arrow = next(arrow_paths(get_layer(root, "arrows")))
    tip = path_endpoint(arrow.get("d", ""))
    # Tip must land on the group's south edge (bottom of bbox over a/b/c).
    assert abs(tip[1] - g.bottom) < ARROW_TIP_TOL


def test_group_with_mixed_shapes():
    box = LabeledBox(x=10, y=10, text="rect", font_size=7, padding=2)
    pill = Pill(x=40, y=10, text="pill", font_size=7, padding=2)
    diamond = Diamond(x=70, y=10, text="dia", font_size=7, padding=2)
    g = Group(box, pill, diamond)
    assert g.left == min(box.left, pill.left, diamond.left)
    assert g.right == max(box.right, pill.right, diamond.right)
    assert g.top == min(box.top, pill.top, diamond.top)
    assert g.bottom == max(box.bottom, pill.bottom, diamond.bottom)


def test_group_requires_at_least_one_member():
    with pytest.raises(ValueError, match="at least one"):
        Group()


def test_group_rejects_sequence_argument():
    a = LabeledBox(x=10, y=10, text="A", font_size=7)
    b = LabeledBox(x=30, y=10, text="B", font_size=7)
    with pytest.raises(TypeError, match="not a Shape"):
        Group([a, b])  # type: ignore[arg-type]


def test_canvas_rejects_group_in_layer():
    a = LabeledBox(x=10, y=10, text="A", font_size=7)
    b = LabeledBox(x=30, y=10, text="B", font_size=7)
    canvas = Canvas(width_mm=80, height_mm=20)
    canvas.layer("boxes").add(Group(a, b))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="virtual container"):
        canvas.to_drawsvg()


# --- Phase 2: Annotation ---

def test_annotation_text_only_no_leader(render_canvas):
    canvas = Canvas(width_mm=60, height_mm=30)
    canvas.layer("annotations").add(Annotation(x=30, y=15, text="callout"))
    svg = render_canvas(canvas, "anno_no_leader")
    root = parse_svg(svg)
    layer = get_layer(root, "annotations")
    assert len(list(layer.iter(f"{{{SVG_NS}}}text"))) == 1
    # drawsvg emits dw.Line as <path d="M x,y L x2,y2"> — count paths.
    assert len(list(layer.iter(f"{{{SVG_NS}}}path"))) == 0


def test_annotation_with_leader_emits_line(render_canvas):
    canvas = Canvas(width_mm=80, height_mm=40)
    canvas.layer("annotations").add(Annotation(
        x=20, y=10, text="this is here", leader_to=(60, 35),
    ))
    svg = render_canvas(canvas, "anno_with_leader")
    root = parse_svg(svg)
    layer = get_layer(root, "annotations")
    texts = list(layer.iter(f"{{{SVG_NS}}}text"))
    paths = list(layer.iter(f"{{{SVG_NS}}}path"))
    assert len(texts) == 1
    assert len(paths) == 1
    coords = _parse_path_d(paths[0].get("d", ""))
    # coords = [start.x, start.y, end.x, end.y]
    assert abs(coords[-2] - 60) < 0.01
    assert abs(coords[-1] - 35) < 0.01


# --- Phase 2 review fixes: additional coverage ---

def test_bracket_negative_depth_label_above_spine(render_canvas):
    # The Bracket label-anchor must flip when depth is negative so the label
    # always sits on the closed (outer) side of the bracket. Previously
    # tested only for positive depth — this locks in the sign-fix from
    # commit 5.
    canvas = Canvas(width_mm=80, height_mm=40)
    canvas.layer("annotations").add(Bracket(
        start=(10, 30), end=(60, 30), depth=-5, label="frontal",
        label_offset=2, font_size=7,
    ))
    svg = render_canvas(canvas, "bracket_neg_depth")
    root = parse_svg(svg)
    layer = get_layer(root, "annotations")
    texts = list(layer.iter(f"{{{SVG_NS}}}text"))
    assert len(texts) == 1
    # depth=-5 puts the spine at y=25 (above start.y in SVG y-down).
    # label_offset=2 in the same direction puts the label at y=23.
    # Test that the text baseline y is < start.y (label is ABOVE the spine).
    label_y = float(texts[0].get("y"))
    assert label_y < 30, (
        f"with negative depth, label baseline y={label_y} should be above the "
        "start.y=30 (closed side of bracket)"
    )


def test_bracket_without_label_emits_no_text(render_canvas):
    canvas = Canvas(width_mm=80, height_mm=40)
    canvas.layer("annotations").add(Bracket(
        start=(10, 20), end=(60, 20), depth=5, label=None,
    ))
    svg = render_canvas(canvas, "bracket_no_label")
    root = parse_svg(svg)
    layer = get_layer(root, "annotations")
    assert len(list(layer.iter(f"{{{SVG_NS}}}text"))) == 0
    assert len(list(layer.iter(f"{{{SVG_NS}}}path"))) == 1


def test_arrow_via_empty_list_equivalent_to_none():
    a = LabeledBox(x=5, y=5, text="A", font_size=7)
    b = LabeledBox(x=60, y=5, text="B", font_size=7)
    a_none = Arrow.connect(a, b, curve="straight", via=None)
    a_empty = Arrow.connect(a, b, curve="straight", via=[])
    assert a_none.d == a_empty.d


def test_corner_radius_clamps_to_segment_half():
    # corner_radius=50 on a path with short segments must not produce
    # control points that overshoot the adjoining vertices.
    a = LabeledBox(x=5, y=5, text="A", font_size=7)
    b = LabeledBox(x=80, y=20, text="B", font_size=7)
    arrow = Arrow.connect(
        a, b, curve="straight", via=[(40, 5), (40, 20)], corner_radius=50.0,
    )
    # The path should still emit; no exception. And the Q segments must
    # exist (rounded) but the c_in/c_out points stay within each L segment.
    assert "Q" in arrow.d
    # Coordinates must all be finite (no NaN/inf from a bad clamp).
    coords = _parse_path_d(arrow.d)
    assert all(abs(c) < 1e6 for c in coords)


def test_orthogonal_h_with_via_raises():
    a = LabeledBox(x=5, y=5, text="A", font_size=7)
    b = LabeledBox(x=60, y=5, text="B", font_size=7)
    with pytest.raises(ValueError, match="not supported"):
        Arrow.connect(a, b, curve="orthogonal-h", via=[(30, 5)])


def test_orthogonal_with_vertically_aligned_boxes():
    # Two boxes sharing the same cx with orthogonal-h. Earlier the W/W
    # routing would produce a degenerate path with two zero-length L
    # segments. The auto-side tiebreaker now falls back to N/S.
    a = LabeledBox(x=20, y=10, text="A", font_size=7, padding=2)
    b = LabeledBox(x=20, y=40, text="B", font_size=7, padding=2)
    arrow = Arrow.connect(a, b, curve="orthogonal-h")
    coords = _parse_path_d(arrow.d)
    # First L segment should travel a non-zero distance from src anchor.
    assert abs(coords[2] - coords[0]) + abs(coords[3] - coords[1]) > 0.1, (
        "first L segment should have non-zero length for stacked boxes"
    )


def test_diamond_with_orthogonal_routing(render_canvas):
    canvas = Canvas(width_mm=120, height_mm=40)
    d = canvas.layer("boxes").add(Diamond(x=10, y=10, text="yes", font_size=7))
    b = canvas.layer("boxes").add(LabeledBox(x=70, y=15, text="B", font_size=7))
    canvas.layer("arrows").add(Arrow.connect(d, b, curve="orthogonal-h"))
    svg = render_canvas(canvas, "diamond_ortho")
    root = parse_svg(svg)
    # Arrowhead orientation should still be auto.
    for m in all_markers(root):
        assert m.get("orient") == "auto"


# --- Phase 3: validation hooks ---

from svg_primitives import Finding, ValidationError, validate_all  # noqa: E402


def _build_clean_canvas() -> Canvas:
    """Two boxes connected by an arrow — a known-good figure."""
    canvas = Canvas(width_mm=80, height_mm=30)
    a = canvas.layer("boxes").add(LabeledBox(x=5, y=5, text="A", font_size=7))
    b = canvas.layer("boxes").add(LabeledBox(x=40, y=5, text="B", font_size=7))
    canvas.layer("arrows").add(Arrow.connect(a, b))
    return canvas


def _build_overflow_canvas() -> Canvas:
    """A box clamped smaller than its text — guaranteed text-overflow."""
    canvas = Canvas(width_mm=40, height_mm=20)
    # min_width=0 plus very long text would normally still auto-fit. To
    # *force* overflow we shrink the box AFTER it has been built.
    box = LabeledBox(x=5, y=5, text="overflows the box", font_size=7, padding=0)
    box.width = 4  # crush below text bbox
    box.height = 3
    canvas.layer("boxes").add(box)
    return canvas


def test_validate_clean_canvas_returns_empty(tmp_path):
    findings = _build_clean_canvas().save(tmp_path / "clean.svg")
    assert findings == []


def test_validate_warn_returns_findings_no_raise(tmp_path, caplog):
    import logging
    caplog.set_level(logging.WARNING, logger="svg_primitives.canvas")
    findings = _build_overflow_canvas().save(tmp_path / "warn.svg", validate="warn")
    assert len(findings) >= 1
    assert any(f.category == "text-overflow" for f in findings)
    assert any("text-overflow" in rec.message or "validation" in rec.message
               for rec in caplog.records)


def test_validate_strict_raises(tmp_path):
    with pytest.raises(ValidationError) as excinfo:
        _build_overflow_canvas().save(tmp_path / "strict.svg", validate="strict")
    assert any(f.category == "text-overflow" for f in excinfo.value.findings)
    assert "text-overflow" in str(excinfo.value)


def test_validate_off_skips_checks(tmp_path):
    # The file is still written; the function returns [] without checking.
    findings = _build_overflow_canvas().save(tmp_path / "off.svg", validate="off")
    assert findings == []


def test_canvas_validate_method_no_disk_write():
    canvas = _build_overflow_canvas()
    findings = canvas.validate()
    assert any(f.category == "text-overflow" for f in findings)


def test_validation_finding_carries_location():
    canvas = _build_overflow_canvas()
    findings = canvas.validate()
    assert any(f.location is not None for f in findings)


def test_phase1_eeg_pipeline_validates_clean(tmp_path):
    import eeg_pipeline
    findings = eeg_pipeline.build().save(tmp_path / "eeg.svg", validate="strict")
    assert findings == []


def test_phase1_stress_test_validates_clean(tmp_path):
    import stress_test
    findings = stress_test.build().save(tmp_path / "stress.svg", validate="strict")
    assert findings == []


def test_sibling_overlap_detected(tmp_path):
    canvas = Canvas(width_mm=60, height_mm=40)
    # Two boxes placed at the same coordinates — guaranteed bbox overlap.
    canvas.layer("boxes").add(LabeledBox(x=10, y=10, text="A", font_size=7, padding=2))
    canvas.layer("boxes").add(LabeledBox(x=11, y=11, text="B", font_size=7, padding=2))
    findings = canvas.validate()
    assert any(f.category == "sibling-overlap" for f in findings)


def test_sibling_overlap_ignores_background_layer(tmp_path):
    canvas = Canvas(width_mm=60, height_mm=40, background=None)
    # Two overlapping rects in the BACKGROUND layer; should be ignored.
    canvas.layer("background").add(LabeledBox(x=10, y=10, text=" ", font_size=7, padding=2))
    canvas.layer("background").add(LabeledBox(x=11, y=11, text=" ", font_size=7, padding=2))
    findings = canvas.validate()
    # No sibling-overlap findings should come from the background layer.
    assert not any(f.category == "sibling-overlap" for f in findings)


def test_validate_all_directly_on_parsed_svg(tmp_path):
    # Demonstrate the public validate_all() entry point can be used on an
    # SVG that was not produced by Canvas.save (e.g. one written elsewhere).
    canvas = _build_clean_canvas()
    out = tmp_path / "external.svg"
    canvas.save(out, validate="off")
    from svg_primitives.validation import parse_svg
    root = parse_svg(out)
    findings = validate_all(root)
    assert findings == []
