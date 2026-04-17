# Package Topology And Naming

## Status

- Status: `approved`
- Scope: package topology, naming, public facades, and topology-oriented
  terminology
- Role: governing design document for capability-first package structure and
  naming

Related documents:

- [quantcraft-architecture.md](quantcraft-architecture.md)
- [architecture-governance.md](architecture-governance.md)

## Why This Document Exists

`quantcraft` needs a durable answer to a different question than bounded-context
ownership alone:

- what should the package tree look like
- which names are preferred or forbidden
- where should public facades live
- how should agents tell engine code apart from product surfaces

This document fixes those answers for the capability-first v0 architecture.

## Default Topology

The default repository topology is:

```text
repo/
  pyproject.toml
  README.md
  ARCHITECTURE.md
  AGENTS.md
  docs/
  apps/
  src/
    quantcraft/
  tests/
  examples/
  notebooks/
```

Within `src/quantcraft`, use the capability contexts defined in
[quantcraft-architecture.md](quantcraft-architecture.md).
This document governs how those contexts should be named and packaged, not
their business ownership.

Rules:

- top-level package names should express capabilities or runtime contexts
- do not create repo-wide top-level `domain`, `application`, `adapters`, or
  `infrastructure` package trees
- keep packages shallow by default
- add deeper subpackages only when they improve navigation, not because a
  pattern looks symmetrical

## Engine Package Versus Product Surfaces

`src/quantcraft` is the installable engine and library package.

`apps/*` are product surfaces that compose the engine package for deployment.

Default interpretation:

- `apps/api` is an external product surface
- future `apps/web` is also an external product surface when it exists
- `src/quantcraft/cli` stays inside the package because CLI is a distributed
  package surface, not a separately deployed product

Do not let product surfaces become the owner of business semantics.

## Facades And Public API

Bounded contexts may expose a top-level `api.py` facade when it improves import
stability and keeps internal refactors local.

Allowed examples:

- `quantcraft.data.api`
- `quantcraft.trading.api`
- `quantcraft.backtest.api`
- `quantcraft.research.api`
- `quantcraft.execution.api`

Rules:

- `api.py` is for bounded-context facades, not every subdirectory
- do not duplicate `api.py` at every nesting level
- apps and CLI should prefer context facades over deep internal imports when
  those facades exist
- current public surface may remain small and partially experimental even when a
  facade exists

## Naming Rules

Prefer names that express domain responsibility directly:

- `engine.py`
- `execution_model.py`
- `broker.py`
- `orders.py`
- `positions.py`
- `analytics.py`

Avoid vague or sink-like names unless tightly justified:

- `core`
- `common`
- `utils`
- `helpers`
- `manager`
- `service`

Use asset-neutral naming in the core package:

- prefer `instrument` over `pair` or `coin`
- prefer `venue` over exchange-specific vocabulary when the concept is general
- prefer `account`, `position`, and `order` over crypto-only metaphors such as
  `wallet`

## `_shared` Policy

`_shared` is internal-only and should stay uncomfortable to use.

Allowed:

- narrow identifiers
- time helpers
- tiny typing helpers
- thin internal exceptions

Not allowed:

- orders
- fills
- positions
- risk rules
- result models
- venue-specific translation logic

If a concept has business meaning, move it back into its owning context.

## `integrations` Policy

`integrations` is the top-level boundary for external systems.

Typical examples:

- `integrations/venues/binance/...`
- `integrations/venues/bybit/...`
- `integrations/data_vendors/...`

Rules:

- keep venue or vendor protocol logic here
- separate market-data translation from trading or brokerage translation where
  practical
- do not let `integrations` become a second home for core domain models
- sibling integrations should stay independent unless an explicit shared helper
  is extracted

## Local Layering

Local layering is allowed when it improves clarity inside one context.

Examples:

- `research/indicators/runtime/`
- `integrations/venues/binance/...`

But local layering is a tool, not a global mandate.
Do not force every context into the same `domain / application / adapters`
subtree if a flatter structure is clearer.

## Steady-State Guidance

This topology is the standing package structure for the repository.

Local layering is still allowed when it materially improves clarity inside one
context, but it must remain local rather than turning back into a repo-wide
`domain / application / adapters` skeleton.
