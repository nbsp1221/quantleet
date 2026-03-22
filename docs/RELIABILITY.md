# Reliability

This document defines repository-level reliability expectations.

## Core Rules

- Changes should start from a written plan or spec.
- Verification must be run from the current repository state.
- Backtest and paper-trading behavior must be reproducible from checked-in inputs and documented assumptions.
- Notebook validation and smoke checks should remain part of the local verification surface.

## Safety Tiers

- Tier A: `trading`, `execution`
- Tier B: `data`, `research`
- Tier C: `ml`, notebooks, generated docs

Tier A work requires stronger human gate and must not be treated as agent-autonomous completion.

## Local Verification

Current baseline verification commands:

- `uv run poe verify`
- `uv run poe format`
- `uv run poe test-live`
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

Low-level repository commands remain available for direct use:

- `uv run python scripts/repo_check.py`
- `uv run python scripts/notebook_validate.py`
- `uv run python scripts/live_smoke.py`

`uv run poe` is the preferred developer entry point for common local workflows. It is a harnessed convenience layer above the repo-local scripts.
