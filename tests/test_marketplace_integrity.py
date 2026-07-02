"""Marketplace integrity checks.

Real filesystem and JSON assertions only (no mocks, no LLM calls). These guard the
class of regressions that are easy to introduce by hand across many manifests and
skill/agent files:

- every plugin/marketplace manifest is valid JSON;
- each plugin's version is identical everywhere it is declared (plugin.json for both
  ecosystems plus native Copilot manifests and the marketplace manifests);
- the marketplace top-level version matches across manifests;
- every review/QA agent shell points its ``test -f "$REF/<procedure>.md"`` guard at a
  procedure file that actually exists in the matching skill's ``references/``;
- review/QA agent descriptions stay scoped to "invoked by the <skill> skill".

Run: ``uv run --with pytest pytest tests/ -q``
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = ROOT / "plugins"
PLUGINS = sorted(
    p.name for p in PLUGINS_DIR.iterdir() if (p / ".claude-plugin" / "plugin.json").exists()
)
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
FRONTMATTER = re.compile(r"\A---\n(?P<body>.*?)\n---", re.DOTALL)
MAX_SKILL_DESCRIPTION_CHARS = 1024


def _load(path: Path):
    return json.loads(path.read_text())


def _marketplace_entry(manifest: dict, name: str):
    return next((p for p in manifest.get("plugins", []) if p.get("name") == name), None)


def _frontmatter_lines(path: Path) -> list[str]:
    text = path.read_text()
    match = FRONTMATTER.match(text)
    assert match, f"{path.relative_to(ROOT)}: missing YAML frontmatter"
    return match.group("body").splitlines()


def _single_line_frontmatter_value(path: Path, key: str) -> str:
    prefix = f"{key}:"
    for line in _frontmatter_lines(path):
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    raise AssertionError(f"{path.relative_to(ROOT)}: missing {key!r} in frontmatter")


def _decode_frontmatter_string(path: Path, key: str) -> str:
    raw = _single_line_frontmatter_value(path, key)
    if (raw.startswith("'") and raw.endswith("'")) or (
        raw.startswith('"') and raw.endswith('"')
    ):
        return raw[1:-1]
    assert ": " not in raw, (
        f"{path.relative_to(ROOT)}: unquoted {key!r} contains ': ', which Codex rejects"
    )
    return raw


def test_all_manifests_are_valid_json():
    manifests = (
        list(PLUGINS_DIR.glob("*/.claude-plugin/plugin.json"))
        + list(PLUGINS_DIR.glob("*/.codex-plugin/plugin.json"))
        + list(PLUGINS_DIR.glob("*/.github/plugin/plugin.json"))
        + [
            ROOT / ".claude-plugin/marketplace.json",
            ROOT / ".github/plugin/marketplace.json",
            ROOT / ".agents/plugins/marketplace.json",
        ]
    )
    for m in manifests:
        assert m.exists(), f"missing manifest: {m.relative_to(ROOT)}"
        _load(m)  # raises JSONDecodeError on malformed JSON


def test_skill_frontmatter_is_codex_loadable():
    skills = sorted(PLUGINS_DIR.glob("*/skills/*/SKILL.md"))
    assert skills, "no plugin skills found"

    for skill in skills:
        description = _decode_frontmatter_string(skill, "description")
        assert description, f"{skill.relative_to(ROOT)}: empty description"
        assert len(description) <= MAX_SKILL_DESCRIPTION_CHARS, (
            f"{skill.relative_to(ROOT)}: description is {len(description)} characters; "
            f"Codex maximum is {MAX_SKILL_DESCRIPTION_CHARS}"
        )


@pytest.mark.parametrize("plugin", PLUGINS)
def test_plugin_version_consistent_across_manifests(plugin):
    canonical = _load(PLUGINS_DIR / plugin / ".claude-plugin/plugin.json")["version"]
    assert SEMVER.match(canonical), f"{plugin}: version is not semver: {canonical!r}"

    codex = PLUGINS_DIR / plugin / ".codex-plugin/plugin.json"
    if codex.exists():
        assert _load(codex)["version"] == canonical, (
            f"{plugin}: .codex-plugin version != .claude-plugin"
        )

    copilot = PLUGINS_DIR / plugin / ".github/plugin/plugin.json"
    assert copilot.exists(), f"{plugin}: missing native Copilot manifest"
    assert _load(copilot)["version"] == canonical, (
        f"{plugin}: .github/plugin version != .claude-plugin"
    )

    claude_mkt = _marketplace_entry(_load(ROOT / ".claude-plugin/marketplace.json"), plugin)
    assert claude_mkt is not None, f"{plugin}: absent from .claude-plugin/marketplace.json"
    assert claude_mkt["version"] == canonical, (
        f"{plugin}: .claude-plugin/marketplace.json {claude_mkt['version']} != plugin.json {canonical}"
    )

    gh_mkt = _marketplace_entry(_load(ROOT / ".github/plugin/marketplace.json"), plugin)
    assert gh_mkt is not None, f"{plugin}: absent from .github/plugin/marketplace.json"
    assert gh_mkt["version"] == canonical, (
        f"{plugin}: .github/plugin/marketplace.json {gh_mkt['version']} != plugin.json {canonical}"
    )


def test_marketplace_toplevel_version_matches():
    claude_top = _load(ROOT / ".claude-plugin/marketplace.json")["version"]
    gh_top = _load(ROOT / ".github/plugin/marketplace.json")["metadata"]["version"]
    assert SEMVER.match(claude_top), f"marketplace version not semver: {claude_top!r}"
    assert claude_top == gh_top, (
        f"marketplace top-level version mismatch: claude {claude_top} != github {gh_top}"
    )


@pytest.mark.parametrize("plugin", PLUGINS)
def test_copilot_component_paths_exist(plugin):
    manifest = _load(PLUGINS_DIR / plugin / ".github/plugin/plugin.json")
    for key in ("commands", "skills", "agents"):
        values = manifest.get(key, [])
        if isinstance(values, str):
            values = [values]
        for value in values:
            path = PLUGINS_DIR / plugin / value
            assert path.exists(), f"{plugin}: Copilot {key} path does not exist: {value}"
            if key == "agents":
                assert list(path.glob("*.agent.md")), (
                    f"{plugin}: Copilot agents path has no .agent.md files: {value}"
                )


# (plugin, agent-stem) pairs for the review/QA agents introduced by the review-subagent
# pattern. Each agent must guard on, and its skill must contain, a procedure file.
REVIEW_AGENTS = [
    ("grant", "grant-review"),
    ("grant", "grant-figure-qa"),
    ("manuscript", "paper-review"),
    ("figures", "figure-qa"),
]

_GUARD = re.compile(r'test -f "\$REF/([A-Za-z0-9._-]+\.md)"')


@pytest.mark.parametrize("plugin,stem", REVIEW_AGENTS)
def test_agent_guard_points_at_existing_procedure(plugin, stem):
    agent = PLUGINS_DIR / plugin / "agents" / f"{stem}.md"
    assert agent.exists(), f"missing agent shell: {agent.relative_to(ROOT)}"
    text = agent.read_text()

    m = _GUARD.search(text)
    assert m, f"{stem}: agent shell has no 'test -f \"$REF/<procedure>.md\"' guard"
    procedure = PLUGINS_DIR / plugin / "skills" / stem / "references" / m.group(1)
    assert procedure.exists(), (
        f"{stem}: guard names {m.group(1)} but {procedure.relative_to(ROOT)} does not exist"
    )

    front = text.split("---", 2)
    assert len(front) >= 3, f"{stem}: agent shell missing YAML frontmatter"
    assert "invoked by the" in front[1].lower(), (
        f"{stem}: agent description is not scoped to 'invoked by the <skill> skill'"
    )
