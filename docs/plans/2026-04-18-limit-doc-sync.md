# Active Plan

- Date: `2026-04-18`
- Task: `Sync limit-order documentation with the current shipped code and regression state`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - remove current-documentation drift around the resolved backtest limit-order semantics work
  - align the governing backtest product spec with the current code and test state
  - clean up accepted limit-order plan artifacts that still claim `active` status
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-17-backtest-limit-semantics-execution.md`
  - `docs/plans/2026-04-17-limit-semantics-verification.md`
  - `docs/plans/2026-04-17-real-strategy-cross-validation-rerun.md`
  - `docs/plans/2026-04-18-limit-strategy-regression-promotion.md`
- Why these are governing:
  - they define the current repo workflow, the governing backtest product contract, the approved conservative limit-order semantics, and the accepted evidence trail for the recent limit-order work
- In-repo scope:
  - update current-documentation claims that conflict with the current code/test state
  - update accepted limit-order plan artifacts whose header status is stale
  - add this active plan and record verification evidence
- Out-of-repo scope:
  - code changes under `src/quantcraft/*`
  - test behavior changes
  - rewriting historical analysis documents whose statements were correct at their original timestamp
- Tier A progression requested: `no`
- Approval record, if required:
  - None. This slice is Tier B documentation synchronization only.
- Verification commands:
  - `uv run pytest tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py tests/integration/research/test_canonical_limit_entry_contract.py tests/integration/research/test_canonical_limit_exit_contract.py tests/integration/research/test_canonical_limit_mixed_contract.py -q`
  - `uv run poe repo-check`
- Success criteria:
  - the governing backtest product spec no longer claims an open current limit-order conformance gap if the current worktree evidence shows it is resolved
  - accepted limit-order plan artifacts no longer report `Status: active`
  - no new workflow or repo-check violations are introduced
- Out of scope:
  - historical narrative cleanup outside the current-authority docs and the accepted plan headers
  - rewording unrelated product-spec content

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - done means the current authoritative docs match the current limit-order code/test state and the updated docs pass fresh repo-local verification
- Acceptance artifact location:
  - `docs/plans/2026-04-18-limit-doc-sync.md`
- How the generator and evaluator agreed on done before execution:
  - the generator may only edit the stale current-state claims and stale accepted-plan statuses needed to remove the observed inconsistencies
- Checks the evaluator will use:
  - focused diff review against the current code/test evidence
  - fresh focused pytest evidence for the current limit-order contracts
  - fresh `uv run poe repo-check`
- Auto-fail conditions:
  - the governing spec still claims the resolved limit-order gap is open
  - an accepted plan artifact still reports `active`
  - verification is skipped or stale

## Generator Work Log

- Planned slice order:
  - inspect current authoritative and accepted limit-order docs
  - update the governing product-spec note
  - update stale accepted-plan statuses
  - run focused verification and record evidence
- Notes:
  - historical analysis documents will be left intact unless they are themselves current-authority documents
- Blockers or scope changes:
  - 2026-04-18: the stale-current-state drift was narrower than expected; only one governing product-spec note and three accepted-plan header statuses required edits

## Evaluator Review

- Findings:
  - Updated `docs/product-specs/backtest-mvp.md` so the current implementation note matches the now-shipped conservative limit-order semantics instead of claiming the conformance gap is still open.
  - Updated the accepted limit-order evidence artifacts `docs/plans/2026-04-17-backtest-limit-semantics-execution.md`, `docs/plans/2026-04-17-limit-semantics-verification.md`, and `docs/plans/2026-04-17-real-strategy-cross-validation-rerun.md` from `Status: active` to `Status: complete`.
  - Left historical analysis documents unchanged where they accurately describe the repository state at their original timestamp rather than acting as current-authority docs.
- Verification evidence:
  - Focused current-behavior verification:
    - `uv run pytest tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py tests/integration/research/test_canonical_limit_entry_contract.py tests/integration/research/test_canonical_limit_exit_contract.py tests/integration/research/test_canonical_limit_mixed_contract.py -q`
    - result: `18 passed`
  - Fresh repo documentation/structure verification:
    - `uv run poe repo-check`
    - result: `repository checks passed`
- Final disposition:
  - `accepted`
