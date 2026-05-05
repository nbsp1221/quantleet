# Canonical Report Snapshot Test Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Strengthen the canonical real-data backtest tests so they pin the public `result.report` contract in addition to existing summary and trade-log regression outputs.

**Architecture:** Keep test ownership in the existing canonical integration suite and shared `tests/support_backtest.py` helpers. Assert user-visible report contracts with readable scalar expectations, compact row samples, and deterministic digests for long sequences; avoid testing private implementation helpers or broad unreadable snapshots.

**Tech Stack:** Python 3.13, pytest, stdlib dataclasses/introspection, hashlib/json normalization, existing canonical BTCUSDT CSV fixture, uv, Poe verification tasks. No new runtime or test dependency.

---

## Repo Workflow Planner Contract

- Date: `2026-05-01`
- Task: `Plan canonical result.report snapshot test hardening`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `User`
- Owner: `Codex`

### Planner Contract

- Goal:
  - Convert the accepted testing principles and the `/tmp` cross-check evidence
    into a concrete test implementation plan.
  - Make the existing real-data canonical backtest tests stronger without
    turning them into brittle, unreadable blob snapshots.
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
  - `docs/plans/2026-04-30-backtest-result-reporting-spec.md`
  - `docs/plans/2026-05-01-backtest-result-reporting-test-scenarios.md`
  - `docs/plans/2026-05-01-backtest-result-reporting-implementation-plan.md`
- Why these are governing:
  - The product specs define the first-beta single-symbol backtesting target
    and current user-facing result interpretation scope.
  - The reporting spec and implementation plan define the `result.report`
    public contract and metric semantics.
  - The test-scenario spec defines contract-first test quality, layer
    separation, and edge-case coverage expectations.
  - `docs/references/testing.md` defines test taxonomy, placement, naming, and
    fixture rules.
- In-repo scope:
  - Modify `tests/support_backtest.py` with maintainable report snapshot
    assertion helpers.
  - Extend the canonical RSI, EMA cross, and MACD integration tests with full
    `result.report` snapshot assertions.
  - Preserve the existing canonical `summary`, first/last fill samples, and
    full `trade_log` digest assertions.
  - Keep existing focused unit tests for formula edge cases and record
    semantics.
  - Add only small helper tests if needed to protect the snapshot helper itself.
- Out-of-repo scope:
  - Do not make `/tmp/quantleet-backtest-crosscheck` a test dependency.
  - Do not add external metrics libraries to the repository.
  - Do not require network access, live services, or package downloads in the
    repo test lane.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A approval is not required. The planned changes are tests and test
    helpers under `tests/`; they must not modify `src/quantleet/trading` or
    `src/quantleet/execution`.
- External evidence record:
  - requestor: User
  - human approver: User
  - verification marker: User explicitly requested `/tmp` experiments comparing
    Quantleet to external libraries and then validating `result.report`
    statistics.
  - granted scope: Use the local `/tmp/quantleet-backtest-crosscheck`
    experiment outputs as planning evidence only.
  - expiration: This canonical report snapshot test-hardening slice only.
  - audit reference:
    - `/tmp/quantleet-backtest-crosscheck/outputs/comparison_report.md`
    - `/tmp/quantleet-backtest-crosscheck/outputs/report_metric_crosscheck.md`
- Verification commands:
  - `uv run pytest tests/integration/research/test_canonical_rsi_contract.py tests/integration/research/test_canonical_ema_cross_contract.py tests/integration/research/test_macd_regression_contract.py -q`
  - `uv run pytest tests/unit/backtest/test_result_reporting_metrics.py tests/unit/backtest/test_result_reporting_records.py -q`
  - `uv run pytest tests/integration/research/test_canonical_limit_entry_contract.py tests/integration/research/test_canonical_limit_exit_contract.py tests/integration/research/test_canonical_limit_mixed_contract.py -q`
  - `uv run pytest tests/integration/research/test_canonical_stop_market_opening_range_contract.py tests/integration/research/test_canonical_stop_market_donchian_contract.py tests/integration/research/test_canonical_stop_market_inside_bar_contract.py -q`
  - `uv run pytest tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py -q`
  - `uv run ruff check .`
  - `uv run mypy src`
  - `uv run poe verify-runtime`
- Success criteria:
  - RSI, EMA cross, and MACD canonical tests assert all public scalar fields in
    `run`, `execution`, `returns`, `risk`, `trades`, `costs`, and `exposure`.
  - Long report sequences are covered by first/last samples plus full digest:
    `equity`, `fills`, and `closed_trades`.
  - The report snapshot helper fails if a public report dataclass gains or
    loses a field without updating the expected contract.
  - Test failure output remains readable enough for a human or agent to identify
    whether the issue is a scalar metric, row sample, or full-sequence digest.
  - Tests assert public behavior and report contracts, not private function
    names or calculation order.
  - Existing unit tests remain focused on hand-computable edge cases.
  - Limit/stop canonical tests are not over-claimed as externally validated;
    their report hardening is staged after the market-order canonical slice.
- Out of scope:
  - Changing production report formulas.
  - Changing canonical strategy behavior.
  - Regenerating the canonical CSV fixture.
  - Adding plotting, optimization, paper trading, live trading, shorting,
    leverage, or multi-symbol tests.
  - Adding external libraries such as `vectorbt`, `quantstats`, or `empyrical`
    to the repository test dependencies.
  - Creating commits.

### Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Confirm the implementation changes map directly to the accepted testing
    principles.
  - Confirm the helper tests user-visible report contracts rather than private
    implementation details.
  - Confirm the focused and runtime-sensitive verification commands are fresh.
  - Confirm the final report clearly distinguishes externally validated
    market-order snapshots from staged limit/stop hardening.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - This document fixes scope, helper design, exact test files, staged rollout,
    verification commands, and auto-fail conditions before any test code is
    changed.
- Checks the evaluator will use:
  - Manual diff review against this plan.
  - Manual review of failed assertion readability.
  - Focused pytest commands listed in the planner contract.
  - `uv run poe verify-runtime`.
- Auto-fail conditions:
  - A broad full-object snapshot is added that hides the meaningful contract.
  - Expected report values are computed by calling production report helper
    functions from the test.
  - Tests require `/tmp`, network access, or external metrics dependencies.
  - Tests assert private helper names, private builder classes, or internal
    calculation order.
  - Tests weaken or remove existing summary/fill digest assertions.
  - Limit/stop tests are labeled externally validated before comparable
    evidence exists.

### Generator Work Log

- Planned slice order:
  1. Add canonical report normalization and assertion helpers.
  2. Add full report expectations for RSI, EMA cross, and MACD.
  3. Run focused canonical market-order tests.
  4. Tighten failure readability if the first pass is too opaque.
  5. Confirm existing report unit tests still cover hand-computable edge cases.
  6. Optionally add staged invariant-only report assertions to limit/stop tests.
  7. Run runtime-sensitive verification.
- Notes:
  - This plan intentionally does not implement the test changes.
  - Expected values should be copied from current canonical run outputs after
    cross-check evidence, not recomputed from production formulas in the test.
  - `/tmp` artifacts are evidence, not repository fixtures.
- Blockers or scope changes:
  - None.
- Implemented scope:
  - Added canonical report snapshot helper infrastructure in
    `tests/support_backtest.py`.
  - Added compact canonical report expectations in
    `tests/fixtures/backtest/canonical_report_snapshots.json`.
  - Extended the RSI, EMA cross, and MACD market-order canonical tests to assert
    `result.report`.
  - Left limit/stop report hardening staged for a later slice, as planned.
- Scope note:
  - The working tree also contains earlier uncommitted result-reporting product,
    source, and test changes governed by
    `docs/plans/2026-05-01-backtest-result-reporting-implementation-plan.md`.
    This plan owns only the canonical report snapshot test-hardening files
    listed above plus this plan artifact.

## Testing Principles Adopted

The test changes must implement the following principles.

1. Tests are product assets.
   - They must be readable, maintainable, and useful to humans and agents.
   - They should test public contracts, not internal implementation details.
   - They should fail with enough context to diagnose the contract that moved.

2. Scenario coverage must represent meaningful behavioral partitions.
   - RSI 30/70 covers low-frequency mean-reversion-like behavior.
   - EMA cross covers trend-following crossover behavior with more trades.
   - MACD cross covers higher-turnover crossover behavior.
   - Existing unit tests cover no-trade, undefined metrics, total loss,
     annualization, partial close, open final inventory, and fee-drag cases.
   - Limit/stop canonical strategies remain part of the staged test portfolio,
     but full report snapshots should follow after comparable execution-policy
     evidence or a deliberately narrower in-repo assertion scope.

3. Unit tests are necessary but insufficient.
   - Unit tests keep formulas and edge cases hand-computable.
   - Canonical integration tests protect the real data + real strategy + real
     engine + real report composition path.
   - Smoke tests protect the first-run public surface.
   - Runtime verification must run because backtest/research changes are
     runtime-sensitive in this repository.

## Evidence From `/tmp` Experiments

The following evidence justifies adding full report snapshots to the market
order canonical tests:

- `/tmp/quantleet-backtest-crosscheck/outputs/comparison_report.md`
  - Quantleet, `backtesting.py`, `backtrader`, and `vectorbt` were run against
    the same BTCUSDT 1h CSV and aligned RSI/EMA/MACD signals.
  - `timestamp`, `side`, and `quantity` matched for all three market-order
    canonical strategies.
  - `vectorbt` matched Quantleet final equity to numerical noise.
  - `backtesting.py` and `backtrader` differences were explained by fixed
    absolute slippage support and engine price-clamp policy.
- `/tmp/quantleet-backtest-crosscheck/outputs/report_metric_crosscheck.md`
  - `38` public report metrics across `3` scenarios produced `114` compatible
    reference matches.
  - `vectorbt` and `quantstats` matched return/risk metrics after aligning
    periods and risk-free assumptions.
  - The only external diagnostic difference was `vectorbt` max-drawdown sign
    convention: vectorbt returns a negative drawdown return, while Quantleet
    reports positive magnitude.

This evidence does not make `/tmp` part of the repo test harness. It is the
reason the expected values can be treated as intentional canonical contracts.

## Current Test Assets

Existing strong assets:

- `tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv`
  - real 2025 BTCUSDT 1h fixture
  - 8,760 rows
  - deterministic ordering and schema checks in `tests/support_backtest.py`
- `tests/support_backtest.py`
  - canonical strategy definitions
  - canonical engine configuration
  - first/last fill sample helpers
  - full trade-log digest helpers
- `tests/integration/research/test_canonical_rsi_contract.py`
- `tests/integration/research/test_canonical_ema_cross_contract.py`
- `tests/integration/research/test_macd_regression_contract.py`
  - current best insertion points for full `result.report` snapshots
- `tests/unit/backtest/test_result_reporting_metrics.py`
- `tests/unit/backtest/test_result_reporting_records.py`
  - focused formula and record edge-case protection

Main gap:

- The real-data canonical tests currently lock `summary` and `trade_log`, but
  they do not lock the richer `result.report` contract that users will rely on.

## Desired Test Shape

The canonical report tests should not snapshot a raw `BacktestReport` repr.
They should assert the public contract in layers.

### Scalar Contract

Assert every public field in these groups:

- `report.run`
- `report.execution`
- `report.returns`
- `report.risk`
- `report.trades`
- `report.costs`
- `report.exposure`

The helper must use dataclass field introspection to ensure the expected
mapping contains the same public field set as the actual dataclass.

### Sequence Contract

Use normalized samples plus digest for:

- `report.equity`
- `report.fills`
- `report.closed_trades`

The test must include:

- first 3 rows
- last 3 rows
- full normalized digest
- row count

This provides both high coverage and useful failure output.

### Normalization Rules

Normalize rows into JSON-compatible dictionaries before digesting:

- floats rounded to `12` decimal places unless a lower precision is explicitly
  needed for an external-library diagnostic
- timestamps kept as integers
- `None` kept as `None`
- `math.inf` represented as the string `"inf"` only inside digest payloads if
  JSON portability requires it
- tuple/list values normalized recursively

Expected scalar values should use:

- exact equality for strings, integers, `None`, and booleans
- `pytest.approx` for finite floats
- explicit `math.isinf(...)` checks for infinite floats

## Implementation Tasks

### Task 1: Add Report Snapshot Helper

**Files:**

- Modify: `tests/support_backtest.py`
- Optional test: `tests/unit/backtest/test_result_reporting_records.py`

**Step 1: Add expected containers**

Add lightweight frozen dataclasses or typed dictionaries for canonical report
expectations.

Required fields:

- scalar groups:
  - `run`
  - `execution`
  - `returns`
  - `risk`
  - `trades`
  - `costs`
  - `exposure`
- sequence expectations:
  - `equity_count`
  - `equity_first`
  - `equity_last`
  - `equity_digest`
  - `reporting_fill_count`
  - `reporting_fill_first`
  - `reporting_fill_last`
  - `reporting_fill_digest`
  - `closed_trade_count`
  - `closed_trade_first`
  - `closed_trade_last`
  - `closed_trade_digest`
  - `order_rejection_count`

**Step 2: Add normalization helpers**

Add helpers that normalize:

- dataclass instances via `dataclasses.asdict`
- floats by rounding to `12` places for digest payloads
- tuples/lists recursively
- `math.inf` consistently

Do not import private production report helpers.

**Step 3: Add scalar assertion helper**

Add `assert_report_group(actual, expected)` that:

- checks exact field-set equality
- compares finite floats with `pytest.approx`
- compares `None`, strings, ints, and booleans exactly
- handles `math.inf`

**Step 4: Add full report assertion helper**

Add `assert_canonical_report(report, expectation)` that:

- calls the scalar helper for each scalar group
- asserts row counts
- asserts first/last normalized sequence samples
- asserts sequence digests
- asserts `len(report.order_rejections)`

**Step 5: Run focused helper-adjacent tests**

Run:

```bash
uv run pytest tests/unit/backtest/test_result_reporting_metrics.py tests/unit/backtest/test_result_reporting_records.py -q
```

Expected:

- Existing report unit tests pass.

### Task 2: Add RSI Full Report Snapshot

**Files:**

- Modify: `tests/integration/research/test_canonical_rsi_contract.py`
- Modify: `tests/support_backtest.py`

**Step 1: Capture expected report values**

Run the current canonical RSI test path and capture:

- scalar groups from `result.report`
- first/last `equity`, `fills`, and `closed_trades`
- full digests for those sequences

Use the already validated current implementation outputs as the expected
contract. Do not calculate expected values in the assertion body.

**Step 2: Add expectation constant**

Place the RSI expectation near the existing RSI helper/digest functions in
`tests/support_backtest.py`, or in the RSI test file if that reads better.

Prefer support-level placement only if EMA and MACD will share the same helper
shape without hiding the expected values.

**Step 3: Assert report after existing assertions**

In `test_canonical_rsi_backtest_matches_public_result_contract`, keep the
existing `summary`, sample fill, and trade-log digest assertions, then add:

```python
assert_canonical_report(result.report, CANONICAL_RSI_REPORT_EXPECTATION)
```

**Step 4: Run focused RSI test**

Run:

```bash
uv run pytest tests/integration/research/test_canonical_rsi_contract.py -q
```

Expected:

- RSI canonical test passes.
- Failure output identifies scalar group or sequence digest if it fails.

### Task 3: Add EMA Cross Full Report Snapshot

**Files:**

- Modify: `tests/integration/research/test_canonical_ema_cross_contract.py`
- Modify: `tests/support_backtest.py`

**Step 1: Capture expected report values**

Capture the same expectation shape for EMA cross.

**Step 2: Add expectation constant**

Add `CANONICAL_EMA_REPORT_EXPECTATION`.

**Step 3: Assert report after existing assertions**

In `test_canonical_ema_backtest_matches_public_result_contract`, add:

```python
assert_canonical_report(result.report, CANONICAL_EMA_REPORT_EXPECTATION)
```

**Step 4: Run focused EMA test**

Run:

```bash
uv run pytest tests/integration/research/test_canonical_ema_cross_contract.py -q
```

Expected:

- EMA canonical test passes.

### Task 4: Add MACD Full Report Snapshot

**Files:**

- Modify: `tests/integration/research/test_macd_regression_contract.py`
- Modify: `tests/support_backtest.py`

**Step 1: Capture expected report values**

Capture the same expectation shape for MACD.

**Step 2: Add expectation constant**

Add `CANONICAL_MACD_REPORT_EXPECTATION`.

**Step 3: Assert report after existing assertions**

In `test_canonical_macd_backtest_matches_public_regression_contract`, add:

```python
assert_canonical_report(result.report, CANONICAL_MACD_REPORT_EXPECTATION)
```

**Step 4: Run focused MACD test**

Run:

```bash
uv run pytest tests/integration/research/test_macd_regression_contract.py -q
```

Expected:

- MACD canonical test passes.

### Task 5: Run Market-Order Canonical Bundle

**Files:**

- No new files.

**Step 1: Run the externally validated canonical report bundle**

Run:

```bash
uv run pytest tests/integration/research/test_canonical_rsi_contract.py tests/integration/research/test_canonical_ema_cross_contract.py tests/integration/research/test_macd_regression_contract.py -q
```

Expected:

- All three tests pass.

**Step 2: Inspect failure readability if any test fails**

If a digest fails, verify the assertion message points to:

- scenario name
- sequence name
- expected digest
- actual digest
- first/last sample mismatch if applicable

If it does not, improve helper error messages before proceeding.

### Task 6: Preserve And Re-run Focused Unit Coverage

**Files:**

- `tests/unit/backtest/test_result_reporting_metrics.py`
- `tests/unit/backtest/test_result_reporting_records.py`

**Step 1: Confirm the unit layer still owns formula edge cases**

Do not move hand-computable edge cases into canonical snapshots.

Keep coverage for:

- no trades
- first return inclusion
- annualization
- zero volatility
- undefined metrics as `None`
- total loss
- closed-trade fee allocation
- partial closes
- open final inventory
- fee drag denominator

**Step 2: Run focused unit tests**

Run:

```bash
uv run pytest tests/unit/backtest/test_result_reporting_metrics.py tests/unit/backtest/test_result_reporting_records.py -q
```

Expected:

- Unit tests pass.

### Task 7: Stage Limit/Stop Report Hardening

**Files:**

- Candidate modifications:
  - `tests/integration/research/test_canonical_limit_entry_contract.py`
  - `tests/integration/research/test_canonical_limit_exit_contract.py`
  - `tests/integration/research/test_canonical_limit_mixed_contract.py`
  - `tests/integration/research/test_canonical_stop_market_opening_range_contract.py`
  - `tests/integration/research/test_canonical_stop_market_donchian_contract.py`
  - `tests/integration/research/test_canonical_stop_market_inside_bar_contract.py`
  - `tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py`

**Step 1: Add only invariant-level report assertions first**

For limit/stop tests, do not immediately add externally validated full scalar
snapshots unless comparable evidence is created.

Safe staged assertions:

- `report.run` identity fields
- `report.execution` assumptions
- `report.returns.final_equity == result.summary.final_equity`
- `report.trades.fill_count == result.summary.total_fills`
- `report.trades.closed_trade_count == result.summary.total_trades`
- `report.costs.total_fees == result.summary.total_fees`
- `len(report.fills) == len(result.trade_log)`
- `report.fills` digest aligns with `trade_log` digest after comparable
  normalization

**Step 2: Mark full limit/stop report snapshots as a follow-up**

Full scalar snapshots for limit/stop should wait for one of:

- external execution-policy comparison evidence for limit/stop, or
- an explicit decision that these are Quantleet-only canonical regression
  contracts rather than external-validation-backed contracts.

**Step 3: Run focused limit/stop tests if changed**

Run:

```bash
uv run pytest tests/integration/research/test_canonical_limit_entry_contract.py tests/integration/research/test_canonical_limit_exit_contract.py tests/integration/research/test_canonical_limit_mixed_contract.py -q
uv run pytest tests/integration/research/test_canonical_stop_market_opening_range_contract.py tests/integration/research/test_canonical_stop_market_donchian_contract.py tests/integration/research/test_canonical_stop_market_inside_bar_contract.py -q
uv run pytest tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py -q
```

Expected:

- Any staged limit/stop report assertions pass.

### Task 8: Runtime Verification

**Files:**

- No new files.

**Step 1: Run lint and type checks**

Run:

```bash
uv run ruff check .
uv run mypy src
```

Expected:

- Both pass.

**Step 2: Run runtime-sensitive verification**

Run:

```bash
uv run poe verify-runtime
```

Expected:

- Default verification passes.
- Performance lane passes.
- If the environment prevents a gate, record the exact command output and
  reason instead of treating it as a pass.

## Expected Value Management

Expected canonical report values should be updated only when one of these is
true:

- A deliberate public contract change is approved.
- A bug in the previous expected value is demonstrated with a focused failing
  test and corrected implementation.
- The canonical CSV fixture or canonical strategy intentionally changes.

When expected values change, the reviewer should require:

- a short explanation of why the contract moved
- focused test evidence
- runtime-sensitive verification evidence
- confirmation that `/tmp` evidence was rerun if the changed metric is part of
  the externally validated market-order report set

Do not update expected values just to make a failing snapshot pass.

## Human And Agent Readability Requirements

The final tests should read as executable documentation:

- test names explain the user-visible contract
- expected scalar groups are named and grouped by report section
- sequence digests are paired with first/last samples
- helper names use product language, e.g. `assert_canonical_report`
- assertion messages identify the scenario and report section
- no expected blob is so large that a reviewer cannot scan the test file

If the expected constants make individual test files too large, prefer moving
only the data constants to `tests/support_backtest.py` while keeping the test
call site obvious.

## Evaluator Review

- Findings:
  - Third-party review found that the first helper draft did not fail when the
    top-level `BacktestReport` dataclass gained or lost a public section. Fixed
    by asserting the top-level report field set before section checks.
  - Third-party review found import-time fixture loading and weak digest
    diagnostics. Fixed by lazy-loading the JSON fixture and including scenario,
    section, expected digest, actual digest, and first/last sample status in
    failure messages.
  - Third-party review found confusing field-set labels in scalar diagnostics.
    Fixed by reporting `missing_actual_fields` and
    `unexpected_actual_fields`.
  - Third-party review found a scope-accounting risk because the working tree
    includes earlier uncommitted reporting implementation changes. Fixed by
    recording the scope note in this plan.
  - No remaining blocking findings after the fixes.
- Verification evidence:
  - `uv run pytest tests/integration/research/test_canonical_rsi_contract.py tests/integration/research/test_canonical_ema_cross_contract.py tests/integration/research/test_macd_regression_contract.py -q`
    - result: `3 passed in 1.27s`
  - `uv run pytest tests/unit/backtest/test_result_reporting_metrics.py tests/unit/backtest/test_result_reporting_records.py -q`
    - result: `11 passed in 0.05s`
  - `uv run pytest tests/integration/research -q`
    - result: `87 passed in 4.31s`
    - note: this broader command covers the staged limit/stop canonical tests
      listed in the planner contract.
  - `uv run pytest tests/smoke/local tests/structure/docs tests/structure/repo -q`
    - result: `72 passed in 0.44s`
  - `uv run ruff check .`
    - result: `All checks passed!`
  - `uv run mypy src`
    - result: `Success: no issues found in 52 source files`
  - `uv run poe verify-runtime`
    - result: default pytest `502 passed, 3 skipped in 5.47s`; coverage lane
      `502 passed, 3 skipped in 14.34s`, total coverage `92%`; `uv build`
      succeeded; repository checks passed; notebooks validated; performance
      lane `2 passed in 1.43s`
  - `uv run python scripts/repo_check.py`
    - result after final plan update: `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
    - result after final plan update: `66 passed`
- Final disposition:
  - Accepted. The implemented slice satisfies this plan's success criteria:
    market-order canonical tests now pin scalar report sections, long report
    sequences are protected by first/last samples plus digest, helper failures
    are contract-oriented and readable, and runtime-sensitive verification is
    fresh.
