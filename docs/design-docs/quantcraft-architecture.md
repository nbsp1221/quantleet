# Quantcraft Architecture

## Status

- Status: `approved`
- Scope: top-level bounded contexts, layer model, dependency directions, and structural invariants
- Role: canonical design document for the repository's long-lived architecture

This document defines the approved architectural baseline that agents are expected to follow.

## Why This Document Exists

`quantcraft` is not trying to freeze every future package detail up front. The goal is to lock in the boundaries and invariants that agents must not violate while the implementation grows.

Two requirements drive the architecture:

1. Backtest, paper trading, and live trading must share as much trading semantics as possible.
2. The repository must stay legible and enforceable for agent-first development.

The result is a bounded-context architecture with strict separation between domain logic, orchestration, and external adapters.

## Top-Level Bounded Contexts

The approved top-level bounded contexts are:

1. `data`
2. `trading`
3. `research`
4. `execution`

Two adjacent areas remain intentionally separate:

- `shared`: very small cross-cutting support only
- `ml`: future adjacent area to be evaluated after the core four contexts stabilize

## Context Responsibilities

### `data`

`data` owns acquisition, normalization, storage, caching, and delivery of market and macro data.

It must not own:

- strategy logic
- order generation
- position or portfolio state transitions
- fill processing

### `trading`

`trading` is the shared trading kernel.

It owns:

- order, fill, position, balance, and portfolio domain models
- the core semantics of `risk` and `portfolio`
- state transitions
- fill application rules
- PnL rules
- cost and price-application interfaces

It must not own:

- exchange API calls
- websocket session management
- database persistence wiring
- CLI or notebook runtime wiring

### `research`

`research` owns strategy authoring, backtest orchestration, analysis, reporting, and experiments.

It must not invent a second trading semantics layer. It must use the `trading` kernel.

### `execution`

`execution` owns paper and live runtime control:

- venue sessions
- order submission
- live event loops
- execution-response handling

It must not invent a second trading semantics layer. It must use the `trading` kernel.

## Layer Model

Bounded contexts and layers are different axes.

Each implemented context should follow this internal structure:

- `domain`
- `application`
- `adapters`

Illustrative layout:

```text
src/quantcraft/
  data/
    domain/
    application/
    adapters/
  trading/
    domain/
    application/
    adapters/
  research/
    domain/
    application/
    adapters/
  execution/
    domain/
    application/
    adapters/
  shared/
```

### `domain`

Owns pure business logic:

- entities
- value objects
- policies
- state transitions

Must not depend on:

- exchange APIs
- databases
- file I/O
- websocket sessions

### `application`

Owns orchestration:

- use cases
- flow control
- port calls
- multi-object coordination

Examples:

- run a backtest once
- evaluate a strategy and emit order intent
- coordinate a data collection pipeline

### `adapters`

Own external integration:

- exchanges
- files
- databases
- caches
- runtime wiring
- CLI and notebook entrypoints

## Core Architectural Principles

### 1. `trading` is the shared trading kernel

The following must be shared across environments as much as possible:

- order semantics
- fill semantics
- position semantics
- portfolio semantics
- state transitions
- core risk rules
- interpretation from order intent to trading state changes

Environment-specific differences belong in adapters and event sources, not in duplicated trading logic.

### 2. Avoid optimistic split implementations

Do not create separate optimistic kernels such as:

- a backtest-only order state machine
- a live-only position engine
- a paper-only fill application layer

Those splits undermine the requirement that backtest, paper, and live should share one trading meaning as much as possible.

### 3. `shared` must stay small

`shared` is not a dumping ground.

Allowed examples:

- basic time types
- narrow identifiers
- thin shared exceptions
- generic helpers with almost no business meaning

Not allowed in `shared`:

- orders
- positions
- fills
- risk rules
- backtest result models

## Dependency Rules

The approved dependency directions are:

- `research -> data`
- `research -> trading`
- `execution -> trading`
- never the reverse

Additional constraints:

- `data` stays focused on data acquisition and normalization
- `research -> data` is allowed narrowly for normalized historical data contracts and ingestion paths; it is not a general license for `research` to absorb `data` internals
- `shared` must not absorb business concepts
- temporary exceptions must be documented where the exception is introduced

## Current Repository State

The current codebase now includes:

- exchange-backed market-data utilities
- an implemented Backtest MVP
- an implemented first `research` ergonomics surface on top of that backtest baseline

That does not change the architectural baseline above. It means the long-lived architecture remains ahead of the final package shape even though the first current-scope `research` and `trading` surfaces are now implemented.

## Relationship To Other Documents

This document defines the approved top-level architecture only.

It does not replace:

- [trading-kernel-contract-draft-ko.md](trading-kernel-contract-draft-ko.md): long-lived trading-kernel contract draft
- [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md): canonical current implemented-scope backtest baseline
- [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md): canonical current implemented-scope research usability surface
- [architecture-governance.md](architecture-governance.md): approved harness and promotion policy
