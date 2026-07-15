"""Filesystem-backed integration tests for user instruction installation."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "project" / "skills" / "install-user-instructions"
SCRIPT = SKILL / "scripts" / "install_user_instructions.py"
TEMPLATE = SKILL / "assets" / "global-instructions.md"
START = "<!-- research-skills:global-instructions:start -->"
END = "<!-- research-skills:global-instructions:end -->"


def run_installer(
    home: Path,
    systems: str,
    *extra: str,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    for name in ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "COPILOT_HOME"):
        env.pop(name, None)
    env.update(env_overrides or {})
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--home",
            str(home),
            "--systems",
            systems,
            *extra,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_preview_does_not_write(tmp_path: Path):
    result = run_installer(tmp_path, "claude,codex,copilot")

    assert result.returncode == 0
    assert "MODE=preview" in result.stdout
    assert "/dev/null" in result.stdout
    assert not (tmp_path / ".claude" / "CLAUDE.md").exists()
    assert not (tmp_path / ".codex" / "AGENTS.md").exists()
    assert not (tmp_path / ".copilot" / "copilot-instructions.md").exists()


def test_apply_writes_only_selected_targets(tmp_path: Path):
    result = run_installer(tmp_path, "claude,copilot", "--apply")

    assert result.returncode == 0
    claude = tmp_path / ".claude" / "CLAUDE.md"
    copilot = tmp_path / ".copilot" / "copilot-instructions.md"
    assert START in claude.read_text()
    assert END in copilot.read_text()
    assert not (tmp_path / ".codex" / "AGENTS.md").exists()


def test_existing_content_is_preserved_and_rerun_is_idempotent(tmp_path: Path):
    target = tmp_path / ".codex" / "AGENTS.md"
    target.parent.mkdir(parents=True)
    prefix = "# My existing rules\n\nKeep this exact text.\n"
    target.write_text(prefix)

    first = run_installer(tmp_path, "codex", "--apply")
    after_first = target.read_text()
    second = run_installer(tmp_path, "codex", "--apply")

    assert first.returncode == 0
    assert second.returncode == 0
    assert after_first.startswith(prefix)
    assert target.read_text() == after_first
    assert after_first.count(START) == 1
    assert "STATUS=current" in second.stdout


def test_existing_crlf_bytes_are_preserved(tmp_path: Path):
    target = tmp_path / ".codex" / "AGENTS.md"
    target.parent.mkdir(parents=True)
    prefix = b"# Existing rules\r\n\r\nKeep CRLF.\r\n"
    target.write_bytes(prefix)

    result = run_installer(tmp_path, "codex", "--apply")

    assert result.returncode == 0
    assert target.read_bytes().startswith(prefix)


def test_symlink_target_is_rejected_without_mutation(tmp_path: Path):
    real = tmp_path / "real-claude.md"
    original = b"# Real file\r\n"
    real.write_bytes(original)
    target = tmp_path / ".claude" / "CLAUDE.md"
    target.parent.mkdir(parents=True)
    target.symlink_to(real)

    result = run_installer(tmp_path, "claude", "--apply")

    assert result.returncode == 2
    assert "target is a symlink" in result.stderr
    assert target.is_symlink()
    assert real.read_bytes() == original


def test_documented_home_overrides_are_honored(tmp_path: Path):
    codex_home = tmp_path / "custom-codex"
    copilot_home = tmp_path / "custom-copilot"
    result = run_installer(
        tmp_path,
        "codex,copilot",
        "--apply",
        env_overrides={
            "CODEX_HOME": str(codex_home),
            "COPILOT_HOME": str(copilot_home),
        },
    )

    assert result.returncode == 0
    assert (codex_home / "AGENTS.md").exists()
    assert (copilot_home / "copilot-instructions.md").exists()


def test_nonempty_codex_override_is_reported_only_when_present(tmp_path: Path):
    codex_home = tmp_path / "custom-codex"
    codex_home.mkdir()

    absent = run_installer(
        tmp_path,
        "codex",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )
    (codex_home / "AGENTS.override.md").write_text("# Override\n")
    present = run_installer(
        tmp_path,
        "codex",
        env_overrides={"CODEX_HOME": str(codex_home)},
    )

    assert "override detected" not in absent.stdout
    assert "non-empty override detected" in present.stdout
    assert str(codex_home / "AGENTS.override.md") in present.stdout


def test_check_reports_drift_without_writing(tmp_path: Path):
    target = tmp_path / ".claude" / "CLAUDE.md"

    drift = run_installer(tmp_path, "claude", "--check")
    assert drift.returncode == 1
    assert not target.exists()

    applied = run_installer(tmp_path, "claude", "--apply")
    current = run_installer(tmp_path, "claude", "--check")

    assert applied.returncode == 0
    assert current.returncode == 0


def test_cursor_is_manual_and_creates_no_guessed_file(tmp_path: Path):
    result = run_installer(tmp_path, "cursor", "--apply")

    assert result.returncode == 0
    assert "SYSTEM=cursor STATUS=manual" in result.stdout
    assert "Cursor Settings > Rules" in result.stdout
    assert not (tmp_path / ".cursor").exists()


@pytest.mark.parametrize("systems", ["", "unknown", ",,"])
def test_invalid_selection_fails(tmp_path: Path, systems: str):
    result = run_installer(tmp_path, systems)

    assert result.returncode == 2
    assert "ERROR:" in result.stderr


def test_unmatched_managed_marker_fails_without_writing(tmp_path: Path):
    target = tmp_path / ".claude" / "CLAUDE.md"
    target.parent.mkdir(parents=True)
    original = f"custom\n{START}\nbroken\n"
    target.write_text(original)

    result = run_installer(tmp_path, "claude", "--apply")

    assert result.returncode == 2
    assert "unmatched or repeated" in result.stderr
    assert target.read_text() == original


def test_template_encodes_routing_cleanup_and_github_exception():
    text = TEMPLATE.read_text()

    assert all(name in text for name in ("Fable", "Opus", "Sonnet"))
    assert all(name in text for name in ("Sol", "Terra", "Luna"))
    assert "close or remove the agent" in text
    assert "Use semantic line breaks" in text
    assert "GitHub issue and pull-request bodies are the exception" in text
