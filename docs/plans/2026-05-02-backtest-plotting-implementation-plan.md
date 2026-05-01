# Backtest Plotting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the first-beta `BacktestResult.plot()` workflow so engine-produced backtest results can render price, fills, equity, and underwater drawdown without users passing bars again or reloading a source.

**Architecture:** Keep plotting ownership inside `quantcraft.backtest`. `BacktestResult.plot()` is a thin public facade; `quantcraft.backtest.plotting` owns Matplotlib rendering; runtime owns the immutable run snapshot and `drawdown_curve`; reporting shares pure backtest analytics helpers but is not the plot data source. The shared `trading` kernel remains unchanged.

**Tech Stack:** Python 3.13, stdlib frozen dataclasses, `datetime.UTC`, Matplotlib runtime dependency with lazy imports, pytest, pytest monkeypatch, Ruff, mypy, uv, Poe task runner, wheel metadata checks via stdlib `zipfile`/`email.parser` or a clean temporary package environment.

---

## Repo Workflow Planner Contract

- Date: `2026-05-02`
- Task: `Implement the first-beta backtest result plotting workflow`
- Status: `active`
- Risk class: `Tier B`
- Requestor: `User`
- Owner: `Codex`

### Planner Contract

- Goal:
  - Convert the accepted plotting product spec and plotting test-scenario spec
    into a concrete how-focused implementation plan.
  - Preserve the user-facing `result.plot()` API, result-reporting behavior,
    and current backtest execution semantics.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/PLANS.md`
  - `docs/DESIGN.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/product-specs/backtest-plotting-test-scenarios.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
- Why these are governing:
  - The product specs define the required beta UX, API, dependency strategy,
    figure content, snapshot contract, drawdown convention, and tests.
  - The architecture docs keep plotting under `backtest`, allow `backtest` to
    depend on `data` and `trading`, and prevent `backtest -> research`.
  - Reliability docs require runtime-sensitive verification for backtest
    runtime changes and keep performance checks explicit.
- In-repo scope:
  - Add runtime `matplotlib` dependency and refresh `uv.lock`.
  - Add backtest-owned drawdown analytics helpers.
  - Extend `BacktestResult` with keyword-only `drawdown_curve`, private
    keyword-only `_run_snapshot`, and no-argument `plot()`.
  - Add a private immutable run snapshot containing symbol, timeframe,
    bar type, timestamps, and closes.
  - Populate `drawdown_curve` and `_run_snapshot` from `BacktestEngine.run(...)`
    paths after `BarSeries` materialization.
  - Add `src/quantcraft/backtest/plotting.py` with lazy Matplotlib rendering.
  - Add unit, integration, smoke, structure, perf-adjacent, packaging, docs,
    and notebook coverage described below.
  - Update quickstart/product docs and notebook examples to show `result.plot()`
    plus standard `plt.show()`/`fig.savefig(...)` usage.
- Out-of-repo scope:
  - No PyPI publishing.
  - No external services.
  - No live/network tests.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A approval is not required because implementation must not modify
    `src/quantcraft/trading` or `src/quantcraft/execution`.
  - If execution discovers a required `trading` or `execution` source change,
    stop and request explicit Tier A approval before continuing.
- Verification commands:
  - Focused commands listed under each task.
  - `uv run pytest tests/unit/backtest/test_results.py tests/unit/backtest/test_plotting.py -q`
  - `uv run pytest tests/integration/backtest/test_plotting.py -q`
  - `uv run pytest tests/smoke/local tests/integration/commands/test_built_artifact_imports.py -q`
  - `uv run pytest tests/structure/architecture tests/structure/docs tests/structure/repo -q`
  - `uv run pytest tests/perf -q -x --run-perf`
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run python scripts/coverage_check.py`
  - `uv run python scripts/repo_check.py`
  - `uv build`
  - `uv run poe verify-runtime`
- Success criteria:
  - `result.plot()` works immediately after both `engine.run(bars=...)` and
    `engine.run(source=...)`.
  - Users never pass `bars`, `source`, dataframe, or report into `plot()`.
  - Matplotlib is a runtime package dependency, but normal `quantcraft.backtest`
    imports do not import Matplotlib.
  - Engine-produced results contain populated `drawdown_curve` and private
    immutable plot data.
  - Manual results without `_run_snapshot` remain valid for non-plot fields and
    fail only on `plot()` with a clear `ValueError`.
  - Plot figures have three axes, correct labels/legends, shared x-axis,
    default 12x8 figure size, approximate 3:2:1 panel ratio, grid, close line,
    fill markers, equity line, underwater drawdown line, and zero baseline.
  - Plotting calls no `show()`, `savefig()`, source reload, or `close()`, and
    mutates no result-owned data.
  - 10,000-bar no-downsampling contract is covered in the explicit performance
    lane.
  - Existing result reporting tests continue to pass.
- Out of scope:
  - Indicator overlays.
  - Candlesticks.
  - Volume.
  - Plotly/Bokeh/browser backends.
  - Interactive widgets.
  - Multi-symbol or multi-timeframe plotting.
  - Paper/live plotting.
  - Downsampling policy.
  - Public snapshot accessor.
  - Public helper `plot_backtest(...)`.
  - Commits; create commits only if the user explicitly asks.

### Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close only after this plan is grounded in the current source tree, points
    to exact files, explains how to implement each contract, and records fresh
    repository-document verification.
- Acceptance artifact location:
  - `docs/plans/2026-05-02-backtest-plotting-implementation-plan.md`
- How the generator and evaluator agreed on done before execution:
  - This document must explain the implementation architecture, reusable code,
    exact file ownership, TDD sequence, verification commands, and known risks
    before production code is touched.
- Checks the evaluator will use:
  - Manual review against `backtest-plotting.md`.
  - Manual review against `backtest-plotting-test-scenarios.md`.
  - Manual review against current source/test layout.
  - `uv run poe repo-check`.
- Auto-fail conditions:
  - Prescribing `trading` or `execution` source changes without Tier A approval.
  - Making `plot()` accept `bars`, `source`, dataframe, or report parameters.
  - Importing Matplotlib from `quantcraft.backtest.__init__`, `results.py`, or
    any non-plot import path.
  - Deriving plot data from `BacktestReport`.
  - Testing private snapshot shape as the primary evidence for normal behavior.
  - Adding perf tests under `tests/perf/` without updating the Poe command
    surface so they run under `verify-runtime`.

### Generator Work Log

- Planned slice order:
  1. Read governing docs and plotting specs.
  2. Survey `src/quantcraft`, tests, docs, Poe tasks, and repo harness code.
  3. Map reusable runtime/reporting/data/test patterns and implementation risks.
  4. Write this how-focused implementation plan.
  5. Run repository-document verification.
  6. Record evaluator findings and final disposition.
- Notes:
  - This plan intentionally modifies no runtime source code.
  - Implementation should be executed with TDD: write a focused failing test,
    run it, implement the minimum production change, rerun the focused test,
    then broaden verification.
  - Existing dirty/untracked documentation files are part of the current
    plotting planning work and should not be reverted.
- Blockers or scope changes:
  - None at plan-writing time.

## Codebase Survey Summary

### Technology And Infrastructure

- Python 3.13 package under `src/quantcraft`.
- `uv` manages dependencies and lockfile.
- Poe task runner owns repo command surface.
- pytest uses `--import-mode=importlib`.
- Ruff, mypy strict mode, coverage, build, repo-check, notebook validation, and
  explicit perf/live lanes are already wired through `pyproject.toml`.
- Current runtime dependencies are `ccxt` and `ta-lib`.
- `matplotlib>=3.10.8` is currently in `[dependency-groups].dev`, so the
  implementation must move it to `[project.dependencies]` and refresh
  `uv.lock`.

### Architecture And Package Ownership

The current package topology matches the capability-first architecture:

- `quantcraft.data` owns `TimeBar`, `BarSeries`, `HistoricalDataSource`, and
  concrete source adapters.
- `quantcraft.trading` owns the Tier A matching/accounting/event kernel.
- `quantcraft.backtest` owns `BacktestEngine`, runtime orchestration,
  execution model, order activation, result models, and reporting.
- `quantcraft.research` owns the user strategy surface.

For plotting, the correct owner is `quantcraft.backtest`. The implementation
may import from `data` and `trading`; it must not import from `research`,
`execution`, or app surfaces.

### Current Backtest Execution Path

Current flow:

```text
BacktestEngine.run(...)
  -> _validated_bars(...)
  -> _run_backtest(...)
  -> _StrategyDriver(strategy)
  -> ConservativeOHLCVExecutionModel.tick_events_for_bar(...)
  -> match_order(...)
  -> apply_fill(...)
  -> _mark_state_to_market(...)
  -> BacktestResult(...)
```

Relevant files:

- `src/quantcraft/backtest/engine.py`
  - validates exactly one of `bars` or `source`
  - materializes `source.load()` before calling `_run_backtest`
  - rejects empty `BarSeries` before runtime, so empty plot data is mainly an
    invalid/manual result concern
- `src/quantcraft/backtest/runtime.py`
  - owns the marked equity stream
  - currently appends `equity_curve` once per bar
  - currently computes summary max drawdown with private `_max_drawdown`
  - currently builds `BacktestReport` through `_ReportBuilder`
  - already has all data needed to create a run snapshot from `bars`
- `src/quantcraft/backtest/results.py`
  - frozen slots dataclasses
  - current `BacktestResult` positional fields:
    `trade_log`, `equity_curve`, `final_state`, `summary`
  - `execution_model_name` is positional-compatible and `compare=False`
  - `_report` is keyword-only, `compare=False`, `repr=False`
  - this is the right place for `_BacktestRunSnapshot`,
    `drawdown_curve`, `_run_snapshot`, and `plot()`
- `src/quantcraft/backtest/reporting.py`
  - `_ReportBuilder.record_equity(...)` independently computes drawdown
  - risk max drawdown currently uses `_max_drawdown(tuple(point.drawdown ...))`
  - report must share the same pure drawdown formula, but plotting must not
    read report data

### Current Data Contracts

- `TimeBar` and `BarSeries` are frozen slots dataclasses in
  `src/quantcraft/data/bars.py`.
- `BarSeries.rows` is already an immutable tuple of `TimeBar` values.
- `DataFrameDataSource.load()` copies mutable row-like input into new
  `TimeBar` objects, which is useful for mutation-resistance tests.
- `HistoricalDataSource.load()` returns `BarSeries`.

Implementation implication:

- Snapshot creation should be cheap and explicit:

```python
_BacktestRunSnapshot(
    symbol=bars.symbol,
    timeframe=bars.timeframe,
    bar_type=bars.bar_type,
    timestamps=tuple(row.timestamp for row in bars.rows),
    closes=tuple(row.close for row in bars.rows),
)
```

### Current Test And Harness Patterns

Existing reusable patterns:

- `tests/integration/research/support_backtest_runner.py`
  - deterministic strategy classes
  - `fixture_rows()`
  - `fixture_bar_series()`
  - `fixture_dataframe_records()`
  - `run_engine_backtest(...)`
  - `run_engine_backtest_from_source(...)`
- `tests/unit/backtest/test_result_reporting_metrics.py`
  - local `_bars(...)` fixture pattern for hand-computable equity cases
- `tests/integration/commands/test_built_artifact_imports.py`
  - builds a wheel
  - currently installs with `--no-deps`, so it cannot prove runtime dependency
    availability by importing `matplotlib` from the dev environment
- `tests/conftest.py`
  - perf tests are explicit-only unless selected by path or `--run-perf`
- `tests/perf/test_rsi_backtest_benchmark.py`
  - existing perf command currently targets only this file
- `src/quantcraft/_repo_tools.py`
  - domain-dependency checks allow `backtest -> data/trading`
  - generic architecture checks do not currently forbid `backtest -> research`
    beyond the configured allowed list, so plotting-specific structure tests
    should explicitly cover the new boundary

Current gap:

- There is no `tests/integration/backtest/` directory yet. Add it for the
  backtest-owned plotting integration contract.

### Existing Risks To Handle Explicitly

1. `drawdown_curve` equality will break existing `BacktestResult(...)`
   equality tests unless expected engine-produced results include the populated
   keyword-only `drawdown_curve`.
2. Manual positional `BacktestResult(...)` construction must remain valid, so
   both `drawdown_curve` and `_run_snapshot` must be keyword-only fields.
3. `results.py` currently imports `BacktestReport`. Adding a `Figure` return
   type must not introduce runtime Matplotlib imports there; use
   `TYPE_CHECKING` plus quoted annotations or omit a concrete runtime import.
4. Source reload tests should observe `load()` calls on a fake source. Plotting
   must never retain or call a source object.
5. Matplotlib figure tests can leak figures. Test code should close figures in
   `finally` blocks or fixture teardown; production code must not close them.
6. The 10,000-bar scale test needs either the normal integration lane or a Poe
   task surface update. If placed under `tests/perf/`, change `perf-check` to
   include all perf tests, then update structure tests/docs that encode the Poe
   task contract.

## Implementation Architecture

### Result Data Model

Modify `src/quantcraft/backtest/results.py`:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure
```

Add a private frozen snapshot dataclass:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class _BacktestRunSnapshot:
    symbol: str
    timeframe: str
    bar_type: str
    timestamps: tuple[int, ...]
    closes: tuple[float, ...]
```

Extend `BacktestResult`:

```python
drawdown_curve: tuple[float, ...] = field(default=(), kw_only=True)
_run_snapshot: _BacktestRunSnapshot | None = field(
    default=None,
    compare=False,
    repr=False,
    kw_only=True,
)
```

Add the facade:

```python
def plot(self) -> "Figure":
    from quantcraft.backtest.plotting import plot_backtest_result

    return plot_backtest_result(self)
```

Do not export `_BacktestRunSnapshot` in `__all__`.

### Backtest Analytics Helpers

Create `src/quantcraft/backtest/analytics.py` for backtest-owned pure result
analytics that are not report-specific.

Recommended functions:

```python
def drawdown_for_equity(*, running_peak: float, equity: float) -> float:
    if running_peak <= 0.0:
        return 0.0
    return round(max((running_peak - equity) / running_peak, 0.0), 12)


def drawdown_curve_for_equity(equity_curve: tuple[float, ...]) -> tuple[float, ...]:
    running_peak: float | None = None
    values: list[float] = []
    for equity in equity_curve:
        running_peak = equity if running_peak is None else max(running_peak, equity)
        values.append(drawdown_for_equity(running_peak=running_peak, equity=equity))
    return tuple(values)


def max_drawdown(drawdown_curve: tuple[float, ...]) -> float:
    return max(drawdown_curve) if drawdown_curve else 0.0
```

Use this helper from runtime and reporting. Delete or replace the old
`runtime._max_drawdown` and `reporting._max_drawdown` paths so the formula
cannot drift.

### Runtime Population

Modify `src/quantcraft/backtest/runtime.py`:

- build `equity_curve_tuple = tuple(equity_curve)` after the bar loop
- compute `drawdown_curve = drawdown_curve_for_equity(equity_curve_tuple)`
- compute `summary.max_drawdown = max_drawdown(drawdown_curve)`
- build `_run_snapshot = _snapshot_from_bars(bars)`
- pass `drawdown_curve=drawdown_curve`
- pass `_run_snapshot=_run_snapshot`

Add private helper in `runtime.py`:

```python
def _snapshot_from_bars(bars: BarSeries) -> _BacktestRunSnapshot:
    return _BacktestRunSnapshot(
        symbol=bars.symbol,
        timeframe=bars.timeframe,
        bar_type=bars.bar_type,
        timestamps=tuple(row.timestamp for row in bars.rows),
        closes=tuple(row.close for row in bars.rows),
    )
```

Import `_BacktestRunSnapshot` from `results.py` even though it is private,
because runtime and result model are inside the same bounded context.

### Reporting Consolidation

Modify `src/quantcraft/backtest/reporting.py`:

- import `drawdown_for_equity` and `max_drawdown`
- in `_ReportBuilder.record_equity(...)`, keep `_equity_peak` but compute
  drawdown through `drawdown_for_equity(...)`
- in `build(...)`, compute `risk.max_drawdown` through the shared
  `max_drawdown(...)`

Do not make reporting the source of `BacktestResult.drawdown_curve`.

### Plotting Module

Create `src/quantcraft/backtest/plotting.py`.

Rules:

- no top-level Matplotlib imports
- no import from `quantcraft.research`
- no import from `quantcraft.backtest.reporting`
- no file writes
- no `show()`
- no `close()`
- no source reloads
- no mutation

Core shape:

```python
from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from quantcraft.backtest.results import BacktestResult

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def plot_backtest_result(result: BacktestResult) -> "Figure":
    from matplotlib import dates as mdates
    from matplotlib import ticker
    from matplotlib import pyplot as plt

    snapshot = result._run_snapshot
    if snapshot is None:
        raise ValueError("run snapshot is required to plot BacktestResult")

    _validate_plot_lengths(
        timestamps=snapshot.timestamps,
        closes=snapshot.closes,
        equity_curve=result.equity_curve,
        drawdown_curve=result.drawdown_curve,
    )
    x_values = _utc_datetimes(snapshot.timestamps)
    drawdown_values = tuple(-value for value in result.drawdown_curve)

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(12, 8),
        sharex=True,
        gridspec_kw={"height_ratios": (3, 2, 1)},
    )
    price_ax, equity_ax, drawdown_ax = axes

    price_ax.plot(x_values, snapshot.closes, label="Close")
    _plot_fill_markers(price_ax, result.trade_log)
    equity_ax.plot(x_values, result.equity_curve, label="Equity")
    drawdown_ax.plot(x_values, drawdown_values, label="Drawdown")
    drawdown_ax.axhline(0.0, linewidth=1.0)
    drawdown_ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))

    fig.suptitle(f"{snapshot.symbol} {snapshot.timeframe} Backtest")
    price_ax.set_ylabel("Price")
    equity_ax.set_ylabel("Equity")
    drawdown_ax.set_ylabel("Drawdown (%)")
    drawdown_ax.set_xlabel("Time (UTC)")

    for axis in axes:
        axis.grid(True, alpha=0.25)
        axis.legend()
    price_ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M", tz=UTC))
    fig.tight_layout()
    return fig
```

Adjust exact implementation details as needed for typing, but preserve the
contract above.

Validation helper:

```python
def _validate_plot_lengths(
    *,
    timestamps: tuple[int, ...],
    closes: tuple[float, ...],
    equity_curve: tuple[float, ...],
    drawdown_curve: tuple[float, ...],
) -> None:
    if not timestamps:
        raise ValueError("run snapshot contains empty run data")
    lengths = {
        "timestamps": len(timestamps),
        "closes": len(closes),
        "equity_curve": len(equity_curve),
        "drawdown_curve": len(drawdown_curve),
    }
    if len(set(lengths.values())) != 1:
        joined = ", ".join(f"{name}={length}" for name, length in lengths.items())
        raise ValueError(f"plot series length mismatch: {joined}")
```

Timestamp helper:

```python
def _utc_datetimes(timestamps: tuple[int, ...]) -> tuple[datetime, ...]:
    return tuple(datetime.fromtimestamp(timestamp / 1000, tz=UTC) for timestamp in timestamps)
```

Fill markers:

- derive buy/sell fills from `result.trade_log`
- x-values use fill timestamps converted to UTC datetimes
- y-values use fill prices
- do not create buy/sell marker artists when there are no fills for that side

### Dependency And Poe Task Strategy

Modify `pyproject.toml`:

- move `"matplotlib>=3.10.8"` from `[dependency-groups].dev` to
  `[project.dependencies]`
- change `perf-check` if the 10,000-bar scenario lives under `tests/perf/`

Recommended perf task:

```toml
"perf-check" = { cmd = "pytest tests/perf -q -x --run-perf", help = "Run the explicit performance verification lane" }
```

Then update structure tests that encode the old sample task text:

- `tests/structure/repo/test_repo_check_contracts.py`

Keep `verify-runtime = { sequence = ["verify", "perf-check"], ... }`.

Refresh lockfile with:

```bash
uv lock
```

## TDD Implementation Tasks

### Task 1: Runtime Dependency And Built Artifact Metadata

**Files:**

- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `tests/integration/commands/test_built_artifact_imports.py`
- Possibly modify: `tests/structure/repo/test_repo_check_contracts.py`

**Step 1: Write failing metadata assertion**

Add a wheel metadata assertion to
`tests/integration/commands/test_built_artifact_imports.py` after the wheel is
built:

```python
from email.parser import Parser
from zipfile import ZipFile


def _wheel_requires(wheel_path: Path) -> tuple[str, ...]:
    with ZipFile(wheel_path) as wheel:
        metadata_name = next(
            name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")
        )
        metadata = Parser().parsestr(wheel.read(metadata_name).decode("utf-8"))
    return tuple(metadata.get_all("Requires-Dist") or ())
```

Assert:

```python
assert any(requirement.startswith("matplotlib") for requirement in _wheel_requires(wheel_path))
```

**Step 2: Run failing test**

Run:

```bash
uv run pytest tests/integration/commands/test_built_artifact_imports.py::test_built_wheel_exposes_documented_public_imports -q
```

Expected before implementation:

- FAIL because wheel metadata does not contain `Requires-Dist: matplotlib`.

**Step 3: Move dependency**

Move `matplotlib>=3.10.8` into `[project.dependencies]`, remove it from
`dependency-groups.dev`, then run:

```bash
uv lock
```

**Step 4: Verify**

Run:

```bash
uv run pytest tests/integration/commands/test_built_artifact_imports.py::test_built_wheel_exposes_documented_public_imports -q
```

Expected:

- PASS.

### Task 2: Shared Drawdown Analytics

**Files:**

- Create: `src/quantcraft/backtest/analytics.py`
- Create or modify: `tests/unit/backtest/test_plotting.py`
- Modify later: `src/quantcraft/backtest/runtime.py`
- Modify later: `src/quantcraft/backtest/reporting.py`

**Step 1: Write failing drawdown tests**

Create `tests/unit/backtest/test_plotting.py` with tests for:

- flat
- monotonically rising
- simple drawdown
- new high resets peak
- zero running peak
- negative after positive peak
- not clamped at `1.0`
- rounded to 12 decimals

Example:

```python
import pytest

from quantcraft.backtest.analytics import drawdown_curve_for_equity


@pytest.mark.parametrize(
    ("equity", "expected"),
    [
        ((100.0, 100.0, 100.0), (0.0, 0.0, 0.0)),
        ((100.0, 110.0, 120.0), (0.0, 0.0, 0.0)),
        ((100.0, 90.0, 95.0), (0.0, 0.1, 0.05)),
        ((100.0, 90.0, 120.0, 108.0), (0.0, 0.1, 0.0, 0.1)),
        ((0.0, -5.0, -1.0), (0.0, 0.0, 0.0)),
        ((100.0, -20.0), (0.0, 1.2)),
    ],
)
def test_drawdown_curve_uses_positive_loss_fraction(equity, expected) -> None:
    assert drawdown_curve_for_equity(equity) == expected
```

**Step 2: Run failing test**

Run:

```bash
uv run pytest tests/unit/backtest/test_plotting.py::test_drawdown_curve_uses_positive_loss_fraction -q
```

Expected:

- FAIL because `quantcraft.backtest.analytics` does not exist.

**Step 3: Implement analytics helper**

Implement `drawdown_for_equity`, `drawdown_curve_for_equity`, and
`max_drawdown` as described in the architecture section.

**Step 4: Verify**

Run:

```bash
uv run pytest tests/unit/backtest/test_plotting.py -q
```

Expected:

- PASS for current drawdown helper tests.

### Task 3: Extend BacktestResult Shape And Plot Facade

**Files:**

- Modify: `src/quantcraft/backtest/results.py`
- Modify: `tests/integration/research/test_backtest_result_contract.py`
- Modify: `tests/unit/backtest/test_results.py`
- Modify or create: `tests/unit/backtest/test_plotting.py`

**Step 1: Write failing result API tests**

Add tests for:

- manual `BacktestResult(...)` positional construction still works
- manual result has default `drawdown_curve == ()`
- `drawdown_curve` participates in equality
- `BacktestResult.plot` signature has no `bars` or `source`
- `result.plot(bars=...)` and `result.plot(source=...)` raise `TypeError`
- manual result without snapshot raises `ValueError` naming run snapshot

Use `inspect.signature(BacktestResult.plot)` for the public API shape.

**Step 2: Run failing tests**

Run:

```bash
uv run pytest tests/unit/backtest/test_results.py tests/unit/backtest/test_plotting.py -q
```

Expected:

- FAIL because `drawdown_curve`, `_run_snapshot`, and `plot()` do not exist.

**Step 3: Implement result fields and facade**

Add `_BacktestRunSnapshot`, `drawdown_curve`, `_run_snapshot`, and `plot()` in
`results.py`.

Implementation constraints:

- keep `drawdown_curve` keyword-only with default `()`
- keep `_run_snapshot` keyword-only, `compare=False`, `repr=False`
- do not import Matplotlib at runtime
- do not export `_BacktestRunSnapshot`

**Step 4: Verify**

Run:

```bash
uv run pytest tests/unit/backtest/test_results.py tests/unit/backtest/test_plotting.py -q
```

Expected:

- result-shape tests pass
- plot tests still fail until plotting module is implemented

### Task 4: Populate Drawdown Curve And Run Snapshot From Runtime

**Files:**

- Modify: `src/quantcraft/backtest/runtime.py`
- Modify: `src/quantcraft/backtest/reporting.py`
- Modify: `tests/integration/research/test_backtest_result_contract.py`
- Modify: canonical summary tests that compare full `BacktestSummary` or
  `BacktestResult` values if needed

**Step 1: Write failing runtime assertions**

In `tests/integration/research/test_backtest_result_contract.py`, add:

```python
assert result.drawdown_curve == (0.0, 0.002111, 0.0)
assert result.summary.max_drawdown == max(result.drawdown_curve)
```

Update full `BacktestResult(...)` expected values for engine-produced results
to include `drawdown_curve=(...)` as a keyword argument.

**Step 2: Run focused failing test**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_result_contract.py -q
```

Expected:

- FAIL because runtime does not populate `drawdown_curve`.

**Step 3: Implement runtime population**

- import `drawdown_curve_for_equity` and `max_drawdown`
- import `_BacktestRunSnapshot`
- create `_snapshot_from_bars(...)`
- pass `drawdown_curve` and `_run_snapshot` to `BacktestResult`
- remove or stop using runtime `_max_drawdown`

**Step 4: Consolidate reporting drawdown**

Update `_ReportBuilder.record_equity(...)` to use `drawdown_for_equity(...)`.
Update report risk max drawdown to use shared `max_drawdown(...)`.

**Step 5: Verify**

Run:

```bash
uv run pytest tests/integration/research/test_backtest_result_contract.py tests/unit/backtest/test_result_reporting_metrics.py tests/unit/backtest/test_result_reporting_records.py -q
```

Expected:

- PASS.

### Task 5: Implement Plotting Module And Unit Figure Contract

**Files:**

- Create: `src/quantcraft/backtest/plotting.py`
- Modify: `tests/unit/backtest/test_plotting.py`

**Step 1: Add Matplotlib test hygiene**

In plotting tests:

```python
import matplotlib

matplotlib.use("Agg")
```

Close figures after each test:

```python
try:
    fig = result.plot()
    ...
finally:
    plt.close(fig)
```

or with a fixture:

```python
@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")
```

**Step 2: Write failing figure contract tests**

Use a narrow internal factory in the test module to create plottable results
with `_BacktestRunSnapshot`. This is acceptable for invalid/manual states and
figure contract unit tests; integration tests must use real engine paths.

Required tests:

- normal result returns a `Figure`
- exactly three axes
- title is `{symbol} {timeframe} Backtest`
- y labels are `Price`, `Equity`, `Drawdown (%)`
- x label is `Time (UTC)`
- legends include `Close`, `Buy`, `Sell`, `Equity`, `Drawdown`
- default size is `(12, 8)`
- axes share x-axis
- panel heights follow approximate `3:2:1`
- grid enabled
- close artist y-data equals snapshot closes
- equity artist y-data equals `result.equity_curve`
- drawdown artist y-data equals `-result.drawdown_curve`
- fill marker offsets use fill timestamps and execution prices
- no-fill result has no buy/sell marker artists or legend entries
- no-drawdown result has all-zero plotted drawdown values and zero baseline
- zero snapshot timestamps raise `ValueError` naming empty run data
- mismatched lengths raise `ValueError` naming `timestamps`, `equity_curve`,
  `drawdown_curve`, and observed lengths
- one-bar result plots one-point series

**Step 3: Run failing tests**

Run:

```bash
uv run pytest tests/unit/backtest/test_plotting.py -q
```

Expected:

- FAIL because `plotting.py` is missing or incomplete.

**Step 4: Implement plotting**

Implement `plot_backtest_result(...)` and private helpers described in
`Implementation Architecture`.

Use stable labels exactly:

- `Close`
- `Buy`
- `Sell`
- `Equity`
- `Drawdown`
- `Price`
- `Equity`
- `Drawdown (%)`
- `Time (UTC)`

Use `scatter(...)` for fill markers only when a side has at least one fill.

**Step 5: Verify**

Run:

```bash
uv run pytest tests/unit/backtest/test_plotting.py -q
```

Expected:

- PASS.

### Task 6: Side Effects And Import Locality

**Files:**

- Modify: `tests/unit/backtest/test_plotting.py`
- Create: `tests/structure/architecture/test_backtest_plotting_boundaries.py`

**Step 1: Add side-effect tests**

Use `monkeypatch` to patch:

- `matplotlib.pyplot.show`
- `matplotlib.pyplot.close`
- `matplotlib.figure.Figure.savefig` if needed

Assert `result.plot()` does not call them.

Also call `result.plot()` twice and assert:

- `trade_log` unchanged
- `equity_curve` unchanged
- `drawdown_curve` unchanged
- summary unchanged
- plotted data still matches original snapshot values

**Step 2: Add import-locality subprocess tests**

Use fresh interpreter subprocesses:

```python
python -c "import quantcraft.backtest, sys; assert 'matplotlib' not in sys.modules"
python -c "import quantcraft.backtest.results, sys; assert 'matplotlib' not in sys.modules"
```

Then separately verify a plot call may import Matplotlib.

**Step 3: Add structure boundary tests**

In `tests/structure/architecture/test_backtest_plotting_boundaries.py`, parse
AST imports for:

- `src/quantcraft/backtest/plotting.py`
- `src/quantcraft/backtest/__init__.py`
- `src/quantcraft/backtest/results.py`
- `src/quantcraft/data/**/*.py`
- `src/quantcraft/trading/**/*.py`

Required assertions:

- plotting implementation lives under `src/quantcraft/backtest/`
- `backtest` and `backtest.plotting` do not import `quantcraft.research`,
  `quantcraft.execution`, `apps`, or deep sibling internals
- `backtest.plotting` does not import `quantcraft.backtest.reporting`
- `data` does not import plotting code
- `trading` does not import `backtest`, `research`, or `matplotlib`

**Step 4: Verify**

Run:

```bash
uv run pytest tests/unit/backtest/test_plotting.py tests/structure/architecture/test_backtest_plotting_boundaries.py -q
```

Expected:

- PASS.

### Task 7: Engine Integration Tests For `bars=...` And `source=...`

**Files:**

- Create: `tests/integration/backtest/test_plotting.py`

**Step 1: Create backtest integration test directory**

Create:

```text
tests/integration/backtest/test_plotting.py
```

Use local deterministic fixtures rather than importing support from
`tests/integration/research/...` when practical. It is fine for strategies to
subclass `quantcraft.research.Strategy` because this is the current public
strategy authoring surface.

**Step 2: Write failing integration tests**

Cover:

- `BacktestEngine.run(bars=...).plot()`
- `BacktestEngine.run(source=...).plot()`
- source fake `load_count == 1`
- source mutation after run does not change plotted closes
- mutable upstream records mutated after `BarSeries` construction do not change
  plotted closes
- no-trade strategy still plots close/equity/drawdown and no buy/sell markers
- drawdown-producing strategy has positive `result.drawdown_curve`,
  `summary.max_drawdown == max(result.drawdown_curve)`, and plotted drawdown
  equals `-result.drawdown_curve`
- plot is independent of `BacktestReport` by verifying plotted data comes from
  result-owned fields and by relying on the structure test from Task 6

**Step 3: Run failing tests**

Run:

```bash
uv run pytest tests/integration/backtest/test_plotting.py -q
```

Expected:

- Initially FAIL until runtime snapshot and plotting are complete.

**Step 4: Implement only missing integration support**

If tests need repeated fixture logic, keep it local to
`tests/integration/backtest/test_plotting.py` unless it is clearly useful to
existing tests.

**Step 5: Verify**

Run:

```bash
uv run pytest tests/integration/backtest/test_plotting.py -q
```

Expected:

- PASS.

### Task 8: 10,000-Bar Scale Contract And Poe Perf Lane

**Files:**

- Create: `tests/perf/test_backtest_plotting_scale.py`
- Modify: `pyproject.toml`
- Modify: `tests/structure/repo/test_repo_check_contracts.py` if hard-coded
  sample fixtures need the new `perf-check` command

**Step 1: Write failing perf-adjacent test**

Create deterministic 10,000-bar input with a no-fill strategy to keep runtime
simple.

Required assertions:

- non-interactive backend
- `result.plot()` completes
- three axes
- close, equity, and drawdown artists each retain 10,000 x-points
- no source reload
- no `show()`
- no file write

Do not add a timing threshold.

**Step 2: Run selected perf test**

Run:

```bash
uv run pytest tests/perf/test_backtest_plotting_scale.py -q -x --run-perf
```

Expected:

- FAIL before plotting implementation; PASS after plotting implementation.

**Step 3: Update Poe perf lane**

Change:

```toml
"perf-check" = { cmd = "pytest tests/perf/test_rsi_backtest_benchmark.py -q -x --run-perf", ... }
```

to:

```toml
"perf-check" = { cmd = "pytest tests/perf -q -x --run-perf", ... }
```

Update any structure-test fixtures that encode the old example command.

**Step 4: Verify**

Run:

```bash
uv run poe perf-check
```

Expected:

- Existing RSI perf tests and new plotting scale test all run.

### Task 9: Docs, Quickstart, And Notebook Examples

**Files:**

- Modify: `docs/references/research-ergonomics-quickstart.md`
- Modify: `notebooks/research-ergonomics-quickstart.ipynb`
- Modify: `tests/structure/docs/test_backtest_result_reporting_docs.py` or add
  `tests/structure/docs/test_backtest_plotting_docs.py`
- Possibly modify: `docs/product-specs/research-ergonomics.md`

**Step 1: Write failing docs structure tests**

Add a plotting-specific docs test that asserts:

- quickstart shows `fig = result.plot()` or `result.plot()`
- quickstart shows `plt.show()` separately
- quickstart shows `fig.savefig(...)`
- docs do not show `result.plot(bars=...)`
- docs do not promote `plot_backtest(...)`, `BacktestEngine.plot()`, or
  `result.report.plot()`
- notebook source includes `result.plot()` on at least one canonical result

**Step 2: Run failing docs tests**

Run:

```bash
uv run pytest tests/structure/docs -q
```

Expected:

- FAIL until docs/notebook are updated.

**Step 3: Update docs**

In quickstart, keep `result.report` as the primary structured report path but
add visual inspection:

```python
fig = result.plot()
```

Document display/export as standard Matplotlib:

```python
plt.show()
fig.savefig("backtest.png")
```

Do not add custom export helpers.

**Step 4: Update notebook**

Add a cell that calls `sma_result.plot()` or assigns `fig = sma_result.plot()`.
Avoid network or live dependencies.

**Step 5: Verify**

Run:

```bash
uv run pytest tests/structure/docs -q
uv run poe notebook-validate
```

Expected:

- PASS.

### Task 10: Final Verification And Review

**Files:**

- No new implementation files unless prior verification reveals a targeted fix.

**Step 1: Run focused verification**

Run:

```bash
uv run pytest tests/unit/backtest/test_results.py tests/unit/backtest/test_plotting.py -q
uv run pytest tests/integration/backtest/test_plotting.py -q
uv run pytest tests/smoke/local tests/integration/commands/test_built_artifact_imports.py -q
uv run pytest tests/structure/architecture tests/structure/docs tests/structure/repo -q
uv run pytest tests/perf -q -x --run-perf
```

Expected:

- PASS.

**Step 2: Run repo quality gates**

Run:

```bash
uv run ruff check .
uv run mypy src
uv run python scripts/coverage_check.py
uv run python scripts/repo_check.py
uv build
```

Expected:

- PASS.

**Step 3: Run runtime-sensitive full lane**

Run:

```bash
uv run poe verify-runtime
```

Expected:

- PASS.

**Step 4: Evaluate diff**

Review the diff against:

- `docs/product-specs/backtest-plotting.md`
- `docs/product-specs/backtest-plotting-test-scenarios.md`
- `ARCHITECTURE.md`
- this implementation plan

Auto-fail the slice if:

- `result.plot()` accepts any bars/source/report argument
- Matplotlib is imported during normal `quantcraft.backtest` import
- `plotting.py` imports `research` or `reporting`
- plot data comes from `BacktestReport`
- 10,000-bar test is not run by `uv run poe verify-runtime`
- built wheel metadata does not include Matplotlib

## Implementation Handoff Notes

- Start with dependency/package metadata because many later tests import
  Matplotlib.
- Add analytics before runtime changes so drawdown behavior is pinned first.
- Add result fields before runtime population so existing positional
  construction compatibility is protected.
- Implement plot unit tests before integration tests so Matplotlib behavior is
  easier to debug.
- Use observable plotted data as the primary assertion for snapshot
  independence; only internal invalid-state tests may construct private
  `_BacktestRunSnapshot` values.
- Keep new public API surface to exactly `BacktestResult.plot()`.

## Evaluator Review

- Findings:
  - The implementation satisfies the first-beta `BacktestResult.plot()`
    contract: the public API is no-argument `result.plot()`, returns a
    Matplotlib figure, and renders price, fills, equity, and underwater
    drawdown from result-owned run data.
  - Plotting remains owned by `quantcraft.backtest`; it does not route through
    `BacktestReport`, does not import `research`, `execution`, or
    `integrations`, and Matplotlib imports remain lazy until plotting is
    invoked.
  - Runtime now stores an immutable private run snapshot and
    `drawdown_curve`; reporting and runtime share pure drawdown helpers so
    summary/report/plot drawdown semantics stay aligned.
  - Subagent review found three material test/evidence gaps. They were fixed by
    removing the environment-sensitive 10,000-bar timing threshold, asserting
    main line timestamp x-data, adding separate mismatch cases for timestamp,
    equity, and drawdown lengths, and recording this fresh evaluator evidence.
  - No remaining blocking findings from the spec/API UX, architecture, or
    testing review passes.
- Verification evidence:
  - `uv run pytest tests/unit/backtest/test_plotting.py tests/perf/test_backtest_plotting_scale.py -q -x --run-perf`
    passed on 2026-05-02 with `16 passed`.
  - `uv run poe verify-runtime` passed on 2026-05-02 after post-review fixes
    with `531 passed, 4 skipped`, coverage policy passed, `uv build` produced
    source and wheel artifacts, repository checks passed, notebooks validated,
    and `tests/perf` passed with `3 passed`.
- Final disposition:
  - Accepted as implemented for the first-beta backtest plotting workflow.
