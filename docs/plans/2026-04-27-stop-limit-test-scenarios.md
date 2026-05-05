# Active Plan

- Date: `2026-04-27`
- Task: `Write the stop-limit test scenario planning artifact`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki (thread user)`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Produce a pre-implementation test scenario planning artifact for the planned
    `stop_limit` implementation before test or production code is written.
  - Translate the stop-limit product intent into a broad, maintainable
    behavior-first test matrix across unit, integration, and canonical
    regression lanes.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
  - `docs/references/testing.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/plans/2026-04-23-stop-trigger-order-test-matrix-design.md`
- Why these are governing:
  - They define repo workflow, Tier A handling, test taxonomy, causal backtest
    execution semantics, the planned stop-limit product contract, and prior
    stop-family testing strategy.
- Supporting external references:
  - `https://docs.pytest.org/en/stable/explanation/goodpractices.html`
  - `https://martinfowler.com/articles/practical-test-pyramid.html`
  - `https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html`
  - `https://kentcdodds.com/blog/testing-implementation-details`
  - `https://learn.microsoft.com/dotnet/core/testing/unit-testing-best-practices`
  - `https://testing.googleblog.com/2014/10/testing-on-toilet-writing-descriptive.html`
  - `https://diataxis.fr/`
  - `https://diataxis.fr/reference/`
  - `https://diataxis.fr/explanation/`
  - `https://agilemodeling.com/essays/agileDocumentationBestPractices.htm`
- Why these references matter:
  - They support behavior-focused tests, clear test names, small deterministic
    tests, balanced unit/integration/E2E coverage, and avoiding brittle
    implementation-detail assertions.
  - They also support separating documentation by user need, recording stable
    concepts in long-lived docs, and treating detailed tests as executable
    specifications where possible.
- In-repo scope:
  - Add a pre-implementation stop-limit test scenario planning artifact.
  - Keep the artifact outside `docs/product-specs/` so executable tests can
    become the scenario-level source of truth after implementation.
  - Update `docs/product-specs/index.md` to avoid routing future work to a
    static test-case catalog as a governing product spec.
  - Update `docs/design-docs/golden-principles.md` with the durable
    doc-management lesson.
  - Update this active plan with evaluator review and verification evidence.
- Out-of-repo scope:
  - Read-only web search for testing best practices explicitly requested by
    the user in this thread.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only testing-spec approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to web-search testing best practices, reread the
      stop-limit spec, and write a concrete test scenario planning artifact
      before runtime test implementation.
    - Granted scope:
      docs-only stop-limit testing-spec work plus task-limited read-only web
      research.
    - Expiration:
      end of this `2026-04-27` testing-spec slice.
    - Audit reference:
      this active plan.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The test scenario planning artifact states the testing philosophy in terms
    of durable behavioral contracts.
  - The artifact covers unit, integration, and canonical regression lanes.
  - The scenario matrix covers happy paths, rejected inputs, boundary
    equality against the last evaluated `last` reference price,
    dormant-vs-triggered lifecycle, gap-through behavior, same-point
    trigger/fill, post-trigger tail behavior, pre-trigger non-causality,
    priority, identity, long-only behavior, and public result contracts.
  - The artifact is concrete enough that a later implementation plan can
    translate each scenario into failing tests without reopening coverage
    design.
  - The product-spec index does not route scenario-level test cases as a
    governing product contract.
  - `uv run poe repo-check` passes after the document update.
- Out of scope:
  - Writing test code.
  - Implementing `stop_limit`.
  - Changing runtime behavior.
  - Expanding into live, paper, venue-specific, percent-sizing, bracket/OCO, or
    partial-fill public contracts.

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close only after the test scenario planning artifact protects the product
    intent rather than implementation mechanics, and after fresh repo-doc
    verification passes.
- Acceptance artifact location:
  - `docs/plans/2026-04-27-stop-limit-test-scenarios.md`
- How the generator and evaluator agreed on done before execution:
  - The document must let a future TDD implementation author know what to test,
    where to place it, which behavior each test protects, and which
    anti-patterns would make the test suite brittle.
- Checks the evaluator will use:
  - Compare against `docs/product-specs/stop-limit.md`.
  - Compare against `docs/references/testing.md`.
  - Compare against external best-practice findings.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - only documenting happy-path tests
  - asserting private implementation details instead of behavior
  - collapsing all coverage into one oversized integration suite
  - omitting gap-through non-fill, same-point fill, or post-trigger tail cases
  - changing production code in this docs-only slice

## Generator Work Log

- Planned slice order:
  1. Reread the stop-limit product spec and existing repo testing references.
  2. Web-search testing best practices.
  3. Write the stop-limit test scenario planning artifact.
  4. Keep product-spec routing focused on product meaning, not static test-case
     catalogs.
  5. Run repo checks.
  6. Record evaluator findings and final disposition.
  7. Reclassify the test scenario document out of `docs/product-specs/` after
     the user challenged the duplicate-contract risk.
  8. Consolidate the scenario catalog into this active plan after the user
     challenged the unnecessary split between two planning documents.
- Notes:
  - This slice intentionally produces a test-design contract before any test
    or implementation code.
  - 2026-04-27 follow-up:
    - User correctly challenged that the first version still read too much like
      principles plus a scenario list.
    - The artifact was strengthened with an executable scenario catalog that
      specifies concrete bar paths, order inputs, and expected outcomes for the
      highest-risk cases.
  - 2026-04-27 doc-governance follow-up:
    - User challenged whether a concrete test scenario document belongs in
      `docs/product-specs/` when tests themselves should be executable
      contracts.
    - Web research and repo doc-gardening rules support reclassifying the
      scenario catalog as a planning artifact, leaving product meaning in
      product specs and scenario truth in executable tests.
    - Key research findings:
      - Diataxis separates reference/explanation/how-to/tutorial needs; a
        concrete test-case catalog is not product reference once executable
        tests can carry the contract.
      - Agile Modeling explicitly recommends executable specifications over
        static documents for detailed requirements/design cases when practical.
      - Fowler's test pyramid guidance warns against redundant higher-level
        tests; the same anti-duplication logic applies to static documents that
        repeat executable tests.
      - Kent C. Dodds' implementation-detail guidance reinforces that tests
        should model real usage rather than private mechanics.
  - 2026-04-27 consolidation follow-up:
    - User challenged why the test scenario plan and the concrete scenario
      artifact were separate documents.
    - There was no strong repo-governance reason for the split; both were
      pre-implementation planning artifacts.
    - The concrete scenario catalog was merged into this active plan so this
      file remains the single planning surface for the stop-limit test-design
      slice.
- Blockers or scope changes:
  - None.


## Test Scenario Planning Artifact

This section is the concrete pre-implementation scenario catalog for the later TDD implementation plan. It is not a long-lived product spec; once corresponding tests exist under `tests/`, those executable tests become the scenario-level source of truth.

## Purpose

The tests for `stop_limit` should be treated as a durable product asset, not as
temporary scaffolding around one implementation.

The product intent is:

> `stop_limit` is dormant before its stop trigger; after trigger it becomes a
> working limit order; no pre-trigger price movement may be reused to fill it.

The stop-family trigger policy is intentionally generic:

- `stop` means a price-trigger primitive, not a venue-specific stop-loss or
  take-profit product name.
- trigger direction is inferred from `stop_price` relative to the last evaluated
  `last` reference price at order intake.
- side, position purpose, and limit price do not determine trigger direction.
- equality against the reference last is rejected as ambiguous.
- existing executable orders are evaluated before newly triggered stop-family
  orders at the same event point.

Equality rejection is a local `quantleet` ambiguity policy. These tests should
not present it as a universal exchange-conformance rule; some venues trigger
already-met stops, while others reject orders that would trigger immediately.

The test suite should make that intent hard to regress. The implementation may
change its helpers, traversal internals, or object layout. The tests should fail
only when the observable contract changes.

## External Testing Practice Evidence

The testing strategy follows these external best-practice findings:

- Pytest recommends project layouts and strictness options that make tests less
  surprising and easier to run consistently.
- Martin Fowler's practical test pyramid guidance supports many focused unit
  tests, fewer broader integration tests, and very few high-level end-to-end
  tests, while avoiding duplicated coverage at higher layers.
- Google Testing Blog warns that excessive end-to-end testing increases runtime
  and flakiness; integration and end-to-end tests should be selected for the
  behaviors that lower layers cannot prove.
- Kent C. Dodds' implementation-detail guidance is directly relevant here:
  tests should ask whether the software works from the user's perspective, not
  whether a private state variable or helper call has a particular shape.
- Microsoft unit-test guidance recommends simple inputs for the behavior being
  tested, one primary Act phase, and Arrange-Act-Assert structure.
- Google's descriptive-test-name guidance supports test names that explain the
  behavior without forcing readers to decode the test body first.

External references:

- [Pytest good integration practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [Martin Fowler: The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Google Testing Blog: Just Say No to More End-to-End Tests](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html)
- [Kent C. Dodds: Testing Implementation Details](https://kentcdodds.com/blog/testing-implementation-details)
- [Microsoft: Unit testing best practices](https://learn.microsoft.com/dotnet/core/testing/unit-testing-best-practices)
- [Google Testing Blog: Writing Descriptive Test Names](https://testing.googleblog.com/2014/10/testing-on-toilet-writing-descriptive.html)

## Good Test Code For This Slice

Good `stop_limit` tests should:

- test behavior and public/domain contracts, not private helper structure
- use deterministic, legible prices and timestamps
- keep one main behavioral claim per test
- use explicit scenario names that reveal the contract being protected
- make trigger direction, trigger timing, limit eligibility, fill price, fill
  time, and final order state easy to inspect
- include both expected user paths and adversarial edge paths
- split local domain semantics from cross-module runtime behavior
- prefer small focused fixtures over giant parameter tables when readability
  would suffer

Bad `stop_limit` tests include:

- one happy-path engine test standing in for the whole feature
- assertions that only prove a helper was called
- tests that know more about current object internals than a real strategy
  author or runtime boundary should know
- broad snapshot assertions that hide which contract failed
- integration tests that duplicate every unit case without adding boundary
  confidence
- unit tests that pretend to prove causal backtest traversal without using the
  execution-model or engine boundary that owns traversal

## Test Layer Strategy

### Layer 1: Unit Tests

Purpose:

- lock down local validation, trigger, matching, and path-construction
  semantics with fast deterministic tests

Target files:

- `tests/unit/trading/test_contracts.py`
- `tests/unit/trading/test_orders.py`
- `tests/unit/trading/test_matching_and_state.py`
- `tests/unit/backtest/test_execution_model.py`
- `tests/unit/backtest/test_order_activation_policy.py`
- `tests/unit/research/test_strategy_surface.py`

Unit tests should prove:

- `stop_limit` is accepted as a known order type
- validation rejects unsupported or ambiguous requests
- dormant orders are not executable
- triggered orders route to ordinary limit semantics
- trigger predicates are inclusive at the stop boundary
- backtest path construction exposes only causal post-trigger eligibility

### Layer 2: Integration Tests

Purpose:

- prove the real collaboration among strategy intake, request normalization,
  next-bar activation, execution-model path traversal, matching, order state,
  position state, and public result output

Target files:

- `tests/integration/research/test_backtest_execution_semantics.py`
- optional focused file:
  `tests/integration/research/test_stop_limit_execution_semantics.py`

Integration tests should prove:

- a strategy-authored `stop_limit` follows the public `BacktestEngine.run(...)`
  path
- no bar-created order can affect the bar that created it
- gap-through trigger/non-fill behavior is visible through the real engine
- same-point trigger/fill and post-trigger tail fill both work
- pre-trigger path movement is never reused
- trigger-only events do not leak into the public trade log

### Layer 3: Canonical Regression Tests

Purpose:

- preserve a small set of public, fixture-backed stop-limit workflows after
  lower-level semantics are locked down

Target files:

- `tests/integration/research/test_canonical_stop_limit_contract.py`

Canonical tests should be few. They should cover public strategy outcomes, not
all local edge cases. The lower layers own edge-case breadth.

## Scenario Naming Pattern

Prefer names that read like contracts:

- `test_stop_limit_buy_gap_through_triggers_but_stays_open_when_open_is_above_limit`
- `test_stop_limit_ignores_limit_touch_before_trigger`
- `test_stop_limit_same_point_trigger_and_fill_uses_limit_execution_contract`

Avoid names tied to implementation mechanics:

- `test_decisive_event_builder_appends_stop_limit_tick`
- `test_runtime_calls_match_order_after_trigger`
- `test_triggered_flag_switches_before_loop_index_advances`

## Scenario Matrix

The matrix below records coverage obligations. The later
"Executable Scenario Catalog" turns the highest-risk obligations into concrete
bar paths, order inputs, and expected outcomes.

### A. Public Strategy Request Contract

These scenarios protect the strategy author surface and request normalization.

1. `buy(quantity=..., order_type="stop_limit", stop_price=..., limit_price=...)`
   is accepted.
2. `sell(quantity=..., order_type="stop_limit", stop_price=..., limit_price=...)`
   is accepted while long.
3. `qty_percent + stop_limit` is rejected in the first slice.
4. missing `stop_price` is rejected.
5. missing `limit_price` is rejected.
6. `stop_price <= 0` is rejected.
7. `limit_price <= 0` is rejected.
8. non-finite `stop_price` is rejected.
9. non-finite `limit_price` is rejected.
10. `stop_price == reference_last` is rejected as ambiguous.
11. `stop_price > reference_last` infers `crosses_above`.
12. `stop_price < reference_last` infers `crosses_below`.
13. trigger direction is not derived from order side, position purpose, or
    limit price:
    - buy above reference last infers `crosses_above`
    - buy below reference last infers `crosses_below`
    - sell above reference last infers `crosses_above`
    - sell below reference last infers `crosses_below`
14. strategy `tag` survives request normalization.
15. user-facing `stop_price` becomes runtime `trigger_price` exactly once.
16. runtime `trigger_type` is normalized to `last`.
17. order intake remains disallowed from `init()` if the existing strategy
    contract disallows all order intake there.
18. `stop_price` remains invalid for non-stop order types.
19. `limit_price` remains invalid for `stop_market`.
20. ordinary `limit` behavior is unchanged by adding `stop_limit`.
21. dormant quantity-based buy stop-limit orders do not consume ordinary
    percent-buy reservations.
22. limit price does not participate in trigger-direction inference:
    - reference last `100`, stop `90`, buy limit `120` infers `crosses_below`
    - reference last `100`, stop `90`, buy limit `80` infers `crosses_below`
    - reference last `100`, stop `90`, sell limit `120` infers `crosses_below`
    - reference last `100`, stop `90`, sell limit `80` infers `crosses_below`

### B. Runtime Order Validation And Identity

These scenarios protect the runtime order contract without depending on
backtest bars.

1. `stop_limit` requires `trigger_price`.
2. `stop_limit` requires `trigger_condition`.
3. `stop_limit` requires `trigger_type`.
4. `stop_limit` requires `limit_price`.
5. non-stop order types reject trigger facts.
6. a new `stop_limit` starts open and dormant.
7. a dormant `stop_limit` is not executable.
8. a dormant `stop_limit` cannot be filled even when its limit price is
   marketable.
9. triggering sets `triggered_at`.
10. triggering preserves the same order id.
11. triggering preserves `order_type="stop_limit"`.
12. triggering preserves original trigger facts for later inspection.
13. runtime trigger evaluation does not retrigger or rewrite `triggered_at`
    after the order is already triggered.
14. after trigger, executable behavior is `limit`.
15. after trigger, buy execution fills only at `limit_price` or lower.
16. after trigger, sell execution fills only at `limit_price` or higher.
17. triggered-but-unfilled orders remain open and active.
18. a fill after trigger follows existing terminal or remaining-quantity order
    state rules.

### C. Trigger Predicate Boundary Cases

These scenarios protect inclusive trigger semantics.

1. `crosses_above` triggers when last price is exactly the stop price.
2. `crosses_above` triggers when last price moves above the stop price.
3. `crosses_above` does not trigger below the stop price.
4. `crosses_below` triggers when last price is exactly the stop price.
5. `crosses_below` triggers when last price moves below the stop price.
6. `crosses_below` does not trigger above the stop price.
7. once inferred, trigger condition does not change after later reference
   prices move around the stop price.
8. stale or pre-submit prices cannot trigger a newly submitted stop-limit.

### D. Matching Delegation Semantics

These scenarios protect the "trigger then ordinary limit" rule.

1. dormant `stop_limit` returns no fill when ordinary buy-limit matching would
   otherwise fill.
2. dormant `stop_limit` returns no fill when ordinary sell-limit matching would
   otherwise fill.
3. triggered buy `stop_limit` matches the same as an ordinary buy limit.
4. triggered sell `stop_limit` matches the same as an ordinary sell limit.
5. a marketable triggered buy fills at the existing conservative executable
   price used by ordinary buy limits.
6. a marketable triggered sell fills at the existing conservative executable
   price used by ordinary sell limits.
7. a non-marketable triggered buy remains open.
8. a non-marketable triggered sell remains open.
9. stop-limit matching tests assert inputs and outcomes, not which helper was
   called internally.

### E. Backtest Execution Model Path Semantics

These scenarios protect causal OHLC traversal before the full engine is
involved.

1. a gap through an upward stop emits the next open as the first trigger point.
2. a gap through a downward stop emits the next open as the first trigger point.
3. a bullish bar follows `open -> low -> high -> close`.
4. a bearish bar follows `open -> high -> low -> close`.
5. if the limit is touched before the stop in the canonical path, no fill is
   possible from that pre-trigger touch.
6. if the stop triggers and the trigger point is marketable against the limit,
   same-point trigger/fill is eligible.
7. if the stop triggers and the trigger point is worse than the limit, the order
   stays open at that point.
8. if the order remains open after trigger, the remaining path tail is evaluated
   for later limit crossings.
9. path traversal does not materialize unrelated ticks solely because a
   stop-limit exists.
10. existing ordinary limit decisive events keep their prior behavior.
11. multiple stop-limit orders crossed in one segment are evaluated in causal
    segment order.
12. existing executable orders remain eligible before newly triggered orders at
    the same event point.

### F. Engine Integration: Buy Stop-Limit

These scenarios go through `BacktestEngine.run(...)`.

1. buy stop-limit created on bar N cannot trigger or fill on bar N.
2. buy `crosses_above` gap-through with `open <= limit_price` triggers and may
   fill at the open under ordinary limit rules.
3. buy `crosses_above` gap-through with `open > limit_price` triggers but does
   not fill.
4. buy `crosses_above` intrabar trigger at `stop_price <= limit_price` can
   trigger and fill at the same point.
5. buy `crosses_above` intrabar trigger with `stop_price > limit_price` triggers
   but remains open if no later tail price is at or below the limit.
6. buy `crosses_above` intrabar trigger followed by a tail move back to the
   limit fills later on the same bar.
7. buy `crosses_below` pullback trigger can create a working buy limit.
8. buy `crosses_below` pullback trigger fills only when post-trigger price is
   at or below the limit.
9. buy stop-limit with a pre-trigger low below the limit and a later upward stop
   trigger does not fill from the earlier low.
10. buy stop-limit triggered but unfilled on bar N+1 can fill on bar N+2.

### G. Engine Integration: Sell Stop-Limit

These scenarios go through `BacktestEngine.run(...)`.

1. sell stop-limit created on bar N cannot trigger or fill on bar N.
2. sell `crosses_below` gap-through with `open >= limit_price` triggers and may
   fill at the open under ordinary limit rules.
3. sell `crosses_below` gap-through with `open < limit_price` triggers but does
   not fill.
4. sell `crosses_below` intrabar trigger at `stop_price >= limit_price` can
   trigger and fill at the same point.
5. sell `crosses_below` intrabar trigger with `stop_price < limit_price`
   triggers but remains open if no later tail price is at or above the limit.
6. sell `crosses_below` intrabar trigger followed by a tail move back to the
   limit fills later on the same bar.
7. sell `crosses_above` take-profit-style trigger can create a working sell
   limit.
8. sell `crosses_above` trigger fills only when post-trigger price is at or
   above the limit.
9. sell stop-limit with a pre-trigger high above the limit and a later downward
   stop trigger does not fill from the earlier high.
10. sell stop-limit triggered but unfilled on bar N+1 can fill on bar N+2.

### H. Gap-Through Non-Execution

These scenarios are mandatory because they distinguish `stop_limit` from
`stop_market`.

1. previous close `100`, buy stop `105`, limit `106`, next open `110`:
   trigger occurs at `110`, no fill occurs, order remains open.
2. previous close `100`, sell stop `95`, limit `94`, next open `90`:
   trigger occurs at `90`, no fill occurs, order remains open.
3. the public trade log has no entry for either trigger-only gap.
4. later favorable movement can fill the already-triggered working limit.
5. if later favorable movement never arrives, final result shows no fill for
   that order.

### I. Same-Point Trigger And Fill

These scenarios protect trigger-tick inclusivity.

1. buy stop `105`, limit `106`, first eligible price `105`: trigger and fill
   are both allowed at that point.
2. buy stop `95`, limit `96`, first eligible price `95`: trigger and fill are
   both allowed at that point for a pullback-style buy.
3. sell stop `95`, limit `94`, first eligible price `95`: trigger and fill are
   both allowed at that point.
4. sell stop `105`, limit `104`, first eligible price `105`: trigger and fill
   are both allowed at that point for a take-profit-style sell.
5. trigger facts are recorded before the fill is applied.
6. only the fill appears in public fill-level results; the trigger itself does
   not create a trade-log row.

### J. Post-Trigger Tail And Pre-Trigger Non-Causality

These scenarios protect the hardest same-bar behavior.

1. bullish path `open=100 -> low=94 -> high=106 -> close=104`, buy stop `105`,
   limit `95`: the low happened before trigger, so the order must not fill.
2. bullish path `open=80 -> low=70 -> high=106 -> close=90`, buy stop `105`,
   limit `95`: the post-trigger tail crosses the limit after trigger, so the
   order may fill at the limit crossing.
3. bearish path `open=100 -> high=106 -> low=94 -> close=96`, sell stop `95`,
   limit `105`: the high happened before trigger, so the order must not fill.
4. bearish path `open=120 -> high=130 -> low=94 -> close=110`, sell stop `95`,
   limit `105`: the post-trigger tail crosses the limit after trigger, so the
   order may fill at the limit crossing.
5. no test should infer fill eligibility from unordered OHLC extremes alone.

### K. Ordering, Identity, And Public Results

These scenarios protect lifecycle observability.

1. existing executable orders are processed before newly triggered stop-limit
   orders at the same event point.
2. two newly triggered stop-limit orders preserve stable order-id ordering.
3. a triggered unfilled stop-limit keeps the same order id in the active order
   set.
4. a triggered filled stop-limit keeps `order_type="stop_limit"` internally.
5. trigger-only events do not appear in `trade_log`.
6. `BacktestResult` remains fill-level for this slice.
7. position state changes only on fills, not on trigger-only events.
8. final summary metrics are unaffected by trigger-only unfilled orders except
   through any explicit open-order state that the public result already exposes.

### L. Long-Only And Flat-Position Behavior

These scenarios protect current long-only scope.

1. `sell(stop_limit)` while flat follows the current long-only no-op policy.
2. flat `sell(stop_limit)` does not leave behind a dormant order that could
   later become a short entry.
3. `sell(stop_limit)` while long can exit only up to the available long
   position under existing sell semantics.
4. rejected or no-op long-only paths should not create trigger-only trade-log
   entries.

### M. Regression Guardrails For Existing Features

These scenarios ensure `stop_limit` does not break shipped order families.

1. market orders keep existing fill behavior.
2. ordinary limit orders keep existing conservative gap and intrabar behavior.
3. `stop_market` keeps existing trigger and market-fill behavior.
4. `qty_percent` behavior for supported market/limit paths is unchanged.
5. `qty_percent + stop_market` remains rejected if that is still the shipped
   contract.
6. `qty_percent + stop_limit` remains rejected in this first slice.
7. quantity-based dormant stop-limit buys do not reduce the budget available to
   ordinary percent-based buy orders.

### N. Canonical Public Contracts

Canonical tests should be added after lower-layer tests are stable.

Recommended first contracts:

1. a synthetic buy stop-limit strategy proving trigger-and-fill.
2. a synthetic buy stop-limit strategy proving trigger-without-fill.
3. a synthetic sell stop-limit strategy proving trigger-and-fill.
4. a synthetic sell stop-limit strategy proving trigger-without-fill.
5. one fixture-backed BTC strategy only after synthetic semantics no longer
   need adjustment.

Canonical tests should assert:

- trade count
- fill timestamps
- fill side
- fill price
- fill quantity
- final cash/equity or final position where the existing public result already
  exposes those values

Canonical tests should not assert:

- private helper names
- intermediate synthetic event lists unless those are already a public or
  explicitly tested execution-model contract
- a giant snapshot of the whole result object

## Executable Scenario Catalog

This catalog is the implementation-ready part of the planning artifact. A later
TDD plan should translate these into concrete tests before broadening into the
full matrix.

Notation:

- `S0` is the submission bar. In the current bar-backtest path, the strategy
  sees `S0.close == 100`; that close is the last evaluated `last` reference
  price for order-intake trigger inference.
- The submitted order becomes eligible on `B1`, not on `S0`.
- Unless stated otherwise, quantity is `1.0`, starting cash is sufficient, and
  timestamps should be explicit consecutive bars.
- Bullish bars use the approved path `open -> low -> high -> close`.
- Bearish bars use the approved path `open -> high -> low -> close`.
- Expected `trade_log` means the public fill-level log. Trigger-only events do
  not appear there.

### Catalog A: Request And Validation Tests

#### A1. Buy Stop-Limit Request Normalizes Above-Reference Trigger

Input:

- reference last at order intake: `100`
- strategy call:
  `buy(quantity=1.0, order_type="stop_limit", stop_price=105, limit_price=106, tag="breakout")`

Expected:

- request is accepted
- runtime order has `order_type="stop_limit"`
- runtime order has `trigger_price=105`
- runtime order has `limit_price=106`
- runtime order has `trigger_condition="crosses_above"`
- runtime order has `trigger_type="last"`
- runtime order preserves `tag="breakout"`
- no fill exists at submission time

#### A2. Buy Stop-Limit Request Normalizes Below-Reference Trigger

Input:

- reference last at order intake: `100`
- strategy call:
  `buy(quantity=1.0, order_type="stop_limit", stop_price=95, limit_price=96)`

Expected:

- request is accepted
- runtime order has `trigger_condition="crosses_below"`
- trigger direction is not derived from side, position purpose, or limit price

#### A3. Sell Stop-Limit Request Normalizes Above-Reference Trigger

Input:

- reference last at order intake: `100`
- strategy call:
  `sell(quantity=1.0, order_type="stop_limit", stop_price=105, limit_price=104)`

Expected:

- request is accepted when the strategy has a long position to exit
- runtime order has `trigger_condition="crosses_above"`
- trigger direction is not derived from side, position purpose, or limit price

#### A4. Sell Stop-Limit Request Normalizes Below-Reference Trigger

Input:

- reference last at order intake: `100`
- strategy call:
  `sell(quantity=1.0, order_type="stop_limit", stop_price=95, limit_price=94)`

Expected:

- request is accepted when the strategy has a long position to exit
- runtime order has `trigger_condition="crosses_below"`

#### A5. Missing Or Ambiguous Request Inputs Are Rejected

Input variants:

- `order_type="stop_limit"` without `stop_price`
- `order_type="stop_limit"` without `limit_price`
- `stop_price=100` when reference last is `100`
- `stop_price=0`
- `limit_price=0`
- `stop_price=float("nan")`
- `limit_price=float("inf")`
- no `quantity` and no `qty_percent`
- both `quantity=1.0` and `qty_percent=50.0`
- `qty_percent=0.5` with `order_type="stop_limit"`

Expected:

- each variant raises the same family of validation error used by current order
  request validation
- no runtime order is created
- no public fill or trade-log entry is created

#### A6. Limit Price Does Not Affect Trigger Direction

Input variants:

- reference last `100`, buy stop `90`, limit `120`
- reference last `100`, buy stop `90`, limit `80`
- reference last `100`, sell stop `90`, limit `120`
- reference last `100`, sell stop `90`, limit `80`

Expected:

- every request is accepted when ordinary side/position preconditions are met
- every request normalizes to `trigger_condition="crosses_below"`
- no request is rejected because the limit price is above or below the stop
  price
- fill or non-fill is not decided at request intake; it is decided after
  trigger by the later executable tick and ordinary limit matching semantics

### Catalog B: Runtime Order And Matching Tests

#### B1. Dormant Buy Stop-Limit Does Not Fill As A Buy Limit

Input:

- dormant buy order:
  `order_type="stop_limit", trigger_price=105, trigger_condition="crosses_above", limit_price=110`
- executable event last price: `100`

Expected:

- order is not executable
- no fill is produced even though an ordinary buy limit at `110` would be
  marketable at `100`
- order remains open and untriggered

#### B2. Dormant Sell Stop-Limit Does Not Fill As A Sell Limit

Input:

- dormant sell order:
  `order_type="stop_limit", trigger_price=95, trigger_condition="crosses_below", limit_price=90`
- executable event last price: `100`

Expected:

- order is not executable
- no fill is produced even though an ordinary sell limit at `90` would be
  marketable at `100`
- order remains open and untriggered

#### B3. Triggered Buy Stop-Limit Reuses Buy Limit Matching

Input:

- triggered buy order:
  `order_type="stop_limit", trigger_price=105, limit_price=106, triggered_at=T1`
- executable event last price: `105`

Expected:

- order is executable as a limit
- fill is produced under the ordinary buy-limit contract
- fill price is `105`
- order id and `order_type="stop_limit"` are preserved

#### B4. Triggered Buy Stop-Limit Remains Open When Price Is Worse Than Limit

Input:

- triggered buy order:
  `order_type="stop_limit", trigger_price=105, limit_price=106, triggered_at=T1`
- executable event last price: `110`

Expected:

- no fill is produced
- order remains open
- `triggered_at` is preserved

#### B5. Triggered Sell Stop-Limit Reuses Sell Limit Matching

Input:

- triggered sell order:
  `order_type="stop_limit", trigger_price=95, limit_price=94, triggered_at=T1`
- executable event last price: `95`

Expected:

- order is executable as a limit
- fill is produced under the ordinary sell-limit contract
- fill price is `95`
- order id and `order_type="stop_limit"` are preserved

#### B6. Triggered Sell Stop-Limit Remains Open When Price Is Worse Than Limit

Input:

- triggered sell order:
  `order_type="stop_limit", trigger_price=95, limit_price=94, triggered_at=T1`
- executable event last price: `90`

Expected:

- no fill is produced
- order remains open
- `triggered_at` is preserved

### Catalog C: Engine Buy Scenarios

#### C1. Buy Gap-Through Within Limit Fills At Next Open

Bars:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=105, high=107, low=104, close=106`

Strategy action on `S0`:

- `buy(quantity=1.0, order_type="stop_limit", stop_price=105, limit_price=106)`

Expected:

- order does not affect `S0`
- order triggers at `B1.open=105`
- order fills at `105`
- `trade_log` has exactly one buy fill
- fill timestamp is `B1`
- final position is long `1.0`

#### C2. Buy Gap-Through Beyond Limit Triggers But Does Not Fill

Bars:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=110, high=112, low=108, close=111`

Strategy action on `S0`:

- `buy(quantity=1.0, order_type="stop_limit", stop_price=105, limit_price=106)`

Expected:

- order triggers at `B1.open=110`
- no fill occurs because `110 > 106`
- `trade_log` is empty
- final position remains flat
- the order remains active as a triggered working limit if open-order state is
  inspectable in the tested layer

#### C3. Buy Same-Point Trigger And Fill

Bars:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=100, high=106, low=99, close=104`

Approved path:

- bullish `100 -> 99 -> 106 -> 104`

Strategy action on `S0`:

- `buy(quantity=1.0, order_type="stop_limit", stop_price=105, limit_price=106)`

Expected:

- order triggers when the path first reaches `105`
- same point is marketable for a buy limit at `106`
- order fills at `105`
- `trade_log` has exactly one buy fill
- no separate trigger row appears in `trade_log`

#### C4. Buy Pre-Trigger Low Does Not Fill

Bars:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=100, high=106, low=94, close=104`

Approved path:

- bullish `100 -> 94 -> 106 -> 104`

Strategy action on `S0`:

- `buy(quantity=1.0, order_type="stop_limit", stop_price=105, limit_price=95)`

Expected:

- the path touches `94` before the stop triggers
- order triggers later when the path reaches `105`
- no fill occurs from the earlier `94`
- no fill occurs after trigger because the tail `105 -> 104` never reaches
  `95`
- `trade_log` is empty
- final position remains flat

#### C5. Buy Post-Trigger Tail Fill At The Limit Crossing

Bars:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=80, high=106, low=70, close=90`

Approved path:

- bullish `80 -> 70 -> 106 -> 90`

Strategy action on `S0`:

- `buy(quantity=1.0, order_type="stop_limit", stop_price=105, limit_price=95)`

Expected:

- the pre-trigger low at `70` does not fill the order
- order triggers when the path reaches `105`
- the post-trigger tail later crosses through `95`
- order fills at the conservative limit crossing price `95`, not at the better
  endpoint `90`
- `trade_log` has exactly one buy fill
- final position is long `1.0`

#### C6. Buy Pullback-Style Stop-Limit Below Close

Bars:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=100, high=101, low=95, close=98`

Approved path:

- bearish `100 -> 101 -> 95 -> 98`

Strategy action on `S0`:

- `buy(quantity=1.0, order_type="stop_limit", stop_price=95, limit_price=96)`

Expected:

- request infers `crosses_below`
- order triggers when the path reaches `95`
- same point is marketable for a buy limit at `96`
- order fills at `95`
- final position is long `1.0`

### Catalog D: Engine Sell Scenarios

Each sell scenario requires an existing long position before the stop-limit exit
is submitted. The test may establish that position with an earlier market buy
or by using the repository's existing supported position setup helper, if one
exists.

#### D1. Sell Gap-Through Within Limit Fills At Next Open

Bars after the long position exists:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=95, high=96, low=93, close=94`

Strategy action on `S0`:

- `sell(quantity=1.0, order_type="stop_limit", stop_price=95, limit_price=94)`

Expected:

- order does not affect `S0`
- order triggers at `B1.open=95`
- order fills at `95`
- `trade_log` includes exactly one sell fill for this exit
- fill timestamp is `B1`
- final position is flat

#### D2. Sell Gap-Through Beyond Limit Triggers But Does Not Fill

Bars after the long position exists:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=90, high=92, low=88, close=91`

Strategy action on `S0`:

- `sell(quantity=1.0, order_type="stop_limit", stop_price=95, limit_price=94)`

Expected:

- order triggers at `B1.open=90`
- no fill occurs because `90 < 94`
- no sell fill appears in `trade_log`
- position remains long
- the order remains active as a triggered working limit if open-order state is
  inspectable in the tested layer

#### D3. Sell Same-Point Trigger And Fill

Bars after the long position exists:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=100, high=101, low=94, close=96`

Approved path:

- bearish `100 -> 101 -> 94 -> 96`

Strategy action on `S0`:

- `sell(quantity=1.0, order_type="stop_limit", stop_price=95, limit_price=94)`

Expected:

- order triggers when the path first reaches `95`
- same point is marketable for a sell limit at `94`
- order fills at `95`
- no separate trigger row appears in `trade_log`
- final position is flat

#### D4. Sell Pre-Trigger High Does Not Fill

Bars after the long position exists:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=100, high=106, low=94, close=96`

Approved path:

- bearish `100 -> 106 -> 94 -> 96`

Strategy action on `S0`:

- `sell(quantity=1.0, order_type="stop_limit", stop_price=95, limit_price=105)`

Expected:

- the path touches `106` before the stop triggers
- order triggers later when the path reaches `95`
- no fill occurs from the earlier `106`
- no fill occurs after trigger because the tail `95 -> 96` never reaches
  `105`
- no sell fill appears in `trade_log`
- position remains long

#### D5. Sell Post-Trigger Tail Fill At The Limit Crossing

Bars after the long position exists:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=120, high=130, low=94, close=110`

Approved path:

- bearish `120 -> 130 -> 94 -> 110`

Strategy action on `S0`:

- `sell(quantity=1.0, order_type="stop_limit", stop_price=95, limit_price=105)`

Expected:

- the pre-trigger high at `130` does not fill the order
- order triggers when the path reaches `95`
- the post-trigger tail later crosses through `105`
- order fills at the conservative limit crossing price `105`, not at the
  better endpoint `110`
- `trade_log` includes exactly one sell fill for this exit
- final position is flat

#### D6. Sell Take-Profit-Style Stop-Limit Above Close

Bars after the long position exists:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=100, high=105, low=99, close=103`

Approved path:

- bullish `100 -> 99 -> 105 -> 103`

Strategy action on `S0`:

- `sell(quantity=1.0, order_type="stop_limit", stop_price=105, limit_price=104)`

Expected:

- request infers `crosses_above`
- order triggers when the path reaches `105`
- same point is marketable for a sell limit at `104`
- order fills at `105`
- final position is flat

### Catalog E: Public Result And Ordering Scenarios

#### E1. Trigger-Only Event Does Not Enter Trade Log

Use either `C2` or `D2`.

Expected:

- trigger occurs internally
- `trade_log` remains empty for the trigger-only event
- public fill count is unchanged
- position state is unchanged

#### E2. Triggered But Unfilled Order Can Fill On Later Bar

Bars:

- use `C2` through `B1` to trigger an unfilled buy stop-limit
- add `B2`: `open=111, high=112, low=106, close=107`

Expected:

- no fill occurs on `B1`
- order remains a triggered working buy limit at `106`
- order fills on `B2` when price reaches `106`
- `trade_log` has exactly one buy fill at `106`

#### E3. Existing Executable Order Has Priority At Same Event Point

Setup:

- one ordinary buy limit for quantity `1.0` at `105` is already active before
  `B1`
- one dormant buy stop-limit for quantity `1.0`, stop `105`, limit `105`, also
  triggers at the same `B1` event point
- `B1` first eligible price is `105`
- starting cash is sufficient for both orders in the primary priority test

Expected:

- the existing executable order is processed before the newly triggered
  stop-family order at that event point
- if both fill, public fill ordering reflects existing-before-newly-triggered
  priority
- a separate constrained-cash variant may assert that the existing ordinary
  limit receives the only affordable fill, but that belongs to accounting and
  affordability interaction coverage rather than the primary priority test

#### E4. Source-Based Public Run Path Matches Bars-Based Stop-Limit Semantics

Setup:

- use one minimal source-backed fixture that represents either `C1` or `C2`
- run the strategy through `BacktestEngine.run(source=..., strategy=...)`
  instead of direct `bars=...`

Expected:

- the source path produces the same stop-limit fill or non-fill contract as the
  equivalent direct bars path
- assertions stay at the public result level: fill count, fill timestamp, fill
  side, fill price, final position, and trade-log absence for trigger-only
  events
- this test does not duplicate every synthetic bars scenario; it only proves
  the included public entrypoint is wired to the same execution semantics

#### E5. Flat Sell Stop-Limit Does Not Become A Short Entry

Bars:

- `S0`: `open=100, high=100, low=100, close=100`
- `B1`: `open=95, high=96, low=93, close=94`

Strategy action on `S0` while flat:

- `sell(quantity=1.0, order_type="stop_limit", stop_price=95, limit_price=94)`

Expected:

- current long-only no-op policy is preserved
- no dormant sell stop-limit is left behind
- no fill occurs on `B1`
- final position remains flat
- `trade_log` is empty

## Minimum Implementation-Ready Test Batch

The later TDD implementation plan should start with this minimum batch before
adding broader regression coverage:

1. request validation and trigger-condition inference unit tests
2. limit-price-independence tests for trigger-condition inference
3. runtime order validation and dormant/executable state unit tests
4. matching delegation tests for triggered buy and sell stop-limits
5. execution-model tests for pre-trigger non-causality and post-trigger tail
6. engine integration tests for buy gap-through non-fill and sell gap-through
   non-fill
7. engine integration tests for buy and sell same-point trigger/fill
8. engine integration tests for buy and sell post-trigger tail fill
9. public trade-log tests proving trigger-only events are not fills
10. sizing-shape validation tests for missing, mixed, and unsupported sizing
11. dormant stop-limit buy reservation tests proving ordinary percent-buy
    budgets are unchanged
12. same-event priority tests proving existing executable orders are evaluated
    before newly triggered stop-family orders
13. a focused source-based public run-path test

This sequence is intentionally smaller than the full matrix. It gives the first
implementation tight feedback while preventing the most damaging semantic bugs.

## Acceptance Criteria

The `stop_limit` implementation should not be treated as complete until:

1. every scenario in the minimum implementation-ready batch has a concrete
   passing test
2. broader scenario coverage has either passing tests or an explicit deferral
   record in the implementation plan
3. unit tests cover local contracts without depending on private helper calls
4. integration tests cover the real strategy-to-engine path
5. canonical regression tests pin only stable public outcomes
6. `uv run poe verify` passes
7. runtime-sensitive backtest coverage is verified with
   `uv run poe verify-runtime`

## Out Of Scope

This test scenario planning artifact does not cover:

- `qty_percent + stop_limit`
- trailing stop-limit
- bracket, OCO, OTO, or attached protective orders
- live trading
- paper trading
- venue-specific price bands
- trigger references beyond `last`
- public partial-fill contracts
- short selling
- leverage or margin

## Evaluator Review

- Findings:
  - No blocking findings.
  - The test scenario planning artifact is aligned with the stop-limit product
    contract:
    dormant before trigger, ordinary limit semantics after trigger, no
    pre-trigger path reuse, gap-through non-execution, same-point trigger/fill,
    and post-trigger tail eligibility are all explicit.
  - The document follows the repository test taxonomy by splitting coverage
    into unit, integration, and canonical regression lanes instead of relying
    on a single end-to-end happy path.
  - The document incorporates current external testing guidance: behavior over
    implementation details, descriptive test names, small deterministic inputs,
    and a balanced test pyramid.
  - The scenario matrix is intentionally broader than the minimum first TDD
    batch; the minimum batch gives implementation a focused starting point
    while the full matrix records the durable coverage target.
  - Follow-up review:
    - The original matrix was directionally useful but not concrete enough for
      immediate test authoring in several scenarios.
    - The added executable scenario catalog closes that gap for the critical
      buy/sell, gap-through, same-point, pre-trigger, post-trigger, public
      result, priority, and long-only cases.
  - Doc-governance review:
    - No blocking findings after reclassification.
    - `docs/product-specs/` now contains product meaning, not a duplicate
      scenario-level test catalog.
    - The concrete scenario catalog remains available as a pre-implementation
      planning artifact under `docs/plans/`.
    - `docs/design-docs/golden-principles.md` now records the durable rule:
      executable tests are the preferred source of truth for scenario-level
      behavior once they exist.
  - Consolidation review:
    - No blocking findings after merging the scenario catalog into this active
      plan.
    - The repo now has one stop-limit test-scenario planning document instead
      of a separate active-plan plus artifact pair.
- Verification evidence:
  - `uv run poe repo-check`
    - output:
      - `Poe => uv run python scripts/repo_check.py`
      - `repository checks passed`
  - `git diff --check`
    - output: no whitespace errors reported
- Final disposition:
  - `complete`
