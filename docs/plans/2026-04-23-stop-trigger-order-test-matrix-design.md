# Active Plan

- Date: `2026-04-23`
- Task: `Freeze the stop/trigger order test strategy and scenario matrix`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Produce a docs-first testing artifact for the stop/trigger order work.
  - Capture:
    - the repository-local testing philosophy for this feature
    - lessons from comparator libraries' stop-order tests
    - the exact unit/integration scenario matrix that later implementation must
      satisfy
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
  - `docs/references/testing.md`
  - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
- Why these are governing:
  - They define the workflow contract, Tier A safety expectations, repository
    testing taxonomy, and the already-approved stop/trigger product shape that
    the tests must enforce.
- Supporting references:
  - `/tmp/quant-sizing-survey/backtesting.py/backtesting/test/_test.py`
  - `/tmp/freqtrade/tests/optimize/test_backtest_detail.py`
  - `/tmp/lean/Tests/Common/Orders/Fills/EquityFillModelTests.StopMarketFill.cs`
  - `/tmp/lean/Tests/Common/Orders/Fills/EquityFillModelTests.cs`
  - `/tmp/nautilus_trader/tests/integration_tests/adapters/binance/test_execution_handlers.py`
  - `tests/integration/research/test_backtest_execution_semantics.py`
- Why these references matter:
  - They show multiple mature testing styles:
    - compact behavior tests
    - broad scenario matrices
    - contract-focused fill-model tests
    - cross-boundary trigger invariants
  - They provide direct evidence for what to copy and what to avoid.
- In-repo scope:
  - Write one repository-local test strategy and scenario matrix document under
    `docs/plans/`.
- Out-of-repo scope:
  - No code or test implementation yet.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only testing-design approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to treat stop-order tests as durable assets,
      inspect comparator test philosophy first, and write a scenario document
      before implementation planning
    - Granted scope:
      docs-only Tier A testing-design work plus read-only `/tmp` comparator
      inspection
    - Expiration:
      end of this `2026-04-23` testing-design slice
    - Audit reference:
      this active plan
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository contains a stop/trigger order testing document that clearly
    states:
    - what good test code means for this feature
    - which comparator practices are adopted or rejected
    - how tests should be split between unit and integration lanes
    - which behavioral scenarios must be covered before implementation can be
      called complete
  - `uv run poe repo-check` passes after the doc is added.
- Out of scope:
  - Writing the implementation plan
  - Writing the test code itself
  - Implementing stop orders

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the testing document is concrete enough that a
    future implementation plan can translate it into failing tests without
    reopening coverage scope.
- Acceptance artifact location:
  - `docs/plans/2026-04-23-stop-trigger-order-test-matrix-design.md`
- How the generator and evaluator agreed on done before execution:
  - This slice is done when the document makes the intended coverage obvious:
    what belongs in unit tests, what belongs in integration tests, what corner
    cases must not be missed, and what anti-patterns future test authors must
    avoid.
- Checks the evaluator will use:
  - Compare the artifact against the repository test taxonomy.
  - Compare the proposed scenarios against the stop/trigger spec.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - reducing the matrix to only "happy path" examples
  - writing implementation-coupled tests that assert private mechanics rather
    than behavioral contracts
  - collapsing all coverage into one oversized integration suite

## Generator Work Log

- Planned slice order:
  1. Inspect comparator tests and current repo test conventions.
  2. Extract useful testing patterns and anti-patterns.
  3. Write the repo-local stop/trigger test strategy and scenario matrix.
  4. Run repo checks.
- Notes:
  - This artifact is meant to be used before the implementation plan so the
    implementation plan can be test-first with better scope discipline.
- Blockers or scope changes:
  - None.

## Stop/Trigger Order Test Strategy

### 1. Role Of This Document

This document exists because stop/trigger orders are not just another feature.

They add:

- dormant-versus-executable state
- trigger timing
- same-bar causality questions
- gap semantics
- order-priority questions

For this feature, tests are a first-class asset. The implementation is allowed
to evolve; the behavioral contract is not.

### 2. Testing Philosophy

For this feature, good tests must satisfy all of the following:

- test the contract, not private implementation shape
- stay readable enough that a later engineer can understand the scenario
  without re-deriving the engine internals
- use deterministic fixture data with obvious prices and timestamps
- isolate one behavior per test whenever possible
- cover both expected use and realistic edge/collision cases
- split local semantics from cross-module semantics instead of forcing
  everything through one giant test

Explicit anti-patterns:

- one "works once" happy-path test standing in for an entire feature
- asserting on private helper calls or internal temporary state when the public
  behavioral result is enough
- giant parameter blobs that maximize case count while destroying readability
- integration tests doing the work that should be locked down in unit tests
- unit tests pretending to validate end-to-end semantics without exercising the
  real path-construction/runtime collaboration

### 3. Comparator Findings

#### Adopt From `backtesting.py`

Useful patterns:

- small targeted behavioral tests
- scenario names tied directly to user-observable outcomes
- asserting on the visible trade result rather than internal helper structure

Evidence:

- [backtesting.py `_test.py`](/tmp/quant-sizing-survey/backtesting.py/backtesting/test/_test.py:549)
- [backtesting.py `_test.py`](/tmp/quant-sizing-survey/backtesting.py/backtesting/test/_test.py:1153)

Adopted lesson:

- prefer short deterministic tests for one semantic claim at a time

Rejected lesson:

- do not rely on a small handful of compact examples as the entire stop-order
  coverage story

#### Adopt From `freqtrade`

Useful patterns:

- scenario breadth matters
- conflict cases are worth enumerating explicitly
- gap, trailing, ROI/stop collisions, and repeated-trade interactions deserve
  concrete named examples

Evidence:

- [freqtrade `test_backtest_detail.py`](/tmp/freqtrade/tests/optimize/test_backtest_detail.py:1)

Adopted lesson:

- build a broad scenario matrix and treat edge cases as first-class

Rejected lesson:

- avoid one giant monolithic data table as the primary test style for
  `quantcraft`; it gives breadth but becomes hard to understand and maintain

#### Adopt From LEAN

Useful patterns:

- unit tests target one fill contract at a time
- inputs are explicit and deterministic
- assertions check fill quantity, fill price, and status directly
- data-source distinctions and stale-data behavior are tested deliberately

Evidence:

- [LEAN `EquityFillModelTests.StopMarketFill.cs`](/tmp/lean/Tests/Common/Orders/Fills/EquityFillModelTests.StopMarketFill.cs:1)
- [LEAN `EquityFillModelTests.cs`](/tmp/lean/Tests/Common/Orders/Fills/EquityFillModelTests.cs:134)

Adopted lesson:

- unit tests should read like executable contract statements

#### Adopt From Nautilus

Useful patterns:

- integration tests verify that trigger-specific invariants survive
  cross-boundary translation
- stop orders are tested as durable order entities, not just backtest candles

Evidence:

- [Nautilus adapter execution test](/tmp/nautilus_trader/tests/integration_tests/adapters/binance/test_execution_handlers.py:339)

Adopted lesson:

- integration tests should verify trigger facts and order identity are
  preserved across boundaries, not only local fill outcomes

#### Keep From Current `quantcraft`

Useful existing pattern:

- integration execution-semantics tests already use simple `TimeBar` fixtures,
  scenario-specific strategy classes, and direct assertions on trade-log
  outcomes

Evidence:

- [test_backtest_execution_semantics.py](/home/retn0/repositories/nbsp1221/quantcraft/tests/integration/research/test_backtest_execution_semantics.py)

Adopted lesson:

- extend the current style rather than replacing it with opaque scenario
  machinery

### 4. Repository-Local Testing Strategy

The stop/trigger work should use **three layers** of tests.

#### Layer 1: Unit tests

Purpose:

- lock down local order semantics and trigger/fill legality

Target files:

- `tests/unit/trading/...`
- `tests/unit/backtest/...`
- `tests/unit/research/...` only where the public strategy request surface is
  concerned

What belongs here:

- order validation
- dormant/triggered/fill legality
- trigger predicate behavior
- trigger-condition inference behavior
- fill delegation behavior
- synthetic path event generation for stop-crossing points
- public strategy request validation for `stop_market`

#### Layer 2: Integration tests

Purpose:

- verify the real collaboration between strategy runtime, activation,
  execution-model path construction, matcher, and backtest summaries

Target files:

- `tests/integration/research/...`

What belongs here:

- next-bar activation semantics
- gap trigger behavior
- intrabar trigger behavior
- conflict ordering between old active orders and newly triggered ones
- long-only exit semantics
- stop-family behavior through the actual engine entrypoints

#### Layer 3: Regression / contract tests

Purpose:

- preserve a few canonical public workflows after the first feature lands

Target files:

- additive canonical backtest contract tests once the first slice ships

What belongs here:

- one or two stable public stop-market strategy contracts
- expected summary/trade-log digests for canonical fixture-backed runs

### 5. Test Asset Rules

The stop/trigger tests should follow these repo-local rules:

- keep fixtures numeric and legible
- prefer short sequences of `TimeBar` values with obvious prices
- use explicit timestamps so order timing is visible
- name tests after the contract, not after the helper used to set them up
- keep one main assertion story per test
- use helper factories only when they improve readability more than they hide
  meaning

Recommended assertion style:

- assert fill timestamp
- assert fill side
- assert fill price
- assert fill quantity
- assert final order or position state

Avoid:

- broad "result looks roughly right" assertions
- excessive snapshot-style assertions in unit tests
- private helper or ordering implementation assertions when the trade log or
  order state already proves the contract

## Stop/Trigger Scenario Matrix

### A. Public Request Contract

These are unit tests around the strategy/request surface.

1. `stop_market` request accepts `stop_price` and `quantity`
2. `stop_market` request rejects missing `stop_price`
3. `stop_market` request rejects `limit_price`
4. non-stop order requests reject `stop_price`
5. explicit symbol mismatch still fails in the single-symbol workflow
6. request normalization converts API `stop_price` into runtime
   `trigger_price` exactly once at the request-to-runtime boundary
7. in the current `on_bar()` backtest workflow, request normalization uses the
   active closed bar's `close` as the submission-time trigger-source reference
   price for first-slice `trigger_condition` inference
8. request normalization infers `crosses_above` when `stop_price` is above the
   active bar `close`
9. request normalization infers `crosses_below` when `stop_price` is below the
   active bar `close`
10. request normalization rejects `stop_price == active_bar.close` in the
   first shipped slice because auto-inference would be ambiguous/in-market
11. request normalization persists inferred `trigger_condition` on the runtime
    order and does not leave it implicit
12. request normalization does not derive `trigger_condition` from buy/sell
    side alone
13. `sell(stop_market)` while flat remains allowed as a no-op in the long-only
    runtime path and is not treated as a short-entry contract
14. `sell(stop_market)` while flat does not leave behind a dormant runtime order
15. `qty_percent + stop_market` is rejected in the first shipped slice rather
    than silently inventing stop-aware sizing semantics
16. the existing `init()` contract still holds: order intake is not allowed
    from `init()`, so stop requests never need a non-`on_bar()` fallback
    inference baseline in the first slice
17. zero or negative quantity remains invalid on the new request path
18. malformed or non-finite stop/trigger prices remain invalid on the new
    request path

### B. Runtime Order Local Semantics

These are unit tests around the runtime order model itself.

1. `StopMarketOrder` starts dormant and open with a persisted
   `trigger_condition`
2. dormant stop order cannot be filled
3. `crosses_above` triggers on price reaching or exceeding trigger
4. `crosses_below` triggers on price reaching or falling below trigger
5. `trigger_condition` remains fixed after submission and does not change with
   later price moves
6. triggering sets trigger facts exactly once
7. when trigger and fill occur on the same executable point, trigger facts are
   recorded before the underlying fill is applied
8. once triggered, `stop_market` delegates to ordinary market execution
9. stale or pre-submit data must not trigger a dormant stop order
10. triggering does not erase original trigger facts needed for auditing
11. non-stop orders do not expose trigger facts or `trigger_condition`

### C. Matching / Fill Delegation Semantics

These are unit tests around execution delegation rather than the full engine.

1. triggered `stop_market` uses the same market-fill semantics as ordinary
   market execution
2. stop-family orders do not each implement independent duplicated fill logic
   from a contract perspective
3. dormant stop orders return no fill even when ordinary market/limit
   conditions would otherwise fill the underlying shape

Note:

- this layer should prove behavior by inputs/outputs, not by asserting which
  helper function was called

### D. Synthetic Path / Execution Model Semantics

These are unit tests around local path semantics in the backtest execution
model.

1. open-gap `crosses_above` trigger recognition is preserved at the first
   executable next-bar point
2. open-gap `crosses_below` trigger recognition is preserved at the first
   executable next-bar point
3. intrabar stop crossing is recognized causally on the approved canonical
   intrabar path:
   - bullish bar: `open -> low -> high -> close`
   - bearish bar: `open -> high -> low -> close`
4. stop recognition does not distort unrelated existing limit-crossing behavior
5. for future `stop_limit`, only the post-trigger tail is eligible for limit
   matching
6. trigger-tick inclusivity is respected for future `stop_limit` matching
7. exact equality with the trigger price at the first eligible executable point
   counts as a trigger
8. when multiple dormant stops are crossed in the same canonical segment, the
   execution model emits decisive trigger prices for all of them in segment
   order instead of collapsing them into one synthetic point

### E. Engine Integration Semantics For `stop_market`

These are integration tests through `BacktestEngine.run(...)`.

1. bar-created `stop_market` activates on the next bar only
2. buy `stop_market` with inferred `crosses_above` gap-through fills at the
   first executable next-bar point
3. buy `stop_market` with inferred `crosses_below` gap-through fills at the
   first executable next-bar point
4. sell `stop_market` with inferred `crosses_above` gap-through fills at the
   first executable next-bar point
5. sell `stop_market` with inferred `crosses_below` gap-through fills at the
   first executable next-bar point
6. buy `stop_market` with inferred `crosses_above` intrabar trigger fills on
   the same decisive executable point
7. buy `stop_market` with inferred `crosses_below` intrabar trigger fills on
   the same decisive executable point
8. sell `stop_market` with inferred `crosses_above` intrabar trigger fills on
   the same decisive executable point
9. sell `stop_market` with inferred `crosses_below` intrabar trigger fills on
   the same decisive executable point
10. untriggered `stop_market` carries forward without trade-log entries
11. repeated exit signals plus dormant stops do not create accidental extra
   fills
12. existing active orders retain priority ahead of newly triggered stops on the
   same executable point
13. multiple newly triggered stops preserve working-order / order-id ordering
14. long-only `sell(stop_market)` while flat remains a no-op
15. a stop order submitted on bar N cannot trigger from stale or pre-submit
    history and only becomes eligible on fresh post-submit executable data
16. the first shipped backtest trigger source uses synthetic executable
    `TickEvent.last` with inclusive equality at the trigger boundary
17. exact-equality `crosses_above` and `crosses_below` cases both trigger and
    fill at the first eligible executable point
18. multiple dormant stops crossed inside the same executable segment trigger
    in causal price order and preserve working-order / order-id ordering inside
    each decisive point

### F. Integration Semantics Reserved For First `stop_limit` Slice

These tests do not need to ship in the first `stop_market` implementation, but
they should be planned now so the first design does not make them awkward.

1. `StopLimitOrder` starts dormant and unexecutable with a persisted
   `trigger_condition`
2. dormant `StopLimitOrder` is invisible to working-limit crossing and matching
3. triggered `stop_limit` uses the same limit-fill semantics as ordinary limit
   execution
4. once triggered, `StopLimitOrder` becomes an ordinary working limit order
5. trigger upgrades the order before the engine evaluates the remainder of the
   current synthetic path
6. the trigger tick itself is included in the post-trigger tail
7. `crosses_above` gap-through trigger creates a working limit that may or may
   not fill depending on the post-trigger tail
8. `crosses_below` gap-through trigger creates a working limit that may or may
   not fill depending on the post-trigger tail
9. intrabar trigger followed by same-bar tail touch fills
10. intrabar trigger without tail touch stays open
11. pre-trigger path touch does not count as a fill
12. triggered stop-limit remains pending across bars when not yet filled
13. trigger tick is included in the post-trigger tail for same-bar eligibility

### G. Canonical Public Regression Scenarios

Once the first slice is stable, keep a small canonical regression set.

Recommended first candidates:

1. simple `crosses_above` `stop_market` entry strategy
2. simple `crosses_below` `stop_market` entry or exit strategy

These should assert public outcomes:

- trade log
- summary
- final state

without overfitting to internal helpers.

## Recommended File Placement

Recommended first target files:

- `tests/unit/trading/test_orders.py`
- `tests/unit/trading/test_matching_and_state.py`
- `tests/unit/trading/test_contracts.py`
- `tests/unit/backtest/test_execution_model.py`
- `tests/unit/research/test_strategy_surface.py`
- `tests/integration/research/test_backtest_execution_semantics.py`

Optional later contract file:

- `tests/integration/research/test_canonical_stop_market_contract.py`

## What The Later Implementation Plan Should Do With This

The implementation plan should:

1. translate the unit scenarios into small failing tests first
2. add only the minimum code to make each unit contract pass
3. then add integration scenarios in small batches
4. defer canonical regression tests until the public slice is stable enough to
   justify fixed fixture-based outputs

This order preserves readability and keeps the test suite from collapsing into
one giant stop-order integration blob.

## Evaluator Review

- Findings:
  - The user's stated testing goals are compatible with current repo
    conventions and with the strongest comparator practices.
  - The best fit for `quantcraft` is:
    - LEAN-style contract-focused local tests
    - Freqtrade-style breadth of scenario coverage
    - Nautilus-style cross-boundary trigger invariant checks
    - current `quantcraft`-style readable `TimeBar` integration scenarios
  - The document therefore recommends a split matrix rather than a single giant
    scenario table or a single happy-path contract test.
- Verification evidence:
  - comparator reads over:
    - `/tmp/quant-sizing-survey/backtesting.py/backtesting/test/_test.py`
    - `/tmp/freqtrade/tests/optimize/test_backtest_detail.py`
    - `/tmp/lean/Tests/Common/Orders/Fills/EquityFillModelTests.StopMarketFill.cs`
    - `/tmp/lean/Tests/Common/Orders/Fills/EquityFillModelTests.cs`
    - `/tmp/nautilus_trader/tests/integration_tests/adapters/binance/test_execution_handlers.py`
  - repo-local reads over:
    - `docs/references/testing.md`
    - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
    - `tests/integration/research/test_backtest_execution_semantics.py`
- Final disposition:
  - `complete`
