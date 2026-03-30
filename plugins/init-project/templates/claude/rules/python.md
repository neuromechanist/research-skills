# Python Development Standards

## Version & Environment
- **Python 3.11+** minimum (use latest stable)
- **Package Manager:** UV only (not pip, conda, or virtualenv)
- **Virtual Environment:** Managed by UV (`uv venv`, `uv sync`)
- **Project Config:** `pyproject.toml` (no requirements.txt)

## Quick Reference
```bash
# Create project
uv init my-project && cd my-project

# Add dependencies
uv add requests pandas

# Add dev dependencies
uv add --dev pytest ruff

# Run commands in venv
uv run pytest
uv run python main.py

# Sync environment
uv sync
```

## Code Style
- **Formatter:** `ruff format` (Black-compatible)
- **Linter:** `ruff check --fix --unsafe-fixes`
- **Type Checker:** `ty` (not mypy)
- **Line Length:** 88 characters (Black standard)
- **Imports:** Sorted by ruff (isort-compatible)

## Type Hints
- **Required for:** All public functions and methods
- **Example:**
```python
def process_data(items: list[dict[str, Any]]) -> pd.DataFrame:
    """Process raw data into DataFrame."""
    ...
```

## Project Structure
```
project/
├── src/project/       # Source code
│   ├── __init__.py
│   └── module.py
├── tests/            # Real tests only
├── pyproject.toml    # Project config (UV + ruff + ty)
└── .gitignore
```

## Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ -n "$files" ]; then
    uv run ruff check --fix --unsafe-fixes $files
    uv run ruff format $files
    git add $files
fi
```

## Common Patterns
- **Context Managers:** For resource management
- **Dataclasses:** For data structures
- **Pathlib:** For file operations (not os.path)
- **F-strings:** For string formatting

## Error Handling
```python
# Be specific with exceptions
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise or handle appropriately

# Never do this:
# except Exception:
#     pass  # Silent failure
```

## Never Do This
- Never use `pip install` directly; use `uv add` or `uv pip install`
- Never use `conda`, `virtualenv`, or `venv`; UV handles environments
- Never use `mypy`; use `ty` for type checking
- Never use bare `except:` or `except Exception: pass`
- Never use `os.path`; use `pathlib.Path`
- Never commit `.env` files or hardcoded secrets

## Documentation
- **Docstrings:** Google or NumPy style
- **Module docs:** At file top
- **Type hints:** Self-documenting code

---
*UV for everything. Ruff for style. Ty for types. Real tests only.*
