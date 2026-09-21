"""Safety contracts for the semantic-line-break wrapper."""

import sys
from pathlib import Path

import pytest

SCRIPT_DIR = (
    Path(__file__).resolve().parents[1]
    / "plugins"
    / "manuscript"
    / "skills"
    / "manuscript-formatting"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

from semantic_breaks import (
    protect_latex_regions,
    restore_changed_spans,
    restore_latex_regions,
)


def test_latex_regions_round_trip_as_atomic_placeholders():
    source = (
        "Visible prose.\n"
        "\\begin{verbatim}\n"
        "a  b\n"
        "% raw content\n"
        "\\end{verbatim}\n\n"
        "% Keep this comment exactly.\n"
        "Acknowledgments remain below.\n"
    )

    protected, regions = protect_latex_regions(source)

    assert len(regions) == 2
    assert "\\begin{verbatim}" not in protected
    assert "% Keep this comment exactly." not in protected
    assert all(token in protected for token in regions)
    assert restore_latex_regions(protected, regions) == source


def test_token_divergence_rolls_back_only_the_affected_paragraph():
    original = (
        "First sentence. Second sentence.\n\n"
        "The protected content is still present.\n"
        "Acknowledgments remain present.\n"
    )
    candidate = (
        "First sentence.\nSecond sentence.\n\n"
        "The protected content is still present.\n"
    )

    guarded = restore_changed_spans(original, candidate)

    assert "First sentence.\nSecond sentence." in guarded
    assert "Acknowledgments remain present." in guarded


def test_whitespace_only_candidate_is_kept():
    original = "A sentence stays intact. Another sentence follows.\n"
    candidate = "A sentence stays intact.\nAnother sentence follows.\n"

    assert restore_changed_spans(original, candidate) == candidate


def test_protected_content_divergence_is_restored_before_unprotecting():
    source = "% Preserve this full-line comment.\nVisible text follows.\n"
    protected, regions = protect_latex_regions(source)
    token = next(iter(regions))
    candidate = protected.replace(token, "", 1)

    guarded = restore_changed_spans(protected, candidate)
    assert restore_latex_regions(guarded, regions) == source


def test_protected_region_restoration_discards_formatter_whitespace():
    source = "Before.\n% Keep this comment.\nAfter.\n"
    protected, regions = protect_latex_regions(source)
    token = next(iter(regions))
    candidate = protected.replace(token, f"{token}  \n\n", 1)

    assert restore_latex_regions(candidate, regions) == source


def test_unmatched_verbatim_block_is_rejected():
    with pytest.raises(ValueError, match="unmatched"):
        protect_latex_regions("\\begin{verbatim}\nnever closes\n")


def test_verbatim_end_before_begin_is_rejected():
    with pytest.raises(ValueError, match="unmatched"):
        protect_latex_regions("\\end{verbatim}\n")
