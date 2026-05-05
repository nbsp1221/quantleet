# Research

Use this directory for time-scoped competitive research, ecosystem scans, and comparative studies that inform `quantleet` planning.

## Metadata

- index_kind: research-status-map
- default_read: Research docs are advisory inputs, not canonical implementation contracts. Promote conclusions into a product spec, design doc, or execution plan before using them to drive implementation.

## Overview Reports

| Document | Status | Canonical | Applicability | Read When | Notes |
| --- | --- | --- | --- | --- | --- |
| [`2026-03-23-python-quant-library-landscape.md`](2026-03-23-python-quant-library-landscape.md) | current | no | competitive research overview and roadmap framing | Before prioritizing post-MVP backtest, paper-trading, or UX/DX expansion. | Overview report for the Python quant/backtesting ecosystem as of 2026-03-23. Includes comparison matrix, strategic interpretation, and links to priority library dossiers. |
| [`2026-04-03-rsi-performance-analysis.md`](2026-04-03-rsi-performance-analysis.md) | current | no | baseline root-cause and implementation-pattern analysis for the completed indicator-runtime optimization batch | Before revisiting future `research` indicator-runtime work or comparing the completed fix against the original bottlenecks. | Advisory baseline analysis of the original perf gate failure, local profile evidence, and comparator implementation patterns that informed the completed fix. |
| [`2026-04-19-order-domain-architecture-comparison.md`](2026-04-19-order-domain-architecture-comparison.md) | current | no | order-domain boundary evidence and cross-library comparison | Before changing the `OrderIntent`/runtime `Order` seam, planning stop-order support, or drafting the first runtime Order implementation slice. | Advisory evidence note for the Order-domain split across research, design, and implementation planning. |
| [`2026-04-20-order-runtime-model-comparison.md`](2026-04-20-order-runtime-model-comparison.md) | current | no | runtime `Order` responsibility, lifecycle depth, and event-boundary evidence | Before deepening the runtime `Order` aggregate, introducing order statuses, or deciding whether state transitions belong on `Order` versus matcher/runtime orchestration. | English advisory comparison focused on runtime Order responsibilities rather than the original `OrderIntent` split itself. |
| [`2026-04-20-order-lifecycle-and-sizing-comparison.md`](2026-04-20-order-lifecycle-and-sizing-comparison.md) | current | no | lifecycle/FSM and sizing-intent evidence for the next order-model slice | Before designing stop-family lifecycle semantics or percentage-based sizing intent for the shared trading kernel. | Advisory evidence note for the next hard seams after the initial runtime `Order` promotion. |

## Library Dossiers

| Document | Status | Canonical | Applicability | Read When | Notes |
| --- | --- | --- | --- | --- | --- |
| [`libraries/backtesting-py.md`](libraries/backtesting-py.md) | current | no | library-specific research | Before copying the ergonomics or reporting patterns of `backtesting.py` into `quantleet`. | Advisory dossier for the bar-native, single-asset research tool with a strong imperative strategy API. |
| [`libraries/backtrader.md`](libraries/backtrader.md) | current | no | library-specific research | Before evaluating multi-data, multi-timeframe, analyzer, or broker-adapter surface ideas. | Advisory dossier for the broad classic Python backtesting framework. |
| [`libraries/vectorbt.md`](libraries/vectorbt.md) | current | no | library-specific research | Before planning vectorized research UX, parameter sweeps, or notebook-first analytics. | Advisory dossier for the dataframe- and portfolio-centric research stack. |
| [`libraries/nautilustrader.md`](libraries/nautilustrader.md) | current | no | library-specific research | Before planning shared-kernel backtest, paper, and live parity or higher-realism execution semantics. | Advisory dossier for the closest current architectural north-star in the comparison set. |
| [`libraries/freqtrade.md`](libraries/freqtrade.md) | current | no | library-specific research | Before planning exchange-operator workflows, anti-bias tooling, or crypto-first runtime breadth. | Advisory dossier for the crypto trading platform with backtest, dry-run, and live workflows. |
| [`libraries/lumibot.md`](libraries/lumibot.md) | current | no | library-specific research | Before planning same-code backtest/live UX or broker-facing Python strategy ergonomics. | Advisory dossier for the Python library that emphasizes same-code backtesting and live trading. |
| [`libraries/pybroker.md`](libraries/pybroker.md) | current | no | library-specific research | Before planning multi-symbol research workflows, ML integration, or walk-forward-oriented backtest UX. | Advisory dossier for the research framework that combines rule-based and model-based workflows. |
