# backtesting.py Dossier

## Status

- Status: `current`
- Class: `research-dossier`
- Canonical: `no`
- Last reviewed: `2026-03-23`

This document is a research artifact, not a system-of-record implementation contract.

Use it to inform future design or roadmap decisions. If a conclusion from this dossier should affect implementation, promote it into a canonical product spec, design doc, or execution plan first.

Related research docs:

- [Research index](../index.md)
- [Python Quant And Backtesting Library Landscape (2026)](../2026-03-23-python-quant-library-landscape.md)

## Purpose

Capture the most relevant lessons from `backtesting.py` for `quantleet`, especially around bar-facing strategy ergonomics, reporting, and low-friction experimentation.

## Project Snapshot

- public docs position `backtesting.py` as a lightweight Python backtesting framework
- the local shallow inspection used in this pass saw recent repository activity on commit `6e9016c` dated `2025-12-20`
- the broader overview pass noted latest visible tag `0.6.5`
- the quick-start docs explicitly frame it as best suited to individual tradeable assets rather than multi-asset portfolio rebalancing

## Core Architecture

`backtesting.py` is centered on a compact bar-native backtesting core: a `Backtest` runner, a `Strategy` subclass API, indicator helpers, built-in statistics, and plotting. It reads as a focused research tool, not as a general shared execution kernel meant to span backtest, paper, and live runtimes.

## Strategy API Shape

The public API is unusually approachable. The common pattern is:

- subclass `Strategy`
- implement `init()` and `next()`
- register indicators with `self.I(...)`
- place orders with `self.buy()` and `self.sell()`
- expose tunable parameters as class variables for optimization

This is a strong reference for bar-facing ergonomics because the API surface is small enough to memorize.

## Data And Execution Model

The project is primarily candle-oriented. The quick-start examples and API docs are built around OHLCV data, sequential bar processing, and fast indicator evaluation on NumPy-backed arrays. The docs include examples for multiple time frames, but the public framing still reads as single-strategy, single-asset research rather than a portfolio-wide execution engine.

## Order And Fill Model

The library appears to offer practical backtest order conveniences such as commissions, hedging toggles, `exclusive_orders`, stop-loss helpers, and trailing-strategy helpers. That is broad enough for many retail backtests, but it is still best understood as a candle-level simulation model rather than detailed venue microstructure modeling.

## Backtest vs Live Story

The public docs and README emphasize backtesting, optimization, statistics, and visualization. This pass did not find an equivalent first-class live-trading runtime or a strong claim that one event kernel is reused unchanged across research and live execution.

## UX/DX Notes

This is where `backtesting.py` stands out.

- the quick-start path is short and memorable
- plotting and summary statistics are first-class
- optimization is built into the default workflow
- example-driven docs make the library easy to evaluate quickly

## Strengths

- very approachable imperative strategy API
- strong built-in reporting and plotting
- low-friction optimization workflow
- clear fit for single-asset strategy iteration

## Weaknesses

- less compelling for multi-asset or portfolio construction workflows
- candle-native assumptions are more implicit than `quantleet`'s current gap and intrabar rules
- no strong shared-kernel backtest-to-live story was visible in this pass

## What Quantcraft Should Learn

- keep the bar-facing strategy surface small enough that users can remember it without constant doc lookup
- make built-in reports, plots, and optimization entry points feel native rather than optional add-ons
- let common parameter sweeps use obvious strategy-local declarations instead of large configuration scaffolds

## What Quantcraft Should Avoid

- do not hide execution assumptions behind convenience helpers
- do not let a polished backtest-only API become a substitute for a coherent paper/live kernel plan
- do not optimize only for the single-asset case if `quantleet` intends to expand into multi-symbol execution later

## Sources

- https://kernc.github.io/backtesting.py/
- https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html
- https://github.com/kernc/backtesting.py
- https://github.com/kernc/backtesting.py/commit/6e9016c7b30d985137cde3fe24e1d39785c5e3a7
