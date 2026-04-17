# Active Plan

- Date: `2026-04-15`
- Task: `Implement conservative backtest execution semantics and verify runtime conformance`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - implement the promoted conservative backtest execution semantics
  - keep `trading` as the generic matcher while moving OHLC approximation into the backtest adapter path
  - verify the new behavior with focused semantics tests and runtime-sensitive repo-local verification
- Governing docs:
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/plans/2026-04-15-backtest-semantics-conformance-implementation-plan.md`
- Why these are governing:
  - they define the intended semantics, the matching boundary, and the approved implementation sequence
- In-repo scope:
  - update backtest execution-path source files
  - add and update semantics tests
  - run repo-local runtime-sensitive verification
- Out-of-repo scope:
  - external experiments
  - live or paper trading code
  - new limit canonical real-data goldens
- Tier A progression requested: `yes`
- Approval record, if required:
  - requestor: `user`
  - human approver: `Naki`
  - countersignature or equivalent verification marker: `user approval in chat after git-config identity check; current turn explicitly requested implementation`
  - scope granted: `Tier A implementation and verification for backtest execution semantics`
  - expiration: `2026-04-16T23:59:59+09:00`
  - audit reference or sanitized audit link: `chat approval lineage plus 2026-04-15-backtest-semantics-implementation-planning.md`
- Verification commands:
  - `uv run pytest tests/unit/research/adapters/test_execution_model.py -q`
  - `uv run pytest tests/integration/research/test_backtest_execution_semantics.py -q`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Success criteria:
  - resting intrabar limits fill at the limit price, not the bar extreme
  - gap-crossed resting limits fill at `open`
  - backtest execution-model path generation remains outside `trading`
  - execution-model traversal no longer requires eager full-run event materialization
  - runtime-sensitive verification passes from current repo state
- Out of scope:
  - refreshing the cross-engine experiment
  - adding canonical limit real-data regression goldens

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - done means the code and tests enforce the promoted conservative semantics for the local deterministic execution semantics suite, and repo-local runtime-sensitive verification passes
- Acceptance artifact location:
  - `docs/plans/2026-04-15-backtest-semantics-implementation-execution.md`
- How the generator and evaluator agreed on done before execution:
  - this plan fixes the implementation slice and required checks before edits begin
- Checks the evaluator will use:
  - focused semantics test review
  - diff review against the promoted docs
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Auto-fail conditions:
  - matching logic in `trading` absorbs bar-aware special cases
  - tests pass only because expectations stayed optimistic
  - runtime verification is skipped or failing

## Generator Work Log

- Planned slice order:
  - read-only subagent research split
  - read-only review fan-out after implementation
  - failing semantics tests
  - minimal runtime changes for conservative semantics
  - runtime-sensitive verification
- Notes:
  - one writer only; delegated agents stay read-only and return evidence
- Blockers or scope changes:
  - implementation landed without creating the optional `backtest_path.py`; the canonical-path logic stayed inside `execution_model.py` for a smaller first conformance slice
  - review fan-out produced one accepted follow-up test gap and one accepted sequence-determinism gap; both were fixed before the final verification rerun
  - review fan-out also raised a `tick_size` usage concern; that remains a documented residual risk for a later slice, not a blocker for the current conservative semantics contract

## Evaluator Review

- Findings:
  - the optimistic eager whole-series event materialization was removed from `src/quantcraft/research/application/backtest.py`
  - `src/quantcraft/research/adapters/execution_model.py` now emits per-bar executable ticks and conservative decisive limit-touch prices instead of bar extremes
  - `trading` matching stayed generic; no bar-aware logic was added under `src/quantcraft/trading/domain/`
  - deterministic integration contracts and backtest summary contracts were updated to the conservative fill outputs
  - review fan-out synthesis:
    - accepted: add explicit buy-side intrabar touched-limit regression coverage
    - accepted: restore stronger sequence-level adapter determinism coverage across the checked-in fixture
    - rejected as blocker: the implementation's use of active intents for decisive-event compression, because the promoted docs explicitly allow order-aware acceleration over a fixed canonical path
    - accepted as residual risk only: `tick_size` is currently unused by the path adapter and should be addressed in a follow-up execution-model slice if exchange-grid enforcement becomes part of the contract
- Verification evidence:
  - `uv run pytest tests/unit/research/adapters/test_execution_model.py -q` -> `11 passed`
  - `uv run pytest tests/unit/research/adapters/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q` -> `27 passed`
  - `uv run pytest tests/integration/research -q` -> `27 passed`
  - `uv run pytest tests/unit/trading/test_matching_and_state.py -q` -> `12 passed`
  - `uv run pytest tests/structure/repo/test_runtime_verification_lane.py -q` -> `2 passed`
  - `uv run poe verify-runtime` -> lint, mypy, full pytest, coverage, build, repo-check, notebook validation, and perf check all passed
  - `uv run poe repo-check` -> `repository checks passed`
- Final disposition:
  - `accepted`
