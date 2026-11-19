"""Tests for scripts/update_model_ids.py against a real temporary git repository.

Provider listings are fixture data in the shape the APIs return; nothing in the
updater is replaced.
"""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "update_model_ids", ROOT / "scripts" / "update_model_ids.py"
)
assert SPEC and SPEC.loader
updater = importlib.util.module_from_spec(SPEC)
sys.modules["update_model_ids"] = updater
SPEC.loader.exec_module(updater)

REGISTRY = {
    "providers": {
        "anthropic": {
            "env": "ANTHROPIC_API_KEY",
            "families": {
                "opus": {
                    "pattern": r"^claude-opus-(\d{1,2}(?:-\d{1,2})?)$",
                    "current": "claude-opus-5-5",
                }
            },
        },
        "openai": {
            "env": "OPENAI_API_KEY",
            "families": {
                "luna": {
                    "pattern": r"^gpt-(\d+(?:\.\d+)?)-luna$",
                    "current": "gpt-6-luna",
                }
            },
        },
    },
    "scan": ["AGENTS.md", "README.md", "plugins/*.md", "plugins/*.json"],
    "retired": ["gpt-5[.]6"],
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    write(tmp_path / "scripts/model_registry.json", json.dumps(REGISTRY, indent=2))
    manifest = '{\n  "name": "demo",\n  "version": "0.1.0"\n}\n'
    for rel in (
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        ".github/plugin/plugin.json",
    ):
        write(tmp_path / "plugins/demo" / rel, manifest)
    write(
        tmp_path / "plugins/demo/skills/s/SKILL.md",
        "Workers run gpt-6-luna.\nNot gpt-6-luna-mini, not gpt-6-luna.1.\n",
    )
    write(tmp_path / "plugins/demo/tests/test_x.py", "# gpt-6-luna\n")
    write(
        tmp_path / "plugins/other/.claude-plugin/plugin.json",
        '{\n  "name": "other",\n  "version": "1.0.0"\n}\n',
    )
    entries = (
        '[{"name": "demo", "version": "0.1.0"}, {"name": "other", "version": "1.0.0"}]'
    )
    write(
        tmp_path / ".claude-plugin/marketplace.json",
        f'{{\n  "version": "0.9.0",\n  "plugins": {entries}\n}}\n',
    )
    write(
        tmp_path / ".github/plugin/marketplace.json",
        f'{{\n  "metadata": {{"version": "0.9.0"}},\n  "plugins": {entries}\n}}\n',
    )
    write(tmp_path / "CITATION.cff", 'version: 0.9.0\ndate-released: "2026-01-01"\n')
    write(tmp_path / "AGENTS.md", "- **demo** (v0.1.0): uses gpt-6-luna.\n")
    write(tmp_path / "README.md", "| **demo** | 0.1.0 | x |\n")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return tmp_path


def listing(tmp_path: Path, name: str, payload: object) -> str:
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(payload))
    return str(path)


def test_newest_ignores_snapshots_and_variants():
    ids = [
        "claude-opus-5-5",
        "claude-opus-6",
        "claude-opus-5-5-20260101",
        "claude-opus-6-fast",
    ]
    assert (
        updater.newest(
            ids, REGISTRY["providers"]["anthropic"]["families"]["opus"]["pattern"]
        )
        == "claude-opus-6"
    )
    luna = REGISTRY["providers"]["openai"]["families"]["luna"]["pattern"]
    assert (
        updater.newest(
            ["gpt-6-luna", "gpt-6.10-luna", "gpt-6.9-luna", "gpt-7-luna-mini"], luna
        )
        == "gpt-6.10-luna"
    )
    assert updater.newest(["gpt-6-sol"], luna) is None


def test_ids_from_listing_reads_api_and_codex_cache_shapes():
    assert updater.ids_from_listing({"data": [{"id": "a"}, {"id": "b"}]}) == ["a", "b"]
    assert updater.ids_from_listing(
        {"models": [{"slug": "gpt-6-luna"}, {"slug": "x"}]}
    ) == ["gpt-6-luna", "x"]


def test_apply_rewrites_exact_ids_and_bumps_versions(repo, tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    output = tmp_path / "gh_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    cache = listing(
        tmp_path,
        "codex",
        {"models": [{"slug": "gpt-6-luna"}, {"slug": "gpt-6.1-luna"}]},
    )

    assert (
        updater.main(["--apply", "--root", str(repo), "--from-file", f"openai={cache}"])
        == 0
    )

    skill = (repo / "plugins/demo/skills/s/SKILL.md").read_text()
    assert (
        skill == "Workers run gpt-6.1-luna.\nNot gpt-6-luna-mini, not gpt-6-luna.1.\n"
    )
    assert (repo / "plugins/demo/tests/test_x.py").read_text() == "# gpt-6-luna\n", (
        "outside the scan globs"
    )
    for rel in (
        ".claude-plugin/plugin.json",
        ".codex-plugin/plugin.json",
        ".github/plugin/plugin.json",
    ):
        assert (
            json.loads((repo / "plugins/demo" / rel).read_text())["version"] == "0.1.1"
        )
    assert (
        json.loads((repo / "plugins/other/.claude-plugin/plugin.json").read_text())[
            "version"
        ]
        == "1.0.0"
    )

    claude_mkt = json.loads((repo / ".claude-plugin/marketplace.json").read_text())
    github_mkt = json.loads((repo / ".github/plugin/marketplace.json").read_text())
    assert (
        claude_mkt["version"] == "0.9.1"
        and github_mkt["metadata"]["version"] == "0.9.1"
    )
    assert [p["version"] for p in claude_mkt["plugins"]] == ["0.1.1", "1.0.0"]
    assert [p["version"] for p in github_mkt["plugins"]] == ["0.1.1", "1.0.0"]
    assert "version: 0.9.1" in (repo / "CITATION.cff").read_text()
    assert (
        repo / "AGENTS.md"
    ).read_text() == "- **demo** (v0.1.1): uses gpt-6.1-luna.\n"
    assert (repo / "README.md").read_text() == "| **demo** | 0.1.1 | x |\n"

    registry = json.loads((repo / "scripts/model_registry.json").read_text())
    assert (
        registry["providers"]["openai"]["families"]["luna"]["current"] == "gpt-6.1-luna"
    )
    assert registry["retired"] == ["gpt-5[.]6", "gpt\\-6\\-luna"]
    assert output.read_text() == "changed=true\n"


def test_no_newer_id_changes_nothing(repo, tmp_path, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    output = tmp_path / "gh_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    before = {
        p: p.read_text()
        for p in repo.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }
    cache = listing(
        tmp_path, "api", {"data": [{"id": "gpt-6-luna"}, {"id": "gpt-5.6-luna"}]}
    )

    assert (
        updater.main(["--apply", "--root", str(repo), "--from-file", f"openai={cache}"])
        == 0
    )

    assert {p: p.read_text() for p in before} == before
    assert output.read_text() == "changed=false\n"


def test_listed_current_id_missing_is_reported(repo, tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cache = listing(tmp_path, "api", {"data": [{"id": "gpt-5.6-luna"}]})
    assert updater.main(["--root", str(repo), "--from-file", f"openai={cache}"]) == 0
    assert "`gpt-6-luna` is no longer listed" in capsys.readouterr().out


def test_no_provider_available_fails(repo, monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert updater.main(["--root", str(repo)]) == 1
    assert "no provider list available" in capsys.readouterr().err
