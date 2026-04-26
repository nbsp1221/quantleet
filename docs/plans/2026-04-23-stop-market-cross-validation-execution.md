# Active Plan

- Date: `2026-04-23`
- Task: `Cross-validate the shipped stop_market slice against comparator backtesting libraries`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - Build a temporary cross-validation harness outside the repository under
    `/tmp`, run three realistic stop-market strategy patterns against
    `quantcraft` and comparator libraries on the same BTC/USDT 1h CSV dataset,
    and explain any mismatches by execution-semantics differences rather than
    expecting exact equality.
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
  - `docs/plans/2026-04-23-stop-trigger-order-test-matrix-design.md`
  - `docs/plans/2026-04-23-stop-trigger-order-execution.md`
  - `docs/plans/2026-04-23-stop-market-real-world-strategy-candidates.md`
- Why these are governing:
  - They define the current shipped stop-market semantics, permitted strategy
    surface, runtime-sensitive constraints, and the three realistic validation
    candidates this experiment will exercise.
- In-repo scope:
  - Add this active plan only.
  - Keep repository code unchanged unless a later, separate approved slice is
    opened to address findings.
- Out-of-repo scope:
  - Create a temporary `uv` project under `/tmp`
  - Read local comparator library clones under `/tmp`
  - Read a local BTC/USDT 1h CSV dataset
  - Install temporary Python dependencies into the experiment environment if
    needed
  - Produce temporary experiment scripts and result artifacts under `/tmp`
- Tier A progression requested: `yes`
- Approval record, if required:
  - Scope-expansion and Tier A experiment approval record:
    - Requestor: `Naki (thread user)`
    - Human approver: `Naki (thread user)`
    - Verification marker:
      explicit thread direction on `2026-04-23` to create a new `/tmp` project,
      code the three realistic strategies for `quantcraft` and comparator
      libraries, run the cross-validation experiment on the shared BTC/USDT 1h
      CSV, and prioritize explaining mismatches
    - Granted scope:
      repository-local planning plus `/tmp` experiment creation, local library
      inspection, dependency installation inside the temporary project, and
      local result generation for stop-market cross-validation
    - Expiration:
      end of this `2026-04-23` experiment slice
    - Audit reference:
      this active plan together with the approved stop-market spec, test
      matrix, execution plan, and real-world strategy candidate note
- Verification commands:
  - `uv run poe repo-check`
  - experiment-local run commands to be recorded in the evaluator section once
    the harness is built
- Success criteria:
  - A `/tmp` cross-validation harness exists and can run the same three
    strategy patterns across `quantcraft` and at least two comparator
    libraries.
  - All engines use the same BTC/USDT 1h dataset and comparable fee/slippage
    assumptions.
  - The final report prioritizes explaining mismatches, not forcing exact
    equality.
  - Repository code remains unchanged in this slice unless separately approved.
- Out of scope:
  - fixing comparator libraries
  - changing shipped `quantcraft` code in this slice
  - proving trading alpha

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - Accept only if the experiment is actually run, the result summary is based
    on fresh evidence, and any mismatches are analyzed in semantic terms rather
    than hand-waved as “different libraries”.
- Acceptance artifact location:
  - this active plan
  - temporary `/tmp` experiment workspace and generated results
- How the generator and evaluator agreed on done before execution:
  - Done means:
    1. the harness runs the same three strategy families on the same dataset
    2. outputs are normalized enough to compare trade timing and order behavior
    3. the final report names concrete causes for any divergence when possible
- Checks the evaluator will use:
  - inspect the temporary harness layout and adapter coverage
  - inspect normalized result artifacts
  - rerun the repo-local doc check
  - cite the exact experiment commands that ran
- Auto-fail conditions:
  - claiming equivalence without running the experiment
  - silently changing repository code during the experiment slice
  - using different datasets across engines
  - reporting only PnL and ignoring trade-semantics differences

## Generator Work Log

- Planned slice order:
  1. Locate the shared BTC/USDT 1h CSV and comparator libraries available
     locally.
  2. Create the `/tmp` `uv` experiment project and define a normalized result
     schema.
  3. Implement the three strategy patterns for `quantcraft` and comparator
     engines.
  4. Run the experiment and collect artifacts.
  5. Compare outputs and explain mismatches.
  6. Record verification evidence here and report findings to the user.
- Notes:
  - Comparator priority is `quantcraft`, `backtesting.py`, and `backtrader`
    because they are the most practical first-pass bar-based baselines.
- Blockers or scope changes:
  - The checked-in dataset was used directly:
    - `tests/fixtures/backtest/binance_usdm_btcusdtusdt_1h_2025.csv`
  - Comparator set was finalized as:
    - `quantcraft`
    - `backtesting.py`
    - `backtrader`
  - The temporary harness was created under:
    - `/tmp/quantcraft-stop-xval`

## Evaluator Review

- Findings:
  - No repository-code findings, because this slice intentionally kept repo
    code unchanged.
  - Experiment findings:
    - `breakout_stop_entry`
      - `quantcraft` and `backtrader` matched exactly on trade count and final
        equity
      - `backtesting.py` differed on exactly one trade and emitted explicit
        same-bar contingent-order ambiguity warnings
    - `pullback_limit_atr`
      - all three engines matched on trade count
      - `quantcraft` was modestly more favorable by about `117.52`
      - the first divergence was a stop-loss exit where `quantcraft` exited at
        the stop trigger level while both comparator engines exited lower on
        the same bar
    - `bracket_like_market`
      - this produced the large mismatch cluster
      - `quantcraft`: `227` trades, final equity `997,181.153571`
      - `backtesting.py`: `253` trades, final equity `981,431.982143`
      - `backtrader`: `244` trades, final equity `983,349.353571`
      - root cause is not plain stop correctness; it is child-exit lifecycle
        timing
      - comparator engines support linked contingent/bracket-style exits that
        become active with the parent entry, while current `quantcraft`
        creates the protective stop and target from `on_bar()` and therefore
        activates them starting on the next bar
  - Overall judgment:
    - the shipped `stop_market` slice itself looks credible for ordinary stop
      entry/exit use
    - the largest trust gap is around bracket-like same-bar child activation,
      not around the core stop trigger model
- Verification evidence:
  - Repo/document lane:
    - `uv run poe repo-check`
    - Result: `repository checks passed`
  - Experiment workspace:
    - `/tmp/quantcraft-stop-xval`
  - Experiment command:
    - `cd /tmp/quantcraft-stop-xval && uv run python run_cross_validation.py`
  - Generated artifacts:
    - `/tmp/quantcraft-stop-xval/results/cross_validation_results.json`
    - `/tmp/quantcraft-stop-xval/results/summary.md`
- Final disposition:
  - `accepted`
