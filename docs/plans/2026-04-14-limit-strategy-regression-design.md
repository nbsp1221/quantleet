# Limit Strategy Regression Design

## Status

- Status: `approved baseline`
- Class: `design / decision record`
- Scope: real-data limit-order regression coverage for the current backtest engine

Related documents:

- [../../AGENTS.md](../../AGENTS.md)
- [../../README.md](../../README.md)
- [../../ARCHITECTURE.md](../../ARCHITECTURE.md)
- [../product-specs/backtest-mvp.md](../product-specs/backtest-mvp.md)
- [../product-specs/research-ergonomics.md](../product-specs/research-ergonomics.md)
- [../RELIABILITY.md](../RELIABILITY.md)

## Goal

Define the first approved real-data `limit order` regression set so future
sessions can add durable backtest coverage that raises engine trust to the same
general level already provided by the current market-order canonical strategy
tests.

The key question behind this design is not:

- "what is the most profitable limit strategy?"

The key question is:

- "which real-data limit strategies, when kept as stable regression tests, make
  it reasonable to trust the current engine's limit-order path?"

## Current Problem

The repository already has:

- real-data canonical regression tests for market-order strategies
- unit coverage for limit matching rules
- synthetic integration coverage for limit fill, no-fill, and mixed-order
  sequencing

What it does **not** yet have is:

- real-data canonical regression coverage for limit-order strategies

This leaves an avoidable trust gap.

A reader can currently believe:

- market-order paths are trusted end to end on the checked-in BTC 1h fixture
- limit-order paths are semantically tested

But the repo does not yet prove:

- that the limit-order path remains stable end to end on real historical data
- that realistic limit-order strategy outcomes stay reproducible when the engine
  changes

## Design Principle

The real-data limit regression lane should optimize for:

1. engine trust
2. reproducibility
3. explainability
4. representative real usage

It should **not** optimize for:

- maximum strategy variety
- maximum indicator diversity
- broad alpha exploration
- covering every possible limit-order style

This is a regression surface, not a research zoo.

## Approved Count

The first approved real-data limit regression set contains **three** strategy
families.

Why three:

- one strategy is too weak because it can only validate one side of limit usage
- two strategies are strong enough to cover entry-limit and exit-limit behavior
- three strategies provide one additional mixed-path confidence check without
  turning the canonical lane into a broad strategy catalog

Why not more than three for now:

- unit and synthetic integration tests already cover much of the lower-level
  semantics
- additional real-data canonical strategies would add maintenance cost faster
  than they add trust
- too many canonical strategies would make future drift triage slower and less
  legible

So the repository should keep:

- `2` primary canonical limit regressions
- `1` supporting mixed-path regression

## Approved Strategy Set

### 1. EMA Pullback Buy-Limit With Market Exit

Role:

- primary canonical limit-entry regression

Why this strategy is selected:

- it represents a widely recognizable real trading pattern: buy the pullback in
  an uptrend using a resting limit order near a moving average
- it fits the current engine surface cleanly because `ta.ema` already exists
- it isolates `limit entry` behavior while keeping exit behavior simple

What it is intended to prove:

- a buy limit can rest across bars and later fill on real BTC 1h data
- fills occur at no worse than the specified limit
- pending-order persistence remains stable under real backtest flow
- the end-to-end result remains reproducible across engine changes

Why market exit is kept here:

- the goal of this strategy is to test limit entry, not to combine multiple
  sources of ambiguity into one regression

### 2. Market Entry With Take-Profit Sell-Limit Exit

Role:

- primary canonical limit-exit regression

Why this strategy is selected:

- take-profit via sell limit is one of the most common and explainable real
  uses of limit orders
- it isolates `limit exit` behavior without depending on limit entry rules
- it mirrors practical usage more directly than many abstract limit-order
  examples

What it is intended to prove:

- a sell limit can rest after a filled long entry and later execute on real
  BTC 1h data
- exit fills remain reproducible in timestamp, price, and fee-sensitive summary
- no-fill and delayed-fill behavior can be observed naturally without needing
  synthetic-only fixtures

Why market entry is kept here:

- the goal of this strategy is to test limit exit in the cleanest possible way

### 3. Bollinger Lower-Band Buy-Limit With Band-Based Sell-Limit

Role:

- supporting mixed-path real-data limit regression

Why this strategy is selected:

- it gives one realistic strategy that uses both limit entry and limit exit in
  the same end-to-end path
- it is still simple enough to explain and reproduce
- it provides a stronger confidence check that mixed pending-order behavior does
  not silently drift

What it is intended to prove:

- limit entry and limit exit can coexist in one realistic strategy without
  breaking result reproducibility
- the engine remains stable when both sides of the trade depend on resting limit
  orders

Why this strategy is supporting rather than primary:

- it is slightly more path-dependent than the first two strategies
- if it breaks, diagnosis can be harder because entry and exit both use limits
- it is valuable as the third confidence layer, not as the foundation

## Rejected Or Deferred Alternatives

### Support / Resistance Retest Limit Strategy

Deferred because:

- it is familiar to traders, but hard to define mechanically without adding
  brittle rule choices
- it risks turning the canonical regression into a debate about level-detection
  semantics instead of limit-order engine trust

### Grid Strategy

Deferred because:

- it is famous and limit-heavy, but too large for the first real-data canonical
  lane
- it would test order-management complexity more than the narrow trust question
  this slice needs to answer

## Trust Claim This Design Is Meant To Support

If these three strategies are later implemented as stable real-data regression
 tests and continue to pass, a reader should be able to infer the following:

- the current engine handles realistic limit entry on real historical data
- the current engine handles realistic limit exit on real historical data
- the current engine can survive one realistic strategy that uses both together

This still does **not** mean:

- all possible limit strategies are verified
- stop or bracket semantics are verified
- live execution semantics are verified

It is a strong current-scope trust statement, not a universal one.

## Implementation Direction For A Later Session

When this design is implemented later, the tests should:

- use the checked-in BTC USD-M 1h 2025 fixture
- run through the public `BacktestEngine` surface
- construct strategies through the normal `Strategy.init()` / `on_bar()`
  contract
- pin summary values, fill samples, and trade-log digests in the same style as
  the current canonical RSI, EMA, and MACD market-order regressions

The later implementation plan should keep the canonical lane small and legible.
