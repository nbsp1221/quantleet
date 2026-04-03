# Research Indicator Performance Optimization Plan

> **For Codex:** REQUIRED SUB-SKILLS: use `systematic-debugging` before changing runtime code, `test-driven-development` before each behavior change, and `verification-before-completion` before claiming the slice is done.

**Goal:** Bring the canonical indicator-driven backtest path back under the
explicit performance gate, using the RSI benchmark as the acceptance case
without making the runtime architecture RSI-specific.

**Architecture:** Keep `BacktestEngine`, `Strategy`, `SeriesView`, and `ta.*`
public behavior stable, but replace the current indicator runtime model that
repeatedly re-materializes and recomputes full series on append. The benchmark
and acceptance path remain the canonical RSI scenario, but the internal fix
must be expressed as a separate shared indicator-runtime layer rather than more
logic accumulating inside `ta.py`. Treat any optimization as invalid if the
canonical RSI result shape changes or if adding a new indicator would require
changing the runtime architecture again.

**Tech Stack:** Python 3.13, `uv`, `pytest-benchmark`, repo-local `poe`,
`quantcraft.research`, `quantcraft.data`

## Lifecycle

- status: completed
- completed_on: 2026-04-03

## Current Verified State

- `uv run poe verify`: passes
- `uv run poe perf-check`: passes
- latest canonical perf result:
  - first-run runtime: under `1.0s`
  - steady-state median: about `0.14s`
  - required threshold: `< 1.0s`
- canonical result shape remains:
  - bars: `8760`
  - closed trades: `118`
  - fills: `236`
  - final equity: `1038523.5766`

## Current Status

- Slice 1: complete
- Slice 2: complete
- Slice 3: complete
- Slice 4: complete

## Root Cause Evidence

Current profile evidence from the canonical perf fixture shows:

- total runtime is dominated by `BacktestEngine.run(...)`, not fixture load
- the hot path is overwhelmingly inside:
  - `src/quantcraft/research/ta.py:_compute_rsi`
  - `src/quantcraft/research/ta.py:_series_values`
  - `src/quantcraft/research/domain/series.py:SeriesView.__getitem__`
- append cost also exists in:
  - `src/quantcraft/research/domain/series.py:_SeriesBuffer.append`

High-signal current profile facts:

- `_compute_rsi` consumes most cumulative runtime
- `_series_values` re-materializes the full visible series for each bar
- `SeriesView.__getitem__` is called tens of millions of times while rebuilding
  the same historical data repeatedly
- `_SeriesBuffer.append` recreates tuples on every appended OHLCV value

## Why The Current Runtime Is Slow

The current indicator runtime is structurally expensive for an event-driven
engine, and RSI is only the benchmark case that exposes it most clearly.

1. each new bar changes `len(series)`
2. the current `ta.*` views invalidate on that length change
3. `_series_values(...)` rebuilds the full visible series through repeated
   reverse indexing
4. the indicator implementation recomputes the full derived history
5. strategy code often then reads only the latest value

This means the runtime behaves much closer to repeated `O(n)` work per bar than
to append-only incremental work.

Current code evidence that this is a shared runtime issue rather than an
RSI-only quirk:

- `sma`, `ema`, `rsi`, `atr`, and `cci` all return `_ComputedSeriesView`
  instances keyed by `len(...)` or length tuples
- `bollinger_bands` and `macd` also use the same invalidation pattern through
  memoized full-series bundles
- the current runtime boundary is therefore `ta.*` + `_ComputedSeriesView` +
  `_series_values(...)`, not just the RSI formula itself

## External Implementation Lessons

The current planning slice studied comparator code directly under `/tmp`.

Useful patterns from those libraries:

- `backtesting.py`
  - `Strategy.I(...)` computes indicator arrays once up front and then reveals
    them gradually during the run
  - data access uses cached NumPy array slices rather than per-element reverse
    indexing
- `backtrader`
  - indicators support both per-bar `next(...)` and bulk `once(...)` execution
  - smoothing indicators use recurrence relations rather than re-walking the
    full historical window
- `vectorbt`
  - indicator execution is built around artifact reuse and explicit cache
    boundaries
  - repeated parameter work is avoided through cache reuse rather than implicit
    recomputation
- `pybroker`
  - indicator computation is separated from strategy consumption
  - full indicator series are computed once per symbol and cached

Reference implementation files worth reading before coding:

- `/tmp/backtesting.py_repo/backtesting/backtesting.py`
- `/tmp/backtesting.py_repo/backtesting/_util.py`
- `/tmp/backtrader_repo/backtrader/indicators/rsi.py`
- `/tmp/backtrader_repo/backtrader/indicators/ema.py`
- `/tmp/backtrader_repo/backtrader/indicators/smma.py`
- `/tmp/vectorbt_repo/vectorbt/indicators/basic.py`
- `/tmp/vectorbt_repo/vectorbt/indicators/nb.py`
- `/tmp/pybroker_repo/src/pybroker/indicator.py`
- `/tmp/pybroker_repo/src/pybroker/vect.py`

General best-practice takeaways for `quantcraft`:

- keep one shared indicator execution model rather than special-casing a single
  indicator
- do not recompute full indicator history when only one new bar arrived
- use append-only internal state for indicators that admit recurrence-based
  updates
- keep a safe rebuild path for non-append invalidation cases
- avoid per-element `__getitem__` loops over reversed series in hot paths
- avoid changing public ergonomics just to get the speedup
- treat JIT/vectorization as later options, not as the first fix for an
  event-driven kernel

## Required Code Shape

The plan is not only about performance principles. It also fixes the intended
code shape so the implementation converges toward the same responsibility split
seen in mature comparator libraries.

Required module roles:

- `src/quantcraft/research/ta.py`
  - public facade only
  - parameter validation
  - public function names and return types
  - thin wiring into internal runtime/kernels
- `src/quantcraft/research/_indicator_runtime.py`
  - shared private runtime layer
  - append-aware state progression
  - rebuild fallback policy
  - computed-view materialization and cache invalidation policy
- `src/quantcraft/research/_indicator_kernels.py`
  - indicator-specific formula/state definitions
  - no public API surface
  - no strategy/backtest orchestration logic

Forbidden implementation shape:

- do not place new runtime state machines, cache policies, rebuild logic, or
  indicator execution abstractions back into `src/quantcraft/research/ta.py`
- do not let `src/quantcraft/research/_indicator_runtime.py` become a grab-bag
  for indicator formulas or public API helpers
- do not couple runtime internals to `BacktestEngine` or strategy lifecycle code

Required extension shape:

- adding a new built-in indicator may require:
  - a new public facade entry in `ta.py`
  - a new kernel/state definition in `_indicator_kernels.py`
- adding a new built-in indicator must not require:
  - changing `_indicator_runtime.py`
  - changing strategy lifecycle code
  - changing perf infrastructure

Required test split:

- public indicator surface tests remain under:
  - `tests/unit/research/test_indicator_surface.py`
- shared runtime invariant tests must live separately under:
  - `tests/unit/research/test_indicator_runtime.py`
- perf acceptance remains under:
  - `tests/perf/test_rsi_backtest_benchmark.py`

This split follows the comparator lesson that public indicator API, runtime
infrastructure, and indicator formula/kernel code should not collapse back into
one file or one test layer.

## Optimization Direction

### Slice 1: Introduce Shared Indicator Runtime Infrastructure

Target files:

- `src/quantcraft/research/_indicator_runtime.py`
- `src/quantcraft/research/_indicator_kernels.py`
- `src/quantcraft/research/ta.py`
- `tests/unit/research/test_indicator_surface.py`
- `tests/unit/research/test_indicator_runtime.py`
- `tests/perf/test_rsi_backtest_benchmark.py`

Intent:

- keep public `ta.*` usage unchanged
- move runtime responsibilities out of `ta.py` and into a separate private
  module boundary
- introduce a shared internal runtime boundary that distinguishes:
  - append-aware incremental update paths
  - conservative full-rebuild fallback paths
- ensure that adding a new indicator later plugs into this boundary rather than
  changing the runtime architecture itself
- preserve current warmup and `NaN` semantics exactly
- preserve current final trade count and summary results exactly

Implementation shape:

- add a shared internal indicator-view/cache abstraction or execution boundary
  in `src/quantcraft/research/_indicator_runtime.py`
- keep indicator-specific recurrence or formula details in
  `src/quantcraft/research/_indicator_kernels.py`
- reduce `src/quantcraft/research/ta.py` to a thin public facade
  - allowed changes there are limited to imports, parameter validation, return
    wiring, and public result-object assembly
- add an append-aware fast path for indicators that can update from prior state
- keep a conservative rebuild path for shrink, reset, or non-monotonic
  invalidation
- add unit tests for:
  - append-by-one growth preserving benchmark parity
  - rebuild fallback after non-monotonic invalidation
  - unchanged warmup and `NaN` behavior
  - unchanged live-view behavior for bindings created in `Strategy.init()`
  - no performance-architecture change required when routing another indicator
    through the same runtime boundary
- do not loosen the current perf gate threshold to make the slice pass

### Slice 2: Route Existing Indicators Through The Shared Runtime

Target files:

- `src/quantcraft/research/_indicator_runtime.py`
- `src/quantcraft/research/_indicator_kernels.py`
- `src/quantcraft/research/ta.py`
- `tests/unit/research/test_indicator_surface.py`
- `tests/unit/research/test_indicator_runtime.py`
- `tests/perf/test_rsi_backtest_benchmark.py`

Intent:

- use the new runtime boundary for the current built-in indicators
- let each indicator provide only its formula/state definition, not a bespoke
  performance framework
- keep the canonical perf gate on the RSI scenario, but avoid an architecture
  that only helps RSI

Expected family split:

- recurrence-friendly indicators: should use append-aware state
- indicators that still need full history: should still use the shared runtime
  and explicit rebuild/caching boundary instead of ad hoc recomputation wiring

Minimum generic-proof scope:

- route `rsi` through the shared runtime
- route at least one additional built-in indicator through the same runtime
  without changing runtime infrastructure code again
- prove that the second indicator keeps its existing public semantics

### Slice 3: Re-evaluate Series Storage Only If The Shared Runtime Is Still Not Enough

Target files:

- `src/quantcraft/research/domain/series.py`
- `src/quantcraft/research/application/_runtime.py`
- `tests/unit/research/domain/test_series.py`

Intent:

- only continue here if the shared indicator runtime change still leaves the
  perf gate red
- inspect tuple-on-append cost and repeated reverse indexing cost
- preserve `SeriesView` public indexing semantics

Possible directions:

- switch the private buffer representation away from tuple-on-append
- keep `SeriesView` read-only while using a cheaper internal append structure
- avoid speculative redesign if the RSI slice already satisfies the gate

### Slice 4: Consider Broader Runtime Follow-Up Only After Evidence

Only if the gate is still red after Slices 1 through 3:

- inspect whether additional runtime-level caching boundaries are missing
- prefer shared runtime improvements over per-indicator patches
- do not introduce JIT or extra heavy dependencies unless the simpler internal
  fixes fail to meet the target

## Non-Negotiable Contracts

Do not change:

- `quantcraft.research.BacktestEngine` entrypoints
- `HistoricalDataSource.load() -> BarSeries`
- `Strategy` lifecycle or signal semantics
- `SeriesView` read-only public behavior
- canonical result shape for the RSI fixture
- perf gate threshold contract

## Success Criteria

This slice is only successful when all of the following are true:

1. `uv run poe perf-check` passes
2. `uv run poe verify` still passes
3. canonical RSI result shape remains unchanged
4. at least one non-RSI built-in indicator is routed through the same runtime
   boundary without runtime-architecture edits
5. the optimization is explained by repository-local evidence, not by hidden
   environment changes

## Outcome

This batch completed with the intended generic runtime shape:

- `ta.py` is now a thin public facade
- shared indicator execution lives in `src/quantcraft/research/_indicator_runtime.py`
- indicator-specific state and formula logic live in
  `src/quantcraft/research/_indicator_kernels.py`
- built-in indicators now share the runtime boundary rather than carrying
  per-indicator recomputation wiring
- `SeriesView` public semantics remain unchanged, but private buffer append
  cost was reduced enough to clear the final perf gate

## Minimum Verification For The Future Execution Batch

- `uv run pytest tests/unit/research/test_indicator_surface.py -q`
- `uv run pytest tests/unit/research/test_indicator_runtime.py -q`
- `uv run pytest tests/perf/test_rsi_backtest_benchmark.py -q -x --run-perf`
- `uv run poe perf-check`
- `uv run poe verify`
