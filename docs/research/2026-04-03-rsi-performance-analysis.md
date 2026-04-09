# RSI Performance Analysis (2026-04-03)

## Status

- Status: `current`
- Class: `research`
- Canonical: `no`
- Last reviewed: `2026-04-03`

This document captures the current-state evidence behind the active RSI
performance optimization plan. It is an advisory analysis artifact, not a
system-of-record product contract.

## Question

Why did the canonical RSI benchmark miss the explicit perf gate at planning
time, and what shared indicator-runtime patterns from other libraries were most
useful for the completed fix?

## Baseline Gate State At Planning Time

Canonical gate:

- command: `uv run poe perf-check`
- fixture: `tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv`
- scenario: RSI `14`, buy `< 30`, sell `> 70`, long-only, one position at a time
- target:
  - first-run `< 1.0s`
  - steady-state median `< 1.0s`

Baseline result before implementation:

- first-run runtime: about `23.93s`
- gate status: `fail`

The default correctness lane still passed:

- command: `uv run poe verify`
- result: `228 passed, 3 skipped`

## Current Outcome

The implementation batch informed by this analysis is now complete.

Fresh post-implementation verification:

- `uv run poe perf-check`: passes
- `uv run poe verify`: passes

Fresh post-implementation notebook-style timing split:

- `source.load()`: about `2.40s`
- `engine.run()`: about `0.12s`

This means the original analysis remains useful as baseline evidence, but it no
longer describes the current runtime bottleneck state.

## Local Profile Evidence

One canonical `cProfile` run took about `81.03s`.

That absolute runtime is profiler-inflated relative to the `perf-check` gate and
should be read as hotspot evidence, not as the throughput baseline itself.

Top cumulative hotspots:

- `src/quantcraft/research/ta.py:_compute_rsi` about `60.68s`
- `src/quantcraft/research/ta.py:_series_values` about `17.97s`
- `src/quantcraft/research/domain/series.py:SeriesView.__getitem__` about `9.06s`
- `src/quantcraft/research/domain/series.py:_SeriesBuffer.append` about `1.00s`

Interpretation:

- the dominant cost is repeated full indicator-history recomputation, with RSI
  as the currently measured benchmark case
- the next cost is repeated full visible-series materialization
- append cost exists, but it is clearly secondary to the current shared
  indicator runtime path

## Root Cause

The current hot path is not fundamentally an RSI-specific design. It is a
shared indicator-runtime design problem.

Evidence in the current code:

- `sma`, `ema`, `rsi`, `atr`, and `cci` all return `_ComputedSeriesView`
  instances keyed by `len(...)` or length tuples in
  [ta.py](/home/retn0/repositories/nbsp1221/quantcraft/src/quantcraft/research/ta.py)
- `bb` and `macd` also use memoized full-series bundles that
  invalidate on the same append-driven version changes
- all of those paths depend on `_series_values(...)`, which rebuilds visible
  history through repeated reverse `SeriesView.__getitem__`

So the current runtime is structurally slow because:

1. appending one new bar changes indicator version keys
2. version invalidation rebuilds the full visible input series
3. indicator execution recomputes full derived history
4. strategy code then often reads only the latest value

This makes the hot path effectively quadratic in the visible series length and
means the benchmarked RSI failure is a symptom of a broader runtime model.

## External Library Study

### `backtesting.py`

Inspected files:

- `/tmp/backtesting.py_repo/backtesting/backtesting.py`
- `/tmp/backtesting.py_repo/backtesting/_util.py`

Observed pattern:

- indicators are computed once in `Strategy.init()` through `Strategy.I(...)`
- the backtest loop only reveals progressively larger slices of already-built
  arrays
- warm-up is handled by delaying the start bar instead of recomputing
  indicators bar-by-bar

Transferable lesson:

- separate indicator computation from progressive visibility through a shared
  runtime boundary

### `backtrader`

Inspected files:

- `/tmp/backtrader_repo/backtrader/indicators/rsi.py`
- `/tmp/backtrader_repo/backtrader/indicators/ema.py`
- `/tmp/backtrader_repo/backtrader/indicators/smma.py`

Observed pattern:

- RSI is built from reusable line operators
- smoothing is recurrence-based rather than full-window recomputation
- Wilder smoothing is expressed as `new = old * (period - 1) / period + current / period`

Transferable lesson:

- recurrence-based indicators should carry rolling state and update append-only,
  but through the common indicator runtime rather than ad hoc per-indicator
  wiring

### `vectorbt`

Inspected files:

- `/tmp/vectorbt_repo/vectorbt/indicators/basic.py`
- `/tmp/vectorbt_repo/vectorbt/indicators/nb.py`

Observed pattern:

- `IndicatorFactory` separates `cache_func` from `apply_func`
- expensive intermediates such as `delta`, `roll_up`, and `roll_down` are
  built once per parameter set
- outputs are reused by parameter-keyed caches

Transferable lesson:

- separate one-time intermediate-state construction from cheap result access in
  a generic cache boundary

### `pybroker`

Inspected files:

- `/tmp/pybroker_repo/src/pybroker/indicator.py`
- `/tmp/pybroker_repo/src/pybroker/vect.py`

Observed pattern:

- indicator work is grouped per symbol/indicator and computed away from the
  strategy callback
- vector math operates on contiguous arrays
- indicator data can be cached and reused instead of recomputed ad hoc

Transferable lesson:

- hot indicator math should operate on contiguous numeric state through a shared
  compute/cache layer, not repeated per-element reverse indexing inside each
  indicator view

## Best-Practice Synthesis

The libraries differ architecturally, but the shared lessons are consistent:

- keep one shared indicator execution model rather than special-casing one
  indicator
- do not recompute full indicator history when one new bar arrives
- keep progressive visibility separate from computation
- reuse rolling intermediate state
- only widen optimization scope after profile evidence says the first fix was not enough

## Recommendation Used For The Completed Batch

The next slice should not start by adding more machinery directly to `ta.py`.
That would repeat the current mistake in a more abstract form.

The better comparator-aligned shape is:

- keep `ta.py` as the public facade
- introduce a private shared runtime module for:
  - append-aware state progression
  - rebuild fallback policy
  - computed-view/cache behavior
- place indicator-specific formula/state definitions in a separate private
  kernel module

This recommendation is intentionally stronger than a stylistic preference:

- adding new runtime execution logic directly to `ta.py` should be treated as a
  design regression
- adding indicator-specific math directly to the shared runtime module should be
  treated as a design regression

Why this shape is the closest fit:

- it keeps the public strategy contract unchanged
- it matches the responsibility separation seen in mature libraries
- it prevents `ta.py` from becoming a second mini-framework
- it makes “add a new indicator without changing runtime architecture” a real
  code-structure rule rather than a slogan

So the benchmark remained RSI, but the optimization target was the generic
indicator runtime, and the intended code shape is:

- public facade: `src/quantcraft/research/ta.py`
- shared runtime: `src/quantcraft/research/indicators/runtime/`
- indicator wrappers/state adapters:
  `src/quantcraft/research/indicators/pure/`

Under that structure:

- `rsi` should be the first acceptance benchmark
- at least one additional built-in indicator should be routed through the same
  runtime without changing runtime infrastructure again
- only if the perf gate is still red should `SeriesView` storage refactoring
  become the next slice
