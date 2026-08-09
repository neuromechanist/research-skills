"""Rewrite an SVG into the editor-safe dialect for Illustrator / Affinity handoff.

Applies the mechanical transforms from references/editor-handoff.md to ANY SVG
(svg-primitives output, matplotlib export, hand-authored, Inkscape save):

  1. Bake <marker> arrowheads into explicit geometry at the path endpoint
     (Illustrator has a filed bug rendering paths with markers).
  2. Resolve text-anchor="middle|end" to a computed left edge with
     text-anchor="start" (Illustrator ignores text-anchor on import).
  3. Flatten nested <svg x y viewBox> into <g transform="translate() scale()">
     (nested viewports arrive as clip-mask nests at best).
  4. Inline <image> elements whose payload is an SVG data URI as real vector
     groups (Illustrator fails on them outright; Affinity V1 dropped them).
  5. Duplicate bare href= to xlink:href= on raster images (more reliable in
     Illustrator) and reduce font-family fallback stacks to their first
     family (neither editor walks a comma stack).
  6. Warn on constructs that cannot be fixed mechanically: <style> blocks,
     dominant-baseline, filters, foreignObject, textPath, @font-face.

The input file is left untouched; output defaults to <stem>-editable.svg.
Idempotent: running the output through again is a no-op.

Run:
    uv run --with lxml --with svgpathtools --with fonttools \
        python editor_prep.py figure.svg
    ... editor_prep.py figure.svg -o handoff.svg --font "Lato=/path/Lato.ttf"
    ... editor_prep.py figure.svg --check   # report only, exit 1 if dirty

Text measurement (transform 2) needs the real font file. Resolution order:
--font FAMILY=PATH mappings, matplotlib's font manager if importable,
fc-match if on PATH. Unmeasurable text keeps its anchor, with a warning.
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


@dataclass
class Report:
    """What the prep pass changed and what it could not fix."""

    markers_baked: int = 0
    anchors_resolved: int = 0
    nested_svgs_flattened: int = 0
    datauris_inlined: int = 0
    hrefs_duplicated: int = 0
    font_stacks_reduced: int = 0
    font_sizes_unitless: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def changes(self) -> int:
        return (self.markers_baked + self.anchors_resolved
                + self.nested_svgs_flattened + self.datauris_inlined
                + self.hrefs_duplicated + self.font_stacks_reduced
                + self.font_sizes_unitless)

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
            f"font sizes made unitless:        {self.font_sizes_unitless}",
        ]
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


# --- font measurement --------------------------------------------------------

class FontMeasurer:
    """Measure text advance width in user units via fontTools.

    Family -> file resolution: explicit mapping, then matplotlib font
    manager, then fc-match. Results (including failures) are cached.
    """

    def __init__(self, font_map: dict | None = None):
        self.font_map = {k.lower(): v for k, v in (font_map or {}).items()}
        self._fonts: dict = {}

    def _resolve_path(self, family: str, bold: bool):
        if family.lower() in self.font_map:
            return self.font_map[family.lower()]
        try:
            from matplotlib import font_manager
            prop = font_manager.FontProperties(
                family=family, weight="bold" if bold else "normal")
            path = font_manager.findfont(prop, fallback_to_default=False)
            return path
        except Exception:
            pass
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
            except Exception:
                pass
        return None

    def _font(self, family: str, bold: bool):
        key = (family.lower(), bold)
        if key not in self._fonts:
            path = self._resolve_path(family, bold)
            font = None
            if path:
                try:
                    from fontTools.ttLib import TTFont, TTLibError
                    try:
                        font = TTFont(path, lazy=True)
                    except TTLibError:
                        font = TTFont(path, lazy=True, fontNumber=0)
                except Exception:
                    font = None
            self._fonts[key] = font
        return self._fonts[key]

    def width(self, text: str, family: str, size: float, bold: bool,
              letter_spacing: float = 0.0):
        """Advance width in the same units as `size`, or None if unmeasurable."""
        font = self._font(family, bold)
        if font is None or not text:
            return None if font is None else 0.0
        try:
            cmap = font.getBestCmap()
            hmtx = font["hmtx"]
            upem = font["head"].unitsPerEm
        except Exception:
            return None
        total = 0
        for ch in text:
            gname = cmap.get(ord(ch))
            if gname is None:
                gname = cmap.get(ord(" "))
                if gname is None:
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


def bake_markers(root, report: Report) -> None:
    markers = {m.get("id"): m for m in root.iter(SVG + "marker") if m.get("id")}
    for el in list(root.iter()):
        if not isinstance(el.tag, str):
            continue
        for attr in ("marker-mid", "marker-start"):
            if el.get(attr):
                report.warn(f"{attr} is not baked (only marker-end is); "
                            "the reference recommends explicit geometry")
        ref = el.get("marker-end") or ""
        m = re.match(r"url\(#(.+?)\)", ref)
        if not m:
            continue
        marker = markers.get(m.group(1))
        if marker is None:
            report.warn(f"marker-end references missing id {m.group(1)!r}")
            continue
        et = _endpoint_tangent(el, report)
        if et is None:
            report.warn("marker-end left in place: endpoint tangent "
                        f"unavailable on <{etree.QName(el).localname}>")
            continue
        end, tan = et
        angle = math.degrees(math.atan2(tan.imag, tan.real))
        scale = 1.0
        if marker.get("markerUnits", "strokeWidth") == "strokeWidth":
            scale = float(_get_prop(el, "stroke-width") or 1)
        ref_x = float(marker.get("refX", 0))
        ref_y = float(marker.get("refY", 0))
        g = etree.SubElement(el.getparent(), SVG + "g")
        parts = [f"translate({end.real:.4f} {end.imag:.4f})",
                 f"rotate({angle:.3f})"]
        if scale != 1.0:
            parts.append(f"scale({scale:.4f})")
        if ref_x or ref_y:
            parts.append(f"translate({-ref_x:.4f} {-ref_y:.4f})")
        g.set("transform", " ".join(parts))
        fill = _get_prop(el, "stroke", inherited=False) or "#000000"
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

def _parse_size(value: str, report: Report):
    m = re.match(rf"^({_num})\s*(px|pt|mm)?$", value.strip())
    if not m:
        return None
    size = float(m.group(1))
    unit = m.group(2)
    if unit == "pt":
        size *= 4 / 3  # CSS: 1pt = 4/3 px == user units
    elif unit == "mm":
        size *= 96 / 25.4
    return size


def resolve_text_anchors(root, measurer: FontMeasurer, report: Report) -> None:
    for el in root.iter(SVG + "text"):
        anchor = _get_prop(el, "text-anchor")
        if anchor not in ("middle", "end"):
            continue
        blockers = [c for c in el.iter()
                    if c is not el and isinstance(c.tag, str)
                    and (c.get("x") or c.get("y")
                         or etree.QName(c).localname == "textPath")]
        if blockers or el.get("textLength") or el.get("rotate"):
            report.warn("text anchor left in place: positioned tspans, "
                        "textLength, rotate, or textPath present")
            continue
        sizes = {_get_prop(c, "font-size") for c in el.iter()
                 if isinstance(c.tag, str)}
        if len(sizes) > 1:
            report.warn("text anchor left in place: mixed font sizes "
                        "inside one <text>")
            continue
        content = "".join(el.itertext())
        family_raw = _get_prop(el, "font-family") or "sans-serif"
        family = _first_family(family_raw)
        size_raw = _get_prop(el, "font-size") or "16"
        size = _parse_size(size_raw, report)
        if size is None:
            report.warn(f"text anchor left in place: unparseable "
                        f"font-size {size_raw!r}")
            continue
        weight = (_get_prop(el, "font-weight") or "normal").strip()
        bold = weight in ("bold", "bolder") or (
            weight.isdigit() and int(weight) >= 600)
        ls_raw = _get_prop(el, "letter-spacing")
        ls = _parse_size(ls_raw, report) if ls_raw else 0.0
        width = measurer.width(content, family, size, bold, ls or 0.0)
        if width is None:
            report.warn(f"text anchor left in place: no font file found "
                        f"for family {family!r} (pass --font "
                        f"'{family}=/path/to/font.ttf')")
            continue
        x = float(el.get("x") or 0)
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
    """SVG viewport-establishing transform as (tx, ty, sx, sy)."""
    if not viewbox:
        return x, y, 1.0, 1.0
    minx, miny, vbw, vbh = viewbox
    sx = w / vbw if vbw else 1.0
    sy = h / vbh if vbh else 1.0
    align = (par or "xMidYMid meet").split()[0]
    if align != "none":
        s = min(sx, sy)
        tx = x - minx * s + (w - vbw * s) / 2 if align.startswith("xMid") else x - minx * s
        ty = y - miny * s + (h - vbh * s) / 2 if "YMid" in align else y - miny * s
        return tx, ty, s, s
    return x - minx * sx, y - miny * sy, sx, sy


def _parse_viewbox(value):
    nums = [float(v) for v in re.findall(_num, value or "")]
    return nums if len(nums) == 4 else None


def _transform_group(parent_tag_ns, x, y, w, h, viewbox, par):
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


def _strip_unit(value, report: Report):
    m = re.match(rf"^({_num})\s*(px)?$", (value or "").strip())
    return float(m.group(1)) if m else None


def flatten_nested_svg(root, report: Report) -> None:
    while True:
        nested = [el for el in root.iter(SVG + "svg") if el is not root]
        if not nested:
            return
        el = nested[0]
        viewbox = _parse_viewbox(el.get("viewBox"))
        x = _strip_unit(el.get("x"), report) or 0.0
        y = _strip_unit(el.get("y"), report) or 0.0
        w = _strip_unit(el.get("width"), report)
        h = _strip_unit(el.get("height"), report)
        if w is None or h is None:
            if viewbox:
                w = w if w is not None else viewbox[2]
                h = h if h is not None else viewbox[3]
            else:
                report.warn("nested <svg> left in place: no width/height "
                            "or viewBox to derive the transform from")
                return
        g = _transform_group(el.tag, x, y, w, h, viewbox,
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
            report.warn(f"SVG data URI left in place: payload did not "
                        f"parse ({exc})")
            continue
        viewbox = _parse_viewbox(inner.get("viewBox"))
        iw = _strip_unit(inner.get("width"), report)
        ih = _strip_unit(inner.get("height"), report)
        if viewbox is None and iw and ih:
            viewbox = [0.0, 0.0, iw, ih]
        x = _strip_unit(el.get("x"), report) or 0.0
        y = _strip_unit(el.get("y"), report) or 0.0
        w = _strip_unit(el.get("width"), report)
        h = _strip_unit(el.get("height"), report)
        if w is None or h is None or viewbox is None:
            report.warn("SVG data URI left in place: image or payload "
                        "lacks the dimensions to derive a transform")
            continue
        count += 1
        uid = f"emb{count}"
        _namespace_ids(inner, uid)
        g = _transform_group(el.tag, x, y, w, h, viewbox,
                             el.get("preserveAspectRatio"))
        g.set("id", el.get("id") or uid)
        for child in list(inner):
            g.append(child)
        el.getparent().replace(el, g)
        report.datauris_inlined += 1


# --- transform 5: hrefs and font families ------------------------------------

def duplicate_raster_hrefs(root, report: Report) -> None:
    for el in root.iter(SVG + "image"):
        href = el.get("href")
        if href and not el.get(XLINK_HREF):
            el.set(XLINK_HREF, href)
            report.hrefs_duplicated += 1


def normalize_fonts(root, report: Report) -> None:
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        fam = el.get("font-family")
        if fam and "," in fam:
            el.set("font-family", _first_family(fam))
            report.font_stacks_reduced += 1
        size = el.get("font-size")
        if size and size.strip().endswith("px"):
            parsed = _strip_unit(size, report)
            if parsed is not None:
                el.set("font-size", f"{parsed:g}")
                report.font_sizes_unitless += 1


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
    bake_markers(root, report)
    inline_svg_datauris(root, report)
    flatten_nested_svg(root, report)
    if resolve_anchors:
        resolve_text_anchors(root, FontMeasurer(font_map), report)
    duplicate_raster_hrefs(root, report)
    normalize_fonts(root, report)
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
                    help="report needed changes without writing; "
                         "exit 1 if any")
    args = ap.parse_args(argv)

    font_map = {}
    for item in args.font:
        if "=" not in item:
            ap.error(f"--font expects FAMILY=PATH, got {item!r}")
        family, path = item.split("=", 1)
        font_map[family] = path

    tree = etree.parse(str(args.input))
    report = prep_tree(tree.getroot(), font_map,
                       resolve_anchors=not args.keep_anchors)
    print(report.summary())
    if args.check:
        return 1 if report.changes else 0
    out = args.input if args.in_place else (
        args.output or args.input.with_name(args.input.stem + "-editable.svg"))
    tree.write(str(out), xml_declaration=True, encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
