# Active Plan

- Date: `2026-04-26`
- Task: `Correct stop_market real-world validation candidates to standalone order scope`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - revise the stop-market real-world validation candidate document so it only
    contains strategies that are expressible with the currently shipped
    standalone `stop_market` surface
  - explicitly remove or defer attached protective stop, OTO, OCO, and bracket
    patterns from the current validation candidate set
  - use fresh web research to ground the replacement candidates in recognizable
    real-world trading patterns
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
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-test-matrix-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-implementation-plan.md`
  - `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
- Why these are governing:
  - They define the shipped `stop_market` scope, the current long-only
    research surface, the active plan workflow, and the validation candidate
    document being corrected.
- In-repo scope:
  - add this active plan
  - update `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
- Out-of-repo scope:
  - web research for standalone stop-market strategy patterns
- Tier A progression requested: `yes`
- Approval record, if required:
  - Tier A and scope-expansion approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread direction on `2026-04-26` to research standalone
      stop-market strategies via web search and update the strategy candidate
      document
    - Granted scope:
      repository-local documentation changes plus task-driven web research
    - Expiration:
      end of this correction slice
    - Audit reference:
      this active plan and the stop-trigger governing plan documents listed
      above
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - candidate document no longer treats attached protective stop, OTO, OCO, or
    bracket semantics as current validation candidates
  - document contains three standalone stop-market strategy candidates that can
    be expressed with `on_bar()` order submission
  - each candidate states why it is realistic and why it fits the current
    shipped scope
  - final report distinguishes corrected current candidates from future
    attached-order validation work
- Out of scope:
  - changing runtime code
  - rerunning cross-validation
  - implementing OTO, OCO, bracket, `stop_limit`, or new order helpers

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - accept only if the candidate document is internally consistent with the
    shipped standalone `stop_market` scope and fresh repository checks pass
- Acceptance artifact location:
  - this active plan
  - `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
- How the generator and evaluator agreed on done before execution:
  - done means the previous attached-order candidate set is replaced by three
    standalone stop-market candidates grounded in external strategy references
- Checks the evaluator will use:
  - inspect the updated candidate document
  - run `uv run poe repo-check`
- Auto-fail conditions:
  - leaving current candidates that require parent-fill child activation
  - claiming bracket-like or protective attached stops are current shipped
    validation candidates
  - missing fresh verification evidence

## Generator Work Log

- Planned slice order:
  1. research external standalone stop-market strategy patterns
  2. rewrite the candidate document around current shipped scope
  3. run `uv run poe repo-check`
  4. update evaluator findings and report
- Notes:
  - current standalone validation should focus on stop-market entries and
    independent signal/time exits, because attached protective stops require a
    future parent-child order lifecycle
  - web research supported three standalone stop-entry patterns:
    opening range breakout, Turtle/Donchian channel breakout, and inside-bar
    breakout
  - the candidate document now explicitly defers attached protective stops,
    bracket orders, OTO, and OCO validation
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No material mismatch found against the active plan.
  - `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
    now limits current validation candidates to standalone `stop_market`
    entries plus independent exits.
  - Previous limit-entry and market-entry protective stop candidates are no
    longer treated as current validation candidates; they are recorded as
    deferred attached-order work.
  - The three current candidates are:
    - opening range breakout stop entry
    - Donchian / Turtle-style breakout stop entry
    - inside-bar breakout stop entry
- Verification evidence:
  - `uv run poe repo-check`
  - Result: `repository checks passed`
- Final disposition:
  - `accepted`
