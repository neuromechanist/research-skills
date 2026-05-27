"""Shared fixtures and geometry helpers for the svg-primitives E2E tests.

Most geometry helpers live in `svg_primitives.validation` so production
validation and test assertions share one implementation. This module
re-exports them with the function names the existing tests already use,
plus the test-only `text_bboxes_pillow_independent` helper that is
intentionally NOT promoted into the public module (it exists specifically
to detect circular-logic regressions in the primary metrics path).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# scripts/ and examples/ are not installed; add them to sys.path so the
# package and example build() helpers are importable in pytest.
_SKILL_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _SKILL_ROOT / "scripts"
_EXAMPLES = _SKILL_ROOT / "examples"
for p in (_SCRIPTS, _EXAMPLES):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


# Re-export the public geometry helpers under their existing test names.
from svg_primitives.validation import (  # noqa: E402, F401
    SVG_NS,
    Bbox,
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
)
from svg_primitives.validation import (  # noqa: E402
    text_bboxes as _text_bboxes_3tuple,
)


def text_bboxes(layer, font_path: str | None = None) -> list[tuple[str, Bbox]]:
    """Test-facing wrapper that drops the element id, keeping the existing
    2-tuple shape that earlier tests rely on."""
    return [(content, tb) for content, tb, _id in _text_bboxes_3tuple(layer, font_path)]


def text_bboxes_pillow_independent(layer) -> list[tuple[str, Bbox]]:
    """Independent text-bbox measurement using Pillow's ImageFont.getbbox
    directly, WITHOUT touching svg_primitives.metrics.

    Used by `test_eeg_text_inside_boxes_via_independent_pillow_measurement`
    to detect a circular-logic regression where both the primary metrics
    and the primary bbox check would be off by the same systematic error.
    Returns empty list if no usable system font is found.
    """
    if layer is None:
        return []
    from PIL import ImageFont

    import os
    font_path = os.environ.get("SVG_PRIMITIVES_TEST_FONT")
    if not font_path:
        for candidate in (
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ):
            if os.path.exists(candidate):
                font_path = candidate
                break
    if not font_path:
        return []

    MEASURE_PX = 200
    try:
        font = ImageFont.truetype(font_path, size=MEASURE_PX, index=0)
    except (OSError, IOError):
        return []

    out: list[tuple[str, Bbox]] = []
    for t in layer.iter(f"{{{SVG_NS}}}text"):
        content = (t.text or "").strip()
        if not content:
            continue
        fs_mm_raw = t.get("font-size", "0")
        try:
            fs_mm = float(fs_mm_raw)
        except ValueError:
            fs_mm = 0.0
        if fs_mm <= 0:
            continue
        left, top_px, right, bottom = font.getbbox(content)
        width_px = right - left
        height_px = bottom - top_px
        if width_px <= 0 or height_px <= 0:
            continue
        scale = fs_mm / height_px
        text_w_mm = width_px * scale
        text_h_mm = fs_mm
        cx = float(t.get("x", "0"))
        baseline_y = float(t.get("y", "0"))
        ascent_mm = (-top_px) * scale if top_px < 0 else fs_mm * 0.78
        top = baseline_y - ascent_mm
        out.append((content, Bbox(cx - text_w_mm / 2, top, text_w_mm, text_h_mm)))
    return out


@pytest.fixture
def render_canvas(tmp_path):
    """Save a Canvas to tmp_path/{name}.svg and return its Path. Validation
    is turned off so deliberately-degenerate test canvases don't trigger
    the new validate='warn' default during rendering."""
    def _save(canvas, name: str = "test") -> Path:
        out = tmp_path / f"{name}.svg"
        canvas.save(out, validate="off")
        return out
    return _save
