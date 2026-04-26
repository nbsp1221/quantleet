# Active Plan

- Date: `2026-04-26`
- Task: `Run standalone stop_market cross-validation with corrected strategy set`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - update the `/tmp/quantcraft-stop-xval` cross-validation harness to use the
    corrected standalone stop-market strategy candidates
  - run the experiment across multiple libraries where the strategy semantics
    can be credibly expressed
  - report whether the shipped `stop_market` behavior remains credible when
    OTO, OCO, bracket, and attached protective stop semantics are excluded
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/order-sizing.md`
  - `docs/design-docs/index.md`
  - `docs/design-docs/package-topology-and-naming.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/DESIGN.md`
  - `docs/PLANS.md`
  - `docs/plans/2026-04-23-stop-trigger-order-spec-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-test-matrix-design.md`
  - `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
  - `docs/plans/2026-04-26-stop-market-standalone-validation-candidates-correction.md`
- Why these are governing:
  - They define the shipped standalone stop-market scope, the corrected
    strategy candidates, and the repo workflow for Tier A validation work.
- In-repo scope:
  - add and complete this active plan
- Out-of-repo scope:
  - modify `/tmp/quantcraft-stop-xval` harness scripts
  - optionally modify `/tmp/quantcraft-stop-xval-nautilus` runner scripts if
    Nautilus is included in the comparison
  - run local comparator experiments and write `/tmp` result artifacts
- Tier A progression requested: `yes`
- Approval record, if required:
  - Tier A and scope-expansion approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread direction on `2026-04-26` to run cross-validation in the
      existing `/tmp` harness with the corrected standalone strategy set
    - Granted scope:
      repository-local plan updates, `/tmp` harness edits, local comparator
      execution, and task-driven use of already-installed comparator libraries
    - Expiration:
      end of this standalone cross-validation slice
    - Audit reference:
      this active plan and the corrected strategy candidate plan
- Verification commands:
  - `cd /tmp/quantcraft-stop-xval && uv run python run_standalone_stop_validation.py`
  - `uv run poe repo-check`
- Success criteria:
  - experiment uses the corrected standalone strategy set:
    - opening range breakout stop entry
    - Donchian / Turtle-style breakout stop entry
    - inside-bar breakout stop entry
  - attached protective stops, OTO, OCO, and bracket semantics are not used in
    the validation strategy implementations
  - final report lists executed comparator engines and explains any mismatch
    causes
- Out of scope:
  - changing shipped `quantcraft` runtime code
  - implementing attached orders, OTO, OCO, bracket, `stop_limit`, or shorting

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - accept only if fresh result artifacts prove the corrected standalone
    strategies were run and any comparator limitations are disclosed
- Acceptance artifact location:
  - this active plan
  - `/tmp/quantcraft-stop-xval/results/standalone_stop_validation.json`
- How the generator and evaluator agreed on done before execution:
  - done means the experiment no longer relies on protective stop-loss orders
    attached after entry and the resulting mismatches, if any, are attributable
    to standalone stop-entry semantics or known adapter limitations
- Checks the evaluator will use:
  - inspect harness strategy definitions
  - inspect fresh result artifact
  - run `uv run poe repo-check`
- Auto-fail conditions:
  - validation strategy submits protective stop orders after entry
  - report treats attached-order behavior as current shipped scope
  - missing fresh verification evidence

## Generator Work Log

- Planned slice order:
  1. implement corrected standalone strategy set in `/tmp` harness
  2. run cross-validation across feasible engines
  3. inspect first divergences and summarize causes
  4. complete this plan and run repo-check
- Notes:
  - exact equality is not required; mismatch explanation is required
  - comparator engines that cannot credibly express the corrected strategies
    will be triaged rather than silently included
  - implemented a fresh runner at
    `/tmp/quantcraft-stop-xval/run_standalone_stop_validation.py`
  - executed comparator engines:
    - `quantcraft`
    - `backtesting.py`
    - `backtrader`
  - `vectorbt` was not promoted into this runner because its public workflow is
    signal-array/stop-array based rather than explicit standalone stop-entry
    order submission; including it would test an adapter translation more than
    the same order primitive
  - Nautilus remains a useful future comparator, but the existing Nautilus
    runner covered the previous mean-reversion pattern and was not reused for
    this fresh three-strategy run
- Blockers or scope changes:
  - None.

## Evaluator Review

- Findings:
  - No material mismatch found in the executed comparator set.
  - All three corrected standalone strategies produced exact result parity
    across `quantcraft`, `backtesting.py`, and `backtrader`.
  - Strategy results:
    - `opening_range_breakout`:
      - final equity: `993564.1400000004`
      - closed trades: `36`
      - first divergences vs `quantcraft`: none
    - `donchian_breakout`:
      - final equity: `1004179.49` for `quantcraft` / `backtrader`;
        `1004179.4900000001` for `backtesting.py`
      - closed trades: `11`
      - first divergences vs `quantcraft`: none
    - `inside_bar_breakout`:
      - final equity: `1002255.8300000002` for `quantcraft` / `backtrader`;
        `1002255.8300000001` for `backtesting.py`
      - closed trades: `37`
      - first divergences vs `quantcraft`: none
  - This supports the revised diagnosis: prior large mismatches came from
    validating attached protective stop behavior with a standalone order
    surface, not from the shipped standalone `stop_market` primitive.
- Verification evidence:
  - Cross-validation command:
    - `cd /tmp/quantcraft-stop-xval && uv run python run_standalone_stop_validation.py`
    - Result: command exited `0`
    - Fresh artifact:
      `/tmp/quantcraft-stop-xval/results/standalone_stop_validation.json`
  - Repo/document lane:
    - `uv run poe repo-check`
    - Result: `repository checks passed`
- Final disposition:
  - `accepted`
