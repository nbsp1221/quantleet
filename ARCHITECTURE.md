# Architecture

`quantcraft` is a local-first quant library and framework that is expected to grow from market-data utilities into research, backtesting, paper trading, live trading, and quant-related ML tooling.

## Domain Map

Current top-level bounded contexts:

- `data`
- `trading`
- `research`
- `execution`

Cross-cutting support remains intentionally narrow:

- `shared`

Future adjacent areas may be introduced later after the core four contexts stabilize:

- `ml`

The repository remains a single Python package for now, but it should be organized so the core bounded contexts can later be extracted without changing the conceptual boundaries.

## Safety Tiers

- Tier A: `trading`, `execution`
- Tier B: `data`, `research`
- Tier C: `ml`, notebooks, generated docs

Tier A domains are high-scrutiny financial areas and require stronger human gate and stronger verification.

## Layer Model

Each implemented domain should eventually follow this internal layering model:

- `domain`
- `application`
- `adapters`

Shared support belongs in explicitly named cross-cutting areas only:

- `shared`

## Dependency Rules

- `research` may depend on `trading`, but `trading` must not depend on `research`.
- `execution` may depend on `trading`, but `trading` must not depend on `execution`.
- `data` must stay focused on data acquisition and normalization, not trading state transitions.
- Shared helpers belong in explicit shared modules, not random utility files.
- `shared` must remain very small and must not become a sink for business concepts like orders, positions, or risk rules.
- Temporary exceptions must be documented near the rule that permits them.

## Current State

The current codebase is still in a pre-domain state centered on exchange-backed market data. The harness setup adds the repository rules and document system before broader domain expansion.

The current approved top-level architecture is tracked in:

- [`docs/design-docs/quantcraft-architecture.md`](docs/design-docs/quantcraft-architecture.md)

Related design and slice-level documents are indexed in:

- [`docs/design-docs/index.md`](docs/design-docs/index.md)

The current approved architecture fixes the following top-level decisions:

- `trading` is the shared trading kernel for backtest, paper trading, and live trading
- `portfolio` and `risk` semantics belong with the `trading` kernel
- each bounded context should follow `domain / application / adapters` internally
- dependency direction remains:
  - `research -> trading`
  - `execution -> trading`
  - never the reverse
- `shared` remains intentionally small and must not absorb business concepts

Active trading-kernel and slice-level contract details are tracked separately:

- [`docs/design-docs/trading-kernel-contract-draft-ko.md`](docs/design-docs/trading-kernel-contract-draft-ko.md): long-lived trading-kernel contract draft
- [`docs/product-specs/backtest.md`](docs/product-specs/backtest.md): current backtest product-spec entry

## Test Layout

The repository uses a type-first test taxonomy:

- `tests/unit`
- `tests/integration`
- `tests/structure`
- `tests/smoke`

Rules:

- `tests/unit` and `tests/integration` mirror the source layout once a matching source package path exists
- `tests/structure` owns repository, architecture, and docs checks
- `tests/smoke/live` is explicit-only and excluded from the default `pytest` lane

## Command Surface

The repository keeps two explicit command layers:

- repo-local harness scripts under `scripts/`
- `tool.poe.tasks` for high-level local developer workflows such as `verify`, `lint`, and `format`

Poe tasks must orchestrate the documented repo-local workflow rather than hide a second command contract inside the package.
