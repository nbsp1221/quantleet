# Backtest Spec

## Status

- Status: `implemented`
- Role: English domain entry for the current implemented backtest baseline
- Canonical implementation contract: [backtest-mvp.md](backtest-mvp.md)

## Purpose

Provide deterministic backtesting workflows built from checked-in code and documented assumptions.

## Safety

Backtests must be reproducible and must not depend on undocumented local state.

## Current MVP Baseline

The current implemented backtest baseline is tracked in:

- [`backtest-mvp.md`](backtest-mvp.md)

That canonical spec currently defines the shipped single-symbol, long-only, deterministic backtest baseline that the `research` ergonomics surface builds on. Broader backtest expansion should start from this implemented baseline rather than treating it as an upcoming slice.

The current preferred user-facing execution entry is documented in the research
ergonomics layer as `BacktestEngine` with the canonical paths
`run(bars=..., strategy=StrategyClass, config=...)` and
`run(source=..., strategy=StrategyClass, config=...)`.
