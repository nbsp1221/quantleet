# Unified Strategy Runtime Design

## Status

- Status: `draft`
- Class: `design / decision record`
- Scope: strategy authoring UX, shared runtime model, and staged path from
  backtest to paper and live trading

Related documents:

- [../../AGENTS.md](../../AGENTS.md)
- [../../README.md](../../README.md)
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
- [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
- [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md)
- [../product-specs/paper-trading.md](../product-specs/paper-trading.md)
- [../product-specs/live-trading.md](../product-specs/live-trading.md)
- [../design-docs/backtest-execution-semantics.md](../design-docs/backtest-execution-semantics.md)
- [../RELIABILITY.md](../RELIABILITY.md)
- [../SECURITY.md](../SECURITY.md)

## Goal

Define the long-lived architecture direction for `quantleet` as a personal
quant framework that:

1. lets one strategy codebase move through research, backtest, paper trading,
   and live trading
2. supports both single-asset and multi-asset use cases
3. supports multi-strategy operation on one account
4. keeps strategy authoring ergonomics close to Pine Script where practical
5. does not force future runtime work to rewrite today's strategy API again

This document is not an implementation plan for the whole system.
It is a future-facing design baseline that later implementation plans may draw
from after explicit product-spec and migration work.

Because this document is still a `Draft`:

- it does not override the current shipped product specs
- it does not by itself change the public API
- it should be treated as long-lived design direction rather than active-plan
  workflow authority

## Product Intent

`quantleet` is not being designed primarily as a general-purpose open source
product for every user and every venue.

The primary intent is:

- a long-lived personal quant framework
- one coherent toolchain for strategy research, validation, and automated
  trading
- open source publication as a side effect rather than the main optimization

This matters because it changes what "success" means:

- deep internal coherence matters more than broad surface area
- a small number of well-supported venues matters more than universal exchange
  coverage
- strategy portability matters more than marketing-level feature breadth

## Current Reality

The current implemented repository scope remains much smaller than the target
end-state:

- current implemented focus: `data`, `research`, `backtest`
- current public backtest scope: single-symbol, long-only, market/limit orders
- paper and live trading are future planning surfaces, not implemented runtime
  systems

The design must therefore solve two different problems at once:

1. what the long-lived architecture should become
2. what should change now without breaking the current MVP

Those are not the same question.

## Core Problem

The immediate UX complaint is that `Strategy.buy()` and `Strategy.sell()`
currently require `symbol=...` even though the current product spec still
frames the public strategy workflow as a single-symbol backtest MVP.

That symptom points to a larger architectural question:

- should the public authoring DSL be shaped around the current single-asset UX
- or should it be shaped around the future multi-asset engine from day one

The answer in this design is:

- the public authoring DSL should optimize for current strategy authoring UX
- the internal engine model should optimize for future multi-asset runtime
  generality

In other words:

- the user-facing strategy language and the engine-facing execution model
  should not be treated as the same abstraction

## Design Principles

### 1. One Trading Kernel, Multiple Runtime Adapters

Backtest, paper, and live should share one core trading model:

- order state
- fills
- positions
- account and portfolio state
- risk checks
- execution lifecycle semantics where those can be shared

What changes by environment is:

- event source
- execution venue
- capability profile
- approximation quality

### 2. Easy Authoring Is A Surface Layer

Pine-like ergonomics are a product requirement, but they belong in the
authoring layer rather than the lowest engine contract.

The public DSL may therefore be simpler than the internal execution model.

### 3. Internal Models Must Carry Asset Identity Explicitly

Even if the public single-asset DSL lets the user omit `symbol`, the internal
runtime must keep explicit asset identity in:

- intents
- targets
- fills
- positions
- portfolio state

This is required for:

- multi-asset expansion
- multi-strategy coordination
- paper/live routing
- account-level risk decisions

### 4. Portability Means Shared Strategy Logic, Not Identical Outcomes

The framework should promise:

- same strategy logic across backtest, paper, and live
- same internal strategy output model
- same runtime pipeline shape

It should not promise:

- identical fills across all environments
- perfect live replication from OHLCV-only historical data

### 5. Account-Level Coordination Is Mandatory

As soon as one account can run:

- multiple strategies
- multiple assets
- or both

there must be an account-level coordinator that sits between strategies and
real order submission.

Strategies should not be the final authority for actual account orders.

## Recommended Architecture

The recommended long-lived runtime stack is:

```text
Strategy DSL
  -> Strategy Output Model
    -> Allocator / Portfolio Controller
      -> Risk Engine
        -> Execution Engine
          -> Runtime Adapter (backtest | paper | live)
```

### 1. Strategy DSL Layer

This is the user-facing layer optimized for readability and strategy authoring.

It should eventually include two distinct public authoring styles:

- `SingleAssetStrategy`
- `MultiAssetStrategy`

These should be treated as separate authoring DSLs, not as two completely
separate engines.

Current compatibility note:

- the currently shipped canonical public base class is
  `quantleet.strategy.Strategy`
- `quantleet.research.Strategy` remains a compatibility re-export until a later
  migration removes it
- if `SingleAssetStrategy` is introduced later, it should land through an
  explicit compatibility-preserving migration plan rather than as an immediate
  replacement of the shipped surface

#### `SingleAssetStrategy`

Primary purpose:

- Pine-like authoring for one active instrument or chart

Expected ergonomics:

- no mandatory `symbol=...` for common order helpers
- simple position view
- simple indicator binding
- clear `on_bar()` or equivalent per-instrument callback

Illustrative shape:

```python
class RsiStrategy(SingleAssetStrategy):
    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=14)

    def on_bar(self, bar) -> None:
        if qc.is_na(self.rsi[0]):
            return
        if not self.position.is_open and self.rsi[0] < 30:
            self.buy(quantity=1.0)
        elif self.position.is_open and self.rsi[0] > 70:
            self.sell(quantity=1.0)
```

This example is illustrative of the intended future single-asset authoring
shape. It is not a claim that the current shipped API already exposes
symbol-free `buy()` / `sell()`.

#### `MultiAssetStrategy`

Primary purpose:

- universe selection
- cross-asset logic
- portfolio construction
- ranking and allocation

This DSL should not pretend to be the same mental model as single-chart
trading.

Expected ergonomics:

- access to a market or universe snapshot
- ranking/filtering helpers
- asset-scoped data access
- target-based outputs rather than only imperative order helpers

Illustrative shape:

```python
class VolumeRsiBasket(MultiAssetStrategy):
    def on_market(self, market) -> None:
        candidates = [
            asset for asset in market.assets
            if asset.volume_spike > 3.0 and asset.rsi < 30
        ]

        if not candidates:
            self.target_weights({})
            return

        weight = 1.0 / len(candidates)
        self.target_weights({
            asset.symbol: weight
            for asset in candidates
        })
```

### 2. Strategy Output Model

This is the canonical internal bridge between user-facing strategy code and the
rest of the runtime.

This design recommends three output levels:

1. `Signal` level
   - simple directional intent
   - mostly useful for high-level research or DSL sugar
2. `Target` level
   - canonical standard for most strategies
   - examples:
     - target quantity
     - target exposure
     - target portfolio weights
3. `OrderProposal` level
   - advanced escape hatch
   - explicit order construction intent for workflows that genuinely need it

### Canonical Recommendation

The default and preferred internal standard should be:

- `Target`-oriented

Why:

- targets compose better across strategies
- targets are easier for allocation and risk systems to reason about
- targets map naturally to portfolio construction and rebalancing
- targets keep the strategy focused on "desired state" rather than immediate
  broker mechanics

`OrderProposal` should still exist, but as an advanced lower-level escape hatch
rather than the default strategy output.

Current compatibility note:

- the current shipped strategy contract still emits `OrderIntent`
- this draft does not retroactively redefine the current MVP contract
- adopting target-oriented outputs would require an additive migration path and
  coordinated updates to product specs, examples, and the runtime surface

### 3. Allocator / Portfolio Controller

This layer combines and resolves strategy outputs before account-level risk and
execution.

Responsibilities:

- combine outputs from multiple strategies
- enforce strategy budgets or sleeves
- resolve conflicting exposures
- turn target-level outputs into account-level desired state
- decide how much capital each strategy is effectively allowed to express

This layer should make both modes possible:

- isolated strategy sleeves
- shared account-level portfolio construction

But those should be policies, not separate engines.

### 4. Risk Engine

The risk engine should be account-scoped.

Ownership boundary:

- `trading` remains the owner of core risk semantics that should stay
  consistent across environments
- the account-scoped risk engine described here belongs to the future
  `execution` runtime layer
- it applies account, venue, and operational policy using the shared `trading`
  kernel rather than inventing a second source of trading truth

Responsibilities:

- kill switch
- maximum notional / leverage / position controls
- strategy-level caps
- symbol-level caps
- venue constraint enforcement
- emergency stop / trading halt
- approval, rejection, or clamping of allocator output

The risk engine answers:

- "is this allowed?"

not:

- "what alpha do we want?"

### 5. Execution Engine

This layer turns approved account-level instructions into actual order
lifecycle behavior.

Responsibilities:

- submit, amend, cancel, track orders
- manage partial fills and fills
- maintain runtime order state
- translate approved internal actions into venue-specific operations

The execution engine should be environment-aware but environment-agnostic at
the interface level.

### 6. Runtime Adapters

The runtime adapter provides the environment-specific reality:

- `backtest`
- `paper`
- `live`

#### Backtest

- historical data replay
- current MVP: OHLCV-derived synthetic execution events
- future stronger mode: tick or order-book replay where available

#### Paper

- real or near-real market data
- simulated fills
- no real fund movement

#### Live

- live market data
- real order submission
- real fills and venue state

The runtime adapter should change:

- event source
- execution realization
- capability profile

without changing:

- strategy DSL
- strategy output model
- account-level coordination pipeline

## Data And Replay Model

The current repository already encodes the correct long-lived boundary:

- `trading` owns matching and fills
- `backtest` owns historical approximation

That boundary should remain.

### Short-Term Backtest Reality

Near-term backtests may still rely on:

- OHLCV bars
- synthetic path generation
- conservative execution semantics

This is acceptable if it is treated honestly as approximation.

### Long-Term Research Direction

For stronger parity between research and live trading, the framework should
eventually support better historical replay sources where useful:

- trade-tick replay
- quote replay
- book or event replay

But the architecture must not depend on those richer feeds existing on day one.

## Capability Profiles

The framework should make runtime capability explicit.

Examples:

- backtest-ohlcv:
  - market orders
  - resting limits
  - synthetic touched-limit fills
- paper-exchange-x:
  - market, limit
  - trailing stop unsupported
- live-exchange-y:
  - stop-market supported
  - reduce-only required for certain flows

This must be machine-readable and enforced before live routing.

Unsupported behavior must fail fast rather than silently degrade.

## Multi-Strategy Operation

The design assumes multi-strategy operation on one account is a first-class
future requirement.

Therefore:

- strategy code should not directly own final account orders
- strategy outputs should flow through shared account coordination
- account-level risk and allocation are mandatory for live readiness

This is the difference between:

- "many backtests in one process"
- and
- "one actual account with many strategy programs"

The second case is the one this design optimizes for.

## What Should Change Now

This section exists to keep the design grounded in current scope.

The framework should **not** attempt to implement the full long-lived runtime
stack immediately.

### Immediate Priority

The first near-term follow-up should be a compatibility-preserving design and
implementation plan for the current public authoring surface.

That follow-up should be aligned with the current actual scope:

- current shipped public strategy workflow remains single-symbol
- internal engine models should still keep symbol identity
- any future single-asset-first DSL changes must be additive first

That means the immediate task is **not** to rewrite the shipped public API from
this draft alone.

The immediate task is to define a migration path such as:

- keep `quantleet.strategy.Strategy` as the shared shipped surface
- keep `quantleet.research.Strategy` only as a compatibility re-export
- optionally introduce a future `SingleAssetStrategy` as an additive alias or
  sibling
- preserve compatibility until product specs, examples, and runtime
  implementation all move together

### Explicitly Deferred

These should remain architecture targets rather than immediate implementation
requirements:

- `MultiAssetStrategy`
- allocator
- account-scoped risk engine
- paper trading runtime
- live trading runtime
- multi-strategy orchestration
- target-based portfolio controller

They should be designed now, but staged later.

## Rejected Alternatives

### 1. One Universal Strategy DSL For Everything

Rejected because:

- it will either make single-asset authoring too noisy
- or make multi-asset workflows too ambiguous
- or both

This is the most likely path to repeated API rewrites.

### 2. Make The Public DSL Match The Lowest Engine Contract

Rejected because:

- it would force current users to pay the complexity cost of future runtime
  generality
- it does not optimize for the current product promise

### 3. Split Backtest And Live Into Separate Strategy APIs

Rejected because:

- it breaks the core product intent of strategy-code portability
- it turns the framework into separate tools instead of one coherent system

## Recommended Staging

### Stage 1: Single-Asset Research / Backtest Foundation

- single-asset public strategy DSL
- no explicit `symbol` in common helpers
- internal symbol-bearing order/target model
- stronger research result and replay confidence

### Stage 2: Shared Runtime Skeleton

- canonical internal strategy output model
- capability profile system
- account controller skeleton
- paper runtime skeleton

### Stage 3: Account-Level Coordination

- allocator
- account-level risk engine
- multi-strategy orchestration
- target-based strategy outputs

### Stage 4: Multi-Asset Strategy Authoring

- explicit multi-asset DSL
- universe snapshot and ranking APIs
- portfolio-level target expressions

### Stage 5: Live Execution Hardening

- venue adapters
- real order lifecycle support
- kill switch and operational controls
- capability-gated live deployment checks
- explicit human approval gate before live order submission
- non-agent-autonomous live activation and supervision

## Final Decision

The framework should adopt the following long-lived design:

1. one shared trading/runtime kernel across backtest, paper, and live
2. separate user-facing authoring DSLs for single-asset and multi-asset work
3. one canonical internal strategy output model, with target-oriented outputs
   as the preferred standard
4. account-level allocation, risk, and execution between strategies and final
   order submission
5. immediate near-term focus on a clean single-asset public DSL that does not
   leak future multi-asset complexity into every strategy call

In short:

- keep the engine general
- keep today's public strategy authoring simple
- grow account coordination and multi-asset logic above the shared kernel
  instead of forcing them into the current single-asset UX prematurely
