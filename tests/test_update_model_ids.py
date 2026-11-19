"""Tests for scripts/update_model_ids.py against a real temporary git repository.

Provider listings are fixture data in the shape the APIs return; nothing in the
updater is replaced. Fixture ids use the made-up ``zeta`` family so that a real
model update, which rewrites ids across ``tests/*.py``, never edits this file.
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

ZETA = r"^gpt-(\d+(?:\.\d+)?)-zeta$"
REGISTRY = {
    "providers": {
        "anthropic": {
            "env": "ANTHROPIC_API_KEY",
            "families": {
                "zeta": {
                    "pattern": r"^claude-zeta-(\d{1,2}(?:-\d{1,2})?)$",
                    "current": "claude-zeta-5-5",
                }
            },
        },
        "openai": {
            "env": "OPENAI_API_KEY",
            "families": {"zeta": {"pattern": ZETA, "current": "gpt-6-zeta"}},
        },
    },
    "scan": ["AGENTS.md", "README.md", "plugins/*.md", "plugins/*.json"],
    "retired": ["gpt-1[.]0-zeta"],
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
        "Workers run gpt-6-zeta.\nNot gpt-6-zeta-mini, not gpt-6-zeta.1.\n",
    )
    write(tmp_path / "plugins/demo/tests/test_x.py", "# gpt-6-zeta\n")
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
    write(tmp_path / "AGENTS.md", "- **demo** (v0.1.0): uses gpt-6-zeta.\n")
    write(tmp_path / "README.md", "| **demo** | 0.1.0 | x |\n")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return tmp_path


@pytest.fixture
def no_keys(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def listing(tmp_path: Path, name: str, payload: object) -> str:
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(payload))
    return str(path)


def snapshot(repo: Path) -> dict[Path, str]:
    return {
        p: p.read_text()
        for p in repo.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }


def test_newest_ignores_snapshots_and_variants():
    claude = REGISTRY["providers"]["anthropic"]["families"]["zeta"]["pattern"]
    ids = [
        "claude-zeta-5-5",
        "claude-zeta-6",
        "claude-zeta-5-5-20260101",
        "claude-zeta-6-fast",
    ]
    assert updater.newest(ids, claude) == "claude-zeta-6"
    ids = ["gpt-6-zeta", "gpt-6.10-zeta", "gpt-6.9-zeta", "gpt-7-zeta-mini"]
    assert updater.newest(ids, ZETA) == "gpt-6.10-zeta"
    assert updater.newest(["gpt-6-other"], ZETA) is None


def test_ids_from_listing_reads_api_and_codex_cache_shapes():
    assert updater.ids_from_listing({"data": [{"id": "a"}, {"id": "b"}]}) == ["a", "b"]
    cache = {"models": [{"slug": "gpt-6-zeta"}, {"slug": "x"}]}
    assert updater.ids_from_listing(cache) == ["gpt-6-zeta", "x"]


def test_retired_regex_spares_variants_and_longer_current_ids():
    retired = updater.retired_regex(
        ["gpt\\-6\\-zeta", "claude\\-zeta\\-5", "gpt-1[.]0-zeta"]
    )
    assert retired.search("still uses gpt-6-zeta.")
    assert retired.search("gpt-1.0-zeta")
    assert not retired.search("gpt-6-zeta-mini and gpt-6-zeta.1")
    assert not retired.search("claude-zeta-5-5")


def test_apply_rewrites_exact_ids_and_bumps_versions(
    repo, tmp_path, no_keys, monkeypatch
):
    output = tmp_path / "gh_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    cache = listing(
        tmp_path,
        "codex",
        {"models": [{"slug": "gpt-6-zeta"}, {"slug": "gpt-6.1-zeta"}]},
    )

    assert (
        updater.main(["--apply", "--root", str(repo), "--from-file", f"openai={cache}"])
        == 0
    )

    skill = (repo / "plugins/demo/skills/s/SKILL.md").read_text()
    assert (
        skill == "Workers run gpt-6.1-zeta.\nNot gpt-6-zeta-mini, not gpt-6-zeta.1.\n"
    )
    assert (repo / "plugins/demo/tests/test_x.py").read_text() == "# gpt-6-zeta\n", (
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
    assert claude_mkt["version"] == "0.9.1"
    assert github_mkt["metadata"]["version"] == "0.9.1"
    assert [p["version"] for p in claude_mkt["plugins"]] == ["0.1.1", "1.0.0"]
    assert [p["version"] for p in github_mkt["plugins"]] == ["0.1.1", "1.0.0"]
    assert "version: 0.9.1" in (repo / "CITATION.cff").read_text()
    assert (
        repo / "AGENTS.md"
    ).read_text() == "- **demo** (v0.1.1): uses gpt-6.1-zeta.\n"
    assert (repo / "README.md").read_text() == "| **demo** | 0.1.1 | x |\n"

    registry = json.loads((repo / "scripts/model_registry.json").read_text())
    assert (
        registry["providers"]["openai"]["families"]["zeta"]["current"] == "gpt-6.1-zeta"
    )
    assert registry["retired"] == ["gpt-1[.]0-zeta", "gpt\\-6\\-zeta"]
    # anthropic was skipped (no key), so the run is incomplete but not failed
    assert output.read_text() == "changed=true\nincomplete=true\n"


def test_marketplace_version_equal_to_a_plugin_version_still_bumps_once(
    repo, tmp_path, no_keys
):
    for rel in (".claude-plugin/marketplace.json", ".github/plugin/marketplace.json"):
        path = repo / rel
        path.write_text(
            path.read_text().replace('"version": "1.0.0"', '"version": "0.9.0"')
        )
    cache = listing(tmp_path, "codex", {"data": [{"id": "gpt-6.1-zeta"}]})

    assert (
        updater.main(["--apply", "--root", str(repo), "--from-file", f"openai={cache}"])
        == 0
    )

    claude_mkt = json.loads((repo / ".claude-plugin/marketplace.json").read_text())
    assert claude_mkt["version"] == "0.9.1"
    assert [p["version"] for p in claude_mkt["plugins"]] == ["0.1.1", "0.9.0"]


def test_unrecognized_doc_version_format_fails_loudly(repo, tmp_path, no_keys, capsys):
    (repo / "AGENTS.md").write_text("- **demo** version 0.1.0: uses gpt-6-zeta.\n")
    cache = listing(tmp_path, "codex", {"data": [{"id": "gpt-6.1-zeta"}]})

    assert (
        updater.main(["--apply", "--root", str(repo), "--from-file", f"openai={cache}"])
        == 1
    )
    assert (
        "AGENTS.md: lists demo but no version text matches 0.1.0"
        in capsys.readouterr().err
    )


def test_no_newer_id_changes_nothing(repo, tmp_path, no_keys, monkeypatch):
    output = tmp_path / "gh_output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    before = snapshot(repo)
    claude = listing(tmp_path, "claude", {"data": [{"id": "claude-zeta-5-5"}]})
    openai = listing(
        tmp_path, "openai", {"data": [{"id": "gpt-6-zeta"}, {"id": "gpt-1.0-zeta"}]}
    )
    args = ["--apply", "--strict", "--root", str(repo)]

    assert (
        updater.main(
            [
                *args,
                "--from-file",
                f"anthropic={claude}",
                "--from-file",
                f"openai={openai}",
            ]
        )
        == 0
    )

    assert {p: p.read_text() for p in before} == before
    assert output.read_text() == "changed=false\nincomplete=false\n"


def test_strict_fails_when_a_provider_is_skipped_or_a_family_unmatched(
    repo, tmp_path, no_keys, capsys
):
    openai = listing(tmp_path, "openai", {"data": [{"id": "gpt-6-zeta"}]})
    assert (
        updater.main(
            ["--strict", "--root", str(repo), "--from-file", f"openai={openai}"]
        )
        == 1
    )
    assert "ANTHROPIC_API_KEY is not set" in capsys.readouterr().err

    claude = listing(tmp_path, "claude", {"data": [{"id": "claude-other-1"}]})
    both = ["--from-file", f"anthropic={claude}", "--from-file", f"openai={openai}"]
    assert updater.main(["--strict", "--root", str(repo), *both]) == 1
    assert "anthropic/zeta: no listed model matches" in capsys.readouterr().err


def test_listed_current_id_missing_is_reported(repo, tmp_path, no_keys, capsys):
    cache = listing(tmp_path, "api", {"data": [{"id": "gpt-1.0-zeta"}]})
    assert updater.main(["--root", str(repo), "--from-file", f"openai={cache}"]) == 0
    assert "`gpt-6-zeta` is no longer listed" in capsys.readouterr().out


def test_no_provider_available_fails(repo, no_keys, capsys):
    assert updater.main(["--root", str(repo)]) == 1
    assert "no provider list available" in capsys.readouterr().err
