# Active Plan

- Date: `2026-04-15`
- Task: `Analyze current backtest runtime against the promoted semantics contract and write the implementation plan`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - analyze how the current backtest runtime diverges from the promoted conservative execution semantics
  - capture the required implementation slices, file ownership, and verification strategy in a durable implementation plan
- Governing docs:
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Why these are governing:
  - the architecture and design docs define the matching boundary and canonical path rules
  - the product spec defines the intended user-visible backtest semantics
  - reliability and security docs govern Tier A planning and verification expectations
- In-repo scope:
  - inspect current backtest runtime and tests
  - write a detailed implementation plan under `docs/plans/`
  - record the mismatch analysis and evaluator findings in this active plan
- Out-of-repo scope:
  - code changes
  - web research
  - rerunning cross-engine experiments
  - live or paper trading work
- Tier A progression requested: `yes`
- Approval record, if required:
  - requestor: `user`
  - human approver: `Naki`
  - countersignature or equivalent verification marker: `user approval in chat after git-config identity check`
  - scope granted: `Tier A planning and canonical doc promotion follow-up for backtest execution semantics`
  - expiration: `2026-04-16T23:59:59+09:00`
  - audit reference or sanitized audit link: `chat approval lineage plus 2026-04-15-backtest-semantics-doc-promotion-plan.md`
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - the active plan clearly names the current semantic mismatches in source and tests
  - a durable implementation plan exists with exact files, phased tasks, and verification commands
  - the plan explains how correctness and performance work will be staged without violating the new contract
- Out of scope:
  - implementing the semantics change
  - changing tests or runtime behavior

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - done means a future engineer can implement the backtest semantics change from the plan alone, without needing this chat for the source of truth
- Acceptance artifact location:
  - `docs/plans/2026-04-15-backtest-semantics-implementation-planning.md`
- How the generator and evaluator agreed on done before execution:
  - this plan freezes the analysis-and-planning-only scope before any new planning artifact is written
- Checks the evaluator will use:
  - source-to-doc mismatch review
  - implementation-plan completeness review
  - `uv run poe repo-check`
- Auto-fail conditions:
  - the plan omits the current optimistic-fill divergence
  - the plan does not distinguish correctness work from performance optimization work
  - the plan does not name exact file paths for the intended implementation slices
  - verification is not run from the current repo state

## Generator Work Log

- Planned slice order:
  - inspect the runtime and current execution semantics tests
  - map each source-level divergence to the promoted contract
  - write the implementation plan document
  - run repo-local verification and record findings
- Notes:
  - this slice produces planning artifacts only
- Blockers or scope changes:
  - none
- Source-level mismatch notes:
  - `src/quantcraft/research/adapters/execution_model.py` currently emits four isolated synthetic prices per bar and sets `bid == ask == last == price`, which grants optimistic executable prices from bar extremes
  - `events_from_bars(...)` eagerly materializes the full event tuple for all bars, which blocks the promoted lazy traversal and acceleration contract
  - `src/quantcraft/research/application/backtest.py` is structured around whole-run event precomputation instead of per-bar execution-event generation
  - `src/quantcraft/trading/domain/matching.py` remains suitable as a generic matcher for real tick/book events and should not absorb backtest-only bar logic
  - `tests/integration/research/test_backtest_execution_semantics.py` currently codifies optimistic synthetic-fill expectations that must be replaced during implementation
  - `tests/unit/trading/test_matching_and_state.py` is still valid for real book matching, but it is not the right place to encode backtest-path semantics

## Evaluator Review

- Findings:
  - the main implementation work belongs in `research` backtest adapters and backtest orchestration, not in `trading`
  - the largest current divergence is not generic matching logic but optimistic synthetic event construction in `execution_model.py`
  - correctness and performance must be staged separately: first conservative outcome parity, then path traversal acceleration
  - the implementation plan now names exact files, failing-test slices, and verification commands for the full conformance path
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
- Final disposition:
  - `accepted`
