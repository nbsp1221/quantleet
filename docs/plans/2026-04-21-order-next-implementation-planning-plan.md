# Active Plan

- Date: `2026-04-21`
- Task: `Write and review the next concrete Order implementation plan`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Produce one concrete, repository-local implementation plan for the next
  `quantcraft.trading` slice after the current runtime-Order seam and
  lifecycle/sizing design drafts. The plan must state what code should change
  next, what must stay deferred, how the work should be verified, and why that
  sequence is narrower and safer than the main alternatives.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow, Tier A safety boundary, current shipped
    backtest/research scope, the design-doc routing authority, package
    structure, the canonical backtest path/matching boundary, and the
    documentation governance model this planning slice must preserve.
- Supporting references:
  - `docs/references/openai-harness-engineering.md`
  - `https://www.anthropic.com/engineering/harness-design-long-running-apps`
  - `docs/design-docs/order-domain-runtime-design.md`
  - `docs/design-docs/order-runtime-model-design.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - official docs and local comparator-source evidence already captured in:
    - `docs/research/2026-04-20-order-runtime-model-comparison.md`
    - `docs/research/2026-04-20-order-lifecycle-and-sizing-comparison.md`
- Why these references matter:
  - The user explicitly requires a harness-style process where the agent gathers
    support and rebuttal evidence, converges through review, and only then
    reports the final implementation direction for approval/rejection.
- In-repo scope:
  - Create one concrete implementation plan under `docs/plans/`.
  - Update this active plan with review findings and verification evidence.
  - Make only discoverability updates that are strictly needed for plan
    legibility.
- Out-of-repo scope:
  - No Python implementation changes.
  - No product-spec changes.
  - No promotion of draft design docs into governing authority.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to create the concrete implementation plan and to
      use `$subagent-orchestration` plus support/rebuttal review before final
      reporting
    - Granted scope:
      docs-only planning and review for the next `trading` implementation
      slice, including read-only comparison against existing repository code and
      prior local/external research evidence
    - Expiration:
      end of this `2026-04-21` implementation-planning slice
    - Audit reference:
      this active plan and the resulting implementation-plan document
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository has one concrete implementation plan that clearly states the
    next code slice, file touchpoints, sequencing, verification, and deferred
    follow-ups.
  - The plan explicitly records why that slice was chosen over broader or more
    speculative alternatives.
  - Review fan-out includes at least one contrarian pass.
  - Final review converges to `approved: no material findings`.
  - `uv run poe repo-check` passes after doc changes.
- Out of scope:
  - Implementing stop orders
  - Implementing percentage sizing in code
  - Changing public strategy syntax
  - Designing the full OMS, portfolio, ledger, or live runtime

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the implementation plan is concrete enough that
    a future agent can execute it without guessing the next code slice, yet
    narrow enough to avoid reopening full OMS or sizing-system design.
- Acceptance artifact location:
  - `docs/plans/2026-04-21-order-stop-market-implementation-plan.md`
- How the generator and evaluator agreed on done before execution:
  - This slice is done when the implementation plan answers:
    1. what code should change next
    2. why this is the next slice instead of broader alternatives
    3. how the work will be verified
    4. what remains intentionally deferred
- Checks the evaluator will use:
  - Compare the plan against current code truth and the draft design docs.
  - Check the chosen slice against
    `docs/design-docs/backtest-execution-semantics.md` for canonical path,
    conservative executable-price, and matching-boundary compliance.
  - Check that the plan chooses one bounded next slice instead of mixing stop,
    sizing, UX, and live-runtime work together.
  - Check fan-out outputs for explicit support and rebuttal reasoning.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - The plan implicitly reopens product direction instead of following the
    already-fixed intent.
  - The plan mixes multiple hard seams into one code slice without a strong
    justification.
  - The plan invents unsupported current-code behavior.
  - Review fan-out lacks a contrarian pass or unresolved objections remain.

## Generator Work Log

- Planned slice order:
  1. Gather the current code truth and the current draft design conclusions.
  2. Fan out read-only subagents for:
     - implementation-sequence recommendation
     - contrarian overdesign rebuttal
     - verification/testability review
  3. Synthesize the evidence into one concrete implementation plan.
  4. Run review fan-out on the written plan.
  5. Revise until all reviewers agree there are no material findings.
  6. Run `uv run poe repo-check` and close the plan.
- Notes:
  - Parent agent owns all writes.
  - Delegated work stays read-only and evidence-bearing.
  - The worktree already contains unrelated uncommitted doc-routing changes from
    earlier slices; this planning slice must not revert them.
- Blockers or scope changes:
  - Review fan-out repeatedly narrowed the implementation plan:
    1. product-spec edits were moved out of pre-code tasks and into final
       shipped-behavior sync
    2. same-tick stop-trigger ordering was made explicit
    3. the active-plan acceptance artifact path was corrected
    4. draft Order docs were moved from governing inputs to supporting
       references only

## Evaluator Review

- Findings:
  - Research/rebuttal fan-out converged on one bounded next slice:
    trigger-aware runtime `Order` plus end-to-end `stop_market`, with
    `stop_limit`, sizing, and UX cleanup explicitly deferred.
  - Review fan-out produced repeated material findings that were incorporated
    into the implementation plan:
    1. split kernel-local versus backtest/runtime contract assertions
    2. keep product-spec updates in the final shipped-behavior sync step
    3. pin the same-tick two-phase priority rule, including within-phase order
    4. keep draft Order docs advisory rather than governing for this planning
       slice
  - Final plan artifact under review:
    `docs/plans/2026-04-21-order-stop-market-implementation-plan.md`
  - Final clean reviewer dispositions were recorded on the last passing state
    for:
    1. the planning artifact pair
    2. the stop-market implementation plan content
    3. the docs-only execution handoff wrapper
- Verification evidence:
  - `uv run poe repo-check`
    -> `repository checks passed`
- Final disposition:
  - `complete`
