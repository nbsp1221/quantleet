# Active Plan

- Date: `2026-04-23`
- Task: `Document real-world validation strategies for the shipped stop_market slice`
- Status: `complete`
- Risk class: `Tier C`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Record three realistic strategy patterns that can be expressed today with
    the shipped `stop_market` slice and are suitable for high-confidence
    end-to-end validation.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-test-matrix-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-execution.md`
- Why these are governing:
  - They define the current shipped strategy surface, backtest semantics, and
    stop-market scope that this documentation must not overstate.
- In-repo scope:
  - Add one documentation artifact under `docs/plans/`
  - Update this active plan with verification evidence
- Out-of-repo scope:
  - no code changes
  - no new external dependencies
- Tier A progression requested: `no`
- Approval record, if required:
  - Not required; documentation-only Tier C slice.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The document clearly states whether each proposed strategy is expressible
    today.
  - The document distinguishes shipped behavior from deferred behavior such as
    `stop_limit`, trailing stops, and OCO.
  - The document is suitable to guide future integration/canonical validation
    tests.
- Out of scope:
  - implementing new strategies in tests
  - changing current shipped semantics

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Accept only if the document stays within current shipped truth and gives a
    technically accurate answer about what can be expressed today.
- Acceptance artifact location:
  - this active plan
  - `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
- How the generator and evaluator agreed on done before execution:
  - The document must answer the user's immediate question first: all three
    candidate strategies are possible today, with explicit caveats where the
    runtime relies on existing long-only cleanup semantics instead of a true
    OCO/bracket primitive.
- Checks the evaluator will use:
  - compare statements in the document against current shipped product specs
  - run `uv run poe repo-check`
- Auto-fail conditions:
  - claiming `stop_limit` is shipped
  - claiming trailing stops are shipped
  - claiming true OCO/bracket semantics are shipped

## Generator Work Log

- Planned slice order:
  1. Confirm current shipped surface can express the three candidate patterns.
  2. Write the validation-strategy document with caveats.
  3. Run repo checks.
- Notes:
  - This is a documentation-only slice.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No unresolved findings.
  - The document stays within current shipped truth:
    - all three candidate strategies are expressible today
    - `stop_limit`, trailing stops, and true OCO/bracket primitives are still
      documented as deferred
  - The main caveat is preserved explicitly: simultaneous TP/SL behavior is
    currently validation-suitable because remaining sell exits are safely
    discarded when flat, not because a linked bracket primitive is shipped.
- Verification evidence:
  - `uv run poe repo-check`
  - Result: `repository checks passed`
- Final disposition:
  - `accepted`
