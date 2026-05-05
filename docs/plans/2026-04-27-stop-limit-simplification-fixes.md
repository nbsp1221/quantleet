# Stop Limit Simplification Fixes

- Date: 2026-04-27
- Task: Apply behavior-preserving simplification fixes from stop-limit code review
- Status: `active`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: resolve the four code-simplifier review findings without changing the stop-limit product contract or public behavior.
- Governing docs:
  - [`../../AGENTS.md`](../../AGENTS.md)
  - [`../PLANS.md`](../PLANS.md)
  - [`../product-specs/stop-limit.md`](../product-specs/stop-limit.md)
  - [`2026-04-27-stop-limit-implementation.md`](2026-04-27-stop-limit-implementation.md)
  - [`2026-04-27-stop-limit-cross-engine-experiment.md`](2026-04-27-stop-limit-cross-engine-experiment.md)
- Why these are governing: this is a code simplification slice over the approved stop-limit implementation and its canonical test promotion.
- In-repo scope:
  - clarify stop-limit intrabar execution-model state flow;
  - centralize the stop-family predicate used by production modules;
  - simplify canonical stop-limit test helpers without changing expected results.
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required:
  - Requestor: user
  - Human approver: user
  - Verification marker: 2026-04-27 chat instruction, "네가 발견한거 같이 수정 진행하자"
  - Granted scope: edit the files needed to resolve the four reported simplification findings.
  - Expiration: this simplification slice only.
  - Audit reference: this plan document.
- Verification commands:
  - `uv run ruff check src/quantleet/backtest/execution_model.py src/quantleet/trading/domain/intents.py src/quantleet/trading/domain/orders.py src/quantleet/trading/domain/matching.py src/quantleet/trading/order_requests.py src/quantleet/trading/sizing.py src/quantleet/research/strategy.py tests/support_backtest.py tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py`
  - `uv run pytest tests/unit/backtest/test_execution_model.py tests/unit/trading/test_orders.py tests/unit/trading/test_matching_and_state.py tests/unit/trading/test_sizing.py tests/unit/research/test_strategy_surface.py tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py tests/integration/research/test_stop_limit_execution_semantics.py -q`
  - `uv run poe repo-check`
  - `uv run poe verify-runtime`
- Success criteria:
  - execution-model segment scanning has explicit stop-limit state flow;
  - stop-family classification has a single production predicate;
  - canonical stop-limit opening-range helper avoids repeated per-row timestamp rescans;
  - entry digest helper makes the entry-only assumption explicit;
  - all focused and runtime-sensitive verification passes.
- Out of scope:
  - changing stop-limit semantics;
  - changing generated canonical expected values;
  - broad architecture redesign.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - all four review findings are either fixed or explicitly deferred with rationale;
  - behavior is preserved by existing focused tests and runtime verification;
  - no external-engine result is encoded as a production dependency.
- Acceptance artifact location: this document.
- How the generator and evaluator agreed on done before execution: user requested fixes for the four reported simplification findings and required subagent orchestration.
- Checks the evaluator will use:
  - inspect diff against the four findings;
  - run focused tests;
  - run repo and runtime verification.
- Auto-fail conditions:
  - any expected canonical stop-limit result changes;
  - any public order API change not required for predicate centralization;
  - any unresolved test failure.

## Generator Work Log

- Planned slice order:
  - gather read-only subagent recommendations;
  - patch execution-model state flow;
  - patch shared stop-family predicate;
  - patch canonical helper simplifications;
  - run focused verification;
  - review the final diff and run runtime verification.
- Notes:
  - Parent agent owns all writes.
  - Subagents are read-only reviewers/researchers.
  - Execution model simplification uses `_SegmentCrossingResult` so segment scanning returns emitted prices separately from newly triggered unfilled stop-limit ids; the outer path traversal owns cross-segment state advancement.
  - Stop-family classification is centralized in `quantleet.trading.domain.intents._is_stop_order_type` and reused by production modules without adding a public domain export.
  - Canonical stop-limit strategy support now precomputes timestamp-keyed signals and opening-range highs once.
  - The digest helper was renamed from entry digest to buy digest because `FillEvent` does not carry order tags and the current canonical strategies are long-only.
  - Added a focused execution-model test for an at-open triggered stop-limit that is not marketable at open but fills later in the same bar.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - Resolved finding 1: segment scan no longer returns a mutated state set; it returns prices plus newly triggered unfilled ids, while the outer traversal explicitly carries `triggered_unfilled_stop_limit_ids`.
  - Resolved finding 2: stop-family predicate is centralized in the low-level intents module; subagent review found no import cycles and no remaining missed family-level literal checks.
  - Resolved finding 3: canonical opening-range stop-limit signals no longer rescan prior rows per bar; a compatibility check confirmed `4,878` precomputed opening-range signals match the previous implementation exactly.
  - Resolved finding 4: renamed the digest helper to `canonical_stop_limit_buy_trade_log_digest`, making the buy-fill assumption explicit without pretending to filter by unavailable order tags.
  - Subagent review found no remaining blockers across execution model, predicate centralization, or canonical test helpers.
- Verification evidence:
  - `uv run ruff check src/quantleet/backtest/execution_model.py src/quantleet/backtest/strategy_runtime.py src/quantleet/trading/domain/intents.py src/quantleet/trading/domain/orders.py src/quantleet/trading/domain/matching.py src/quantleet/trading/order_requests.py src/quantleet/trading/sizing.py src/quantleet/research/strategy.py tests/support_backtest.py tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py`: passed.
  - `uv run pytest tests/unit/backtest/test_execution_model.py tests/integration/research/test_stop_limit_execution_semantics.py tests/integration/research/test_canonical_stop_limit_contract.py -q`: `38 passed`.
  - `uv run pytest tests/unit/backtest/test_execution_model.py tests/unit/trading/test_orders.py tests/unit/trading/test_matching_and_state.py tests/unit/trading/test_sizing.py tests/unit/research/test_strategy_surface.py tests/integration/research/test_canonical_stop_limit_crosscheck_regression.py tests/integration/research/test_stop_limit_execution_semantics.py -q`: `132 passed`.
  - `uv run poe repo-check`: `repository checks passed`.
  - `uv run poe verify-runtime` passed:
    - `ruff check .`: passed
    - `mypy src`: `Success: no issues found in 51 source files`
    - `pytest -q`: `452 passed, 3 skipped`
    - coverage check: `coverage policy check passed`
    - `uv build`: source distribution and wheel built successfully
    - `repo_check.py`: `repository checks passed`
    - `notebook_validate.py`: four notebooks validated
    - `pytest tests/perf/test_rsi_backtest_benchmark.py -q -x --run-perf`: `2 passed`
- Final disposition:
  - Complete.
