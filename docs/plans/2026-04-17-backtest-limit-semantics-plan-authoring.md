- Date: 2026-04-17
- Task: Author and harden the implementation plan for the remaining backtest limit-order semantics conformance gap
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal:
  - produce a current-state implementation plan that explains how to close the
    remaining backtest limit-order semantics conformance gap
  - ground the plan in the current `backtest`, `trading`, and test topology
  - obtain explicit subagent review fan-out and revise the plan until the
    remaining issues are either fixed in the document or clearly called out
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
  - `docs/plans/TEMPLATE.md`
  - existing draft: `docs/plans/2026-04-15-backtest-semantics-conformance-implementation-plan.md`
- Why these are governing:
  - they define the current shipped backtest contract, the approved conservative
    execution-semantics model, the repository workflow contract, and the
    planning artifact location/rules
- In-repo scope:
  - inspect current source and tests relevant to the limit-order semantics gap
  - update the implementation plan document under `docs/plans/`
  - record a handoff contract suitable for later implementation
  - run bounded subagent review fan-out and revise the plan document
- Out-of-repo scope:
  - implementing the code change
  - changing the public API or backtest behavior in this slice
  - external benchmarking or live-trading validation
- Tier A progression requested: `no`
- Approval record, if required:
  - None. This slice is documentation and planning only.
- Verification commands:
  - targeted `sed -n` reads over governing docs, current backtest source, and
    current tests
  - `uv run poe repo-check`
- Success criteria:
  - the implementation plan references current file paths rather than retired
    `research.application` or `research.adapters` paths
  - the plan clearly separates semantic correctness work from optional
    performance follow-up
  - the plan includes explicit acceptance criteria, evidence expectations, and
    verification commands for the eventual implementation slice
  - subagent review findings are synthesized and applied or explicitly rejected
- Out of scope:
  - fixing the semantics bug itself
  - committing any code changes outside planning artifacts

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - the finished plan must be actionable by an engineer with no local context
  - the finished plan must describe the real remaining issue without relying on
    outdated package ownership or deleted test paths
  - the review pass must use evidence-bearing subagent output and parent
    synthesis
- Acceptance artifact location:
  - `docs/plans/2026-04-15-backtest-semantics-conformance-implementation-plan.md`
  - `docs/plans/2026-04-17-backtest-limit-semantics-plan-authoring.md`
- How the generator and evaluator agreed on done before execution:
  - done means a current, reviewed implementation plan with a clear handoff
    contract for later execution, not just a prose explanation of the bug
- Checks the evaluator will use:
  - current-source and current-test inspection
  - subagent review fan-out
  - `uv run poe repo-check`
- Auto-fail conditions:
  - the plan still references removed package paths
  - the plan collapses semantic fixes and performance work into one opaque step
  - the plan lacks verification commands or acceptance criteria

## Generator Work Log

- Planned slice order:
  - inspect current code/tests and the old untracked plan draft
  - write/update this active plan
  - draft the refreshed implementation plan
  - run subagent review fan-out with explicit handoff contracts
  - revise the plan and close this planning slice
- Notes:
  - existing untracked semantics-plan drafts appear to be from the pre-migration
    topology, so the relevant draft should be updated rather than trusted as-is
- Blockers or scope changes:
  - 2026-04-17: the existing draft at
    `docs/plans/2026-04-15-backtest-semantics-conformance-implementation-plan.md`
    was still anchored to retired `research.application` /
    `research.adapters` paths and had to be rewritten against the current
    `backtest` topology.
  - 2026-04-17: reviewer fan-out identified four gaps in the first local
    rewrite, all of which were incorporated into the plan:
    - explicit first-bar `previous_close=None` / no-gap semantics
    - preserved out-of-order timestamp rejection before gap generation
    - explicit same-open multi-order regression ownership
    - narrowed/clarified perf-gate scope for limit-heavy traversal

## Evaluator Review

- Findings:
  - The refreshed implementation plan now uses current source ownership under
    `src/quantcraft/backtest/*` and no longer relies on removed
    `research.application` or `research.adapters` package paths.
  - The plan now explicitly preserves the architectural boundary required by
    the governing docs:
    - OHLC approximation stays in `backtest`
    - `trading.domain.matching` stays bar-agnostic
  - Reviewer fan-out surfaced and resolved the following material plan gaps:
    - missing first-bar no-gap rule
    - missing owner for monotonic timestamp validation after the runtime
      refactor
    - under-specified same-open multi-order regression surface
    - perf-gate overclaiming for limit-heavy traversal
  - Final reviewer re-check confirmed no further high-signal issues remained in
    architecture/semantics scope or testing-plan scope after the revisions.
- Verification evidence:
  - Current-state source/test inspection:
    - `src/quantcraft/backtest/execution_model.py`
    - `src/quantcraft/backtest/runtime.py`
    - `src/quantcraft/backtest/order_activation.py`
    - `src/quantcraft/backtest/strategy_runtime.py`
    - `src/quantcraft/trading/domain/matching.py`
    - `tests/unit/backtest/test_execution_model.py`
    - `tests/integration/research/test_backtest_execution_semantics.py`
    - `tests/integration/research/test_backtest_result_contract.py`
    - `tests/integration/research/support_backtest_runner.py`
    - `tests/perf/test_rsi_backtest_benchmark.py`
    - `tests/support_backtest.py`
  - Reviewed implementation plan artifact:
    - `docs/plans/2026-04-15-backtest-semantics-conformance-implementation-plan.md`
  - Subagent review fan-out:
    - `Nash` (semantics/architecture): flagged first-bar no-gap and timestamp
      validation ownership; final re-check said no further high-signal issues
    - `Jason` (testing/contracts): flagged same-open regression ownership and
      Task 4 verification/file-list mismatches; final re-check said the mismatch
      was fixed with no new high-signal issue
    - `Wegener` (runtime/perf): flagged preserved chronological validation,
      first-bar rule, and perf-gate blind spot for limit-heavy traversal
  - Fresh repo verification:
    - `uv run poe repo-check`
    - result: `repository checks passed`
- Final disposition:
  - Complete. The implementation plan document was rewritten against the
    current codebase, reviewed through bounded subagent fan-out, revised to
    address all high-signal findings, and verified to remain consistent with
    repository doc checks.
