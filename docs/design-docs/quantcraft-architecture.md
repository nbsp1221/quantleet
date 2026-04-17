# Quantcraft Architecture

## Status

- Status: `approved`
- Scope: top-level capability contexts, product-surface boundaries, dependency
  directions, and structural invariants
- Role: canonical design document for the repository's long-lived architecture

Related documents:

- [package-topology-and-naming.md](package-topology-and-naming.md)
- [architecture-governance.md](architecture-governance.md)
- [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
- [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md)

## Why This Document Exists

`quantcraft` is a long-lived, agent-first quant system.

It is expected to support:

- library use
- CLI use
- future API and UI surfaces
- research and alpha-search workflows
- deterministic backtesting
- paper and live execution

The repository therefore needs a stable answer to:

1. which top-level contexts own which responsibilities
2. which contexts are runtimes versus user ergonomics layers
3. how product surfaces relate to the engine package
4. which dependency directions are non-negotiable

This document fixes those answers.

## Architectural Baseline

The approved long-lived baseline is:

- one installable engine package under `src/quantcraft`
- capability-first top-level package ownership
- one shared trading kernel
- separate runtime contexts for `backtest` and `execution`
- product surfaces outside the engine package when deployment concerns differ
- agent-legible boundaries backed by future mechanical checks

This is the architectural truth that current code and future package work must
preserve.

## Engine Package And Product Surfaces

The repository distinguishes between two axes:

### 1. Engine Package

`src/quantcraft` contains the installable engine and library package.

This is where the durable business semantics live.

### 2. Product Surfaces

`apps/*` contain deployed product surfaces that compose the engine package.

Initial direction:

- `apps/api`: approved product-surface direction
- `apps/web`: possible future product surface when it actually exists

`src/quantcraft/cli` remains part of the packaged engine because CLI is a
distributed library surface, not a separately deployed product.

## Top-Level Contexts

The approved engine-package contexts are:

1. `data`
2. `trading`
3. `research`
4. `backtest`
5. `execution`
6. `integrations`

Cross-cutting support remains intentionally narrow:

- `_shared`

Adjacent future-only areas may be introduced later:

- `ml`

## Context Responsibilities

### `data`

`data` owns normalized data concepts and data workflows:

- bars, ticks, books, and related normalized contracts
- cataloging, replay, transforms, caching, and loading
- macro or market data delivery in normalized form

It must not own:

- strategy logic
- order generation
- position or portfolio state transitions
- venue-specific protocol code

### `trading`

`trading` is the shared trading kernel.

It owns:

- orders, fills, positions, balances, and portfolios
- state transitions
- fill application rules
- PnL and cost semantics
- core risk semantics that should remain consistent across environments

It must not own:

- backtest-only path fabrication
- live venue sessions
- exchange or broker client wiring
- notebook, API, or CLI composition

### `research`

`research` owns strategy authoring and research ergonomics:

- strategy APIs
- indicators
- analytics and alpha-search helpers
- optimization or experiment-facing tooling

It must not invent a second trading semantics layer.

It may compose `backtest`, but it does not own the historical execution runtime.

### `backtest`

`backtest` owns historical execution runtime concerns:

- backtest engine orchestration
- historical event-source construction
- synthetic execution-path construction
- backtest reporting and backtest-only fill-model concerns

It must use the shared `trading` kernel.

It must not become a second strategy ergonomics surface.

### `execution`

`execution` owns paper and live runtime control:

- order routing
- broker or venue runtime control
- paper-trading supervision
- live session supervision

It must use the shared `trading` kernel.

### `integrations`

`integrations` owns external system translation:

- venue adapters
- broker adapters
- data-vendor adapters
- raw HTTP, websocket, auth, and mapping code

It translates external protocols into internal contracts.
It does not own core trading, research, or backtest semantics.

### `_shared`

`_shared` is internal-only and must stay tiny.

It exists for mechanical cross-cutting support, not business meaning.

## Structural Principles

### 1. Capability-First Topology

Top-level package names should answer "what responsibility lives here?" rather
than "which architectural layer is this?".

That is why the architecture uses contexts such as:

- `trading`
- `backtest`
- `execution`
- `integrations`

rather than a repo-wide `domain / application / adapters` directory tree.

### 2. Shallow By Default

Package depth should remain shallow unless deeper grouping clearly improves
navigation.

Local layering is allowed when useful, but it is not a global naming mandate.

### 3. One Trading Meaning

Backtest, paper, and live should share one trading meaning as much as possible.

Environment-specific differences belong in:

- event sources
- runtime orchestration
- integrations

not in duplicated trading kernels.

### 4. Product Surfaces Compose The Engine

APIs, CLIs, and future UIs should compose the engine package.
They must not quietly become a second home for core business logic.

### 5. Agent Legibility Matters

The repository is optimized for long-lived human and agent navigation.

That means:

- explicit context ownership
- few sink folders
- short entry docs that point to deeper authority
- future mechanical checks for declared boundaries

## Dependency Rules

The approved dependency directions are:

- `backtest -> data`
- `backtest -> trading`
- `research -> data`
- `research -> trading`
- `research -> backtest` through public backtest surfaces
- `execution -> trading`
- `execution -> data` only for normalized contracts when needed
- `execution -> integrations`
- `data -> integrations` only for provider-facing translation or loading seams

Never allowed:

- `trading -> research`
- `trading -> backtest`
- `trading -> execution`
- `trading -> integrations`
- `backtest -> execution`
- deep cross-context imports that bypass an owned public surface without an
  explicit exception

Additional constraints:

- `integrations` should not absorb core business concepts
- sibling integrations should remain independent unless an explicit shared
  helper is extracted
- `_shared` must not absorb orders, fills, positions, backtest reports, or risk
  rules

## Steady-State Guidance

The approved capability-first structure is the standing architectural authority
for the repository.

Current local layering choices such as `trading/domain` are intentional,
context-local structure, not a return to a repo-wide layer-first skeleton.

When behavior contracts and architecture concerns differ:

- product specs define the shipped behavior
- this document defines package ownership and dependency direction
- implementation plans should record temporary exceptions explicitly instead of
  silently widening a context boundary
