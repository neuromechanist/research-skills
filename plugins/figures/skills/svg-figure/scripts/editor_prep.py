"""Rewrite an SVG into the editor-safe dialect for Illustrator / Affinity handoff.

Applies the mechanical transforms from references/editor-handoff.md to ANY SVG
(svg-primitives output, matplotlib export, hand-authored, Inkscape save):

  1. Bake marker-end arrowheads into explicit geometry at the path endpoint
     (Illustrator has a filed bug rendering paths with markers). Honors the
     marker's viewBox/markerWidth/markerHeight scaling, refX/refY, orient
     (auto, auto-start-reverse, fixed angle), and markerUnits. marker-start
     and marker-mid are warned about, not baked.
  2. Resolve text-anchor="middle|end" to a computed left edge with
     text-anchor="start" (Illustrator ignores text-anchor on import).
  3. Flatten nested <svg x y viewBox> into <g transform="translate() scale()">
     (nested viewports arrive as clip-mask nests at best).
  4. Inline <image> elements whose payload is an SVG data URI as real vector
     groups (Illustrator fails on them outright; Affinity V1 dropped them).
  5. Duplicate bare href= to xlink:href= on every <image> that lacks it
     (more reliable in Illustrator).
  6. Reduce font-family fallback stacks to their first family (neither
     editor walks a comma stack) and convert px font sizes to user units
     (Affinity has a px-as-pt import bug; the px-to-user-unit ratio is
     derived from the root width/viewBox, so mm-viewport documents convert
     correctly).
  7. Warn on constructs that cannot be fixed mechanically: <style> blocks,
     @font-face rules, dominant-baseline, filters, foreignObject, textPath,
     the font CSS shorthand.

The input file is left untouched; output defaults to <stem>-editable.svg.
Idempotent: running the output through again is a no-op.

Run:
    uv run --with lxml --with svgpathtools --with fonttools \
        python editor_prep.py figure.svg
    ... editor_prep.py figure.svg -o handoff.svg --font "Lato=/path/Lato.ttf"
    ... editor_prep.py figure.svg --check   # report only; exit 1 if anything
                                            # would change OR any warning fired

Text measurement (transform 2) needs the real font file. Resolution order:
--font FAMILY=PATH mappings, matplotlib's font manager if importable,
fc-match if on PATH. Unmeasurable text keeps its anchor, with a warning
that distinguishes "no font file found" from "font file failed to load".
"""

from __future__ import annotations

import argparse
import base64
import copy
import math
import re
import shutil
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
SVG = f"{{{SVG_NS}}}"
XLINK_HREF = f"{{{XLINK_NS}}}href"

_num = r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"

_UNIT_TO_PX = {"": 1.0, "px": 1.0, "pt": 96 / 72, "pc": 16.0,
               "mm": 96 / 25.4, "cm": 96 / 2.54, "in": 96.0}


@dataclass
class Report:
    """What the prep pass changed, skipped, and could not fix."""

    markers_baked: int = 0
    markers_skipped: int = 0
    anchors_resolved: int = 0
    anchors_skipped: int = 0
    nested_svgs_flattened: int = 0
    nested_svgs_skipped: int = 0
    datauris_inlined: int = 0
    datauris_skipped: int = 0
    hrefs_duplicated: int = 0
    font_stacks_reduced: int = 0
    font_sizes_converted: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def changes(self) -> int:
        return (self.markers_baked + self.anchors_resolved
                + self.nested_svgs_flattened + self.datauris_inlined
                + self.hrefs_duplicated + self.font_stacks_reduced
                + self.font_sizes_converted)

    @property
    def skipped(self) -> int:
        return (self.markers_skipped + self.anchors_skipped
                + self.nested_svgs_skipped + self.datauris_skipped)

    def warn(self, msg: str) -> None:
        if msg not in self.warnings:
            self.warnings.append(msg)

    def summary(self) -> str:
        lines = [
            f"markers baked into paths:        {self.markers_baked}",
            f"text anchors resolved to start:  {self.anchors_resolved}",
            f"nested <svg> flattened to <g>:   {self.nested_svgs_flattened}",
            f"SVG data URIs inlined as groups: {self.datauris_inlined}",
            f"xlink:href added to images:      {self.hrefs_duplicated}",
            f"font stacks reduced to first:    {self.font_stacks_reduced}",
            f"px font sizes converted:         {self.font_sizes_converted}",
        ]
        skips = [(n, c) for n, c in (
            ("markers", self.markers_skipped),
            ("text anchors", self.anchors_skipped),
            ("nested <svg>", self.nested_svgs_skipped),
            ("SVG data URIs", self.datauris_skipped)) if c]
        if skips:
            lines.append("left in place: "
                         + ", ".join(f"{c} {n}" for n, c in skips))
        if self.warnings:
            lines.append("warnings:")
            lines += [f"  - {w}" for w in self.warnings]
        return "\n".join(lines)


# --- property lookup (presentation attributes + minimal style="", inherited) --

def _style_dict(el) -> dict:
    out = {}
    for part in (el.get("style") or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def _get_prop(el, name: str, inherited: bool = True):
    node = el
    while node is not None and isinstance(node.tag, str):
        v = node.get(name) or _style_dict(node).get(name)
        if v is not None:
            return v
        if not inherited:
            return None
        node = node.getparent()
    return None


def _first_family(value: str) -> str:
    return value.split(",")[0].strip().strip("'\"")


def _ident(el) -> str:
    """Short element identifier for warning messages."""
    tag = etree.QName(el).localname if isinstance(el.tag, str) else "?"
    eid = el.get("id")
    return f"<{tag} id={eid!r}>" if eid else f"<{tag}>"


# --- length / unit parsing ----------------------------------------------------

def _strip_unit(value):
    """Parse a unitless-or-px length. None when absent OR unparseable."""
    m = re.match(rf"^({_num})\s*(px)?$", (value or "").strip())
    return float(m.group(1)) if m else None


def _length_attr(el, attr, report: Report, default=0.0):
    """Attribute as a float. Absent -> default; unparseable -> None + warn
    (percentages and non-px units cannot be resolved without layout)."""
    raw = el.get(attr)
    if raw is None:
        return default
    v = _strip_unit(raw)
    if v is None:
        report.warn(f"unsupported {attr}={raw!r} on {_ident(el)}; "
                    "only unitless or px lengths are handled")
    return v


def _unit_scale(root) -> float:
    """User units per CSS px, from the root width/viewBox ratio.

    A document with width="100mm" viewBox="0 0 100 100" has 1 user unit
    = 1 mm, so 1 px = 25.4/96 mm = 0.2646 user units. Unitless or px
    root widths give 1.0, as does anything unparseable.
    """
    m = re.match(rf"^({_num})\s*([a-z]*)$", (root.get("width") or "").strip())
    vb = _parse_viewbox(root.get("viewBox"))
    if not m or not vb or m.group(2) not in _UNIT_TO_PX:
        return 1.0
    width_px = float(m.group(1)) * _UNIT_TO_PX[m.group(2)]
    return vb[2] / width_px if width_px else 1.0


def _parse_size(value: str, uupx: float = 1.0):
    """A font-size or letter-spacing value in user units, or None.

    Unitless values are already user units; px/pt/mm are absolute CSS
    lengths converted through `uupx` (user units per px, from
    `_unit_scale`), so mm-viewport documents measure correctly.
    """
    if value.strip() == "normal":
        return 0.0
    m = re.match(rf"^({_num})\s*(px|pt|mm)?$", value.strip())
    if not m:
        return None
    size = float(m.group(1))
    unit = m.group(2)
    if unit:
        size *= _UNIT_TO_PX[unit] * uupx
    return size


# --- font measurement --------------------------------------------------------

class FontMeasurer:
    """Measure text advance width in user units via fontTools.

    Family -> file resolution: explicit mapping, then matplotlib font
    manager, then fc-match. Results (including failures, with the reason)
    are cached; `reason(family, bold)` says why a family is unmeasurable.
    """

    def __init__(self, font_map: dict | None = None):
        self.font_map = {k.lower(): v for k, v in (font_map or {}).items()}
        self._fonts: dict = {}
        self._reasons: dict = {}

    def _resolve_path(self, family: str, bold: bool):
        if family.lower() in self.font_map:
            return self.font_map[family.lower()]
        try:
            from matplotlib import font_manager
            prop = font_manager.FontProperties(
                family=family, weight="bold" if bold else "normal")
            return font_manager.findfont(prop, fallback_to_default=False)
        except ImportError:
            pass
        except Exception as exc:
            self._reasons[(family.lower(), bold)] = (
                f"matplotlib font lookup failed: {exc}")
        if shutil.which("fc-match"):
            query = f"{family}:weight=bold" if bold else family
            try:
                out = subprocess.run(
                    ["fc-match", "--format", "%{file}\t%{family}", query],
                    capture_output=True, text=True, timeout=10, check=True,
                ).stdout
                path, matched = (out.split("\t") + [""])[:2]
                # fc-match always answers; only trust an actual family match.
                if family.lower() in matched.lower():
                    return path
            except (subprocess.SubprocessError, OSError) as exc:
                self._reasons[(family.lower(), bold)] = f"fc-match failed: {exc}"
        return None

    def _font(self, family: str, bold: bool):
        key = (family.lower(), bold)
        if key not in self._fonts:
            path = self._resolve_path(family, bold)
            font = None
            if path is None:
                self._reasons.setdefault(
                    key, f"no font file found for family {family!r} "
                         f"(pass --font '{family}=/path/to/font.ttf')")
            else:
                try:
                    from fontTools.ttLib import TTFont, TTLibError
                    try:
                        font = TTFont(path, lazy=True)
                    except TTLibError:
                        font = TTFont(path, lazy=True, fontNumber=0)
                except Exception as exc:
                    self._reasons[key] = (
                        f"font file {path} for family {family!r} "
                        f"failed to load: {exc}")
            self._fonts[key] = font
        return self._fonts[key]

    def reason(self, family: str, bold: bool) -> str:
        return self._reasons.get(
            (family.lower(), bold), f"family {family!r} is unmeasurable")

    def width(self, text: str, family: str, size: float, bold: bool,
              letter_spacing: float = 0.0):
        """Advance width in the same units as `size`, or None if unmeasurable."""
        font = self._font(family, bold)
        if font is None or not text:
            return None if font is None else 0.0
        key = (family.lower(), bold)
        try:
            cmap = font.getBestCmap()
            hmtx = font["hmtx"]
            upem = font["head"].unitsPerEm
        except Exception as exc:
            self._reasons[key] = (
                f"font for family {family!r} lacks usable metrics: {exc}")
            return None
        total = 0
        for ch in text:
            gname = cmap.get(ord(ch))
            if gname is None:
                gname = cmap.get(ord(" "))
                if gname is None:
                    self._reasons[key] = (
                        f"font for family {family!r} has no glyph or "
                        f"space fallback for {ch!r}")
                    return None
            total += hmtx[gname][0]
        w = total * size / upem
        if letter_spacing:
            w += letter_spacing * max(len(text) - 1, 0)
        return w


# --- transform 1: bake markers ----------------------------------------------

def _endpoint_tangent(el, report: Report):
    """(end_point, unit_tangent) as complex numbers, or None."""
    tag = etree.QName(el).localname
    try:
        if tag == "path":
            from svgpathtools import parse_path
            p = parse_path(el.get("d", ""))
            if not len(p):
                return None
            end = p.point(1)
            try:
                tan = p.unit_tangent(1)
            except Exception:
                delta = p.point(1) - p.point(1 - 1e-4)
                tan = delta / abs(delta) if abs(delta) else None
            return (end, tan) if tan else None
        if tag == "line":
            p1 = complex(float(el.get("x1", 0)), float(el.get("y1", 0)))
            p2 = complex(float(el.get("x2", 0)), float(el.get("y2", 0)))
            if p1 == p2:
                return None
            return p2, (p2 - p1) / abs(p2 - p1)
        if tag in ("polyline", "polygon"):
            nums = [float(v) for v in re.findall(_num, el.get("points", ""))]
            if len(nums) < 4:
                return None
            p1 = complex(nums[-4], nums[-3])
            p2 = complex(nums[-2], nums[-1])
            if p1 == p2:
                return None
            return p2, (p2 - p1) / abs(p2 - p1)
    except Exception as exc:
        report.warn(f"could not compute endpoint tangent on <{tag}>: {exc}")
    return None


def _marker_numbers(marker, el, report: Report):
    """(stroke_scale, refx, refy, content_scale_x, content_scale_y) for a
    marker instance, or None when a value cannot be parsed.

    Applies the marker viewport mapping: with a viewBox, content coordinates
    are scaled into the markerWidth x markerHeight box (default 3 x 3 per
    the SVG spec) and refX/refY — which live in content coordinates — are
    scaled the same way, so the alignment offsets cancel out of the final
    translate.
    """
    values = {}
    for name, default in (("refX", 0.0), ("refY", 0.0),
                          ("markerWidth", 3.0), ("markerHeight", 3.0)):
        raw = marker.get(name)
        v = default if raw is None else _strip_unit(raw)
        if v is None:
            report.warn(f"marker {_ident(marker)} left in place: "
                        f"unparseable {name}={raw!r}")
            return None
        values[name] = v
    stroke_scale = 1.0
    if marker.get("markerUnits", "strokeWidth") == "strokeWidth":
        sw_raw = _get_prop(el, "stroke-width")
        stroke_scale = 1.0 if sw_raw is None else _strip_unit(sw_raw)
        if stroke_scale is None:
            report.warn(f"marker on {_ident(el)} left in place: "
                        f"unparseable stroke-width={sw_raw!r}")
            return None
    mvb = _parse_viewbox(marker.get("viewBox"))
    if mvb:
        _, _, csx, csy = _viewport_transform(
            0.0, 0.0, values["markerWidth"], values["markerHeight"],
            mvb, marker.get("preserveAspectRatio"))
    else:
        csx = csy = 1.0
    return stroke_scale, values["refX"], values["refY"], csx, csy


def bake_markers(root, report: Report) -> None:
    markers = {m.get("id"): m for m in root.iter(SVG + "marker") if m.get("id")}
    for el in list(root.iter()):
        if not isinstance(el.tag, str):
            continue
        for attr in ("marker-mid", "marker-start"):
            if el.get(attr):
                report.warn(f"{attr} on {_ident(el)} is not baked (only "
                            "marker-end is); the reference recommends "
                            "explicit geometry")
        ref = el.get("marker-end") or ""
        m = re.match(r"url\(#(.+?)\)", ref)
        if not m:
            continue
        marker = markers.get(m.group(1))
        if marker is None:
            report.warn(f"marker-end on {_ident(el)} references missing "
                        f"id {m.group(1)!r}")
            report.markers_skipped += 1
            continue
        et = _endpoint_tangent(el, report)
        if et is None:
            report.warn(f"marker-end on {_ident(el)} left in place: "
                        "endpoint tangent unavailable")
            report.markers_skipped += 1
            continue
        end, tan = et
        orient = (marker.get("orient") or "0").strip()
        if orient in ("auto", "auto-start-reverse"):
            # auto-start-reverse only reverses marker-start; for marker-end
            # it behaves exactly like auto.
            angle = math.degrees(math.atan2(tan.imag, tan.real))
        else:
            angle = _strip_unit(orient)
            if angle is None:
                report.warn(f"marker {_ident(marker)} left in place: "
                            f"unparseable orient={orient!r}")
                report.markers_skipped += 1
                continue
        nums = _marker_numbers(marker, el, report)
        if nums is None:
            report.markers_skipped += 1
            continue
        stroke_scale, ref_x, ref_y, csx, csy = nums
        g = etree.SubElement(el.getparent(), SVG + "g")
        parts = [f"translate({end.real:.4f} {end.imag:.4f})"]
        if abs(angle) > 1e-9:
            parts.append(f"rotate({angle:.3f})")
        if abs(stroke_scale - 1) > 1e-9:
            parts.append(f"scale({stroke_scale:.4f})")
        if abs(ref_x * csx) > 1e-9 or abs(ref_y * csy) > 1e-9:
            parts.append(f"translate({-ref_x * csx:.4f} {-ref_y * csy:.4f})")
        if abs(csx - 1) > 1e-9 or abs(csy - 1) > 1e-9:
            parts.append(f"scale({csx:.6f})" if abs(csx - csy) < 1e-9
                         else f"scale({csx:.6f} {csy:.6f})")
        g.set("transform", " ".join(parts))
        fill = _get_prop(el, "stroke") or "#000000"
        for child in marker:
            baked = copy.deepcopy(child)
            if baked.get("fill") in (None, "context-stroke"):
                baked.set("fill", fill)
            g.append(baked)
        # marker content paints after the path, so the group goes right
        # after the element it decorates.
        el.addnext(g)
        del el.attrib["marker-end"]
        report.markers_baked += 1
    body_text = None
    for marker_id, marker in markers.items():
        if body_text is None:
            body_text = etree.tostring(root, encoding="unicode")
        if f"url(#{marker_id})" not in body_text:
            marker.getparent().remove(marker)
            body_text = None


# --- transform 2: resolve text anchors ---------------------------------------

def resolve_text_anchors(root, measurer: FontMeasurer, report: Report,
                         uupx: float = 1.0) -> None:
    for el in root.iter(SVG + "text"):
        anchor = _get_prop(el, "text-anchor")
        if anchor not in ("middle", "end"):
            continue
        blockers = [c for c in el.iter()
                    if c is not el and isinstance(c.tag, str)
                    and (c.get("x") or c.get("y")
                         or etree.QName(c).localname == "textPath")]
        if blockers or el.get("textLength") or el.get("rotate"):
            report.warn(f"text anchor on {_ident(el)} left in place: "
                        "positioned tspans, textLength, rotate, or "
                        "textPath present")
            report.anchors_skipped += 1
            continue
        mixed = [prop for prop in ("font-size", "font-family", "font-weight")
                 if len({_get_prop(c, prop) for c in el.iter()
                         if isinstance(c.tag, str)}) > 1]
        if mixed:
            report.warn(f"text anchor on {_ident(el)} left in place: mixed "
                        f"{'/'.join(mixed)} inside one <text>")
            report.anchors_skipped += 1
            continue
        content = "".join(el.itertext())
        family = _first_family(_get_prop(el, "font-family") or "sans-serif")
        size_raw = _get_prop(el, "font-size") or "16"
        size = _parse_size(size_raw, uupx)
        if size is None:
            report.warn(f"text anchor on {_ident(el)} left in place: "
                        f"unparseable font-size {size_raw!r}")
            report.anchors_skipped += 1
            continue
        weight = (_get_prop(el, "font-weight") or "normal").strip()
        bold = weight in ("bold", "bolder") or (
            weight.isdigit() and int(weight) >= 600)
        ls = 0.0
        ls_raw = _get_prop(el, "letter-spacing")
        if ls_raw is not None:
            ls = _parse_size(ls_raw, uupx)
            if ls is None:
                report.warn(f"text anchor on {_ident(el)} left in place: "
                            f"unsupported letter-spacing {ls_raw!r}")
                report.anchors_skipped += 1
                continue
        x = _strip_unit(el.get("x") or "0")
        if x is None:
            report.warn(f"text anchor on {_ident(el)} left in place: "
                        f"unsupported x={el.get('x')!r}")
            report.anchors_skipped += 1
            continue
        width = measurer.width(content, family, size, bold, ls)
        if width is None:
            report.warn(f"text anchor on {_ident(el)} left in place: "
                        + measurer.reason(family, bold))
            report.anchors_skipped += 1
            continue
        el.set("x", f"{x - (width / 2 if anchor == 'middle' else width):.4f}")
        # An explicit start overrides any anchor inherited from an ancestor.
        el.set("text-anchor", "start")
        style = _style_dict(el)
        if "text-anchor" in style:
            style.pop("text-anchor")
            el.set("style", ";".join(f"{k}:{v}" for k, v in style.items()))
        report.anchors_resolved += 1


# --- transforms 3+4: flatten nested viewports --------------------------------

def _viewport_transform(x, y, w, h, viewbox, par: str):
    """SVG viewport-establishing transform as (tx, ty, sx, sy).

    Implements the full preserveAspectRatio grammar: the xMin/xMid/xMax and
    YMin/YMid/YMax alignment offsets and the meet (fit, default) vs slice
    (cover) scale choice.
    """
    if not viewbox:
        return x, y, 1.0, 1.0
    minx, miny, vbw, vbh = viewbox
    sx = w / vbw if vbw else 1.0
    sy = h / vbh if vbh else 1.0
    tokens = (par or "").split() or ["xMidYMid"]
    align = tokens[0] or "xMidYMid"
    if align == "none":
        return x - minx * sx, y - miny * sy, sx, sy
    s = max(sx, sy) if len(tokens) > 1 and tokens[1] == "slice" else min(sx, sy)
    xa, ya = align[:4], align[4:]
    ox = (w - vbw * s) / 2 if xa == "xMid" else (w - vbw * s) if xa == "xMax" else 0.0
    oy = (h - vbh * s) / 2 if ya == "YMid" else (h - vbh * s) if ya == "YMax" else 0.0
    return x - minx * s + ox, y - miny * s + oy, s, s


def _parse_viewbox(value):
    nums = [float(v) for v in re.findall(_num, value or "")]
    return nums if len(nums) == 4 else None


def _transform_group(x, y, w, h, viewbox, par):
    tx, ty, sx, sy = _viewport_transform(x, y, w, h, viewbox, par)
    g = etree.Element(SVG + "g")
    parts = []
    if abs(tx) > 1e-9 or abs(ty) > 1e-9:
        parts.append(f"translate({tx:.4f} {ty:.4f})")
    if abs(sx - 1) > 1e-9 or abs(sy - 1) > 1e-9:
        parts.append(f"scale({sx:.6f})" if abs(sx - sy) < 1e-9
                     else f"scale({sx:.6f} {sy:.6f})")
    if parts:
        g.set("transform", " ".join(parts))
    return g


def flatten_nested_svg(root, report: Report) -> None:
    # Snapshot in document order: children of a replaced viewport stay
    # live in the tree, and no new nested <svg> can appear mid-pass.
    for el in [el for el in root.iter(SVG + "svg") if el is not root]:
        viewbox = _parse_viewbox(el.get("viewBox"))
        x = _length_attr(el, "x", report)
        y = _length_attr(el, "y", report)
        w = _strip_unit(el.get("width")) if el.get("width") else None
        h = _strip_unit(el.get("height")) if el.get("height") else None
        if x is None or y is None or (el.get("width") and w is None) \
                or (el.get("height") and h is None):
            report.warn(f"nested {_ident(el)} left in place: "
                        "x/y/width/height uses unsupported units")
            report.nested_svgs_skipped += 1
            continue
        if w is None or h is None:
            if viewbox:
                w = w if w is not None else viewbox[2]
                h = h if h is not None else viewbox[3]
            else:
                report.warn(f"nested {_ident(el)} left in place: no "
                            "width/height or viewBox to derive the "
                            "transform from")
                report.nested_svgs_skipped += 1
                continue
        g = _transform_group(x, y, w, h, viewbox,
                             el.get("preserveAspectRatio"))
        if el.get("id"):
            g.set("id", el.get("id"))
        if (el.get("overflow") or "hidden") != "visible":
            report.warn("nested <svg> flattened without a clip; content that "
                        "overflowed its viewport is no longer clipped")
        for child in list(el):
            g.append(child)
        el.getparent().replace(el, g)
        report.nested_svgs_flattened += 1


_DATAURI_SVG = re.compile(r"^data:image/svg\+xml(;charset=[^;,]+)?(;base64)?,",
                          re.IGNORECASE)


def _namespace_ids(el, uid: str) -> None:
    for node in el.iter():
        if not isinstance(node.tag, str):
            continue
        if node.get("id"):
            node.set("id", f"{uid}-{node.get('id')}")
        for attr in ("href", XLINK_HREF):
            v = node.get(attr)
            if v and v.startswith("#"):
                node.set(attr, f"#{uid}-{v[1:]}")
        for attr, v in node.attrib.items():
            if "url(#" in v:
                node.set(attr, re.sub(r"url\(#([^)]+)\)",
                                      rf"url(#{uid}-\1)", v))


def inline_svg_datauris(root, report: Report) -> None:
    count = 0
    for el in list(root.iter(SVG + "image")):
        href = el.get(XLINK_HREF) or el.get("href") or ""
        m = _DATAURI_SVG.match(href)
        if not m:
            continue
        payload = href[m.end():]
        try:
            raw = (base64.b64decode(payload) if m.group(2)
                   else urllib.parse.unquote(payload).encode())
            inner = etree.fromstring(raw)
        except Exception as exc:
            report.warn(f"SVG data URI on {_ident(el)} left in place: "
                        f"payload did not parse ({exc})")
            report.datauris_skipped += 1
            continue
        viewbox = _parse_viewbox(inner.get("viewBox"))
        iw = _strip_unit(inner.get("width"))
        ih = _strip_unit(inner.get("height"))
        if viewbox is None and iw and ih:
            viewbox = [0.0, 0.0, iw, ih]
        x = _length_attr(el, "x", report)
        y = _length_attr(el, "y", report)
        w = _strip_unit(el.get("width")) if el.get("width") else None
        h = _strip_unit(el.get("height")) if el.get("height") else None
        if x is None or y is None or w is None or h is None or viewbox is None:
            report.warn(f"SVG data URI on {_ident(el)} left in place: "
                        "image or payload lacks parseable dimensions")
            report.datauris_skipped += 1
            continue
        count += 1
        uid = f"emb{count}"
        _namespace_ids(inner, uid)
        g = _transform_group(x, y, w, h, viewbox,
                             el.get("preserveAspectRatio"))
        g.set("id", el.get("id") or uid)
        for child in list(inner):
            g.append(child)
        el.getparent().replace(el, g)
        report.datauris_inlined += 1


# --- transforms 5+6: hrefs and fonts -----------------------------------------

def duplicate_image_hrefs(root, report: Report) -> None:
    """Any <image> keeping a bare href gets an xlink:href duplicate."""
    for el in root.iter(SVG + "image"):
        href = el.get("href")
        if href and not el.get(XLINK_HREF):
            el.set(XLINK_HREF, href)
            report.hrefs_duplicated += 1


def normalize_fonts(root, report: Report, uupx: float = 1.0) -> None:
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        fam = el.get("font-family")
        if fam and "," in fam:
            el.set("font-family", _first_family(fam))
            report.font_stacks_reduced += 1
        size = el.get("font-size")
        if size and size.strip().endswith("px"):
            parsed = _parse_size(size, uupx)
            if parsed is not None:
                el.set("font-size", f"{parsed:g}")
                report.font_sizes_converted += 1


def collect_warnings(root, report: Report) -> None:
    checks = {
        "style": "a <style> block is present; editors bake or mishandle CSS "
                 "(move rules to presentation attributes)",
        "foreignObject": "<foreignObject> is not rendered by either editor",
        "textPath": "<textPath> does not import into Illustrator",
        "filter": "SVG <filter> effects are unreliable in both editors",
    }
    for tag, msg in checks.items():
        if root.find(f".//{SVG}{tag}") is not None:
            report.warn(msg)
    for style_el in root.iter(SVG + "style"):
        if "@font-face" in (style_el.text or ""):
            report.warn("@font-face rules are ignored by both editors; "
                        "ship the font files with the master instead")
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        if el.get("dominant-baseline") or "dominant-baseline" in _style_dict(el):
            report.warn("dominant-baseline is present; Illustrator ignores "
                        "'middle' (position by computed baseline y instead)")
        if "font:" in (el.get("style") or ""):
            report.warn("the 'font' CSS shorthand is ignored by Affinity; "
                        "use font-family + font-size")


# --- driver -------------------------------------------------------------------

def prep_tree(root, font_map: dict | None = None,
              resolve_anchors: bool = True) -> Report:
    report = Report()
    uupx = _unit_scale(root)
    bake_markers(root, report)
    inline_svg_datauris(root, report)
    flatten_nested_svg(root, report)
    if resolve_anchors:
        resolve_text_anchors(root, FontMeasurer(font_map), report, uupx)
    duplicate_image_hrefs(root, report)
    normalize_fonts(root, report, uupx)
    collect_warnings(root, report)
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Rewrite an SVG for editable handoff to Illustrator / "
                    "Affinity Designer (see references/editor-handoff.md).")
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path,
                    help="output path (default: <stem>-editable.svg)")
    ap.add_argument("--in-place", action="store_true",
                    help="overwrite the input file")
    ap.add_argument("--font", action="append", default=[],
                    metavar="FAMILY=PATH",
                    help="font file for text measurement (repeatable)")
    ap.add_argument("--keep-anchors", action="store_true",
                    help="skip text-anchor resolution")
    ap.add_argument("--check", action="store_true",
                    help="report without writing; exit 1 if anything would "
                         "change or any warning fired")
    args = ap.parse_args(argv)

    font_map = {}
    for item in args.font:
        if "=" not in item:
            ap.error(f"--font expects FAMILY=PATH, got {item!r}")
        family, path = item.split("=", 1)
        font_map[family] = path

    try:
        tree = etree.parse(str(args.input))
    except OSError as exc:
        ap.error(f"cannot read {args.input}: {exc}")
    except etree.XMLSyntaxError as exc:
        ap.error(f"{args.input} is not well-formed XML: {exc}")
    report = prep_tree(tree.getroot(), font_map,
                       resolve_anchors=not args.keep_anchors)
    print(report.summary())
    if args.check:
        return 1 if (report.changes or report.warnings) else 0
    out = args.input if args.in_place else (
        args.output or args.input.with_name(args.input.stem + "-editable.svg"))
    tree.write(str(out), xml_declaration=True, encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
