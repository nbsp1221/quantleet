# Python Quant And Backtesting Library Landscape (2026)

## Status

- Status: `current`
- Class: `research`
- Canonical: `no`
- Role: `overview`
- Last reviewed: `2026-03-23`

This document is a research artifact, not a system-of-record implementation contract.

Use it to inform future design or roadmap decisions. If a conclusion from this report should affect implementation, promote it into a canonical product spec, design doc, or execution plan first.

For deeper library-specific detail, use this overview together with the priority dossiers in [`docs/research/libraries/`](libraries/).

## Purpose

This report compares `quantcraft` against notable open-source Python quant, backtesting, and trading frameworks as of March 23, 2026.

It is intended to answer four questions:

1. What does `quantcraft` already have today?
2. What do popular open-source Python libraries provide that `quantcraft` does not yet provide?
3. How does `quantcraft` differ in usability and product positioning?
4. Which next priorities are most defensible for `quantcraft`?

## Scope And Method

This report focuses on open-source Python libraries and Python-first frameworks, not hosted commercial platforms.

Research inputs:

- `quantcraft` repository docs and current implemented code
- project documentation and GitHub repositories for selected libraries
- shallow local inspections of selected upstream repositories in `/tmp`
- public release and maintenance signals visible on March 23, 2026

Local inspection roots used in this pass:

- `/tmp/quantcraft-lib-research/`
  - `backtesting.py`
  - `backtrader`
  - `bt`
  - `pybroker`
  - `vectorbt`
- `/tmp/quantcraft-frameworks/`
  - `freqtrade`
  - `lumibot`
  - `nautilus_trader`
  - `qstrader`
  - `zipline`
  - `zipline-reloaded`

`aat` was included as a public-repo architectural reference, but not as a locally cloned code inspection target in this pass.

Observed upstream snapshots used during this pass:

| Library | Observed snapshot note |
| --- | --- |
| `backtesting.py` | latest visible tag `0.6.5`; recent visible commit activity in late 2025 |
| `Backtrader` | inspected visible upstream commit `b853d7c` on 2023-04-19 |
| `vectorbt` | latest visible release `0.28.4` on 2026-01-26; recent visible commit activity on 2026-03-19 |
| `bt` | latest visible release `1.1.3`; recent visible commit activity on 2026-03-21; docs freshness appears mixed |
| `PyBroker` | latest visible release `1.2.12` on 2026-03-05; recent visible commit activity on 2026-03-05 |
| `NautilusTrader` | inspected visible upstream commit `ae3bc93` on 2026-03-22 |
| `Zipline-Reloaded` | inspected visible upstream commit `943010b` on 2025-11-13 |
| `Zipline` | inspected visible upstream commit `014f1fc` on 2020-10-14 |
| `QSTrader` | inspected visible upstream commit `e6d86a3` on 2018-12-21 |
| `Lumibot` | inspected visible upstream commit `d2b0158` on 2026-03-17; visible tag `v4.4.56` |
| `Freqtrade` | inspected visible upstream commit `250156f` on 2026-03-22; visible dev version `2026.3-dev` |
| `aat` | used as a smaller architectural reference; this pass relied on public repo/docs positioning rather than a locally cloned code audit |

Selected comparison set:

- `backtesting.py`
- `Backtrader`
- `vectorbt`
- `bt`
- `PyBroker`
- `NautilusTrader`
- `Zipline-Reloaded`
- `QSTrader`
- `Lumibot`
- `Freqtrade`
- `aat`

## Quantcraft Current Baseline

Current `quantcraft` scope is intentionally narrow.

Important scope note:

- current implemented-scope product authority is routed through
  [the product-spec index](../product-specs/index.md)
- [market-data.md](../product-specs/market-data.md) is one implemented-scope
  entry, not the sole product authority
- an implemented in-repo backtest baseline exists and is aligned to the approved [Backtest MVP](../product-specs/backtest-mvp.md) slice
- the first public beta target has now been promoted into [Research Ergonomics](../product-specs/research-ergonomics.md)
- this report compares both the current market-data footing and the newly implemented backtest slice, but it does not redefine the canonical product-scope map

Canonical references:

- [ARCHITECTURE.md](../../ARCHITECTURE.md)
- [Backtest MVP](../product-specs/backtest-mvp.md)
- [Research Ergonomics](../product-specs/research-ergonomics.md)
- [BacktestEngine](../../src/quantcraft/backtest/engine.py)
- [strategy.py](../../src/quantcraft/research/strategy.py)
- [execution_model.py](../../src/quantcraft/backtest/execution_model.py)
- [matching.py](../../src/quantcraft/trading/domain/matching.py)
- [state.py](../../src/quantcraft/trading/domain/state.py)

In-repo today, `quantcraft` includes an implemented backtest baseline that provides:

- deterministic single-symbol backtesting
- OHLCV external input format
- OHLCV to synthetic L2/tick conversion
- explicit gap semantics
- explicit conservative intrabar path rules
- tick/event-driven internal kernel with a bar-facing strategy surface
- `self`-based `on_bar` strategy API
- `market`, `limit`, `stop_market`, and `stop_limit` orders
- explicit `quantity` and `qty_percent` sizing
- conservative resource reservation for accepted active and dormant orders
- a baseline indicator/helper surface under `quantcraft.research`
- long-only, `1x`, spot-like state transitions
- injected slippage and fee configuration
- trade log, PnL, and ending equity summary
- repository-local harnessing intended for AI-agent-driven development

Current hard limitations:

- single symbol only
- single timeframe only
- no shorting
- no leverage or margin
- no trailing / bracket orders
- no cancel / modify / replace lifecycle
- no user-visible partial fills
- no paper-trading runtime
- no live-trading runtime
- no portfolio rebalancing layer
- no optimizer / walk-forward / parameter sweep system
- no first-class plotting or charting layer

## Ecosystem Clusters

The Python ecosystem is not one uniform category. It splits into several distinct camps.

### 1. Research-first, candle-native tools

Representative projects:

- `backtesting.py`
- `vectorbt`
- `Freqtrade`
- `QSTrader`

Typical properties:

- centered on OHLCV/bar workflows
- optimized for signal testing, parameter sweeps, and reporting
- often simpler execution semantics than a live-parity engine
- usually much stronger than `quantcraft` on convenience today

### 2. Hybrid event/bar engines

Representative projects:

- `Backtrader`
- `Zipline-Reloaded`
- `Lumibot`

Typical properties:

- imperative event-loop APIs
- richer order models
- often support some live integration story
- still heavily bar-centric in real usage

### 3. Research-to-live parity engines

Representative projects:

- `NautilusTrader`
- `aat`

Typical properties:

- stronger emphasis on one engine across research and live
- more realistic execution and market modeling
- heavier operational and architectural footprint

`quantcraft` already sits closer to the third camp in intent, even though its current feature surface is still much smaller than the first two camps.

## Priority Dossiers

These dossiers hold the deeper per-library architectural notes for this research pass:

| Library | Dossier |
| --- | --- |
| `backtesting.py` | [`libraries/backtesting-py.md`](libraries/backtesting-py.md) |
| `Backtrader` | [`libraries/backtrader.md`](libraries/backtrader.md) |
| `vectorbt` | [`libraries/vectorbt.md`](libraries/vectorbt.md) |
| `NautilusTrader` | [`libraries/nautilustrader.md`](libraries/nautilustrader.md) |
| `Freqtrade` | [`libraries/freqtrade.md`](libraries/freqtrade.md) |
| `Lumibot` | [`libraries/lumibot.md`](libraries/lumibot.md) |
| `PyBroker` | [`libraries/pybroker.md`](libraries/pybroker.md) |

## Comparison Matrix

| Library | Core Style | Backtest | Paper/Live Story | Order Realism | Research UX | Current Breadth vs quantcraft |
| --- | --- | --- | --- | --- | --- | --- |
| quantcraft | tick/event kernel with bar-facing API | implemented single-symbol baseline | not yet | moderate in current slice, stronger long-term direction than current breadth | low to moderate | baseline |
| backtesting.py | bar-native imperative | yes | no | moderate | high | much broader today |
| Backtrader | hybrid event/bar | yes | yes | moderate to high | moderate | much broader today |
| vectorbt | vectorized/dataframe-first | yes | limited | low to moderate | very high | much broader today |
| bt | portfolio/rebalance framework | yes | no | low | moderate | broader for portfolio allocation |
| PyBroker | research/ML platform | yes | limited | moderate | high | much broader today |
| NautilusTrader | event-driven parity engine | yes | yes | very high | moderate | far broader and deeper |
| Zipline-Reloaded | event-driven research engine | yes | limited | moderate | moderate | broader research stack |
| QSTrader | event-driven backtester | yes | weak | low to moderate | low to moderate | similar size historically, weaker modern harness |
| Lumibot | hybrid event/live platform | yes | yes | high | moderate | much broader today |
| Freqtrade | crypto trading platform | yes | yes | moderate | high for crypto users | much broader today |
| aat | event-driven algo engine | yes | yes | moderate to high | lower | architecturally relevant reference |

## Maintenance And Activity Signals

These signals are directional, not exhaustive. They are based on docs and repository state visible on March 23, 2026.

| Library | Observed Signal |
| --- | --- |
| backtesting.py | healthy recent activity; latest visible tag `0.6.5`, with visible commit activity in late 2025 |
| Backtrader | broad feature set but appears comparatively stale relative to newer projects |
| vectorbt | strong recent activity and recent release cadence, with visible 2026 activity |
| bt | code activity looks current, though docs freshness appears uneven |
| PyBroker | recent release and active visible development signals |
| NautilusTrader | very active and clearly evolving, with visible activity on 2026-03-22 |
| Zipline-Reloaded | maintained, but reads more like ecosystem continuation than a frontier engine |
| QSTrader | historically important, appears comparatively dormant |
| Lumibot | active 2026-era parity and broker/product work |
| Freqtrade | highly active and operations-heavy, with visible activity on 2026-03-22 |
| aat | relevant architecturally, but lower mindshare than the leaders above |

## Where Quantcraft Is Already Strong

Relative to its size, `quantcraft` already has several unusually strong properties:

- a documented shared-kernel direction across backtest, paper, and live
- explicit anti-lookahead rules
- explicit gap semantics
- explicit conservative intrabar path policy
- a path from OHLCV to synthetic L2 rather than a pure candle-native engine
- a repository-local agent-first harness that keeps architecture and docs legible for future AI work

This combination is less common among user-friendly incumbents, even when individual pieces exist elsewhere.

## Where Quantcraft Is Weak Today

Compared to the ecosystem, the biggest current gaps are straightforward.

### Feature gaps

- no multi-symbol support
- no multi-timeframe support
- no shorting or leverage
- no trailing / bracket orders
- no cancel / modify lifecycle
- no portfolio layer
- no paper/live runtime

### Research workflow gaps

- limited built-in indicator surface compared with mature research libraries
- no optimizer / hyperparameter sweep layer
- no walk-forward tooling
- no rich statistics or charting package
- no notebook-oriented convenience layer beyond the MVP core

### Usability gaps

- strategy ergonomics are usable but not yet competitive with polished
  single-asset tools
- no “batteries included” examples comparable to mature libraries
- no polished visualization or reporting workflow
- no broad data adapter story beyond the current ingestion baseline

### Ecosystem gaps

- no broker/exchange adapter surface beyond current market-data work
- no community recipe/catalog surface
- no advanced operational tooling

## Usability Differences

The biggest usability difference is that incumbent libraries usually optimize for immediate user convenience, while `quantcraft` currently optimizes for future semantic integrity.

That creates a real trade-off.

What incumbents often do better today:

- easier first-run experience
- more indicators and examples
- charts and reports out of the box
- more obvious portfolio/research workflows

What `quantcraft` is already better positioned to do:

- explain exactly why an order did or did not fill
- preserve one coherent engine model as the project expands toward paper/live
- keep agent-generated implementation inside a more legible architectural frame

In short:

- incumbents win on immediate UX/DX breadth
- `quantcraft` is betting on correctness-oriented architecture and future parity

## Strategic Interpretation

The strongest competitive opening for `quantcraft` is not “be bigger than everyone else.”

The intended differentiation is:

- eventually easier to use than heavy parity engines like `NautilusTrader`
- more semantically rigorous than bar-native convenience tools like `backtesting.py`
- more explicit about backtest-to-live causality than crypto-first operators like `Freqtrade`

That suggests a clear product posture:

- stay narrow on breadth for now
- make the first beta competitive for single-symbol strategy backtesting before
  widening runtime scope
- deepen the bar-facing UX on top of the tick/event kernel
- make execution explainability a visible product feature
- prove paper-trading parity after the beta backtesting loop is credible

## Recommended Next Priorities

These priorities are research recommendations only. The first-beta direction
has been promoted into [Research Ergonomics](../product-specs/research-ergonomics.md);
that spec governs product work.

### Must

- make the single-symbol first-run flow competitive for general Python quant users
- improve summaries, plotting, trade/equity inspection, and notebook-oriented reporting
- add constrained parameter exploration for common strategy tuning
- keep execution assumptions and fill causality visible in user-facing docs

### Should

- add execution explainability artifacts such as synthetic-path traces, fill provenance, and cost breakdowns
- build the thinnest credible paper-trading runtime on the same kernel after the beta backtesting loop is credible
- add multi-symbol support only after the single-symbol UX and runtime semantics are stable

### Not now

- broad broker coverage
- giant indicator catalog
- ML-first product expansion
- portfolio-rebalancing abstractions as the core identity

## Practical Notes

License posture in the comparison set is mixed and matters if `quantcraft` wants to borrow ideas but avoid entanglement.

Examples:

- `bt`: MIT
- `backtesting.py`: AGPL-3.0
- `Backtrader`: GPL-3.0
- some modern projects use source-available or mixed licensing

This makes architectural learning safer than direct code borrowing.

## Conclusion

`quantcraft` is not feature-competitive yet with the major Python incumbents.

It is already architecturally differentiated.

Today, `quantcraft` should be understood as:

- weaker on breadth
- weaker on convenience
- stronger than expected on explicit execution semantics and long-term kernel direction

The best next move is not trying to catch every incumbent feature.
The best next move is making the current semantic advantage visible and usable.
