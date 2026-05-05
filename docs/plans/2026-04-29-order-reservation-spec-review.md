# Order Reservation Spec Review Plan

- Date: `2026-04-29`
- Task: `Review order reservation policy and test scenario specs`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki (thread user)`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Use subagent review fan-out to evaluate the order reservation policy spec
    and test scenario planning artifact before implementation planning begins.
  - Apply clear best-practice fixes directly, and collect only human-intent
    questions that cannot be resolved from the existing documents.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/PLANS.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/references/testing.md`
  - `docs/product-specs/order-reservation.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/plans/2026-04-29-order-reservation-test-scenarios.md`
- Why these are governing:
  - They define repo workflow, Tier A handling, product contract authority,
    testing taxonomy, and the exact documents under review.
- In-repo scope:
  - Review and, if needed, update the order reservation policy spec, test
    scenario planning artifact, and this review plan.
  - Keep changes documentation-only.
- Out-of-repo scope:
  - None planned. External testing best-practice links already recorded in the
    test scenario artifact may be used as review context.
- Tier A progression requested: `yes`
- Approval record, if required:
  - Requestor: `Naki (thread user)`
  - Human approver: `Naki (thread user)`
  - Verification marker:
    explicit thread request on `2026-04-29` to use Subagent Orchestration for
    reviewing the order reservation policy spec and test scenario spec before
    implementation planning.
  - Granted scope:
    docs-only review and best-practice cleanup for the order reservation policy
    and test scenario specs.
  - Expiration:
    end of this review slice.
  - Audit reference:
    this active plan.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - At least four independent read-only review lenses evaluate the documents.
  - Findings are synthesized, deduplicated, and classified as auto-fix,
    no-change, or human-intent question.
  - Clear correctness, clarity, scope, and testability fixes are reflected in
    the docs without changing runtime behavior.
  - Human-intent questions are reported separately instead of guessed.
  - `uv run poe repo-check` passes after any document update.
- Out of scope:
  - Writing implementation code.
  - Writing executable tests.
  - Changing runtime behavior.
  - Changing the core product decision unless the user explicitly redirects.

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close only after review evidence is recorded, meaningful fixes are applied,
    unresolved human-intent questions are separated, and repo-doc verification
    passes.
- Acceptance artifact location:
  - This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution:
  - Review agents must provide evidence from the documents. Parent agent owns
    final judgment and writes any doc changes.
- Checks the evaluator will use:
  - Compare final docs against product intent and testing best practices.
  - Confirm no implementation files changed.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Skipping synthesis after subagent fan-out.
  - Applying subjective product-scope changes without human approval.
  - Leaving known doc contradictions unresolved.
  - Changing production code.

## Generator Work Log

- Planned slice order:
  1. Create this active review plan.
  2. Dispatch read-only subagents for product semantics, architecture/runtime
     boundaries, testing strategy, and adversarial scope/edge-case review.
  3. Synthesize findings.
  4. Apply clear best-practice doc fixes.
  5. Run repo checks.
  6. Record evaluator review and final disposition.
- Notes:
  - Subagent review fan-out completed with four read-only lenses:
    product semantics/coherence, architecture/runtime boundaries,
    testing strategy, and adversarial edge-case review.
  - Product semantics review found no meaningful contradiction between the
    planned reservation policy and adjacent current-scope documents.
  - Architecture review confirmed the main boundary is sound, then requested
    clearer test-lane wording so `trading` tests never receive raw
    `qty_percent` requests and reservation shrink remains outside
    `quantleet.trading.domain.Order`.
  - Testing-strategy review requested ordinary market-slippage and limit-fee
    cases, and clarified that lifecycle release is deferred rather than an MVP
    hook.
  - Adversarial review requested explicit-vs-percent competition, same-event
    priority, triggered-but-unfilled stop-limit competition, and partial-fill
    price-improvement cases.
- Blockers or scope changes:
  - Implementation planning was blocked on human-intent questions recorded in
    `docs/product-specs/order-reservation.md` and
    `docs/plans/2026-04-29-order-reservation-test-scenarios.md`.
  - Those questions were answered in the follow-up product discussion on
    `2026-04-29` and recorded in the documents under review.

## Evaluator Review

- Findings:
  - Auto-fixed:
    - Added ordinary market-slippage and ordinary limit-fee test scenarios.
    - Clarified lifecycle release as deferred scope rather than an MVP hook.
    - Reworded `tests/unit/trading/` placement so raw `qty_percent` never
      belongs in trading-level tests.
    - Split reservation-shrink testing away from domain `Order` ownership.
    - Added explicit-vs-percent same-cycle competition scenarios.
    - Added same-event priority coverage.
    - Added triggered-but-unfilled stop-limit reservation competition coverage.
    - Added a partial-fill price-improvement reservation arithmetic scenario.
  - No-change:
    - Product semantics remain coherent: stop-family orders are trigger
      overlays, `qty_percent` is strategy/request syntax, and runtime `Order`
      remains quantity-based.
  - Human-intent questions closed:
    - Stop-market gap overspend rejects with an observable event when the
      modeled execution price is unaffordable.
    - Invalid request shape raises validation errors; valid runtime/account
      failures emit explicit rejection events.
    - Reservation and rejection ownership belongs to the runtime/account-control
      layer, while domain `Order` owns order invariants.
- Verification evidence:
  - `uv run poe repo-check`: `repository checks passed`.
- Final disposition:
  - Review fan-out, auto-fix slice, and human-intent closure are complete.
    Implementation planning may begin from the recorded policy decisions.
