# Active Plan

- Date: `2026-04-17`
- Task: `Implement the remaining conservative backtest limit-order semantics in the current backtest runtime`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - close the remaining limit-order conformance gap in the shipped backtest runtime
  - preserve the architectural boundary where `backtest` owns OHLC approximation and `trading` remains bar-agnostic
  - execute the work with planner/generator/evaluator discipline plus bounded subagent orchestration
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-15-backtest-semantics-conformance-implementation-plan.md`
  - `docs/plans/2026-04-17-backtest-limit-semantics-plan-authoring.md`
- Why these are governing:
  - they define the current backtest product contract, the canonical conservative path rules, the package boundaries, and the repository workflow/verification requirements
- In-repo scope:
  - update the current `src/quantcraft/backtest/*` execution path
  - add and update current semantics regressions in `tests/unit/backtest/*` and `tests/integration/research/*`
  - preserve public result contracts unless conservative semantics intentionally change them
  - run repo-local verification from the current worktree
- Out-of-repo scope:
  - live or paper trading
  - exchange-grid enforcement beyond the current contract
  - cross-engine experiments or external benchmarking
  - committing or staging changes without a later user request
- Tier A progression requested: `no`
- Approval record, if required:
  - None. The approved scope is limited to `backtest` and related tests/docs; `trading` behavior is to remain unchanged except through its existing public matcher contract.
- Verification commands:
  - `uv run pytest tests/unit/backtest/test_execution_model.py -q`
  - `uv run pytest tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q`
  - `uv run poe verify`
  - `uv run poe verify-runtime`
- Success criteria:
  - resting limits touched during continuous intrabar movement fill at the limit price rather than the bar extreme
  - resting limits crossed by a gap fill at `open`
  - the first bar has no synthetic gap segment
  - marketable limits at bar start fill immediately at the first executable price no worse than the limit
  - non-increasing timestamps are still rejected before path generation
  - `src/quantcraft/trading/domain/matching.py` stays bar-agnostic and unchanged unless fresh evidence proves otherwise
  - default and runtime-sensitive verification lanes pass from the current worktree
- Out of scope:
  - changing the public API
  - introducing a new fill-model family
  - adding unrelated refactors

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - done means the current backtest runtime and tests enforce the conservative semantics defined in the governing docs, with fresh verification evidence and synthesized subagent review findings
- Acceptance artifact location:
  - `docs/plans/2026-04-17-backtest-limit-semantics-execution.md`
- How the generator and evaluator agreed on done before execution:
  - the generator may only edit files needed for the locked semantics regressions and the minimal backtest-runtime fix set; the evaluator will reject any change that moves bar-aware semantics into `trading`
- Checks the evaluator will use:
  - red/green evidence from focused unit and integration tests
  - diff review against the governing docs
  - bounded review fan-out with evidence-bearing subagent returns
  - fresh `uv run poe verify`
  - fresh `uv run poe verify-runtime`
- Auto-fail conditions:
  - touched-limit fills still use bar extremes
  - the implementation depends on order-specific path fabrication rather than conservative traversal over the canonical path
  - `trading` absorbs bar-aware fill logic
  - verification is partial, stale, or skipped

## Generator Work Log

- Planned slice order:
  - confirm current gap from docs and code
  - run read-only research split with explicit handoff contracts
  - add failing semantics regressions first
  - implement the minimal backtest execution-model/runtime changes
  - run focused tests, review fan-out, and full repo-local verification
- Notes:
  - single writer only; delegated agents are read-only and must return evidence
  - external process guidance from Anthropic's `Harness design for long-running application development` is advisory for orchestration style, not repository authority
- Blockers or scope changes:
  - 2026-04-17: red phase added unit regressions for touched-limit, gap-cross, and marketable-limit semantics plus integration regressions for deterministic result drift
  - 2026-04-17: implementation stayed within `src/quantcraft/backtest/execution_model.py` and `src/quantcraft/backtest/runtime.py`; `trading` code was intentionally left unchanged
  - 2026-04-17: evaluator fan-out flagged one concrete post-implementation gap in runtime-ordering coverage, so an explicit out-of-order runtime regression was added before the final verification rerun
  - 2026-04-17: reviewer fan-out also noted that the gap segment remains implicit in the decisive event stream because `previous_close` is not used to emit executable events; this was accepted as a residual risk, not a blocker, because the governing contract requires `open` as the first executable price and the current tests lock the observable outcomes that matter in this slice

## Evaluator Review

- Findings:
  - The change closes the remaining conservative limit-order conformance gap in the shipped backtest runtime without moving bar-aware behavior into `trading`.
  - `src/quantcraft/backtest/execution_model.py` now exposes `tick_events_for_bar(...)` and inserts decisive synthetic ticks at crossed resting limit prices along the canonical intrabar route, while preserving `open` as the first executable price.
  - `src/quantcraft/backtest/runtime.py` now consumes per-bar decisive ticks instead of an eager whole-series event tuple, includes pending intents in per-bar traversal planning, and still activates pending intents before matching the first tick at a timestamp.
  - `src/quantcraft/trading/domain/matching.py` was not changed; the shared matcher remains bar-agnostic, which matches the governing design boundary.
  - The deterministic integration/result contracts were rebaselined from the optimistic sell fill at `115.0` to the conservative touched-limit fill at `114.0`.
  - Added regression coverage now locks:
    - sell-side intrabar touched-limit fill at the limit price
    - buy-side intrabar touched-limit fill at the limit price
    - gap-crossed resting limit fill at `open`
    - marketable limit fill at the first executable `open`
    - out-of-order bars rejected on the runtime path before matching
  - Review fan-out synthesis:
    - accepted: add explicit runtime-path out-of-order regression because runtime now owns the guard
    - accepted as residual risk only: the gap segment is implicit in the current decisive event stream because `previous_close` does not emit executable events of its own
    - accepted as residual risk only: the perf gate still does not stress a limit-heavy workload, even though the checked runtime lane passed
- Verification evidence:
  - Red phase:
    - `uv run pytest tests/unit/backtest/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q`
    - result before implementation: `4 failed, 21 passed`
    - failures were the missing `tick_events_for_bar(...)` API and the optimistic `115.0` deterministic sell-fill expectation
  - Focused green verification after implementation:
    - `uv run pytest tests/unit/backtest/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q`
    - final result: `27 passed`
  - Fresh repo-local verification after the final coverage addition:
    - `uv run poe verify`
    - result: `308 passed, 3 skipped`; coverage policy passed at `92%`; `ruff`, `mypy`, `uv build`, `repo_check.py`, and notebook validation all passed
    - `uv run poe verify-runtime`
    - result: `308 passed, 3 skipped`; runtime lane, coverage, packaging, repo check, notebook validation, and perf check all passed
    - runtime perf evidence:
      - `pytest tests/perf/test_rsi_backtest_benchmark.py -q -x --run-perf`
      - result within `verify-runtime`: `2 passed`
  - Evidence-bearing review fan-out:
    - architecture/correctness reviewer: no findings; boundary preserved; residual risk noted for implicit gap modeling
    - test/contracts reviewer: flagged missing runtime-path ordering coverage and noted the implicit-gap distinction as residual risk
    - runtime/perf reviewer: no blockers; residual risk only for limit-heavy workload scaling outside the current perf gate
- Final disposition:
  - `accepted`
