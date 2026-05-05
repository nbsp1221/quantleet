# Lumibot Dossier

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

Capture the most relevant lessons from `Lumibot` for `quantleet`, especially around same-code backtest/live messaging, broker-facing strategy APIs, and the scope risks of a broad parity product.

## Project Snapshot

- public docs and README position `Lumibot` as a backtesting and trading library for stocks, options, crypto, futures, forex, and more
- the local shallow inspection used in this pass saw visible upstream commit `d2b0158` dated `2026-03-17`
- that local inspection also surfaced visible tag `v4.4.56`
- the public message is explicit that the same code used for backtesting can be used for live trading

## Core Architecture

`Lumibot` appears to be organized around Python strategy classes, broker integrations, data-source integrations, and backtesting/live execution paths. It is much broader than current `quantleet` and noticeably more productized around real brokers and operational workflows.

## Strategy API Shape

Local examples show strategies subclassing `Strategy`, implementing `on_trading_iteration`, and running through backtest helpers or broker-backed execution. This is a useful reference for Python-side parity ergonomics because the strategy surface is still user-facing and imperative, even while the product reaches into many broker and data integrations.

## Data And Execution Model

The public docs point to multiple asset classes, multiple brokers, and configurable backtesting data sources. The current repository also exposes environment-variable-driven data-source routing for backtests. This makes `Lumibot` a useful reference for parity UX, but it also highlights how quickly external dependencies can dominate the design.

## Order And Fill Model

This pass found public and repository-visible evidence of a broad order surface, including market, limit, stop, stop-limit, trailing, smart-limit, and contingency-style flows such as OCO, OTO, and bracket semantics in changelog and examples. That is useful as a reminder of user expectations, but it is a much broader order model than the current `quantleet` slice.

## Backtest vs Live Story

The same-code backtest/live story is a headline feature. `Lumibot` is therefore a strong reference for how parity can be presented at the Python strategy layer, even if the broader operational surface is much heavier than what `quantleet` should take on immediately.

## UX/DX Notes

- parity messaging is easy to understand
- the strategy surface stays Python-first
- broad integrations are attractive to users, but create real maintenance and operational complexity
- repository-visible product integrations and hosted-service references show how quickly a library can expand beyond a narrow kernel identity

## Strengths

- strong same-code backtest/live message
- broad asset and broker coverage
- user-facing imperative strategy API
- broad order-surface expectations are already represented

## Weaknesses

- large operational scope compared with current `quantleet`
- external data and broker dependencies can dominate the user experience
- breadth can make architectural boundaries harder to keep crisp

## What Quantcraft Should Learn

- parity should be legible at the strategy layer, not just as an internal architectural aspiration
- a Python-first strategy API can stay friendly even when the underlying execution system becomes more capable
- order-model documentation needs to be explicit once the surface grows beyond simple market and limit orders

## What Quantcraft Should Avoid

- do not let external service integrations become the center of gravity before the core kernel and paper runtime are solid
- do not adopt a huge cross-asset promise before the narrow initial story is polished
- do not let parity marketing outrun actual semantic equivalence

## Sources

- https://lumibot.lumiwealth.com/
- https://github.com/Lumiwealth/lumibot
- https://github.com/Lumiwealth/lumibot/commit/d2b015809415e7057fbd70bd7fc8218aa33b75a9
