#!/usr/bin/env python3
"""Keep model ids current against the providers' model lists.

Reads ``scripts/model_registry.json``: one entry per model family with a version
pattern and the id the repository currently uses. For each provider whose key is
set (or whose list is given with ``--from-file``), finds the highest version that
matches each family's pattern. When a family has a newer id, ``--apply``:

1. replaces every exact occurrence of the old id with the new one in the tracked
   files the registry's ``scan`` globs match (fnmatch, so ``plugins/*.md`` matches
   at any depth);
2. records the new id as ``current`` and adds the old id to ``retired``;
3. bumps the patch version of every plugin with a changed file outside its
   ``tests/`` directory, the marketplace version once, and ``CITATION.cff``.

Without ``--apply`` it only reports. Writes a Markdown summary with ``--summary``,
and ``changed`` and ``incomplete`` (a provider skipped or a family unmatched) to
``$GITHUB_OUTPUT`` when that variable is set; ``--strict`` exits 1 when incomplete.

Usage:
  update_model_ids.py [--apply] [--strict] [--summary PATH] [--from-file PROVIDER=PATH ...]
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = "scripts/model_registry.json"
USER_AGENT = "research-skills-model-check"
MARKETPLACES = (".claude-plugin/marketplace.json", ".github/plugin/marketplace.json")
PLUGIN_MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".github/plugin/plugin.json",
)


class UpdateError(RuntimeError):
    """A condition the run cannot recover from; the message says what to fix."""


# --- provider lists -----------------------------------------------------------


def _get_json(url: str, headers: dict[str, str]) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **headers})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_anthropic(key: str) -> list[str]:
    headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
    ids: list[str] = []
    url = "https://api.anthropic.com/v1/models?limit=1000"
    while True:
        page = _get_json(url, headers)
        ids += [model["id"] for model in page["data"]]
        if not page.get("has_more"):
            return ids
        url = (
            f"https://api.anthropic.com/v1/models?limit=1000&after_id={page['last_id']}"
        )


def fetch_openai(key: str) -> list[str]:
    page = _get_json(
        "https://api.openai.com/v1/models", {"Authorization": f"Bearer {key}"}
    )
    return [model["id"] for model in page["data"]]


FETCHERS = {"anthropic": fetch_anthropic, "openai": fetch_openai}


def ids_from_listing(listing: dict | list) -> list[str]:
    """Model ids from an API response (``data[].id``) or a Codex models cache (``models[].slug``)."""
    if isinstance(listing, dict):
        listing = listing.get("data", listing.get("models", []))
    ids = []
    for entry in listing:
        model_id = (
            entry if isinstance(entry, str) else entry.get("id") or entry.get("slug")
        )
        if model_id:
            ids.append(model_id)
    return ids


# --- selection ----------------------------------------------------------------


def version_of(model_id: str, pattern: str) -> tuple[int, ...] | None:
    match = re.match(pattern, model_id)
    if not match:
        return None
    return tuple(int(part) for part in re.split(r"[.-]", match.group(1)))


def newest(ids: list[str], pattern: str) -> str | None:
    """The id with the highest version that matches ``pattern``, or None."""
    versioned = [(version_of(i, pattern), i) for i in ids]
    versioned = [(v, i) for v, i in versioned if v is not None]
    return max(versioned)[1] if versioned else None


def plan(
    registry: dict, listings: dict[str, list[str]]
) -> tuple[list[dict], list[str], list[str]]:
    """Return (updates, notes, unmatched). An update is {provider, family, old, new};
    ``unmatched`` names families no listed model matches."""
    updates, notes, unmatched = [], [], []
    for provider, spec in registry["providers"].items():
        if provider not in listings:
            continue
        ids = listings[provider]
        for family, entry in spec["families"].items():
            current, pattern = entry["current"], entry["pattern"]
            latest = newest(ids, pattern)
            if latest is None:
                unmatched.append(f"{provider}/{family}")
                notes.append(
                    f"{provider}/{family}: no listed model matches `{pattern}`."
                )
                continue
            if current not in ids:
                notes.append(f"{provider}/{family}: `{current}` is no longer listed.")
            latest_version = version_of(latest, pattern) or ()
            if latest_version > (version_of(current, pattern) or ()):
                updates.append(
                    {
                        "provider": provider,
                        "family": family,
                        "old": current,
                        "new": latest,
                    }
                )
    return updates, notes, unmatched


# --- rewriting ----------------------------------------------------------------


def tracked_files(root: Path, globs: list[str]) -> list[Path]:
    listed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.split("\0")
    return [
        root / name
        for name in listed
        if name and name != REGISTRY and any(fnmatch.fnmatch(name, g) for g in globs)
    ]


def id_regex(model_id: str) -> re.Pattern[str]:
    # Exact id only: not a prefix of a longer id (gpt-6-luna-mini, gpt-6-luna.1), but a
    # sentence-ending period is fine.
    return re.compile(rf"(?<![\w.-]){re.escape(model_id)}(?![\w-]|\.\w)")


def retired_regex(patterns: list[str]) -> re.Pattern[str]:
    """Match any retired id with the same boundaries as ``id_regex``.

    A variant or snapshot of a retired id (``gpt-6-luna-mini``) and a longer current id
    that merely starts with it (``claude-opus-5-5`` for a retired ``claude-opus-5``) do not match.
    """
    return re.compile("|".join(rf"(?<![\w.-])(?:{p})(?![\w-]|\.\w)" for p in patterns))


def rewrite(root: Path, globs: list[str], updates: list[dict]) -> list[Path]:
    changed = []
    for path in tracked_files(root, globs):
        text = path.read_text()
        new = text
        for update in updates:
            new = id_regex(update["old"]).sub(update["new"], new)
        if new != text:
            path.write_text(new)
            changed.append(path)
    return changed


# --- versions -----------------------------------------------------------------


def bump_patch(version: str) -> str:
    major, minor, patch = (int(p) for p in version.split("."))
    return f"{major}.{minor}.{patch + 1}"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise UpdateError(
            f"{path}: expected exactly one {old!r}, found {text.count(old)}"
        )
    path.write_text(text.replace(old, new))


def bump_versions(root: Path, changed: list[Path]) -> dict[str, tuple[str, str]]:
    """Patch-bump every plugin with a non-test change, then the marketplace once."""
    plugins = sorted(
        {
            p.relative_to(root).parts[1]
            for p in changed
            if p.relative_to(root).parts[0] == "plugins"
            and "tests" not in p.relative_to(root).parts[2:3]
        }
    )
    bumps: dict[str, tuple[str, str]] = {}
    for name in plugins:
        base = root / "plugins" / name
        old = json.loads((base / ".claude-plugin/plugin.json").read_text())["version"]
        new = bump_patch(old)
        bumps[name] = (old, new)
        for manifest in PLUGIN_MANIFESTS:
            if (base / manifest).exists():
                replace_once(
                    base / manifest, f'"version": "{old}"', f'"version": "{new}"'
                )
        for marketplace in MARKETPLACES:
            path = root / marketplace
            text = path.read_text()
            entry = re.compile(
                rf'("name": "{re.escape(name)}"[^}}]*?"version": "){re.escape(old)}"',
                re.DOTALL,
            )
            text, count = entry.subn(rf'\g<1>{new}"', text)
            if count != 1:
                raise UpdateError(
                    f"{marketplace}: plugin entry {name} at {old} not found"
                )
            path.write_text(text)
        for doc, patterns in (
            ("AGENTS.md", [f"**{name}** (v{{}})"]),
            ("README.md", [f"| **{name}** | {{}} |", f"**{name}** (v{{}})"]),
        ):
            path = root / doc
            if path.exists():
                text = path.read_text()
                hits = sum(text.count(pattern.format(old)) for pattern in patterns)
                if hits == 0 and f"**{name}**" in text:
                    raise UpdateError(
                        f"{doc}: lists {name} but no version text matches {old}; update the patterns in bump_versions"
                    )
                for pattern in patterns:
                    text = text.replace(pattern.format(old), pattern.format(new))
                path.write_text(text)

    if bumps or changed:
        old = json.loads((root / MARKETPLACES[0]).read_text())["version"]
        new = bump_patch(old)
        bumps["marketplace"] = (old, new)
        for marketplace in MARKETPLACES:
            path = root / marketplace
            text = path.read_text()
            head, sep, tail = text.partition('"plugins"')
            target = f'"version": "{old}"'
            if head.count(target) != 1:
                raise UpdateError(
                    f"{marketplace}: expected one top-level {target}, found {head.count(target)}"
                )
            path.write_text(head.replace(target, f'"version": "{new}"') + sep + tail)
        citation = root / "CITATION.cff"
        if citation.exists():
            text = re.sub(
                r"^version: .*$",
                f"version: {new}",
                citation.read_text(),
                flags=re.MULTILINE,
            )
            text = re.sub(
                r"^date-released: .*$",
                f'date-released: "{dt.date.today().isoformat()}"',
                text,
                flags=re.MULTILINE,
            )
            citation.write_text(text)
    return bumps


# --- driver -------------------------------------------------------------------


def collect_listings(
    registry: dict, from_files: list[str]
) -> tuple[dict[str, list[str]], list[str]]:
    listings, warnings = {}, []
    for item in from_files:
        provider, _, path = item.partition("=")
        if provider not in registry["providers"] or not path:
            raise UpdateError(
                f"--from-file expects PROVIDER=PATH with PROVIDER in {sorted(registry['providers'])}"
            )
        listings[provider] = ids_from_listing(
            json.loads(Path(path).expanduser().read_text())
        )
    for provider, spec in registry["providers"].items():
        if provider in listings:
            continue
        key = os.environ.get(spec["env"], "")
        if not key:
            warnings.append(f"{provider}: {spec['env']} is not set; skipped.")
            continue
        try:
            listings[provider] = FETCHERS[provider](key)
        except (urllib.error.URLError, KeyError, ValueError) as error:
            raise UpdateError(
                f"{provider}: model list request failed: {error}"
            ) from error
    if not listings:
        raise UpdateError(
            "no provider list available: set ANTHROPIC_API_KEY and/or OPENAI_API_KEY, or pass --from-file"
        )
    return listings, warnings


def summarize(updates, notes, warnings, bumps, changed, root, checked) -> str:
    lines = [f"Checked: {', '.join(sorted(checked))}.", ""]
    if updates:
        lines += ["| Provider | Family | Old | New |", "|---|---|---|---|"]
        lines += [
            f"| {u['provider']} | {u['family']} | `{u['old']}` | `{u['new']}` |"
            for u in updates
        ]
        lines.append("")
    else:
        lines += ["Every family is on its newest listed id.", ""]
    if changed:
        lines += [
            f"Rewrote {len(changed)} file(s): "
            + ", ".join(f"`{p.relative_to(root)}`" for p in changed),
            "",
        ]
    if bumps:
        lines += [
            "Version bumps: "
            + ", ".join(f"{k} {a} -> {b}" for k, (a, b) in bumps.items()),
            "",
        ]
    for note in notes + warnings:
        lines.append(f"- {note}")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument(
        "--apply",
        action="store_true",
        help="rewrite ids, update the registry, and bump versions",
    )
    parser.add_argument(
        "--summary", type=Path, help="write a Markdown summary to this path"
    )
    parser.add_argument(
        "--from-file", action="append", default=[], metavar="PROVIDER=PATH"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail when a provider is skipped or a family matches no listed model",
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    registry_path = root / REGISTRY
    registry = json.loads(registry_path.read_text())
    try:
        listings, warnings = collect_listings(registry, args.from_file)
        updates, notes, unmatched = plan(registry, listings)
        changed, bumps = [], {}
        if args.apply and updates:
            changed = rewrite(root, registry["scan"], updates)
            for update in updates:
                registry["providers"][update["provider"]]["families"][update["family"]][
                    "current"
                ] = update["new"]
                registry["retired"].append(re.escape(update["old"]))
            registry_path.write_text(json.dumps(registry, indent=2) + "\n")
            bumps = bump_versions(root, changed)
    except UpdateError as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"::warning::{warning}", file=sys.stderr)
    summary = summarize(updates, notes, warnings, bumps, changed, root, listings)
    print(summary)
    if args.summary:
        args.summary.write_text(summary)
    incomplete = bool(warnings or unmatched)
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as handle:
            handle.write(f"changed={'true' if args.apply and updates else 'false'}\n")
            handle.write(f"incomplete={'true' if incomplete else 'false'}\n")
    if args.strict and incomplete:
        print(
            "::error::incomplete check: "
            + "; ".join(
                warnings + [f"{f}: no listed model matches" for f in unmatched]
            ),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
