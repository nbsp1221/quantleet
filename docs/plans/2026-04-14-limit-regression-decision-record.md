# Active Plan

- Date: 2026-04-14
- Task: record the approved real-data limit regression strategy set
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Persist the agreed decision for real-data limit-order regression coverage so it survives session loss and can guide later implementation.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/RELIABILITY.md`
- Why these are governing:
  - they define the repo workflow, current backtest scope, current research surface, and the reliability expectations for canonical regression tests
- In-repo scope:
  - add a plan artifact for this recording task
  - add a design/decision document under `docs/plans/`
  - capture the approved strategy count, rationale, and selected strategy shapes
- Out-of-repo scope:
  - no code changes
  - no test implementation yet
  - no network-dependent execution
- Tier A progression requested: `no`
- Approval record, if required: not required for this Tier C documentation slice
- Verification commands:
  - `git diff -- docs/plans/2026-04-14-limit-regression-decision-record.md docs/plans/2026-04-14-limit-strategy-regression-design.md`
  - `sed -n '1,260p' docs/plans/2026-04-14-limit-strategy-regression-design.md`
- Success criteria:
  - the document states why real-data limit regression coverage is needed
  - the document records the approved count as three strategies
  - the document names the three selected strategy families and why each exists
  - the document explains why more than three is not currently justified
- Out of scope:
  - implementing the strategies
  - adding tests
  - running backtests

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: The repo contains a clear decision record that a later session can read without needing chat history to understand the selected limit regression strategy set and its rationale.
- Acceptance artifact location: `docs/plans/2026-04-14-limit-strategy-regression-design.md`
- How the generator and evaluator agreed on done before execution: The document must reflect the conversation faithfully and distinguish approved decisions from future implementation details.
- Checks the evaluator will use:
  - verify the approved count is three
  - verify the three strategy families match the discussion
  - verify the rationale is explicit and tied to engine trust rather than arbitrary strategy breadth
- Auto-fail conditions:
  - the document omits the approved count
  - the document mixes selected strategies with rejected alternatives without labeling them
  - the document reads like an implementation plan instead of a decision record

## Generator Work Log

- Planned slice order:
  1. create the active recording plan
  2. write the design/decision document
  3. review for alignment and completeness
- Notes:
  - this is a persistence artifact for session continuity
- Blockers or scope changes:
  - none

## Evaluator Review

- Findings:
  - The decision record preserves the key approved outcome from the session: the repository should add three real-data limit-order regression strategy families, not one or many.
  - The design distinguishes the two primary trust-building strategies from the third supporting mixed-path strategy.
  - The document also records why support/resistance and grid were deferred, which helps future sessions avoid repeating the same selection debate.
- Verification evidence:
  - `sed -n '1,260p' docs/plans/2026-04-14-limit-strategy-regression-design.md`
  - `git diff -- docs/plans/2026-04-14-limit-regression-decision-record.md docs/plans/2026-04-14-limit-strategy-regression-design.md`
- Final disposition:
  - complete
