"""Shared theme-bible helpers for the figures plugin.

A `theme.json` is the single source of truth for a project's figure style:
palette, typography, composition, and image-model preferences. This module is
imported by `figure-bible`'s scripts (`init_theme.py`, `validate_theme.py`)
and, via a `sys.path` shim, by the figure-qa scripts (`check_svg.py`,
`check_raster.py`) so all three read the same palette and journal data.

No third-party imports at module scope: `jsonschema` is optional and only
loaded inside `validate_theme()` so callers without it fall back to a
hand-written structural check.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "theme.schema.json"

# Per-venue page widths (millimetres) and minimum body-text size (points).
# Journal figures: single_col_mm is the one-column width, double_col_mm the
# full-page width. Poster and slide use the same two keys for a uniform
# lookup even though "columns" is not a meaningful concept for either: poster
# uses the standard 36x48 in printed poster (short/long edge), slide uses a
# 16:9 deck (height/width).
JOURNAL_PROFILES: dict[str, dict[str, float]] = {
    "nature": {"single_col_mm": 89.0, "double_col_mm": 183.0, "min_pt": 5.0},
    "science": {"single_col_mm": 55.0, "double_col_mm": 120.0, "min_pt": 5.0},
    "cell": {"single_col_mm": 85.0, "double_col_mm": 174.0, "min_pt": 5.0},
    "pnas": {"single_col_mm": 87.0, "double_col_mm": 180.0, "min_pt": 5.0},
    "poster": {"single_col_mm": 914.4, "double_col_mm": 1219.2, "min_pt": 18.0},
    "slide": {"single_col_mm": 190.5, "double_col_mm": 338.67, "min_pt": 18.0},
}

# Curated colorblind-safe palette presets, shared by the theme bible and the
# figure-qa palette compliance checks.
PALETTE_PRESETS: dict[str, list[str]] = {
    "okabe-ito": [
        "#000000",
        "#E69F00",
        "#56B4E9",
        "#009E73",
        "#F0E442",
        "#0072B2",
        "#D55E00",
        "#CC79A7",
    ],
    "tol-bright": [
        "#4477AA",
        "#EE6677",
        "#228833",
        "#CCBB44",
        "#66CCEE",
        "#AA3377",
        "#BBBBBB",
    ],
    "neuro-flat": [
        "#1F3A5F",
        "#E07A5F",
        "#F4F1DE",
        "#C45146",
        "#2A6F3D",
        "#7E57C2",
    ],
}
# Wong 2011 republished the Okabe-Ito 2008 palette unchanged; keep both names
# pointing at the same list so users see the canonical citation either way.
PALETTE_PRESETS["wong"] = PALETTE_PRESETS["okabe-ito"]

_PALETTE_ROLE_ORDER = ("primary", "accent", "neutral", "background")
_PALETTE_ARRAY_KEYS = ("categorical", "sequential", "diverging")

_HEX_RE = re.compile(
    r"^#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})$"
)


def _is_hex(value: Any) -> bool:
    return isinstance(value, str) and bool(_HEX_RE.match(value))


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    """Convert a 3/4/6/8-digit CSS hex color to an (R, G, B) triple."""
    s = value.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    elif len(s) == 4:
        s = "".join(c * 2 for c in s[:3])
    elif len(s) == 8:
        s = s[:6]
    if len(s) != 6:
        raise ValueError(f"unexpected hex length after normalization: '#{s}'")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG relative luminance for an (R, G, B) triple in 0-255."""

    def channel(c: int) -> float:
        c_norm = c / 255.0
        return (
            c_norm / 12.92 if c_norm <= 0.03928 else ((c_norm + 0.055) / 1.055) ** 2.4
        )

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """WCAG contrast ratio between two hex colors (1.0 = identical, 21.0 = max)."""
    l1 = _relative_luminance(hex_to_rgb(hex_a))
    l2 = _relative_luminance(hex_to_rgb(hex_b))
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def load_theme(path: str | Path) -> dict[str, Any]:
    """Load and JSON-decode a theme file. Raises FileNotFoundError or
    json.JSONDecodeError on bad input; callers decide how to report those."""
    theme_path = Path(path)
    data = json.loads(theme_path.read_text())
    if not isinstance(data, dict):
        raise TypeError(f"{theme_path}: theme root must be a JSON object")
    return data


def _structural_check(theme: dict[str, Any]) -> list[str]:
    """Hand-written fallback used when `jsonschema` is not installed. Checks
    the required keys, hex validity, and the enums this plugin relies on."""
    problems: list[str] = []
    for key in ("theme_id", "palette", "style_tokens"):
        if key not in theme:
            problems.append(f"missing required key: {key}")

    theme_id = theme.get("theme_id")
    if isinstance(theme_id, str) and not re.match(r"^[a-z0-9][a-z0-9_-]*$", theme_id):
        problems.append(f"theme_id '{theme_id}' does not match ^[a-z0-9][a-z0-9_-]*$")

    palette = theme.get("palette")
    if palette is not None and not isinstance(palette, dict):
        problems.append("palette must be an object")
    elif isinstance(palette, dict):
        for role in _PALETTE_ROLE_ORDER:
            value = palette.get(role)
            if value is not None and value != "transparent" and not _is_hex(value):
                problems.append(f"palette.{role} '{value}' is not a valid hex color")
        for arr_key in _PALETTE_ARRAY_KEYS:
            values = palette.get(arr_key)
            if values is None:
                continue
            if not isinstance(values, list):
                problems.append(f"palette.{arr_key} must be an array")
                continue
            for v in values:
                if not _is_hex(v):
                    problems.append(
                        f"palette.{arr_key} contains invalid hex color '{v}'"
                    )

    style_tokens = theme.get("style_tokens")
    if style_tokens is not None and not isinstance(style_tokens, list):
        problems.append("style_tokens must be an array")

    journal = theme.get("journal")
    if journal is not None and journal not in (
        "nature",
        "science",
        "cell",
        "pnas",
        "poster",
        "slide",
        "custom",
    ):
        problems.append(
            f"journal '{journal}' is not one of nature|science|cell|pnas|poster|slide|custom"
        )

    postprocess = theme.get("postprocess")
    if isinstance(postprocess, dict):
        bg_removal = postprocess.get("bg_removal")
        if bg_removal is not None and bg_removal not in (
            "auto",
            "pillow",
            "rembg",
            "none",
        ):
            problems.append(
                f"postprocess.bg_removal '{bg_removal}' is not one of auto|pillow|rembg|none"
            )

    return problems


def validate_theme(theme: dict[str, Any]) -> list[str]:
    """Validate a theme dict against schemas/theme.schema.json. Returns a list
    of human-readable problem strings; an empty list means valid. Uses
    `jsonschema` when importable (run with `--with jsonschema`), otherwise
    falls back to `_structural_check`. Always appends a low-contrast warning
    when background/primary contrast is weak, regardless of which validator ran."""
    problems: list[str]
    try:
        import jsonschema  # type: ignore[import-not-found]
    except ImportError:
        problems = _structural_check(theme)
    else:
        schema = json.loads(SCHEMA_PATH.read_text())
        validator = jsonschema.Draft7Validator(schema)
        problems = [
            f"{'.'.join(str(p) for p in error.path) or '<root>'}: {error.message}"
            for error in sorted(
                validator.iter_errors(theme), key=lambda e: list(e.path)
            )
        ]

    palette = theme.get("palette")
    if isinstance(palette, dict):
        bg = palette.get("background") or palette.get("bg")
        primary = palette.get("primary")
        if _is_hex(bg) and _is_hex(primary):
            ratio = contrast_ratio(bg, primary)
            if ratio < 3.0:
                problems.append(
                    f"warning: low contrast between palette.background and palette.primary "
                    f"(ratio {ratio:.2f} < 3.0); labels may be hard to read"
                )

    return problems


def palette_hexes(theme: dict[str, Any]) -> list[str]:
    """All colors declared in a theme's palette, in role order: primary,
    accent, neutral, background, then categorical, sequential, diverging.
    Non-hex values (e.g. 'transparent') are skipped."""
    palette = theme.get("palette") or {}
    hexes: list[str] = []
    for role in _PALETTE_ROLE_ORDER:
        value = palette.get(role)
        if _is_hex(value):
            hexes.append(value)
    if not _is_hex(palette.get("background")) and _is_hex(palette.get("bg")):
        hexes.append(palette["bg"])  # legacy key from the pre-bible icon theme examples
    for arr_key in _PALETTE_ARRAY_KEYS:
        for value in palette.get(arr_key) or []:
            if _is_hex(value):
                hexes.append(value)
    return hexes


def theme_defaults(
    journal: str, preset: str = "okabe-ito", theme_id: str = "untitled"
) -> dict[str, Any]:
    """Build a complete, schema-valid theme dict for a journal profile and a
    palette preset. `init_theme.py` overrides fields (theme_id, colors, font,
    style/negative tokens, references, model preferences) from CLI args."""
    profile = JOURNAL_PROFILES.get(journal.lower())
    if profile is None:
        raise ValueError(
            f"unknown journal '{journal}'; known: {sorted(JOURNAL_PROFILES)}"
        )
    colors = PALETTE_PRESETS.get(preset.lower())
    if colors is None:
        raise ValueError(
            f"unknown palette preset '{preset}'; known: {sorted(PALETTE_PRESETS)}"
        )
    primary = colors[0]
    accent = colors[1] if len(colors) > 1 else colors[0]
    neutral = colors[2] if len(colors) > 2 else colors[0]

    return {
        "theme_id": theme_id,
        "journal": journal.lower(),
        "palette": {
            "primary": primary,
            "accent": accent,
            "neutral": neutral,
            "background": "#FFFFFF",
            "categorical": list(colors),
        },
        "typography": {
            "family": "Helvetica",
            "min_pt": profile["min_pt"],
            "panel_letter": {"weight": "bold", "case": "lower"},
        },
        "stroke": {"weight_px": 4, "linejoin": "round", "linecap": "round"},
        "style_tokens": ["flat vector", "minimal", "no shading"],
        "negative_tokens": ["gradient", "3D", "shadow", "watermark"],
        "composition": {
            "aspect": "4:3",
            "padding_pct": 8,
            "perspective": "orthographic",
        },
        "text": {
            "max_words_per_label": 4,
            "max_words_per_title": 8,
            "headline_size_class": "large",
        },
        "reference_images": [],
        "model_preferences": {
            "codex_model": "gpt-5.6-luna",
            "codex_effort": "xhigh",
            "image_quality": "high",
        },
        "postprocess": {"bg_removal": "auto"},
    }


def resolve_palette(spec: str) -> tuple[str, list[str]]:
    """Resolve a `--palette` argument to (name, hex list). `spec` is either a
    known preset name (case-insensitive) or a path to a theme.json, whose
    palette is flattened via `palette_hexes`. Raises ValueError when `spec` is
    neither, so the caller (check_svg.py / check_raster.py) can report a
    clear error instead of silently accepting an empty palette."""
    preset = PALETTE_PRESETS.get(spec.lower())
    if preset is not None:
        return spec.lower(), list(preset)
    theme_path = Path(spec)
    if theme_path.exists():
        theme = load_theme(theme_path)
        hexes = palette_hexes(theme)
        if not hexes:
            raise ValueError(
                f"{theme_path}: theme has no usable hex colors in its palette"
            )
        return str(theme.get("theme_id") or theme_path.stem), hexes
    raise ValueError(
        f"'{spec}' is neither a known palette preset ({sorted(PALETTE_PRESETS)}) "
        "nor an existing theme.json path"
    )
