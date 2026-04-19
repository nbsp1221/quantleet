# Active Plan

- Date: `2026-04-19`
- Task: `Design the trading kernel canonical model v1`
- Status: `blocked`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Run a design-session workflow for a future `trading` kernel canonical model
  which can support coherent strategy-to-runtime semantics across backtest,
  paper, and live trading.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/design-docs/unified-strategy-runtime-design.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-18-trading-kernel-architecture-insights.md`
- Why these are governing:
  - They define the repo workflow, current shipped scope, package ownership,
    backtest semantics, future runtime direction, and the dated research note
    produced from the prior architecture investigation.
- In-repo scope:
  - Explore and refine the design in conversation.
  - Write a dated design document under `docs/plans/` once the design is
    approved in the session.
- Out-of-repo scope:
  - No implementation changes.
  - No promotion into governing design-doc authority in this slice.
- Tier A progression requested: `no`
- Approval record, if required:
  - No Tier A implementation is planned in this slice. This is a design-only
    workflow artifact and discussion record.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The design conversation reaches an approved shape for the canonical model.
  - A dated design note is written in `docs/plans/`.
  - The note clearly distinguishes current truth from future model direction.
  - `uv run poe repo-check` passes after documentation changes.
- Out of scope:
  - Writing implementation code
  - Changing shipped public APIs
  - Editing governing design docs directly

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the design has been presented, accepted by the
    user, written to a dated design note, and repo checks pass.
- Acceptance artifact location:
  - `docs/plans/2026-04-19-trading-kernel-canonical-model-design.md`
- How the generator and evaluator agreed on done before execution:
  - The design is done when the user approves the proposed model and the note
    faithfully captures that approved shape.
- Checks the evaluator will use:
  - Compare the resulting design note against governing docs for conflicts.
  - Verify the note remains non-governing.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Skipping clarifying/design steps and jumping to implementation
  - Writing a design note before user approval
  - Contradicting current architecture boundaries without explicitly framing the
    change as future-facing

## Generator Work Log

- Planned slice order:
  1. Review context and prior research.
  2. Ask one clarifying question at a time.
  3. Propose 2-3 candidate canonical-model approaches.
  4. Present a recommended design in sections.
  5. Write the approved design note.
  6. Run repo verification and close the plan.
- Notes:
  - This is a design-session workflow, not an implementation slice.
- Blockers or scope changes:
  - Scope narrowed on `2026-04-19` to the smaller and currently decisive
    `Order` domain slice. Follow-on work continues under
    `docs/plans/2026-04-19-order-domain-spec-design-plan.md`.

## Evaluator Review

- Findings:
  - Pending.
- Verification evidence:
  - Pending.
- Final disposition:
  - Superseded by the narrower active plan at
    `docs/plans/2026-04-19-order-domain-spec-design-plan.md`.
