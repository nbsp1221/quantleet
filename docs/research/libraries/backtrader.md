# Backtrader Dossier

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

Capture the most relevant lessons from `Backtrader` for `quantleet`, especially around breadth, multi-data workflows, and the trade-offs of a large classic framework surface.

## Project Snapshot

- public docs position `Backtrader` as a feature-rich backtesting and trading framework
- the local shallow inspection used in this pass saw visible upstream commit `b853d7c` dated `2023-04-19`
- that visible commit message corresponds to version `1.9.78.123`
- repository samples and package layout still expose a wide feature surface for feeds, analyzers, indicators, brokers, and live connectors

## Core Architecture

`Backtrader` uses a framework-style architecture centered on `Cerebro`, which wires together strategies, data feeds, broker simulation, analyzers, indicators, and optional live integrations. It is broader than `quantleet` in almost every user-facing dimension, but it also carries the weight of an older and more sprawling abstraction stack.

## Strategy API Shape

The common pattern visible in samples is:

- subclass `bt.Strategy`
- implement `next()`
- add data feeds and strategy classes to `bt.Cerebro()`
- configure broker cash, commission, analyzers, and plotting through framework objects

This gives users a broad, consistent surface, but it is also more framework-heavy than `backtesting.py`.

## Data And Execution Model

The framework supports multiple data feeds, resampling, replay, and multi-timeframe workflows. It reads as a hybrid event/bar engine, but most public usage still appears heavily bar-centric. The local code inspection also showed live-oriented feeds such as Interactive Brokers integrations, which reinforces the framework's breadth.

## Order And Fill Model

The project appears to support a broad classic order and broker model, with analyzers and broker abstractions layered around it. That is useful as a reference for order-surface coverage, but the docs surfaced in this pass are less explicit than `quantleet`'s current docs about causal intrabar defaults or gap handling.

## Backtest vs Live Story

`Backtrader` clearly includes live-integration pathways, but the public story reads more like "one framework with many connectors" than "one rigorously shared kernel with the same semantic contract across research and live."

## UX/DX Notes

- users get a lot of features in one place
- samples and analyzers show many common workflows already solved
- the framework surface is dense and can feel older than newer libraries
- depth is a strength, but discoverability is weaker than more modern, narrower tools

## Strengths

- broad feature coverage
- multi-data and multi-timeframe support
- rich analyzer and indicator ecosystem
- live integrations and broker abstractions already exist

## Weaknesses

- maintenance freshness appears weaker than newer leaders in the space
- framework complexity is high relative to current `quantleet`
- causal execution semantics are less foregrounded than in `quantleet`'s current documentation

## What Quantcraft Should Learn

- users will eventually expect explicit support for multiple data streams and timeframes
- analyzers and reporting hooks are worth treating as first-class extension surfaces
- broker and data-adapter seams should stay visible and composable

## What Quantcraft Should Avoid

- do not grow a giant framework surface before the kernel semantics are stable
- do not bury the key execution rules inside implicit framework behavior
- do not make common workflows depend on a large orchestrator object if a smaller API can stay legible

## Sources

- https://www.backtrader.com/home/features/
- https://www.backtrader.com/docu/
- https://github.com/mementum/backtrader
- https://github.com/mementum/backtrader/commit/b853d7c90b6721476eb5a5ea3135224e33db1f14
