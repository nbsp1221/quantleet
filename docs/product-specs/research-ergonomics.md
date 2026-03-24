# Research Ergonomics Spec

## Status

- Status: `implemented`
- Class: `product-spec`
- Scope: the current implemented `research` usability surface on top of the backtest MVP

Related documents:

- [../design-docs/quantcraft-architecture.md](../design-docs/quantcraft-architecture.md)
- [../design-docs/architecture-governance.md](../design-docs/architecture-governance.md)
- [backtest-mvp.md](backtest-mvp.md)
- [../research/2026-03-23-python-quant-library-landscape.md](../research/2026-03-23-python-quant-library-landscape.md)

This document defines the canonical current implemented-scope contract for the shipped `research ergonomics` surface that sits on top of the backtest MVP.

## Goal

Build a usable research surface on top of the current backtest kernel so that:

- a user can write a first strategy and run a backtest within 5 to 10 minutes
- future agent work extends one coherent strategy, series, indicator, and result surface
- research usability improves without forking or weakening the existing `trading` semantics

## Why This Slice Exists

`quantcraft` already has a deterministic single-symbol backtest MVP, but it is still weak compared with established Python backtesting libraries in the following areas:

- strategy-writing ergonomics
- time-series access surface
- indicator surface
- result interpretation surface
- examples and quickstart experience

This slice focuses on making the current kernel legible and reusable rather than adding more execution complexity.

## Included Scope

### Research Usability Surface

- a user-facing `Strategy` contract for research workflows
- series access through a controlled read-only view
- a small official helper surface
- a small official indicator baseline
- an expanded backtest result surface
- official examples
- a canonical quickstart document and notebook

### Explicitly Out Of Scope

This slice does not include:

- plotting
- parameter sweeps
- walk-forward tooling
- dedicated anti-bias diagnostics tooling
- paper trading
- live trading
- a plotting subsystem
- guaranteed fallback behavior when `TA-Lib` is unavailable

## Official Import Surface

The official user-facing research ergonomics surface lives under `quantcraft.research`.

Recommended import:

```python
from quantcraft.research import Strategy, ta, qc, run_backtest
```

This slice does not promote:

- root-level kitchen-sink imports such as `from quantcraft import ta, qc`
- a fragmented public surface spread across many submodules

## Strategy Contract

### Strategy Type

The user-facing strategy surface is an abstract base class named `Strategy`.

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
- `self.buy()`
- `self.sell()`
- `ta.*`
- `qc.*`

Current order semantics for this slice:

- `buy()` and `sell()` currently require an explicit `symbol=...` argument
- `buy()` means long entry or long increase
- `sell()` means long exit in the current long-only MVP scope, not short entry

Examples and quickstarts must explain that `sell()` is an exit operation in the current scope.

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
            self.buy(symbol=bar.symbol, quantity=1)
        elif qc.crossunder(self.fast, self.slow):
            self.sell(symbol=bar.symbol, quantity=1)
```

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

The public indicator contract is owned by `quantcraft` and exposed through `ta.*`.

The approved baseline signatures are:

- `ta.sma(series, length=20)`
- `ta.ema(series, length=20)`
- `ta.rsi(series, length=14)`
- `ta.atr(high, low, close, length=14)`
- `ta.cci(high, low, close, length=20)`
- `ta.bollinger_bands(series, length=20, stddev=2)`
- `ta.macd(series, fast=12, slow=26, signal=9)`

Rules:

- the public contract belongs to `quantcraft`
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
- `bollinger_bands`

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

- `ta.bollinger_bands(...)`
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

This slice upgrades the result surface to a medium baseline.

Required result content:

- trade log
- equity curve
- final balance
- final equity
- total return
- max drawdown
- total trades
- win rate
- average win
- average loss
- profit factor
- simple exposure summary

This slice does not attempt a large analytics surface such as:

- Sharpe
- Sortino
- Calmar
- rolling performance statistics
- optimizer-specific result objects
- walk-forward-specific result objects

## Examples And Quickstart

### Shipped Canonical Example Set

The shipped canonical example strategy set for this slice is:

1. `SMA crossover`
2. `RSI 30/70 mean reversion`

Other implemented indicators, including `bollinger_bands` and `macd`, remain part of the supported API surface, but they are not part of the current canonical example set.

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
- lower-layer setup imports used to construct example input data must be labeled as supporting setup types, not as part of the `quantcraft.research` public import surface

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
4. call `run_backtest(...)`
5. inspect the summary and result object
6. inspect equity curve and trade log in the notebook

## Success Criteria

This slice is successful only if all of the following are true:

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
   - `bollinger_bands`

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

## Harness Constraints

This slice must preserve the following harness rules:

1. keep continuity with the already approved `Strategy` and backtest kernel direction
2. do not let agents normalize direct `talib`, `pandas`, or `numpy` usage inside canonical strategy examples
3. keep bias protection expressible in API contracts and tests
4. do not duplicate `trading` semantics inside `research`
5. treat quickstart as a standard usage path, not a throwaway tutorial
