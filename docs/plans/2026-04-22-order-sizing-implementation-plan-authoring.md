- Date: `2026-04-22`
- Task: `Author and harden the order-sizing implementation plan`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Write a concrete implementation-planning artifact for the first
    `qty_percent` order-sizing slice, then review and revise it using
    evidence-backed subagent fan-out.
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
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/design-docs/order-lifecycle-and-sizing-design.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing:
  - They define the active repo workflow, the current shipped backtest and
    research contract, the approved architecture boundaries, and the newly
    drafted future-only sizing spec that the implementation plan must realize
    without widening scope.
- In-repo scope:
  - Add one implementation-planning document under `docs/plans/`.
  - Update this active plan with evaluator findings and verification evidence.
  - Run read-only, evidence-backed subagent review fan-out on the drafted plan.
- Out-of-repo scope:
  - No Python implementation changes.
  - No non-primary-source product research beyond targeted evidence checks
    needed to resolve review findings.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only approval record:
    - Requestor: `thread user`
    - Human approver: `thread user`
    - Verification marker:
      explicit thread request to author the order-sizing implementation plan and
      review it with subagent orchestration
    - Granted scope:
      docs-only implementation planning for the next `trading` sizing slice,
      including read-only evidence-backed review and local verification
    - Expiration:
      end of this `2026-04-22` planning slice
    - Audit reference:
      this active plan and the resulting implementation-plan document
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The repository contains one coherent implementation plan for the first
    `qty_percent` sizing slice.
  - The plan is consistent with `docs/product-specs/order-sizing.md`.
  - The plan names concrete files, implementation stages, and verification
    steps without silently widening into portfolio-target or stop-order work.
  - Evidence-backed subagent review findings are synthesized and either
    incorporated or explicitly reported.
  - `uv run poe repo-check` passes after the doc changes.
- Out of scope:
  - Any Python behavior changes
  - Any approval to start implementation from the plan
  - Portfolio-target or rebalance work
  - Margin, leverage, or buying-power modeling

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close the slice only after the implementation plan is specific enough that
    a future code-writing slice can adopt it without having to rediscover the
    main architectural and semantic decisions from chat history.
- Acceptance artifact location:
  - `docs/plans/2026-04-22-order-sizing-implementation-plan.md`
- How the generator and evaluator agreed on done before execution:
  - Done means the implementation plan answers:
    1. which files should change first
    2. where raw percent sizing may live and where it may not
    3. how quantity-only runtime `Order` is preserved
    4. how tests and verification should freeze the new semantics
- Checks the evaluator will use:
  - Compare the plan against the governing spec and current repo truth.
  - Review evidence from subagent fan-out.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - The plan contradicts `docs/product-specs/order-sizing.md`.
  - The plan smuggles raw percentage fields into runtime `Order`.
  - The plan silently widens into target-percent, leverage, or stop-family
    scope.
  - Review finds a material unresolved contradiction and it is neither fixed
    nor reported.

## Generator Work Log

- Planned slice order:
  1. Re-read governing docs and current code/test touchpoints.
  2. Draft the implementation plan document.
  3. Run read-only subagent review fan-out with evidence requirements.
  4. Revise the plan if review findings are valid.
  5. Run `uv run poe repo-check`.
  6. Record evaluator findings and verification evidence here.
- Notes:
  - This is a docs-only planning slice.
  - Review fan-out should stay read-only and evidence-backed.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
- Added `docs/plans/2026-04-22-order-sizing-implementation-plan.md` as the
  concrete implementation-planning artifact for the first `qty_percent` slice.
- Evidence-backed subagent review fan-out did run after the host config issue
  was fixed and surfaced three real gaps in the draft:
  1. the pending request contract was incorrectly placed under `research`,
     which would have created `backtest -> research` coupling
  2. Task 1 did not explicitly lock runtime `Order` field-surface and
     `buy` / `sell` signature coverage tightly enough
  3. shipped-doc promotion did not yet cover the routing index and
     system-of-record structure tests fully
- Revised the plan to fix those findings:
  - moved the proposed cross-runtime request contract to
    `src/quantleet/trading/order_requests.py` instead of a
    `research`-local file
  - strengthened Task 1 so the plan explicitly freezes additive
    `buy` / `sell` signatures, implicit-symbol `qty_percent`, and quantity-only
    `Order` field-surface coverage
  - strengthened Task 7 so shipped-doc promotion includes
    `docs/product-specs/index.md`,
    `tests/structure/repo/test_index_status_maps.py`, and
    `tests/structure/docs/test_system_of_record_docs.py`
  - simplified the verification section so `verify-runtime` is the main final
    lane and duplicate umbrella commands are not required by default
- The final review pass reported no remaining architecture-boundary issue and
  no remaining test-contract issue apart from the routed-doc promotion gap,
  which was then addressed in the plan.
- Verification evidence:
- `uv run poe repo-check`
  -> `repository checks passed`
- Final disposition:
- `complete`
