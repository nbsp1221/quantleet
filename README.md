# quantcraft

`quantcraft` is a quant library and framework that will grow across market data, research tooling, backtesting, paper trading, live trading, and quant-related ML utilities.

The long-lived repository direction is a capability-first engine package under
`src/quantcraft`, with product surfaces such as an API server living outside the
core package when they arrive.
The current codebase follows that package topology, while some future-facing
contexts remain intentionally minimal.

The current implemented scope is intentionally small:

- typed exchange access for OHLCV market data
- spot and USD-M support through the current `quantcraft.integrations.venues.ccxt` exchange API
- a first `quantcraft.data` ingestion surface with `CCXTDataSource`, `CSVDataSource`, `DataFrameDataSource`, `TimeBar`, and `BarSeries`
- automatic historical pagination inside `CCXTDataSource.load()` for exchange-backed range assembly
- `source.load()` materialization into `BarSeries` with `tuple[TimeBar, ...]` rows and `bar_type="time"`
- a deterministic single-symbol Backtest MVP built on the shared trading kernel
- a first `quantcraft.research` ergonomics surface with `Strategy`, `ta`, and `qc`
- a first `quantcraft.backtest` runtime surface with `BacktestEngine`
- canonical backtest execution paths via `BacktestEngine.run(bars=..., strategy=...)` and `BacktestEngine.run(source=..., strategy=...)`
- canonical quickstart and notebook assets for the current research workflow

## Initial Canonical User Journeys

These journeys are the first frozen library-consumption paths for both human users and AI agents.

They exist to anchor docs, examples, reviews, and later automation to real use of the public library surface.
They are not automatically equivalent to strict merge gates.

### 1. Clean Install To Public Imports

- starting state: a fresh environment with the built package artifact or synced repository environment
- user intent: confirm the package installs cleanly and exposes the documented public API
- success artifact: importing `BacktestEngine`, `Strategy`, `ta`, `qc`, `BarSeries`, `TimeBar`, and the documented data sources from their documented capability paths works exactly as the docs imply
- superficially passing but still bad: the package builds, but documented imports or import paths drift

### 2. DataFrame-Like Quickstart To First Backtest

- starting state: the canonical `DataFrameDataSource` quickstart path
- user intent: reach a first successful backtest with minimal setup
- success artifact: the documented quickstart flow runs and produces a `BacktestResult`
- superficially passing but still bad: the example only works with hidden setup or undocumented assumptions

### 3. Materialized `BarSeries` To `engine.run(bars=...)`

- starting state: user-created `TimeBar` and `BarSeries` values
- user intent: run the engine from explicit materialized historical bars
- success artifact: `BacktestEngine.run(bars=..., strategy=...)` works with the documented canonical types
- superficially passing but still bad: the path only works because code or docs silently rely on lower-layer internals

### 4. Exchange-Backed Historical Research Flow

- starting state: the documented `CCXTDataSource` historical path
- user intent: load historical bars and run a real research workflow through `engine.run(source=...)`
- success artifact: the documented exchange-backed flow remains coherent and reproducible enough for humans and agents to follow
- superficially passing but still bad: the path stays "documented" but becomes too hidden, flaky, or environment-dependent to serve as a trustworthy reference workflow

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
uv run python scripts/coverage_check.py
uv build
uv run python scripts/repo_check.py
uv run python scripts/notebook_validate.py
uv run python scripts/live_smoke.py
```

## Current Verification Surface

The repository currently relies on:

- unit tests
- integration tests
- explicit performance regression checks
- structure and repo-rule checks
- static analysis
- packaging checks
- notebook validation

The default integration surface keeps a deliberately small canonical strategy pair:

- `RSI 30/70 mean reversion`
- `EMA crossover`

This keeps the default lane representative without turning it into a slow “many strategies” suite.
Additional deterministic strategy regression contracts can stay in the normal integration suite
as long as they remain cheap and legible.

For day-to-day development, use the Poe task layer:

- `uv run poe lint`
- `uv run poe format`
- `uv run poe perf-check`
- `uv run poe typecheck`
- `uv run poe test`
- `uv run poe test-unit`
- `uv run poe test-integration`
- `uv run poe test-structure`
- `uv run poe test-smoke`
- `uv run poe test-live`
- `uv run poe coverage`
- `uv run poe build`
- `uv run poe repo-check`
- `uv run poe notebook-validate`
- `uv run poe live-smoke`
- `uv run poe verify`
- `uv run poe verify-runtime`

For runtime-sensitive changes, also run the explicit performance lane:

- `uv run poe perf-check`
- `uv run poe verify-runtime`

Agent-first repository harnessing keeps documentation, architecture rules, and local verification as first-class repository features.

The harness is repo-local DX infrastructure. It lives in `scripts/` and is orchestrated by Poe; it is not modeled as an installed package CLI.

## Test Taxonomy

The test suite is being organized by test type at the top level:

- `tests/unit`
- `tests/integration`
- `tests/perf`
- `tests/structure`
- `tests/smoke`

`unit` and `integration` mirror the source layout when a matching source package
path exists. `structure` owns repository-rule checks, and live/network-backed
smoke validation stays out of the default test lane.

Live tests are explicit-only and excluded from the default `pytest` run.

Current examples:

- `tests/unit/integrations/...`
- `tests/integration/commands/...`
- `tests/structure/architecture/...`
- `tests/structure/docs/...`
- `tests/structure/repo/...`
- `tests/smoke/local/...`
- `tests/smoke/live/...`
