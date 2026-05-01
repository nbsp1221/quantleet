# Active Plan

- Date: 2026-05-02
- Task: Review the first-beta backtest plotting product spec and test scenario spec before implementation planning
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal: Use read-only subagent review plus best-practice checks to validate
  `docs/product-specs/backtest-plotting.md` and
  `docs/product-specs/backtest-plotting-test-scenarios.md` before writing the
  concrete implementation plan.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-plotting.md`
  - `docs/product-specs/backtest-plotting-test-scenarios.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
- Why these are governing: The review concerns a first-beta public backtest UX
  contract, its test contract, package ownership, workflow rules, and local
  verification policy.
- In-repo scope:
  - Review and, when objectively correct, revise the two plotting spec
    documents.
  - Update this plan with evaluator findings, review coverage, and verification
    evidence.
- Out-of-repo scope:
  - Web research is limited to public best-practice and comparator references
    needed to validate the spec and test approach.
  - No external connectors, secrets, live trading systems, or non-repository
    files are in scope.
- Tier A progression requested: `no`
- Approval record, if required: Not required. The work is documentation and
  planning for Tier B `backtest` and `research` scope.
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - At least three independent read-only subagent reviewers examine the spec
    and test scenario documents from distinct perspectives.
  - Findings include evidence, severity, and suggested fixes or explicit human
    questions.
  - Clear best-practice or consistency fixes are applied without changing
    product direction.
  - Product-direction choices that require human intent are separated into
    explicit questions.
  - Repository documentation checks pass after accepted edits.
- Out of scope:
  - Production code changes.
  - Test implementation.
  - Concrete implementation plan authoring.
  - Changing the already selected primary API or dependency strategy unless the
    review surfaces a human decision that explicitly reopens it.

## Evaluator Acceptance Contract

- Evaluator owner: Codex
- Evaluator-owned done contract for this slice: Review outputs are synthesized,
  meaningful issues are either fixed in the documents or routed to human
  questions, and the repo-check verification result is recorded here.
- Acceptance artifact location:
  - `docs/plans/2026-05-02-backtest-plotting-spec-and-test-scenarios-review-plan.md`
- How the generator and evaluator agreed on done before execution: The planner
  contract above defines the review fan-out, fix policy, human-question policy,
  and verification command before any document edits in this slice.
- Checks the evaluator will use:
  - Compare subagent findings against the product spec, test scenario spec, and
    governing architecture/reliability docs.
  - Apply only low-ambiguity documentation corrections.
  - Run `uv run poe repo-check`.
- Auto-fail conditions:
  - Fewer than three independent reviewer perspectives complete.
  - A material contradiction remains between the product spec and test scenario
    spec without being fixed or raised as a human question.
  - Repo-check fails after edits.

## Generator Work Log

- Planned slice order:
  1. Create this active plan. Completed.
  2. Dispatch read-only subagent reviewers. Completed with five reviewer
     lenses: Product/API UX, Architecture/Data Ownership, Test Strategy,
     Implementation Feasibility, and External Best-Practice/Comparator.
  3. Synthesize findings and classify them as apply, reject, or human question.
     Completed.
  4. Apply clear documentation fixes. Completed.
  5. Run verification. Completed.
  6. Record evaluator findings and final disposition. Completed.
- Notes:
  - Reviewers must not edit files.
  - Codex is the single writer for any accepted documentation updates.
  - Applied fixes:
    - narrowed first-beta required run snapshot content to timestamps, closes,
      and metadata while allowing internal immutable OHLCV storage if useful
    - changed plot drawdown rendering to an underwater series while preserving
      positive stored `drawdown_curve` values
    - specified empty plot data and one-bar plot behavior
    - added public no-argument API shape tests for `result.plot()`
    - added figure-data assertions for close, equity, drawdown, and fill marker
      x/y values
    - added default layout assertions for size, shared x-axis, approximate panel
      ratio, and grid enablement
    - added no-`close()` side-effect and Matplotlib figure cleanup test hygiene
    - moved primary plotting integration placement to `tests/integration/backtest/`
    - strengthened import-boundary tests so `backtest` plotting does not depend
      on `research`, `execution`, app surfaces, or deep sibling internals
    - rewrote snapshot-related tests toward observable plotted data rather than
      private snapshot object identity
    - corrected built-artifact dependency testing to use wheel metadata or a
      clean dependency-installed environment
    - recorded that `tests/perf/` placement requires Poe task surface updates
      so the 10,000-bar scale scenario actually runs under `verify-runtime`
    - labeled Backtrader as a historical/popular comparator rather than a
      current-practice anchor
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - Product/API UX reviewer found snapshot overreach, drawdown visual ambiguity,
    and missing empty/single-bar behavior. The snapshot and degenerate-data
    issues were fixed. The drawdown ambiguity was resolved in favor of the
    standard underwater visual convention while preserving positive result
    values for analytics.
  - Architecture/Data Ownership reviewer found missing `backtest -> research`
    import-boundary protection, private snapshot coupling in tests, and
    research-owned integration placement. The test scenario spec now protects
    the dependency direction, uses observable plot data for snapshot
    independence, and places primary integration tests under `backtest`.
  - Test Strategy reviewer found missing public API shape tests, insufficient
    data assertions, incomplete default-layout coverage, missing no-`close()`
    assertions, and underspecified mutable-input fixtures. These were added or
    clarified.
  - Implementation Feasibility reviewer found that the built-artifact test could
    falsely pass from the dev environment, that `tests/perf/` is not
    automatically in `verify-runtime`, and that drawdown calculation should be
    consolidated. The test spec now requires wheel metadata or a clean
    dependency-installed environment, explicit Poe task inclusion, and the
    product spec now calls for shared drawdown-helper consolidation.
  - External Best-Practice reviewer found missing Matplotlib test cleanup and
    stale/mutable comparator risks. The test spec now requires figure cleanup,
    and the product spec labels Backtrader as historical/popular evidence.
- Verification evidence:
  - `uv run poe repo-check` passed on 2026-05-02 with
    `repository checks passed`.
- Final disposition:
  - Accepted. The reviewed specs are ready to use as inputs for the concrete
    implementation plan. No remaining human-blocking question was identified in
    this review pass.
