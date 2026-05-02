# Parameter Exploration Product And Test Spec Review Plan

- Date: 2026-05-02
- Task: Review the parameter exploration product spec and test scenario spec
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Use read-only subagent review fan-out to check whether the product spec
  and test scenario spec are mutually consistent, sufficiently concrete, and
  ready to feed a technical implementation plan.
- Governing docs:
  - `AGENTS.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/parameter-exploration.md`
  - `docs/product-specs/parameter-exploration-test-scenarios.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/PLANS.md`
- Why these are governing: The review target is a planned first-beta research
  feature and its test contract. The product/test specs define the feature and
  validation target; the architecture, reliability, security, and plan docs
  define package ownership, risk tier, and workflow.
- In-repo scope:
  - Review and, if justified, edit
    `docs/product-specs/parameter-exploration.md`.
  - Review and, if justified, edit
    `docs/product-specs/parameter-exploration-test-scenarios.md`.
  - Update this plan with reviewer coverage, accepted/rejected findings, and
    verification evidence.
- Out-of-repo scope:
  - None planned. This is an internal spec consistency review.
- Tier A progression requested: `no`
- Approval record, if required: Not required; this is documentation review for
  a Tier B research/backtest planning artifact.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - At least three distinct read-only subagent reviews are completed or any
    timeout/failure is reported.
  - Parent synthesis critically evaluates subagent findings rather than
    accepting them blindly.
  - Clear, scope-preserving improvements are applied directly.
  - Human-judgment questions are separated from direct edits.
  - Fresh verification evidence is recorded.
- Out of scope:
  - Technical implementation planning.
  - Runtime code or test implementation.
  - Changing already closed product scope without human confirmation.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm reviewer findings were deduplicated and checked against the product
    and test specs.
  - Confirm direct edits do not add deferred product scope.
  - Confirm unresolved questions are genuinely human-judgment items.
  - Run the planned verification commands.
- Acceptance artifact location:
  - `docs/plans/2026-05-02-parameter-exploration-product-test-spec-review.md`
- How the generator and evaluator agreed on done before execution:
  - The planner contract above is the definition of done.
- Checks the evaluator will use:
  - Manual review of final product/test spec diff.
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Auto-fail conditions:
  - A subagent-suggested scope change is applied without human confirmation.
  - The specs become inconsistent about API ownership, objective behavior,
    failure handling, storage, or beta exclusions.
  - Verification fails.

## Generator Work Log

- Planned slice order:
  1. Re-read the product and test specs.
  2. Dispatch read-only subagents with distinct review lenses.
  3. Synthesize and classify findings.
  4. Apply only scope-preserving documentation improvements.
  5. Verify and report.
- Notes:
  - Subagent review will use product/requirements, test quality, edge/failure,
    and implementation-risk perspectives.
- Blockers or scope changes:
  - None.

## Subagent Review Coverage

- Hilbert: product and requirements alignment reviewer.
  - Accepted: canonical example must show comparison output before selected-run
    inspection; strategy identity and execution assumptions needed a minimum
    record contract; candidate-count visibility needed to avoid implying a
    progress API; record key spelling needed to be closed.
- Sagan: test quality reviewer.
  - Accepted: meaningful infinity behavior belongs in P0; materialized-bars
    tests should verify public call shape rather than a fake source interaction;
    record collision tests were missing.
  - Partially accepted: exact enumeration order was under-specified, so the
    product spec now defines deterministic public ordering and zero-based
    `run_index`.
- Curie: edge cases and failure scenarios reviewer.
  - Accepted: parameter-name policy, explicit status enum, count invariants,
    invalid objective preflight failure, `top(n)` over-ask behavior,
    metric-extraction failed-row behavior, and negative-infinity alignment.
- Dirac: implementation risk reviewer.
  - Accepted: record schema, objective metric path set, engine run-state
    isolation, callback parameter mutation protection, and selected-run plot
    test scope needed clarification.
  - Partially accepted: `max_candidates=None` memory risk was documented as an
    explicit user responsibility; the existing beta decision to allow it was
    not changed.

## Parent Synthesis

- Directly applied scope-preserving fixes:
  - Updated the canonical product example to print `results.to_records()`
    before selecting `best()`.
  - Clarified candidate-count visibility as preflight diagnostics plus
    `GridSearchResult` aggregate counts, not a progress/logging/dry-run API.
  - Defined deterministic enumeration as parameter insertion order, candidate
    value order, and zero-based `run_index`.
  - Added non-empty string parameter-name rules, allowed reserved-looking and
    dotted names under nested `parameters`, and rejected non-string names.
  - Clarified large explicit `max_candidates` overrides retain in-memory risk.
  - Required callback parameter mappings not to corrupt stored row identity.
  - Required reused `BacktestEngine` objects not to leak run-scoped state.
  - Closed the beta comparison metric path set and required invalid objective
    paths to fail before backtests.
  - Defined `top(n)` over-ask behavior as returning all eligible rows.
  - Added top-level record `status` values, dotted metric record keys,
    `_state` companion keys, `eligible_count`, and count invariants.
  - Clarified `metric_extraction` rows are failed comparison rows and are not
    required to expose underlying `BacktestResult` through selected-run helpers.
  - Adjusted the test spec for parameter-name/collision cases, mutation
    attempts, infinity as P0, materialized-bars public call shape, plot-path
    test scope, and closed record-key/negative-infinity open questions.
- Rejected or limited findings:
  - Did not add a public progress callback, logging API, dry-run API, storage
    policy, or memory envelope; those would change closed beta scope.
  - Did not require failed rows to expose real reports or plots; selected-run
    inspection remains a successful-row contract.
  - Did not re-open the existing decision that `max_candidates=None` is allowed
    as an explicit override.

## Evaluator Review

- Findings:
  - No blocking findings remain in the docs after scope-preserving edits. The
    remaining open questions are implementation-planning choices that do not
    block product/test spec alignment.
- Verification evidence:
  - `uv run poe repo-check` passed with `repository checks passed`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q` passed with
    `67 passed`.
- Final disposition:
  - Complete.
