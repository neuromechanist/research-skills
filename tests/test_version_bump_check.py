"""Real-git tests for scripts/check_version_bump.py (temporary repositories, no mocks)."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_version_bump.py"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


def _write_json(path: Path, version: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": version}))


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)


def _repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q", "-b", "main")
    _write_json(tmp_path / ".claude-plugin/marketplace.json", "1.0.0")
    _write_json(tmp_path / "plugins/alpha/.claude-plugin/plugin.json", "0.1.0")
    _write_json(tmp_path / "plugins/beta/.claude-plugin/plugin.json", "0.2.0")
    (tmp_path / "plugins/alpha/skills").mkdir(parents=True)
    (tmp_path / "plugins/alpha/tests").mkdir()
    (tmp_path / "plugins/alpha/skills/SKILL.md").write_text("one\n")
    _commit(tmp_path, "base")
    _git(tmp_path, "checkout", "-q", "-b", "pr")
    return tmp_path


def _run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPT), "--base", "main", "--root", str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_unbumped_plugin_change_fails(tmp_path):
    repo = _repo(tmp_path)
    (repo / "plugins/alpha/skills/SKILL.md").write_text("two\n")
    _commit(repo, "edit")
    result = _run(repo)
    assert result.returncode == 1
    assert "plugin alpha" in result.stdout
    assert "marketplace version" in result.stdout


def test_plugin_bump_without_marketplace_bump_fails(tmp_path):
    repo = _repo(tmp_path)
    (repo / "plugins/alpha/skills/SKILL.md").write_text("two\n")
    _write_json(repo / "plugins/alpha/.claude-plugin/plugin.json", "0.1.1")
    _commit(repo, "edit")
    result = _run(repo)
    assert result.returncode == 1
    assert "plugin alpha" not in result.stdout
    assert "marketplace version" in result.stdout


def test_both_bumped_passes_and_untouched_plugin_needs_nothing(tmp_path):
    repo = _repo(tmp_path)
    (repo / "plugins/alpha/skills/SKILL.md").write_text("two\n")
    _write_json(repo / "plugins/alpha/.claude-plugin/plugin.json", "0.1.1")
    _write_json(repo / ".claude-plugin/marketplace.json", "1.0.1")
    _commit(repo, "edit")
    result = _run(repo)
    assert result.returncode == 0, result.stdout


def test_numeric_not_lexical_comparison(tmp_path):
    repo = _repo(tmp_path)
    _write_json(repo / "plugins/alpha/.claude-plugin/plugin.json", "0.1.9")
    _write_json(repo / ".claude-plugin/marketplace.json", "1.0.9")
    _commit(repo, "to 9")
    _git(repo, "checkout", "-q", "main")
    _git(repo, "merge", "-q", "--ff-only", "pr")
    _git(repo, "checkout", "-q", "-b", "pr2")
    (repo / "plugins/alpha/skills/SKILL.md").write_text("two\n")
    _write_json(repo / "plugins/alpha/.claude-plugin/plugin.json", "0.1.10")
    _write_json(repo / ".claude-plugin/marketplace.json", "1.0.10")
    _commit(repo, "to 10")
    assert _run(repo).returncode == 0


def test_test_only_and_root_changes_need_no_bump(tmp_path):
    repo = _repo(tmp_path)
    (repo / "plugins/alpha/tests/test_x.py").write_text("x = 1\n")
    (repo / "README.md").write_text("hi\n")
    _commit(repo, "tests and docs")
    assert _run(repo).returncode == 0


def test_new_plugin_needs_only_marketplace_bump(tmp_path):
    repo = _repo(tmp_path)
    _write_json(repo / "plugins/gamma/.claude-plugin/plugin.json", "0.1.0")
    _write_json(repo / ".claude-plugin/marketplace.json", "1.0.1")
    _commit(repo, "new plugin")
    assert _run(repo).returncode == 0
