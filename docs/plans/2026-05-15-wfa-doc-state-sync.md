# WFA Public And Internal Docs State Sync

- Date: 2026-05-15
- Task: Align WFA public docs and internal product-doc state
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Fix the two WFA beta-readiness documentation gaps: public docs must
  match the implemented `quantleet.research.WalkForwardStudy` surface, and
  internal WFA product/roadmap routing must no longer imply Stage 4 is still
  paused or only draft.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/public-beta-documentation.md`
  - `docs/product-specs/walk-forward-analysis.md`
  - `docs/product-specs/walk-forward-analysis-resume.md`
  - `docs/product-specs/walk-forward-analysis-resume-test-scenarios.md`
  - `docs/product-specs/walk-forward-analysis-readiness.md`
  - `docs/product-specs/wfa-prerequisite-roadmap.md`
  - `docs/PLANS.md`
- Why these are governing: the repo contract requires an active plan for
  non-trivial changes; public beta docs define the public user docs boundary;
  WFA product/test specs and prerequisite docs define the intended Stage 4
  contract and the historical pause rationale.
- In-repo scope:
  - update README and `docs/site` so public docs mention WFA consistently with
    the implemented public import surface
  - add a small public WFA guide only if needed to avoid overloading canonical
    examples
  - keep the public canonical example count at exactly three
  - update WFA product-spec routing/status language from paused/draft to
    implemented/superseded where Stage 4 has already landed
  - update structure tests that currently encode the stale paused state
- Out-of-repo scope: none.
- Tier A progression requested: `no`
- Approval record, if required: not required; documentation/test contract only.
- Verification commands:
  - `uv run pytest tests/structure/docs tests/smoke/local/test_public_imports.py -q`
  - `uv run poe repo-check`
  - `git diff --check`
- Success criteria:
  - public docs mention `WalkForwardStudy` and related WFA public result types
  - public docs describe WFA as research validation evidence, not optimizer
    guarantees, financial advice, live/paper trading, or continuous account
    reporting
  - public examples remain exactly three canonical examples
  - product-spec routing points current WFA work to the implemented Stage 4
    resume spec/test spec
  - historical WFA pause/readiness/roadmap docs are clearly historical or
    superseded rather than current blockers
  - targeted verification passes
- Out of scope:
  - adding or changing runtime WFA behavior
  - adding LICENSE or other non-WFA release files
  - commit, push, tag, package publish, or GitHub Pages deployment

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: inspect changed WFA public and
  internal docs, confirm no non-WFA release files were added, run targeted
  verification, and confirm no commit was made.
- Acceptance artifact location:
  `docs/plans/2026-05-15-wfa-doc-state-sync.md`
- How the generator and evaluator agreed on done before execution: this plan
  fixes the exact two doc-state problems, verification commands, and explicit
  non-scope before edits.
- Checks the evaluator will use:
  - inspect README and `docs/site` WFA references
  - inspect product-spec routing/status language
  - scan for stale current-state paused wording
  - run targeted tests and repo-check
- Auto-fail conditions:
  - public docs imply WFA is a trading recommendation, optimizer guarantee,
    live/paper feature, or continuous OOS account report
  - public canonical examples become more than three
  - runtime code changes are introduced
  - LICENSE or unrelated release files are added in this slice
  - git commit is created

## Generator Work Log

- Planned slice order:
  1. Update public WFA docs and tests.
  2. Update internal WFA product-spec/roadmap status and routing.
  3. Run targeted verification and audit the actual diff.
- Notes:
  - Current code already exports WFA public types from `quantleet.research`.
  - Current smoke tests already assert WFA public imports exist.
  - Current public docs still list only `ParameterStudy`.
  - Current structure tests still assert stale paused WFA wording.
  - README, `docs/site`, and public API docs now mention WFA consistently with
    the implemented public import surface.
  - Added `docs/site/guides/walk-forward-analysis.md` as a bounded public guide
    without increasing the three canonical example count.
  - WFA baseline/readiness/roadmap docs are marked historical or superseded,
    and the resume spec/test spec are marked implemented.
  - Structure tests now enforce the current implemented WFA documentation
    contract rather than the old paused-state wording.
- Blockers or scope changes: none.

## Evaluator Review

- Findings:
  - No blocker findings. The two requested WFA documentation gaps are closed.
  - No runtime source files changed.
  - No `LICENSE` or unrelated release file was added in this slice.
  - No commit was created; `HEAD` remains `9636507`.
- Verification evidence:
  - `uv run pytest tests/structure/docs tests/smoke/local/test_public_imports.py -q`
    passed: `45 passed in 0.34s`.
  - `uv run poe repo-check` passed: `repository checks passed`.
  - `git diff --check` passed with no whitespace errors.
  - Stale current-state wording scan returned no matches:
    `rg -n 'WFA implementation is paused|WFA remains paused|currently paused|Implementation of WFA is paused|Walk-forward analysis remains paused|paused future research-validation|before WFA resumes|implementation resumes|must not be treated as authorization to implement WFA' docs/product-specs tests/structure/docs tests/structure/repo README.md docs/site || true`.
- Final disposition: complete for WFA public/internal documentation state sync.
