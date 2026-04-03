# RSI Performance Gate Design

## Goal

Add a repository-local performance regression gate for the canonical RSI
backtest scenario so AI agents cannot silently reintroduce the runtime collapse
 that was just diagnosed and fixed.

The gate should fail mechanically when the canonical benchmark regresses past
the approved threshold.

## Decision

Use `pytest-benchmark` as the primary performance-gate mechanism for this slice.

Do not implement the gate as:

- a normal `pytest` unit test with raw `time.perf_counter()` assertions
- a bespoke one-off shell script with hand-rolled timing logic as the main gate
- an `asv` suite as the first performance-regression layer

## Evidence

This choice follows the strongest fit between the current repository goal and
the documented behavior of the available tools.

### 1. General tests and timing-sensitive checks should not be conflated

`pytest` explicitly documents timing issues and uncontrolled environment as
common causes of flaky tests. That makes a raw time-threshold assertion inside
the normal functional test lane a poor default.

Source:

- `pytest` flaky tests guide:
  - https://docs.pytest.org/en/stable/explanation/flaky.html

### 2. `pytest-benchmark` already supports the exact regression workflow we need

`pytest-benchmark` provides:

- persisted benchmark runs
- comparison against prior saved runs
- failure on regression through `--benchmark-compare-fail`
- calibrated repeated rounds instead of naive single-run timing
- explicit support for separating setup from measured code

Sources:

- `pytest-benchmark` usage and comparison docs:
  - https://pytest-benchmark.readthedocs.io/en/stable/usage.html
  - https://pytest-benchmark.readthedocs.io/en/stable/comparing.html

### 3. `asv` is stronger for longitudinal benchmark suites than for this first gate

`asv` is a strong tool for historical benchmark tracking across commits and
machines, but it is heavier than needed for a first repository-local guard on
one canonical RSI scenario. It is better treated as a future expansion path if
`quantcraft` grows a broader performance suite.

Source:

- `asv` usage docs:
  - https://asv.readthedocs.io/en/stable/using.html

### 4. Repository-tracked benchmark fixtures should stay small and reviewable

GitHub recommends keeping repositories healthy by avoiding large objects, using
Git LFS for binary files, and staying within a recommended `1 MB` single-object
limit. GitHub also notes that text previews generally work for files smaller
than `2 MB`.

For the current RSI benchmark fixture, that makes a small checked-in text file a
better fit than a binary large-file workflow.

Sources:

- GitHub repository limits:
  - https://docs.github.com/en/repositories/creating-and-managing-repositories/repository-limits
- GitHub large files guidance:
  - https://docs.github.com/en/articles/conditions-for-large-files

### 5. `Parquet` is optimized for analytics storage, not for review-friendly fixture diffs

Apache Parquet documents itself as a column-oriented storage format designed for
efficient storage and retrieval. That is valuable for analytics pipelines, but
it is not the main need here because load time is excluded from the benchmark
measurement window.

Source:

- Apache Parquet overview:
  - https://parquet.apache.org/docs/overview/

## Recommended Architecture

Use a repository-tracked fixture dataset as the canonical benchmark input.

Recommended fixture path:

- `tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv`

Recommended fixture contract:

- text `CSV`, not `Parquet`
- header: `timestamp,open,high,low,close,volume`
- UTC timestamps in ISO 8601 form
- sorted ascending by timestamp
- fixed row count: `8760`
- loaded before the timed region begins

The benchmark and gate should treat this file as a stable repository artifact,
not as a `/tmp` cache.

Then add a dedicated performance gate lane with these properties:

1. fixed shared dataset
2. benchmarked backtest call only
3. repeated calibrated measurement
4. explicit threshold failure
5. separate command surface from the default correctness lane

## Fixture Format Decision

For this slice, the canonical benchmark fixture should be a git-tracked `CSV`
file, not `Parquet`.

Reasoning:

- the benchmark measures the backtest execution call only, so data-load speed is
  outside the timed region
- the current canonical dataset is small enough to track directly in Git without
  introducing repository-health risk
- `CSV` is text and easy to audit when the fixture contract needs review
- `Parquet` is a binary columnar format designed for efficient storage and
  retrieval, which is useful for analytics pipelines but adds binary-file
  opacity with little benefit for this narrow benchmark gate

Local evidence from the current benchmark dataset:

- path: `/tmp/quantcraft-backtest-benchmarks/binance-usdm-btcusdtusdt-1h-2025.csv`
- shape: `8760` data rows plus header
- size: `616043` bytes

This size is below GitHub's recommended `1 MB` single-object limit and well
below the thresholds where Git LFS becomes necessary. It is also small enough
to remain previewable and easy to inspect in pull requests.

If the fixture later grows materially or multiple large benchmark fixtures are
added, the repository can revisit this decision. For the current canonical RSI
scenario, plain `CSV` is the best fit.

## Why Separate From Default `verify`

Best practice says performance checks should be explicit because they are more
environment-sensitive than correctness checks.

That means:

- keep `uv run poe verify` focused on correctness, typing, structure, build, and
  notebook validation
- add `uv run poe perf-check` as a first-class repository command
- make AI harnesses that care about release-quality runtime run both `verify`
  and `perf-check`

This still gives mechanical failure, but avoids turning the default correctness
lane into a timing-sensitive flaky gate.

## Canonical Threshold

For the canonical RSI scenario, the gate should fail unless:

- first-run runtime is `< 1.0s`
- steady-state median runtime is `< 1.0s`

The dedicated perf test should measure both values against the canonical
fixture and strategy contract.

## Scope

Included:

- add benchmark dependency and configuration
- add a dedicated performance benchmark test for the RSI scenario
- add a repo-local `perf-check` command surface
- record threshold rules in docs

Excluded:

- broad multi-scenario performance suite
- `asv` historical tracking
- CI hardware normalization beyond basic environment notes
- performance assertions for non-canonical strategies

## Success Criteria

This design is successful when:

- the canonical RSI scenario can fail mechanically on runtime regression
- the regression gate is based on a standard benchmarking tool, not ad-hoc timing
- the repository command surface exposes performance checks explicitly
- the performance gate remains understandable to humans and AI agents
