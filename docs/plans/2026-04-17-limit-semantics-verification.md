# Active Plan

- Date: `2026-04-17`
- Task: `Verify whether the original optimistic limit-fill bug is actually resolved`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - verify the original limit-fill problem against actual executable evidence rather than repo-local tests alone
  - determine whether the current implementation still diverges on the exact favorable-limit scenario that motivated the semantics work
- Governing docs:
  - `AGENTS.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/plans/2026-04-15-limit-cross-engine-results.md`
- Why these are governing:
  - they define the intended conservative semantics, the trust problem that blocked canonical limit regressions, and the repo rules for approval and verification
- In-repo scope:
  - this verification plan artifact
  - repo-local inline execution against the current `quantcraft` code
- Out-of-repo scope:
  - ephemeral comparator package download and execution via `uv --with ...`
  - ephemeral temporary files created by the inline verification script if required by comparator APIs
- Tier A progression requested: `no`
- Approval record, if required:
  - requestor: `user`
  - human approver: `user`
  - countersignature or equivalent verification marker: current chat request explicitly demanding verification before any claim of resolution
  - scope granted: task-driven ephemeral comparator installation/execution with `uv --with ...` and temporary verification artifacts needed to prove or disprove resolution of the original limit-fill bug
  - expiration: end of current session
  - audit reference or sanitized audit link: current chat plus this active plan
- Verification commands:
  - inline `uv run python - <<'PY' ... PY` or `uv run --with <pkg> python - <<'PY' ... PY` reproductions
  - any focused `uv run pytest ... -q` command needed to confirm the current repo path still matches the reproduced scenario
- Success criteria:
  - reproduce the original favorable-limit scenario on the current `quantcraft` code
  - compare that scenario against at least one external conservative comparator if technically feasible in the current session
  - state clearly whether the original bug is resolved, still present, or only partially verified
- Out of scope:
  - new code changes
  - freezing canonical real-data golden fixtures
  - rerunning the full historical multi-strategy experiment unless required for the minimal answer

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - done means the answer is based on fresh executable evidence about the original optimistic limit-fill scenario, not inference from modified tests
- Acceptance artifact location:
  - `docs/plans/2026-04-17-limit-semantics-verification.md`
- How the generator and evaluator agreed on done before execution:
  - the evaluator will reject any claim that is not backed by a fresh reproduction of the original issue shape
- Checks the evaluator will use:
  - fresh reproduction outputs from current `quantcraft`
  - fresh comparator output if the comparator run is technically feasible
  - consistency check against the now-checked-in deterministic semantics tests
- Auto-fail conditions:
  - claiming cross-engine resolution without running a comparator
  - claiming issue resolution based only on previously known test expectations
  - leaving the result ambiguous when the command output is decisive

## Generator Work Log

- Planned slice order:
  - confirm comparator availability
  - create a minimal reproduction of the original optimistic sell-limit scenario
  - run `quantcraft` and at least one external conservative comparator on that same scenario
  - synthesize the result
- Notes:
  - no repository code edits are planned in this slice
- Blockers or scope changes:
  - 2026-04-17: local environment did not already contain comparator libraries, so verification used ephemeral `uv --with backtrader --with pandas ...` execution instead of a preexisting experiment workspace
  - 2026-04-17: verification was narrowed to the exact three-bar favorable sell-limit scenario that exposed the original optimistic-fill bug, rather than rerunning the full historical multi-strategy comparison

## Evaluator Review

- Findings:
  - The original optimistic limit-fill bug is resolved for the reproduced scenario that motivated the semantics work.
  - Fresh current-worktree `quantcraft` output on the exact three-bar repro now fills the resting sell limit at `114.0`, not `115.0`.
  - Fresh external comparator output from `backtrader` on the same three-bar repro also fills the resting sell limit at `114.0`.
  - When costs are zeroed to isolate limit semantics, `quantcraft` and `backtrader` match exactly on both fills and ending equity for the repro scenario.
  - A cost-bearing rerun still shows the same corrected sell-limit fill at `114.0` in `quantcraft`; the remaining final-equity difference in that run comes from market-order slippage configuration, not from the limit-order bug under investigation.
- Verification evidence:
  - Fresh current `quantcraft` repro with production-like costs:
    - command: inline `uv run python - <<'PY' ... PY`
    - output: `fills [('buy', 111.0, 120, 0.111), ('sell', 114.0, 180, 0.114)]`
  - Fresh external comparator repro with `backtrader`:
    - command: inline `uv run --with backtrader --with pandas python - <<'PY' ... PY`
    - output: `fills [('buy', 110.0, 2, 0.11), ('sell', 114.0, 3, 0.114)]`
  - Fresh zero-cost semantics-isolation rerun:
    - current `quantcraft` output: `fills [('buy', 110.0, 120, 0.0), ('sell', 114.0, 180, 0.0)]`, `summary 1004.0 0.0 4.0`
    - `backtrader` output: `fills [('buy', 110.0, 2, 0.0), ('sell', 114.0, 3, 0.0)]`, `final_value 1004.0`
  - Supporting repo-local semantics suite already green from the current worktree:
    - `uv run pytest tests/unit/backtest/test_execution_model.py tests/integration/research/test_backtest_execution_semantics.py tests/integration/research/test_backtest_result_contract.py -q`
    - current result earlier in session: `27 passed`
- Final disposition:
  - `accepted`
