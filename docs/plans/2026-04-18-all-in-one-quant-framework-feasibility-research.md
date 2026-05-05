- Date: 2026-04-18
- Task: Feasibility and architecture research for an all-in-one quant framework spanning backtest, paper trading, and live trading
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal:
  - Assess whether `quantleet` can realistically become a single framework
    covering backtest, paper trading, and live trading with minimal strategy
    rewrites, and identify the architectural conditions required to make that
    promise credible.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/paper-trading.md`
  - `docs/product-specs/live-trading.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Why these are governing:
  - They define the current scope, future planning surfaces, architecture
    boundaries, and safety constraints for any recommendation about
    backtest-to-live unification.
- In-repo scope:
  - Current backtest/research docs and architecture constraints.
- Out-of-repo scope:
  - Official external docs and comparable framework designs.
- Tier A progression requested: `no`
- Approval record, if required:
  - None. This is read-only architecture research.
- Verification commands:
  - targeted local doc/source inspection
  - official external documentation lookups
- Success criteria:
  - State whether the all-in-one goal is feasible and under what constraints.
  - Explain why many libraries split these concerns.
  - Recommend an architecture direction that preserves strategy portability
    without making impossible guarantees.
- Out of scope:
  - Implementing the architecture.

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - The conclusion must distinguish feasible portability guarantees from
    unrealistic "same strategy works everywhere without caveats" marketing.
- Acceptance artifact location:
  - `docs/plans/2026-04-18-all-in-one-quant-framework-feasibility-research.md`
- How the generator and evaluator agreed on done before execution:
  - Done means a clear feasibility judgment plus the key architectural tradeoff
    that determines success or failure.
- Checks the evaluator will use:
  - local doc inspection
  - official external docs
  - explicit trade-off analysis
- Auto-fail conditions:
  - claiming universal portability without discussing venue/runtime
    incompatibilities
  - ignoring Tier A live-trading safety implications

## Generator Work Log

- Planned slice order:
  - inspect local future-planning docs
  - ask one key clarification question
  - research external framework tradeoffs
  - synthesize feasibility judgment and architecture guidance
- Notes:
  - Research/design only.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
  - The all-in-one goal is feasible in the strong sense that one framework can
    span backtest, paper, and live with shared strategy code.
  - Existing systems already prove important parts of this:
    - NautilusTrader explicitly states that the same strategies and execution
      algorithms run against both the backtest engine and a live trading node.
    - QuantConnect/LEAN explicitly positions the same algorithm design across
      backtests and live trading.
    - Freqtrade supports one strategy codebase across backtest, dry-run, and
      live trading, though within a narrower pair-centric model.
  - So the reason many libraries do not deliver “very easy Pine-like UX plus
    deep research-to-live parity” is not physical impossibility. The primary
    reasons are product trade-offs and scope management.
  - The hard part is not strategy-code reuse; the hard part is preserving
    honest semantics across environments:
    - backtest is deterministic and replay-based
    - paper is simulated execution with imperfect approximations
    - live adds venue rules, rejections, latency, partial fills, session
      constraints, and infrastructure failures
  - Therefore the realistic promise is:
    - same strategy logic
    - same internal intent/target model
    - same shared trading kernel where possible
    - but not identical fills and outcomes across all environments
  - Your proposed direction is correct in principle:
    - use one shared event-driven trading kernel
    - run the same strategy logic in backtest, paper, and live
    - feed each environment through different runtime adapters
  - Important constraint:
    - converting OHLCV bars into synthetic ticks can reduce code-path drift and
      is useful
    - but OHLCV-to-tick conversion cannot recreate actual microstructure such
      as queue position, hidden liquidity, within-bar order-book evolution,
      message sequencing, or latency races
    - it improves architectural unification, but it does not make bar-only
      backtests equivalent to real exchange replay
  - The parity ladder is therefore:
    - strongest: historical tick/order-book replay -> paper -> live
    - medium: trade-tick replay -> paper -> live
    - weakest but still viable: OHLCV with conservative synthetic path ->
      paper -> live
  - Architecture implication for `quantleet`:
    - you can build the framework you want
    - the user-facing Pine-like DSL should be treated as an authoring layer
    - the internal engine should use stricter symbol-bearing intents/targets
    - capability mismatches must fail fast instead of silently degrading in
      live/paper contexts
  - Refined product conclusion from the current chat:
    - the intended product is not “a better backtester”
    - it is an integrated quant framework with four simultaneous promises:
      - very easy strategy authoring
      - serious research validation such as WFA and replayable evaluation
      - same strategy code across backtest, paper, and live
      - one coherent library/framework rather than disconnected tools
    - no widely adopted product appears to strongly optimize all four at once
      because most frameworks choose one or two primary promises:
      - `NautilusTrader`: research-to-live parity and execution realism
      - `QuantConnect/LEAN`: unified algorithm lifecycle and deployment
      - `Freqtrade`: one strategy codebase across backtest/dry/live for a bot
        workflow
      - `backtesting.py` / `vectorbt`: strategy research ergonomics
    - the missing combination is therefore better explained by product-focus
      trade-offs than by impossibility
- Verification evidence:
  - Local docs:
    - `docs/design-docs/backtest-execution-semantics.md`
    - `docs/product-specs/paper-trading.md`
    - `docs/product-specs/live-trading.md`
  - External official docs:
    - NautilusTrader:
      - `https://nautilustrader.io/docs/latest/concepts/live/`
      - `https://nautilustrader.io/docs/latest/concepts/backtesting`
      - `https://nautilustrader.io/docs/latest/concepts/strategies/`
    - QuantConnect / LEAN:
      - `https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-types/market-orders`
      - `https://cdn.quantconnect.com/docs/i/Quantconnect-Writing-Algorithms-Python.pdf`
    - Freqtrade:
      - `https://www.freqtrade.io/en/latest/backtesting/`
      - `https://www.freqtrade.io/en/stable/strategy-customization/`
- Final disposition:
  - Complete. The all-in-one goal is feasible and already partially validated
  by existing systems, but only if the portability promise is stated
  honestly and the architecture separates user DSL, internal trading model,
  and environment adapters.
