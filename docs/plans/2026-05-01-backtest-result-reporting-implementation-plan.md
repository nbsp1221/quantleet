# Backtest Result Reporting Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the first-beta single-symbol backtest reporting surface so an engine-produced `BacktestResult` exposes a typed, human-readable, and machine-readable `result.report`.

**Architecture:** Keep reporting ownership inside `quantcraft.backtest`, because the report is derived from historical runtime data and must not contaminate the shared `trading` kernel. Add an additive `BacktestResult.report` property backed by runtime-collected provenance, pure metric functions, and frozen report dataclasses. Preserve existing `BacktestResult`, `BacktestSummary`, `trade_log`, `equity_curve`, and `order_events` behavior while making richer beta reporting available from the returned result.

**Tech Stack:** Python 3.13, stdlib dataclasses, `math`, `statistics`, pytest, Ruff, mypy, uv, Poe task runner. No new runtime dependency.

---

## Repo Workflow Planner Contract

- Date: `2026-05-01`
- Task: `Implement the backtest result reporting beta slice`
- Status: `active`
- Risk class: `Tier B`
- Requestor: `User`
- Owner: `Codex`

### Planner Contract

- Goal:
  - Convert the accepted result-reporting spec and test-scenario spec into a
    concrete implementation plan.
  - Keep the implementation bounded to first-beta single-symbol, long-only
    historical backtesting.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/PLANS.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/references/testing.md`
  - `docs/references/research-ergonomics-quickstart.md`
  - `docs/research/libraries/backtesting-py.md`
  - `docs/plans/2026-04-30-backtest-result-reporting-spec.md`
  - `docs/plans/2026-05-01-backtest-result-reporting-test-scenarios.md`
- Why these are governing:
  - The product specs define current backtest/research scope and the first-beta
    UX target.
  - The active result-reporting spec fixes the user-facing reporting contract,
    metric formulas, and final API/DX decisions.
  - The test-scenario spec fixes the contract-first test portfolio that this
    implementation must satisfy.
  - The architecture docs keep reporting inside `backtest` and keep the
    shared `trading` kernel free of report-only fields.
- In-repo scope:
  - Add `result.report` for engine-produced `BacktestResult` values.
  - Add report dataclasses, pure metric calculations, and grouped text
    rendering.
  - Capture runtime provenance needed for run identity, execution assumptions,
    timestamped equity rows, reporting fill rows, closed-trade rows, fees,
    exposure, and ending state.
  - Add unit, integration, smoke, and structure tests from the scenario spec.
  - Promote the durable reporting contract into the routed product-spec and
    quickstart surfaces.
- Out-of-repo scope:
  - No PyPI publishing.
  - No external service integration.
  - No network-backed live tests.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A approval is not required for this plan because the implementation
    must not modify `src/quantcraft/trading` or `src/quantcraft/execution`.
  - If execution discovers that `trading` changes are necessary, stop and create
    a Tier A approval record before implementation continues.
- Verification commands:
  - focused pytest commands listed under each task
  - `uv run pytest tests/unit/backtest tests/unit/research tests/integration/research tests/smoke/local -q`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run python scripts/coverage_check.py`
  - `uv run python scripts/repo_check.py`
  - `uv build`
  - `uv run poe verify-runtime`
- Success criteria:
  - `engine.run(...).report` is directly reachable as `result.report`.
  - Existing result fields and existing basic `engine.run(...)` calls remain
    compatible.
  - Metric semantics match the accepted spec, including no public `NaN`,
    `None` for undefined beta metrics, sample volatility, CAGR annualized
    return, net-of-fees profit factor, and any-position-during-bar exposure.
  - Reporting rows preserve order id, order type, and tag provenance without
    adding `tag` to `FillEvent`.
  - The durable product docs and quickstart no longer describe only
    `result.summary` as the primary inspection path.
  - Runtime-sensitive verification passes or unavailable verification is
    explicitly recorded.
- Out of scope:
  - Plotting.
  - Optimizer or parameter sweeps.
  - Multi-symbol, short, leverage, margin, paper trading, or live trading.
  - FIFO, tax-lot, or multiple accounting views.
  - Changing `FillEvent`, `Order`, `OrderIntent`, or `TradingState` for
    report-only data.
  - Adding new third-party dependencies.
  - Creating commits; this repository session is intentionally local-only per
    user direction.

### Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close only after the implementation plan is grounded in the current source
    tree, points to exact files, preserves architecture boundaries, and records
    fresh repository-document verification.
- Acceptance artifact location:
  - `docs/plans/2026-05-01-backtest-result-reporting-implementation-plan.md`
- How the generator and evaluator agreed on done before execution:
  - This document must explain exactly how to implement the accepted specs,
    what files to touch, what tests to write first, and how to verify each
    slice.
- Checks the evaluator will use:
  - Manual review against the accepted spec and test-scenario docs.
  - Manual review against the current source/test layout.
  - `uv run poe repo-check`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q`.
- Auto-fail conditions:
  - Prescribing changes under `src/quantcraft/trading` without Tier A approval.
  - Adding report-only fields to `FillEvent` or `TradingState`.
  - Making a helper-only report API instead of `result.report`.
  - Relying on arbitrary public strategy-attribute introspection.
  - Leaving execution assumptions as prose-only labels.
  - Omitting runtime-sensitive verification from the final implementation gate.

### Generator Work Log

- Planned slice order:
  1. Read governing docs and active reporting specs.
  2. Survey source, tests, quickstart docs, and verification task layout.
  3. Identify reusable code, ownership boundaries, and implementation gaps.
  4. Write this how-focused implementation plan.
  5. Run repository/document verification for the plan document.
  6. Record evaluator findings and final disposition.
- Notes:
  - This plan intentionally modifies no runtime source code.
  - The implementation execution phase should follow this plan with TDD.
  - Commit steps are omitted because the user explicitly said local commits are
    unnecessary for this workflow.
- Blockers or scope changes:
  - None at plan-writing time.

## Codebase Survey Summary

### Current Architecture

The repository is a Python 3.13 local-first library under `src/quantcraft` with
capability-first package ownership:

- `quantcraft.data` owns normalized historical bar inputs.
- `quantcraft.research` owns user strategy ergonomics.
- `quantcraft.backtest` owns historical orchestration, synthetic execution
  modeling, runtime result assembly, and now richer reporting.
- `quantcraft.trading` owns the shared trading kernel and is Tier A.

The reporting implementation must stay in `backtest` and `research`. It must
read trading-domain objects, but it must not move reporting concerns into the
trading kernel.

### Current Backtest Path

The current execution path is:

```text
BacktestEngine.run(bars/source, strategy)
  -> _validated_bars(...)
  -> _run_backtest(...)
  -> _StrategyDriver(strategy)
  -> Strategy.buy/sell(...)
  -> PendingOrderRequest
  -> Order
  -> ConservativeOHLCVExecutionModel.tick_events_for_bar(...)
  -> match_order(...)
  -> apply_fill(...)
  -> BacktestResult(trade_log, equity_curve, final_state, summary, order_events)
```

Source evidence:

- `BacktestResult` currently exposes `trade_log`, `equity_curve`,
  `final_state`, `summary`, `execution_model_name`, and `order_events` in
  `src/quantcraft/backtest/results.py`.
- `BacktestEngine.run(...)` currently accepts only `strategy`, `bars`, and
  `source` in `src/quantcraft/backtest/engine.py`.
- `_run_backtest(...)` already has the data needed to collect most report
  provenance: bars, costs, execution model, active orders, fills, order
  rejections, marked equity, and final state.
- Current exposure is end-of-bar only. The beta report requires
  any-position-during-bar exposure, so runtime must record whether a positive
  position existed at any point in the bar.
- Current closed-trade stats are only a list of net PnL values. The beta report
  needs explicit closed-trade rows with gross/net PnL, allocated fees, entry
  tags, exit tag, timestamps, and duration.

### Current Strategy Metadata Gap

`Strategy` currently has `init()`, `on_bar()`, `buy()`, `sell()`, `data`, and
`position`, but it does not expose:

- `display_name`
- `parameters()`

The implementation must add those explicit hooks to `Strategy` and to
`StrategyLike`. It must not infer parameters from arbitrary public attributes.

### Current Test And Verification Layout

Reusable test locations:

- `tests/unit/backtest/test_engine.py`
- `tests/unit/backtest/test_execution_model.py`
- `tests/unit/research/test_strategy_surface.py`
- `tests/integration/research/test_backtest_result_contract.py`
- `tests/integration/research/support_backtest_runner.py`
- `tests/smoke/local/test_public_imports.py`
- `tests/structure/docs/test_research_ergonomics_quickstart.py`

New reporting tests should follow the accepted scenario spec:

- `tests/unit/backtest/test_result_reporting_metrics.py`
- `tests/unit/backtest/test_result_reporting_records.py`
- `tests/integration/research/test_backtest_result_reporting_contract.py`
- `tests/integration/research/test_backtest_result_reporting_edge_cases.py`
- `tests/smoke/local/test_backtest_result_reporting_quickstart.py`
- `tests/structure/docs/test_backtest_result_reporting_docs.py`

Because this will touch runtime-sensitive backtest and research paths, final
implementation verification must include `uv run poe verify-runtime`.

## Implementation Design

### File Ownership

Create:

- `src/quantcraft/backtest/reporting.py`
- `tests/unit/backtest/test_result_reporting_metrics.py`
- `tests/unit/backtest/test_result_reporting_records.py`
- `tests/integration/research/test_backtest_result_reporting_contract.py`
- `tests/integration/research/test_backtest_result_reporting_edge_cases.py`
- `tests/smoke/local/test_backtest_result_reporting_quickstart.py`
- `tests/structure/docs/test_backtest_result_reporting_docs.py`

Modify:

- `src/quantcraft/backtest/results.py`
- `src/quantcraft/backtest/runtime.py`
- `src/quantcraft/backtest/engine.py`
- `src/quantcraft/backtest/strategy_runtime.py`
- `src/quantcraft/backtest/__init__.py`
- `src/quantcraft/research/strategy.py`
- `docs/product-specs/research-ergonomics.md`
- `docs/references/research-ergonomics-quickstart.md`
- `notebooks/research-ergonomics-quickstart.ipynb`
- existing focused tests where public signatures or import surfaces need
  additive assertions

Do not modify:

- `src/quantcraft/trading/domain/events.py`
- `src/quantcraft/trading/domain/state.py`
- `src/quantcraft/trading/domain/orders.py`
- `src/quantcraft/trading/domain/intents.py`

### Public API Contract

Implement:

```python
result = engine.run(source=source, strategy=SmaCrossStrategy(), label="sma-20-50")
report = result.report
print(report)
```

Add:

- `BacktestEngine.run(..., label: str | None = None)`
- `Strategy.display_name -> str | None`
- `Strategy.parameters() -> dict[str, object]`
- `BacktestResult.report -> BacktestReport`

`BacktestEngine.run(...)` must keep existing calls valid. `label` is a
keyword-only optional argument after `source`.

### Report Model

Add frozen dataclasses in `src/quantcraft/backtest/reporting.py`:

```python
@dataclass(frozen=True, slots=True)
class RunManifest:
    symbol: str
    timeframe: str
    start_timestamp: int
    end_timestamp: int
    bar_count: int
    initial_cash: float
    execution_model_name: str
    strategy_class_name: str
    strategy_display_name: str | None
    strategy_parameters: dict[str, object]
    run_label: str | None

@dataclass(frozen=True, slots=True)
class ExecutionAssumptions:
    execution_model_name: str
    order_activation_timing: str
    fill_price_basis: str
    open_position_finalization: str
    tick_size: float
    slippage_ticks: float
    fee_rate: float
    order_rejection_count: int
    annual_risk_free_rate: float
    periods_per_year: float | None

@dataclass(frozen=True, slots=True)
class EquityPoint:
    bar_index: int
    timestamp: int
    equity: float
    cash: float
    position_quantity: float
    mark_price: float
    drawdown: float

@dataclass(frozen=True, slots=True)
class ReportingFill:
    order_id: int
    order_type: str
    tag: str | None
    timestamp: int
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float

@dataclass(frozen=True, slots=True)
class ClosedTrade:
    entry_timestamp: int
    exit_timestamp: int
    entry_bar_index: int
    exit_bar_index: int
    duration_bars: int
    quantity: float
    entry_price: float
    exit_price: float
    gross_pnl: float
    net_pnl: float
    allocated_entry_fee: float
    exit_fee: float
    total_fees: float
    net_return: float | None
    entry_tag: str | None
    entry_tags: tuple[str, ...]
    exit_tag: str | None
```

Also add grouped metric dataclasses:

- `ReturnMetrics`
- `RiskMetrics`
- `TradeMetrics`
- `CostMetrics`
- `ExposureMetrics`
- `BacktestReport`

`BacktestReport` owns `to_text()` and `__str__()`. Human-readable rendering
should use grouped sections and `n/a` for `None`, but tests must not assert full
formatted snapshots.

### Runtime Provenance Pattern

Use a report-owned mutable builder internally, then freeze it into dataclasses
before attaching it to `BacktestResult`.

Recommended internal type:

```python
class _ReportBuilder:
    def record_fill(
        self,
        *,
        order: Order,
        fill: FillEvent,
        state_before: TradingState,
        state_after: TradingState,
        bar_index: int,
    ) -> None: ...

    def record_equity(
        self,
        *,
        bar_index: int,
        timestamp: int,
        mark_price: float,
        state: TradingState,
    ) -> None: ...

    def build(self, ...) -> BacktestReport: ...
```

The builder must live in `quantcraft.backtest.reporting`, not `trading`.
`runtime.py` should call it at the two fill application sites and at each
end-of-bar mark.

### Exposure Semantics

Replace report exposure evidence with any-position-during-bar semantics:

- At each bar start, initialize `bar_had_position = state.position_quantity > 0.0`.
- After each accepted fill, update `bar_had_position = bar_had_position or state.position_quantity > 0.0 or state_before.position_quantity > 0.0`.
- After end-of-bar mark, increment report `bars_in_position` if `bar_had_position`.
- Preserve legacy `BacktestSummary.exposure` behavior only if tests require old
  behavior. Prefer aligning summary to the new report exposure only if existing
  tests are updated intentionally.

### Metric Rules

Implement pure helpers in `reporting.py` and unit-test them before integration:

- `none_if_undefined(...)` style helpers should return `None`, not `NaN`.
- Return series uses the full marked equity curve, including the first mark.
- `total_return = (final_equity - initial_cash) / initial_cash`
- `buy_and_hold_return = (last_close - first_close) / first_close`, with
  `None` for invalid zero denominator.
- `active_return = total_return - buy_and_hold_return` when both exist.
- `annualized_return` is CAGR over the observed periodic equity series.
- Volatility uses sample standard deviation (`ddof=1`) over periodic returns.
- Sharpe uses period risk-free conversion from annual risk-free rate, default
  `0.0`.
- `max_drawdown` is non-negative magnitude.
- `longest_drawdown_bar_count` counts consecutive bars below the prior peak.
- `profit_factor` uses net closed-trade PnL.
- A gross winner flipped to net loser by fees is a losing trade.
- No-trade report metrics are `None`; legacy `BacktestSummary` zero defaults
  may remain until a later migration.

Timeframe annualization:

- Parse only fixed tokens: `ms`, `s`, `m`, `h`, `d`, `w`.
- Use calendar year `365.2425` days.
- If timeframe is parseable, use nominal cadence even when timestamp gaps
  exist.
- Month-like or unsupported tokens fall back to timestamp deltas.
- Expose `periods_per_year` in the report.

Execution assumptions:

- `order_activation_timing = "next_bar"`
- `fill_price_basis = "conservative_ohlcv"`
- `open_position_finalization = "mark_to_market"`

### Compatibility Pattern

Add an internal optional report field without breaking positional construction:

```python
@dataclass(frozen=True, slots=True)
class BacktestResult:
    ...
    order_events: tuple[OrderRejectedEvent, ...] = ()
    _report: BacktestReport | None = field(default=None, compare=False, repr=False, kw_only=True)

    @property
    def report(self) -> BacktestReport:
        if self._report is None:
            raise ValueError("report is only available for engine-produced BacktestResult values")
        return self._report
```

Rationale:

- Existing positional tests remain valid.
- Engine-produced results always have a report.
- Manually constructed legacy results fail loudly if a caller asks for missing
  report provenance.

## TDD Task Plan

### Task 1: Public API Shape And Compatibility

**Files:**

- Modify: `tests/unit/backtest/test_engine.py`
- Modify: `tests/unit/research/test_strategy_surface.py`
- Modify: `tests/integration/research/test_backtest_result_contract.py`
- Modify: `src/quantcraft/backtest/engine.py`
- Modify: `src/quantcraft/research/strategy.py`
- Modify: `src/quantcraft/backtest/results.py`

**Step 1: Write failing tests**

Add tests that assert:

- `BacktestEngine.run(..., label="demo")` is accepted.
- `BacktestEngine.run(..., label="")` raises `ValueError`.
- `Strategy.display_name` defaults to `None`.
- `Strategy.parameters()` defaults to `{}`.
- A subclass can override `display_name` and `parameters()`.
- Existing positional `BacktestResult(...)` construction still works.
- Engine-produced results expose `result.report`.

**Step 2: Run focused tests and verify failure**

Run:

```bash
uv run pytest tests/unit/backtest/test_engine.py tests/unit/research/test_strategy_surface.py tests/integration/research/test_backtest_result_contract.py -q
```

Expected:

- Failures for missing `label`, missing strategy metadata hooks, and missing
  `result.report`.

**Step 3: Implement minimal API**

- Add `label: str | None = None` to `BacktestEngine.run(...)`.
- Validate `label` is either `None` or a non-empty string.
- Pass `label` into `_run_backtest(...)`.
- Add `display_name` and `parameters()` to `Strategy`.
- Extend `StrategyLike` with `display_name` and `parameters()`.
- Add `_report` and the `report` property to `BacktestResult`.

**Step 4: Run focused tests and verify pass**

Run the same focused command.

Expected:

- API shape and compatibility tests pass.

### Task 2: Reporting Dataclasses And Public Import Surface

**Files:**

- Create: `src/quantcraft/backtest/reporting.py`
- Modify: `src/quantcraft/backtest/__init__.py`
- Modify: `tests/smoke/local/test_public_imports.py`
- Create: `tests/unit/backtest/test_result_reporting_records.py`

**Step 1: Write failing tests**

Assert:

- `quantcraft.backtest.BacktestReport` imports from the public backtest surface.
- Report dataclasses are frozen and expose the required fields.
- Structured values are accessible without parsing formatted text.
- `str(report)` or `report.to_text()` contains grouped section labels, but the
  test does not assert exact spacing.

**Step 2: Run focused tests and verify failure**

```bash
uv run pytest tests/smoke/local/test_public_imports.py tests/unit/backtest/test_result_reporting_records.py -q
```

Expected:

- Fails because `reporting.py` and exports do not exist.

**Step 3: Implement dataclass skeleton**

- Add report dataclasses listed in this plan.
- Add `BacktestReport.to_text()` and `__str__()`.
- Export `BacktestReport` and stable public dataclasses from
  `quantcraft.backtest`.

**Step 4: Run focused tests and verify pass**

Run the same focused command.

### Task 3: Pure Metric Helpers

**Files:**

- Create: `tests/unit/backtest/test_result_reporting_metrics.py`
- Modify: `src/quantcraft/backtest/reporting.py`

**Step 1: Write failing metric tests**

Cover these scenario IDs from the test-scenario spec:

- `RR-UNIT-001`
- `RR-UNIT-002`
- `RR-UNIT-002A`
- `RR-UNIT-003`
- `RR-UNIT-004`
- `RR-UNIT-005`
- `RR-UNIT-006`
- `RR-UNIT-007`
- `RR-UNIT-008`
- `RR-UNIT-009`
- `RR-UNIT-010`
- `RR-UNIT-011`
- `RR-UNIT-012`
- `RR-UNIT-013`
- `RR-UNIT-016`
- `RR-UNIT-017`
- `RR-UNIT-018`
- `RR-UNIT-019`
- `RR-UNIT-020`
- `RR-UNIT-021`
- `RR-UNIT-022`

Use hand-computable fixtures only. Do not recompute production formulas inside
assertions.

**Step 2: Run focused tests and verify failure**

```bash
uv run pytest tests/unit/backtest/test_result_reporting_metrics.py -q
```

Expected:

- Fails because helpers are missing or incomplete.

**Step 3: Implement pure helpers**

Implement:

- timeframe parsing and `periods_per_year`
- periodic return extraction
- CAGR annualized return
- sample volatility
- Sharpe with annual risk-free default `0.0`
- max drawdown and longest drawdown bar count
- buy-and-hold return
- net-of-fees trade statistics
- no-public-NaN sentinel normalization

**Step 4: Run focused tests and verify pass**

```bash
uv run pytest tests/unit/backtest/test_result_reporting_metrics.py -q
```

Expected:

- All metric helper tests pass.

### Task 4: Runtime Report Builder And Equity Rows

**Files:**

- Modify: `src/quantcraft/backtest/reporting.py`
- Modify: `src/quantcraft/backtest/runtime.py`
- Create: `tests/integration/research/test_backtest_result_reporting_contract.py`

**Step 1: Write failing integration tests**

Cover:

- `RR-INT-001`
- `RR-INT-004`
- `RR-INT-009`
- `RR-INT-011`

Assert:

- `result.report.run.symbol`, timeframe, timestamps, bar count, initial cash,
  and execution model match input.
- `result.report.execution.order_activation_timing == "next_bar"`.
- `result.report.execution.fill_price_basis == "conservative_ohlcv"`.
- `result.report.execution.open_position_finalization == "mark_to_market"`.
- `result.report.equity` rows include timestamps and final row equals final
  reported equity.
- Existing `result.trade_log`, `result.equity_curve`, `result.summary`, and
  `result.order_events` stay available.

**Step 2: Run focused tests and verify failure**

```bash
uv run pytest tests/integration/research/test_backtest_result_reporting_contract.py -q
```

Expected:

- Fails because `_run_backtest(...)` does not build a report.

**Step 3: Implement builder attachment**

- Instantiate `_ReportBuilder` in `_run_backtest(...)`.
- Record equity rows after each marked end-of-bar state.
- Build `BacktestReport` before returning `BacktestResult`.
- Pass `_report=report` to `BacktestResult`.
- Keep existing summary construction intact unless a test intentionally updates
  exposure semantics.

**Step 4: Run focused tests and verify pass**

Run the same integration command.

### Task 5: Strategy Metadata And Run Labels

**Files:**

- Modify: `src/quantcraft/backtest/engine.py`
- Modify: `src/quantcraft/backtest/runtime.py`
- Modify: `src/quantcraft/backtest/reporting.py`
- Modify: `tests/integration/research/test_backtest_result_reporting_contract.py`

**Step 1: Write failing tests**

Cover `RR-INT-002`:

- class name visible when `display_name is None`
- `Strategy.display_name` visible when supplied
- `BacktestEngine.run(..., label=...)` preserved
- `parameters()` values preserved
- arbitrary public attributes are ignored

**Step 2: Run focused tests and verify failure**

```bash
uv run pytest tests/integration/research/test_backtest_result_reporting_contract.py::test_report_captures_strategy_identity_and_explicit_parameters -q
```

Expected:

- Fails until runtime passes strategy metadata into the report builder.

**Step 3: Implement metadata capture**

- Add a small validation helper in `reporting.py`:
  - keys must be non-empty strings
  - reject or stringify unsupported nested values only if tests require it
  - copy the returned mapping so later strategy mutation cannot change the
    report
- Build the run manifest from `type(strategy).__name__`,
  `strategy.display_name`, `strategy.parameters()`, and `label`.

**Step 4: Run focused tests and verify pass**

Run the same focused test.

### Task 6: Reporting Fill Rows And Closed-Trade Accounting

**Files:**

- Modify: `src/quantcraft/backtest/reporting.py`
- Modify: `src/quantcraft/backtest/runtime.py`
- Create/modify: `tests/unit/backtest/test_result_reporting_records.py`
- Modify: `tests/integration/research/test_backtest_result_reporting_edge_cases.py`

**Step 1: Write failing tests**

Cover:

- `RR-UNIT-014`
- `RR-UNIT-015`
- `RR-UNIT-018`
- `RR-UNIT-019`
- `RR-UNIT-020`
- `RR-UNIT-021`
- `RR-INT-005`

Assert:

- reporting fill rows include `order_id`, `order_type`, and `tag`
- raw `FillEvent` remains unchanged
- closed-trade rows include entry/exit timestamps, quantity, prices, gross PnL,
  net PnL, allocated entry fee, exit fee, net return, duration, entry tag,
  entry tags, and exit tag
- weighted-average aggregate accounting is used
- partial closes allocate entry fees proportionally
- mixed entry tags produce `entry_tag is None` and preserve `entry_tags`
- net profit factor treats fee-flipped losers as losers
- order rejections remain separate from fills

**Step 2: Run focused tests and verify failure**

```bash
uv run pytest tests/unit/backtest/test_result_reporting_records.py tests/integration/research/test_backtest_result_reporting_edge_cases.py -q
```

Expected:

- Fails because fill provenance and closed-trade rows are not implemented.

**Step 3: Implement fill and trade recording**

- Call `_ReportBuilder.record_fill(...)` immediately after each accepted fill.
- Pass both `state_before` and `state_after`.
- Track aggregate open position:
  - aggregate entry starts when prior quantity is zero and a buy fill opens a
    position
  - increases update weighted-average entry price and append non-null entry tags
  - partial exits create one closed-trade row and keep aggregate entry timestamp
    for remaining inventory
  - final exit resets aggregate state
- Use current `Order` facts for `order_id`, `order_type`, and `tag`.
- Do not modify `FillEvent`.

**Step 4: Run focused tests and verify pass**

Run the same focused command.

### Task 7: Exposure, Ending State, And Empty Input

**Files:**

- Modify: `src/quantcraft/backtest/engine.py`
- Modify: `src/quantcraft/backtest/runtime.py`
- Modify: `src/quantcraft/backtest/reporting.py`
- Modify: `tests/integration/research/test_backtest_result_reporting_edge_cases.py`

**Step 1: Write failing tests**

Cover:

- `RR-INT-003`
- `RR-INT-008`
- `RR-UNIT-023`

Assert:

- empty `BarSeries` is rejected before reporting
- a carried position that exits intrabar and is flat at bar close still counts
  as exposed for that bar
- `ending_state == "flat"` when final position quantity is zero
- `ending_state == "open"` when final position quantity is positive

**Step 2: Run focused tests and verify failure**

```bash
uv run pytest tests/integration/research/test_backtest_result_reporting_edge_cases.py -q
```

Expected:

- Fails because empty input and any-position exposure are not implemented.

**Step 3: Implement behavior**

- Reject empty `BarSeries.rows` in `_validated_bars(...)`.
- Add per-bar `bar_had_position` tracking in runtime.
- Attach `ExposureMetrics` and ending state to `BacktestReport`.
- Decide whether to align `BacktestSummary.exposure` with the report exposure.
  If this changes existing expected values, update only the tests whose
  expectations are explicitly about exposure.

**Step 4: Run focused tests and verify pass**

Run the same focused command.

### Task 8: Human-Readable Report And Quickstart Smoke

**Files:**

- Modify: `src/quantcraft/backtest/reporting.py`
- Create: `tests/smoke/local/test_backtest_result_reporting_quickstart.py`
- Modify: `tests/smoke/local/test_public_imports.py`

**Step 1: Write failing smoke tests**

Cover:

- `RR-SMOKE-001`
- `RR-SMOKE-002`
- `RR-SMOKE-003`
- `RR-INT-010`

Assert:

- local `DataFrameDataSource` quickstart path executes
- `result.report` is directly reachable
- `str(result.report)` contains grouped labels for return, risk, trade
  quality, costs, exposure/ending state, and execution assumptions
- undefined values render as `n/a`
- no private imports are needed

**Step 2: Run focused smoke tests and verify failure**

```bash
uv run pytest tests/smoke/local/test_public_imports.py tests/smoke/local/test_backtest_result_reporting_quickstart.py -q
```

Expected:

- Fails until text rendering and quickstart smoke path are complete.

**Step 3: Implement text rendering**

- Implement `BacktestReport.to_text()` with stable group headings.
- Keep formatting compact and notebook-friendly.
- Use `n/a` for `None`.
- Do not use broad snapshots in tests.

**Step 4: Run focused smoke tests and verify pass**

Run the same smoke command.

### Task 9: Product Spec, Quickstart, And Notebook Sync

**Files:**

- Modify: `docs/product-specs/research-ergonomics.md`
- Modify: `docs/references/research-ergonomics-quickstart.md`
- Modify: `notebooks/research-ergonomics-quickstart.ipynb`
- Create: `tests/structure/docs/test_backtest_result_reporting_docs.py`
- Modify if needed: `tests/structure/docs/test_research_ergonomics_quickstart.py`

**Step 1: Write failing structure tests**

Assert:

- routed product docs mention `result.report`
- quickstart shows `result.report`
- quickstart still shows canonical imports and both `source=...` and `bars=...`
  paths
- quickstart no longer presents `result.summary` as the only primary inspection
  route
- notebook source includes `result.report`

**Step 2: Run focused structure tests and verify failure**

```bash
uv run pytest tests/structure/docs/test_backtest_result_reporting_docs.py tests/structure/docs/test_research_ergonomics_quickstart.py -q
```

Expected:

- Fails until docs and notebook are updated.

**Step 3: Update docs and notebook**

- Promote the durable reporting contract into
  `docs/product-specs/research-ergonomics.md`.
- Update quickstart inspection section:
  - primary: `result.report`
  - still available: `result.trade_log`, `result.equity_curve`,
    `result.summary`
- Update notebook cells to display `result.report`.

**Step 4: Run focused structure tests and notebook validation**

```bash
uv run pytest tests/structure/docs/test_backtest_result_reporting_docs.py tests/structure/docs/test_research_ergonomics_quickstart.py -q
uv run poe notebook-validate
```

Expected:

- Structure tests pass.
- Notebook validation passes.

### Task 10: Full Focused Verification

**Files:**

- No new source files beyond prior tasks.

**Step 1: Run focused reporting suite**

```bash
uv run pytest tests/unit/backtest/test_result_reporting_metrics.py tests/unit/backtest/test_result_reporting_records.py tests/integration/research/test_backtest_result_reporting_contract.py tests/integration/research/test_backtest_result_reporting_edge_cases.py tests/smoke/local/test_backtest_result_reporting_quickstart.py tests/structure/docs/test_backtest_result_reporting_docs.py -q
```

Expected:

- All reporting-focused tests pass.

**Step 2: Run broader impacted lanes**

```bash
uv run pytest tests/unit/backtest tests/unit/research tests/integration/research tests/smoke/local tests/structure/docs tests/structure/repo -q
```

Expected:

- All impacted lanes pass.

**Step 3: Run runtime-sensitive final gate**

```bash
uv run poe verify-runtime
```

Expected:

- `verify` passes.
- `perf-check` passes.

**Step 4: Record evaluator findings**

Update this document's `Evaluator Review` section with:

- focused tests run
- full verification output
- any deviations from this plan
- any remaining risks

## Implementation Notes And Pitfalls

- Keep metric helpers pure and directly unit-testable. Do not bury formulas in
  runtime loops.
- Avoid adding a second public reporting helper as the primary path. The
  product contract is `result.report`.
- Avoid full-string text snapshots. Assert sections and stable labels only.
- Do not let `BacktestReport` mutate after construction except for plain nested
  user dictionaries if implementation deliberately chooses that DX tradeoff.
- Prefer exact numeric constants in tests for deterministic hand-computable
  fixtures; use tolerance only for floating-point risk formulas.
- Reuse existing deterministic strategy fixtures from
  `tests/integration/research/support_backtest_runner.py` when they fit, but
  keep edge-case fixtures local when that improves readability.
- Do not make no-trade beta report metrics silently zero. Use `None` in the
  report while preserving legacy `BacktestSummary` behavior until a separate
  migration.
- Do not add public `NaN`.
- If any implementation step requires changing `trading` domain models, stop
  and request Tier A approval.

## Evaluator Review

- Findings:
  - No blocking findings remain after the implementation and review-fix pass.
    The code keeps reporting ownership in `quantcraft.backtest`, uses additive
    `BacktestResult.report` compatibility, and does not modify Tier A
    `src/quantcraft/trading` or `src/quantcraft/execution` files.
  - Third-party subagent review initially found metric-contract gaps in
    annualized volatility, Sharpe, first-return handling, timestamp-delta
    annualization, total-loss annualized return, fee-drag denominator, product
    doc sync, public report exports, and stale evaluator evidence. Those
    findings were reviewed and fixed before final verification.
  - The final implementation exposes `BacktestEngine.run(..., label=...)`,
    `Strategy.display_name`, `Strategy.parameters()`, public report dataclasses
    from `quantcraft.backtest`, and `result.report` for engine-produced
    results.
  - Remaining risk is ordinary beta-surface risk: the first report renderer is
    intentionally compact and the metric suite is deterministic rather than
    exhaustive across every future accounting view.
- Fresh verification evidence after implementation:
  - Focused reporting suite passed:
    `uv run pytest tests/unit/backtest/test_result_reporting_metrics.py tests/unit/backtest/test_result_reporting_records.py tests/integration/research/test_backtest_result_reporting_contract.py tests/integration/research/test_backtest_result_reporting_edge_cases.py tests/smoke/local/test_backtest_result_reporting_quickstart.py tests/structure/docs/test_backtest_result_reporting_docs.py -q`
    with output `22 passed`.
  - Broader impacted lanes passed:
    `uv run pytest tests/unit/backtest tests/unit/research tests/integration/research tests/smoke/local tests/structure/docs tests/structure/repo -q`
    with output `323 passed`.
  - `uv build` passed and built `dist/quantcraft-0.1.0.tar.gz` and
    `dist/quantcraft-0.1.0-py3-none-any.whl`.
  - `uv run poe verify-runtime` passed after review fixes:
    - `ruff check .`: `All checks passed!`
    - `mypy src`: `Success: no issues found in 52 source files`
    - `pytest -q`: `502 passed, 3 skipped`
    - coverage gate: `coverage policy check passed`
    - `uv build`: built source distribution and wheel
    - `repo_check.py`: `repository checks passed`
    - notebook validation: all four tracked notebooks validated
    - perf lane: `2 passed`
- Final disposition:
  - Accepted as implemented for the backtest result reporting beta slice.
