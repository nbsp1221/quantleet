# Parameter Exploration Product Spec Plan

- Date: 2026-05-02
- Task: Define the first-beta product spec for constrained parameter exploration
- Status: `complete`
- Risk class: `Tier B`
- Requestor: retn0
- Owner: Codex

## Planner Contract

- Goal: Create a durable product spec for first-beta parameter exploration that
  defines what Quantcraft should provide, why it matters, and where the beta
  boundary is, without prematurely fixing implementation details.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/quantcraft-architecture.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: They define repo workflow, current shipped research
  and backtest contracts, package ownership, Tier A boundaries, and the product
  routing model for future work.
- In-repo scope:
  - Add `docs/product-specs/parameter-exploration.md`.
  - Register the new spec in `docs/product-specs/index.md`.
  - Link the planned slice from `docs/product-specs/research-ergonomics.md`.
  - Record evaluator acceptance and verification evidence in this plan.
- Out-of-repo scope:
  - External documentation and `/tmp` cloned library research are advisory
    inputs only.
  - No dependency, source, package, runtime, or test implementation changes.
- Tier A progression requested: `no`
- Approval record, if required: Not required. The slice defines planned
  research UX and does not modify `trading` or `execution` code.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - Product spec covers background, goals, non-goals, user intent, core
    requirements, functional requirements, nonfunctional requirements, major
    scenarios, edge/failure cases, external contracts, success conditions, and
    open questions.
  - The spec clearly scopes the beta feature as constrained parameter
    exploration rather than broad optimizer, walk-forward, portfolio, paper, or
    live trading work.
  - UI/UX and architecture requirements are stated independently from current
    implementation convenience.
  - Existing product routing points future parameter-exploration work to the
    new spec.
  - Repo/document verification passes or any failures are recorded.
- Out of scope:
  - Implementing parameter exploration.
  - Writing executable test scenarios for the implementation.
  - Choosing a final public API name.
  - Adding optimizers, heatmaps, walk-forward, parallel execution, or live
    integration.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - The new product spec is complete enough to be a source of truth for later
    test specs and technical implementation plans.
  - It does not claim unimplemented behavior as implemented.
  - It respects current architecture ownership: research owns experiment UX,
    backtest owns historical runtime outputs, and trading semantics are reused
    rather than redefined.
  - It separates closed requirements from open product questions.
  - It records external research as rationale without making competitor APIs the
    Quantcraft contract.
- Acceptance artifact location:
  - `docs/product-specs/parameter-exploration.md`
  - this plan's `## Evaluator Review`
- How the generator and evaluator agreed on done before execution: The planner
  contract above defines the required document sections, routing updates, and
  verification commands before edits begin.
- Checks the evaluator will use:
  - Read the new spec against the user-requested section list.
  - Compare scope against `research-ergonomics.md`, `backtest-mvp.md`, and
    architecture docs.
  - Confirm product routing includes the new spec.
  - Run the verification commands.
- Auto-fail conditions:
  - The spec makes live/paper trading or Tier A execution changes part of beta.
  - The spec chooses a broad optimizer implementation as mandatory for beta.
  - The routing index omits the new product spec.
  - Verification fails without a documented reason.

## Generator Work Log

- Planned slice order:
  1. Review repo docs and current strategy/backtest/reporting surfaces.
  2. Review external comparator patterns from web docs and `/tmp` cloned
     financial libraries.
  3. Draft `docs/product-specs/parameter-exploration.md`.
  4. Update product routing and research ergonomics links.
  5. Run verification and record evaluator findings.
- Notes:
  - External comparators inspected include `backtesting.py`, Backtrader,
    QuantStats, vectorbt, and PyBroker.
  - The product direction is constrained comparison and inspection for first
    beta, not automated optimization.
- Blockers or scope changes: None.

## Evaluator Review

- Findings:
  - No blocking findings.
  - The product spec keeps the beta scope to constrained finite parameter
    exploration and selected-run inspection.
  - The spec does not claim implementation status and does not require Tier A
    `trading` or `execution` changes.
  - Open product decisions are separated into the spec's `Open Questions`
    section rather than being silently resolved.
- Verification evidence:
  - `uv run poe repo-check`
    - `repository checks passed`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
    - `67 passed in 0.17s`
- Final disposition: Accepted as the first-beta parameter exploration product
  spec authoring slice.
