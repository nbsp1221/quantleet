# Active Plan

- Date: `2026-04-15`
- Task: `Promote conservative backtest execution semantics into canonical docs`
- Status: `complete`
- Risk class: `Tier A`
- Requestor: `user`
- Owner: `Codex`

## Planner Contract

- Goal:
  - promote the agreed backtest execution semantics from session discussion into canonical repository docs
  - make the architecture split explicit: backtest path generation owns synthetic ticks, trading matching owns fills
  - validate the promoted contract against external best-practice references for OHLC backtesting and limit-order handling
- Governing docs:
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/index.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/design-docs/index.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Why these are governing:
  - `ARCHITECTURE.md` defines bounded-context responsibility and shared-kernel intent
  - `backtest-mvp.md` is the current implemented product contract for the backtest slice
  - `docs/design-docs/` is the long-lived authority for architectural decisions beyond a plan artifact
  - `RELIABILITY` and `SECURITY` define reproducibility and Tier A handling expectations
- In-repo scope:
  - update canonical docs for backtest execution semantics
  - add or update a long-lived design doc under `docs/design-docs/`
  - update any relevant doc indexes
  - update the active plan with evaluator findings and source-backed best-practice notes
- Out-of-repo scope:
  - code changes
  - benchmark reruns
  - external package changes
  - live trading or paper trading behavior changes
- Tier A progression requested: `yes`
- Approval record, if required:
  - requestor: `user`
  - human approver: `Naki`
  - countersignature or equivalent verification marker: `user approval in chat after git-config identity check`
  - scope granted: `task-driven web research, use of external references, promotion of execution-semantics contract into canonical repo docs`
  - expiration: `2026-04-16T23:59:59+09:00`
  - audit reference or sanitized audit link: `chat turn approval + prior experiment approval lineage recorded in 2026-04-15-limit-cross-engine-experiment.md`
- Verification commands:
  - `uv run poe repo-check`
- Success criteria:
  - canonical docs clearly state that matching consumes ticks only and does not own path generation
  - canonical docs clearly forbid order-dependent path fabrication while allowing order-aware acceleration over a fixed canonical path
  - canonical docs clearly define conservative within-bar and gap semantics at a level suitable for future implementation
  - a long-lived design doc captures the architectural rationale and performance tradeoff
  - the active plan records whether external best-practice sources reveal any material conflict
- Out of scope:
  - implementing the new semantics
  - changing current backtest code behavior
  - freezing new limit regression goldens

## Evaluator Acceptance Contract

- Evaluator owner: `Codex`
- Evaluator-owned done contract for this slice:
  - done means the repository has a coherent canonical documentation set for conservative backtest execution semantics, with no contradiction between architecture, product-spec, and design-doc layers, and with explicit note of any externally observed best-practice tension
- Acceptance artifact location:
  - `docs/plans/2026-04-15-backtest-semantics-doc-promotion-plan.md`
- How the generator and evaluator agreed on done before execution:
  - this plan freezes the documentation promotion slice before any edits
- Checks the evaluator will use:
  - diff review against governing docs
  - source-backed external best-practice comparison
  - `uv run poe repo-check`
- Auto-fail conditions:
  - canonical docs still imply optimistic limit-price improvement from OHLC extremes
  - canonical docs mix path generation and matching responsibilities
  - no durable design doc is added for the promoted semantics
  - verification is not run from the current repo state

## Generator Work Log

- Planned slice order:
  - research external references for intrabar ambiguity, bar-based limit handling, and event-driven matching separation
  - promote agreed semantics into `ARCHITECTURE.md`, `docs/product-specs/backtest-mvp.md`, and a long-lived design doc
  - update indexes if needed
  - run repo-local doc/structure verification
- Notes:
  - this slice documents the intended contract; it does not claim the implementation already matches it
- Blockers or scope changes:
  - none
- Research notes:
  - Coinbase Help states that limit orders execute only at the specified limit price or better, which supports the marketable-limit and no-worse-than-limit parts of the promoted contract
  - Backtrader official docs model limit orders conservatively on OHLC bars: if the bar opens through the limit, execution happens at `open`; if the bar later touches the limit, execution happens at the limit price
  - Backtesting.py official docs explicitly state that it cannot make decisions or trades within candlesticks, which is stricter than the promoted `on_bar` plus synthetic-path model but not in conflict with the repository's lookahead guardrail
  - NautilusTrader official docs emphasize deterministic event-driven replay and performance-sensitive loading/streaming controls, which aligns with keeping one matching kernel and allowing performance optimizations that do not change outcomes

## Evaluator Review

- Findings:
  - no material conflict was found between the promoted conservative limit semantics and the reviewed official references
  - the promoted contract is more conservative than the current `quantcraft` implementation and is directionally aligned with common OHLC backtest practice shown in Backtrader
  - the promoted contract remains compatible with real exchange semantics because marketable limits still fill immediately at a no-worse-than-limit executable price
  - the promoted performance rule needed one explicit clarification: order-aware traversal acceleration is acceptable only when it preserves the already-defined canonical path and does not fabricate order-specific prices
- Verification evidence:
  - `uv run poe repo-check` -> `repository checks passed`
  - external references reviewed:
    - `https://help.coinbase.com/en/trading-and-funding/pricing-and-fees/nbbo-pricing-transparency`
    - `https://www.backtrader.com/blog/posts/2015-08-08-order-creation-execution/order-creation-execution/`
    - `https://kernc.github.io/backtesting.py/doc/examples/Quick%20Start%20User%20Guide.html`
    - `https://nautilustrader.io/docs/latest/concepts/backtesting/`
    - `https://nautilustrader.io/docs/nightly/getting_started/backtest_low_level/`
- Final disposition:
  - `accepted for documentation promotion`
