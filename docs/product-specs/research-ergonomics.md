# Research Ergonomics Spec

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope: the current implemented `research` usability surface on top of the backtest MVP

Related documents:

- [../design-docs/quantleet-architecture.md](../design-docs/quantleet-architecture.md)
- [../design-docs/architecture-governance.md](../design-docs/architecture-governance.md)
- [backtest-mvp.md](backtest-mvp.md)
- [backtest-plotting.md](backtest-plotting.md)
- [parameter-exploration.md](parameter-exploration.md)
- [order-sizing.md](order-sizing.md)
- [../research/2026-03-23-python-quant-library-landscape.md](../research/2026-03-23-python-quant-library-landscape.md)
- [../research/libraries/backtesting-py.md](../research/libraries/backtesting-py.md)

This document defines the canonical current implemented-scope contract for the
shipped `research ergonomics` surface that sits on top of the backtest MVP. It
also records the first public beta target; beta-target language is direction,
not a claim that the current implementation already satisfies it.

## Goal

Build a usable research surface on top of the current backtest kernel so that:

- a user can write a first strategy and run a backtest within 5 to 10 minutes
- the first public beta is credible for general Python quant users who want to
  backtest one strategy on one tradeable asset
- future agent work extends one coherent strategy, series, indicator, and result surface
- research usability improves without forking or weakening the existing `trading` semantics

## Why This Slice Exists

`quantleet` already has a deterministic single-symbol backtest MVP, but it is still weak compared with established Python backtesting libraries in the following areas:

- strategy-writing ergonomics
- time-series access surface
- indicator surface
- result interpretation surface
- examples and quickstart experience

This slice focuses on making the current kernel legible and reusable rather than adding more execution complexity.

For the first beta, `backtesting.py` is the near-term UX comparator. The target
is not to copy its internals or abandon the shared-kernel direction; it is to
make the single-symbol "test my strategy" workflow comparably useful for a
general Python quant user. `NautilusTrader` remains a longer-term architectural
reference for paper/live parity, not the beta feature checklist.

## Included Scope

### Research Usability Surface

- a user-facing `Strategy` contract for research workflows
- series access through a controlled read-only view
- a small official helper surface
- a small official indicator baseline
- an expanded backtest result surface
- constrained first-beta parameter exploration through `ParameterStudy`
- official examples
- a canonical quickstart document and notebook

### Remaining Deferred Scope

The current implemented slice now includes readable result reporting, a basic
`result.plot()` workflow, and constrained first-beta parameter exploration. It
still does not include:

- walk-forward tooling
- dedicated anti-bias diagnostics tooling
- paper trading
- live trading
- guaranteed fallback behavior when `TA-Lib` is unavailable

These items are not all equally deferred. For the first beta, richer examples,
fresh install guidance, and release metadata/documentation cleanup remain product
gaps to close before broad public positioning. The first-beta parameter
exploration contract is governed by
[parameter-exploration.md](parameter-exploration.md). Paper trading and live
trading stay outside the first beta.

## Official Import Surface

The official user-facing research ergonomics surface lives under `quantleet.research`.
The canonical strategy authoring base lives under `quantleet.strategy`.
The canonical backtest runtime surface lives under `quantleet.backtest`.

Recommended import:

```python
from quantleet.backtest import BacktestEngine
from quantleet.research import ParameterStudy, ta, qc
from quantleet.strategy import Strategy
```

This slice does not promote:

- root-level kitchen-sink imports such as `from quantleet import ta, qc`
- root-level `Strategy` imports

### Backtest Entry Surface

The preferred public execution entry for the current research workflow is:

- `quantleet.backtest.BacktestEngine`

Approved execution paths:

- `BacktestEngine(...).run(bars=..., strategy=StrategyClass, config=...)`
- `BacktestEngine(...).run(source=..., strategy=StrategyClass, config=...)`

Current rules:

- `bars` must be `quantleet.data.BarSeries`
- the canonical single-bar type is `quantleet.data.TimeBar`
- `BarSeries.rows` must be `tuple[quantleet.data.TimeBar, ...]`
- `source.load()` returns `BarSeries`
- the engine does not expose public `bar_type`
- the current historical backtest path fixes bar type internally to `time`

`run_backtest(...)` is not part of the public surface for this slice.

### Initial Canonical User Journeys

The current shipped `research` usability surface should stay anchored to a small set of canonical user journeys.

These journeys exist so future docs, examples, benchmarks, and automation stay tied to real library use rather than easier surrogate tasks.
They are reference workflows, not automatically all strict merge gates.

#### 1. Clean Install To Public Imports

- starting state: a fresh environment with the package installed
- user intent: confirm the documented public imports work exactly as presented
- success artifact: importing `BacktestEngine`, `Strategy`, `ta`, `qc`, `BarSeries`, `TimeBar`, and the documented data sources from their documented capability paths works cleanly
- superficially passing but still bad: the package installs, but the documented public import paths drift

#### 2. DataFrame-Like Quickstart To First Backtest

- starting state: the canonical `DataFrameDataSource` quickstart path
- user intent: reach a first successful backtest with minimal setup
- success artifact: the documented quickstart flow runs and produces a `BacktestResult`
- superficially passing but still bad: the example still needs hidden setup or undocumented assumptions

#### 3. Materialized `BarSeries` To `BacktestEngine.run(bars=...)`

- starting state: user-created `TimeBar` and `BarSeries`
- user intent: run the engine from explicit materialized historical bars
- success artifact: `BacktestEngine.run(bars=..., strategy=StrategyClass, config=...)` works with the documented canonical types
- superficially passing but still bad: the path only works because docs or code silently rely on lower-layer internals

#### 4. Exchange-Backed Historical Research Flow

- starting state: the documented `CCXTDataSource` historical path
- user intent: load historical bars and run a research workflow through `BacktestEngine.run(source=...)`
- success artifact: the documented exchange-backed flow remains coherent and reproducible enough for humans and agents to follow
- superficially passing but still bad: the path remains "documented" but becomes too hidden, flaky, or environment-dependent to serve as a trustworthy reference workflow

## Strategy Contract

### Strategy Type

The user-facing strategy surface is an abstract base class named `Strategy`.
Its canonical import path is `quantleet.strategy.Strategy`.

Users define strategies by subclassing `Strategy`.

The approved public lifecycle hooks for this slice are:

- `init()`
- `on_bar()`

This slice does not add:

- `on_start()`
- `on_finish()`
- other runtime lifecycle hooks

### Strategy Responsibilities

Approved public surface:

- `self.data.*`
- `self.position`
- `self.buy()`
- `self.sell()`
- `ta.*`
- `qc.*`

Current order semantics for this slice:

- `buy()` and `sell()` accept explicit `symbol=...` everywhere they are allowed
- `buy()` and `sell()` accept exactly one sizing mode:
  - `quantity=...`
  - `qty_percent=...`
- `buy()` and `sell()` accept `stop_price=...` when
  `order_type="stop_market"` or `order_type="stop_limit"`
- `buy()` and `sell()` accept `limit_price=...` when `order_type="limit"` or
  `order_type="stop_limit"`
- in the current single-symbol `on_bar()` workflow, `buy()` and `sell()` may
  omit `symbol`; the helper infers the active `bar.symbol`
- in the current shipped single-symbol backtest, any explicit `symbol=...`
  should match the active series symbol
- `buy()` means long entry or long increase
- `sell()` means long exit in the current long-only MVP scope, not short entry
- `sell()` while flat is treated as a no-op in the current long-only backtest path
- `qty_percent` uses current executable sizing resources for the requested
  direction rather than portfolio-target semantics
- for `stop_market`, the strategy surface infers runtime `trigger_condition`
  from the active closed-bar `close`; users do not supply `trigger_condition`
  directly
- `qty_percent` is supported for `market`, `limit`, `stop_market`, and
  `stop_limit`; it is resolved to concrete quantity before runtime order
  creation

Examples and quickstarts must explain that `sell()` is an exit operation in the current scope.

### Strategy Position View

The approved public strategy-state view is:

- `self.position`

`self.position` is a small read-only runtime view that is meaningful for strategy decisions in `on_bar()`.

Approved fields:

- `self.position.is_open`
- `self.position.quantity`
- `self.position.average_entry_price`

Flat-state semantics:

- `self.position.is_open == False`
- `self.position.quantity == 0.0`
- `self.position.average_entry_price == 0.0`

This slice does not expose:

- account objects
- portfolio objects
- `cash`
- `equity`
- `market_value`
- `unrealized_pnl`

### Strategy Initialization And Evaluation

The lifecycle split is:

- `init()` is for one-time strategy preparation
- `on_bar()` is for signal evaluation and order decisions

Rules:

- `init()` may prepare indicator bindings and internal strategy state
- `init()` must not create orders
- order decisions must happen in `on_bar()`

Recommended pattern:

```python
class SmaCross(Strategy):
    def init(self):
        self.fast = ta.sma(self.data.close, length=10)
        self.slow = ta.sma(self.data.close, length=20)

    def on_bar(self, bar):
        if qc.crossover(self.fast, self.slow):
            self.buy(quantity=1)
        elif qc.crossunder(self.fast, self.slow):
            self.sell(quantity=1)
```

Explicit `symbol=...` remains supported for compatibility. In the current
single-symbol backtest path, it should still match the active series symbol.

Indicator bindings created in `init()` are not frozen snapshots. They are causal read-only views whose latest value updates with the current backtest time.

### User Freedom Inside Strategy Classes

The official contract is documented using `self.data.*`, but user-authored strategy classes are not forbidden from creating local aliases or bound indicator attributes such as:

```python
self.close = self.data.close
self.rsi14 = ta.rsi(self.data.close, length=14)
```

Those aliases are user implementation choices, not part of the public contract.

Canonical docs and examples should still prefer `self.data.*` as the primary documented surface.

## Series Contract

### SeriesView

Public time-series data must not expose raw `pandas.Series` or raw `numpy.ndarray` objects directly.

The slice uses a small read-only causal series abstraction, referred to here as `SeriesView`.

Core rules:

- read-only
- no mutation
- no future access
- the same series contract is shared between strategy logic and indicators

### Indexing Semantics

Official indexing semantics:

- `series[0]` = current confirmed value at the current `on_bar()` step
- `series[1]` = previous confirmed value
- `series[2]` = the one before that
- negative indexing is not allowed

This keeps the mental model close to Pine-style history references while preserving explicit bias guards.

### Minimal Interface

The approved minimal public interface is:

- `series[index]`
- `len(series)`
- `series.latest`
- `series.is_empty`

This slice does not expose:

- slicing
- arbitrary iteration as a public contract
- raw array export
- direct pandas/numpy views
- broad arithmetic or comparison operator overloading

Additional rules:

- `series.latest` is equivalent in meaning to `series[0]`
- `len(series)` means the number of currently visible confirmed values
- `len(series)` is a secondary convenience, not the primary user mental model
- examples and quickstarts should prefer `series[0]`, `series[1]`, and `qc.is_na(...)` over `len(series)`

### Missing History And Warmup Semantics

When history is insufficient or an indicator warmup period is incomplete:

- the public concept is `na`
- the default concrete representation is `NaN`
- users should check with `qc.is_na(...)`, not with ad-hoc `value != value` patterns

Rules:

- insufficient-history regions must not be replaced with `0` or any optimistic default
- canonical examples and quickstarts should model `na` checks explicitly where needed

## Indicator Contract

### Public Surface

Users should not import third-party indicator libraries directly as the canonical research path.

The public indicator contract is owned by `quantleet` and exposed through `ta.*`.

The approved baseline signatures are:

- `ta.sma(series, length=20)`
- `ta.ema(series, length=20)`
- `ta.rsi(series, length=14)`
- `ta.atr(high, low, close, length=14)`
- `ta.cci(high, low, close, length=20)`
- `ta.bb(series, length=20, stddev=2)`
- `ta.macd(series, fast=12, slow=26, signal=9)`

Rules:

- the public contract belongs to `quantleet`
- `TA-Lib` semantics are the canonical truth for warmup, lookback, seed, and `NaN` behavior
- internal implementations may wrap `TA-Lib` or another calculation backend
- external dependencies are implementation details, not public API ownership
- the baseline does not allow multiple argument aliases such as `period`, `window`, or `n`

### Usage Style

Indicators should be used as functions:

- preferred: `ta.rsi(self.data.close, length=14)`
- not preferred: `self.rsi(...)` or `self.indicators.rsi(...)`

This keeps responsibilities clear between:

- strategy object
- data surface
- indicator surface
- order surface

### Lookahead And Visibility Rules

Lookahead protection belongs to the series visibility contract, not to whether a user called a method or a function.

Rules:

- eager precomputation is allowed internally
- public indicator results must still behave as if only the current causal prefix is visible
- `ta.*` takes causal read-only series inputs
- `ta.*` returns causal read-only series outputs

### Caching Rules

Indicator caching is an internal optimization, not a user-facing semantic guarantee.

Rules:

- users may call the same indicator repeatedly
- internal implementations may cache identical calls
- examples and quickstarts should still prefer binding indicators once and reusing them
- this slice does not add user-facing `cache=True/False` indicator arguments

### Official Baseline Indicators

The implemented baseline indicator API for this slice is:

- `sma`
- `ema`
- `rsi`
- `macd`
- `atr`
- `cci`
- `bb`

Canonical shipped quickstart assets currently demonstrate:

- `sma`
- `rsi`

Other implemented baseline indicators are part of the supported API surface, but they are not all required to appear in the first shipped quickstart examples.

This slice explicitly does not baseline:

- `stochastic`
- `adx`
- `supertrend`
- `ichimoku`
- `sar`
- `obv`
- `mfi`

### Multi-Output Indicator Results

Multi-output indicators must return named result objects, not tuples or dicts.

Applies to:

- `ta.bb(...)`
- `ta.macd(...)`

Rules:

- each field is accessed by name
- each field is itself a causal read-only series
- tuple ordering must not become part of the public contract
- dict-style access must not become part of the public contract

Approved field names:

`BollingerBandsResult`

- `upper`
- `middle`
- `lower`

`MACDResult`

- `macd`
- `signal`
- `histogram`

## Helper Contract

The helper surface should remain small.

Approved helpers:

- `qc.is_na(x)`
- `qc.crossover(a, b)`
- `qc.crossunder(a, b)`

Rules:

- helpers may accept scalars or causal series inputs
- helper semantics must still be causal at the current time step
- broad arithmetic and comparison overloading should not be used as the primary user model

## Result Surface

This slice upgrades the result surface to a medium baseline. The first-beta
inspection path is `result.report`; legacy `result.summary`, `result.trade_log`,
and `result.equity_curve` remain available for compatibility and low-level
inspection.

Required result content:

- direct `result.report` access from engine-produced `BacktestResult` values
- grouped human-readable report text
- typed structured report sections for run identity, execution assumptions,
  returns, risk, trades, costs, exposure, equity rows, fills, closed trades, and
  order rejections
- trade log
- equity curve
- final balance
- final equity
- total return
- max drawdown
- total trades
- total fills
- win rate
- average win
- average loss
- profit factor
- simple exposure summary

Current summary semantics for the implemented slice:

- `total_trades` means closed trades, not raw fills
- `total_fills` means the raw fill count from `trade_log`
- `win_rate`, `average_win`, `average_loss`, and `profit_factor` are based on net closed-trade PnL after fees

Current beta report semantics:

- `BacktestEngine.run(..., label=...)` may attach a user-visible run label
- `Strategy.display_name` is the explicit human-readable strategy identity hook
- reportable execution config comes from the materialized `StrategyConfig`
  snapshot
- execution assumptions use stable structured identifiers:
  `next_bar`, `conservative_ohlcv`, and `mark_to_market`
- undefined report metrics use `None` structurally and `n/a` in human-readable
  text
- report exposure counts bars where a positive position existed at any point
  during the bar

This slice does not attempt a larger analytics surface such as:

- Sortino
- Calmar
- rolling performance statistics
- optimizer-specific result objects
- walk-forward-specific result objects

For the first beta, result inspection must become a product workflow rather
than only a dataclass contract: readable stats, analysis-friendly trade/equity
access, and one basic price/fill/equity plot are required before broad beta
positioning. The plotting contract is governed by
[backtest-plotting.md](backtest-plotting.md).

## Examples And Quickstart

### Shipped Canonical Example Set

The shipped canonical example strategy set for this slice is:

1. `SMA crossover`
2. `RSI 30/70 mean reversion`

Other implemented indicators, including `bb` and `macd`, remain part of the supported API surface, but they are not part of the current canonical example set.

For the first beta, add examples only where they close first-run confusion:
one stop-family example and one `qty_percent` example are enough. Do not add
examples that imply unsupported multi-symbol, shorting, leverage, paper, or live
scope.

### Example Placement

Example strategies must not live inside `src/`.

They belong in:

- the quickstart doc
- the quickstart notebook
- or a separate example artifact area outside the source package

The source package and the educational artifact surface must remain separate.

### Canonical Quickstart Form

The canonical quickstart is:

- a short document
- plus a notebook

Rules:

- the document is the system of record
- the notebook is an executable supporting artifact
- the notebook must not define a competing contract
- lower-layer setup imports used to construct example input data must be labeled as supporting setup types, not as part of the `quantleet.research` public import surface

### Canonical Quickstart Examples

- primary example: `SMA crossover`
- secondary example: `RSI 30/70 mean reversion`

Rules:

- canonical examples and quickstart examples must always specify order size explicitly
- the default teaching example should use `quantity=1`
- this slice must not introduce an implicit default size or a future sizing abstraction into the public examples

### Canonical Quickstart Flow

The quickstart should walk through this flow:

1. subclass `Strategy`
2. bind indicators in `init()`
3. evaluate signals and place orders in `on_bar()`
4. create a `BacktestEngine(...)`
5. call `engine.run(...)`
6. inspect `result.report`
7. inspect legacy summary, equity curve, and trade log in the notebook when
   lower-level details are needed

For the first beta, the quickstart should also show the shortest supported path
from common user-owned tabular data to a readable result. It should avoid
forcing users to understand the full architecture before their first backtest.

## Success Criteria

The current implemented slice is successful only if all of the following are true:

1. `Strategy` ergonomics are implemented
   - abstract base class
   - `init()` / `on_bar()`
   - `self.data.*`
   - `self.buy()` / `self.sell()`

2. `SeriesView` and helper surface are implemented
   - `series[0]`
   - `len(series)`
   - `series.latest`
   - `series.is_empty`
   - `qc.is_na`
   - `qc.crossover`
   - `qc.crossunder`

3. the baseline `ta.*` indicators are implemented
   - `sma`
   - `ema`
   - `rsi`
   - `macd`
   - `atr`
   - `cci`
   - `bb`

4. the result surface is expanded to the approved medium baseline

5. the canonical quickstart exists
   - short document
   - notebook
   - primary example: `SMA crossover`
   - secondary example: `RSI 30/70 mean reversion`
   - no requirement that every implemented baseline indicator appear in the first shipped canonical examples

6. acceptance tests exist for:
   - lookahead-safe usage
   - warmup / `na` behavior
   - executable canonical quickstart flow

Before broad beta positioning, the docs and product surface must still support
a fresh install path, constrained parameter exploration, richer examples, and
explicit unsupported-scope notes for multi-symbol, shorting, leverage, paper,
and live trading. The current implementation already supports readable result
inspection and a basic plot.

## Harness Constraints

This slice must preserve the following harness rules:

1. keep continuity with the already approved `Strategy` and backtest kernel direction
2. do not let agents normalize direct `talib`, `pandas`, or `numpy` usage inside canonical strategy examples
3. keep bias protection expressible in API contracts and tests
4. do not duplicate `trading` semantics inside `research`
5. treat quickstart as a standard usage path, not a throwaway tutorial
