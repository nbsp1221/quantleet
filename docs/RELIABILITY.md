# Reliability

This document defines repository-level reliability expectations.

## Core Rules

- Changes should start from a written plan or spec.
- Verification must be run from the current repository state.
- Backtest and paper-trading behavior must be reproducible from checked-in inputs and documented assumptions.
- Notebook validation and smoke checks should remain part of the local verification surface.

## Evaluation Modes

Repository reliability work uses three distinct evaluation modes:

- `mechanical checks` for objective pass/fail contracts
- `LLM-assisted critique` for adversarial review of confusion paths, weak proxies, and missing failure modes
- `human judgment` for value, product direction, and whether a proposed proxy is worth keeping

Use [design-docs/architecture-governance.md](design-docs/architecture-governance.md) as the canonical source for the full taxonomy, promotion ladder, and metric/check admission rule.

Reliability policy must not collapse these into one score or one gate.

In particular:

- passing a mechanical check does not prove a change is valuable
- LLM critique is evidence-bearing review input, not a final verdict
- human judgment remains required when a proposed evaluation changes product direction or evaluation philosophy

## Safety Tiers

- Tier A: `trading`, `execution`
- Tier B: `data`, `research`
- Tier C: `ml`, notebooks, generated docs

Tier A work requires stronger human gate and must not be treated as agent-autonomous completion.

## Local Verification

Current baseline verification commands:

- `uv run poe verify`
- `uv run poe coverage`
- `uv run poe format`
- `uv run poe test-live`
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`

Low-level repository commands remain available for direct use:

- `uv run python scripts/coverage_check.py`
- `uv run python scripts/repo_check.py`
- `uv run python scripts/notebook_validate.py`
- `uv run python scripts/live_smoke.py`

`uv run poe` is the preferred developer entry point for common local workflows. It is a harnessed convenience layer above the repo-local scripts.

## Coverage Guardrail

The repository treats coverage as a repo-local reliability floor for source code under `src/quantcraft`.

- global source line coverage must stay at or above `90%`
- files under `src/quantcraft/trading/domain/` must remain at `100%` line coverage

This is a risk-based guardrail for agent work, not a substitute for contract tests or structure checks.
