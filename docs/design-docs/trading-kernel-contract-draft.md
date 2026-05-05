# Quantcraft Trading Kernel Contract Draft v1

## Status

- Status: `draft`
- Purpose:
  future-only working draft for the long-lived shared semantics of the
  `trading` kernel
- Scope:
  candidate trading semantics and unresolved questions that backtest, paper,
  and live could eventually share

## How To Read This Document

This is **not** the canonical document for current implemented behavior.

- The currently implemented backtest behavior is governed by
  [`../product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md).
- The currently implemented research ergonomics surface is governed by
  [`../product-specs/research-ergonomics.md`](../product-specs/research-ergonomics.md).
- Top-level structure and boundaries are governed by
  [`quantleet-architecture.md`](quantleet-architecture.md).

So this document is a **future-only draft**, not the current contract that
should immediately change implementation.

## Why This Lives In A Separate Document

Top-level architecture and trading-kernel contract are different things.

- Architecture docs describe boundaries and responsibility ownership.
- This document talks about trading-kernel-specific contracts such as strategy
  output, event shapes, and the long-lived relationship between backtest and
  the shared kernel.

If these stay mixed together, agents can confuse:

- top-level structure
- current implemented contracts
- future shared trading contracts

as though they were equally authoritative.

## Core Principles For Shared Trading Semantics

### 1. All three environments should share one trading kernel

Backtest, paper trading, and live trading should not become separate trading
engines.

They should be different input environments for the same trading kernel.

What should be shared:

- interpretation of trading decisions
- execution semantics
- position / balance / portfolio state transitions
- core risk semantics
- event ordering

### 2. `portfolio` and `risk` belong to the `trading` kernel

These are not only `execution` concerns. They are part of shared trading
semantics.

Why:

- backtest and live results should sit on the same semantic foundation
- if portfolio and risk interpretation change by environment, that goal breaks

### 3. The engine is `tick/event-driven` internally

Even if strategy authoring supports `on_bar`, the engine itself should remain
event-driven rather than becoming a bar-native engine.

In other words:

- internal engine: `tick/event-driven`
- user strategy interface: `on_tick`, `on_bar`

## Strategy Contract

### Strategy output is `OrderIntent`

Strategy should not emit only an abstract `Signal`.
It should reach the level of order intent.

At minimum, strategy should be able to express:

- entry / exit intent
- direction
- quantity intent
- order-related intent

But actual order-state transitions, execution application, and
balance/position updates still belong to the `trading` kernel.

The current narrow backtest MVP uses these minimal fields:

- `symbol`
- `side`
- `quantity`
- `order_type`
- `limit_price?`
- `tag?`

### The strategy interface stays `self`-based

The user-facing API should stay `self`-based rather than becoming `ctx`-based.

Expected feel:

- `self.trade.entry(...)`
- `self.trade.exit(...)`

Internally, runtime context and engine state may still live on separate
objects, but the user contract should remain `self`-based.

### Strategies may expose `on_tick` and `on_bar`

Strategies may eventually support:

- `on_tick`
- `on_bar`

Again, those are user-facing callback shapes.
The internal engine remains `tick/event-driven`.

## Initial Canonical Event Set

The current future-facing `v1` candidate event set is this minimal group:

- `TickEvent`
- `BarEvent`
- `OrderEvent`
- `FillEvent`
- `TimerEvent`

Under the current narrow backtest MVP, `FillEvent` has these minimal fields:

- `symbol`
- `side`
- `quantity`
- `price`
- `timestamp`
- `fee`

Derived accounting values such as closing PnL should not live on `FillEvent`.
They should be computed downstream in the position/reporting layer.

Under the current draft baseline, `BarEvent` is interpreted as a closed general
bar-aggregation event rather than a TimeBar-only event.

The baseline fields are:

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

This draft does **not** yet standardize the following as formal kernel events:

- `SignalEvent`
- `RiskEvent`
- `PortfolioEvent`
- `PositionEvent`

## Canonical `TickEvent` Shape

In `v1`, `TickEvent` uses an `L2 snapshot` as the candidate canonical shape.

Minimum information:

- `timestamp`
- `symbol`
- `bids[]`
- `asks[]`
- `last`
- `last_size?`

Why:

- it naturally represents realtime order books
- it supports quote-aware paper-trading execution modeling
- backtests can degrade it to a simple one-level book on each side

## How Backtest Connects To The Engine

Backtest should not become a separate trading engine.

Instead, it should feed different input events into the same engine.

So:

- `live / paper`
  - feed realtime market events and real/virtual execution events
- `backtest`
  - generate synthetic tick/event inputs from historical data

OHLCV can still be a stored backtest input source, but the engine’s final
execution unit should remain event/tick based.

## Current Backtest MVP Agreement

The initial implementation slice is still a backtest MVP.
But that MVP should be the first vertical slice of the shared trading kernel,
not a bar-native toy engine.

Current agreement:

- external storage format starts with `OHLCV`
- a backtest adapter converts `OHLCV -> synthetic L2 tick stream`
- the internal engine stays `tick/L2 event-driven`
- simplification happens by narrowing feature scope, not by downgrading engine
  semantics to a bar-native model

## Boundary Schemas And Core Objects

Canonical book/event objects should be treated as the in-memory core contract.

- storage, file, network, and serialization forms are boundary schemas
- data is normalized at the boundary and converted into core objects
- inside the core, simpler mathematical representations are allowed

The same rule should hold later for file, DB, network, and notebook
boundaries.

## Initial Backtest Book Simplification

The early backtest path may keep an array-based L2 engine while simplifying the
input book.

Current direction:

- `bids` and `asks` remain arrays
- a synthetic early book can use one level per side
- the initial slice can allow conceptually infinite liquidity
- but the engine logic itself should still process arrays and quantities
  generically

The point is to avoid rewriting the engine later when partial fills or deeper
books arrive.

## Current MVP Path And Gap Defaults

The current narrow backtest MVP baseline uses:

- bullish bar: `open -> low -> high -> close`
- bearish bar: `open -> high -> low -> close`
- `prev_close -> open` as a separate gap segment
- no midpoint execution inside the gap; `open` is the first executable price
- same-bar child orders are evaluated only on the post-parent tail, not on the
  full bar

## What This Document Does Not Yet Freeze

This draft does **not** yet fix the long-lived canonical contract for:

- the exact `OrderIntent` schema
- the exact long-lived payloads for `OrderEvent` and `FillEvent`
- the long-lived payload of `BarEvent` and the exact type shape for `bar_spec`
- exactly when an `OrderIntent` created inside a callback becomes effective
- the time ordering and conservatism rules of the synthetic tick generator
- the full pricing rules for market and limit fills
- the exact in-memory representation of infinite liquidity

The current product specs are still allowed to define narrower defaults for
the first implemented slice.

For the narrow current backtest MVP defaults, track:

- [`../product-specs/backtest-mvp.md`](../product-specs/backtest-mvp.md)

For the narrow current research-ergonomics defaults, track:

- [`../product-specs/research-ergonomics.md`](../product-specs/research-ergonomics.md)

## One-Line Summary

`trading` is a future-only draft of the shared kernel that backtest, paper, and
live should eventually share. Current implemented truth still belongs to the
product specs.
