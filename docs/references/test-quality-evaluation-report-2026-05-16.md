# Test Quality Evaluation Report

- Date: 2026-05-16
- Evaluator: Codex with three read-only LLM subagent reviewers
- Commit: current working tree on `main`
- Scope: current `quantleet` test suite quality
- Evaluation plan: `docs/references/test-quality-evaluation-plan.md`

## Executive Summary

- Overall disposition: strong beta-level suite with several quality-gate gaps
  to address before the next major feature push.
- Main strengths:
  - The default suite is fast enough for local feedback: `739 passed, 4 skipped`
    in `14.74s` to `15.00s`.
  - Coverage is high: coverage.py combined line/branch coverage is `91%`,
    above the current `90%` repository floor.
  - The suite has broad unit, integration, structure, smoke, and explicit perf
    coverage.
  - Integration tests cover many externally visible backtest, reporting,
    parameter-study, and walk-forward contracts.
- Main risks:
  - Some integration tests import internal `quantleet.trading.domain.*` paths
    instead of public beta surfaces.
  - Some real-data golden tests lock broad incidental numeric behavior into the
    default lane.
  - Live-test exclusion depends on the `live` marker instead of the
    `tests/smoke/live` path.
  - Ingestion adapter tests need stronger malformed-input and provider-failure
    coverage.
  - Mutation testing and randomized-order flakiness testing were not run in
    this evaluation.
- Recommended next gate:
  - Keep current default gates.
  - Add a qualitative changed-test review gate for major feature work.
  - Add targeted structure checks for live/perf taxonomy and public-surface
    imports before adding heavier mutation gates.

## Commands

| Command | Result | Runtime | Notes |
| --- | --- | ---: | --- |
| `uv run pytest --collect-only -q` | passed | `0.90s` | `743` collected test cases |
| `uv run pytest -q --durations=10` | passed | `15.00s` | `739 passed, 4 skipped` |
| `uv run pytest -q -rs` | passed | `14.74s` | skip reasons recorded |
| `uv run poe coverage` | passed | `43.90s` pytest runtime | combined line/branch coverage `91%` |
| `uv run pytest -q tests/unit` | passed | `1.35s` | `456 passed` |
| `uv run pytest -q tests/integration` | passed | `13.31s` | `124 passed` |
| `uv run pytest -q tests/structure tests/smoke/local` | passed | `1.04s` | `159 passed` |
| `uv run pytest -q tests/perf --run-perf` | passed | `2.35s` | `3 passed`; benchmark median `229.0639 ms` |

## Quantitative Metrics

| Metric | Value | Threshold | Disposition |
| --- | ---: | ---: | --- |
| Collected pytest cases | `743` | n/a | informational |
| Default passed tests | `739` | n/a | pass |
| Default skipped tests | `4` | expected explicit-only skips | pass |
| Xfail usage | `0` | n/a | good |
| Test files | `120` | n/a | informational |
| AST test functions | `665` | n/a | informational; parametrization expands to `743` |
| Unit collected cases | `456` | n/a | pass |
| Integration collected cases | `124` | n/a | pass |
| Structure collected cases | `149` | n/a | pass |
| Smoke collected cases | `11` | n/a | pass |
| Perf collected cases | `3` | n/a | explicit-only pass |
| Combined line/branch coverage | `91%` | `90%` | pass |
| Default suite runtime | `14.74s` to `15.00s` | TBD | good local loop |
| Slowest default test | `2.45s` | TBD | acceptable but watch |
| Broad `pytest.raises(Exception)` | `1` | prefer `0` | important cleanup |
| Tests with no `assert` or `pytest.raises` by AST scan | `5` | review required | currently defensible but worth reducing |
| `getattr(..., None) is not None` public import checks | `91` occurrences in `6` files | review required | acceptable for smoke/import checks, weak elsewhere |
| Mutation score | not run | TBD | not enough evidence |
| Randomized-order flakiness run | not run | `0` failures when adopted | not enough evidence |

## Skip Reasons

Default `pytest -q -rs` skipped exactly the explicit-only lanes:

- `tests/perf/test_backtest_plotting_scale.py`: performance tests are
  explicit-only
- `tests/perf/test_rsi_backtest_benchmark.py`: performance tests are
  explicit-only, two tests
- `tests/smoke/live/test_exchange_live_smoke.py`: live tests are explicit-only

No `xfail` usage was found.

## Test Portfolio

| Area | Files | Collected cases | Main coverage | Gaps |
| --- | ---: | ---: | --- | --- |
| Unit | `47` | `456` | domain objects, sizing, execution, data adapters, indicators, strategy config, WFA preflight | ingestion adapter failure cases; some existence-only assertions |
| Integration | `35` | `124` | public workflows, execution semantics, reporting, parameter study, WFA, real data contracts | internal imports; golden regression brittleness; some fake-engine coupling |
| Structure | `32` | `149` | architecture boundaries, docs, repo rules, command surface | taxonomy enforcement misses `perf`; live skip is marker-dependent |
| Smoke | `4` | `11` | public imports, local examples, quickstart | import existence assertions are intentionally shallow |
| Performance | `2` | `3` | RSI runtime benchmark, plotting scale behavior | plotting scale test has no runtime threshold despite perf placement |

## Coverage

Coverage passed the repository policy:

- coverage.py branch measurement is enabled
- combined line/branch coverage: `91%`
- required combined coverage floor: `90%`

Lowest notable files from the coverage report:

- `src/quantleet/_notebook_tools.py`: `0%`
- `src/quantleet/_repo_tools.py`: `75%`
- `src/quantleet/trading/order_requests.py`: `85%`
- `src/quantleet/data/sources.py`: `86%`
- `src/quantleet/trading/sizing.py`: `87%`
- `src/quantleet/data/__init__.py`: `88%`
- `src/quantleet/strategy/series.py`: `90%`

Interpretation: coverage is healthy as a floor. The current gate intentionally
uses coverage.py's standard combined line/branch semantics instead of custom
separate line, branch, or path-specific thresholds. It does not by itself prove
assertion strength. The qualitative findings below are more important for the
next gate increase.

## Runtime Cost

Slowest default-lane tests:

| Test | Runtime |
| --- | ---: |
| `tests/integration/research/test_parameter_study_canonical_grid_contract.py::test_parameter_study_pins_validated_canonical_btc_grid_outputs[rsi_mean_reversion]` | `2.45s` |
| `tests/integration/research/test_walk_forward_real_data_contract.py::test_wfa_real_data_focused_sma_rsi_contract_matches_golden_slice` | `2.08s` |
| `tests/integration/research/test_parameter_study_canonical_grid_contract.py::test_parameter_study_pins_validated_canonical_btc_grid_outputs[donchian_breakout]` | `1.43s` |
| `tests/integration/research/test_parameter_study_canonical_grid_contract.py::test_parameter_study_pins_validated_canonical_btc_grid_outputs[sma_cross]` | `1.25s` |
| `tests/integration/commands/test_built_artifact_imports.py::test_built_wheel_exposes_documented_public_imports` | `0.51s` |

Interpretation: the default lane is still comfortably local-loop friendly. The
slowest tests are valuable real-data or build/import contracts, but the broad
golden assertions should be reviewed before they become harder to maintain.

## Assertion Pattern Scan

AST scan across `tests/**/*.py`:

- test functions: `665`
- assert statements: `1843`
- `pytest.raises` calls: `202`
- no `assert` and no `pytest.raises`: `5`
- `assert ... is not None`: `74`
- `assert ... is None`: `62`
- `len(...) > 0` assertions: `0`

The five tests without direct asserts or `pytest.raises` are:

- `tests/structure/architecture/test_backtest_plotting_boundaries.py:29`
- `tests/structure/architecture/test_backtest_plotting_boundaries.py:38`
- `tests/unit/trading/test_contracts.py:214`
- `tests/unit/trading/test_contracts.py:251`
- `tests/unit/trading/test_contracts.py:300`

Manual interpretation:

- the two plotting-boundary tests rely on subprocess `check=True`; that is a
  valid assertion style but should be used sparingly
- the three trading contract tests delegate assertions to helper functions;
  that is acceptable, but direct local assertions would make the AST signal
  clearer

Broad exception pattern:

- one `pytest.raises(Exception)` appears in
  `tests/unit/research/test_walk_forward_preflight.py:145`

## Mutation Testing

Mutation testing was not run in this evaluation.

Reason:

- the evaluation plan recommends targeted mutation as a later audit because it
  can be expensive and requires tool selection.
- no mutation tool is currently part of the repo-local command surface.

Recommended first target:

- `src/quantleet/trading/domain/`
- `src/quantleet/trading/sizing.py`
- `src/quantleet/backtest/execution_model.py`
- `src/quantleet/research/walk_forward.py`

Do not make mutation score a full-repository hard gate before a baseline run
establishes runtime cost and equivalent-mutant handling.

## Flakiness

Observed evidence:

- default pytest lane passed repeatedly during this evaluation:
  - `uv run pytest -q --durations=10`
  - `uv run pytest -q -rs`
  - the pytest execution inside `uv run poe coverage`
- no random/time/sleep usage was found in tests by simple text scan.
- live and perf lanes are explicit-only in current behavior.

Not run:

- randomized-order testing
- formal repeat-count testing with a plugin

Interpretation: there is no current sign of flakiness, but this is not yet a
formal flaky-test gate.

## LLM Review Synthesis

Three read-only subagent reviews were used:

- unit-test reviewer: `tests/unit`
- integration-contract reviewer: `tests/integration`
- structure/smoke/perf reviewer: `tests/structure`, `tests/smoke`,
  `tests/perf`, repository test configuration

### Finding Counts

| Severity | Count |
| --- | ---: |
| High | `1` |
| Medium / Important | `9` |
| Low / Minor | `4` |
| Blocker | `0` |

### High Finding

1. Integration tests sometimes depend on internal package paths instead of
   public beta surfaces.

   Evidence from subagent review:

   - `tests/integration/research/test_backtest_execution_semantics.py`
   - `tests/integration/research/test_order_reservation_contract.py`
   - `tests/integration/backtest/test_plotting.py`

   These tests import internal domain types such as `CostConfig`, `BarEvent`,
   `OrderRejectedEvent`, and `TradingState` from `quantleet.trading.domain.*`
   where public surfaces exist for at least some of the contracts. This makes
   integration tests more sensitive to internal topology refactors than a
   public-contract integration suite should be.

   Recommendation:

   - prefer `quantleet.backtest`, `quantleet.research`, `quantleet.strategy`,
     and `quantleet.data` imports in integration tests when a public facade
     exists
   - add a structure check that flags integration imports from internal domain
     paths once a public equivalent exists

### Medium / Important Findings

1. CCXT adapter tests are biased toward happy paths.

   Evidence:

   - `tests/unit/data/adapters/test_ccxt_source.py` covers loading,
     pagination, limits, bounded timeframes, short pages, and end filtering
   - no `pytest.raises` cases are present in that file

   Missing risk coverage:

   - malformed CCXT rows
   - non-finite OHLCV values
   - bad timestamps
   - backend exceptions
   - unsupported timeframe parsing behavior

2. Some tests assert symbol existence rather than meaningful contract shape.

   Evidence:

   - `tests/unit/research/test_parameter_study_preflight.py`
   - `tests/unit/research/test_indicator_surface.py`
   - `tests/unit/trading/test_contracts.py`
   - smoke and built-artifact import tests intentionally use many
     `getattr(..., None) is not None` checks

   Interpretation:

   - existence checks are acceptable for public import smoke tests
   - they should not be the main assertion in unit or integration tests for
     behavior-bearing contracts

3. Plotting unit tests are coupled to Matplotlib internals and exact styling.

   Evidence:

   - private `fig._suptitle`
   - exact color, collection, linewidth, and marker internals in
     `tests/unit/backtest/test_plotting.py`

   Interpretation:

   - some visual contract checks are valid
   - internal representation details should be reduced where they do not
     represent user-visible behavior

4. WFA failure tests encode execution order and call counts.

   Evidence:

   - fake engines in `tests/integration/research/test_walk_forward_failures.py`
     trigger failures using `len(bars.rows)` and `self.calls`

   Recommendation:

   - make failure conditions depend on public strategy/config/window behavior
     rather than exact call sequence

5. Real-data golden tests lock broad incidental numeric behavior.

   Evidence:

   - `tests/integration/research/test_walk_forward_real_data_contract.py`
   - `tests/integration/research/test_order_sizing_contract.py`

   Interpretation:

   - these are valuable regression sentinels
   - the exact full digest assertions may be too brittle for the default
     integration lane if they conflate public contract, fixture data,
     indicator details, rounding, and matching internals

6. Some ParameterStudy metric-extraction integration tests are actually unit
   boundary tests.

   Evidence:

   - `tests/integration/research/test_parameter_study_failures.py` uses
     `SimpleNamespace` reports and fake engines for metric-extraction failure
     paths

   Recommendation:

   - keep fake-heavy metric extractor tests in unit
   - preserve integration tests for real `BacktestEngine` and real report
     composition

7. Live-test exclusion is marker-based, not path-based.

   Evidence:

   - `tests/conftest.py` skips live tests when `"live" in item.keywords`
   - an unmarked test under `tests/smoke/live` would run in default `pytest -q`
   - current live module is marked correctly, so behavior is currently passing

   Recommendation:

   - either skip `tests/smoke/live/` by path as well as marker, or add a
     structure test requiring every live module to declare `pytestmark =
     pytest.mark.live`

8. Repo-check taxonomy does not fully enforce `tests/perf`.

   Evidence:

   - `docs/references/testing.md` includes `tests/perf`
   - `src/quantleet/_repo_tools.py` has
     `SUPPORTED_TEST_DIRS = ("unit", "integration", "structure", "smoke")`
   - `perf` is omitted

   Recommendation:

   - include `perf` in the repo-check taxonomy list
   - consider failing if `tests/` itself is absent

9. Skip/xfail admission policy is under-documented.

   Evidence:

   - current suite has no xfail usage
   - `docs/references/testing.md` does not define future skip/xfail admission
     rules beyond explicit-only live/perf behavior

   Recommendation:

   - document that skips/xfails require a reason, owner or issue reference,
     expiration/removal condition, and cannot be long-term compatibility masks

### Low / Minor Findings

1. CSV source edge-case coverage is weaker than DataFrame source coverage.
2. Duplicate CCXT monthly timeframe tests reduce maintainability.
3. Some fresh-instance assertions inspect construction logs rather than
   outcome isolation.
4. `tests/perf/test_backtest_plotting_scale.py` is more of a scale behavior
   test than a bounded performance test, despite its location and name.

## Strengths

The suite has several strong properties:

- unit tests are numerous and fast: `456 passed in 1.35s`
- integration tests cover real user workflows and execution semantics
- structure tests actively protect repository conventions, docs, architecture
  boundaries, command surfaces, and hard gates
- smoke tests validate public import surfaces and public examples
- live and perf tests are excluded from the default lane in current behavior
- trading domain coverage is exactly at the strict `100%` requirement
- test names are generally behavior-oriented and readable

Strong examples called out by reviewers:

- parameter grid validation preflight/no-run behavior
- strategy config validation outcomes
- trading order validation across non-finite quantities
- backtest result/reporting contract tests
- plotting snapshot ownership tests
- stop-market, stop-limit, reservation, and sizing integration contracts

## Recommended Gate Changes

### Immediate

- Add a structure rule that `tests/smoke/live/` tests are live-explicit by path
  or must declare the `live` marker.
- Add `perf` to repo-check taxonomy enforcement.
- Add a skip/xfail policy to `docs/references/testing.md`.
- Add qualitative changed-test review guidance that flags:
  - new existence-only assertions outside smoke/import tests
  - broad `pytest.raises(Exception)`
  - internal/private assertions that do not represent user-visible behavior

### Next

- Replace integration-test internal imports with public facade imports where
  public equivalents exist.
- Strengthen CCXT and CSV ingestion failure tests.
- Move fake-heavy ParameterStudy metric-extraction tests to unit, or add a real
  integration equivalent.
- Rework WFA failure tests to fail based on public scenario conditions rather
  than call counts.

### Later

- Establish a targeted mutation-testing baseline on trading/backtest/research
  hotspots.
- Add randomized-order or repeat-count flaky-test audits as an explicit quality
  lane.
- Split broad golden fixture digests into explicit regression/runtime checks if
  they start to slow or destabilize the default lane.

## Open Human Decisions

1. Whether exact real-data golden digests should remain in the default
   integration lane or move to `verify-runtime` / a named regression lane.
2. Which mutation-testing tool should become the first repo-local audit tool.
3. Whether live/perf explicit-only enforcement should use path as source of
   truth, marker as source of truth, or both.
4. How strict the next gate should be for public-surface-only imports in
   integration tests.

## Final Disposition

The current test suite is strong enough for beta maintenance and ordinary small
feature work. It is not yet at the desired next-level quality gate for larger
feature expansion because some tests still protect internal implementation
shape rather than only public contracts, and mutation/flakiness evidence is not
yet established.

Recommended next step: fix the immediate structure/policy gaps first, then run
a targeted cleanup pass on integration public-surface imports and ingestion
failure coverage.
