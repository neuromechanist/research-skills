#!/usr/bin/env python3
"""Fail when a plugin changes without a version bump.

Compares HEAD with a base ref (the merge base with it, so a base that moved ahead is
not blamed on the PR). Every plugin with a changed file outside its ``tests/``
directory must have a higher version in ``.claude-plugin/plugin.json`` than at the base,
and the marketplace top-level version in ``.claude-plugin/marketplace.json`` must be
higher too. A new plugin only needs the marketplace bump.

Usage: check_version_bump.py --base origin/main [--root PATH]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

MARKETPLACE = ".claude-plugin/marketplace.json"


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout


def version_at(root: Path, ref: str, path: str) -> tuple[int, ...] | None:
    """Parsed version of ``path`` at ``ref``, or None when the file does not exist there."""
    try:
        text = git(root, "show", f"{ref}:{path}")
    except subprocess.CalledProcessError:
        return None
    return tuple(int(part) for part in json.loads(text)["version"].split("."))


def fmt(version: tuple[int, ...]) -> str:
    return ".".join(map(str, version))


def changed_plugins(root: Path, base: str) -> list[str]:
    names = set()
    for path in git(root, "diff", "--name-only", base, "HEAD").splitlines():
        parts = path.split("/")
        if len(parts) > 2 and parts[0] == "plugins" and parts[2] != "tests":
            names.add(parts[1])
    return sorted(names)


def check(root: Path, base_ref: str) -> list[str]:
    base = git(root, "merge-base", base_ref, "HEAD").strip()
    errors = []
    plugins = changed_plugins(root, base)

    for name in plugins:
        manifest = f"plugins/{name}/.claude-plugin/plugin.json"
        old, new = version_at(root, base, manifest), version_at(root, "HEAD", manifest)
        if old is None or new is None:  # new or removed plugin
            continue
        if new <= old:
            errors.append(f"plugin {name} changed but its version is still {fmt(new)} (base {fmt(old)})")

    if plugins:
        old, new = version_at(root, base, MARKETPLACE), version_at(root, "HEAD", MARKETPLACE)
        if old is not None and new is not None and new <= old:
            errors.append(f"marketplace version is still {fmt(new)} (base {fmt(old)})")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", required=True, help="base ref, e.g. origin/main")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    errors = check(args.root, args.base)
    for error in errors:
        print(f"::error::{error}")
    if errors:
        print("Bump the plugin version in every manifest and the marketplace patch version.")
        return 1
    print("Version bumps present for every changed plugin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
