# Backtest Throughput Benchmark Design

## Goal

Measure `quantcraft`'s current single-symbol backtest throughput against a small set
of relevant Python backtesting libraries, using the same data and the same
strategy shape, so the next optimization slice can target a defensible runtime
goal instead of guessing.

The question for this batch is narrow:

- given identical BTC perpetual 1h bars for one year
- and a long-only RSI `30/70` strategy
- how long does the backtest execution itself take?

## Scope

Included:

- one repository-local benchmark harness for `quantcraft`
- one comparator harness rooted in `/tmp`
- one shared input dataset for all engines
- comparator libraries:
  - `backtesting.py`
  - `backtrader`
  - `vectorbt`
  - `pybroker`
- one fairness review pass on the benchmark design and results
- one summary artifact that records runtimes, result shape, and target-setting

Excluded:

- install time
- package import time
- network fetch time
- file-load time
- charting or notebook rendering time
- full product ranking across frameworks
- live-trading or paper-trading comparisons

## Benchmark Contract

The benchmark must measure only the backtest execution window.

For every engine:

1. load identical bars before the timer starts
2. construct the strategy and runner objects
3. start timing immediately before the engine backtest call
4. stop timing immediately after the engine returns the result object
5. record result-shape fields alongside runtime

The benchmark must also record:

- number of bars processed
- number of completed trades or closest comparable field
- final equity or closest comparable field
- any unavoidable semantic mismatch

## Shared Scenario

Input data:

- venue data origin: Binance USD-M futures
- symbol: `BTC/USDT:USDT`
- timeframe: `1h`
- range: `2025-01-01T00:00:00Z` to `2026-01-01T00:00:00Z`
- expected bars: `8760`

Strategy shape:

- indicator: RSI with length `14`
- entry: buy `1` unit when RSI drops below `30` and no position is open
- exit: sell `1` unit when RSI rises above `70` and a position is open
- direction: long-only
- one position at a time

Trading-cost assumptions should match as closely as each engine allows, but they
must not block the benchmark. If exact parity is not available, record the
difference instead of forcing an unnatural adapter layer.

## Comparator Selection

The comparator set is intentionally small.

Primary direct comparisons:

- `backtesting.py`
- `backtrader`
- `pybroker`

Reference throughput ceiling:

- `vectorbt`

`vectorbt` stays in the set even though its execution model differs, because it
is still useful as a research-throughput reference point. Its result must be
reported with a clear note that it is not an event-driven kernel match.

## Fairness Rules

The benchmark must not be gameable.

- do not benchmark different datasets per library
- do not let one engine fetch data while another reads local bars
- do not count setup or installation time as backtest runtime
- do not force comparator APIs into unnatural wrappers if that changes their
  normal execution path materially
- do not claim semantic parity where it does not exist
- do not rely on a single noisy timing sample

## Measurement Rules

For each engine:

- run at least one first-run measurement
- run repeated steady-state measurements
- report the steady-state median as the primary runtime
- keep the first-run runtime as a secondary field

This split matters because some engines may pay compilation or internal cache
setup costs on the first execution.

## Success Criteria

This benchmark batch is successful when:

- `quantcraft` has a repository-local benchmark script for the canonical RSI
  scenario
- the shared dataset is fixed and reused across all compared engines
- comparator runs complete for the selected library set, or skipped engines are
  explicitly explained
- runtime numbers are paired with result-shape notes
- the final report proposes a concrete optimization target for `quantcraft`

