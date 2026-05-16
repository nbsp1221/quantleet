# Test Quality Evaluation Plan Document

- Date: 2026-05-16
- Task: Add an English test quality evaluation plan that can produce concrete
  quantitative and qualitative reports.
- Status: `complete`
- Risk class: `Tier C`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Document how `quantleet` should evaluate test-code quality before
  raising future feature gates.
- Governing docs:
  - `AGENTS.md`
  - `docs/PLANS.md`
  - `docs/RELIABILITY.md`
  - `docs/references/testing.md`
- Why these are governing:
  - `AGENTS.md` requires active plans for non-trivial repository changes.
  - `docs/PLANS.md` defines where current plan artifacts live.
  - `docs/RELIABILITY.md` defines mechanical checks, LLM-assisted critique,
    and human judgment as separate reliability modes.
  - `docs/references/testing.md` defines the existing test taxonomy and
    placement rules.
- In-repo scope:
  - Add a reusable English reference under `docs/references/`.
  - Update the references index.
  - Record evaluator evidence in this plan.
- Out-of-repo scope:
  - No external repo changes.
  - No new test tooling or CI gate implementation in this slice.
- Tier A progression requested: `no`
- Approval record, if required: not required.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - The new reference explains quantitative and qualitative test quality
    evaluation.
  - The reference includes concrete metrics that can be filled into a future
    report.
  - The reference includes an LLM review rubric suitable for qualitative
    assessment.
  - The references index links to the new document.
- Out of scope:
  - Running the full current test-quality audit.
  - Adding mutation testing, flaky-test tooling, or new CI jobs.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice:
  - Confirm the document is a plan for future evaluation, not a completed
    audit.
  - Confirm the report template has explicit numeric fields.
  - Confirm the document keeps mechanical checks, LLM critique, and human
    judgment separate.
- Acceptance artifact location:
  - `docs/references/test-quality-evaluation-plan.md`
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - Done means the documentation is sufficient for a later agent or human to
    run the evaluation and produce a report with numbers, findings, and
    recommended gates.
- Checks the evaluator will use:
  - Manual document review against governing docs.
  - `uv run poe repo-check`
- Auto-fail conditions:
  - The document claims coverage alone proves test quality.
  - The document turns LLM review into a single unquestioned score.
  - The document adds unapproved CI or tooling changes.

## Generator Work Log

- Planned slice order:
  - Add the test quality evaluation plan reference.
  - Link it from `docs/references/index.md`.
  - Run repository document checks.
- Notes:
  - The source research used public testing references on coverage, mutation
    testing, flaky tests, pytest flaky-test guidance, and LLM rubric-based
    evaluation.
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No blocker findings.
  - The reference is explicitly framed as an evaluation plan, not a completed
    audit or CI implementation.
  - The report template includes concrete numeric fields for test count,
    coverage, runtime, flakiness, mutation testing, and LLM finding counts.
  - The document keeps mechanical checks, LLM-assisted critique, and human
    judgment separate, matching `docs/RELIABILITY.md`.
  - The document does not claim coverage alone proves test quality and does not
    add tooling or CI gates in this slice.
- Verification evidence:
  - `uv run poe repo-check` passed with `repository checks passed`.
- Final disposition:
  - Complete.
