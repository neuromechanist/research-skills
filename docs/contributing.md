# Contributing

## Versioning

- Each plugin has independent versioning in its own `plugin.json`.
- Adding a new plugin or skill is a marketplace minor bump (`0.x.0`).
- A version bump within an existing plugin is a marketplace patch bump (`0.x.y`).
- Bumps don't propagate upward by default: a skill patch doesn't automatically bump its plugin, and a plugin bump doesn't automatically bump the marketplace, beyond the rule above.

## Releases and citation

- The marketplace version lives in `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json` (the Codex `.agents/plugins/marketplace.json` carries no top-level version).
- GitHub release tags mirror the marketplace top-level version: marketplace `0.15.12` gets tag `v0.15.12`, not a separately incrementing release sequence.
- The repository is archived to Zenodo on every GitHub release, minting a versioned DOI under a stable concept DOI. When the marketplace version bumps for a release, `CITATION.cff`'s `version` and `date-released` fields get bumped alongside it, and `.zenodo.json` stays in sync.
- The concept DOI (in `CITATION.cff`'s `doi:` field and the README badge) is stable across versions and does not change.

## Development conventions

- Detailed project rules live in `.rules/`; check the relevant rule file before changing manifests, skills, agents, tests, CI, or language tooling.
- Use [Bun](https://bun.sh/) for JavaScript/TypeScript work; see `.rules/javascript.md`.
- Use [UV](https://docs.astral.sh/uv/) for Python work (this docs site included); see `.rules/python.md`.
- No mocks in tests; see `.rules/testing.md`.
- No emojis in commits or code; see `.rules/git.md`.

## Cross-agent compatibility

Any plugin update must check Claude Code, Codex, and GitHub Copilot CLI manifests and install paths together; see [Cross-Agent Compatibility](cross-agent-compatibility.md) for the researched registration paths, and `.rules/cross-agent-compatibility.md` for the update policy itself.

## Building these docs locally

```bash
uv sync --group docs
uv run mkdocs serve   # http://127.0.0.1:8000/
uv run mkdocs build --strict
```

CI builds and deploys this site to the `gh-pages` branch on every push to `main` that touches `docs/**`, `mkdocs.yml`, or `pyproject.toml`. Run `mkdocs build --strict` locally before pushing; it fails on any broken nav entry or image link, which is the easiest way to catch a typo'd path.

## Adding to these docs

A new plugin gets a page at `docs/plugins/<name>.md` following the same skeleton every existing plugin page uses, in this order:

1. `# Title` and a one-paragraph intro (what the plugin does, in plain terms).
2. All of the plugin's workflow sections, one to three of them, each pairing a short explanation with one diagram, if a diagram exists that illustrates that workflow well. Not every section needs one; `presentation.md` has none.
3. `## Skills`, after every workflow section, not interleaved with them: every skill in the plugin, one bullet each, one line of accurate description. Pull the wording from `README.md`'s existing plugin section rather than re-describing from scratch, so the two don't drift.
4. `## Try it`: a fenced code block of 2-4 realistic example prompts (or commands, for `project`), taken from or matching the README's examples.
5. `## Learn more`: a link to the matching [Agentic Research Course](https://courses.osc.earth/agentic-research/) week, if one exists; otherwise say so plainly (see `presentation.md`).

Then add the page to `mkdocs.yml`'s `nav.Plugins` list; nav entries are manual, not auto-discovered.

New diagrams go in `docs/assets/diagrams/` as flat files (no subfolders) and get referenced with a path relative to the current page's depth: `assets/diagrams/foo.svg` from a top-level page like `index.md`, `../assets/diagrams/foo.svg` from a page under `docs/plugins/`. `mkdocs build --strict` catches a wrong relative depth immediately.

If a diagram is reused from an external repo (as the current set is, from `agentic-research-course`), copy it rather than symlinking, since a separate repo's files aren't guaranteed to stay at that path, and caption it based on what it actually depicts, not what the surrounding prose would like it to depict. When no existing diagram fits a new section well, prose-only is preferable to a mismatched image.
