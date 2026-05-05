# PyBroker Dossier

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

Capture the most relevant lessons from `PyBroker` for `quantleet`, especially around practical multi-symbol research workflows, ML integration, and walk-forward-oriented user tooling.

## Project Snapshot

- public docs and README position `PyBroker` as an algorithmic trading framework with a focus on machine-learning-enabled strategies
- the local shallow inspection used in this pass saw recent repository activity on commit `31094c7` dated `2026-03-04`
- the broader overview pass noted latest visible release `1.2.12` on `2026-03-05`
- the public feature set includes multi-instrument backtesting, walkforward analysis, bootstrapped metrics, caching, and parallelized computation

## Core Architecture

`PyBroker` is best understood as a research framework rather than a parity engine. The project combines a fast NumPy and Numba backtesting core with data-source integrations, indicator pipelines, model training hooks, caching, and walk-forward-style evaluation workflows.

## Strategy API Shape

The README examples show a `Strategy` object configured with a data source and execution callbacks. Users define execution logic through context objects that expose indicators, models, positions, share sizing, hold durations, and stop settings. That is broader than `quantleet`'s current `on_bar` MVP, but it is still approachable and pragmatic.

## Data And Execution Model

The public docs emphasize multi-symbol workflows, pluggable data sources, ML model training, and walkforward analysis. The local code inspection also surfaced explicit support for cached models, randomized bootstrapping, and long and short position controls. This makes `PyBroker` a useful reference for practical research breadth.

## Order And Fill Model

The local code inspection exposed context fields for buy and sell share sizing, hold periods, stop-loss configuration, limit prices, cover behavior, long and short positions, and slippage models. That suggests a richer research order model than current `quantleet`, but it still reads as a backtest-centric execution surface rather than a venue-realistic shared kernel.

## Backtest vs Live Story

This pass found a strong backtesting and research story, but not an equally strong first-class live-trading parity story. `PyBroker` is therefore more useful to `quantleet` as a reference for research breadth than for one-kernel backtest/paper/live architecture.

## UX/DX Notes

- practical, user-facing support for multi-symbol workflows is a major advantage
- model-based and rule-based strategies live in one framework
- walk-forward and bootstrapped metrics make the research story more credible
- the product identity is broad research, not deep execution semantics

## Strengths

- strong multi-symbol research usability
- built-in ML and walk-forward capabilities
- caching and parallelism for practical iteration speed
- richer research workflow coverage than current `quantleet`

## Weaknesses

- not a direct model for a parity-oriented trading kernel
- easier to grow into breadth than into explicit execution explainability
- public identity is more research-platform oriented than runtime-semantics oriented

## What Quantcraft Should Learn

- practical multi-symbol research workflows matter sooner than a full production-trading surface
- walk-forward helpers and better metrics can make conservative strategy evaluation more credible
- a single framework can expose both rule-based and model-based workflows without making ML the core identity

## What Quantcraft Should Avoid

- do not treat research breadth as a substitute for explicit execution semantics
- do not overload the early strategy API with too many context knobs before the basic ergonomics are stable
- do not let ML-oriented expansion outrun the narrow backtest and paper-trading foundation

## Sources

- https://www.pybroker.com/en/latest/
- https://github.com/edtechre/pybroker
- https://github.com/edtechre/pybroker/commit/31094c7cbec42316969e7358ae169339548a03a6
