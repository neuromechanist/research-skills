"""Real filesystem contracts for the project-scoped memory convention."""

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = ROOT / "plugins" / "project" / "bin"
INIT = BIN_DIR / "project-init-templates"
DIFF = BIN_DIR / "project-diff-rules"
MEMORY_TEMPLATE = ROOT / "plugins" / "project" / "templates" / "memory"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{BIN_DIR}{os.pathsep}{env.get('PATH', '')}"
    return env


def _run_init(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(INIT), str(project)],
        cwd=project,
        env=_env(),
        check=False,
        capture_output=True,
        text=True,
    )


def _run_diff(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(DIFF), "project", str(project)],
        cwd=project,
        env=_env(),
        check=False,
        capture_output=True,
        text=True,
    )


def test_init_scaffolds_memory_and_rerun_preserves_project_content(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()

    first = _run_init(project)
    assert first.returncode == 0, first.stderr
    memory = project / ".memory"
    assert (memory / "README.md").exists()
    assert (memory / "INDEX.md").exists()

    custom_fact = memory / "observed-flag.md"
    custom_fact.write_text(
        "---\nname: observed-flag\ntype: observation\nrecorded: 2026-09-20\n"
        "revalidate_after: 2026-10-20\n---\nThe flag was verified.\n"
    )
    custom_readme = memory / "README.md"
    custom_index = memory / "INDEX.md"
    custom_readme.write_text(custom_readme.read_text() + "\nProject addition.\n")
    custom_index.write_text(custom_index.read_text() + "\nProject entry.\n")
    before = {
        path: path.read_text()
        for path in (custom_fact, custom_readme, custom_index)
    }

    second = _run_init(project)
    assert second.returncode == 0, second.stderr
    assert {path: path.read_text() for path in before} == before
    assert "preserving existing entries" in second.stdout
    assert "already exists, skipping" in second.stdout


def test_init_adds_missing_memory_convention_files_without_touching_facts(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    memory = project / ".memory"
    memory.mkdir()
    fact = memory / "kept.md"
    fact.write_text("project fact\n")

    result = _run_init(project)
    assert result.returncode == 0, result.stderr
    assert (memory / "README.md").exists()
    assert (memory / "INDEX.md").exists()
    assert fact.read_text() == "project fact\n"


def test_diff_reports_missing_memory_templates_without_mutating_project(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()

    result = _run_diff(project)
    assert result.returncode == 0, result.stderr
    assert "HAS_MEMORY_DIR=false" in result.stdout
    assert "MEMORY_FILE_MISSING=README.md" in result.stdout
    assert "MEMORY_FILE_MISSING=INDEX.md" in result.stdout
    assert not (project / ".memory").exists()


def test_memory_template_documents_boundary_format_and_safety():
    readme = (MEMORY_TEMPLATE / "README.md").read_text()
    index = (MEMORY_TEMPLATE / "INDEX.md").read_text()

    for field in (
        "name:",
        "description:",
        "type:",
        "recorded:",
        "revalidate_after:",
    ):
        assert field in readme
    for store in (".context/decisions/", ".context/", ".memory/"):
        assert store in readme
    for forbidden in (
        "secrets",
        "tokens",
        "credentials",
        "private transcripts",
        "customer data",
        "personal data",
    ):
        assert forbidden in readme
    assert "one line" in index
    assert "Entry" in index
