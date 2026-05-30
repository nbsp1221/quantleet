# Critical And High Mutation Survivor Remediation Plan

- Date: 2026-05-30
- Task: Plan targeted test remediation for critical and high survived mutants in
  the `trading` and `backtest` mutation gate.
- Status: `active - targeted remediation complete; aggregate mutation gate passed`
- Risk class: `Tier A`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Ensure survived mutants classified as `critical` or `high` are killed by
  tests that protect observable financial behavior, instead of treating all
  survived mutants as equal score noise.
- Governing docs:
  - `AGENTS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
  - `docs/design-docs/agentic-quality-gates.md`
  - `docs/plans/2026-05-30-mutation-test-quality-remediation-plan.md`
- Why these are governing: The work touches Tier A `trading` behavior,
  runtime-sensitive `backtest` behavior, the aggregate mutation hard gate, and
  the repository's test placement policy.
- In-repo scope:
  - Add or strengthen tests under `tests/unit/trading`.
  - Add or strengthen tests under `tests/unit/backtest`.
  - Add or strengthen targeted integration tests only when the contract is
    inherently cross-module.
  - Update mutation triage notes or this plan with final survivor evidence.
- Out-of-repo scope:
  - No external services.
  - No live trading, live exchange, or network-backed tests.
  - No CI workflow migration.
  - No production code changes unless a test exposes a real implementation bug
    and the user explicitly approves the fix in a later slice.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: user
  - Human approver: user
  - Check marker: `uv run poe mutation-gates`, `uv run poe check-runtime`,
    and `uv run poe check`
  - Granted scope: planning and future test-only remediation for critical/high
    survived mutants in `trading` and `backtest`.
  - Expiration: this remediation effort
  - Audit reference: user request on 2026-05-30 to classify mutation survivors
    by severity and make critical/high survivors test-detectable.
- Verification commands:
  - Planning-only:
    - `git diff --check`
  - Implementation:
    - `uv run pytest tests/unit/trading tests/unit/backtest -q`
    - `uv run pytest tests/integration/backtest tests/integration/research -q`
      when integration contracts are added or changed
    - `uv run poe mutation-gates`
    - `uv run poe check-runtime`
    - `uv run poe check`
- Success criteria:
  - Every known `critical` survivor listed in this plan is killed by a test or
    reclassified with written evidence.
  - Every known `high` survivor listed in this plan is killed by a test or
    reclassified with written evidence.
  - Tests assert public or domain-observable behavior: cash, position,
    reservation, fill rejection, fee/PnL accounting, order-intent validity, or
    report metrics.
  - Tests do not assert private implementation details only to improve the
    mutation score.
  - Remaining `medium` and `low` survivors are not allowed to hide unresolved
    `critical` or `high` risk.
- Out of scope:
  - Killing every survived mutant in this slice.
  - Adding brittle assertions for equivalent mutants, error-message trivia, or
    plot styling.
  - Lowering the mutation threshold to pass.
  - Changing the hard gate to ignore critical/high survivors.

## Severity Policy

Use this policy when triaging survived mutants:

- `critical`: A mutant can alter cash availability, reserved cash, order
  validity, fill acceptance/rejection, position state, fee allocation, or PnL
  accounting in a way that can create materially wrong financial behavior.
- `high`: A mutant can materially misreport financial performance, risk, final
  portfolio state, or strategy quality, even if it does not directly create an
  invalid order or fill.
- `medium`: A mutant affects financial precision, boundary values, or secondary
  contracts where the expected policy is real but less likely to cause immediate
  severe damage.
- `low`: A mutant affects message text, display-only presentation, plotting
  style, or behavior that is equivalent under the domain contract.

The `critical` and `high` labels are action labels. They require a targeted
test or a documented reclassification before the remediation is considered
complete.

## Current Critical Candidates

These candidates came from local `uv run mutmut results` and representative
`uv run mutmut show <mutant>` inspection after the aggregate gate passed with
remaining survivors.

### Backtest Runtime: Buy Reservation Update After Fill

- Mutant: `quantleet.backtest.runtime.x__process_executable_order__mutmut_60`
- Observed mutation:
  - `_update_buy_reservation_after_fill(..., costs=costs)` becomes
    `_update_buy_reservation_after_fill(..., costs=None)`.
- Reclassification after implementation inspection: `low/equivalent-current-path`.
- Evidence:
  - Current `match_order` fills the whole `order.remaining_quantity`.
  - `_process_executable_order` passes the post-fill order to
    `_update_buy_reservation_after_fill`, so the runtime path reaches
    `order.remaining_quantity <= 0.0` and removes the reservation before the
    cost model is used.
  - Direct targeted mutation execution left this mutant surviving after the
    critical/high remediation tests, confirming that this specific call-site
    mutation is not an observable current-runtime behavior change.
- Required test signal if runtime partial fills are introduced later:
  - A partial buy fill with non-zero costs updates reserved cash using the same
    fee/cost policy as order sizing.
  - The test must fail if the cost model is dropped during reservation update.
- Preferred test layer: `tests/unit/backtest`, with an integration assertion only
  if the behavior requires the full backtest runtime.

### Backtest Runtime: Entry Fee Pool And Closed PnL Accounting

- Mutants:
  - `quantleet.backtest.runtime.x__apply_runtime_fill__mutmut_43`
  - `quantleet.backtest.runtime.x__apply_runtime_fill__mutmut_44`
- Observed mutations:
  - `round(open_entry_fee_pool - allocated_entry_fee, 12)` becomes lower-quality
    rounding or an invalid constant-like rounding expression.
- Risk: Entry fee allocation can corrupt closed-trade net PnL, remaining fee
  pool, and trade statistics during partial exits.
- Required test signal:
  - A partial sell after a fee-bearing entry allocates only the proportional
    entry fee to the closed portion.
  - Remaining open fee pool is preserved for the residual position.
  - Closed-trade net PnL changes if the entry fee pool is rounded incorrectly or
    replaced by a constant.
- Preferred test layer: `tests/unit/backtest`.

### Backtest Strategy Runtime: Invalid Flat Stop Sell Intent

- Mutant:
  - `quantleet.backtest.strategy_runtime.xǁ_StrategyDriverǁactivate_pending_order_intents__mutmut_33`
- Observed mutation:
  - `_is_stop_order_type(request.order_type)` becomes `_is_stop_order_type(None)`.
- Reclassification after implementation inspection: `low/equivalent-current-path`.
- Evidence:
  - Flat fixed-quantity sell requests are rejected by sizing before this guard
    can create an order.
  - Flat percent sell requests are also rejected by sizing before this guard.
  - The existing `test_flat_sell_stop_limit_resolves_to_no_new_order` already
    asserts the public behavior for a flat stop-limit sell.
  - Direct targeted mutation execution left this mutant surviving, which is
    consistent with the guard being redundant under the current sizing contract.
- Required test signal if sizing later permits flat sell sizing to reach this
  guard:
  - A stop sell intent while flat is rejected or omitted according to the public
    strategy-runtime contract.
  - A valid stop sell while a position exists remains allowed.
- Preferred test layer: `tests/unit/backtest`.

### Trading Sizing: Active Buy Reservation Price Removal

- Mutant:
  - `quantleet.trading.sizing.x__resolve_quantity_request__mutmut_67`
- Observed mutation:
  - `_active_buy_cash_reservation(..., market_buy_price=market_buy_price)`
    becomes `_active_buy_cash_reservation(..., market_buy_price=None)`.
- Risk: Active buy reservations can be undercounted or mispriced, weakening the
  overspend guard for new buy sizing requests.
- Required test signal:
  - Existing market buy reservations consume cash using the supplied market buy
    price.
  - A new buy request that would overspend after active reservations is rejected
    or reduced according to the sizing contract.
  - The test fails if `market_buy_price` is ignored.
- Preferred test layer: `tests/unit/trading`.

## Current High Candidates

### Backtest Runtime: Fill Rejection Cash Guard

- Mutants:
  - `quantleet.backtest.runtime.x__runtime_fill_rejection__mutmut_6`
  - `quantleet.backtest.runtime.x__runtime_fill_rejection__mutmut_21`
  - `quantleet.backtest.runtime.x__runtime_fill_rejection__mutmut_27`
- Observed mutations:
  - Required cash rounding changes.
  - Reservation fallback behavior changes.
  - Available-for-order precision changes.
- Risk: The runtime can accept or reject a buy fill with the wrong cash
  availability calculation.
- Required test signal:
  - A buy fill just above available cash is rejected.
  - A buy fill covered by its reservation plus unreserved cash is accepted.
  - The boundary includes non-zero fees.
- Preferred test layer: `tests/unit/backtest`.

### Trading Sizing: Zero Quantity Buy Boundary

- Mutant:
  - `quantleet.trading.sizing.x__resolve_buy_percent_request__mutmut_67`
- Observed mutation:
  - `quantity <= 0.0` becomes `quantity < 0.0`.
- Risk: A zero-quantity buy can pass a sizing boundary when minimum quantity is
  zero or not strict enough.
- Required test signal:
  - A buy-percent request that resolves to zero quantity is rejected or produces
    the documented no-op outcome.
  - The test fails if zero quantity is treated as valid executable size.
- Preferred test layer: `tests/unit/trading`.

### Backtest Reporting: Final Cash Contract

- Mutant:
  - `quantleet.backtest.reporting.xǁ_ReportBuilderǁbuild__mutmut_158`
- Observed mutation:
  - `final_cash=final_state.cash` becomes `final_cash=None`.
- Risk: The final portfolio state can be reported with missing cash while tests
  still pass.
- Required test signal:
  - A built backtest report includes exact final cash from the final state.
  - The report contract rejects or exposes `None` final cash as invalid.
- Preferred test layer: `tests/unit/backtest`.

### Backtest Reporting: Profit Factor Contract

- Mutant:
  - `quantleet.backtest.reporting.x__trade_metrics__mutmut_37`
- Observed mutation:
  - `profit_factor = round(gross_profit / gross_loss, 12)` becomes rounding to
    integer precision.
- Risk: Strategy quality can be materially misreported.
- Required test signal:
  - Profit factor preserves fractional precision for mixed win/loss closed
    trades.
  - The assertion uses a precise expected value, not only non-null or positive
    existence.
- Preferred test layer: `tests/unit/backtest`.

### Backtest Reporting: Closed Trade Sell Economics

- Survivor group:
  - `quantleet.backtest.reporting.xǁ_ReportBuilderǁ_record_sell`
- Observed risk from sampled survivors:
  - Closed-trade fees, net PnL, net return, and sell-side attribution can be
    mutated without enough local assertions.
- Risk: Closed trade economics can be wrong while aggregate smoke-style report
  tests still pass.
- Required test signal:
  - A sell that closes a known position records gross PnL, allocated entry fee,
    exit fee, total fees, net PnL, and net return.
  - At least one test uses values that produce non-integer fractional metrics.
- Preferred test layer: `tests/unit/backtest`.

### Trading State: Fill Application Accounting

- Survivor group:
  - `quantleet.trading.domain.state.x_apply_fill`
- Observed risk from sampled survivors:
  - Realized PnL, unrealized PnL, average entry price, and equity preservation
    are not fully pinned by local tests.
- Risk: The trading state can drift while order/fill paths still execute.
- Required test signal:
  - Buy, partial sell, full sell, and mark-to-market paths assert position
    quantity, cash, average entry price, realized PnL, unrealized PnL, and
    equity.
  - The tests include fee-bearing fills.
- Preferred test layer: `tests/unit/trading`.

## Proposed Slice Order

1. Runtime cash and reservation invariants.
   - Target `_runtime_fill_rejection`, `_process_executable_order`, and active
     buy reservation sizing.
   - Rationale: These are the closest paths to invalid order or fill behavior.

2. Runtime fee and PnL accounting invariants.
   - Target `_apply_runtime_fill` and `apply_fill`.
   - Rationale: Fee allocation and realized/unrealized PnL errors directly
     affect financial correctness.

3. Strategy order-intent validity.
   - Target flat-position stop sell behavior in
     `StrategyDriver.activate_pending_order_intents`.
   - Rationale: Invalid exits should be rejected before they become runtime
     artifacts.

4. Reporting financial contracts.
   - Target final cash, profit factor, and closed-trade sell economics.
   - Rationale: Reporting does not execute orders, but it is the user-facing
     basis for strategy and risk decisions.

5. Reclassification pass.
   - Re-run `uv run mutmut results`.
   - For any remaining survivor in the listed critical/high groups, either add
     a contract test or reclassify with written evidence.

## Test Design Rules

- Assert business outcomes, not internal call structure.
- Prefer exact expected values when the formula is deterministic.
- Include non-zero fees and fractional values so integer rounding mutants do not
  survive by accident.
- Include boundary values around zero cash, zero quantity, exact affordability,
  and just-over-affordability.
- Keep tests deterministic and cheap enough for the default mutation lane.
- Do not add broad snapshot assertions as the only proof for financial metrics.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The plan lists current critical/high candidates and describes the contract
    each candidate must be tested against.
  - The plan separates mutation-score improvement from financial-risk
    remediation.
  - The plan defines which checks must pass after implementation.
- Acceptance artifact location:
  - `docs/plans/2026-05-30-critical-high-mutation-survivor-remediation.md`
- How the generator and evaluator agreed on done before execution:
  - The user asked to create a concrete plan document for making critical/high
    mutation survivors test-detectable.
- Checks the evaluator will use:
  - `git diff --check`
  - Implementation follow-up: `uv run poe mutation-gates`,
    `uv run poe check-runtime`, and `uv run poe check`
- Auto-fail conditions:
  - The plan recommends lowering or bypassing the mutation gate.
  - The plan treats critical/high survivors as acceptable score noise.
  - The plan proposes brittle implementation-detail assertions instead of
    observable financial contracts.

## Generator Work Log

- Planned slice order:
  - Author the remediation plan.
  - Review the plan against the current survivor evidence.
  - Add targeted observable contract tests for true critical/high candidates.
  - Reclassify equivalent-current-path candidates with evidence.
- Notes:
  - This plan is intentionally narrower than full survivor cleanup.
  - Medium and low survivors remain useful, but they must not distract from
    unresolved critical/high mutants.
  - Implementation added tests for runtime fill-rejection cash precision,
    runtime fee-pool/PnL accounting, explicit buy reservation pricing,
    zero-quantity buy percent sizing, final cash reporting, and fractional
    profit factor reporting.
  - Targeted mutation execution killed:
    - `quantleet.backtest.runtime.x__runtime_fill_rejection__mutmut_6`
    - `quantleet.backtest.runtime.x__runtime_fill_rejection__mutmut_21`
    - `quantleet.backtest.runtime.x__runtime_fill_rejection__mutmut_27`
    - `quantleet.backtest.runtime.x__apply_runtime_fill__mutmut_43`
    - `quantleet.backtest.runtime.x__apply_runtime_fill__mutmut_44`
    - `quantleet.trading.sizing.x__resolve_quantity_request__mutmut_67`
    - `quantleet.trading.sizing.x__resolve_buy_percent_request__mutmut_67`
    - `quantleet.backtest.reporting.xǁ_ReportBuilderǁbuild__mutmut_158`
    - `quantleet.backtest.reporting.x__trade_metrics__mutmut_37`
  - Targeted mutation execution still left the two reclassified
    equivalent-current-path mutants alive:
    - `quantleet.backtest.runtime.x__process_executable_order__mutmut_60`
    - `quantleet.backtest.strategy_runtime.xǁ_StrategyDriverǁactivate_pending_order_intents__mutmut_33`
- Reclassification evidence:
  - `quantleet.backtest.runtime.x__process_executable_order__mutmut_60`
    changes the `costs` argument passed into
    `_update_buy_reservation_after_fill`. In the current runtime,
    `match_order` fills the full remaining order quantity or returns `None`;
    it does not create partial fills. `_update_buy_reservation_after_fill`
    only needs `costs` when the post-fill buy order remains open. That branch
    is therefore unreachable through `_process_executable_order` today. The
    underlying partial-fill reservation contract is still tested directly in
    `tests/unit/backtest/test_runtime_accounting.py`.
  - `quantleet.backtest.strategy_runtime.xǁ_StrategyDriverǁactivate_pending_order_intents__mutmut_33`
    disables the explicit flat-position stop-sell guard. In the current sizing
    contract, flat sell requests already resolve to no-op before that guard:
    explicit-quantity sells fail with `insufficient_position`, and
    percent-based sells fail with `no_closable_position`. The flat stop-limit
    behavior is covered in
    `tests/unit/backtest/test_order_sizing_activation.py`.
- Blockers or scope changes:
  - Two initially critical-looking mutants were reclassified from
    `critical/high` to equivalent-current-path after targeted mutation execution
    and source-path review.
  - Earlier full aggregate mutation-gate attempts hit mutmut generated-cache
    errors after interrupted or overlapping runs. After killing stale mutmut
    processes and rebuilding the generated `mutants/` tree, the aggregate gate
    completed and produced valid score evidence.

## Evaluator Review

- Findings:
  - Removed direct `_rejection_reason` helper assertions from
    `tests/unit/backtest/test_order_sizing_activation.py` because they asserted
    implementation details instead of observable financial behavior.
  - No remaining true `critical` or `high` candidate from this plan is both
    reachable and survived in targeted mutation execution.
  - The direct business-contract tests killed the cash-boundary, fee/PnL,
    sizing, final-cash, and profit-factor candidates.
  - Two survivors remain, but both are defensibly equivalent under the current
    execution and sizing contracts. They should stay documented rather than be
    killed with brittle monkeypatch tests.
- Verification evidence:
  - `uv run pytest tests/unit/backtest/test_runtime_accounting.py tests/unit/backtest/test_order_sizing_activation.py tests/unit/backtest/test_result_reporting_metrics.py tests/unit/trading/test_sizing.py -q`
    passed: `76 passed in 0.16s`.
  - `uv run pytest tests/unit/trading tests/unit/backtest -q` passed:
    `245 passed in 2.79s`.
  - Targeted mutation command:
    `uv run mutmut run <9 true critical/high candidate names> --max-children 4`
    reported killed status for all nine true critical/high candidates.
  - Reclassification validation command:
    `uv run mutmut run <2 reclassified candidate names> --max-children 4`
    reported survived status for both equivalent-current-path candidates, as
    expected under the current runtime and sizing contracts.
  - After cleaning stale mutmut state, `uv run poe mutation-gates` passed:
    `mutation score: total=2945 killed=2392 survived=547 no_tests=0 suspicious=0 timeout=0 segfault=0 score=81.22% threshold=80%`.
  - `uv run poe check-runtime` passed. Key evidence from the stronger lane:
    format/lint/dead-code/duplicate/dependency/typecheck passed; full pytest
    passed `836 passed, 4 skipped, 1 warning in 53.58s`; coverage baseline
    passed with `current=92.453600%`; aggregate mutation score passed with
    `score=81.36% threshold=80%`; build, twine check, repo check, notebook
    validation, and perf checks passed.
  - `git diff --check` passed after the final plan update.
- Final disposition:
  - Targeted critical/high remediation accepted.
  - Aggregate mutation score gate accepted at the current 80% threshold.
  - Runtime-sensitive stronger lane accepted.
  - Remaining survived mutants are outside this slice and should be handled by
    future severity-ranked remediation rather than by lowering the threshold.
