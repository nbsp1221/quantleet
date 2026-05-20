# Trading Mutation Test Hardening Plan

- Date: 2026-05-20
- Task: Strengthen trading unit tests using mutation-testing survivor evidence.
- Status: `complete`
- Risk class: `Tier A`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Improve the `trading` unit test suite so it detects materially
  relevant mutations in position accounting, sizing, and reservation logic,
  while preserving the current production behavior and architecture boundary.
- Governing docs:
  - `AGENTS.md`
  - `ARCHITECTURE.md`
  - `docs/PLANS.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/product-specs/order-reservation.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/references/testing.md`
- Why these are governing:
  - `AGENTS.md` requires planner/generator/evaluator workflow and Tier A
    approval records.
  - `ARCHITECTURE.md` identifies `trading` as the shared trading kernel and a
    Tier A context.
  - `docs/PLANS.md` defines active plan location and plan authority.
  - `docs/RELIABILITY.md` defines local verification, mutation-command
    placement, and Tier A safety expectations.
  - `docs/SECURITY.md` requires explicit human approval for Tier A work.
  - `docs/DESIGN.md`, `docs/design-docs/index.md`, and
    `docs/design-docs/package-topology-and-naming.md` route package-boundary
    and architecture constraints.
  - `docs/product-specs/backtest-mvp.md` defines the current trading kernel
    role, long-only spot-like accounting, fill state outputs, and cost inputs.
  - `docs/product-specs/order-sizing.md` defines percent-sizing semantics,
    fee-aware affordability, price anchors, rounding, and fixed-quantity
    behavior.
  - `docs/product-specs/order-reservation.md` defines conservative
    reserve-on-accept behavior for active and dormant orders.
  - `docs/product-specs/stop-limit.md` defines stop-family lifecycle and
    stop-limit price-anchor semantics.
  - `docs/references/testing.md` defines test placement and command-lane
    policy, including the manual `mutation-trading` audit command.
- In-repo scope:
  - Add or strengthen unit tests under `tests/unit/trading/`.
  - Target these existing production modules without changing their behavior:
    - `src/quantleet/trading/domain/state.py`
    - `src/quantleet/trading/sizing.py`
    - `src/quantleet/trading/order_requests.py`
    - optionally `src/quantleet/trading/domain/matching.py` if earlier
      survivor clusters are resolved cleanly.
  - Use `uv run poe mutation-trading` as the before/after evidence command.
  - Classify remaining survivors into real gaps, equivalent/noisy mutants, or
    deferred lower-priority gaps after the first hardening pass.
- Out-of-repo scope:
  - No CI workflow change.
  - No default `check` integration for mutation testing.
  - No web-service, broker, exchange, or live trading integration.
  - No production code behavior change unless a test exposes a genuine defect
    and the user approves a separate fix slice.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: user
  - Human approver: user
  - Check marker: `uv run poe mutation-trading`
  - Granted scope: add focused unit tests for existing `trading` behavior using
    mutation survivor evidence; do not change production trading behavior in
    this slice without separate approval
  - Expiration: this task slice
  - Audit reference: user request on 2026-05-20 to plan mutation-score
    improvement for `trading`
- Verification commands:
  - `uv run pytest tests/unit/trading -q`
  - `uv run poe mutation-trading`
  - `uv run poe repo-check`
  - Optional if production code changes become necessary after separate
    approval: `uv run poe check`
- Success criteria:
  - New tests are focused on real product contracts rather than asserting
    implementation trivia only to chase the score.
  - `uv run pytest tests/unit/trading -q` passes.
  - `uv run poe mutation-trading` completes successfully.
  - Trading mutation score improves from the current baseline:
    - baseline: `450` killed / `571` total = `78.8%`
    - target for this first hardening pass: at least `80.0%`
    - stretch target: reduce survivors from `121` to `100` or fewer
  - Any remaining equivalent/noisy survivors are explicitly listed with a
    short rationale before any `# pragma: no mutate` is proposed.
  - `uv run poe repo-check` passes.
- Out of scope:
  - Enforcing mutation score as a CI or default `check` hard gate.
  - Rewriting the sizing or state model.
  - Adding broad integration tests when focused unit tests can kill the same
    mutants faster and more clearly.
  - Marking survivors as ignored before adding tests for the highest-risk
    accounting, sizing, and reservation gaps.

## Current Mutation Evidence

Fresh `uv run poe mutation-trading` evidence before this hardening plan:

- Mutated files: `10`
- Total mutants: `571`
- Killed: `450`
- Survived: `121`
- Timeout: `0`
- Score: `78.8%`
- Speed: `67.29 mutations/second`

Survivors by module:

| Module | Killed | Survived | Total | Score |
| --- | ---: | ---: | ---: | ---: |
| `quantleet.trading.domain.intents` | 5 | 0 | 5 | 100.0% |
| `quantleet.trading.domain.matching` | 104 | 8 | 112 | 92.9% |
| `quantleet.trading.domain.state` | 68 | 26 | 94 | 72.3% |
| `quantleet.trading.order_requests` | 3 | 2 | 5 | 60.0% |
| `quantleet.trading.sizing` | 270 | 85 | 355 | 76.1% |

Worst survivor clusters:

| Function | Survivors | Total | Current score | Risk |
| --- | ---: | ---: | ---: | --- |
| `apply_fill` | 26 | 94 | 72.3% | PnL, equity, cash, position state |
| `_resolve_quantity_request` | 20 | 71 | 71.8% | fixed quantity affordability and reservation |
| `_resolve_buy_percent_request` | 17 | 83 | 79.5% | percent sizing, fee clamp, budget invariants |
| `_active_buy_cash_reservation` | 9 | 32 | 71.9% | active buy cash reservation |
| `_buy_anchor_price` | 9 | 24 | 62.5% | market/limit/stop-family buy anchors |
| `_resolve_sell_percent_request` | 8 | 34 | 76.5% | net closable quantity and sell reservations |
| `_active_sell_quantity` | 5 | 13 | 61.5% | active exit reservation |
| `_maximum_affordable_position_budget` | 5 | 15 | 66.7% | fee-aware affordability |

## Planned Test Hardening Slices

### Slice 1: `apply_fill` Accounting State Transitions

Owner file: `tests/unit/trading/test_matching_and_state.py`

Add focused tests for:

- adding to an existing long at a different price updates weighted
  `average_entry_price`
- buy fills use `mark_price`, not only fill price, for `unrealized_pnl` and
  `equity`
- partial sell at profit leaves remaining quantity, preserves average entry,
  accumulates realized PnL, and recalculates unrealized PnL using remaining
  quantity greater than `1`
- partial sell at loss records negative realized PnL and keeps state
  spot-like/long-only
- multiple sells accumulate realized PnL rather than replacing it
- full close resets `position_quantity`, `average_entry_price`, and
  `unrealized_pnl` while preserving realized PnL and cash
- buy and sell fees affect cash/equity exactly but do not incorrectly enter
  realized PnL in the current contract

Mutation intent:

- Kill arithmetic operator mutants in unrealized PnL and equity.
- Kill branch mutants around full close and remaining-position behavior.
- Kill accumulator mutants in realized PnL.
- Leave only precision-equivalent rounding mutants for later triage if they
  remain.

### Slice 2: Fixed-Quantity Sizing Contract Tests

Owner file: `tests/unit/trading/test_sizing.py`

Add focused tests for explicit `quantity` requests:

- successful fixed market buy asserts `quantity`, `position_budget`,
  `cash_consumption`, and zero sell reservation
- fixed buy with fee and slippage uses the conservative market anchor and
  fee-aware cash consumption
- successful fixed limit or stop-limit buy uses `limit_price` as the anchor
  and does not resize quantity
- fixed stop-market buy uses `stop_price + slippage` as the anchor
- fixed buy fails below `min_cost` only after affordability is satisfied, with
  stable `below_minimum_cost` reason
- fixed buy respects active buy orders and manual `SizingReservations.buy_cash`
- successful fixed sell asserts `sell_quantity_reservation == quantity`
- fixed sell respects active sell orders and manual
  `SizingReservations.sell_quantity`
- fixed sell rejects when net closable quantity is fully reserved
- fixed requests round down to `quantity_increment` before affordability and
  reservation decisions

Mutation intent:

- Kill comparison/sign mutants in cash and position availability.
- Kill missing active-order or manual-reservation subtraction mutants.
- Kill budget/cash-consumption arithmetic mutants.
- Kill explicit buy/sell reservation-field omissions.

### Slice 3: Percent Sizing Invariant Tests

Owner file: `tests/unit/trading/test_sizing.py`

Strengthen existing percent tests by asserting the whole result contract:

- affordable buy percent preserves requested position budget and asserts
  `position_budget` plus `cash_consumption`
- 100% buy with fees clamps only enough to stay affordable and asserts exact
  cash consumption
- active buy reservations with fees/slippage reduce the basis before applying
  `qty_percent`
- manual `SizingReservations.buy_cash` reduces the buy basis and serial
  reservations use resolved rounded budget
- percent buy below `min_cost` returns `below_minimum_cost`
- fully reserved cash returns `no_buy_budget_available`
- sell percent asserts `sell_quantity_reservation == quantity`
- sell percent respects manual sell reservations and fully reserved position
  returns `no_closable_position`
- exact 100% sell of net closable quantity reserves exactly that net quantity
- sub-minimum rounded sell returns `below_minimum_size`

Mutation intent:

- Kill `or`/`and` mutants in size and minimum checks.
- Kill fee-clamp and maximum-affordable-budget arithmetic mutants.
- Kill active/manual reservation basis mutants.
- Kill missing sell reservation result mutants.

### Slice 4: Active Reservation And Price-Anchor Matrix

Owner file: `tests/unit/trading/test_sizing.py`

Add compact table-style tests for active orders:

- active market buy reserves remaining quantity at `market_buy_price +
  slippage`
- active limit buy reserves at `limit_price`
- dormant stop-market buy reserves at `trigger_price + slippage`
- dormant stop-limit buy reserves at `limit_price`
- triggered stop-limit buy continues to reserve at `limit_price`
- partially filled active buy reserves only `remaining_quantity`
- closed or fully filled buy orders do not reduce new buy basis
- active sell orders reduce net closable quantity by remaining quantity
- non-open sell orders do not reduce net closable quantity
- buy reservations ignore sell orders and sell reservations ignore buy orders

Mutation intent:

- Kill `_active_buy_cash_reservation`, `_active_sell_quantity`,
  `_buy_anchor_price`, and `_order_buy_anchor_price` survivors.
- Exercise stop-family reservation policy without adding slow integration
  tests.

### Slice 5: Pending Request Validation Gaps

Owner file: `tests/unit/trading/test_contracts.py`

Add small validation tests for:

- exactly one of `quantity` and `qty_percent` must be provided
- both sizing modes provided is rejected
- neither sizing mode provided is rejected
- non-positive and non-finite `qty_percent` is rejected
- `qty_percent > 100` is rejected if current contract enforces the public
  percent range
- bool-like numeric values are rejected if current validation treats bool as
  invalid numeric input
- stop-family requests require stop price and trigger condition where
  appropriate
- limit and stop-limit requests require limit price where appropriate

Mutation intent:

- Kill the two `order_requests` survivors if they are real validation gaps.
- Keep this slice small because it will not move the score as much as state and
  sizing tests.

### Slice 6: Remaining Survivor Triage

After slices 1-5, rerun:

```bash
uv run poe mutation-trading
```

Then classify remaining survivors:

- `real gap`: add another focused test in the owning unit file
- `equivalent`: record exact mutant and rationale
- `unreachable defensive branch`: record constructor/type-contract reason
- `low-value precision mutant`: consider `# pragma: no mutate` only after
  documenting why public behavior is intentionally unchanged

No survivor should be ignored merely to reach a numeric score.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Tests must improve behavioral
  accountability for trading accounting, sizing, and reservation contracts; the
  mutation score should improve for real reasons, not from excluding high-risk
  code.
- Acceptance artifact location: this plan's Evaluator Review section.
- How the generator and evaluator agreed on done before execution: The planner
  contract fixes target modules, test-only scope, baseline mutation evidence,
  priority slices, verification commands, and out-of-scope production changes.
- Checks the evaluator will use:
  - `uv run pytest tests/unit/trading -q`
  - `uv run poe mutation-trading`
  - `uv run poe repo-check`
  - Diff review against this plan
- Auto-fail conditions:
  - Production trading behavior changes without a separate approved fix slice.
  - Mutation score improves only because high-risk code was excluded or muted.
  - New tests assert private implementation trivia without tying back to a
    product contract or financial invariant.
  - `uv run pytest tests/unit/trading -q` fails.
  - `uv run poe mutation-trading` cannot complete.
  - `uv run poe repo-check` fails.

## Generator Work Log

- Completed slice order:
  - Slice 1: Added `apply_fill` state-transition tests for weighted average
    entry, mark-to-market unrealized PnL, exact-cash buy affordability,
    partial realized PnL accumulation, loss-making sells, and full close reset.
  - Slice 2: Added fixed-quantity sizing contract tests for market, limit,
    stop-market, and stop-limit buy anchors; fixed buy affordability and
    reservation behavior; and fixed sell net-closable reservation behavior.
  - Slice 3: Strengthened percent sizing invariant tests for requested budget,
    fee-aware cash consumption, full-fee affordability clamping, manual
    reservations, no-budget reasons, sell reservation, and sub-minimum results.
  - Slice 4: Added active reservation and price-anchor matrix tests for open,
    closed, partially filled, stop-family, buy-side, and sell-side orders.
  - Slice 5: Added pending request validation tests for mutually exclusive
    sizing modes, invalid numeric inputs, and invalid price-shape contracts.
  - Slice 6: Reran mutation testing and triaged remaining survivors.
- Notes:
  - All changes are test-only, scoped to `tests/unit/trading/`.
  - No production `trading` behavior was changed and no mutant was muted.
  - The new tests stay deterministic and unit-local; no integration or live
    checks were added.
- Blockers or scope changes:
  - None.

## Post-Run Mutation Evidence

Fresh `uv run poe mutation-trading` evidence after the hardening pass:

- Mutated files: `10`
- Total mutants: `610`
- Killed: `527`
- Survived: `83`
- Timeout: `0`
- Score: `86.4%`
- Speed: `22.43 mutations/second`

The total mutant count increased from `571` to `610` because new tests caused
mutmut to discover additional covered code paths. The meaningful comparison is
still favorable: killed mutants increased from `450` to `527`, survivors fell
from `121` to `83`, and score improved from `78.8%` to `86.4%`.

Survivors by module:

| Module | Killed | Survived | Total | Score |
| --- | ---: | ---: | ---: | ---: |
| `quantleet.trading.domain.intents` | 5 | 0 | 5 | 100.0% |
| `quantleet.trading.domain.matching` | 104 | 8 | 112 | 92.9% |
| `quantleet.trading.domain.state` | 76 | 18 | 94 | 80.9% |
| `quantleet.trading.order_requests` | 5 | 0 | 5 | 100.0% |
| `quantleet.trading.sizing` | 337 | 57 | 394 | 85.5% |

Survivors by remaining function cluster:

| Function | Survivors | Total | Score | Triage |
| --- | ---: | ---: | ---: | --- |
| `apply_fill` | 18 | 94 | 80.9% | Mixed: remaining real state-edge gaps plus precision/message mutants |
| `_resolve_quantity_request` | 12 | 87 | 86.2% | Deferred real fixed-sizing boundary gaps |
| `_resolve_buy_percent_request` | 10 | 93 | 89.2% | Deferred real percent-sizing boundary gaps plus precision mutants |
| `_active_buy_cash_reservation` | 6 | 33 | 81.8% | Deferred active-order ordering and reservation-matrix gaps |
| `_buy_anchor_price` | 6 | 24 | 75.0% | Mostly unreachable defensive branches and precision mutants |
| `_order_buy_anchor_price` | 6 | 22 | 72.7% | Mostly runtime-order defensive branches and precision mutants |
| `_resolve_sell_percent_request` | 5 | 39 | 87.2% | Deferred sell percent boundary gaps |
| `match_order` | 4 | 63 | 93.7% | Lower-priority matching edge and fee precision mutants |
| `_maximum_affordable_position_budget` | 4 | 15 | 73.3% | Deferred fee-aware affordability edge gaps |
| `_round_down_to_increment` | 4 | 13 | 69.2% | Deferred zero/increment boundary gaps |
| `_active_sell_quantity` | 3 | 13 | 76.9% | Deferred active sell ordering gaps |
| `_match_notional` | 2 | 29 | 93.1% | Lower-priority notional trigger edge gaps |
| `is_order_triggered` | 2 | 15 | 86.7% | Lower-priority trigger boundary gaps |
| `_cash_consumption_for_budget` | 1 | 7 | 85.7% | Low-count fee arithmetic edge gap |

Remaining equivalent/noisy survivors explicitly triaged:

- `quantleet.trading.domain.state.x_apply_fill__mutmut_4`,
  `__mutmut_14`, and `__mutmut_28` mutate exception message text. Current tests
  assert stable public error classes and meaningful substrings, not exact full
  messages. These are low-value message mutants, not financial behavior gaps.
- `quantleet.trading.domain.state.x_apply_fill__mutmut_47` changes
  `next_quantity > 0.0` to `next_quantity >= 0.0` for unrealized PnL. At
  `next_quantity == 0.0`, both branches produce `0.0`, so this is equivalent
  for the current long-only arithmetic contract.
- `quantleet.trading.domain.state.x_apply_fill__mutmut_69`,
  `quantleet.trading.sizing.x__buy_anchor_price__mutmut_6`, and
  `quantleet.trading.domain.matching.x_match_order__mutmut_46` change rounding
  precision by one decimal place or to whole-number rounding in fixtures where
  the public result remains unchanged. These are precision-contract candidates,
  not immediate evidence of a trading logic bug.
- `_buy_anchor_price` and `_order_buy_anchor_price` survivors that raise for
  missing `stop_price` or `limit_price` are mostly unreachable through valid
  `PendingOrderRequest` and `Order` construction. They should remain documented
  until a separate defensive-validation decision is made.

Remaining real or deferred survivor groups:

- `_resolve_quantity_request` still has comparison/order-of-check survivors
  around rounded quantity, minimum size, affordability, and reservation
  boundaries. These are valid next hardening targets.
- `_resolve_buy_percent_request`, `_maximum_affordable_position_budget`, and
  `_cash_consumption_for_budget` still have fee-aware budget and final
  affordability edge survivors. These matter for finance-grade sizing and
  should be the next focused slice if the mutation score is raised again.
- `_active_buy_cash_reservation`, `_active_sell_quantity`, and
  `_resolve_sell_percent_request` still have active-order ordering and
  reservation-matrix survivors. These are real enough to keep visible, but this
  pass already reduced the larger reservation gap without adding broad
  integration tests.
- `matching` survivors remain lower priority for this pass because the module
  already scores `92.9%`; they should be handled after sizing/state edges unless
  a matching behavior change is planned.

No `# pragma: no mutate` is proposed in this slice.

## Evaluator Review

- Findings:
  - No blocking findings after parent diff review and review fan-out.
  - The change is test-only and does not alter Tier A production behavior.
  - Added assertions check cash, equity, average entry, realized PnL,
    unrealized PnL, fee-aware affordability, price anchors, and active
    reservations. These are product contracts and financial invariants, not
    incidental implementation details.
  - Remaining survivors are visible and triaged. The unresolved real groups
    are deferred intentionally rather than hidden with mutation pragmas.
- Verification evidence:
  - `uv run pytest tests/unit/trading -q`:
    `130 passed in 0.25s`
  - `uv run ruff format --check tests/unit/trading/test_matching_and_state.py tests/unit/trading/test_sizing.py tests/unit/trading/test_contracts.py`:
    `3 files already formatted`
  - `uv run ruff check tests/unit/trading/test_matching_and_state.py tests/unit/trading/test_sizing.py tests/unit/trading/test_contracts.py`:
    `All checks passed!`
  - `uv run poe mutation-trading`:
    `527` killed / `610` total, `83` survived, `86.4%`, no timeouts
  - `uv run poe repo-check`:
    `repository checks passed`
  - `uv run poe check`:
    format, lint, mypy, full pytest/coverage, build, twine check,
    repo-check, and notebook validation passed; full pytest result was
    `802 passed, 4 skipped, 1 warning in 103.50s`
  - The full check raised `.coverage-baseline.json` from `90.758392%` to
    `91.276419%`, matching the stronger trading test coverage added here.
  - Review fan-out:
    `Wegener` approved, `Linnaeus` approved, `Ohm` initially blocked on
    missing post-run survivor classification and evaluator evidence; after
    this evaluator artifact update, `Ohm` re-reviewed and approved.
- Final disposition:
  - Accepted.
