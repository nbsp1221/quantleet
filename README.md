# quantcraft

`quantcraft` is a quant library and framework that will grow across market data, research tooling, backtesting, paper trading, live trading, and quant-related ML utilities.

The current implemented scope is intentionally small:

- typed exchange access for OHLCV market data
- spot and USD-M support through a stable `Exchange` API
- notebook-based validation for market-data workflows

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

Agent-first repository harnessing is being added so documentation, architecture rules, and local verification become first-class repository features.

The harness is repo-local DX infrastructure. It lives in `scripts/` and is orchestrated by Poe; it is not modeled as an installed package CLI.

## Test Taxonomy

The test suite is being organized by test type at the top level:

- `tests/unit`
- `tests/integration`
- `tests/structure`
- `tests/smoke`

`unit` and `integration` mirror the source layout when a matching source package path exists. In the current pre-domain codebase, transitional domain-intent names such as `market_data` are still acceptable. `structure` owns repository-rule checks, and live/network-backed smoke validation stays out of the default test lane.

Live tests are explicit-only and excluded from the default `pytest` run.

Current examples:

- `tests/unit/market_data/...`
- `tests/integration/commands/...`
- `tests/structure/architecture/...`
- `tests/structure/docs/...`
- `tests/structure/repo/...`
- `tests/smoke/local/...`
- `tests/smoke/live/...`
