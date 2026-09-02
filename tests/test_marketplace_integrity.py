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
import shutil
import stat
import subprocess
import tomllib
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


def test_project_model_routing_contract_is_cross_agent():
    fanout = (PLUGINS_DIR / "project" / "skills" / "agent-fanout" / "SKILL.md").read_text()
    for model in ("Fable", "Opus", "Sonnet", "Sol", "Terra", "Luna"):
        assert model in fanout, f"agent-fanout routing is missing {model}"

    consumers = [
        PLUGINS_DIR / "project" / "skills" / "implementation-planning" / "SKILL.md",
        PLUGINS_DIR / "project" / "skills" / "epic-dev" / "SKILL.md",
        PLUGINS_DIR / "project" / "skills" / "workflow-reference" / "SKILL.md",
    ]
    for path in consumers:
        assert "agent-fanout" in path.read_text(), (
            f"{path.relative_to(ROOT)} does not reference central routing policy"
        )


def test_github_body_writers_state_semantic_break_exception():
    writers = [
        PLUGINS_DIR / "project" / "commands" / "epic-dev.md",
        PLUGINS_DIR / "project" / "skills" / "engineering-loop" / "SKILL.md",
        PLUGINS_DIR / "project" / "skills" / "epic-dev" / "SKILL.md",
        PLUGINS_DIR / "project" / "skills" / "implementation-planning" / "SKILL.md",
        PLUGINS_DIR
        / "project"
        / "skills"
        / "agent-fanout"
        / "references"
        / "fanout-prompts.md",
        PLUGINS_DIR / "project" / "skills" / "workflow-reference" / "SKILL.md",
    ]
    for path in writers:
        text = path.read_text()
        assert re.search(r"semantic\s+line\s+break", text, re.IGNORECASE), (
            f"{path.relative_to(ROOT)} is missing semantic-line-break guidance"
        )
        assert re.search(r"one\s+source\s+line", text), (
            f"{path.relative_to(ROOT)} is missing GitHub paragraph formatting"
        )


def test_github_validation_uses_contributor_entrypoint():
    script = ROOT / "scripts" / "validate"
    workflow = ROOT / ".github" / "workflows" / "tests.yml"

    assert script.exists(), "missing contributor validation script"
    assert script.stat().st_mode & stat.S_IXUSR, "scripts/validate is not executable"
    assert "./scripts/validate" in workflow.read_text()


def test_codex_agent_templates_are_valid_and_pin_worker_tiers():
    templates = PLUGINS_DIR / "project" / "agents" / "templates"
    parsed = {}
    for path in sorted(templates.glob("*.toml")):
        data = tomllib.loads(path.read_text())
        for key in ("name", "description", "developer_instructions"):
            assert data.get(key), f"{path.relative_to(ROOT)}: missing {key}"
        parsed[data["name"]] = data

    assert parsed["phase-planner"]["model"] == "gpt-5.6-terra"
    assert parsed["phase-planner"]["sandbox_mode"] == "read-only"
    assert parsed["implementation-worker"]["model"] == "gpt-5.6-luna"
    assert parsed["implementation-worker"]["sandbox_mode"] == "workspace-write"


def test_copilot_agent_templates_have_descriptions():
    templates = PLUGINS_DIR / "project" / "agents" / "templates"
    agents = sorted(templates.glob("*.agent.md"))
    assert agents, "project plugin has no Copilot agent templates"
    for path in agents:
        assert _decode_frontmatter_string(path, "description")


def test_copilot_worker_templates_use_cli_tool_names():
    templates = PLUGINS_DIR / "project" / "agents" / "templates"
    planner = (templates / "phase-planner.agent.md").read_text()
    worker = (templates / "implementation-worker.agent.md").read_text()

    for tool in ("view", "glob", "rg"):
        assert f"  - {tool}\n" in planner
    for tool in ("view", "edit", "apply_patch", "bash", "glob", "rg"):
        assert f"  - {tool}\n" in worker
    assert "  - terminal\n" not in worker


def test_version_bump_aborts_before_writing_when_plugin_manifests_drift(tmp_path: Path):
    script = tmp_path / "plugins" / "project" / "bin" / "project-bump-version"
    script.parent.mkdir(parents=True)
    shutil.copy2(PLUGINS_DIR / "project" / "bin" / "project-bump-version", script)

    manifests = {
        "plugins/project/.claude-plugin/plugin.json": {
            "name": "project",
            "version": "1.0.0",
        },
        "plugins/project/.codex-plugin/plugin.json": {
            "name": "project",
            "version": "1.0.1",
        },
        "plugins/project/.github/plugin/plugin.json": {
            "name": "project",
            "version": "1.0.0",
        },
        ".claude-plugin/marketplace.json": {
            "version": "2.0.0",
            "plugins": [{"name": "project", "version": "1.0.0"}],
        },
        ".github/plugin/marketplace.json": {
            "metadata": {"version": "2.0.0"},
            "plugins": [{"name": "project", "version": "1.0.0"}],
        },
    }
    for relative, content in manifests.items():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content))
    before = {relative: (tmp_path / relative).read_bytes() for relative in manifests}

    result = subprocess.run(
        ["bash", str(script), "project", "patch"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "version drift" in result.stderr
    assert all(
        (tmp_path / relative).read_bytes() == content
        for relative, content in before.items()
    )


_REFERENCE_MENTION = re.compile(r"references/([\w.-]+\.md)")


def test_skill_name_matches_directory():
    for skill in sorted(PLUGINS_DIR.glob("*/skills/*/SKILL.md")):
        name = _single_line_frontmatter_value(skill, "name")
        assert name == skill.parent.name, (
            f"{skill.relative_to(ROOT)}: frontmatter name {name!r} != directory {skill.parent.name!r}"
        )


def test_skill_reference_mentions_exist():
    for skill in sorted(PLUGINS_DIR.glob("*/skills/*/SKILL.md")):
        text = skill.read_text()
        for ref in sorted(set(_REFERENCE_MENTION.findall(text))):
            path = skill.parent / "references" / ref
            assert path.exists(), (
                f"{skill.relative_to(ROOT)}: mentions references/{ref} but "
                f"{path.relative_to(ROOT)} does not exist"
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


DISPATCH_RE = re.compile(r'subagent_type:\s*"([^"]+)"')


def _dispatching_skills() -> list[tuple[str, Path, str]]:
    found = []
    for plugin in PLUGINS:
        for skill_md in sorted((PLUGINS_DIR / plugin / "skills").glob("*/SKILL.md")):
            for target in DISPATCH_RE.findall(skill_md.read_text()):
                found.append((plugin, skill_md, target))
    return found


def test_claude_dispatch_targets_are_namespaced_and_exist():
    """Claude Code registers plugin agents as ``<plugin>:<agent>``.

    A bare agent name never resolves, so the primary dispatch path silently
    degrades to the inline fallback. Every ``subagent_type`` string in a skill
    must carry its own plugin's namespace and point at a shipped agent file.
    """
    dispatches = _dispatching_skills()
    assert dispatches, "expected at least one dispatching skill"
    for plugin, skill_md, target in dispatches:
        rel = skill_md.relative_to(ROOT)
        assert ":" in target, f"{rel}: subagent_type {target!r} is not namespaced"
        target_plugin, agent = target.split(":", 1)
        assert target_plugin == plugin, (
            f"{rel}: subagent_type {target!r} names plugin {target_plugin!r}, expected {plugin!r}"
        )
        agent_file = PLUGINS_DIR / plugin / "agents" / f"{agent}.md"
        assert agent_file.is_file(), f"{rel}: subagent_type {target!r} has no agent at {agent_file.relative_to(ROOT)}"


def test_claude_dispatch_uses_agent_tool_name():
    """The subagent tool is ``Agent``; ``Task(subagent_type ...)`` is the pre-rename form."""
    stale = []
    for path in sorted(PLUGINS_DIR.rglob("*.md")):
        if "Task(subagent_type" in path.read_text():
            stale.append(str(path.relative_to(ROOT)))
    assert not stale, f"stale Task(subagent_type ...) dispatch in: {stale}"
