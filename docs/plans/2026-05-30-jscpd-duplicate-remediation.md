# jscpd Duplicate Remediation

- Date: 2026-05-30
- Task: Re-review current jscpd duplicate-code findings, fix confirmed issues, and prove the gate passes.
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Decide whether the 9 current jscpd findings are true maintainability issues or acceptable test symmetry, then remove the duplicated blocks without changing production behavior.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repository workflow, safety tiers, current product scope, and check surface for test/backtest/research changes.
- In-repo scope:
  - Test support modules and tests under `tests/`.
  - Existing jscpd configuration and plan evidence if needed.
- Out-of-repo scope:
  - No package publishing, no external services, no live checks, no commits, no worktree separation.
- Tier A progression requested: `no`
- Approval record, if required:
  - Not required. The slice changes tests/support only and does not alter `trading` or `execution` source behavior.
- Verification commands:
  - `uv run poe duplicate-code`
  - Targeted pytest for changed test files
  - `uv run poe repo-check`
  - `uv run poe check-runtime`
- Success criteria:
  - Read-only subagent review records a verdict for the duplicate groups.
  - Confirmed true duplicates are refactored or removed.
  - Any acceptable test symmetry that still triggers the hard gate is reshaped with narrow helpers while preserving explicit scenario assertions.
  - `uv run poe duplicate-code` passes with the configured 10-line/100-token/0.5% threshold.
  - Targeted tests and repository/runtime checks pass from the current worktree.
- Out of scope:
  - Adding duplicate-code to the default `check` lane.
  - Changing jscpd thresholds.
  - Refactoring production code.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The evaluator must compare the post-change jscpd output with the original 9 findings, confirm no duplicate-code gate failure remains, and verify changed tests still pass.
- Acceptance artifact location: This plan.
- How the generator and evaluator agreed on done before execution:
  - The generator will make narrowly scoped test/helper edits only after the subagent verdicts are synthesized.
- Checks the evaluator will use:
  - `uv run poe duplicate-code`
  - targeted `uv run pytest ...`
  - `uv run poe repo-check`
  - `uv run poe check-runtime`
- Auto-fail conditions:
  - jscpd still reports a threshold failure.
  - A changed test fails.
  - Production code is changed without a new approval record.
  - The default check lane is changed in this slice.

## Generator Work Log

- Planned slice order:
  - Capture fresh jscpd failure evidence.
  - Collect subagent verdicts for the duplicate groups.
  - Extract small test helpers for shared fakes and repeated setup.
  - Remove exact redundant tests where the duplicate carries no separate assertion value.
  - Run duplicate-code and repo checks.
- Notes:
  - Initial `uv run poe duplicate-code` failed with 9 clones and 0.68% duplicated lines over the 0.5% threshold.
  - Subagent verdict synthesis:
    - True duplicates: shared runtime `MutableSeries`, shared CCXT fake client, duplicate parameter-study/WFA fixture strategy setup, duplicate CCXT source entrypoint setup, dormant stop-order activation setup, and one exact duplicate monthly timeframe test.
    - Acceptable test symmetry but still reshaped for the hard gate: rejection activation ceremony and the shared stop-market gap-below sell row fixture.
    - Acceptable and not directly changed beyond support extraction: public-result versus execution-semantics assertions remain separate.
  - Generator changes:
    - Added `tests/support_indicator_runtime.py`, `tests/support_ccxt.py`, and `tests/integration/research/support_parameter_studies.py`.
    - Moved repeated test doubles/fixtures into those support modules and updated import sites.
    - Removed the exact duplicate monthly timeframe test in `tests/unit/data/adapters/test_ccxt_source.py`.
    - Added narrow helpers for order activation/rejection setup and CCXT-backed backtest entrypoint setup.
    - Added `stop_market_gap_below_sell_rows()` to keep the shared scenario row fixture explicit.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocking findings. The post-change duplicate-code gate reports zero clones, and the changed tests still pass.
- Verification evidence:
  - `uv run poe duplicate-code`: passed, 183 Python files, 26,916 total lines, 0 clones, 0 duplicated lines, 0 duplicated tokens.
  - Targeted pytest for changed duplicate groups and dependent import sites: passed, 93 passed, 1 pre-existing dependency warning from `requests`.
  - `uv run ruff check .`: passed.
  - `uv run poe repo-check`: passed.
  - `uv run poe check-runtime`: passed, including 813 passed, 4 skipped, 1 warning; coverage total 92%; build/twine/repo/notebook/perf checks passed.
  - `uv run poe check`: passed, including 813 passed, 4 skipped, 1 warning; coverage total 92%; build/twine/repo/notebook checks passed.
- Final disposition:
  - Complete. The current 9 jscpd findings were reviewed, true duplicates were remediated, hard-gate output is clean with zero clones, and the repository checks passed.
