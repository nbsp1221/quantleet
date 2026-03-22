# Developer Tasks Reference

Use this reference for the local developer task surface.

## Command Layers

- `scripts/`: stable repo-local harness commands
- `tool.poe.tasks`: high-level local development workflows

Do not collapse these layers together.

## Preferred Poe Tasks

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

## Direct Harness Commands

- `uv run python scripts/repo_check.py`
- `uv run python scripts/notebook_validate.py`
- `uv run python scripts/live_smoke.py`

## Formatter Contract

The standard formatter is Ruff:

- `uv run poe format`
- `uv run ruff format .`

Formatting is part of the documented developer interface and should not be treated as an implicit convention.
