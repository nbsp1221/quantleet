# Tooling Reference

Use this reference for the repository's local command and task surface.

## Low-Level Stable Commands

These commands remain the stable low-level repo-local interface:

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`
- `uv run python scripts/repo_check.py`
- `uv run python scripts/notebook_validate.py`
- `uv run python scripts/live_smoke.py`

## Poe Task Layer

Use `uv run poe` for the common developer workflow:

- `uv run poe lint`
- `uv run poe format`
- `uv run poe typecheck`
- `uv run poe test`
- `uv run poe test-unit`
- `uv run poe test-integration`
- `uv run poe test-structure`
- `uv run poe test-smoke`
- `uv run poe test-live`
- `uv run poe build`
- `uv run poe repo-check`
- `uv run poe notebook-validate`
- `uv run poe live-smoke`
- `uv run poe verify`

The current repository uses the shorthand configuration:

- `[tool.poe]`
- `executor = "uv"`

The harness accepts either official Poe executor form:

- `executor = "uv"`
- `[tool.poe.executor] type = "uv"`

## Formatting Standard

- `ruff format .` is the standard formatter
- `uv run poe format` applies formatting
- `uv run poe lint` verifies lint rules after formatting
