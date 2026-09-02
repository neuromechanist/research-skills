"""Tests for lib/prompting.py: prompt construction and the text ladder."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib import prompting


def test_build_figure_prompt_with_text_contains_verbatim_block():
    prompt = prompting.build_figure_prompt(
        "a stylized brain",
        text=[
            prompting.TextItem(
                text="Panel A", role="title", placement="top-center", size_class="large"
            )
        ],
    )
    assert "Text (verbatim, render exactly, no extra characters):" in prompt
    assert '"Panel A"' in prompt
    assert "role: title" in prompt
    assert "Use your built-in image_gen tool" in prompt
    assert "./output.png" in prompt


def test_build_figure_prompt_without_text_says_no_text():
    prompt = prompting.build_figure_prompt("a stylized brain")
    assert "No text, no labels, no numerals anywhere." in prompt
    assert "Text (verbatim" not in prompt


def test_build_figure_prompt_opaque_background_says_not_transparent():
    prompt = prompting.build_figure_prompt("a brain", background="opaque")
    assert "opaque solid white background" in prompt
    assert "not transparent, no alpha" in prompt


def test_build_figure_prompt_transparent_background_asks_for_alpha():
    prompt = prompting.build_figure_prompt("a brain", background="transparent")
    assert "preserve the alpha channel" in prompt
    assert "chroma-key background instead" in prompt


def test_build_figure_prompt_chroma_alias_behaves_like_transparent():
    prompt = prompting.build_figure_prompt("a brain", background="chroma")
    assert "preserve the alpha channel" in prompt


def test_build_icon_prompt_is_flat_minimal_and_transparent():
    prompt = prompting.build_icon_prompt("a neuron")
    assert "flat minimal scientific icon" in prompt
    assert "preserve the alpha channel" in prompt


def test_theme_palette_lines_handles_missing_theme():
    assert prompting.theme_palette_lines(None) == []
    assert prompting.theme_palette_lines({}) == []


def test_theme_palette_lines_reports_roles():
    theme = {
        "palette": {
            "primary": "#111111",
            "accent": "#222222",
            "categorical": ["#333333"],
        }
    }
    lines = prompting.theme_palette_lines(theme)
    assert "primary: #111111" in lines
    assert "accent: #222222" in lines
    assert any("categorical" in line for line in lines)


def test_enforce_text_ladder_accepts_short_items():
    items = [prompting.TextItem(text="EEG cap", role="label", placement="left")]
    prompting.enforce_text_ladder(items, theme=None)  # should not raise


def test_enforce_text_ladder_rejects_long_label():
    items = [
        prompting.TextItem(
            text="this label has way too many words", role="label", placement="left"
        )
    ]
    with pytest.raises(prompting.TextLadderError) as exc_info:
        prompting.enforce_text_ladder(items, theme=None)
    assert "word label limit" in str(exc_info.value)
    assert "overlay" in str(exc_info.value)


def test_enforce_text_ladder_rejects_equation_like_text():
    items = [prompting.TextItem(text="x = 3", role="label", placement="left")]
    with pytest.raises(prompting.TextLadderError) as exc_info:
        prompting.enforce_text_ladder(items, theme=None)
    assert "numeral, unit, or equation" in str(exc_info.value)


def test_enforce_text_ladder_rejects_unit_glued_to_digit():
    items = [prompting.TextItem(text="latency 250ms", role="label", placement="left")]
    with pytest.raises(prompting.TextLadderError):
        prompting.enforce_text_ladder(items, theme=None)


def test_enforce_text_ladder_honors_theme_overrides():
    items = [
        prompting.TextItem(
            text="one two three four five six", role="label", placement="left"
        )
    ]
    theme = {"text": {"max_words_per_label": 6}}
    prompting.enforce_text_ladder(items, theme)  # 6 words, limit 6: should pass

    theme_strict = {"text": {"max_words_per_label": 2}}
    with pytest.raises(prompting.TextLadderError):
        prompting.enforce_text_ladder(
            [
                prompting.TextItem(
                    text="three word label", role="label", placement="left"
                )
            ],
            theme_strict,
        )


def test_enforce_text_ladder_title_word_limit():
    items = [
        prompting.TextItem(
            text="one two three four five six seven eight nine",
            role="title",
            placement="top",
        )
    ]
    with pytest.raises(prompting.TextLadderError) as exc_info:
        prompting.enforce_text_ladder(items, theme=None)
    assert "word title limit" in str(exc_info.value)


def test_text_item_rejects_invalid_role():
    with pytest.raises(ValueError):
        prompting.TextItem(text="x", role="bogus")


def test_text_item_rejects_invalid_size_class():
    with pytest.raises(ValueError):
        prompting.TextItem(text="x", size_class="huge")
