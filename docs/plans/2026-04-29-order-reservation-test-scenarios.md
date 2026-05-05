# Active Plan

- Date: `2026-04-29`
- Task: `Write the order reservation test scenario planning artifact`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki (thread user)`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Produce a pre-implementation test scenario planning artifact for the
    conservative order reservation policy.
  - Translate the product intent from
    [order-reservation.md](../product-specs/order-reservation.md) into a broad,
    behavior-first test matrix before runtime implementation begins.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
  - `docs/references/testing.md`
  - `docs/product-specs/order-reservation.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - `docs/design-docs/backtest-execution-semantics.md`
- Why these are governing:
  - They define the repo workflow, Tier A handling, test taxonomy, existing
    percent-sizing behavior, planned stop-family behavior, runtime order
    boundaries, and backtest execution semantics.
- Supporting external references:
  - `https://abseil.io/resources/swe-book/html/ch12.html`
  - `https://testing.googleblog.com/2014/04/testing-on-toilet-test-behaviors-not.html`
  - `https://martinfowler.com/articles/practical-test-pyramid.html`
  - `https://docs.pytest.org/en/stable/example/parametrize.html`
  - `https://pytest.org/en/6.2.x/fixture.html`
  - `https://testing.googleblog.com/2024/04/prefer-narrow-assertions-in-unit-tests.html`
- Why these references matter:
  - They support behavior-focused tests, DAMP readability over excessive DRY
    indirection, many focused unit tests plus fewer broader tests, explicit
    pytest fixtures and parametrization, and narrow assertions that verify the
    relevant contract.
- In-repo scope:
  - Add this pre-implementation test scenario planning artifact.
  - Add a related-doc pointer from `order-reservation.md`.
  - Keep the artifact outside `docs/product-specs/` so executable tests can
    become the scenario-level source of truth after implementation.
  - Update this active plan with evaluator review and verification evidence.
- Out-of-repo scope:
  - Read-only web search for testing best practices, explicitly requested by
    the user in this thread.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: `Naki (thread user)`
  - Human approver: `Naki (thread user)`
  - Verification marker:
    explicit thread request on `2026-04-29` to web-search testing best
    practices, reread the order reservation spec, and write a concrete test
    scenario spec before runtime test implementation.
  - Granted scope:
    docs-only order-reservation testing-spec work plus task-limited read-only
    web research.
  - Expiration:
    end of this `2026-04-29` testing-spec slice.
  - Audit reference:
    this active plan.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The artifact treats tests as durable behavior contracts rather than
    implementation probes.
  - The artifact covers unit, integration, structure, and canonical regression
    lanes.
  - The scenario matrix covers all four order types, buy and sell side,
    percent and explicit quantity differences, reservation on accept, dormant
    stop behavior, trigger-time non-recalculation, same-cycle competition,
    sequential reservations, fees and slippage, rounding, no-short behavior,
    partial fills, and deferred lifecycle-release boundaries.
  - The artifact is concrete enough that a later implementation plan can turn
    each scenario into failing tests without reopening coverage design.
  - `uv run poe repo-check` passes after the document update.
- Out of scope:
  - Writing test code.
  - Implementing the reservation ledger.
  - Changing runtime behavior.
  - Expanding into live venues, margin, leverage, shorts, cancel/replace, or
    `check_on_trigger`.

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close only after the scenario artifact protects the product intent rather
    than private implementation mechanics, and after fresh repo-doc
    verification passes.
- Acceptance artifact location:
  - `docs/plans/2026-04-29-order-reservation-test-scenarios.md`
- How the generator and evaluator agreed on done before execution:
  - The document must let a future TDD implementation author know what to test,
    where to place it, which user-visible behavior each test protects, and
    which anti-patterns would make the suite brittle.
- Checks the evaluator will use:
  - Compare against `docs/product-specs/order-reservation.md`.
  - Compare against `docs/product-specs/order-sizing.md`.
  - Compare against `docs/product-specs/stop-limit.md`.
  - Compare against `docs/references/testing.md`.
  - Compare against external best-practice findings.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - only documenting happy-path tests
  - asserting private reservation-ledger internals instead of observable
    resource contracts
  - omitting `qty_percent + stop_market` or `qty_percent + stop_limit`
  - treating stop orders as a separate sizing primitive
  - allowing trigger-time percent recalculation
  - changing production code in this docs-only slice

## Generator Work Log

- Planned slice order:
  1. Reread the order reservation, order sizing, stop-limit, lifecycle, and
     backtest execution docs.
  2. Web-search current testing best practices.
  3. Write the order-reservation test scenario planning artifact.
  4. Add a related-doc pointer from the governing product spec.
  5. Run repo checks.
  6. Record evaluator findings and final disposition.
- Notes:
  - This slice intentionally produces a test-design contract before any test
    or implementation code.
  - The artifact is a planning surface. Once corresponding tests exist under
    `tests/`, those executable tests become the scenario-level source of truth.
  - External research supports the user's stated principles:
    - Google's testing guidance emphasizes behavior-focused tests rather than
      one test per method.
    - Google's software engineering book argues that test readability often
      matters more than eliminating every duplicate setup line.
    - Fowler's test pyramid supports a broad base of focused lower-level tests
      with fewer broader integration and high-level regression tests.
    - Pytest documentation supports explicit fixtures and parametrization for
      repeatable scenario matrices.
    - Google Testing Blog's narrow-assertion guidance supports checking the
      specific observable contract each test exists to protect.
- Blockers or scope changes:
  - None.

## Test Scenario Planning Artifact

This section is the concrete pre-implementation scenario catalog for the later
TDD implementation plan. It is not a long-lived product spec; once
corresponding tests exist under `tests/`, those executable tests become the
scenario-level source of truth.

## Purpose

The tests for conservative order reservation should be treated as durable
product assets. They should encode the user-facing contract:

> if the engine accepts an order, the resources needed for that order are no
> longer available to later competing orders.

The target behavior is intentionally simple:

- `qty_percent` is strategy/request syntax only.
- `market`, `limit`, `stop_market`, and `stop_limit` all accept
  `qty_percent`.
- Percent sizing resolves to concrete quantity before runtime order creation.
- Stop-family orders inherit the sizing semantics of the child order they
  become after trigger.
- Accepted orders reserve cash or position immediately.
- Dormant stop-family orders are reserved but not executable.
- Triggering a stop-family order does not recalculate percent sizing.

Tests should make that intent hard to regress while allowing implementation
details to change. A future implementation may choose a reservation ledger
object, account-control service, or runtime state extension. Tests should fail
when the observable resource and execution contract changes, not when a private
helper is renamed.

## External Testing Practice Evidence

The testing strategy follows these external best-practice findings:

- Google's Software Engineering book recommends tests that are clear and
  maintainable, with DAMP readability favored over excessive DRY indirection in
  test code.
- Google Testing Blog recommends testing behaviors rather than methods, because
  one behavior can span multiple methods and one method can expose multiple
  behaviors.
- Fowler's practical test pyramid supports many focused unit tests, fewer
  integration tests, and very few broad end-to-end or canonical regression
  tests.
- Pytest documentation supports explicit fixtures and parametrization for
  repeatable, readable scenario matrices.
- Google Testing Blog's narrow assertion guidance supports assertions that
  check the relevant behavior rather than broad snapshots of unrelated state.

External references:

- [Software Engineering at Google: Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html)
- [Google Testing Blog: Test Behaviors, Not Methods](https://testing.googleblog.com/2014/04/testing-on-toilet-test-behaviors-not.html)
- [Martin Fowler: The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Pytest parametrizing tests](https://docs.pytest.org/en/stable/example/parametrize.html)
- [Pytest fixtures](https://pytest.org/en/6.2.x/fixture.html)
- [Google Testing Blog: Prefer Narrow Assertions](https://testing.googleblog.com/2024/04/prefer-narrow-assertions-in-unit-tests.html)

## Good Test Code For This Slice

Good tests should:

- test behavior and public or domain contracts, not private helper structure
- use deterministic prices, cash, position quantities, fees, and timestamps
- make the resource basis, price anchor, resolved quantity, reservation, and
  final outcome easy to inspect
- keep one main behavioral claim per test
- use small explicit fixtures close to the tests that need them
- use parametrization for true matrices, but split cases when a parameter table
  would hide the story
- assert narrow outcomes such as resolved quantity, accepted order count,
  final cash, final position, trade log, or visible order state
- include adversarial paths, not only the expected happy path
- keep unit tests fast enough for default verification
- use canonical fixture regression only for high-value end-to-end confidence

Bad tests include:

- one oversized integration test that tries to prove the whole feature
- tests that assert the exact private shape of a reservation ledger
- tests that inspect `Order.__dict__` rather than public/domain attributes
- brittle mocks that only verify that a helper was called
- generated parameter tables whose names do not explain the behavior
- snapshot-style assertions over the entire runtime state when a narrow
  quantity, cash, position, or fill assertion would prove the contract
- tests that pass only because current helpers happen to run in a specific
  private order not promised by the product spec

## Test Placement

Use the repo taxonomy from [testing.md](../references/testing.md):

- `tests/unit/backtest/`
  - sizing resolver behavior
  - activation-time reservation behavior
  - order-state/account-control behavior
  - trigger-time non-recalculation at the smallest stable public/domain seam
- `tests/unit/trading/`
  - runtime order remains quantity-based
  - matching consumes concrete quantity, trigger facts, and limit facts only
  - tests construct concrete `Order` or `OrderIntent` objects, never raw
    `qty_percent` requests
  - `Order.apply_fill()` and remaining-quantity behavior can be tested here,
    but reservation accounting belongs to the runtime/account-control seam
- `tests/integration/research/`
  - full strategy-to-backtest behavior through `BacktestEngine`
  - public strategy API cases for `qty_percent` across all four order types
  - trade log, final state, and active-order behavior
- `tests/structure/architecture/` or `tests/structure/docs/`
  - architectural guardrails such as no raw `qty_percent` on runtime `Order`
  - doc routing and policy relationship checks when needed
- `tests/perf/`
  - only if reservation tracking creates measurable runtime risk
- `tests/smoke/live/`
  - out of scope for this MVP policy document

## Core Scenario Matrix

Each scenario id is intentionally behavior-oriented. Test names should preserve
the same idea even if implementation modules change.

### A. Strategy API And Validation

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| A1 | unit/research | `buy(quantity=1.0)` remains accepted for `market`, `limit`, `stop_market`, and `stop_limit` when required prices are present | fixed quantity requests still work |
| A2 | unit/research | `buy(qty_percent=50)` is accepted for `market`, `limit`, `stop_market`, and `stop_limit` when required prices are present | percent syntax is uniform across all four order types |
| A3 | unit/research | `sell(qty_percent=50)` is accepted for `market`, `limit`, `stop_market`, and `stop_limit` when required prices are present | exits have the same percent surface as entries |
| A4 | unit/research | request provides both `quantity` and `qty_percent` | raise validation error before runtime order creation |
| A5 | unit/research | request provides neither `quantity` nor `qty_percent` | raise validation error before runtime order creation |
| A6 | unit/research | `qty_percent <= 0` | raise validation error as non-tradable sizing input |
| A7 | unit/research | `qty_percent > 100` in the MVP long-only cash/position-percent surface | raise validation error unless a later spec explicitly expands percent semantics |
| A8 | unit/research | `stop_market` without `stop_price` | raise validation error before runtime order creation |
| A9 | unit/research | `stop_limit` without `stop_price` or without `limit_price` | raise validation error before runtime order creation |
| A10 | unit/research | `limit` without `limit_price` | raise validation error before runtime order creation |

### B. Quantity Boundary

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| B1 | unit/trading or structure | runtime `Order` has concrete `quantity` and no raw `qty_percent` field | strategy percent syntax does not leak into the trading kernel |
| B2 | unit/backtest | percent market request activates into one concrete `Order` before matching | matching never receives raw percent |
| B3 | unit/backtest | percent limit request activates into one concrete `Order` before matching | `limit_price` plus concrete quantity reach the order book |
| B4 | unit/backtest | percent stop-market request activates into one concrete dormant `Order` before trigger | dormant stop-market quantity is knowable before trigger |
| B5 | unit/backtest | percent stop-limit request activates into one concrete dormant `Order` before trigger | dormant stop-limit quantity is knowable before trigger |
| B6 | integration/research | public `BacktestEngine` run emits fills with concrete quantities only | result contracts never expose raw percent sizing as execution quantity |

### C. Buy-Side Price Anchors

Use simple zero-fee cases first, then fee/slippage cases.

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| C1 | unit/backtest | cash `100`, next executable buy reference `10`, `buy(qty_percent=50, market)` | quantity `5.0`; reservation based on market anchor |
| C1a | unit/backtest | cash `100`, market buy reference `10`, one slippage tick of `1`, `buy(qty_percent=50, market)` | affordability uses `11`, not `10` |
| C2 | unit/backtest | cash `100`, `buy(qty_percent=50, limit_price=20)` | quantity `2.5`; reservation based on `limit_price`, not current optimistic mark |
| C3 | unit/backtest | cash `100`, `buy(qty_percent=50, stop_market, stop_price=25)` | quantity `2.0`; reservation based on `stop_price` plus modeled slippage |
| C4 | unit/backtest | cash `100`, `buy(qty_percent=50, stop_limit, stop_price=25, limit_price=20)` | quantity `2.5`; stop price does not affect size |
| C5 | unit/backtest | `stop_limit` has `stop_price=25`, `limit_price=30` | quantity uses `limit_price=30` even when stop is lower |
| C6 | unit/backtest | `stop_market` with one slippage tick and tick size `1` at stop `25` | affordability uses `26`, not `25` |
| C7 | integration/research | same four buy-side percent orders in one engine run with independent tags | each accepted order quantity matches its order-type anchor |

### D. Buy-Side Fee, Rounding, And Affordability

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| D1 | unit/backtest | `qty_percent=100` market buy where budget plus fee is unaffordable | percent resolver clamps only enough to afford modeled costs |
| D2 | unit/backtest | `qty_percent=50` market buy where budget plus fee is affordable | requested position budget is preserved exactly |
| D3 | unit/backtest | `qty_percent=100` stop-market buy with fee and slippage | clamp is based on stop-market anchor plus costs |
| D4 | unit/backtest | `qty_percent=100` stop-limit buy with fee | clamp is based on limit price plus costs |
| D4a | unit/backtest | `qty_percent=100` ordinary limit buy where limit-price budget plus fee is unaffordable | clamp is based on limit price plus costs |
| D5 | unit/backtest | final resolved quantity rounds below tradable minimum | request emits explicit `OrderRejected`-style event with stable reason |
| D6 | unit/backtest | rounding down leaves affordable residue cash | residue remains available for later orders |
| D7 | unit/backtest | explicit `quantity` buy exceeds available cash | do not silently resize; emit explicit rejection event |
| D8 | integration/research | percent and explicit over-budget requests appear in same strategy | percent may clamp, explicit over-budget does not become a smaller order |

### E. Sell-Side Position Basis

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| E1 | unit/backtest | position `10`, `sell(qty_percent=50, market)` | quantity `5.0`; reserve `5.0` position |
| E2 | unit/backtest | position `10`, `sell(qty_percent=50, limit)` | quantity `5.0`; limit price does not change sell quantity |
| E3 | unit/backtest | position `10`, `sell(qty_percent=50, stop_market)` | quantity `5.0`; stop price does not change sell quantity |
| E4 | unit/backtest | position `10`, `sell(qty_percent=50, stop_limit)` | quantity `5.0`; stop and limit prices do not change sell quantity |
| E5 | unit/backtest | flat account, `sell(qty_percent=50)` for each order type | no short entry is created |
| E6 | unit/backtest | existing reserved sell quantity `4`, position `10`, new `sell(qty_percent=50)` | quantity `3.0`, based on unreserved closable `6` |
| E7 | integration/research | entry fills, then two percent exits are accepted before either fills | total reserved exits never exceed current long position |

### F. Reservation On Accept

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| F1 | unit/backtest | accepted market buy reserves cash immediately | later buy percent basis excludes the reservation |
| F2 | unit/backtest | accepted limit buy reserves cash immediately even before fill | later buy percent basis excludes the reservation |
| F3 | unit/backtest | dormant stop-market buy reserves cash immediately before trigger | later buy percent basis excludes the reservation |
| F4 | unit/backtest | dormant stop-limit buy reserves cash immediately before trigger | later buy percent basis excludes the reservation |
| F5 | unit/backtest | accepted market sell reserves position immediately | later sell percent basis excludes the reservation |
| F6 | unit/backtest | accepted limit sell reserves position immediately before fill | later sell percent basis excludes the reservation |
| F7 | unit/backtest | dormant stop-market sell reserves position immediately before trigger | later sell percent basis excludes the reservation |
| F8 | unit/backtest | dormant stop-limit sell reserves position immediately before trigger | later sell percent basis excludes the reservation |

### G. Same-Cycle And Sequential Competition

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| G1 | unit/backtest | two same-cycle `buy(qty_percent=50, market)` requests, cash `100`, anchor `10` | quantities `(5.0, 2.5)` |
| G2 | unit/backtest | `stop_market` buy `qty_percent=50` followed by market buy `qty_percent=50` in same activation cycle | second order sizes from remaining unreserved cash |
| G3 | unit/backtest | `stop_limit` buy `qty_percent=50` followed by limit buy `qty_percent=50` in same activation cycle | no double use of cash |
| G4 | unit/backtest | market buy accepted, then stop-limit buy accepted later before first fills | second order uses reserved-adjusted cash |
| G5 | unit/backtest | two same-cycle `sell(qty_percent=50)` requests with position `10` | quantities `(5.0, 2.5)` |
| G6 | unit/backtest | dormant stop-market exit followed by ordinary limit exit | ordinary exit sizes from unreserved position |
| G7 | unit/backtest | dormant stop-limit exit followed by ordinary market exit | ordinary exit sizes from unreserved position |
| G8 | integration/research | mixed entry orders across all four order types in one strategy | total cash reservation never exceeds modeled available cash |
| G9 | integration/research | mixed exit orders across all four order types in one strategy | total position reservation never exceeds closable position |
| G10 | unit/backtest | explicit limit buy quantity reserves cash before later `buy(qty_percent=50)` in the same activation cycle | percent order sizes from cash remaining after the explicit reservation |
| G11 | unit/backtest | `buy(qty_percent=50)` reserves cash before later explicit buy quantity in the same activation cycle | explicit order is accepted only if the remaining unreserved cash can support it |
| G12 | unit/backtest | explicit sell quantity reserves position before later `sell(qty_percent=50)` in the same activation cycle | percent order sizes from position remaining after the explicit reservation |
| G13 | unit/backtest | `sell(qty_percent=50)` reserves position before later explicit sell quantity in the same activation cycle | explicit order is accepted only if the remaining unreserved position can support it |

### H. Dormant Stop Execution Boundary

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| H1 | integration/research | dormant stop-market buy reserves cash but trigger is not reached | no fill; later buy budget is still reduced |
| H2 | integration/research | dormant stop-limit buy reserves cash but trigger is not reached | no fill; later buy budget is still reduced |
| H3 | integration/research | dormant stop-market sell reserves position but trigger is not reached | no fill; later sell quantity is still reduced |
| H4 | integration/research | dormant stop-limit sell reserves position but trigger is not reached | no fill; later sell quantity is still reduced |
| H5 | unit/trading or integration | limit price crosses before stop-limit trigger | no fill before trigger |
| H6 | unit/trading or integration | stop-market trigger occurs | order becomes market-executable using its fixed quantity |
| H7 | unit/trading or integration | stop-limit trigger occurs | order becomes limit-executable using its fixed quantity and limit price |
| H8 | integration/research | existing executable buy order and newly triggered buy stop-family order are both marketable at the same event | existing executable order is processed before the newly triggered order |
| H9 | integration/research | existing executable sell order and newly triggered sell stop-family order are both marketable at the same event | existing executable order is processed before the newly triggered order |

### I. Trigger-Time Non-Recalculation

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| I1 | integration/research | stop-market buy `qty_percent=50` accepted at cash `100`, later cash changes before trigger | fill uses original fixed quantity |
| I2 | integration/research | stop-limit buy accepted, later cash is consumed by fills or fees before trigger | no percent recalculation occurs |
| I3 | integration/research | stop-market sell accepted against position `10`, later position changes before trigger through unrelated fills | order quantity remains fixed; later overcommitment should have been prevented by reservation |
| I4 | integration/research | stop-limit sell accepted, later exit orders attempt to consume same position | later orders cannot reserve already reserved quantity |
| I5 | unit/backtest | trigger-time executable price differs materially from activation anchor | quantity remains activation-time quantity |
| I6 | unit/backtest | stop-market buy triggers through a gap above stop | quantity remains based on stop price plus modeled slippage, not gap open |
| I7 | unit/backtest | stop-limit buy triggers through a gap above stop and remains unfilled because open is beyond limit | reservation remains associated with the fixed-quantity order |
| I8 | integration/research | triggered-but-unfilled stop-limit buy remains open, then a later buy percent request is emitted | later request sizes from cash excluding the still-open stop-limit reservation |
| I9 | integration/research | triggered-but-unfilled stop-limit sell remains open, then a later sell percent request is emitted | later request sizes from position excluding the still-open stop-limit reservation |

### J. Fill, Partial Fill, And Reservation Shrink

Partial fills may be internal-first before they are user-facing. These tests
should be written at the smallest stable seam that can model finite liquidity.
Trading-level tests may prove fill application and remaining quantity, but
reservation shrink belongs to the runtime/account-control seam, not
`quantleet.trading.domain.Order`.

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| J0 | unit/trading | concrete order quantity `10`, partial fill `4` | runtime order reports remaining quantity `6` without owning reservation accounting |
| J1 | unit/backtest | full fill consumes entire buy reservation | no remaining reservation for the filled order |
| J2 | unit/backtest | full fill consumes entire sell reservation | no remaining reserved position for the filled order |
| J3 | unit/backtest | buy order quantity `10`, partial fill `4` | remaining reservation shrinks to unresolved `6` |
| J4 | unit/backtest | sell order quantity `10`, partial fill `4` | remaining reserved position shrinks to unresolved `6` |
| J5 | unit/backtest | partial fill then later percent buy | later basis excludes only unresolved buy reservation plus actual cash effects |
| J6 | unit/backtest | partial fill then later percent sell | later basis excludes unresolved sell reservation and accounts for current position |
| J7 | integration/research | triggered stop-limit partially fills and remains open | reservation follows remaining quantity under same order id |
| J8 | unit/backtest | buy limit reserves quantity `10` at limit `100`, partially fills `4` at gap-open price `95` | remaining reservation covers unresolved quantity `6` at the order anchor, and price-improvement residue is available |

### K. Rejection And Validation Paths

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| K1 | unit/backtest | percent buy after all cash is reserved | emit explicit rejection event with stable reason |
| K2 | unit/backtest | percent sell after all position is reserved | emit explicit rejection event with stable reason |
| K3 | unit/backtest | explicit buy quantity exceeds unreserved cash | emit explicit rejection event; no silent downsize |
| K4 | unit/backtest | explicit sell quantity exceeds unreserved position in long-only workflow | emit explicit rejection event; no short is opened |
| K5 | unit/backtest | stop order request would be valid syntactically but resulting percent quantity rounds to zero | emit explicit rejection event; no order is accepted |
| K6 | integration/research | rejected path does not create a phantom reservation | later valid request can use resources that were never accepted |

### L. Order Identity And Reporting

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| L1 | unit/backtest | accepted order receives an id and reservation is keyed consistently to that id or equivalent public identity | reservation follows the same order through trigger/fill |
| L2 | integration/research | dormant stop later triggers and fills | trade log uses the original fixed quantity and user tag |
| L3 | integration/research | stop-limit triggers but remains open | public result surface does not report a fill |
| L4 | integration/research | two orders with different tags compete for cash | accepted/fill outcomes remain attributable to the intended order |
| L5 | integration/research | rejection due to reservation exhaustion | public result records rejection and does not invent a zero-quantity fill |

### M. Canonical Regression Scenarios

Canonical regression tests should be few. They protect high-value behavior
across the complete strategy/backtest path.

| ID | Lane | Scenario | Expected Contract |
| --- | --- | --- | --- |
| M1 | integration/research | small synthetic strategy uses percent market, limit, stop-market, and stop-limit entries over deterministic bars | final trade log and final state match the fixed contract |
| M2 | integration/research | small synthetic strategy enters once, then places competing percent exits across all four order types | final position never goes negative and fills are deterministic |
| M3 | integration/research | canonical BTC fixture with percent stop-market entries and exits | summary digest protects real-data behavior without overspecifying internals |
| M4 | integration/research | canonical BTC fixture with percent stop-limit entries and exits | summary digest protects real-data stop-limit reservation behavior |
| M5 | integration/research | source-based run path and direct bars path for the same reservation scenario | both entrypoints produce the same result contract |

## Concrete Starter Scenarios

These are intentionally small and arithmetic-friendly. They should be converted
first because they catch the highest-risk misunderstandings.

### S1. Buy stop-market percent reserves on accept

Setup:

- cash `100`
- no position
- current activation context has stop anchor `20`
- zero fee and zero slippage

Action:

```python
self.buy(qty_percent=50, order_type="stop_market", stop_price=20)
self.buy(qty_percent=50, order_type="market")
```

Expected:

- first accepted order quantity is `2.5`
- first order is dormant and has no fill before trigger
- first order reserves `50` cash
- second accepted order sizes from remaining `50` cash
- second order quantity is `2.5` when market anchor is `10`

### S2. Buy stop-limit percent uses limit price, not stop price

Setup:

- cash `100`
- zero fee and zero slippage
- `stop_price=25`
- `limit_price=20`

Action:

```python
self.buy(qty_percent=50, order_type="stop_limit", stop_price=25, limit_price=20)
```

Expected:

- accepted order quantity is `2.5`
- cash reservation is based on `limit_price=20`
- changing `stop_price` to `30` does not change quantity when the trigger
  direction remains valid

### S3. Sell stop-market percent reserves position on accept

Setup:

- position quantity `10`
- no existing sell reservations

Action:

```python
self.sell(qty_percent=50, order_type="stop_market", stop_price=95)
self.sell(qty_percent=50, order_type="market")
```

Expected:

- first accepted order quantity is `5`
- first order is dormant and has no fill before trigger
- second accepted order sizes from unreserved position `5`
- second order quantity is `2.5`

### S4. Stop trigger does not recalculate percent

Setup:

- cash `100`
- stop-market buy accepted with `qty_percent=50` and `stop_price=20`
- accepted quantity is `2.5`
- before trigger, later activity changes visible cash or price

Action:

- trigger the stop at a later bar where executable price is not `20`

Expected:

- fill quantity remains `2.5`
- no trigger-time portfolio snapshot is used to recompute size
- any fill failure is due to normal execution rules, not percent sizing

### S5. Explicit over-budget quantity is not clamped

Setup:

- cash `100`
- market anchor `10`
- explicit buy quantity `20`

Action:

```python
self.buy(quantity=20, order_type="market")
```

Expected:

- request emits an explicit rejection event with a stable reason
- it does not become quantity `10`
- no reservation is created for a rejected request

### S6. Percent over-budget may clamp only as percent sizing

Setup:

- cash `100`
- market anchor `10`
- fee rate makes `qty_percent=100` unaffordable at exactly quantity `10`

Action:

```python
self.buy(qty_percent=100, order_type="market")
```

Expected:

- request may resolve to a smaller affordable quantity
- the behavior is documented as percent affordability clamping
- the test does not imply explicit fixed-quantity requests may be resized

## Coverage Priorities

The first implementation test plan should prioritize:

1. API validation and quantity boundary tests.
2. Buy-side anchor tests for all four order types.
3. Ordinary market/limit fee and slippage tests, not only stop-family cost tests.
4. Sell-side reservation tests for all four order types.
5. Same-cycle competition across percent and explicit quantity orders.
6. Dormant stop reservation and same-event priority tests.
7. Trigger-time non-recalculation tests.
8. Partial-fill reservation shrink tests if the implementation slice touches
   finite-liquidity or partial-fill paths.
9. Canonical regression tests after focused unit and integration behavior is
   stable.

## Implementation Decisions Before Planning

The human-intent questions for this scenario catalog are closed:

1. Invalid order shape and invalid strategy request input raise validation
   errors at the earliest boundary. Runtime account or market failures emit an
   explicit rejection event with a stable reason. Silent no-order behavior is
   out of policy.
2. A triggered buy `stop_market` attempts execution at the modeled executable
   price from the OHLC path, including gap and slippage effects. Quantity is
   not recalculated. If the account cannot afford the actual execution cost
   with the order reservation plus currently unreserved cash, the order is
   rejected, no fill is created, negative cash is not allowed, and the
   reservation is released.
3. Reservation accounting, available-balance checks, rejection decisions, and
   release behavior belong to the runtime/account-control layer. Domain
   `Order` remains responsible for order invariants only.

Do not start with canonical fixture digests. They are useful as late regression
guards, but they are too broad to diagnose the first implementation failures.

## Future-Lane Notes

The following should remain out of the MVP default lane:

- live venue reservation behavior
- margin, leverage, and short-side reservations
- `check_on_trigger`
- cancel, replace, amend, and expire flows
- OCO, OTO, bracket, trailing, reduce-only, post-only, or time-in-force

When those features become product scope, they need separate scenario planning.
They should not be smuggled into this MVP reservation test matrix.

## Evaluator Review

- Findings:
  - No remaining auto-fixable findings for this documentation slice after
    subagent review follow-up. The artifact covers the order-reservation policy
    as a behavior contract, includes all four order types and both sides,
    separates unit/integration/structure/canonical lanes, and avoids requiring
    private reservation-ledger shape.
  - Human-intent questions remain recorded in the dedicated section before
    implementation planning.
- Verification evidence:
  - `uv run poe repo-check`: `repository checks passed`.
  - After subagent review follow-up, `uv run poe repo-check`: `repository
    checks passed`.
- Final disposition:
  - Accepted for the pre-implementation order-reservation test scenario
    planning slice; implementation planning is blocked on the recorded
    human-intent questions.
