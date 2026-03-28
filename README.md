# quantcraft

`quantcraft` is a quant library and framework that will grow across market data, research tooling, backtesting, paper trading, live trading, and quant-related ML utilities.

The current implemented scope is intentionally small:

- typed exchange access for OHLCV market data
- spot and USD-M support through a stable `Exchange` API
- a first `quantcraft.data` ingestion surface with `CCXTDataSource`, `CSVDataSource`, and `DataFrameDataSource`
- automatic historical pagination inside `CCXTDataSource.load()` for exchange-backed range assembly
- a deterministic single-symbol Backtest MVP built on the shared trading kernel
- a first `quantcraft.research` ergonomics surface with `Strategy`, `run_backtest`, `ta`, and `qc`
- canonical quickstart and notebook assets for the current research workflow

## Setup

Requirements:

- Python 3.13
- `uv`

Install and verify locally:

```bash
uv sync
uv run poe verify
```

Direct commands remain available:

```bash
uv run pytest -q
uv run ruff check .
uv run mypy src
uv build
uv run python scripts/repo_check.py
uv run python scripts/notebook_validate.py
uv run python scripts/live_smoke.py
```

## Current Verification Surface

The repository currently relies on:

- unit tests
- integration tests
- structure and repo-rule checks
- static analysis
- packaging checks
- notebook validation

For day-to-day development, use the Poe task layer:

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

Agent-first repository harnessing keeps documentation, architecture rules, and local verification as first-class repository features.

The harness is repo-local DX infrastructure. It lives in `scripts/` and is orchestrated by Poe; it is not modeled as an installed package CLI.

## Test Taxonomy

The test suite is being organized by test type at the top level:

- `tests/unit`
- `tests/integration`
- `tests/structure`
- `tests/smoke`

`unit` and `integration` mirror the source layout when a matching source package path exists. Transitional domain-intent names such as `market_data` are still acceptable where bounded-context package moves are not yet complete. `structure` owns repository-rule checks, and live/network-backed smoke validation stays out of the default test lane.

Live tests are explicit-only and excluded from the default `pytest` run.

Current examples:

- `tests/unit/market_data/...`
- `tests/integration/commands/...`
- `tests/structure/architecture/...`
- `tests/structure/docs/...`
- `tests/structure/repo/...`
- `tests/smoke/local/...`
- `tests/smoke/live/...`
