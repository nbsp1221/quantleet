# Beta Backtesting Product Positioning Plan

- Date: 2026-04-30
- Task: Align beta positioning and remove stale additive documentation around the current backtesting scope.
- Status: `completed`
- Risk class: `Tier B`
- Requestor: User
- Owner: Codex

## Planner Contract

- Goal: Reframe the current documentation so the first beta target is a user-facing single-symbol Python backtesting product comparable in experience to `backtesting.py`, while replacing stale current-scope statements instead of preserving them with caveats.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/design-docs/doc-gardening.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: The task changes product positioning and documentation routing, not code behavior. The product specs define current implemented behavior, the design docs define long-lived architecture and doc cleanup policy, and the repo contract defines the planner/generator/evaluator loop.
- In-repo scope:
  - Prefer modifying or consolidating existing docs over adding new long-lived docs.
  - Update existing user-facing or governing docs to distinguish current implemented scope, first beta target, and longer-term paper/live direction.
  - Replace stale "previous/future/partial" statements with current facts where the implementation has moved on.
  - Keep advisory competitive research advisory unless a conclusion is promoted into product specs.
  - Add this active plan as the required planner/evaluator artifact.
- Out-of-repo scope:
  - No package publishing.
  - No network-backed competitive refresh.
  - No code/API implementation.
  - No changes outside this repository.
- Tier A progression requested: `no`
- Approval record, if required: Not required. This slice changes documentation for Tier B research/backtest positioning and does not implement `trading` or `execution` behavior.
- Verification commands:
  - `uv run poe repo-check`
  - `uv run pytest tests/structure/docs tests/structure/repo -q`
- Success criteria:
  - The README gives a clear user-facing beta target and current limitation statement.
  - The product routing docs make the first beta target discoverable without creating a new duplicate roadmap surface.
  - `research-ergonomics.md` promotes the beta UX target from advisory research into a product contract.
  - Competitive research remains advisory, but points to the promoted product contract.
  - Quickstart wording supports the beta target without pretending unimplemented plotting, stats, or optimization already exist.
  - Verification commands pass.
- Out of scope:
  - Implementing plotting, optimization, result export, or paper/live runtime.
  - Renaming packages or moving source files.
  - Deleting historical plan artifacts.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Review the final diff against the planner contract.
  - Confirm the edited docs do not create a second source of truth for behavior already governed by product specs.
  - Confirm every new beta-target statement is framed as target/future work unless currently implemented.
  - Confirm the doc set still routes implementation work through product specs and design docs.
- Acceptance artifact location: This plan's `Evaluator Review` section.
- How the generator and evaluator agreed on done before execution: The planner contract defines exact docs goals, out-of-scope items, and verification commands before edits.
- Checks the evaluator will use:
  - Manual diff review.
  - `uv run poe repo-check`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q`.
- Auto-fail conditions:
  - Docs claim plotting, optimization, richer stats, paper trading, or live trading are implemented when they are not.
  - A new long-lived roadmap doc is added instead of integrating into existing routing/spec docs.
  - Tier A implementation work is introduced without approval.
  - Repo/document structure checks fail.

## Generator Work Log

- Planned slice order:
  1. Update README with current scope, first beta target, and longer-term direction.
  2. Update `docs/product-specs/index.md` so beta-target product work routes through existing specs.
  3. Update `docs/product-specs/research-ergonomics.md` with first-beta success criteria and UX gaps.
  4. Update advisory research docs only where needed to avoid duplicate authority or misleading claims.
  5. Run verification and review the diff.
  6. Replace stale additive documentation found during follow-up review:
     `backtest-mvp.md`, `data-ingestion.md`, `research-ergonomics.md`,
     `research-ergonomics-quickstart.md`, `order-reservation.md`,
     `order-lifecycle-and-sizing-design.md`, and the competitive research
     matrix.
- Notes:
  - The user explicitly prefers modification, deletion, consolidation, or renaming over adding docs. This plan is the only new file expected because the repo contract requires it.
  - Updated `README.md` with product-stage framing, current scope, and first-beta gaps.
  - Updated `docs/product-specs/index.md` by extending the existing `research-ergonomics.md` routing row instead of adding a duplicate row.
  - Updated `docs/product-specs/research-ergonomics.md` with concise first-beta comparator, UX gaps, and beta threshold language folded into existing sections.
  - Updated `docs/research/2026-03-23-python-quant-library-landscape.md` to reflect the current implemented baseline and route promoted beta direction back to the product spec.
  - Reverted the quickstart-note addition after review because `research-ergonomics.md` now carries the beta distinction without duplicating it.
  - Replaced stale current-scope wording for stop-family orders, the backtest
    baseline, and ingestion examples instead of preserving old statements with
    caveats.
  - Removed duplicate `source.load()` bullets and the supersession paragraph
    that forced readers to reconcile older deferral notes with current behavior.
- Blockers or scope changes:
  - Initial attempt to add a second product-index row for `research-ergonomics.md` failed the repo's duplicate-routing check. The final version keeps one row and folds beta routing into its `Read When` column.

## Evaluator Review

- Findings:
  - No blocking findings. The final routing keeps one product-spec row per document, beta-target language is framed as direction rather than implemented behavior, and stale current-scope statements were replaced instead of preserved with caveats.
  - Historical `docs/plans/` records still contain past stop-order scope notes; those are execution logs rather than current product authority and are intentionally outside this cleanup slice.
- Verification evidence:
  - `uv run poe repo-check` passed with output `repository checks passed`.
  - `uv run pytest tests/structure/docs tests/structure/repo -q` failed once because two docs removed the exact contract phrase `source.load()` returns `BarSeries` while removing duplicate bullets; after keeping the required phrase once in each doc, it passed with output `63 passed in 0.15s`.
  - `uv run poe verify` passed: `ruff check .`, `mypy src`, `pytest -q` with `476 passed, 3 skipped`, coverage policy at `92%`, `uv build`, `repo_check.py`, and four notebook validations.
- Final disposition:
  - Accepted for this documentation slice after final verification.
