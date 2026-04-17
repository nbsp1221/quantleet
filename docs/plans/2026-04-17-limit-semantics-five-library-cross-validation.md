# Active Plan

- Date: `2026-04-17`
- Task: `Cross-validate the resolved limit-order bug against at least five external libraries and judge mismatches`
- Status: `complete`
- Risk class: `Tier B`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - verify the resolved favorable sell-limit scenario against at least five external backtesting libraries
  - determine whether any remaining mismatch indicates a `quantcraft` logic defect or a comparator-specific modeling difference
- Governing docs:
  - `AGENTS.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
  - `docs/plans/2026-04-15-limit-cross-engine-results.md`
  - `docs/plans/2026-04-17-limit-semantics-verification.md`
- Why these are governing:
  - they define the conservative fill contract, the prior trust problem, and the repository requirements for evidence-bearing verification
- In-repo scope:
  - repo-local inline verification against current `quantcraft`
  - evidence artifact for this expanded cross-validation slice
- Out-of-repo scope:
  - ephemeral comparator installs via `uv --with ...`
  - temporary files under `/tmp` needed to satisfy comparator APIs
- Tier A progression requested: `no`
- Approval record, if required:
  - requestor: `user`
  - human approver: `user`
  - countersignature or equivalent verification marker: current chat request explicitly requiring five-library cross-validation and mismatch judgment
  - scope granted: ephemeral external comparator installs/execution and temporary artifacts required to run the repro across multiple libraries
  - expiration: end of current session
  - audit reference or sanitized audit link: current chat plus this active plan
- Verification commands:
  - inline `uv run python - <<'PY' ... PY` for current `quantcraft`
  - inline `uv run --with <library> python - <<'PY' ... PY` comparator repros
- Success criteria:
  - run the resolved favorable sell-limit repro against at least five external libraries when technically feasible
  - state which comparators are apples-to-apples, which are only approximate, and why
  - decide whether any mismatch is evidence of a current `quantcraft` logic issue
- Out of scope:
  - code changes
  - freezing real-data canonical goldens
  - rerunning the full multi-strategy historical experiment

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - done means the conclusion is based on fresh executable evidence from at least five external libraries or a clearly documented technical reason why a candidate is not reliable for the exact scenario
- Acceptance artifact location:
  - `docs/plans/2026-04-17-limit-semantics-five-library-cross-validation.md`
- How the generator and evaluator agreed on done before execution:
  - the evaluator will distinguish comparator disagreement caused by the library's own default fill model from disagreement caused by `quantcraft`
- Checks the evaluator will use:
  - fresh comparator outputs
  - direct source inspection when a library proves not apples-to-apples
  - consistency check against current `quantcraft` semantics tests
- Auto-fail conditions:
  - claiming universal agreement without a mismatch table
  - blaming `quantcraft` without isolating comparator-specific defaults
  - treating an obviously non-comparable engine as equal evidence without labeling the caveat

## Generator Work Log

- Planned slice order:
  - confirm which comparator libraries are installable
  - run the repro in the lowest-friction equivalent form for each engine
  - classify each comparator as apples-to-apples, approximate, or unreliable
  - judge whether any mismatch points back to `quantcraft`
- Notes:
  - exact 3-bar parity is not possible in every framework because some engines only expose next-bar actions after warmup or delay semantics; equivalent delayed scenarios were used where required
- Blockers or scope changes:
  - `pybroker` install name was `lib-pybroker`, not `pybroker`
  - `zipline-reloaded` required a temporary `csvdir` bundle and a daily-session equivalent scenario
  - `quanttrader` package installed ephemerally but is not a reliable comparator due stale runtime compatibility and close-only backtest fills
  - `nautilus_trader` remained a non-decisive comparator for this scenario because prior repo evidence already showed it was not apples-to-apples for the relevant passive sell-limit family

## Evaluator Review

- Findings:
  - Fresh external-library results:
    - `backtrader`: matched the resolved `quantcraft` result; resting sell limit filled at `114.0`
    - `pyalgotrade`: matched the resolved `quantcraft` result; resting sell limit filled at `114.0`
    - `backtesting.py`: matched the resolved conservative outcome in a 4-bar equivalent repro; exit filled at `114.0`
    - `zipline-reloaded`: matched the resolved conservative outcome in a daily 3-session equivalent repro; the resting sell limit cleared on the `114.0` session and the position was flat by the final row
    - `lib-pybroker`: did **not** match exactly; exit filled at `114.5`
  - Mismatch judgment:
    - the `lib-pybroker` mismatch is **not** evidence of a current `quantcraft` bug
    - root cause: `StrategyConfig.exit_sell_fill_price` defaults to `PriceType.MIDDLE`, so the comparator's own default exit-price model intentionally fills the exit at the bar midpoint instead of the limit price
  - Reliability judgment for additional inspected libraries:
    - `quanttrader` is not a reliable comparator for this exact scenario because its backtest broker crosses standing orders against `Close` only and its current package also has stale runtime compatibility issues (`np.str`, old pandas append usage)
    - `nautilus_trader` remains non-decisive for this scenario because prior repo evidence already showed it was not apples-to-apples for the passive sell-limit family under investigation
  - Final judgment:
    - the resolved `quantcraft` implementation agrees with the conservative comparator cluster for this bug shape
    - no fresh evidence from this five-library pass indicates that the current `quantcraft` logic is still wrong on the original favorable sell-limit problem
- Verification evidence:
  - Current `quantcraft` zero-cost repro:
    - output: `fills [('buy', 110.0, 120, 0.0), ('sell', 114.0, 180, 0.0)]`
  - `backtrader` zero-cost repro:
    - output: `fills [('buy', 110.0, 2, 0.0), ('sell', 114.0, 3, 0.0)]`
  - `pyalgotrade` zero-cost repro:
    - output: `fills [('buy', 110.0, '2026-01-01T01:00:00'), ('sell', 114.0, '2026-01-01T02:00:00')]`
  - `backtesting.py` equivalent repro:
    - output: trade table with `EntryPrice 109.0`, `ExitPrice 114.0`
  - `zipline-reloaded` daily-session equivalent repro:
    - output final state table:
      - `2024-01-02 ... pos 0 open_orders 1`
      - `2024-01-03 ... pos 1 open_orders 1`
      - `2024-01-04 ... pos 0 open_orders 0`
    - the final session bar had `open=high=low=close=114.0`, so the cleared resting sell-limit could only have filled at `114.0`
  - `lib-pybroker` equivalent repro:
    - output order table:
      - buy fill `110.0`
      - sell limit `114.0`
      - actual sell `fill_price 114.5`
    - supporting config evidence:
      - `StrategyConfig().exit_sell_fill_price == PriceType.MIDDLE`
      - available `PriceType`: `OPEN`, `LOW`, `HIGH`, `CLOSE`, `MIDDLE`, `AVERAGE`
  - `quanttrader` inspected source evidence:
    - `DataBoard.get_current_price()` returns `Close`
    - `BacktestBrokerage._try_cross_order()` compares only against that single `current_price`
- Final disposition:
  - `accepted`
