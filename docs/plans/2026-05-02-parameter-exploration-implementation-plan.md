# Parameter Exploration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the first-beta `ParameterStudy(...).grid_search(...)` workflow so users can compare a finite parameter grid through the existing single-symbol backtest and report surfaces.

**Architecture:** Keep parameter exploration inside `quantcraft.research` as a study/result UX layer. `ParameterStudy` owns validation, deterministic candidate enumeration, failure capture, result rows, objective selection, and record output; it composes the public `BacktestEngine.run(bars=..., strategy=...)` path and reads engine-produced `BacktestResult.report` metrics. Do not add optimizer behavior to `BacktestEngine`, do not create a second execution model, and do not modify Tier A `trading` or `execution` code.

**Tech Stack:** Python 3.13, stdlib dataclasses, `itertools`, `math`, `types.MappingProxyType`, `typing`, pytest, Ruff, mypy strict mode, uv, Poe task runner. No new runtime dependency.

---

## Repo Workflow Planner Contract

- Date: `2026-05-02`
- Task: `Implement the first-beta parameter exploration workflow`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `User`
- Owner: `Codex`

### Planner Contract

- Goal:
  - Convert the accepted product spec and test scenario spec into a concrete
    how-focused implementation plan.
  - Preserve the existing research/backtest architecture while adding the
    missing beta comparison workflow.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/PLANS.md`
  - `docs/DESIGN.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantcraft-architecture.md`
- Why these are governing:
  - The parameter exploration product spec fixes the beta API, product scope,
    objective model, failure policy, record schema, and non-goals.
  - The parameter exploration test scenario spec fixes the contract-level test
    portfolio that implementation must satisfy.
  - The research/backtest specs define the existing strategy, execution,
    report, and selected-run inspection contracts this feature must reuse.
  - Architecture and package-topology docs keep study UX under `research`, keep
    historical execution under `backtest`, and keep Tier A domains untouched.
- In-repo scope:
  - Add the `quantcraft.research.ParameterStudy` public study container.
  - Add the returned `GridSearchResult` comparison artifact and row selection
    objects under the research package.
  - Add deterministic finite-grid validation, enumeration, constraints,
    default `max_candidates=1000`, continue-by-default failures, and
    `fail_fast=True`.
  - Extract comparison metrics from engine-produced `BacktestResult.report`.
  - Add stable `to_records()` output with metric-state companion fields.
  - Add unit, integration, smoke, and structure tests from the scenario spec.
  - Update routed docs and quickstart-style references only where needed to
    expose the implemented public workflow.
- Out-of-repo scope:
  - No PyPI publishing.
  - No live exchange calls or external services.
  - No network-backed tests.
  - No `/tmp` library changes.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A approval is not required because this implementation must not modify
    `src/quantcraft/trading` or `src/quantcraft/execution`.
  - If execution discovers a required Tier A source change, stop and create a
    human approval record before continuing.
- Verification commands:
  - Focused commands listed under each task.
  - `uv run pytest tests/unit/research/test_parameter_grid_validation.py tests/unit/research/test_parameter_study_preflight.py -q`
  - `uv run pytest tests/unit/research/test_grid_search_result_selection.py tests/unit/research/test_grid_search_records.py -q`
  - `uv run pytest tests/integration/research/test_parameter_study_grid_search.py tests/integration/research/test_parameter_study_failures.py tests/integration/research/test_parameter_study_selected_run.py -q`
  - `uv run pytest tests/smoke/local/test_public_imports.py -q`
  - `uv run pytest tests/structure/architecture tests/structure/docs tests/structure/repo -q`
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run python scripts/coverage_check.py`
  - `uv run python scripts/repo_check.py`
  - `uv build`
  - `uv run poe verify-runtime`
- Success criteria:
  - `from quantcraft.research import ParameterStudy` works.
  - `ParameterStudy(engine=..., bars=..., strategy_factory=...).grid_search(...)`
    runs finite grids through the existing `BacktestEngine.run(bars=...)`
    path.
  - The feature produces one inspectable row per raw candidate outcome.
  - Successful, rejected, and failed rows are distinguishable and counted.
  - Failed rows continue by default and include `failure_stage`, `error_type`,
    and `error_message`.
  - `fail_fast=True` re-raises the original exception type for user-code
    failures and exposes the failing stage/parameters through standard Python
    diagnostics.
  - Selection is single-objective, deterministic, and tied to explicit
    `(metric_path, direction)` tuples.
  - Every successful row retains its engine-produced `BacktestResult`.
  - `to_records()` emits the exact stable schema from the product spec,
    including metric-state companion fields and no `NaN`/`Infinity` tokens.
  - No public `source=`, `n_jobs`, `workers`, `parallel`, `executor`, heatmap,
    persistence, custom objective callable, or multi-objective API is added.
  - Runtime-sensitive verification passes or any unavailable command is
    explicitly recorded with cause.
- Out of scope:
  - New order semantics.
  - Changes under `src/quantcraft/trading` or `src/quantcraft/execution`.
  - Parallel execution controls.
  - Persistence, resume, retry queues, or result caching.
  - Random/Bayesian/SAMBO/genetic search.
  - Walk-forward analysis or train/test splitting.
  - Heatmaps, dashboards, first-party visual tables, or pandas-only output.
  - Creating commits unless the user explicitly asks.

### Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close this planning slice only after the plan is grounded in the current
    source/test tree, names exact files, preserves architecture boundaries, and
    records fresh document/repo verification evidence.
- Acceptance artifact location:
  - `docs/plans/2026-05-02-parameter-exploration-implementation-plan.md`
- How the generator and evaluator agreed on done before execution:
  - This document is done when it explains the implementation architecture,
    reusable code paths, exact file responsibilities, TDD sequence, risks, and
    verification commands without reopening closed product decisions.
- Checks the evaluator will use:
  - Manual review against `docs/product-specs/parameter-exploration.md`.
  - Manual review against
    `docs/product-specs/parameter-exploration-test-scenarios.md`.
  - Manual review against the current `src/quantcraft` and `tests` layout.
  - `uv run poe repo-check`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q`.
- Auto-fail conditions:
  - Prescribing `BacktestEngine.optimize(...)` or optimizer ownership under
    `backtest`.
  - Prescribing a second execution model or report parser.
  - Prescribing Tier A source changes without approval.
  - Adding public deferred controls such as `source=`, `n_jobs`, `parallel`,
    custom objective callables, multi-objective ranking, persistence, or
    heatmaps.
  - Omitting default continue-on-failure rows or selected-run `BacktestResult`
    retention.
  - Making record output depend on pandas.

### Generator Work Log

- Planned slice order:
  1. Read governing docs and accepted parameter exploration specs.
  2. Survey source packages, test taxonomy, public import surfaces, and
     existing backtest/reporting contracts.
  3. Map reusable code paths, implementation ownership, and test fixtures.
  4. Write this how-focused implementation plan.
  5. Run repository/document verification.
  6. Record evaluator findings and final disposition.
- Notes:
  - This plan intentionally modifies no runtime source code.
  - Implementation should be executed with TDD: write a focused failing test,
    run it, implement only the code needed for that behavior, rerun the
    focused test, then broaden verification.
  - Existing uncommitted spec documents are part of the current planning work
    and should not be reverted.
- Blockers or scope changes:
  - None at plan-writing time.

## Codebase Survey Summary

### Technology And Infrastructure

- Python 3.13 package under `src/quantcraft`.
- `uv` manages dependencies and lockfile.
- Poe owns repository command surface through `pyproject.toml`.
- pytest uses `--import-mode=importlib`.
- Ruff, mypy strict mode, coverage, build, repo-check, notebook validation, and
  explicit perf/live lanes are wired through Poe.
- Runtime dependencies currently include `ccxt`, `matplotlib`, and `ta-lib`.
  Parameter exploration needs no new dependency.
- No web app or external product surface is involved.

### Package Structure

Current capability roots under `src/quantcraft`:

- `data`: `BarSeries`, `TimeBar`, and historical source contracts.
- `research`: public `Strategy`, `ta`, `qc`, indicator runtime, and series
  ergonomics.
- `backtest`: `BacktestEngine`, runtime, execution model, reporting,
  `BacktestResult`, and plotting.
- `trading`: shared trading kernel; Tier A.
- `execution`: future execution context; Tier A.
- `integrations`: venue/data integrations.

The implementation belongs under `src/quantcraft/research`. `research` is
allowed to depend on the public `backtest` surface, `data`, and `trading`.
`backtest` must not import `research` to host optimizer behavior.

### Existing Public Surfaces

- `quantcraft.research.__init__` lazily exports `Strategy`, `qc`, and `ta`.
  It should be extended to lazily export `ParameterStudy` and the returned
  public result/row types without importing backtest at module import time.
- `quantcraft.backtest.__init__` exports `BacktestEngine`, `BacktestResult`,
  `BacktestReport`, and report dataclasses. Do not add parameter exploration
  exports here.
- `quantcraft.data.__init__` exports `BarSeries`, `TimeBar`, and data sources.
  `ParameterStudy` should require a materialized `BarSeries`.
- The root `quantcraft.__init__` intentionally exports nothing. Do not promote
  `ParameterStudy` to the root package.

### Existing Backtest Flow

The canonical path to reuse is:

```text
ParameterStudy.grid_search(...)
  -> strategy_factory(parameters)
  -> BacktestEngine.run(bars=bars, strategy=strategy, label=stable_label)
  -> _run_backtest(...)
  -> BacktestResult(report=BacktestReport, plot() path intact)
```

Important existing files:

- `src/quantcraft/backtest/engine.py`
  - `BacktestEngine.run(...)` validates exactly one of `bars` or `source`.
  - The study must call `engine.run(bars=..., strategy=..., label=...)`.
- `src/quantcraft/backtest/runtime.py`
  - Owns historical execution and report construction.
  - It already creates a fresh `_StrategyDriver`, `TradingState`, orders, and
    report builder per `run(...)` call.
- `src/quantcraft/backtest/strategy_runtime.py`
  - `_StrategyDriver.initialize(...)` resets public strategy runtime state, but
    arbitrary user attributes may not reset. The study must call the strategy
    factory once per admissible combination instead of reusing one strategy.
- `src/quantcraft/backtest/reporting.py`
  - Owns typed `BacktestReport` groups: `run`, `execution`, `returns`, `risk`,
    `trades`, `costs`, `exposure`.
  - Parameter exploration must read these typed fields, not parse
    `BacktestReport.to_text()`.
- `src/quantcraft/backtest/results.py`
  - `BacktestResult.report` is available only for engine-produced results.
  - `BacktestResult.plot()` is the selected-run visual inspection path.

### Existing Report Metric Mapping

Use report fields as the canonical source for beta metric paths:

| Metric path | Report source |
| --- | --- |
| `equity.final` | `result.report.returns.final_equity` |
| `returns.total_return` | `result.report.returns.total_return` |
| `risk.max_drawdown` | `result.report.risk.max_drawdown` |
| `risk.sharpe_ratio` | `result.report.risk.sharpe_ratio` |
| `trades.closed_count` | `result.report.trades.closed_trade_count` |
| `trades.win_rate` | `result.report.trades.win_rate` |
| `trades.profit_factor` | `result.report.trades.profit_factor` |
| `costs.total_fees` | `result.report.costs.total_fees` |
| `exposure.ratio` | `result.report.exposure.exposure_ratio` |
| `execution.order_rejection_count` | `result.report.execution.order_rejection_count` |

Use the report manifest/execution groups for non-metric record keys:

| Record key | Report source |
| --- | --- |
| `run.label` | `result.report.run.run_label` |
| `strategy.class_name` | `result.report.run.strategy_class_name` |
| `strategy.display_name` | `result.report.run.strategy_display_name` |
| `run.symbol` | `result.report.run.symbol` |
| `run.timeframe` | `result.report.run.timeframe` |
| `run.initial_cash` | `result.report.run.initial_cash` |
| `execution.model_name` | `result.report.execution.execution_model_name` |

### Existing Test Structure

Current tests are organized by type:

- `tests/unit/...`
- `tests/integration/...`
- `tests/smoke/local/...`
- `tests/structure/...`
- `tests/perf/...`

Relevant reusable test helpers:

- `tests/integration/research/support_backtest_runner.py`
  - Small deterministic `BarSeries` fixtures and real strategy classes for
    integration tests.
  - `run_engine_backtest(...)` and `fixture_bar_series(...)` show compact real
    engine usage.
- `tests/support_backtest.py`
  - Larger canonical BTC fixture and strategy/report helpers. Use only where
    broad real-data regression value justifies runtime cost.
- `tests/unit/backtest/test_engine.py`
  - Public validation style for standard exceptions and clear diagnostics.
- `tests/integration/research/test_backtest_result_reporting_contract.py`
  - Contract style for report metadata, display name, parameters, and report
    grouping.
- `tests/smoke/local/test_public_imports.py`
  - Public import smoke expectations; update current "research surface is
    strategy only" assertion.
- `tests/structure/architecture/test_domain_boundaries.py`
  - Existing architecture scanner verifies `research -> backtest` is allowed
    and `backtest -> research` is not.

### Areas Affected

- `src/quantcraft/research/__init__.py`
- New `src/quantcraft/research/parameter_exploration.py`
- Unit tests under `tests/unit/research/`
- Integration tests under `tests/integration/research/`
- Smoke imports under `tests/smoke/local/test_public_imports.py`
- Structure/docs tests under `tests/structure/...` if mechanical guardrails are
  needed for deferred controls and package boundaries.
- Product/reference docs for the implemented canonical example if execution
  includes doc updates.

### Existing Paths Not To Bypass

- Do not call `_run_backtest(...)` directly from `research`; call
  `BacktestEngine.run(...)`.
- Do not parse `BacktestReport.to_text()`.
- Do not duplicate report metric formulas in `research`; read typed report
  fields.
- Do not add parameter exploration to `quantcraft.backtest`.
- Do not add helper modules under old removed `research/domain`,
  `research/application`, or `research/adapters` paths.
- Do not use pandas as the required result output.

## Implementation Architecture

### New Module

Create `src/quantcraft/research/parameter_exploration.py`.

Keep the beta in one cohesive module first. Split only if the file becomes
materially difficult to navigate after implementation. A single module is
appropriate because beta has one public study class, one result artifact, and
small internal helpers.

Expected public classes:

- `ParameterStudy`
- `GridSearchResult`
- `GridSearchRow`

`GridSearchResult` and `GridSearchRow` are public because users receive and
inspect them. They should be exported from `quantcraft.research` alongside
`ParameterStudy`, but not from `quantcraft.backtest` or the root package.

### Type Model

Use frozen dataclasses for row/result values where practical:

- `GridSearchRow`
  - `run_index: int`
  - `status: Literal["success", "rejected", "failed"]`
  - `parameters: Mapping[str, JSONScalar]`
  - `backtest: BacktestResult | None`
  - `metrics: Mapping[str, float | None]`
  - `metric_states: Mapping[str, MetricState]`
  - `failure_stage: FailureStage | None`
  - `error_type: str | None`
  - `error_message: str | None`
- `GridSearchResult`
  - private tuple of `GridSearchRow`
  - optional default objective
  - counts as properties
  - `to_records()`
  - `best(objective: Objective | None = None)`
  - `top(n: int, objective: Objective | None = None)`
  - `failed()`
  - `rejected()`
  - `successful()`
- `ParameterStudy`
  - frozen or slots dataclass-like object containing `engine`, `bars`, and
    `strategy_factory`
  - `grid_search(...)`

Use type aliases:

```python
JSONScalar = str | int | float | bool | None
Objective = tuple[str, Literal["max", "min"]]
MetricState = Literal["defined", "undefined", "positive_infinity", "negative_infinity"]
FailureStage = Literal["constraint", "strategy_factory", "backtest", "metric_extraction"]
RowStatus = Literal["success", "rejected", "failed"]
```

Keep helper functions private unless a test can only reasonably validate a
public behavior through that helper. Unit tests should primarily exercise
public `ParameterStudy.grid_search(...)`, `GridSearchResult`, and
`GridSearchRow` behavior.

### Parameter Mapping Contract

Candidate mappings passed to `constraint` and `strategy_factory` must not let
callback code corrupt row identity or later callback inputs.

Implementation choice:

- Build each raw candidate as a plain `dict[str, JSONScalar]`.
- Store an immutable `MappingProxyType(dict(candidate))` or fresh copied dict
  inside the row.
- Pass a read-only mapping to callbacks.

This prevents accidental mutation and makes deliberate mutation attempts fail
with standard Python behavior. If `MappingProxyType` creates awkward typing,
keep public storage as a copied plain dict and pass `MappingProxyType` only to
callbacks.

### Grid Validation And Enumeration

Implement private helpers:

- `_validate_parameter_grid(parameters: object) -> dict[str, tuple[JSONScalar, ...]]`
- `_candidate_count(grid: Mapping[str, tuple[JSONScalar, ...]]) -> int`
- `_iter_candidates(grid: Mapping[str, tuple[JSONScalar, ...]]) -> Iterator[tuple[int, dict[str, JSONScalar]]]`
- `_validate_max_candidates(value: int | None) -> int | None`

Validation rules:

- `parameters` must be a mapping with at least one item.
- Keys must be non-empty strings.
- Values must be ordered finite sequences, not strings/bytes and not unordered
  containers such as `set`.
- Candidate values must be JSON scalars only.
- `bool` is accepted as a scalar value but must not be treated as an `int` for
  `max_candidates`.
- `float` values must be finite.
- Duplicate values within one parameter are invalid.
- Duplicate full combinations are invalid. This mostly falls out of duplicate
  value rejection, but keep a defensive check if future accepted values make it
  possible.
- Candidate order follows mapping insertion order and sequence order.
- `run_index` is zero-based raw cartesian order before constraints.

Use `itertools.product` after validation has normalized values to tuples.

### Objective And Metric Extraction

Define one beta metric registry inside `parameter_exploration.py`:

```python
_METRIC_EXTRACTORS: dict[str, Callable[[BacktestResult], float | int | None]]
```

Each extractor should read `result.report` and return one scalar. Unknown paths
must fail before any backtest runs. The registry is the single source for:

- objective validation
- metric extraction
- record metric key ordering
- metric-state output

Do not make metric paths dynamic through `getattr` traversal in beta. The fixed
registry is clearer, avoids non-scalar paths, and exactly matches the accepted
product contract.

Metric normalization:

- finite `int`/`float`: internal value stays numeric, record value is numeric,
  state `"defined"`
- `None`: internal value `None`, record value `None`, state `"undefined"`
- `math.nan`: internal value `None`, record value `None`, state `"undefined"`
- `math.inf`: internal value `math.inf`, record value `None`, state
  `"positive_infinity"`
- `-math.inf`: internal value `-math.inf`, record value `None`, state
  `"negative_infinity"`

Selection uses the internal metric values, not the portable record values.

### Failure Handling

Default `fail_fast=False` behavior records failed rows for:

- constraint exceptions
- non-bool constraint returns
- strategy factory exceptions
- `BacktestEngine.run(...)` exceptions, including strategy `init()` and
  `on_bar()` exceptions
- unexpected metric extraction exceptions for known metric paths

Failed rows must include:

- `parameters`
- `failure_stage`
- `error_type`
- `error_message`

Default records must not include tracebacks, cause chains, or local traceback
paths.

`fail_fast=True` behavior:

- For constraint, strategy factory, backtest, and metric extraction failures,
  re-raise the original exception object when one exists.
- For invalid non-bool constraint returns, raise `TypeError`.
- Add parameter and stage context with `BaseException.add_note(...)` when
  available:
  - `stage=<failure_stage>`
  - `parameters=<candidate_mapping_repr>`
- Do not wrap failures in a custom Quantcraft exception.

Whole-search input validation errors, such as invalid grids, invalid
objectives, invalid `max_candidates`, or invalid construction arguments, should
raise before any row execution and should not become failed rows.

### Run Labels

Use stable labels for successful engine runs so records can trace rows back to
parameters:

```text
grid-search-<run_index>
```

This keeps labels short and deterministic. The full parameter mapping is still
stored in the row and in `Strategy.parameters()` when user strategies implement
that hook.

### Selection Helpers

`GridSearchResult.best(...)`:

- resolves the explicit argument objective or default objective
- raises if no objective is available
- raises if there are no eligible rows
- returns the first row from `top(1, objective=...)`

`GridSearchResult.top(n, ...)`:

- rejects `n <= 0` with `ValueError`
- resolves the objective
- filters to successful rows with defined or meaningful non-finite objective
  values
- sorts by metric value according to `"max"` or `"min"`
- preserves original `run_index` for ties
- returns an empty tuple when no rows are eligible
- returns all eligible rows when `n` exceeds eligible count

`eligible_count` on the result uses the default objective when present. If no
default objective is present, it returns `0`.

### Record Output

`GridSearchResult.to_records()` returns `list[dict[str, object]]` with one row
per raw candidate outcome.

Record shape must include:

- `run_index`
- `status`
- `parameters`
- `run.label`
- `strategy.class_name`
- `strategy.display_name`
- `run.symbol`
- `run.timeframe`
- `run.initial_cash`
- `execution.model_name`
- `failure_stage`
- `error_type`
- `error_message`
- every metric key from the beta metric registry
- every companion `<metric_key>_state`

Rejected and failed rows use `None` for metric values and `"undefined"` for
metric states. Rejected rows use `None` for `failure_stage`, `error_type`, and
`error_message`.

Return plain Python containers only. Do not require pandas.

## Data Flow And Control Flow

### Normal Successful Candidate

```text
grid_search(parameters, constraint, objective)
  -> validate study construction and grid
  -> validate objective and max_candidates
  -> count raw cartesian candidates
  -> enumerate candidate #N
  -> pass immutable/copy mapping to constraint
  -> constraint returns True
  -> pass immutable/copy mapping to strategy_factory
  -> strategy_factory returns StrategyLike
  -> engine.run(bars=materialized_bars, strategy=strategy, label="grid-search-N")
  -> extract all beta metrics from result.report
  -> create success GridSearchRow with retained BacktestResult
  -> create GridSearchResult(rows=..., objective=...)
```

### Constraint Rejection

```text
candidate #N
  -> constraint returns False
  -> create rejected GridSearchRow
  -> do not call strategy_factory
  -> do not call engine.run(...)
```

### Default Failure Row

```text
candidate #N
  -> stage raises or produces invalid outcome
  -> capture exception class name and message
  -> create failed GridSearchRow with stage
  -> continue to candidate #N+1
```

### Fail Fast

```text
candidate #N
  -> stage raises or produces invalid outcome
  -> add stage/parameter context to the standard exception
  -> raise immediately
  -> no GridSearchResult returned
```

## File-Level Plan

### Production Files

- Create: `src/quantcraft/research/parameter_exploration.py`
  - Own `ParameterStudy`, `GridSearchResult`, `GridSearchRow`, type aliases,
    metric registry, grid validation, row construction, objective validation,
    selection, and record output.
- Modify: `src/quantcraft/research/__init__.py`
  - Add lazy exports for `ParameterStudy`, `GridSearchResult`, and
    `GridSearchRow`.
  - Preserve lazy `Strategy`, `qc`, and `ta` behavior.

No production changes should be made in:

- `src/quantcraft/backtest/engine.py`
- `src/quantcraft/backtest/runtime.py`
- `src/quantcraft/backtest/reporting.py`
- `src/quantcraft/trading/**`
- `src/quantcraft/execution/**`

If implementation reveals a necessary change in those files, pause and update
the plan before editing.

### Test Files

- Create: `tests/unit/research/test_parameter_grid_validation.py`
  - Grid values, parameter names, duplicate values, unordered containers,
    deterministic enumeration, callback mutation protection.
- Create: `tests/unit/research/test_parameter_study_preflight.py`
  - Study constructor validation, materialized bars only, `max_candidates`,
    invalid objective, no-run preflight failures, public signature checks.
- Create: `tests/unit/research/test_grid_search_result_selection.py`
  - `best()`, `top(n)`, objectives, no eligible rows, ties, infinity,
    undefined objective values.
- Create: `tests/unit/research/test_grid_search_records.py`
  - Stable `to_records()` schema, metric states, failed/rejected nullability,
    no non-standard JSON floats.
- Create: `tests/integration/research/test_parameter_study_grid_search.py`
  - Canonical small real `BacktestEngine` grid with constraint and selected row.
- Create: `tests/integration/research/test_parameter_study_failures.py`
  - Constraint, strategy factory, backtest, metric extraction failures,
    continue-by-default and fail-fast.
- Create: `tests/integration/research/test_parameter_study_selected_run.py`
  - Selected run `BacktestResult.report` and `BacktestResult.plot()` access path.
- Modify: `tests/smoke/local/test_public_imports.py`
  - Replace the current "research public import surface is strategy only"
    expectation with the new beta surface: `Strategy`, `ta`, `qc`, and
    `ParameterStudy`; keep `BacktestEngine` absent from `research`.
- Create or modify: `tests/structure/architecture/test_parameter_exploration_boundaries.py`
  - Check that parameter exploration lives under `research`, `backtest` does
    not import it, no heavy optimizer dependency is added, and public signatures
    omit deferred controls.
- Create or modify: `tests/structure/docs/test_parameter_exploration_docs.py`
  - Check docs route to the implemented public path and do not promote
    deferred controls as beta behavior.

### Documentation Files

- Modify if implementation includes docs in the same slice:
  - `README.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/references/research-ergonomics-quickstart.md`
  - `notebooks/research-ergonomics-quickstart.ipynb`

The implementation can defer full canonical example/notebook execution to P1
docs-release work, but P0 docs must not contradict the shipped API once the
feature lands.

## Test Implementation Plan

### Task 1: Public Import And Constructor Contract

**Files:**

- Modify: `tests/smoke/local/test_public_imports.py`
- Create: `tests/unit/research/test_parameter_study_preflight.py`
- Create: `src/quantcraft/research/parameter_exploration.py`
- Modify: `src/quantcraft/research/__init__.py`

**Steps:**

1. Write failing tests for `from quantcraft.research import ParameterStudy`.
2. Write failing tests for constructing with `engine`, `bars`, and
   `strategy_factory`.
3. Write failing tests that `source=` is not accepted and deferred controls are
   absent from the `grid_search` signature.
4. Run:
   - `uv run pytest tests/smoke/local/test_public_imports.py tests/unit/research/test_parameter_study_preflight.py -q`
5. Add minimal classes and lazy exports.
6. Rerun the focused command.

Expected initial failure: import/signature errors.

### Task 2: Grid Validation And Candidate Counting

**Files:**

- Modify: `src/quantcraft/research/parameter_exploration.py`
- Create: `tests/unit/research/test_parameter_grid_validation.py`
- Extend: `tests/unit/research/test_parameter_study_preflight.py`

**Steps:**

1. Write failing tests for valid one- and two-parameter grids.
2. Add invalid cases from U1, including non-string names, empty names, empty
   values, unordered values, duplicate values, unsupported scalar types, and
   non-finite floats.
3. Add raw cartesian limit tests from U2.
4. Implement validation, candidate counting, and deterministic enumeration.
5. Run:
   - `uv run pytest tests/unit/research/test_parameter_grid_validation.py tests/unit/research/test_parameter_study_preflight.py -q`

Expected completion: invalid grids fail before any strategy factory or engine
call.

### Task 3: Constraint Rows And Callback Isolation

**Files:**

- Modify: `src/quantcraft/research/parameter_exploration.py`
- Extend: `tests/unit/research/test_parameter_grid_validation.py`
- Extend: `tests/integration/research/test_parameter_study_grid_search.py`

**Steps:**

1. Write failing tests for accepted, rejected, all-rejected, raising
   constraint, and non-bool constraint outcomes.
2. Add a mutation-attempt test proving callback code cannot corrupt stored row
   identity or later callback inputs.
3. Implement constraint evaluation, rejected rows, failed rows, and fail-fast
   behavior for constraint stage.
4. Run:
   - `uv run pytest tests/unit/research/test_parameter_grid_validation.py tests/integration/research/test_parameter_study_grid_search.py -q`

Expected completion: rejected rows do not call the strategy factory and do not
receive failure diagnostics.

### Task 4: Real Backtest Execution Through Existing Engine

**Files:**

- Modify: `src/quantcraft/research/parameter_exploration.py`
- Create: `tests/integration/research/test_parameter_study_grid_search.py`
- Create or extend: `tests/integration/research/test_parameter_study_failures.py`

**Steps:**

1. Build small deterministic `BarSeries` fixtures in the integration test file
   or reuse compact helpers from `tests/integration/research/support_backtest_runner.py`.
2. Write a small parameterized SMA-style `Strategy`.
3. Assert strategy factory is called once per admissible combination.
4. Assert reused `BacktestEngine` state does not leak across runs.
5. Implement strategy factory invocation and `engine.run(bars=..., strategy=...)`
   calls.
6. Run:
   - `uv run pytest tests/integration/research/test_parameter_study_grid_search.py -q`

Expected completion: successful rows retain real engine-produced
`BacktestResult` values.

### Task 5: Metric Registry And Records

**Files:**

- Modify: `src/quantcraft/research/parameter_exploration.py`
- Create: `tests/unit/research/test_grid_search_records.py`
- Extend: `tests/integration/research/test_parameter_study_grid_search.py`

**Steps:**

1. Write failing tests for the exact non-metric record keys and all beta metric
   keys with `_state` companion fields.
2. Write tests for finite, undefined, `NaN`, `math.inf`, and `-math.inf`
   metric states.
3. Implement `_METRIC_EXTRACTORS`, metric normalization, and `to_records()`.
4. Run:
   - `uv run pytest tests/unit/research/test_grid_search_records.py tests/integration/research/test_parameter_study_grid_search.py -q`

Expected completion: records are portable plain Python dictionaries and emit no
`NaN`/`Infinity` numeric tokens.

### Task 6: Objective Validation And Selection Helpers

**Files:**

- Modify: `src/quantcraft/research/parameter_exploration.py`
- Create: `tests/unit/research/test_grid_search_result_selection.py`
- Extend: `tests/unit/research/test_parameter_study_preflight.py`

**Steps:**

1. Write failing tests for every accepted beta objective path and invalid
   objective shapes.
2. Assert unknown objectives fail before strategy factory or engine calls.
3. Write `best()` and `top(n)` tests for `"max"`, `"min"`, ties, undefined
   values, infinity, no eligible rows, and `n <= 0`.
4. Implement objective validation and selection helpers.
5. Run:
   - `uv run pytest tests/unit/research/test_grid_search_result_selection.py tests/unit/research/test_parameter_study_preflight.py -q`

Expected completion: selection is deterministic and never ranks failed,
rejected, or undefined-objective rows.

### Task 7: Failure Diagnostics And Fail Fast

**Files:**

- Modify: `src/quantcraft/research/parameter_exploration.py`
- Create: `tests/integration/research/test_parameter_study_failures.py`
- Extend: `tests/unit/research/test_grid_search_records.py`

**Steps:**

1. Write failing tests for strategy-factory, strategy `init()`, strategy
   `on_bar()`, and metric-extraction failures.
2. Assert default mode records failed rows and continues to later combinations.
3. Assert `fail_fast=True` re-raises the original exception type and includes
   stage/parameter context via exception notes or equivalent standard
   diagnostic.
4. Assert records do not contain traceback/cause/local path fields.
5. Implement failure capture and fail-fast re-raise helpers.
6. Run:
   - `uv run pytest tests/integration/research/test_parameter_study_failures.py tests/unit/research/test_grid_search_records.py -q`

Expected completion: all failed-row stages are visible and debuggable without
custom public exceptions.

### Task 8: Selected-Run Inspection

**Files:**

- Create: `tests/integration/research/test_parameter_study_selected_run.py`
- Modify: `src/quantcraft/research/parameter_exploration.py` only if needed

**Steps:**

1. Write failing tests that `results.best().backtest.report` is the normal
   engine-produced report path.
2. Write a narrow test that `results.best().backtest.plot()` is reachable when
   plotting dependencies are installed.
3. Assert rejected and failed rows have `backtest is None`.
4. Run:
   - `uv run pytest tests/integration/research/test_parameter_study_selected_run.py -q`

Expected completion: selected rows need no rerun for report or plot
inspection.

### Task 9: Architecture, Docs, And Boundary Checks

**Files:**

- Create or modify: `tests/structure/architecture/test_parameter_exploration_boundaries.py`
- Create or modify: `tests/structure/docs/test_parameter_exploration_docs.py`
- Modify docs only if implementation docs are included in this slice.

**Steps:**

1. Add structure checks for package ownership and deferred-control absence when
   those checks are objective and cheap.
2. Update import-smoke checks.
3. Update docs to avoid stale "research surface is strategy only" language and
   to show the implemented `ParameterStudy` path if docs are part of the
   implementation slice.
4. Run:
   - `uv run pytest tests/smoke/local tests/structure/architecture tests/structure/docs tests/structure/repo -q`

Expected completion: repo structure protects the public surface without
overfitting to private helpers.

### Task 10: Final Verification

**Files:**

- All changed production, tests, docs, and notebook files from prior tasks.

**Steps:**

1. Run focused research/backtest tests:
   - `uv run pytest tests/unit/research tests/integration/research -q`
2. Run structure/smoke:
   - `uv run pytest tests/smoke/local tests/structure -q`
3. Run static and packaging checks:
   - `uv run ruff check .`
   - `uv run mypy src`
   - `uv run python scripts/coverage_check.py`
   - `uv build`
   - `uv run python scripts/repo_check.py`
4. Run runtime-sensitive lane:
   - `uv run poe verify-runtime`
5. Record verification evidence in this plan's evaluator review before
   claiming implementation complete.

Expected completion: default and runtime verification pass from the current
workspace state.

## Migration And Compatibility

- This is additive to the public research surface.
- Existing `Strategy`, `ta`, `qc`, `BacktestEngine`, `BacktestResult.report`,
  and `BacktestResult.plot()` behavior must remain compatible.
- Existing root package exports must remain empty.
- Existing `quantcraft.backtest` exports must not gain optimizer/study names.
- No data migrations, persistent files, or schema changes are involved.
- No new runtime dependency is needed.
- Manually constructed `BacktestResult` values remain valid; parameter
  exploration only stores engine-produced results for successful rows.

## Risks And Responses

- Risk: Tests accidentally mirror private helpers instead of public behavior.
  - Response: Keep unit tests public-surface oriented and use private helpers
    only as implementation details.
- Risk: Metric extraction duplicates report formulas.
  - Response: Use a fixed registry that reads existing typed `BacktestReport`
    fields only.
- Risk: User callback mutation corrupts stored row identity.
  - Response: Pass immutable mappings or defensive copies and store copied
    parameter maps.
- Risk: Fail-fast wraps user exceptions and loses useful traceback.
  - Response: Re-raise original exceptions and add context with
    `BaseException.add_note(...)`.
- Risk: Large grid retention surprises users.
  - Response: Preserve default `max_candidates=1000`, require explicit
    override, and document that successful `BacktestResult` values are kept in
    memory.
- Risk: `research` starts owning execution semantics.
  - Response: Call only public `BacktestEngine.run(...)`; do not import or call
    backtest runtime internals.
- Risk: Structure checks become too brittle.
  - Response: Check public boundaries and deferred-control absence, not private
    class or helper names.

## Open Questions

- None for the implementation plan stage. Internal helper names can be adjusted
  during implementation if tests continue to validate the product/test-spec
  contracts and the architecture boundary remains intact.

## Evaluator Review

### Planning Slice Review

- Findings:
  - No blocking findings. The implementation plan is grounded in the current
    `research`, `backtest`, `data`, and test layout; it preserves
    `ParameterStudy` ownership under `research`; it composes the public
    `BacktestEngine.run(bars=...)` and `BacktestResult.report` paths; and it
    keeps deferred optimizer, source-backed study input, parallelism,
    persistence, visualization, and Tier A execution semantics out of scope.
- Verification evidence:
  - `uv run poe repo-check` passed with `repository checks passed`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q` passed with
    `67 passed in 0.19s`.
- Final disposition:
  - Complete for the technical implementation planning slice. Runtime source
    implementation has not started.

### Implementation Slice Review

- Generator changes:
  - Added `src/quantcraft/research/parameter_exploration.py` with
    `ParameterStudy`, `GridSearchResult`, and `GridSearchRow`.
  - Extended `quantcraft.research` lazy exports for the new public study/result
    surface.
  - Added unit tests for grid validation, preflight validation, objective
    selection, record output, metric states, and failure diagnostics.
  - Added integration tests proving real `BacktestEngine.run(bars=...)`
    composition, fresh strategy factory use, continue-by-default failures,
    fail-fast re-raise behavior, selected-run report/plot inspection, and
    no-trade undefined metric handling.
  - Added smoke, structure, built-artifact, and docs guardrails for public
    imports, capability boundaries, deferred-control absence, and docs routing.
  - Updated public docs to include the implemented `ParameterStudy` research
    surface without promoting broad optimizer semantics.
- Subagent review summary:
  - Implementation/API reviewer found important issues with non-`BarSeries`
    exception type, missing fail-fast coverage for backtest and non-bool
    constraint outcomes, and a non-contract-shaped metric extraction fake.
  - Correctness reviewer found the same non-`BarSeries` exception mismatch and
    a minor explicit-falsy objective fallback issue in `top(...)`.
  - Architecture/scope reviewer found no blocker, important, or minor issues;
    it confirmed no Tier A changes, no private runtime bypass, no deferred
    controls, no heavy optimizer dependency, and no broad optimizer docs claim.
- Review issue resolutions:
  - Changed non-`BarSeries` `ParameterStudy` construction failures from
    `ValueError` to `TypeError` and updated the preflight test.
  - Added fail-fast tests for backtest failures and non-bool constraint
    outcomes.
  - Replaced the bare-object metric extraction fake with a minimal
    report-shaped object whose known metric accessor raises.
  - Fixed explicit invalid falsy objectives so they do not fall back to the
    default objective.
  - Added coverage for enum parameter rejection, negative infinity selection,
    and no-trade undefined metric states.
- Verification evidence after review fixes:
  - `uv run pytest tests/unit/research/test_parameter_study_preflight.py tests/unit/research/test_grid_search_result_selection.py tests/integration/research/test_parameter_study_failures.py tests/integration/research/test_parameter_study_metric_states.py -q`
    passed with `33 passed in 0.07s`.
  - `uv run poe verify-runtime` passed:
    - `ruff check .` -> `All checks passed!`
    - `mypy src` -> `Success: no issues found in 55 source files`
    - `pytest -q` -> `609 passed, 4 skipped in 6.48s`
    - `coverage_check.py` -> `coverage policy check passed`
    - `uv build` -> built source distribution and wheel
    - `repo_check.py` -> `repository checks passed`
    - `notebook_validate.py` -> validated five notebooks
    - `pytest tests/perf -q -x --run-perf` -> `3 passed in 1.80s`
- Final disposition:
  - Complete for the implementation slice. The implemented feature satisfies
    the product spec, test scenario spec, and implementation plan success
    criteria without Tier A scope expansion.
