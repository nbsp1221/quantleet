# Active Plan

- Date: `2026-04-23`
- Task: `Rerun stop_market cross-validation with non-linked strategies only`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - revise the real-world validation strategy set so it tests the shipped
    `stop_market` primitive without relying on unshipped linked-order
    semantics such as OCO, OTO, or bracket activation
  - rerun the `/tmp` cross-validation experiment with the revised strategy set
    and report mismatch causes more cleanly
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-execution.md`
  - `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
  - `docs/plans/2026-04-23-stop-market-cross-validation-execution.md`
- Why these are governing:
  - They define the shipped stop-market scope, the absence of linked-order
    primitives, and the previously recorded cross-validation findings that this
    rerun is meant to cleanly isolate.
- In-repo scope:
  - update the real-world validation strategy candidate document
  - add this active rerun plan
- Out-of-repo scope:
  - modify the temporary `/tmp/quantcraft-stop-xval` harness
  - rerun the experiment there
  - update temporary result artifacts there
- Tier A progression requested: `yes`
- Approval record, if required:
  - Tier A and scope-expansion rerun approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread direction on `2026-04-23` to revise the three strategies,
      exclude linked-order semantics from the validation target, rerun the
      `/tmp` experiment, and report the new trust judgment
    - Granted scope:
      repository-local documentation updates plus `/tmp` harness edits and
      local comparator execution for the rerun
    - Expiration:
      end of this rerun slice
    - Audit reference:
      this active plan together with the prior stop-market cross-validation
      execution plan and stop-trigger governing documents
- Verification commands:
  - `uv run poe repo-check`
  - rerun command to be recorded after execution
- Success criteria:
  - candidate strategies no longer require linked-order semantics
  - rerun experiment exercises `stop_market` meaningfully across all engines
  - final report clearly separates stop primitive agreement from remaining
    library-specific fill-model differences
- Out of scope:
  - changing shipped `quantcraft` runtime code
  - implementing OCO/OTO/brackets

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - accept only if the revised strategy set is technically compatible with the
    shipped product scope and the rerun conclusions are supported by fresh
    comparator output
- Acceptance artifact location:
  - this active plan
  - revised doc under `docs/plans/`
  - temporary `/tmp/quantcraft-stop-xval/results/` artifacts
- How the generator and evaluator agreed on done before execution:
  - done means the bracket-linked confound has been removed from the validation
    target and the rerun reflects that narrower scope
- Checks the evaluator will use:
  - inspect revised strategy candidates against current shipped semantics
  - inspect rerun result artifacts
  - run `uv run poe repo-check`
- Auto-fail conditions:
  - leaving bracket-like linked-order semantics in the validation set
  - claiming stop-market agreement without rerunning the experiment

## Generator Work Log

- Planned slice order:
  1. revise the candidate strategy document
  2. rework the `/tmp` harness to the new non-linked strategy set
  3. rerun the cross-validation
  4. summarize mismatch causes
- Notes:
  - strategy quality for alpha is not the target; primitive-level validation is
    the target
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No unresolved repo findings.
  - Revised candidate strategies now avoid linked-order semantics and test only
    shipped primitives.
  - Fresh rerun findings:
    - `breakout_stop_entry`
      - exact agreement across `quantcraft`, `backtesting.py`, and
        `backtrader`
    - `pullback_limit_atr`
      - trade counts matched across all three engines
      - remaining divergence is a stop fill-price difference on a gap-through
        loss bar
    - `mean_reversion_market`
      - trade counts and equity still diverged materially
      - the remaining mismatch is no longer an OCO/OTO/bracket issue; it is a
        repeated stop fill-model difference under many fast stop exits
  - Overall judgment:
    - confidence is now high that the shipped `stop_market` primitive is
      fundamentally working
    - the main unresolved design question is whether `quantcraft` should keep
      its current trigger-point-oriented stop fill behavior or adopt a more
      conservative post-gap bar fill model
- Verification evidence:
  - Repo/document lane:
    - `uv run poe repo-check`
    - Result: `repository checks passed`
  - Rerun command:
    - `cd /tmp/quantcraft-stop-xval && uv run python run_cross_validation.py`
  - Temporary result artifacts:
    - `/tmp/quantcraft-stop-xval/results/cross_validation_results.json`
    - `/tmp/quantcraft-stop-xval/results/summary.md`
- Final disposition:
  - `accepted`
