# Active Plan

- Date: `2026-04-27`
- Task: `Promote standalone stop_market validation strategies into canonical integration tests`
- Status: `active`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - add durable repo-native integration tests for the three validated
    standalone stop-market strategy patterns
  - lock the public `BacktestEngine` behavior on the checked-in BTC USD-M 1h
    2025 fixture without copying the external cross-validation harness
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
  - `docs/plans/2026-04-26-stop-market-standalone-cross-validation.md`
- Why these are governing:
  - They define the current public backtest/research surface, the standalone
    stop-market scope, the validated strategy set, and the repository workflow
    for runtime-sensitive backtest tests.
- In-repo scope:
  - extend `tests/support_backtest.py` with canonical stop-market strategy
    helpers and deterministic signal construction
  - add three `tests/integration/research/test_canonical_stop_market_*`
    contract files
  - apply a mechanical line-wrap lint fix in an existing stop-market unit test
    if required for repository verification
  - complete this active plan with evaluator findings and fresh verification
- Out-of-repo scope:
  - none for implementation
  - read-only reference to the completed `/tmp/quantcraft-stop-xval` result
    artifact is allowed as prior evidence only
- Tier A progression requested: `no`
- Approval record, if required:
  - None. This slice does not change `src/quantcraft/trading` or
    `src/quantcraft/execution`; it promotes validated behavior into
    repo-native integration tests.
- Verification commands:
  - `uv run pytest tests/integration/research/test_canonical_stop_market_opening_range_contract.py tests/integration/research/test_canonical_stop_market_donchian_contract.py tests/integration/research/test_canonical_stop_market_inside_bar_contract.py -q`
  - `uv run pytest tests/integration/research -q`
  - `uv run poe verify`
  - `uv run poe verify-runtime`
  - `uv run poe repo-check`
- Success criteria:
  - all three validated standalone strategies are represented as canonical
    integration contracts:
    - opening range breakout stop entry
    - Donchian / Turtle-style breakout stop entry
    - inside-bar breakout stop entry
  - tests run through public `BacktestEngine` plus normal `Strategy.init()` /
    `on_bar()` order intake
  - tests do not import `backtesting.py`, `backtrader`, `vectorbt`,
    `Nautilus`, pandas, or the `/tmp` harness
  - tests do not model OTO, OCO, brackets, attached stop-loss, attached
    take-profit, or parent-child order activation
  - each contract pins `BacktestSummary`, `ExposureSummary`, first fills, last
    fills, and full trade-log digest in the existing canonical style
- Out of scope:
  - changing production engine semantics
  - adding new datasets
  - adding comparator harness code to the repo
  - implementing `stop_limit`, trailing stop, OTO, OCO, bracket, shorting, or
    attached orders

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - accepted only if the new tests are repo-native public-surface contracts,
    the corrected standalone strategy scope is preserved, and fresh
    verification passes
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - the generator may only add deterministic test support and contract files;
    any production code change or attached-order modeling is an auto-fail
- Checks the evaluator will use:
  - focused red/green evidence for the new contracts
  - diff review against existing canonical strategy test pattern
  - subagent review fan-out for correctness/testing, maintainability, and
    plan/spec conformance
  - fresh repo verification output
- Auto-fail conditions:
  - new tests depend on external comparator libraries or `/tmp` scripts
  - any strategy submits protective stops after entry or requires parent-child
    lifecycle semantics
  - tests bypass the public `BacktestEngine` path
  - runtime-sensitive verification is skipped

## Generator Work Log

- Planned slice order:
  1. add failing canonical stop-market contract imports/tests
  2. add minimal deterministic helper and strategy support in
     `tests/support_backtest.py`
  3. rebaseline expected summaries, fill samples, and digests from the current
     verified engine behavior
  4. run focused tests and integration sweep
  5. run review fan-out and fix material findings
  6. run full verification and complete evaluator review
- Notes:
  - implementation write ownership stays with the parent agent
  - subagents are read-only reviewers/explorers
- Blockers or scope changes:
  - `uv run poe verify` initially failed on a pre-existing long line in
    `tests/unit/trading/test_orders.py`; this slice applied only a mechanical
    line wrap there so repository verification could complete.
  - A read-only conformance review found that the first repo-native helper
    version produced `35/10/34` trades, while the prior standalone
    cross-validation artifact proved `36/11/37`. The helpers were changed to
    reproduce the validated signal definitions with repo-local pure
    calculations and then submit orders through the public `Strategy` API.
    The promoted contracts now assert `36/11/37` trades. PnL differs from
    `/tmp` validation because canonical repo tests use the repo default
    canonical costs while the standalone validation used zero fees and
    slippage.

## Evaluator Review

- Findings:
  - Added three durable BTC USD-M 1h 2025 fixture-backed stop-market canonical
    strategy contracts:
    - opening range breakout stop entry
    - Donchian / Turtle-style breakout stop entry
    - inside-bar breakout stop entry
  - The tests are repo-native public-surface contracts:
    - strategy helpers submit standalone `buy(order_type="stop_market",
      stop_price=...)` entries
    - exits are independent plain `sell(quantity=1.0)` signals
    - contracts run through `BacktestEngine.run(...)`
    - no comparator library, `/tmp` script, OTO, OCO, bracket, attached
      stop-loss, attached take-profit, `stop_limit`, trailing stop, or short
      entry behavior is used
  - Each contract pins the full `BacktestSummary`, `ExposureSummary`, first
    fills, last fills, and full trade-log digest, matching the existing
    canonical market/limit test style.
  - Review fan-out synthesis:
    - correctness/testing review: no findings; verified public `BacktestEngine`
      path and standalone stop-market scope
    - maintainability/performance review: no findings; targeted Ruff and
      focused tests passed, runtime cost is acceptable for default integration
      lane
    - conformance review: initial trade-count divergence was material and was
      fixed; final follow-up found no remaining material issue for this slice
      except this plan needing final evaluator evidence
  - Pre-existing uncommitted production stop-market implementation and docs
    remain outside this plan's ownership; this slice did not add new
    production semantics.
- Verification evidence:
  - Red phase:
    - `uv run pytest tests/integration/research/test_canonical_stop_market_opening_range_contract.py tests/integration/research/test_canonical_stop_market_donchian_contract.py tests/integration/research/test_canonical_stop_market_inside_bar_contract.py -q`
    - Result before helper implementation: `3 errors during collection`
    - Failure mode: missing canonical stop-market helper imports in
      `tests/support_backtest.py`
  - Focused green phase:
    - `uv run pytest tests/integration/research/test_canonical_stop_market_opening_range_contract.py tests/integration/research/test_canonical_stop_market_donchian_contract.py tests/integration/research/test_canonical_stop_market_inside_bar_contract.py -q`
    - Result: `3 passed in 0.90s`
  - Fresh research integration sweep:
    - `uv run pytest tests/integration/research -q`
    - Result: `57 passed in 2.67s`
  - Fresh repo-local verification:
    - `uv run poe verify`
    - Result: passed
    - Evidence within run: Ruff passed; mypy passed for `51` source files;
      pytest `401 passed, 3 skipped`; coverage policy passed at `92%`; build,
      repo check, and notebook validation passed
  - Fresh runtime-sensitive verification:
    - `uv run poe verify-runtime`
    - Result: passed
    - Evidence within run: Ruff passed; mypy passed for `51` source files;
      pytest `401 passed, 3 skipped`; coverage policy passed at `92%`; build,
      repo check, notebook validation, and perf check passed
    - Perf evidence: `pytest tests/perf/test_rsi_backtest_benchmark.py -q -x
      --run-perf` reported `2 passed in 1.14s`
  - Fresh repo/document check:
    - `uv run poe repo-check`
    - Result: `repository checks passed`
- Final disposition:
  - `accepted`
