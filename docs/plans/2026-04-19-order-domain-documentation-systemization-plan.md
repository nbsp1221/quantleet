# Active Plan

- Date: `2026-04-19`
- Task: `Systematize Order-domain documentation into research, spec, and implementation-plan artifacts`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Turn the recent Order-domain investigation into a clearer repository-local
  documentation set that AI agents can follow with lower ambiguity. This slice
  should separate:
  - research evidence
  - durable Order-domain spec/design direction
  - concrete implementation planning for the next code slice
  and should incorporate the newer architectural conclusions reached after the
  first Order-domain spec note was written.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the workflow contract, current package and bounded-context
    ownership, safety and approval requirements, and the repository-local
    documentation structure that the new Order-domain documents must respect.
- Supporting references:
  - `docs/references/openai-harness-engineering.md`
- Why these references matter:
  - They are not repo authority, but they reinforce the repository-local
    harness principles this slice should follow: humans steer, agents execute,
    repository docs are the system of record, and research/spec/plan roles
    should stay distinct.
- In-repo scope:
  - Create one active plan for this documentation slice.
  - Create or update one research artifact under `docs/research/`.
  - Update the durable Order-domain spec in `docs/design-docs/`.
  - Create one concrete Order-domain implementation plan under `docs/plans/`.
  - Update any relevant local indexes or routing docs required for
    discoverability.
  - Run bounded read-only subagent research and review loops, then synthesize
    them in the parent agent.
- Out-of-repo scope:
  - No Python implementation changes.
  - No external contract changes.
  - No promotion of draft design docs into governing authority.
- Tier A progression requested: `no`
- Approval record, if required:
  - No Tier A implementation is planned. This slice is documentation-only in a
    Tier A context.
  - Tier A design/plan approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to create or update a concrete implementation
      plan, keep docs clearly separated by role, and use
      `$subagent-orchestration` plus review loops until approved
    - Granted scope:
      docs-only work in the Tier A `trading` context, including spec updates,
      research-note authoring, implementation-plan authoring, and review
      closure; no code implementation approved
    - Expiration:
      end of this `2026-04-19` documentation-systemization slice
    - Audit reference:
      this active plan plus the resulting Order-domain docs
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository has a clearly separated Order-domain research note,
    durable draft spec, and concrete implementation plan.
  - The design doc reflects the newer decisions from the session, including the
    recommended Order responsibility split and event boundary guidance.
  - The implementation plan stays implementation-facing and does not collapse
    back into a research or architecture note.
  - The research artifact records support and rebuttal evidence rather than
    pretending to be authority.
  - Reviewer fan-out includes at least one adversarial or contrarian lens.
  - `uv run poe repo-check` passes after the documentation changes.
- Out of scope:
  - Editing Python source files
  - Designing the full portfolio, ledger, allocator, or paper/live runtime
  - Promoting draft Order-domain docs to governing status
  - Cleaning up all historical misfiled docs unrelated to this slice

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the Order-domain documents are role-separated,
    internally consistent, reviewed through bounded fan-out including a
    contrarian pass, and repo checks pass.
- Acceptance artifact location:
  - `docs/research/2026-04-19-order-domain-architecture-comparison.md`
  - `docs/design-docs/order-domain-runtime-design.md`
  - `docs/plans/2026-04-19-order-domain-runtime-implementation-plan.md`
- How the generator and evaluator agreed on done before execution:
  - This slice is done when the three document roles are clearly distinct,
    newer Order-domain decisions are reflected in the durable spec, and the
    implementation plan is specific enough to drive a later code slice without
    re-reading the whole conversation.
- Checks the evaluator will use:
  - Compare document roles and claims against the governing docs.
  - Compare the spec against current repository truth.
  - Check whether the implementation plan stays implementation-scoped.
  - Check reviewer outputs for evidence and unresolved objections.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Collapsing research, spec, and implementation planning into one document
  - Treating draft design or research notes as governing truth
  - Writing implementation details that contradict current package topology
  - Skipping synthesis after subagent fan-out

## Generator Work Log

- Planned slice order:
  1. Establish the active plan and acceptance contract.
  2. Run read-only subagent fan-out:
     - one structure-and-routing pass
     - one contrarian/rebuttal pass
     - one harness-protocol alignment pass
  3. Synthesize the desired doc split and update/create the documents.
  4. Run bounded review fan-out and revise until no material findings remain.
  5. Run repo verification and close the plan.
- Notes:
  - Parent agent owns all writes.
  - Delegated work stays read-only and evidence-bearing.
  - This slice follows the repository-local harness principle from
    `docs/references/openai-harness-engineering.md`: humans steer, agents
    execute, and the repository should hold the legible system of record.
- Blockers or scope changes:
  - Contrarian review pushed the durable spec and implementation plan to narrow
    the first code slice from “stop-ready trigger-aware seam” down to
    “runtime `Order` for current market/limit behavior, with stop-family
    pressure documented but deferred.”

## Evaluator Review

- Findings:
  - Initial research fan-out converged on the intended document split:
    - advisory evidence under `docs/research/`
    - durable but non-governing boundary note under `docs/design-docs/`
    - implementation-facing plan under `docs/plans/`
  - Contrarian fan-out found three material issues and they were fixed:
    1. the active plan incorrectly treated
       `docs/references/openai-harness-engineering.md` as governing authority
       instead of a supporting reference
    2. the draft design doc carried too much implementation detail and follow-on
       sequencing for a durable boundary note
    3. the implementation plan overcommitted stop-order internals and did not
       initially name the `backtest/execution_model.py` touchpoint
  - Follow-up review then found one remaining ambiguity:
    - trigger-aware behavior was still half-in and half-out of the first code
      slice
  - That ambiguity was closed by:
    - deferring trigger-aware stop behavior explicitly in the draft spec
    - pinning the first implementation slice to market/limit runtime-order
      refactoring only
    - pinning the matcher shape to `FillEvent | None` for the first slice
  - Final re-review passes returned `approved: no material findings` on both
    the content split and the narrowed implementation plan.
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed` on `2026-04-19`
- Final disposition:
  - `complete`
