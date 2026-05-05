# Backtest MVP

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope: the current implemented backtest baseline for the shared trading kernel

Related documents:

- [../design-docs/quantleet-architecture.md](../design-docs/quantleet-architecture.md)
- [../design-docs/backtest-execution-semantics.md](../design-docs/backtest-execution-semantics.md)
- [../design-docs/trading-kernel-contract-draft.md](../design-docs/trading-kernel-contract-draft.md)
- [../design-docs/architecture-governance.md](../design-docs/architecture-governance.md)
- [order-sizing.md](order-sizing.md)

This document is the canonical current implemented-scope contract for the shipped backtest MVP.

Conservative limit-order execution is implemented and governed by
[`../design-docs/backtest-execution-semantics.md`](../design-docs/backtest-execution-semantics.md).

## Goal

Build a deterministic single-symbol long-only backtest that:

- accepts OHLCV as the external stored format
- converts that data into a canonical backtest-only price path and synthetic executable events
- runs on the same tick/event-driven trading kernel that future paper and live environments will use

This MVP intentionally reduces feature scope without downgrading the core engine semantics.

## Included Scope

### Public Backtest Entry

The current preferred user-facing backtest entry lives in the `backtest` surface:

- `quantleet.backtest.BacktestEngine`

Approved current paths:

- `BacktestEngine(...).run(bars=..., strategy=...)`
- `BacktestEngine(...).run(source=..., strategy=...)`

`run_backtest(...)` is not part of the public surface in this slice.

Long-lived backtest runtime ownership is defined in the architecture docs, not
by this current public entry location.

### Data And Input

- single symbol
- single timeframe
- OHLCV as the external stored format
- canonical public data types:
  - `quantleet.data.TimeBar`
  - `quantleet.data.BarSeries`
- `BarSeries.rows` is `tuple[TimeBar, ...]`
- `BarSeries.bar_type` is fixed to `"time"` in this slice
- an OHLCV-to-synthetic-L2 adapter in the backtest path

Responsibility split:

- `data`: load, normalize, and provide `BarSeries`
- `backtest`: own historical runtime orchestration, synthetic execution-path construction, and backtest summarization
- `research`: expose the current user-facing strategy and backtest facade for this slice
- `trading`: process executable events, interpret orders, match fills, and apply state transitions

### Strategy Surface

- user-facing strategy API is `self`-based
- first public hook is `on_bar` only
- strategy output is a pending order request that resolves into a runtime
  `OrderIntent` at activation

MVP pending strategy-request minimum fields:

- `symbol`
- `side`
- exactly one of:
  - `quantity`
  - `qty_percent`
- `order_type`
- `stop_price?`
- `limit_price?`
- `tag?`

Runtime `OrderIntent` minimum fields:

- `symbol`
- `side`
- `quantity`
- `order_type`
- `trigger_price?`
- `trigger_condition?`
- `trigger_type?`
- `limit_price?`
- `tag?`

### Engine And Events

- internal engine remains `tick/event-driven`
- implemented event set for this slice:
  - `TickEvent`
  - `BarEvent`
  - `FillEvent`
  - `OrderRejectedEvent`
- deferred event types for this slice:
  - `OrderEvent`
  - `TimerEvent`
- `TickEvent` uses an `L2 snapshot` shape
- `BarEvent` is a general completed bar-aggregation event, not a time-bar-only event

`OrderEvent` and `TimerEvent` remain part of the longer-lived event model direction, but they are deferred for this MVP slice and must not appear in the current public trading surface. `OrderRejectedEvent` is intentionally narrower than a full order-event hierarchy: it records valid runtime/account failures that the backtest must expose rather than silently skipping.

MVP `BarEvent` minimum fields:

- `bar_type`
- `bar_spec`
- `symbol`
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `is_closed`

MVP `FillEvent` minimum fields:

- `symbol`
- `side`
- `quantity`
- `price`
- `timestamp`
- `fee`

Derived accounting values such as closing PnL do not belong in `FillEvent`. They are computed in position-application or reporting layers.

### Orders And Position Scope

- order types: `market`, `limit`, `stop_market`
- position scope: `long + flat`
- leverage: `1x`
- semantics: effectively spot-like for this slice

### Matching And Cost Inputs

- the engine must be able to process array-based depth and finite liquidity in general
- the first backtest input may use a simplified one-level book on each side
- the first backtest input may use conceptually unbounded liquidity
- the matching kernel consumes executable tick or book events only
- the matching kernel must not fabricate bar-aware fills on its own
- slippage is injected in ticks
- fees are injected as a percentage rate
- cost inputs come from configuration or market metadata, not hard-coded engine constants

### Outputs

- trade log
- position, balance, realized PnL, unrealized PnL, and equity updates
- simple summary statistics

Current summary semantics:

- the raw trade log is fill-level
- user-facing trade-count metrics should be interpreted as closed trades, not raw fills
- fee-aware trade statistics belong in the user-facing summary layer

## Excluded Scope

This MVP does not include:

- multi-symbol support
- multi-timeframe support
- shorting
- leverage or margin
- trailing or bracket orders
- cancel, modify, or replace flows
- user-visible partial-fill scenarios
- paper-trading runtime
- live-trading runtime
- multiple selectable fill-model families
- strategy optimization
- portfolio rebalancing

## Core Rules

### 1. Same Engine, Different Event Sources

Backtest is not a toy engine. It uses the same trading kernel.

What changes is the event source:

- backtest: historical data converted into synthetic events
- paper/live: real-time market data and real or simulated execution events

### 2. Bar UX, Tick Engine

The public MVP strategy surface is `on_bar`, but the engine stays tick/L2-driven internally.

This is a UX constraint, not an engine downgrade.

### 3. General Matching Logic

Even though the first user-visible experience uses effectively unbounded simplified books, the engine must already support:

- finite liquidity
- multi-level depth traversal
- later extension to partial fills without replacing the matching core

### 4. Injected Cost Model

The MVP uses a simple injected cost contract:

- `tick_size`
- `slippage_ticks`
- `fee_rate`

More advanced fee and slippage model objects may be added later, but they are not part of the MVP contract.

## Execution Semantics

### Strategy Timing

- `on_bar` is called only after the bar is complete
- a pending strategy request created inside that callback does not apply retroactively to the current bar
- by default, it becomes effective starting from the next bar

This is the slice's lookahead-bias guardrail.

### Synthetic Execution Path And Fill Rules

Detailed canonical path, gap handling, conservative limit behavior, and
traversal rules are governed by
[`../design-docs/backtest-execution-semantics.md`](../design-docs/backtest-execution-semantics.md).

This MVP adds the following slice-specific constraints on top:

- `market`, `limit`, and `stop_market` orders are in scope
- the strategy callback still runs after bar close, so newly emitted orders do
  not apply retroactively to the bar that created them
- `stop_market` orders activate on the next bar like other requests, remain
  dormant until their trigger condition is met on a causal synthetic
  executable point, and then fill through the ordinary market path on that
  same point
- in the current long-only slice, a `sell` intent while flat is treated as an exit-only no-op rather than as a short entry
- if finer-grained data becomes available later, the current default path model
  may be replaced by a more accurate one
- for same-bar child activation in future OTO-style flows, only the tail after
  the parent fill may be evaluated

## Reference UX Guidance

The first user-facing strategy model should stay close to familiar Python backtesting conventions:

- `backtesting.py`: `Strategy.next()` with `self.buy()` and `self.sell()`
- `backtrader`: `Strategy.next()` with `self.buy()` and `self.sell()`

That is why `quantleet` keeps a `self`-based strategy model even while aiming for Pine-like expressive goals.

## Acceptance Criteria

The slice is acceptable only if it satisfies all of the following:

1. it runs from checked-in OHLCV input for a single symbol
2. the engine remains tick/L2-driven internally
3. strategy code can emit pending order requests from a `self`-based `on_bar`
   hook, and runtime activation resolves them into runtime `OrderIntent`
4. `market`, `limit`, and `stop_market` orders work within the current slice
5. long-only, `1x`, spot-like semantics remain consistent
6. costs are externally injected
7. orders never fill retroactively into the bar that produced them
8. gaps are modeled as `prev_close -> open`, without intermediate gap-price fills
9. the run produces trade logs plus equity and PnL outputs
10. the resulting code path remains compatible with a shared future paper/live trading kernel

## Non-Blocking Deferred Questions

These topics do not block this MVP:

1. whether the in-memory representation of unbounded liquidity should be formally frozen as `inf`
2. how future trigger variants, trailing orders, and bracket orders should generalize gap handling and same-bar causality

These should be promoted only if they begin to create repeated ambiguity or correctness risk.

## Summary

This document defines the first implementation slice as a deterministic single-symbol long-only backtest built on the shared trading kernel, not as a separate bar-only simulation engine.
