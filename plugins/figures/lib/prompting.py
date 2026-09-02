"""Prompt construction for the Codex/OpenAI image_gen verbatim-text contract.

Builds the structured prompt blocks documented in Codex's built-in `imagegen`
skill (`~/.codex/skills/.system/imagegen/`): an instruction header telling the
model to use the built-in image_gen tool exactly once and save the result to
./output.png, followed by Use case / Asset type / Primary request / Subject /
Style-medium / Composition-layout / Text (verbatim) / Avoid / Background
sections.

Also implements the text ladder: AI-rendered text is fine for short titles,
panel letters, and labels, but numerals, units, equations, and axis ticks
must go through the SVG overlay or a plotting library instead, since
gpt-image-2 cannot render them reliably.

Themes are treated as plain dicts (loaded elsewhere with `json.loads`); every
lookup here uses `.get(...)` with a default so a partial or missing theme
never raises.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

VALID_ROLES = ("title", "panel-letter", "label", "caption")
VALID_SIZE_CLASSES = ("large", "medium", "small")

DEFAULT_MAX_WORDS_PER_LABEL = 4
DEFAULT_MAX_WORDS_PER_TITLE = 8


@dataclass
class TextItem:
    text: str
    role: str = "label"
    placement: str = "center"
    size_class: str | None = None
    style: str | None = None

    def __post_init__(self) -> None:
        if self.role not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}, got {self.role!r}")
        if self.size_class is not None and self.size_class not in VALID_SIZE_CLASSES:
            raise ValueError(
                f"size_class must be one of {VALID_SIZE_CLASSES}, got {self.size_class!r}"
            )


class TextLadderError(ValueError):
    """Raised when requested AI-rendered text violates the text ladder."""


_EQUALS_RE = re.compile(r"=")
_UNIT_WORD_RE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mm|cm|km|px|pt|hz|khz|mhz|ghz|ms|min|hr|kg|mg|"
    r"ml|mv|ma|ohm|db|deg|°|%)\b",
    re.IGNORECASE,
)
# Bare unit letters ("m", "s", "g", "l", "v", "a", "w") are ambiguous with
# ordinary words, so they only count when directly glued to the digit
# (no space), e.g. "3s" or "5V", not "3 A" (article) or "1 in" (word "in").
_GLUED_UNIT_RE = re.compile(r"\b\d+(?:\.\d+)?(?:m|s|g|l|v|a|w)\b", re.IGNORECASE)


def _word_count(text: str) -> int:
    return len(text.split())


def _looks_numeric(text: str) -> bool:
    return bool(
        _EQUALS_RE.search(text)
        or _UNIT_WORD_RE.search(text)
        or _GLUED_UNIT_RE.search(text)
    )


def enforce_text_ladder(text: list[TextItem], theme: dict | None) -> None:
    """Raise TextLadderError listing every item that violates the text ladder.

    Labels over `theme.text.max_words_per_label` words (default 4), titles
    over `theme.text.max_words_per_title` words (default 8), and any item
    that mixes digits with units or contains an equals sign (numerals,
    equations, axis ticks) must be rendered by the SVG overlay instead of the
    AI image model.
    """
    theme = theme or {}
    text_cfg = theme.get("text") or {}
    max_label_words = int(
        text_cfg.get("max_words_per_label", DEFAULT_MAX_WORDS_PER_LABEL)
    )
    max_title_words = int(
        text_cfg.get("max_words_per_title", DEFAULT_MAX_WORDS_PER_TITLE)
    )

    offenses: list[str] = []
    for item in text:
        words = _word_count(item.text)
        if item.role == "label" and words > max_label_words:
            offenses.append(
                f'"{item.text}" ({item.role}): {words} words exceeds the '
                f"{max_label_words}-word label limit"
            )
        if item.role == "title" and words > max_title_words:
            offenses.append(
                f'"{item.text}" ({item.role}): {words} words exceeds the '
                f"{max_title_words}-word title limit"
            )
        if _looks_numeric(item.text):
            offenses.append(
                f'"{item.text}" ({item.role}): looks like a numeral, unit, or equation'
            )

    if offenses:
        raise TextLadderError(
            "Text ladder violation(s); render these with the SVG overlay (or a "
            "plotting library, for axis ticks and equations) instead of "
            "AI-rendered text:\n- " + "\n- ".join(offenses)
        )


def theme_palette_lines(theme: dict | None) -> list[str]:
    """Render a theme's palette entries as 'role: #hex' strings for a prompt."""
    theme = theme or {}
    palette = theme.get("palette") or {}
    lines = []
    for key in ("primary", "accent", "neutral", "background"):
        value = palette.get(key)
        if value:
            lines.append(f"{key}: {value}")
    categorical = palette.get("categorical") or []
    if categorical:
        lines.append("categorical: " + ", ".join(categorical))
    return lines


def resolve_size_class(item: TextItem, theme: dict | None) -> str:
    """Explicit size class wins; otherwise titles and panel letters take the theme
    headline size (default large) and labels or captions are medium."""
    if item.size_class:
        return item.size_class
    if item.role in ("title", "panel-letter"):
        headline = ((theme or {}).get("text") or {}).get("headline_size_class")
        return headline if headline in VALID_SIZE_CLASSES else "large"
    return "medium"


def _size_class_words(size_class: str) -> str:
    if size_class == "large":
        return "large (at least one tenth of the image height in cap height)"
    if size_class == "small":
        return "small (a fine-print caption size, still fully legible)"
    return "medium (clearly readable but not dominant)"


def _text_block(text: list[TextItem], theme: dict | None) -> list[str]:
    if not text:
        return ["No text, no labels, no numerals anywhere."]
    theme = theme or {}
    family = (theme.get("typography") or {}).get("family")
    lines = ["Text (verbatim, render exactly, no extra characters):"]
    for item in text:
        bit = (
            f'- "{item.text}" -- role: {item.role}; placement: {item.placement}; '
            f"size: {_size_class_words(resolve_size_class(item, theme))}"
        )
        if family:
            bit += f"; typography: {family}"
        if item.style:
            bit += f"; style: {item.style}"
        lines.append(bit)
    return lines


def _compose_prompt(
    use_case: str,
    subject: str,
    *,
    theme: dict | None,
    text: list[TextItem],
    size: str,
    quality: str,
    background: str,
    layout: str | None,
    extra_avoid: list[str],
) -> str:
    theme = theme or {}
    subject = subject.strip()
    if background == "chroma":  # legacy alias
        background = "transparent"
    style_tokens = list(theme.get("style_tokens") or [])
    negative_tokens = list(theme.get("negative_tokens") or [])
    stroke = theme.get("stroke") or {}
    composition = theme.get("composition") or {}
    typography = theme.get("typography") or {}
    palette = theme.get("palette") or {}

    header = (
        "Use your built-in image_gen tool to generate exactly one image. "
        "Do not display the image inline. Copy the final selected image to "
        "./output.png in the current working directory. Reply with only the "
        "absolute path to that file on success, or the single word ERROR on "
        "failure."
    )
    lines = [
        header,
        "",
        f"Use case: {use_case}.",
        f"Asset type: static image, size {size}, quality {quality}.",
        f"Primary request: {subject}",
        "",
        f"Subject: {subject}",
        "",
    ]

    style_bits = style_tokens
    if stroke.get("weight_px"):
        style_bits.append(f"stroke weight approximately {stroke['weight_px']} px")
    palette_lines = theme_palette_lines(theme)
    if palette_lines:
        style_bits.append("palette: " + "; ".join(palette_lines))
    if typography.get("family"):
        style_bits.append(f"typography family: {typography['family']}")
    if style_bits:
        lines.append("Style/medium: " + ", ".join(style_bits) + ".")
    else:
        lines.append("Style/medium: clean scientific illustration style.")
    lines.append("")

    composition_bits = []
    if layout:
        composition_bits.append(layout)
    if composition.get("perspective"):
        composition_bits.append(f"perspective: {composition['perspective']}")
    if composition_bits:
        lines.append("Composition/layout: " + "; ".join(composition_bits) + ".")
    else:
        lines.append(
            "Composition/layout: single centered subject with balanced padding."
        )
    lines.append("")

    lines.extend(_text_block(text, theme))
    lines.append("")

    avoid = [
        *negative_tokens,
        *extra_avoid,
        "no other text anywhere",
        "no watermark",
        "no caption",
        "no border",
    ]
    lines.append("Avoid: " + ", ".join(avoid) + ".")
    lines.append("")

    if background == "transparent":
        lines.append(
            "Background: fully transparent; preserve the alpha channel exactly, "
            "with no gradient, texture, shadow, or vignette. If true "
            "transparency is not achievable, fall back to a perfectly flat, "
            "solid #00ff00 chroma-key background instead (it will be removed "
            "programmatically)."
        )
    else:
        bg_hex = palette.get("background") or palette.get("bg")
        bg_desc = (
            f"#FFFFFF or {bg_hex}"
            if bg_hex and bg_hex.upper() != "#FFFFFF"
            else "#FFFFFF"
        )
        lines.append(
            f"Background: opaque solid white background ({bg_desc}), not transparent, no alpha."
        )

    return "\n".join(lines)


def build_figure_prompt(
    subject: str,
    *,
    theme: dict | None = None,
    text: list[TextItem] | None = None,
    size: str = "auto",
    quality: str = "high",
    background: str = "opaque",
    layout: str | None = None,
    extra_avoid: list[str] | None = None,
) -> str:
    return _compose_prompt(
        "full scientific figure or figure panel for a publication, poster, or presentation",
        subject,
        theme=theme,
        text=text or [],
        size=size,
        quality=quality,
        background=background,
        layout=layout,
        extra_avoid=extra_avoid or [],
    )


def build_icon_prompt(
    subject: str,
    theme: dict | None = None,
    size: str = "1024x1024",
    chroma: bool = True,
) -> str:
    theme = theme or {}
    quality = (theme.get("model_preferences") or {}).get("image_quality") or "high"
    return _compose_prompt(
        "flat minimal scientific icon for use in a figure, slide deck, or UI",
        subject,
        theme=theme,
        text=[],
        size=size,
        quality=quality,
        background="transparent" if chroma else "opaque",
        layout="single flat minimal icon, centered, generous padding",
        extra_avoid=[
            "shading",
            "gradients",
            "3D effects",
            "drop shadows",
            "photographic realism",
        ],
    )
