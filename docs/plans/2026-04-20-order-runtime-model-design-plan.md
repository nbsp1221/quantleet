# Active Plan

- Date: `2026-04-20`
- Task: `Design the runtime Order model and responsibility split`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Produce a repository-local, Korean-language Order-runtime design slice that
  clarifies:
  - what runtime `Order` should be as a domain object
  - which responsibilities belong to `Order` versus matching/runtime/event
    orchestration
  - how far event-driven decoupling should go before it becomes harmful
  - which minimal lifecycle/status model best fits `quantleet` now
  while grounding the recommendation in official docs, existing `/tmp`
  comparator source trees, and explicit contrarian evidence.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/design-docs/order-domain-runtime-design.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow contract, current implemented scope,
    Tier A safety expectations, package ownership, the existing
    `OrderIntent` versus runtime `Order` seam, and the documentation routing
    rules this slice must preserve.
- Supporting references:
  - `docs/references/openai-harness-engineering.md`
  - `https://www.anthropic.com/engineering/harness-design-long-running-apps`
  - official library docs for NautilusTrader, QuantConnect LEAN, and
    backtrader
  - local comparator sources under `/tmp/nautilus_trader`, `/tmp/lean`,
    `/tmp/backtrader`, and `/tmp/freqtrade`
- Why these references matter:
  - They are not repo authority, but they provide the cross-library evidence
    and process guidance the user explicitly requested for this design slice.
- In-repo scope:
  - Create one active plan for this design slice.
  - Create one Korean research artifact under `docs/research/`.
  - Create one Korean draft design doc under `docs/design-docs/`.
  - Update routing indexes only as needed for discoverability.
  - Run bounded read-only subagent research and review fan-out, then
    synthesize in the parent agent.
- Out-of-repo scope:
  - No Python implementation changes.
  - No product-spec changes.
  - No promotion of draft design docs into governing authority.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A design approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to use web search and `/tmp` library sources,
      use `$subagent-orchestration` aggressively, include rebuttal arguments,
      and write the resulting document in Korean
    - Granted scope:
      docs-only design and research work for the Tier A `trading` context,
      including out-of-repo read access for official docs and existing local
      comparator source trees
    - Expiration:
      end of this `2026-04-20` runtime-Order design slice
    - Audit reference:
      this active plan and the resulting research/design docs
  - External-read approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to use web search and read the Anthropic article
    - Granted scope:
      read-only external documentation lookup for process and comparator
      evidence
    - Expiration:
      end of this `2026-04-20` design slice
    - Audit reference:
      this active plan plus cited sources in the resulting documents
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository has a Korean research note capturing support and rebuttal
    evidence for runtime `Order` responsibility design.
  - The repository has a Korean draft design doc that clearly states the
    recommended runtime `Order` model, responsibility split, lifecycle
    boundary, and event-collaboration policy.
  - Reviewer fan-out includes at least one contrarian pass.
  - Final synthesis explicitly records where the reviewers converged and where
    open questions remain.
  - `uv run poe repo-check` passes after the doc updates.
- Out of scope:
  - Editing Python source files
  - Implementing stop orders, cancel/replace, or paper/live runtime behavior
  - Designing the full portfolio, ledger, or risk engine
  - Treating draft design guidance as governing truth

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the new research and draft design docs are
    role-separated, evidence-backed, reviewed through bounded fan-out
    including a contrarian pass, and aligned with the existing
    `OrderIntent`/runtime `Order` seam.
- Acceptance artifact location:
  - Original artifacts produced by this slice:
    - `docs/research/2026-04-20-order-runtime-model-comparison-ko.md`
    - `docs/design-docs/order-runtime-model-design-ko.md`
  - Later promoted English canonical replacements:
    - `docs/research/2026-04-20-order-runtime-model-comparison.md`
    - `docs/design-docs/order-runtime-model-design.md`
  - index updates if added
- How the generator and evaluator agreed on done before execution:
  - This slice is done when a future agent can read the new design doc and
    understand which responsibilities belong to `Order`, which belong outside
    it, and why that split is preferred over the main alternatives.
- Checks the evaluator will use:
  - Compare the doc claims against current repo truth and governing docs.
  - Check the research note for explicit support and rebuttal evidence.
  - Check that the draft design remains narrower than a full OMS spec.
  - Check subagent outputs for evidence and unresolved objections.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Collapsing research and design into one document
  - Making unsupported claims about current implementation truth
  - Drifting into full OMS or portfolio design
  - Skipping contrarian evidence or synthesis after fan-out

## Generator Work Log

- Planned slice order:
  1. Establish the active plan and source inventory.
  2. Run read-only research fan-out:
     - runtime-order lifecycle and object-model lens
     - event-collaboration and aggregate-boundary lens
     - contrarian/overdesign lens
  3. Synthesize the evidence and draft the Korean research and design docs.
  4. Run bounded review fan-out on the written docs.
  5. Revise until no material findings remain.
  6. Run `uv run poe repo-check` and close the plan.
- Notes:
  - Parent agent owns all writes.
  - Delegated work stays read-only and evidence-bearing.
  - This slice follows the repository-local harness approach: humans steer,
    agents execute, docs become the system of record.
- Blockers or scope changes:
  - First review round surfaced three material issues and all were fixed:
    1. research and design docs were too normative in parallel, weakening
       doc-role separation
    2. the older seam note still mixed historical and current runtime-Order
       claims in a confusing way
    3. the first Korean design draft was too conservative about reserved
       stop/paper-live semantics and too loose about inbound execution events
  - Additional maintainability review then found one remaining issue:
    the seam note still re-specified too much of the narrower runtime-Order
    responsibility model. The seam note was slimmed so it now only fixes the
    `OrderIntent` versus `Order` boundary and points to the follow-on runtime
    `Order` responsibility doc for ownership/lifecycle depth.

## Evaluator Review

- Findings:
  - Read-only research fan-out converged on a bounded recommendation:
    `quantleet` should use a small runtime `Order` aggregate with explicit
    runtime orchestration, while avoiding both a fake `OrderIntent` runtime
    object and a full OMS design.
  - First review fan-out found these material issues and they were fixed:
    1. research and design docs were too close to co-equal authority
    2. `order-domain-runtime-design.md` still used stale pre-implementation
       framing in parts of the seam note
    3. docs cited machine-local `/tmp/...` paths as durable references
    4. the design doc was too conservative about reserved stop/paper-live
       pressure and insufficiently clear that inbound execution events are
       first-class kernel inputs in future paper/live paths
  - Second review round found one remaining material maintainability issue:
    the English seam note still re-specified too much of the narrower runtime
    `Order` ownership model. That overlap was removed by slimming the seam note
    back down to boundary guidance and pointing readers to the follow-on draft
    for responsibility details.
  - Final re-review results:
    - reviewer 1: `approved: no material findings`
    - reviewer 2: `approved: no material findings`
    - reviewer 3: `approved: no material findings`
- Verification evidence:
  - `uv run poe repo-check`
    -> `repository checks passed` on `2026-04-20`
- Final disposition:
  - `complete`
