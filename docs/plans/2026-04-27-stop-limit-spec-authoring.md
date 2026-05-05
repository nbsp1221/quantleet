# Active Plan

- Date: `2026-04-27`
- Task: `Author the stop-limit product spec and validate it against exchange practice`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - write the first repository product spec for `stop_limit` orders before
    implementation, grounded in current `quantleet` order architecture and
    external exchange/broker order semantics
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repository workflow, product-spec routing, capability
    ownership, Tier A safety boundary, existing backtest/research behavior, and
    the stop-family order lifecycle direction this spec must preserve.
- In-repo scope:
  - create `docs/product-specs/stop-limit.md`
  - add the stop-limit spec to `docs/product-specs/index.md`
  - record planner/evaluator findings and verification evidence in this active
    plan
- Out-of-repo scope:
  - read-only web research against official exchange/broker support or API
    documentation for stop-limit semantics
  - no live service calls, credentials, trading, or external code changes
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only design/spec approval record:
    - Requestor: `thread user`
    - Human approver: `thread user`
    - Verification marker:
      explicit thread request to draft the stop-limit spec, actively use
      subagent review, and verify best practices plus real exchange concepts
      with web search before final reporting
    - Granted scope:
      docs-only Tier A product-spec work for stop-limit order semantics;
      read-only web research against official exchange/broker materials;
      no implementation
    - Expiration:
      end of this `2026-04-27` spec-authoring slice
    - Audit reference:
      this active plan
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - `docs/product-specs/stop-limit.md` exists and clearly defines:
    - public strategy UX
    - trigger and limit-price validation
    - dormant-to-triggered lifecycle
    - backtest gap and intrabar execution semantics
    - sizing scope
    - included and excluded scope
    - canonical test matrix for the later implementation plan
  - the spec cites external official sources for stop-limit semantics and
    records how `quantleet` intentionally maps or narrows those concepts
  - read-only subagent review covers:
    - external exchange/broker best practice
    - repository architecture/spec conformance
    - user-flow and edge-case completeness
  - `uv run poe repo-check` passes
- Out of scope:
  - Python implementation
  - changing shipped runtime behavior
  - enabling live or paper execution
  - implementing `qty_percent + stop_limit`
  - implementing trailing stops, OCO, OTO, brackets, cancel/replace/modify, or
    shorting

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - accept only if the spec is internally coherent, repo-aligned, externally
    validated against real order semantics, and explicit about deferred scope
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - this slice is complete when a future implementation plan can use the spec
    without reopening the core questions about trigger lifecycle, limit fill
    semantics, gap-through non-execution, or first-slice sizing scope
- Checks the evaluator will use:
  - diff review against governing docs and current source shape
  - subagent research/review synthesis
  - official exchange/broker source cross-check
  - fresh `uv run poe repo-check`
- Auto-fail conditions:
  - spec treats `stop_limit` as a bar-aware shortcut instead of a triggered
    working limit order
  - spec allows pre-trigger price movement to fill a stop-limit order
  - spec silently widens scope into `%` sizing, brackets, trailing stops,
    paper/live execution, or shorting
  - spec lacks exchange/broker source evidence

## Generator Work Log

- Planned slice order:
  1. review current stop-market, limit, sizing, and execution-semantics docs
  2. research official external stop-limit semantics
  3. draft `docs/product-specs/stop-limit.md`
  4. add product-spec routing entry
  5. run read-only subagent research/review fan-out
  6. incorporate material findings
  7. run `uv run poe repo-check`
  8. complete evaluator review
- Notes:
  - Write ownership stays with the parent agent.
  - Subagents are read-only reviewers/researchers.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
  - Added `docs/product-specs/stop-limit.md` as the planned product contract
    for the first `stop_limit` slice.
  - Added the stop-limit spec to `docs/product-specs/index.md` so future
    implementation work routes through the new product authority.
  - External source synthesis:
    - Coinbase Advanced Trade, Binance.US, Interactive Brokers, and Kraken all
      describe stop-limit behavior as a stop/trigger price that activates or
      posts a limit order.
    - Interactive Brokers and Coinbase/Kraken materials explicitly support the
      risk that a stop-limit may not execute after trigger if the market moves
      through the limit or matching liquidity is unavailable.
    - Binance.US examples use the common buffered pattern:
      buy stop-limit with limit above stop, sell stop-limit with limit below
      stop.
    - Venue constraints differ. Coinbase documents price bands, Kraken exposes
      selectable trigger signals, and derivatives venues may expose mark,
      index, or contract-price trigger references. The spec keeps these as
      future venue/instrument constraints rather than hard-coded first-slice
      behavior.
  - Subagent review synthesis:
    - external best-practice research found the spec's core model matches real
      exchange/broker semantics and recommended documenting trigger reference,
      venue-specific constraints, and non-execution risk
    - repo/spec conformance review found the spec aligns with existing
      `PendingOrderRequest -> OrderIntent -> Order -> matching` seams and
      correctly defers `%` sizing
    - flow review identified the main implementation risk: same-bar post-trigger
      tail traversal must discover limit crossings after a mid-segment trigger
      without reusing pre-trigger path movement
  - Material findings incorporated:
    - `trigger_type="last"` is now explicit for the first slice
    - venue trigger references and price bands are documented as future
      constraints
    - order identity after trigger is specified as same order id and same
      `order_type="stop_limit"` unless implementation proves that impossible
    - trigger-only events remain internal and do not create public trade-log
      entries
    - same-bar post-trigger tail traversal is explicitly required
  - Scope remains intentionally narrow:
    - quantity-only `stop_limit`
    - single-symbol long/flat research/backtest workflow
    - no `%` sizing, trailing stops, attached orders, OCO/OTO/brackets,
      cancel/replace/modify, paper/live execution, shorting, or margin
- Verification evidence:
  - `uv run poe repo-check`
    - Result: `repository checks passed`
- Final disposition:
  - `accepted`
