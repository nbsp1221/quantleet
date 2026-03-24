# Backtest MVP

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope: the current implemented backtest baseline for the shared trading kernel

Related documents:

- [../design-docs/quantcraft-architecture.md](../design-docs/quantcraft-architecture.md)
- [../design-docs/trading-kernel-contract-draft-ko.md](../design-docs/trading-kernel-contract-draft-ko.md)
- [../design-docs/architecture-governance.md](../design-docs/architecture-governance.md)

This document is the canonical current implemented-scope contract for the shipped backtest MVP.

## Goal

Build a deterministic single-symbol long-only backtest that:

- accepts OHLCV as the external stored format
- converts that data into a synthetic L2 tick stream
- runs on the same tick/event-driven trading kernel that future paper and live environments will use

This MVP intentionally reduces feature scope without downgrading the core engine semantics.

## Included Scope

### Data And Input

- single symbol
- single timeframe
- OHLCV as the external stored format
- an OHLCV-to-synthetic-L2 adapter in the backtest path

Responsibility split:

- `data`: load, normalize, and provide OHLCV
- `research`: orchestrate the backtest, convert OHLCV into synthetic events, and summarize results
- `trading`: process events, interpret orders, match fills, and apply state transitions

### Strategy Surface

- user-facing strategy API is `self`-based
- first public hook is `on_bar` only
- strategy output is `OrderIntent`

MVP `OrderIntent` minimum fields:

- `symbol`
- `side`
- `quantity`
- `order_type`
- `limit_price?`
- `tag?`

### Engine And Events

- internal engine remains `tick/event-driven`
- implemented event set for this slice:
  - `TickEvent`
  - `BarEvent`
  - `FillEvent`
- deferred event types for this slice:
  - `OrderEvent`
  - `TimerEvent`
- `TickEvent` uses an `L2 snapshot` shape
- `BarEvent` is a general completed bar-aggregation event, not a time-bar-only event

`OrderEvent` and `TimerEvent` remain part of the longer-lived event model direction, but they are deferred for this MVP slice and must not appear in the current public trading surface.

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

- order types: `market`, `limit`
- position scope: `long + flat`
- leverage: `1x`
- semantics: effectively spot-like for this slice

### Matching And Cost Inputs

- the engine must be able to process array-based depth and finite liquidity in general
- the first backtest input may use a simplified one-level book on each side
- the first backtest input may use conceptually unbounded liquidity
- slippage is injected in ticks
- fees are injected as a percentage rate
- cost inputs come from configuration or market metadata, not hard-coded engine constants

### Outputs

- trade log
- position, balance, realized PnL, unrealized PnL, and equity updates
- simple summary statistics

## Excluded Scope

This MVP does not include:

- multi-symbol support
- multi-timeframe support
- shorting
- leverage or margin
- stop, stop-limit, trailing, or bracket orders
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
- `OrderIntent` created inside that callback does not apply retroactively to the current bar
- by default, it becomes effective starting from the next bar

This is the slice's lookahead-bias guardrail.

### Market And Limit Semantics

- `market` consumes opposite-side liquidity at the first executable price, with adverse slippage applied
- `limit` may only fill at a price no worse than the limit price
- under the simplified MVP liquidity model, a `limit` may appear as an at-limit fill in practice

### Gap Semantics

Treat `prev_close -> open` as a distinct price-movement segment.

Rules:

- no fills at intermediate gap prices
- `open` is the first executable price of the next bar
- a `market` order may therefore fill at `open`
- future trigger-style orders should reuse this same segment model

## Synthetic Tick Generation

The backtest path converts OHLCV into a synthetic L2 tick stream.

Allowed:

- lazily materializing or skipping synthetic path generation when no order needs evaluation

Not allowed:

- changing the path in an order-dependent way to make an order fill

In short:

- lazy generation is allowed
- order-dependent path fabrication is forbidden

## Intrabar Ambiguity

OHLCV does not reveal the true intrabar path.

The slice therefore uses a fixed conservative path rule:

- bullish bar: `open -> low -> high -> close`
- bearish bar: `open -> high -> low -> close`

The rule must not change dynamically to favor order outcomes.

If finer-grained data becomes available later, a more accurate model may replace this slice default.

For same-bar child activation in future OTO-style flows, only the tail after the parent fill may be evaluated.

## Reference UX Guidance

The first user-facing strategy model should stay close to familiar Python backtesting conventions:

- `backtesting.py`: `Strategy.next()` with `self.buy()` and `self.sell()`
- `backtrader`: `Strategy.next()` with `self.buy()` and `self.sell()`

That is why `quantcraft` keeps a `self`-based strategy model even while aiming for Pine-like expressive goals.

## Acceptance Criteria

The slice is acceptable only if it satisfies all of the following:

1. it runs from checked-in OHLCV input for a single symbol
2. the engine remains tick/L2-driven internally
3. strategy code can emit `OrderIntent` from a `self`-based `on_bar` hook
4. `market` and `limit` orders both work
5. long-only, `1x`, spot-like semantics remain consistent
6. costs are externally injected
7. orders never fill retroactively into the bar that produced them
8. gaps are modeled as `prev_close -> open`, without intermediate gap-price fills
9. the run produces trade logs plus equity and PnL outputs
10. the resulting code path remains compatible with a shared future paper/live trading kernel

## Non-Blocking Deferred Questions

These topics do not block this MVP:

1. whether the in-memory representation of unbounded liquidity should be formally frozen as `inf`
2. how future stop and trigger orders should generalize gap handling and same-bar causality

These should be promoted only if they begin to create repeated ambiguity or correctness risk.

## Summary

This document defines the first implementation slice as a deterministic single-symbol long-only backtest built on the shared trading kernel, not as a separate bar-only simulation engine.
