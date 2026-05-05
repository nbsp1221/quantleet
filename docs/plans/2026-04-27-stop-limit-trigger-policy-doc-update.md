# Active Plan

- Date: `2026-04-27`
- Task: `Update stop-limit trigger policy docs after human decisions`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `Naki (thread user)`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Update the stop-limit product spec and test scenario planning artifact with
    the human-approved stop-family trigger policy.
  - Re-review the updated documents with read-only subagents and fresh external
    source checks where industry practice is relevant.
- Governing docs:
  - `AGENTS.md`
  - `docs/PLANS.md`
  - `docs/product-specs/stop-limit.md`
  - `docs/plans/2026-04-27-stop-limit-test-scenarios.md`
  - `docs/plans/2026-04-27-stop-limit-preimplementation-doc-review.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/design-docs/golden-principles.md`
- Why these are governing:
  - They define repo workflow, planned stop-limit product behavior, current
    test-design input, prior unresolved review findings, execution semantics,
    and durable documentation policy.
- In-repo scope:
  - Update `docs/product-specs/stop-limit.md`.
  - Update `docs/plans/2026-04-27-stop-limit-test-scenarios.md`.
  - Record review synthesis and verification evidence in this active plan.
- Out-of-repo scope:
  - Read-only web checks for stop-trigger behavior and price-time/FIFO matching
    practice.
- Tier A progression requested: `no`
- Approval record, if required:
  - Tier A docs-only trigger-policy update approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread decisions approving generic stop-family trigger
      primitive semantics, equality rejection against the last evaluated
      `last` reference price, and existing-before-newly-triggered same-event
      priority.
    - Granted scope:
      docs-only update of stop-limit product/test planning documents plus
      task-limited read-only external research and subagent review.
    - Expiration:
      end of this `2026-04-27` docs update slice.
    - Audit reference:
      this active plan.
- Verification commands:
  - `uv run poe repo-check`
  - `git diff --check`
- Success criteria:
  - Product spec states that stop-family orders are generic price-triggered
    primitives.
  - Product spec states that trigger direction is inferred from `stop_price`
    relative to the last evaluated `last` reference price at order intake.
  - Bar backtest `close` is described as the current bar-based implementation's
    reference price, not as the general product model.
  - Equality against the reference `last` is documented as a conservative
    `quantleet` rejection policy.
  - Same-event priority is documented as existing executable orders before
    newly triggered stop-family orders, aligned with deterministic
    price-time-like priority.
  - Test scenarios reflect the same terminology and decisions.
  - Read-only subagent review has no unresolved best-practice-settled blocking
    findings.
- Out of scope:
  - Implementation code.
  - Test code.
  - Public API expansion for explicit `trigger_condition`.
  - Venue-specific side/type validation, price bands, reduce-only, live/paper
    adapters, brackets, OCO/OTO, and `% + stop_limit`.

## Evaluator Acceptance Contract

- Evaluator owner:
  - `Codex`
- Evaluator-owned done contract for this slice:
  - Close only after updated docs faithfully capture the human decisions,
    external practice is checked where relevant, subagent findings are
    synthesized, and fresh repo checks pass.
- Acceptance artifact location:
  - this active plan
- How the generator and evaluator agreed on done before execution:
  - Docs must avoid claiming all venues behave identically. They should instead
    separate the generic trigger primitive from venue-specific order-entry
    validation and product naming.
- Checks the evaluator will use:
  - Diff review against the human decisions.
  - Subagent review fan-out.
  - Fresh `uv run poe repo-check`.
  - Fresh `git diff --check`.
- Auto-fail conditions:
  - changing runtime code
  - reintroducing side-derived trigger direction
  - describing bar close as the universal trigger reference
  - presenting equality rejection as a universal exchange rule
  - skipping subagent synthesis

## Generator Work Log

- Planned slice order:
  1. Create this active plan.
  2. Update product spec terminology and rules.
  3. Update test scenario terminology and coverage obligations.
  4. Run read-only subagent review fan-out.
  5. Incorporate objective findings.
  6. Run verification.
  7. Record evaluator findings and final disposition.
- Notes:
  - Parent agent owns all writes.
  - Subagents are read-only reviewers.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
  - No blocking findings remain after subagent review and follow-up fixes.
  - Human-approved policy captured in the product spec:
    - stop-family orders are generic price-trigger primitives
    - trigger direction is inferred from `stop_price` relative to the last
      evaluated `last` reference price at order intake
    - side, position purpose, and limit price do not determine trigger
      direction
    - equality against the reference `last` is rejected as a conservative
      `quantleet` ambiguity policy
    - existing executable orders are evaluated before newly triggered
      stop-family orders at the same event point
  - External practice synthesis:
    - Coinbase Prime and Kraken describe stop/stop-limit behavior as trigger
      price activation followed by market or limit execution.
    - Coinbase Advanced documents that already-met stops may trigger
      instantly, while Binance-style APIs may reject orders that would trigger
      immediately; the docs therefore correctly avoid claiming equality
      rejection is universal exchange behavior.
    - Coinbase Exchange, Coinbase Derivatives, Binance.US, and Kraken-style
      rulebooks support price-time/FIFO as the common matching-priority model;
      this supports the existing-before-newly-triggered same-event policy as a
      deterministic price-time-like backtest rule.
  - Subagent findings incorporated:
    - The test scenario plan now states that equality rejection is a local
      `quantleet` ambiguity policy, not universal venue conformance.
    - The E3 priority scenario now tests public fill ordering with sufficient
      cash first; constrained-cash behavior is demoted to an additional
      accounting interaction variant.
    - The minimum implementation-ready test batch now includes same-event
      priority coverage.
    - The post-trigger tail scenarios were corrected so bullish and bearish
      labels match the actual `close >= open` execution-model rule.
  - No human-intent questions remain for this trigger-policy slice.
- Verification evidence:
  - `uv run poe repo-check`
    - output:
      - `Poe => uv run python scripts/repo_check.py`
      - `repository checks passed`
  - `git diff --check`
    - output: no whitespace errors reported
  - targeted stale-wording search:
    - searched for old `active_bar_close`, `active_bar.close`, side-only, and
      invalid path wording in the updated stop-limit docs
    - only intentional bar-backtest explanatory wording remains
- Final disposition:
  - `complete`
