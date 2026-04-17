# Active Plan

- Date: `2026-04-18`
- Task: `Promote the approved real-data limit strategies into canonical integration regression tests`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - add durable real-data limit-order regression coverage that mirrors the existing canonical market-strategy contracts
  - keep the default integration lane small, legible, and grounded in the approved three-strategy limit set
  - ensure the new regressions run through the public `BacktestEngine` surface on the checked-in BTC USD-M 1h 2025 fixture
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-14-limit-strategy-regression-design.md`
  - `docs/plans/2026-04-17-real-strategy-cross-validation-rerun.md`
- Why these are governing:
  - they define the current backtest and strategy surface, the approved real-data limit regression set, the current execution semantics, and the repository workflow/verification policy
- In-repo scope:
  - extend `tests/support_backtest.py` with canonical helpers for the approved limit strategies
  - add canonical integration regression contracts under `tests/integration/research/`
  - keep the tests on the checked-in BTC USD-M 1h 2025 fixture and the public backtest surface
  - update repo docs only if a directly relevant pointer becomes stale
- Out-of-repo scope:
  - changing backtest engine semantics
  - new datasets
  - comparator harnesses under `/tmp`
  - committing or staging changes without a later user request
- Tier A progression requested: `no`
- Approval record, if required:
  - None. This slice is limited to Tier B regression-test promotion work in `research` and test support code.
- Verification commands:
  - `uv run pytest tests/integration/research/test_canonical_limit_entry_contract.py tests/integration/research/test_canonical_limit_exit_contract.py tests/integration/research/test_canonical_limit_mixed_contract.py -q`
  - `uv run pytest tests/integration/research -q`
  - `uv run poe verify`
  - `uv run poe verify-runtime`
- Success criteria:
  - the approved three-strategy limit set is represented by durable integration contracts on the checked-in BTC USD-M 1h 2025 fixture
  - each contract pins summary values, leading/trailing fill samples, and a trade-log digest in the same style as the existing canonical market regressions
  - the tests run through the public `BacktestEngine` path and normal `Strategy.init()` / `on_bar()` semantics
  - the default verification and runtime-sensitive verification lanes pass from the current worktree
- Out of scope:
  - performance-gate changes
  - expanding beyond the approved three-strategy limit set
  - changes to `src/quantcraft/*` unless a fresh failing test proves a supporting bug in current code

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - done means the approved three-strategy limit regression set exists as durable integration contracts with fresh red/green evidence and passes the repository verification lanes
- Acceptance artifact location:
  - `docs/plans/2026-04-18-limit-strategy-regression-promotion.md`
- How the generator and evaluator agreed on done before execution:
  - the generator may only add the minimal canonical helpers and contract tests needed to lock the approved limit set; the evaluator will reject gratuitous refactors or scope creep into engine semantics unless a failing regression forces it
- Checks the evaluator will use:
  - red/green evidence from the new canonical limit tests
  - diff review against the approved design doc and existing canonical market-test pattern
  - fresh `uv run poe verify`
  - fresh `uv run poe verify-runtime`
- Auto-fail conditions:
  - the new tests depend on ad hoc comparator harnesses or external data
  - the approved three-strategy set is only partially represented
  - the tests bypass the public backtest surface
  - verification is partial, stale, or skipped

## Generator Work Log

- Planned slice order:
  - add failing canonical limit contracts first
  - implement the minimal helper and strategy support in `tests/support_backtest.py`
  - rebaseline expected outputs from the current verified worktree
  - run focused tests, then full repo verification
- Notes:
  - single writer only; delegated work is read-only evidence gathering
  - no git staging is allowed in this slice without a later user request
- Blockers or scope changes:
  - 2026-04-18: the canonical limit regressions were implemented on the repo-native `Strategy` + `ta` surface rather than by copying the temporary cross-engine harnesses; this matches the existing canonical market-test pattern and keeps the regression lane inside the public library surface
  - 2026-04-18: the supporting docs fully froze the three strategy families but did not explicitly freeze the EMA/Bollinger numeric parameters for strategies 1 and 3; the regression implementation made those values explicit as `EMA(20)` and `BB(20, 2)` to match the earlier approved experiment harnesses and keep the canonical lane deterministic

## Evaluator Review

- Findings:
  - Added the approved real-data limit strategy set as durable canonical integration contracts:
    - `EMA Pullback Buy-Limit With Market Exit`
    - `Market Entry With Take-Profit Sell-Limit Exit`
    - `Bollinger Lower-Band Buy-Limit With Middle-Band Sell-Limit`
  - The new regressions mirror the existing canonical market-order pattern exactly:
    - strategy and runner helpers live in `tests/support_backtest.py`
    - each strategy has one focused contract file under `tests/integration/research/`
    - each contract pins the full `BacktestSummary`, `ExposureSummary`, first fills, last fills, and trade-log digest
  - The new strategies run through the public `BacktestEngine` plus normal `Strategy.init()` / `on_bar()` flow on the checked-in BTC USD-M 1h 2025 fixture.
  - No production code under `src/quantcraft/*` was changed for this slice.
  - The repo-native strategy implementations now freeze the previously approved limit-regression families inside the canonical test surface; this closes the prior gap where real-data regressions existed only for market-order strategies.
  - Residual risk:
    - the approval docs named the strategy families but did not explicitly codify `EMA(20)` and `BB(20, 2)` before this implementation; the tests now freeze those parameters implicitly through the canonical helpers and snapshots
- Verification evidence:
  - Red phase:
    - `uv run pytest tests/integration/research/test_canonical_limit_entry_contract.py tests/integration/research/test_canonical_limit_exit_contract.py tests/integration/research/test_canonical_limit_mixed_contract.py -q`
    - result before helper implementation: `3 errors during collection`
    - failure mode: missing canonical limit helper imports in `tests/support_backtest.py`
  - Green phase for the new contracts:
    - `uv run pytest tests/integration/research/test_canonical_limit_entry_contract.py tests/integration/research/test_canonical_limit_exit_contract.py tests/integration/research/test_canonical_limit_mixed_contract.py -q`
    - result: `3 passed`
  - Fresh research integration sweep:
    - `uv run pytest tests/integration/research -q`
    - result: `31 passed`
  - Fresh repo-local verification:
    - `uv run poe verify`
    - result: `311 passed, 3 skipped`; coverage policy passed at `92%`; `ruff`, `mypy`, `uv build`, `repo_check.py`, and notebook validation all passed
    - `uv run poe verify-runtime`
    - result: `311 passed, 3 skipped`; runtime lane, coverage, packaging, repo check, notebook validation, and perf check all passed
    - runtime perf evidence:
      - `pytest tests/perf/test_rsi_backtest_benchmark.py -q -x --run-perf`
      - result within `verify-runtime`: `2 passed`
- Final disposition:
  - `accepted`
