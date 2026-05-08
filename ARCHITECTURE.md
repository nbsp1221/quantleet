# Architecture

`quantleet` is a local-first quant library and framework that is expected to
grow from market-data utilities into research, backtesting, paper trading, live
trading, and quant-related ML tooling.

## Current Truth

The repository's approved long-lived direction is a capability-first v0
architecture.

That means:

- the installable engine and library live under `src/quantleet`
- future product surfaces such as `apps/api` live outside the engine package
- top-level package ownership is organized by capability and runtime context,
  not by a repo-wide `domain / application / adapters` skeleton

The current codebase now largely matches this package topology. These docs
define the standing architecture that future package work must preserve and
extend.

## Top-Level Contexts

The approved engine-package contexts are:

- `data`
- `trading`
- `research`
- `strategy`
- `backtest`
- `execution`
- `integrations`

Cross-cutting support remains intentionally narrow:

- `_shared`

Adjacent future-only areas may be introduced later:

- `ml`

## Product Surfaces

The repository distinguishes between:

- `src/quantleet`: the installable engine and library package
- `apps/*`: product surfaces that compose the engine package for deployment
- `src/quantleet/cli`: the packaged CLI surface, because it ships with the
  library

Do not treat product surfaces as owners of core business semantics.
They compose the engine package; they do not redefine it.

## Safety Tiers

- Tier A: `trading`, `execution`
- Tier B: `data`, `research`, `strategy`, `backtest`
- Tier C: `ml`, notebooks, generated docs

`integrations` inherit the safety expectations of the context they serve.
Execution-side integrations should be reviewed with Tier A scrutiny; data-side
integrations should be reviewed with Tier B scrutiny unless they can create
exposure or move funds.

## Structural Principles

- organize top-level packages by capability and runtime context
- keep internal package depth shallow by default
- use local subpackages only when they materially improve legibility
- do not require every context to expose `domain`, `application`, and
  `adapters` subdirectories
- use `api.py` only for bounded-context facades, not as a file-naming ritual
- keep `_shared` tiny and mechanical
- prefer asset-neutral names such as `instrument`, `venue`, `account`,
  `position`, and `order`

## Dependency Rules

- `trading` is the shared trading kernel
- `trading` must not depend on `research`, `backtest`, `execution`,
  `integrations`, `cli`, or `apps/*`
- `data` owns normalized market and macro data contracts and must not absorb
  strategy or trading-state semantics
- `strategy` owns the shared strategy authoring and configuration contract
  used by research, backtest, and future execution workflows; it may depend on
  `trading` but must not depend on `research`, `backtest`, or `execution`
- `backtest` owns historical execution runtime concerns and may depend on
  `data`, `trading`, and `strategy`
- `research` owns strategy authoring, indicators, analytics, and alpha-search
  ergonomics; it may depend on `data`, `trading`, `strategy`, and the public
  `backtest` surface
- `execution` owns paper/live runtime control and may depend on `trading`,
  normalized data contracts, `strategy`, and concrete integrations
- `integrations` translate external systems into internal contracts; they do not
  own core trading or research semantics
- sibling contexts should prefer public facades such as `quantleet.<context>.api`
  over deep internal imports when those facades exist

## Steady-State Guidance

The approved long-lived authority remains the capability-first topology
described here and in the linked design docs.

Use the docs below when extending or policing that package structure:

- [`docs/design-docs/quantleet-architecture.md`](docs/design-docs/quantleet-architecture.md)
- [`docs/design-docs/package-topology-and-naming.md`](docs/design-docs/package-topology-and-naming.md)
- [`docs/design-docs/index.md`](docs/design-docs/index.md)

Current implemented-scope behavior remains governed by the product specs:

- [`docs/product-specs/backtest.md`](docs/product-specs/backtest.md)
- [`docs/product-specs/research-ergonomics.md`](docs/product-specs/research-ergonomics.md)
