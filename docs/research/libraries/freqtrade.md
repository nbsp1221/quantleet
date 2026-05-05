# Freqtrade Dossier

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

Capture the most relevant lessons from `Freqtrade` for `quantleet`, especially around exchange-operator workflows, anti-bias tooling, and the strengths and limits of a crypto-first product surface.

## Project Snapshot

- public docs and README position `Freqtrade` as a free and open-source crypto trading bot written in Python
- the local shallow inspection used in this pass saw recent repository activity on commit `250156f` dated `2026-03-22`
- the broader overview pass noted visible development version `2026.3-dev`
- the public feature surface includes backtesting, dry-run trading, live trading, web UI, Telegram control, hyperoptimization, and FreqAI

## Core Architecture

`Freqtrade` reads as an operational trading platform first and a research library second. The public surface is organized around exchange connectivity, bot operation, strategy customization, data downloading, backtesting, hyperoptimization, and optional machine-learning extensions.

## Strategy API Shape

The docs expose a strategy-class model with standard customization points and optional advanced callback methods. The public guidance encourages users to start with templates and only implement callbacks they actually need. This is a pragmatic reference for extensible strategy APIs, even if the overall product identity is more operator-focused than `quantleet`.

## Data And Execution Model

The system is heavily exchange- and candle-data-oriented. Backtesting, dry-run, and live trading all rely on exchange-specific data availability and operational caveats. The docs also include explicit lookahead-analysis material and repeated warnings about data and feature-design mistakes, which is unusually valuable from a research-safety standpoint.

## Order And Fill Model

Relative to research-only tools, `Freqtrade` has a stronger operational story because it actually runs bots against exchanges. At the same time, the backtesting model still appears more candle-native than the explicit event-kernel direction `quantleet` is pursuing, so it should not be treated as a strict kernel-semantics reference.

## Backtest vs Live Story

`Freqtrade` clearly supports backtesting, dry-run, and live execution. The public docs emphasize operational continuity, but this pass did not treat the product as a strict same-kernel parity engine in the `NautilusTrader` sense. Exchange-specific caveats and data availability details still matter materially.

## UX/DX Notes

- very strong operator tooling for crypto users
- web UI and Telegram control reduce friction for active bot operators
- docs are broad and practical, especially on exchange caveats
- breadth is a strength, but it also creates substantial product and maintenance scope

## Strengths

- strong crypto exchange integration story
- backtest, dry-run, and live workflows already exist
- hyperopt and FreqAI broaden the research surface
- anti-bias and lookahead-analysis docs are unusually actionable

## Weaknesses

- identity is tightly coupled to crypto exchange operation
- candle-native assumptions remain stronger than in an event-first kernel
- product breadth is much larger than current `quantleet` scope

## What Quantcraft Should Learn

- bias-detection and lookahead-analysis tooling should be visible product features, not hidden implementation details
- operator workflows need explicit guardrails, exchange caveats, and first-class docs
- dry-run and runtime observability can make a research system materially more useful before live trading exists

## What Quantcraft Should Avoid

- do not let exchange-operator breadth overwhelm the semantic clarity of the core kernel
- do not bind the product identity too tightly to one asset-class niche if the long-term architecture is broader
- do not copy candle-native runtime assumptions into a kernel intended to explain event-causal fills

## Sources

- https://www.freqtrade.io/en/stable/
- https://docs.freqtrade.io/en/stable/backtesting/
- https://docs.freqtrade.io/en/stable/lookahead-analysis/
- https://github.com/freqtrade/freqtrade
- https://github.com/freqtrade/freqtrade/commit/250156f1a398f9960c651c144e90f616fbbe0ccb
