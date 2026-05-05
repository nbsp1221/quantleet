# Active Plan

- Date: `2026-04-27`
- Task: `Review and harden stop-limit spec/test planning before implementation planning`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki (thread user)`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Use read-only subagent review to validate the current stop-limit product
    spec and test scenario planning artifact before writing the implementation
    plan.
  - Fix objective documentation gaps that can be settled by repo governance,
    current code shape, and external best-practice evidence.
  - Leave product-intent decisions open for the human when no universal
    exchange or testing best practice determines the answer.
- Governing docs:
  - `AGENTS.md`
  - `docs/PLANS.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/plans/2026-04-27-stop-limit-test-scenarios.md`
  - `docs/design-docs/golden-principles.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/references/testing.md`
- Why these are governing:
  - They define repo workflow, planned product behavior, test-design intent,
    documentation lifecycle rules, causal execution semantics, and the testing
    contract for the later TDD implementation slice.
- In-repo scope:
  - Update the stop-limit product spec and test scenario planning artifact.
  - Record subagent review synthesis and fresh verification evidence in this
    active plan.
- Out-of-repo scope:
  - Read-only web review of stop-limit order concepts and testing/documentation
    best practices, as requested in the thread.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only review/hardening approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to actively use `$subagent-orchestration`, review
      the current stop-limit spec and test document from multiple angles, fix
      best-practice-settled issues, and ask back when human intent is required.
    - Granted scope:
      docs-only review and hardening for stop-limit implementation planning;
      task-limited read-only web research; no runtime implementation.
    - Expiration:
      end of this `2026-04-27` review slice.
    - Audit reference:
      this active plan.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check`
- Success criteria:
  - Read-only subagent review covers product semantics, testing strategy,
    documentation governance, and implementation readiness.
  - Objective findings are either fixed in the docs or explicitly rejected with
    evidence.
  - Human-intent-dependent decisions are separated from best-practice-settled
    decisions.
  - Product spec remains the long-lived product contract.
  - Test scenario planning remains the pre-implementation test-design input for
    the later TDD plan.
  - Verification commands pass.
- Out of scope:
  - Writing implementation code.
  - Writing tests.
  - Creating the actual stop-limit implementation plan.
  - Expanding scope into venue-specific order constraints, live/paper trading,
    `qty_percent + stop_limit`, brackets/OCO/OTO, or shorting.

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Accept only after the docs route a later implementation agent to the right
    artifacts, the known objective gaps are closed, and remaining product
    choices are surfaced as human questions instead of being silently assumed.
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - Subagent findings must be synthesized, not copied wholesale.
  - Fixes must reduce drift or improve test implementability without changing
    unresolved product intent.
- Checks the evaluator will use:
  - Compare changes against subagent findings.
  - Compare product spec and test scenario plan for duplicate-contract risk.
  - Run fresh repository/document checks.
- Auto-fail conditions:
  - changing runtime code in this docs-only slice
  - burying a human product decision as an implementation detail
  - leaving the next implementation plan without a clear document path
  - making the product spec a duplicate scenario catalog again

## Generator Work Log

- Planned slice order:
  1. Read subagent-orchestration guidance.
  2. Read the current stop-limit spec, test scenario plan, indexes, and current
     code shape.
  3. Run review fan-out across product semantics, testing, documentation
     governance, and implementation readiness.
  4. Synthesize objective fixes and human-intent questions.
  5. Apply docs-only hardening changes.
  6. Run verification.
  7. Record evaluator findings and final disposition.
- Notes:
  - Write ownership stays with the parent agent.
  - Subagents are read-only reviewers.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
  - No blocking documentation-governance findings remain after hardening.
  - Subagent review fan-out covered four independent lenses:
    - product semantics and exchange/broker concept alignment
    - testing strategy and TDD readiness
    - documentation governance and drift risk
    - implementation readiness against current source shape
  - Objective findings fixed:
    - `docs/product-specs/stop-limit.md` now links to the test scenario plan
      and labels it as planning input, not a second product authority.
    - The product spec's detailed duplicate test checklist was collapsed into
      product-level coverage expectations.
    - The test scenario catalog now covers missing sizing and mixed
      `quantity + qty_percent` request shapes.
    - Post-trigger tail examples now cross beyond the limit and assert the
      conservative limit crossing price, not the better path endpoint.
    - Priority testing now names a deterministic constrained-cash setup instead
      of leaving observability conditional.
    - A source-based public `BacktestEngine.run(source=..., strategy=...)`
      scenario was added.
    - Runtime retrigger wording now targets the observable runtime contract
      instead of forcing direct `Order.trigger()` idempotence.
    - Dormant stop-limit buy reservation behavior is now part of the minimum
      test batch.
  - Objective findings intentionally not implemented as product changes:
    - No public open-order result surface was added; engine tests should infer
      triggered unfilled persistence via later fills, while domain/runtime tests
      cover internal order state.
  - Human-intent-dependent findings remain open for the next step:
    - whether first-slice `stop_limit` should stay a generic conditional limit
      order with close-inferred trigger direction, rather than venue-style
      side-derived stop semantics or separate take-profit/stop-loss names
    - whether `stop_price == active_bar_close` should remain rejected as
      ambiguous, become already-triggered behavior, or require an explicit
      trigger direction
    - whether existing-before-newly-triggered priority is the intended
      deterministic `quantleet` backtest policy
- Verification evidence:
  - `uv run poe repo-check`
    - output:
      - `Poe => uv run python scripts/repo_check.py`
      - `repository checks passed`
  - `git diff --check`
    - output: no whitespace errors reported
- Final disposition:
  - `complete`
