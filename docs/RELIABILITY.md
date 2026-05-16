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
- Tier B: `data`, `research`, `backtest`
- Tier C: `ml`, notebooks, generated docs

Tier A work requires stronger human gate and must not be treated as agent-autonomous completion.

## Local Verification

Current baseline verification commands:

- `uv run poe verify`
- `uv run poe verify-runtime`
- `uv run poe coverage`
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

The default test and coverage commands intentionally serve different purposes:

- `uv run poe test` runs `pytest -q` as the plain test pass/fail lane
- `uv run poe coverage` reruns pytest under coverage.py, measures coverage, and
  enforces the configured coverage hard gate

The performance gate is explicit:

- `uv run poe verify` remains the correctness lane
- `uv run poe perf-check` is the canonical RSI performance-regression lane
- `uv run poe verify-runtime` is the stronger explicit lane for runtime-sensitive backtest or research changes
- the default integration lane keeps a canonical strategy pair:
  - `RSI 30/70 mean reversion`
  - `EMA crossover`
- additional deterministic strategy regression contracts may run in the normal integration lane when they stay cheap and legible
- current checked-in examples include BTC-fixture-backed `qty_percent`
  regressions for shipped market, limit-entry, and limit-exit behavior in the
  normal integration suite
- `perf-check` uses the checked-in BTC USD-M 1h 2025 CSV fixture and measures the backtest execution call only
- the gate fails unless first-run runtime is `< 1.0s`
- the gate also fails unless steady-state median runtime is `< 1.0s`

Run `uv run poe verify-runtime` when a change touches the runtime-sensitive
backtest or research path, especially:

- `src/quantleet/backtest/engine.py`
- `src/quantleet/backtest/runtime.py`
- `src/quantleet/backtest/execution_model.py`
- `src/quantleet/backtest/order_activation.py`
- `src/quantleet/backtest/strategy_runtime.py`
- `src/quantleet/research/ta.py`
- `src/quantleet/research/strategy.py`
- `src/quantleet/research/indicators/runtime/runtime.py`
- `src/quantleet/research/indicators/runtime/factory.py`
- `src/quantleet/research/indicators/pure/`

## Coverage Guardrail

The repository treats coverage as a repo-local reliability floor for source code under `quantleet`.

- coverage.py branch measurement must remain enabled
- coverage.py's combined line/branch total must stay at or above `90%`
- `uv run poe coverage` must collect fresh coverage data by rerunning pytest
  before reporting the gate result

This is a risk-based guardrail for agent work, not a substitute for contract tests or structure checks.
