# Python

- Use Python 3.11+ unless a plugin explicitly supports an older runtime.
- Use `uv` for dependency management, virtual environments, scripts, and test
  commands. Do not introduce `pip install`, `conda`, `virtualenv`, `venv`, or
  `requirements.txt` workflows for project-managed code.
- Use `pyproject.toml` for package metadata and tool configuration.
- Prefer:
  - `uv sync`
  - `uv add <package>`
  - `uv add --dev <package>`
  - `uv run pytest`
  - `uv run ruff check --fix .`
  - `uv run ruff format .`
- Use `ruff` for linting and formatting.
- Use `ty` for type checking when adding or updating type checks.
- Use `pathlib.Path` for filesystem paths.
- Avoid broad exception swallowing. Never use `except Exception: pass` or bare
  `except:`.
- Keep generated artifacts, caches, and local environments out of git.
