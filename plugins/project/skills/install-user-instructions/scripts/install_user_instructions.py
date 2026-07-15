#!/usr/bin/env python3
"""Preview or install a managed user-instruction block across agent tools."""

from __future__ import annotations

import argparse
import difflib
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

START = "<!-- research-skills:global-instructions:start -->"
END = "<!-- research-skills:global-instructions:end -->"
SUPPORTED = ("claude", "codex", "copilot", "cursor")


@dataclass(frozen=True)
class Target:
    system: str
    path: Path | None
    note: str = ""


def parse_systems(raw: str) -> list[str]:
    systems: list[str] = []
    for item in raw.split(","):
        name = item.strip().lower()
        if not name:
            continue
        if name not in SUPPORTED:
            choices = ", ".join(SUPPORTED)
            raise ValueError(f"unsupported system {name!r}; choose from: {choices}")
        if name not in systems:
            systems.append(name)
    if not systems:
        raise ValueError("select at least one system")
    return systems


def env_home(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else default


def resolve_targets(systems: list[str], home: Path) -> list[Target]:
    targets: list[Target] = []
    for system in systems:
        if system == "claude":
            root = env_home("CLAUDE_CONFIG_DIR", home / ".claude")
            targets.append(Target(system, root / "CLAUDE.md"))
        elif system == "codex":
            root = env_home("CODEX_HOME", home / ".codex")
            override = root / "AGENTS.override.md"
            note = (
                f"non-empty override detected and takes precedence: {override}"
                if override.is_file() and override.stat().st_size > 0
                else ""
            )
            targets.append(Target(system, root / "AGENTS.md", note))
        elif system == "copilot":
            root = env_home("COPILOT_HOME", home / ".copilot")
            targets.append(Target(system, root / "copilot-instructions.md"))
        else:
            targets.append(
                Target(
                    system,
                    None,
                    "paste the managed content into Cursor Settings > Rules",
                )
            )
    return targets


def managed_block(template: str) -> str:
    body = template.strip()
    if START in body or END in body:
        raise ValueError("template must not contain managed-block markers")
    return f"{START}\n{body}\n{END}"


def update_content(existing: str, block: str) -> str:
    start_count = existing.count(START)
    end_count = existing.count(END)
    if start_count != end_count or start_count > 1:
        raise ValueError("target has unmatched or repeated managed-block markers")
    if start_count == 1:
        start = existing.index(START)
        end = existing.index(END, start) + len(END)
        return existing[:start] + block + existing[end:]
    if not existing:
        return block + "\n"
    separator = (
        "" if existing.endswith("\n\n") else "\n" if existing.endswith("\n") else "\n\n"
    )
    return existing + separator + block + "\n"


def show_diff(path: Path, existing: str, proposed: str) -> None:
    before = str(path) if existing else "/dev/null"
    diff = difflib.unified_diff(
        existing.splitlines(keepends=True),
        proposed.splitlines(keepends=True),
        fromfile=before,
        tofile=str(path),
    )
    sys.stdout.writelines(diff)


def atomic_write(path: Path, content: bytes) -> None:
    """Replace path atomically while retaining an existing file's mode."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            temporary.chmod(path.stat().st_mode & 0o777)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parser() -> argparse.ArgumentParser:
    default_template = (
        Path(__file__).resolve().parents[1] / "assets" / "global-instructions.md"
    )
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--systems", required=True, help="comma-separated system names")
    result.add_argument("--template", type=Path, default=default_template)
    result.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help=(
            "base home for default targets; CLAUDE_CONFIG_DIR, CODEX_HOME, and "
            "COPILOT_HOME take precedence"
        ),
    )
    result.add_argument("--apply", action="store_true", help="write approved changes")
    result.add_argument(
        "--check", action="store_true", help="exit 1 when changes are needed"
    )
    return result


def main() -> int:
    args = parser().parse_args()
    if args.apply and args.check:
        print("ERROR: --apply and --check are mutually exclusive", file=sys.stderr)
        return 2
    try:
        systems = parse_systems(args.systems)
        template = args.template.read_text()
        block = managed_block(template)
        targets = resolve_targets(systems, args.home.expanduser())
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    changed = False
    for target in targets:
        if target.path is None:
            print(f"SYSTEM={target.system} STATUS=manual NOTE={target.note}")
            print(block)
            continue

        path = target.path
        try:
            if path.is_symlink():
                raise ValueError(
                    f"target is a symlink; replace it explicitly before applying: {path}"
                )
            existing = path.read_bytes().decode("utf-8") if path.exists() else ""
            proposed = update_content(existing, block)
        except (OSError, ValueError) as error:
            print(f"ERROR: {target.system}: {error}", file=sys.stderr)
            return 2

        status = (
            "current" if existing == proposed else "updated" if existing else "created"
        )
        mode = "apply" if args.apply else "preview"
        print(f"SYSTEM={target.system} TARGET={path} STATUS={status} MODE={mode}")
        if target.note:
            print(f"NOTE={target.note}")
        if existing == proposed:
            continue
        changed = True
        if args.apply:
            try:
                atomic_write(path, proposed.encode("utf-8"))
            except OSError as error:
                print(f"ERROR: {target.system}: {error}", file=sys.stderr)
                return 2
        else:
            show_diff(path, existing, proposed)

    if args.check and changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
