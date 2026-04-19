# Active Plan

- Date: `2026-04-19`
- Task: `Design the Order domain spec and OrderIntent/runtime Order boundary`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Produce a future-facing but implementation-grounded design note for the
  `trading` Order domain slice. The note should define the recommended boundary
  between strategy-facing `OrderIntent` and runtime-managed `Order`, including
  the minimum lifecycle seam needed to later support immediately executable and
  stop-triggered orders without architecture breakage.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the workflow contract, current MVP scope, bounded-context
    ownership, package naming rules, and the shared-kernel backtest boundary
    that this Order slice must not contradict.
- In-repo scope:
  - Create one active design-session plan for this narrower Order slice.
  - Run read-only research and counterargument analysis.
  - Write one draft design/spec note under `docs/design-docs/`.
  - Record evaluator findings and verification evidence in this plan.
- Out-of-repo scope:
  - No implementation changes.
  - No edits to governing design docs in this slice.
  - No promotion of this note into architecture authority.
- Tier A progression requested: `no`
- Approval record, if required:
  - No Tier A implementation is planned. This slice is design-only and remains
    non-governing until a later approved promotion or implementation plan.
  - Tier A design-slice approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to proceed with the Order-domain spec workflow and
      use `$subagent-orchestration` aggressively for review and design closure
    - Granted scope:
      docs-only Order-domain design work in the Tier A `trading` context,
      including review closure for this planning slice; no implementation code
      or trading-state mutation approved
    - Expiration:
      end of this `2026-04-19` Order-domain design slice
    - Audit reference:
      this active plan plus the resulting draft design doc
  - External research approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread instructions to use web search and, if needed, inspect
      reference-library source in `/tmp` via direct clone/read for comparison
      research; human identity resolved from local `git config user.name`
    - Granted scope:
      read-only external architecture research, official docs, and temporary
      `/tmp` source inspection for comparative evidence only
    - Expiration:
      end of this `2026-04-19` Order-domain design slice
    - Audit reference:
      this active plan plus the cited evidence in the draft design note
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The Order-domain design note clearly distinguishes current repo truth from
    recommended future shape.
  - The note covers `OrderIntent` vs runtime `Order` boundary, minimum runtime
    lifecycle, and stop-order accommodation without claiming implementation
    exists today.
  - The recommendation is based on explicit support and rebuttal evidence, not
    assertion.
  - Read-only subagent research and review loops are synthesized in the parent
    agent.
  - `uv run poe repo-check` passes after documentation updates.
- Out of scope:
  - Writing or modifying Python implementation code
  - Defining full `Portfolio`, `Ledger`, or allocator models
  - Designing the complete paper/live runtime
  - Changing shipped public strategy APIs

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the design note exists, cites current-repo truth
    accurately, captures the final recommendation with rebuttal analysis, has
    been reviewed through bounded subagent fan-out, and passes repo checks.
- Acceptance artifact location:
  - `docs/design-docs/order-domain-runtime-design.md`
- How the generator and evaluator agreed on done before execution:
  - This slice is done when the note is narrow, evidence-backed, explicitly
    non-governing, and review feedback leaves no material findings.
- Checks the evaluator will use:
  - Compare the note against governing docs for contradictions.
  - Compare claims against current repository implementation.
  - Review subagent outputs for evidence quality and unresolved conflicts.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Expanding into full kernel/portfolio/runtime design
  - Treating future design as current implementation truth
  - Accepting summary-only subagent output without evidence
  - Skipping review synthesis after fan-out

## Generator Work Log

- Planned slice order:
  1. Gather current repo truth and governing boundaries.
  2. Run read-only research fan-out:
     - supporting evidence for a rich runtime `Order`
     - opposing evidence and “design smaller” counterarguments
     - comparable library patterns for order lifecycle boundaries
  3. Synthesize one recommendation and rejected alternatives.
  4. Write the dated design/spec note.
  5. Run review fan-out on the note and revise if needed.
  6. Run repo verification and close the plan.
- Notes:
  - Write ownership stays with the parent agent.
  - Delegated work is read-only and evidence-bearing.
  - Draft and research-only context consulted during synthesis but not treated
    as governing authority:
    - `docs/design-docs/unified-strategy-runtime-design.md`
    - `docs/plans/2026-04-18-trading-kernel-architecture-insights.md`
- Blockers or scope changes:
  - None yet.

## Evaluator Review

- Findings:
  - Initial reviewer fan-out found four material issues and they were fixed:
    1. moved the durable design artifact out of `docs/plans/` into
       `docs/design-docs/`
    2. narrowed the Order seam to avoid premature OMS scope
    3. corrected current-repo truth statements and local evidence anchors
    4. added explicit Tier A design-slice and external-research approval
       records in the active plan
  - Follow-up reviewer passes after those fixes reported no material findings on
    scope/YAGNI, current-repo truth, or governance fit, aside from the plan
    needing its evaluator artifact completed. That bookkeeping issue is closed
    in this section.
  - Final truth-only approval pass returned `approved: no material findings`
    after the last low-severity wording and citation fixes.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed` on `2026-04-19`
- Final disposition:
  - `complete`
