"""Real-process contract tests for the project preflight entrypoint."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "plugins" / "project" / "bin" / "project-preflight"


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repo)], check=True)
    return repo


def _run(repo: Path, **overrides: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "PROJECT_PREFLIGHT_NETWORK_PROBE_COMMAND": "true",
            "PROJECT_PREFLIGHT_AGENT_STATUS": "unavailable",
            "PROJECT_PREFLIGHT_GH_BIN": "/private/tmp/project-preflight-missing-gh",
            **overrides,
        }
    )
    return subprocess.run(
        [str(PREFLIGHT), "--format", "json"],
        cwd=repo,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def _data(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0, result.stderr
    assert not result.stderr
    return json.loads(result.stdout)


def test_healthy_repository_state_is_machine_readable(tmp_path: Path):
    data = _data(_run(_repo(tmp_path)))

    assert data["current_branch"] in {"master", "main", "detached"}
    assert data["worktree_count"] == 1
    assert data["gh_network_status"] == "reachable"
    assert data["native_agent_status"] == "unavailable"
    assert data["dirty_paths"] == []


def test_missing_gh_is_optional_and_not_reported_as_auth_failure(tmp_path: Path):
    data = _data(_run(_repo(tmp_path)))

    assert data["gh_command_status"] == "unavailable"
    assert data["gh_auth_status"] == "unavailable"
    assert "not authenticated" not in data["gh_error"]


@pytest.mark.skipif(shutil.which("gh") is None, reason="GitHub CLI is not installed")
def test_invalid_auth_is_distinguished_from_missing_command(tmp_path: Path):
    config_dir = tmp_path / "empty-gh-config"
    config_dir.mkdir()
    data = _data(
        _run(
            _repo(tmp_path),
            PROJECT_PREFLIGHT_GH_BIN=shutil.which("gh") or "gh",
            GH_CONFIG_DIR=str(config_dir),
        )
    )

    assert data["gh_command_status"] == "available"
    assert data["gh_auth_status"] == "not_authenticated"
    assert data["gh_token_status"] == "missing_or_invalid"


@pytest.mark.skipif(shutil.which("gh") is None, reason="GitHub CLI is not installed")
def test_network_failure_does_not_collapse_into_unauthenticated(tmp_path: Path):
    data = _data(
        _run(
            _repo(tmp_path),
            PROJECT_PREFLIGHT_NETWORK_PROBE_COMMAND="false",
            PROJECT_PREFLIGHT_GH_BIN=shutil.which("gh") or "gh",
        )
    )

    assert data["gh_network_status"] == "unreachable"
    assert data["gh_auth_status"] == "unknown_network_unavailable"
    assert "network" in data["gh_error"].lower()


def test_child_shell_credential_mismatch_is_visible_without_exposing_token(tmp_path: Path):
    result = _run(
        _repo(tmp_path),
        GH_TOKEN="parent-token",
        PROJECT_PREFLIGHT_CHILD_GH_TOKEN_PRESENT="false",
    )
    data = _data(result)

    assert data["gh_child_credential_status"] == "mismatch"
    assert "parent-token" not in result.stdout


def test_no_native_agent_is_successful_and_actionable(tmp_path: Path):
    data = _data(_run(_repo(tmp_path), PROJECT_PREFLIGHT_AGENT_STATUS="unavailable"))

    assert data["native_agent_status"] == "unavailable"
    assert data["agent_model"] == "unknown"
    assert data["agent_effort"] == "unknown"
