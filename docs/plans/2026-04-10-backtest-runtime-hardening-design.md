# Backtest Runtime Hardening Design

## Status

- Status: `proposed baseline`
- Class: `design`
- Scope: clarify semantic preservation, runtime paths, and future paper/live extensibility for the current `research` / `trading` backtest runtime

Related documents:

- [../../AGENTS.md](../../AGENTS.md)
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
- [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
- [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md)
- [../RELIABILITY.md](../RELIABILITY.md)
- [../design-docs/quantleet-architecture.md](../design-docs/quantleet-architecture.md)
- [../design-docs/architecture-governance.md](../design-docs/architecture-governance.md)

## Goal

Keep the current Backtest MVP simple, but resolve the following four risks into
a structure that is safer in the long run.

1. indicator causality still depends too much on convention
2. the streaming/live path does not yet have a strong incremental runtime path
3. the current OHLCV-based execution approximation remains hidden as implicit
   implementation detail
4. the boundary between backtest-specific semantics and shared trading
   semantics is not fully locked yet

The goal of this document is not "add every new feature right now."
It is to clarify which parts should become shared contract and which parts
should remain explicit backtest approximation.

## Background

Today, `quantleet` operates as the following combination:

- user surface: `Strategy.init()` + `Strategy.on_bar()`
- time-series surface: `SeriesView` with causal indexing
- indicator surface: `ta.*`
- helper surface: `qc.*`
- execution engine: an event-driven backtest that runs on the shared execution
  core with OHLCV converted into synthetic execution-driving events

This direction is not strange. It is closer to a sensible hybrid of the
following strengths:

- `backtesting.py`: simple strategy-authoring UX
- `backtrader`: preload plus event-driven strategy execution
- `nautilus_trader`: shared execution semantics across research/live and
  explicit separation of bar-based execution modeling

The problem is not the direction itself.
The problem is whether the current simplified implementation stays safe as the
system grows.

## Non-Goals

This design does not aim to:

- introduce multi-symbol or multi-timeframe support immediately
- implement a live-trading runtime immediately
- make large public UX changes to `Strategy`, `ta`, or `qc`
- pivot toward a large vectorized research framework in the style of
  `vectorbt`
- promote the execution model to high-frequency or venue microstructure
  fidelity

## Core Design Principle

The most important principle is:

> Allow the simplifications required by the current backtest, but do not let
> those simplifications appear to be shared trading meaning.

That means:

- keep strategy UX simple
- make runtime contracts stricter
- split backtest approximations into explicit models
- move shared semantics gradually toward `trading`

## Decision Summary

### D1. Separate indicator batch correctness from runtime causality

Official indicators should be split into two layers:

- reference / pure layer: batch-calculation baseline implementations
- runtime / online layer: execution implementations that expose only causally
  visible values up to the current step

Principles:

- the pure layer exists primarily for correctness baseline and fixture lock
- the runtime layer owns actual strategy-execution meaning
- precompute is an optimization, not the source of meaning
- `TA-Lib` remains the canonical batch reference backend
- `quantleet` owns runtime-contract authority

The key point is to stop allowing "precomputed, but accidentally causal-looking"
behavior to stand in for the official runtime contract.
In principle, shipped indicators should have an incremental-capable runtime path.

The runtime path may be implemented in one of the following ways:

- an internal runtime kernel
- a vetted external incremental indicator adapter
- a thin runtime wrapper around a compiled backend

However, regardless of implementation strategy, the common runtime contract
must first define:

- `append`
- `reset`
- `initialized`
- causal visibility only up to the current runtime prefix

### D2. The default runtime path should be incremental-capable

The current backtest can be fast with preload and precompute, but for future
streaming/live paths, recomputing an entire length-`N` array each time is
structurally weak.

So the first thing to lock for official baseline indicators is not a specific
hand-written implementation, but these principles:

- the default runtime path should support incremental updates
- batch full recompute should be fallback or correctness reference
- backtest precompute is allowed only when it is semantically equivalent to the
  runtime path

In this document, "incremental-capable path" does not mean
"we must rewrite every formula by hand immediately."
All of the following remain valid candidates:

1. internal thin runtime kernels
2. vetted external incremental adapters
3. compiled/runtime hybrid wrappers

#### D2-A. Internal thin runtime kernel

This is especially appropriate when the official baseline indicator set is still
small and the shipped contract is intentionally narrow.

Advantages:

- it can match `quantleet`'s runtime contract exactly
- reset / initialized / append semantics remain under engine-level control
- it helps future paper/live parity

Disadvantages:

- implementation and verification cost
- parity against the batch reference must be maintained continuously

#### D2-B. Vetted external incremental adapter

For example, wrapping an external incremental indicator library.

Advantages:

- potentially faster initial implementation
- reuse of already-built incremental data structures

Disadvantages:

- warmup, `NaN`, and initialization semantics may differ from the current
  product spec
- the external lifecycle contract may not match `quantleet`'s runtime
  contract closely enough
- semantic authority can drift outward too easily

#### D2-C. Compiled/runtime hybrid wrapper

For example, keeping a compiled backend such as `TA-Lib` as reference while a
thin wrapper owns runtime state.

Advantages:

- preserves the validation benefits of the reference backend
- does not fully abandon runtime ownership

Disadvantages:

- if the backend is full-array oriented, streaming gains are limited
- Python/C boundaries and array reconstruction may remain in the hot path

The current baseline judgment is:

- `TA-Lib only` is good as batch correctness reference, but weak as canonical
  runtime path
- external incremental adapters are worth leaving open as secondary options
- if shared runtime semantics matter in the long run, `quantleet` should own
  runtime behavior for at least the baseline indicator set

So the baseline direction for official indicators is:

- `sma`: runtime path based on rolling sum
- `ema`: runtime path based on prior EMA state
- `rsi`: runtime path based on Wilder smoothing state
- `atr`: runtime path based on prior TR/ATR state
- `cci`: runtime path based on rolling typical-price statistics
- `bb`: runtime path based on rolling mean / variance
- `macd`: runtime path based on internal EMA states

Important:

- this list does not mean "implement every one of these by hand immediately"
- this list describes the intended runtime-state model for each indicator
- concrete implementation choice should still be decided per indicator in a
  later implementation plan

Policy:

- if an indicator has an incremental-capable path, runtime should use it as the
  canonical path
- pure full recompute should remain as fallback or verification path
- batch precompute optimization is allowed only when it is semantically
  identical to runtime output
- regardless of implementation strategy, parity must be verified against the
  current product spec and batch reference

### D3. Promote the current OHLCV approximation into an explicit backtest execution model

Converting OHLCV into a synthetic tick path is reasonable for the MVP.
However, the purpose of this logic is not to recover the "truth" of bar
history. It is to provide a backtest-only event-source approximation so that
backtest, paper, and live can share as much execution-core behavior as possible.

So the current logic should be treated not as a hidden fill helper, but as an
explicit `BacktestExecutionModel` layer.

Recommended structure:

- `BacktestExecutionModel`
  - responsibility: convert `TimeBar` input into execution-driving market
    events consumable by the shared matcher
- default implementation: `ConservativeOHLCVExecutionModel`
  - responsibility: preserve the current conservative OHLCV intrabar-sequencing
    rules
- optional lower layer: `FillModel`
  - responsibility: execution-quality assumptions such as queue position,
    slippage, synthetic liquidity, and partial-fill visibility
- possible internal policy layers:
  - `IntrabarPathPolicy`
  - `SyntheticBookPolicy`
  - future: `VolumeAllocationPolicy`

Naming principles:

- `ExecutionModel` is the outer abstraction that converts market data into
  execution-driving events and market-state updates
- `FillModel` is a narrower abstraction that adjusts execution quality either
  inside or beneath that layer
- the current MVP problem is not just fill price calculation, but the entire
  OHLCV-based execution approximation, so `ExecutionModel` is the right outer
  name

The current default meaning should be locked explicitly in both code and docs:

- input: OHLCV time bars
- output: synthetic execution-driving events passed into the shared execution
  core
- intrabar path follows the current directional ordering rule:
  - bullish: `Open -> Low -> High -> Close`
  - bearish: `Open -> High -> Low -> Close`
- synthetic book uses same-price bid/ask with a simplified snapshot
  approximation
- queue position, venue latency, order persistence, and partial-fill
  visibility are out of scope for the current model
- backtest results or engine config should record the execution-model name and
  key model metadata

The point is not to remove the simple model.
The point is to keep the shared execution core while making the backtest input
approximation explicit.

This is aligned with the same family of concerns seen in
`nautilus_trader`, where bar-based backtests maintain an internal order-book
model, process bars as ordered price-point sequences, and separate fill-model
concerns. `quantleet` remains much narrower, but the architectural intent is
similar.

Current recommended decision:

- split `ExecutionModel` and `FillModel` responsibilities internally now
- do not expose every setting publicly through the engine constructor yet
- first lock a single internal default,
  `ConservativeOHLCVExecutionModel`, and document its meaning through code and
  metadata
- open a public config surface only when there is real extension demand

### D4. Cut the boundary more clearly: shared trading semantics in `trading`, historical approximation in `research`

The following meanings should remain stable over time:

- order-intent meaning
- cash / position / PnL state transitions after fills
- interpretation of `sell while flat` in the current long-only MVP
- cost-model injection

By contrast, the following are backtest-specific approximations and should be
split accordingly:

- how OHLCV is converted into a synthetic event stream
- what intrabar path is assumed for historical bars
- backtest scheduling details such as when an order created on the current bar
  becomes active

The baseline direction in this document is:

- `trading.domain`: fill / state / order semantics
- `trading.application`: order activation policy and event-consumption order
- `research.adapters`: historical bars -> synthetic events conversion
- `research.application`: strategy-facing orchestration

The key goal is to avoid a future in which `research` and `execution` each
reinvent different trading meaning once paper/live runtimes arrive.

## Recommended Architecture Changes

### 1. Harden the indicator contract

Recommended changes:

- introduce an explicit runtime contract for official indicators
- document the role split between pure layer and runtime layer
- promote "official indicators must be causal" into a testable repository rule

Verification principles:

- runtime-path output == pure batch-reference output
- values are exposed only through the visible prefix
- warmup and `NaN` semantics match the current product spec

Recommended test types:

- deterministic fixture tests
- randomized prefix-equivalence tests
- lookahead-regression tests
- backend-parity tests

### 2. Separate the backtest execution model

Recommended changes:

- split the current synthetic-event logic into a named
  `BacktestExecutionModel` abstraction
- introduce `ConservativeOHLCVExecutionModel` as the default implementation
- keep matcher and state transitions in `trading`, and move only the
  backtest-specific event-source approximation into the model layer
- record execution-model metadata in the backtest result or engine config
- keep interface room for future quote/L2-backed models

Additional principles:

- execution model and fill model are not the same thing
- for the current MVP, execution model is the outer layer; fill/liquidity
  assumptions are narrower internal policy or later split layer
- if needed later, a separate `FillModel` layer may be promoted, but naming and
  responsibilities should not be mixed early
- separate internal architecture split from public configurability

Not allowed:

- leaving fill approximation hidden inside the backtest loop so the meaning
  stays implicit
- describing OHLCV-model output as venue-faithful simulation

### 3. Promote order activation policy

Recommended changes:

- promote the rule "orders created on bar close become active starting from the
  next execution segment" from internal `research` convention into an explicit
  policy object or shared application rule
- make backtest use that policy and prepare it for future reuse in paper/live
  semantics tables

Intent:

- lock the lookahead guardrail into structure, not just prose
- reduce ordering drift across runtimes

### 4. Add shared-semantics boundary checks

Recommended changes:

- add structure tests protecting what `trading` must own versus what
  `research` is allowed to approximate
- promote current boundary expectations into repo checks where appropriate

Examples:

- prevent `research` from reimplementing fill state transitions
- prevent `execution` from introducing a second position engine

## Priority Order

The default priority order is:

### P1. Introduce indicator online-kernel direction

This affects both correctness and performance.
However, "first priority" here means
"lock the runtime contract and backend strategy first,"
not "immediately hand-write every indicator."
This is the largest long-term risk in the current structure.

### P2. Make the backtest execution model explicit

Even if the current OHLCV approximation remains simple, making it explicit
improves both extensibility and user expectation management.

### P3. Split order activation policy

Expose one of the most important semantics that may eventually move into shared
trading behavior.

### P4. Add boundary checks

Gradually promote document-level principles into structure tests and repo checks.

## What Should Stay The Same For Now

For now, the following should remain unchanged:

- `Strategy.init()` / `on_bar()` UX
- the `SeriesView` mental model of `series[0]`, `series[1]`
- the public `ta.*` / `qc.*` surface
- the current single-symbol long-only MVP scope
- the current cost-injection approach

This is not a UX rewrite.
It is an internal honesty-and-safety pass on the runtime meaning.

## Best-Practice Alignment

This direction is aligned with the following best-practice ideas:

1. indicators should be definable not only as batch helpers, but also as online
   state machines
2. backtest simplifications should be exposed as explicit execution or
   simulation models
3. if research and live are meant to share semantics, the common meaning should
   live in the lower layer
4. precompute is an optimization, not semantic authority
5. using a compiled library is a separate question from owning runtime meaning
6. when targeting backtest/paper/live parity, environment-specific differences
   should live in event-source approximation while execution semantics stay as
   shared as possible
7. architecture responsibility split and public configuration surface should be
   treated as separate decisions

In short:

- this is not a pivot toward `vectorbt`-style large-scale vectorization
- it keeps the simple UX closer to `backtesting.py`
- it prepares a clearer split between batch optimization and runtime execution
  in the spirit of `backtrader`
- it moves closer to `nautilus_trader`'s clarity around shared execution core
  versus bar-based execution modeling
- it keeps `TA-Lib` as correctness reference without confusing it for canonical
  runtime authority

## Rollout Constraints

Any follow-up implementation based on this design should obey these constraints:

1. read the current implemented product specs first
2. do not introduce optimizations that weaken lookahead safety
3. any public API change requires explicit human approval
4. do not make live-faithful claims while the fill model remains intentionally
   simple
5. if the runtime-sensitive research path changes, include
   `uv run poe verify-runtime`

## Open Questions For Review

This design still requires later human review on:

1. whether every baseline indicator must immediately gain an online kernel, or
   whether `sma/ema/rsi/atr` should be the first priority set
2. whether external incremental adapters should remain official candidates, or
   whether the baseline should stay focused on internal thin kernels
3. whether order activation policy should move directly into
   `trading.application`, or whether an intermediate adapter layer is safer
4. whether `BacktestExecutionModel` should remain internal first or later become
   part of the public engine constructor
5. whether the current directional ordering should remain the only default or
   whether multiple ordering modes should eventually be supported
6. how long the current MVP should keep partial-fill invisibility

## Current Recommended Answers

At the time of this document, the recommended baseline answers are:

1. `ExecutionModel` is the right outer name rather than `FillModel`.
   The current model owns the full OHLCV-based execution approximation, not
   just a fill-price helper.
2. Internally, `ExecutionModel` and `FillModel` responsibilities should already
   be split now.
   This is consistent with the way systems such as `nautilus_trader`,
   `backtrader`, and `pybroker` separate execution/input policy from
   slippage/liquidity policy.
3. Public API should still keep a single default for now.
   Internal architecture split should come first; public configurability should
   follow only when real extension demand appears.

## Summary

The conclusion is simple:

- keep the current `quantleet` direction
- but cut the current simplified implementation into safer long-term contracts
- treat indicator runtime, not batch backend calls, as the source of official
  runtime meaning
- make the OHLCV-to-shared-core approximation explicit through a backtest
  execution model
- move shared trading meaning more clearly toward `trading`

This is not a proposal to replace the current system wholesale.
It is a baseline design for deciding what to harden next while preserving the
current MVP.
