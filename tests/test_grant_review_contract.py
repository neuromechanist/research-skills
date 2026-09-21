"""Cross-agent contract tests for the grant readability review mode."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRANT = ROOT / "plugins" / "grant"
READABILITY = GRANT / "skills" / "grant-review" / "references" / "readability-procedure.md"


def test_readability_mode_is_a_non_scoring_dispatch():
    skill = (GRANT / "skills" / "grant-review" / "SKILL.md").read_text()
    procedure = READABILITY.read_text()

    assert READABILITY.exists()
    assert "mode=readability" in skill
    assert "references/readability-procedure.md" in skill
    assert "never score merit" in skill
    assert "Do not append merit scores" in procedure
    assert "length-neutral rewrite" in procedure


def test_all_review_surfaces_route_readability_to_shared_procedure():
    surfaces = [
        GRANT / "agents" / "grant-review.md",
        GRANT / "agents" / "templates" / "grant-review.toml",
        GRANT / "agents" / "templates" / "grant-review.agent.md",
    ]

    for surface in surfaces:
        text = surface.read_text()
        assert "mode=readability" in text, surface
        assert "readability-procedure.md" in text, surface
        lowered = text.lower()
        assert (
            "never add merit scores" in lowered or "do not score or discuss merit" in lowered
        ), surface


def test_readability_preserves_substantive_limitations():
    procedure = READABILITY.read_text()
    style = (GRANT / "skills" / "grant-writing" / "references" / "writing-style-guide.md").read_text()

    assert "Preserve substantive limitations" in procedure
    assert "Avoid gratuitous self-undermining" in style
    assert "Preserve substantive limitations" in style
