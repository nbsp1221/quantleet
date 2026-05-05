# vectorbt Dossier

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

Capture the most relevant lessons from `vectorbt` for `quantleet`, especially around fast research workflows, multi-asset analysis, and parameter-sweep ergonomics.

## Project Snapshot

- public docs and README position `vectorbt` as a fast, vectorized backtesting and portfolio-research stack built on pandas, NumPy, and Numba
- the local shallow inspection used in this pass saw recent repository activity on commit `a4e264f` dated `2026-03-19`
- the broader overview pass noted latest visible release `0.28.4` on `2026-01-26`
- the open-source project presents itself as the community edition of a broader product family

## Core Architecture

`vectorbt` is not centered on an event loop. Its architecture is dataframe- and portfolio-centric: signal generation, array broadcasting, accessors, portfolio simulation helpers, metrics, plotting, and batch analysis. This makes it a strong reference for research scale, but a weaker direct model for an execution-first kernel.

## Strategy API Shape

The public API is oriented around objects such as `Portfolio.from_orders`, `Portfolio.from_signals`, and `Portfolio.from_order_func` rather than around an imperative subclass with `on_bar` callbacks. Users compose data, signals, and portfolio simulations instead of driving a strategy through a mutable event context.

## Data And Execution Model

The library is optimized for vectorized simulation across large datasets, multiple assets, grouped columns, and many parameter combinations. It also exposes walk-forward splitters and rich portfolio-analysis primitives. This is excellent for fast exploratory research, but it is a different execution model from `quantleet`'s current event-driven kernel.

## Order And Fill Model

`vectorbt` clearly simulates orders and tracks trades, positions, logs, and performance, but the public framing is still portfolio simulation rather than venue-realistic execution modeling. It is best treated as a high-throughput research tool, not as a reference for detailed intrabar causality or live parity.

## Backtest vs Live Story

The open-source docs emphasize backtesting, analysis, plotting, and automation helpers such as Telegram messaging. This pass did not find a strong claim that the same core engine is the system of record for live brokerage execution in the same sense that parity engines advertise.

## UX/DX Notes

- very strong for notebook-heavy quantitative workflows
- supports large sweeps and multi-asset analysis naturally
- rich plotting and portfolio analytics reduce custom analysis work
- the API is powerful, but less intuitive for users who think in imperative strategy methods

## Strengths

- excellent research throughput
- strong multi-asset and parameter-sweep workflows
- rich portfolio analysis and plotting
- flexible simulation APIs from simple orders to custom order functions

## Weaknesses

- less natural for users who want an imperative strategy object
- weaker direct fit for shared-kernel backtest, paper, and live ambitions
- easy to confuse analytical convenience with execution realism

## What Quantcraft Should Learn

- multi-asset research ergonomics matter and should not require users to build their own analysis scaffolding
- portfolio-level stats, logs, and plots should be treated as product features
- parameter sweeps and walk-forward-style helpers can dramatically improve the practical value of a research tool

## What Quantcraft Should Avoid

- do not let vectorized convenience dictate the execution-kernel design
- do not collapse event-causal semantics into a purely dataframe-first abstraction
- do not assume users who want parity with paper/live will accept research-only simulation trade-offs

## Sources

- https://vectorbt.dev/
- https://github.com/polakowo/vectorbt
- https://github.com/polakowo/vectorbt/commit/a4e264f720d80b20b4f246b7ee2a1f271e504b30
