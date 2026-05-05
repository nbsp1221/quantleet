# Active Plan

- Date: `2026-04-20`
- Task: `Design the Order lifecycle model and sizing intent contract`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  Produce a repository-local, evidence-backed design slice that answers two
  next hard-seam questions for `quantleet.trading`:
  - what lifecycle/FSM direction should runtime `Order` prefer next for
    `market`, `limit`, `stop-market`, and `stop-limit`
  - what sizing direction should be preferred if percentage-based sizing is
    later introduced beyond the current explicit-quantity MVP
  The output should be grounded in official docs, actual comparator library
  sources, and explicit contrarian evidence, then recorded in durable docs for
  future agent work.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/order-domain-runtime-design.md`
  - `docs/design-docs/order-runtime-model-design.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the repo workflow contract, Tier A safety expectations,
    current implemented scope, existing `OrderIntent` versus runtime `Order`
    boundary, current runtime `Order` responsibility guidance, and the
    documentation authority model this slice must preserve.
- Supporting references:
  - `docs/references/openai-harness-engineering.md`
  - `https://www.anthropic.com/engineering/harness-design-long-running-apps`
  - official docs and local comparator sources for NautilusTrader,
    QuantConnect LEAN, backtrader, freqtrade, and at least one sizing-oriented
    research framework such as Zipline, vectorbt, or backtesting.py
- Why these references matter:
  - The user explicitly requested a best-practices process that starts from a
    candidate answer, gathers supporting evidence, gathers rebuttal evidence,
    and only then records the synthesized answer for human approval/rejection.
- In-repo scope:
  - Create one active plan for this design slice.
  - Create one English research note under `docs/research/`.
  - Create one English draft design doc under `docs/design-docs/`.
  - Update routing indexes and local cross-links only if needed for
    discoverability.
  - Update existing Order-runtime docs only if they need a narrow pointer to
    the new lifecycle/sizing follow-on draft.
- Out-of-repo scope:
  - No Python implementation changes.
  - No product-spec changes.
  - No promotion of draft docs into governing authority.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to use web search, local comparator source
      analysis, contrarian evidence, and `$subagent-orchestration`, then
      document the synthesized answer before human review
    - Granted scope:
      docs-only design and research work for Tier A `trading`, including
      out-of-repo read access for official docs and existing local comparator
      source trees
    - Expiration:
      end of this `2026-04-20` lifecycle-and-sizing design slice
    - Audit reference:
      this active plan plus the resulting research/design docs and review
      findings
  - External-read approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread request to use web search and comparator libraries as
      design evidence
    - Granted scope:
      read-only external documentation lookup for architecture/process/library
      evidence
    - Expiration:
      end of this `2026-04-20` lifecycle-and-sizing design slice
    - Audit reference:
      this active plan plus cited sources in the resulting docs
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository has one research note that captures support and rebuttal
    evidence for lifecycle/FSM and sizing-intent design.
  - The repository has one draft design doc that clearly states the recommended
    runtime `Order` lifecycle direction and the recommended sizing direction,
    and that design remains narrower than a full OMS or full portfolio spec.
  - Reviewer fan-out includes at least one contrarian pass.
  - Final synthesis explicitly records where evidence converged and what was
    intentionally deferred.
  - `uv run poe repo-check` passes after doc updates.
- Out of scope:
  - Implementing stop orders
  - Implementing percentage sizing in code
  - Designing the full portfolio, ledger, or risk engine
  - Changing current public `Strategy` UX in code

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the new research and draft design docs are
    role-separated, evidence-backed, reviewed through bounded fan-out
    including a contrarian pass, and clearly answer what runtime `Order`
    lifecycle and sizing-intent contracts should be preferred next.
- Acceptance artifact location:
  - `docs/research/2026-04-20-order-lifecycle-and-sizing-comparison.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - index updates if added
- How the generator and evaluator agreed on done before execution:
  - This slice is done when a future agent can read the new design doc and
    understand:
    1. what lifecycle/FSM direction should be preferred for runtime `Order`
    2. what sizing direction should be preferred if percentage sizing is added
    3. why those answers beat the main alternatives
- Checks the evaluator will use:
  - Compare the doc claims against current repo truth and governing docs.
  - Check the research note for explicit support and rebuttal evidence.
  - Check that the draft design stays narrower than a full OMS or portfolio
    spec.
  - Check subagent outputs for evidence and unresolved objections.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Collapsing research and design into one document
  - Making unsupported claims about current implementation truth
  - Drifting into full OMS, full portfolio, or public-API redesign
  - Skipping contrarian evidence or synthesis after fan-out

## Generator Work Log

- Planned slice order:
  1. Establish the active plan and gather current repo truth for orders and
     sizing pressure.
  2. Run read-only research fan-out:
     - lifecycle/FSM comparator lens
     - sizing-intent comparator lens
     - contrarian/overdesign lens
  3. Synthesize the evidence and draft the English research and design docs.
  4. Run bounded review fan-out on the written docs.
  5. Revise until no material findings remain.
  6. Run `uv run poe repo-check` and close the plan.
- Notes:
  - Parent agent owns all writes.
  - Delegated work stays read-only and evidence-bearing.
  - This slice follows the repository-local harness approach: humans steer,
    agents execute, docs become the system of record.
  - The current worktree already contains uncommitted doc/routing changes from
    the prior English-promotion slice; this slice will avoid reverting them and
    will scope its own writes narrowly.
- Blockers or scope changes:
  - First review round found that the initial design draft overcommitted:
    1. it froze a lifecycle taxonomy more strongly than the evidence justified
    2. it implicitly chose a near-term sizing contract instead of a narrower
       direction
    3. it specified resolver behavior beyond the support chain in the research
       note
  - The slice was revised to:
    1. keep lifecycle guidance at the principle/direction level
    2. keep runtime `Order` quantity-based without freezing the next public
       sizing contract
    3. defer exact resolver rules, exact lifecycle representation, and exact
       public strategy syntax
  - A later review found only plan-close hygiene missing; the evaluator section
    and verification evidence were then recorded here.

## Evaluator Review

- Findings:
  - Read-only research fan-out converged on a bounded recommendation:
    1. do not jump to a full live-style OMS lifecycle taxonomy
    2. do make stop-trigger facts explicit in the future lifecycle shape
    3. keep runtime `Order` quantity-based
    4. if percentage sizing is later introduced, do it through a separate
       sizing layer rather than overloading `quantity`
  - First review fan-out found these material issues and they were fixed:
    1. the design draft froze too much lifecycle taxonomy too early
    2. the design draft chose a near-term sizing contract more strongly than
       current repo truth justified
    3. the draft specified detailed resolver behavior without enough evidence
  - The design doc was revised to stay at the direction/principle level and to
    defer exact taxonomy, exact sizing variant names, exact resolver policy,
    and public strategy syntax.
  - Final re-review results:
    - reviewer 1: `approved: no material findings`
    - reviewer 2: `approved: no material findings`
    - reviewer 3 originally found only missing plan-close hygiene; that gap was
      resolved by recording this evaluator artifact and fresh verification
      evidence
- Verification evidence:
  - `uv run poe repo-check`
    -> `repository checks passed`
  - `uv run pytest tests/structure/docs/test_system_of_record_docs.py tests/structure/repo/test_index_status_maps.py tests/structure/repo/test_poe_task_contracts.py tests/structure/repo/test_repo_check_contracts.py -q`
    -> `29 passed`
- Final disposition:
  - `complete`
