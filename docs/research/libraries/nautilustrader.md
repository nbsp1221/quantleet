# NautilusTrader Dossier

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

Capture the most relevant lessons from `NautilusTrader` for `quantleet`, especially around one-kernel parity, explicit time and venue semantics, and the trade-off between realism and product weight.

## Project Snapshot

- public docs and README position `NautilusTrader` as an open-source, production-grade, Rust-native engine for multi-asset and multi-venue trading systems
- the local shallow inspection used in this pass saw recent repository activity on commit `ae3bc93` dated `2026-03-22`
- the docs explicitly describe one event-driven architecture spanning research, deterministic simulation, and live execution
- Python is presented as the control plane for strategy logic, configuration, and orchestration, with a Rust core underneath

## Core Architecture

This is the closest architectural match to `quantleet`'s intended direction in the current comparison set. The public design centers on a compiled core, explicit adapters, a message bus, cache, deterministic time, and one event-driven runtime shared across backtesting and live trading.

## Strategy API Shape

The public positioning emphasizes Python strategy logic and orchestration on top of the Rust engine, with the option to write more of the system in Rust for critical workloads. The important lesson is not one exact method name; it is the architectural split between a strong execution core and a higher-level strategy control plane.

## Data And Execution Model

The README explicitly calls out multiple venues, instruments, strategies, quote ticks, trade ticks, bars, order books, and nanosecond-resolution backtesting. That is materially beyond current `quantleet` scope, but it is still the clearest example here of treating market data and execution as first-class runtime concerns rather than as convenience-layer inputs.

## Order And Fill Model

`NautilusTrader` exposes a much deeper order model than the research-first tools in this set: multiple time-in-force policies, advanced order types, conditional triggers, execution instructions, and contingency orders. This dossier treats it as a realism benchmark, not as a feature checklist for immediate copying.

## Backtest vs Live Story

The public docs strongly emphasize research-to-live parity. The same execution semantics and deterministic time model are presented as operating in both research and live systems, with strategies moving from research to production without code changes.

## UX/DX Notes

- conceptually clear once the architecture is understood
- significantly heavier than lightweight Python research tools
- more operational and architectural discipline is required up front
- better suited as a north-star than as a near-term scope match

## Strengths

- strongest parity story in this comparison set
- serious execution, venue, and time modeling
- modular adapter architecture
- multi-asset and multi-venue support are treated as core concerns, not add-ons

## Weaknesses

- heavier operational and conceptual footprint than current `quantleet`
- likely steeper learning curve for users who want a lightweight research notebook tool
- too much of its surface would be premature for the current `quantleet` slice

## What Quantcraft Should Learn

- keep one kernel semantics contract across backtest, paper, and live as the core architectural discipline
- make time, venue, and order-state semantics explicit in docs and code boundaries
- maintain a clear separation between execution core responsibilities and higher-level strategy ergonomics

## What Quantcraft Should Avoid

- do not import heavyweight platform scope before the simpler backtest and paper-trading slices are credible
- do not require users to absorb multi-venue complexity before the single-venue story is polished
- do not turn the long-term north-star into a justification for premature complexity in the short term

## Sources

- https://nautilustrader.io/docs/latest/
- https://github.com/nautechsystems/nautilus_trader
- https://github.com/nautechsystems/nautilus_trader/commit/ae3bc930041a3c5435051ac7ae5603ce8f197b8e
