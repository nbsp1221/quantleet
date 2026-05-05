- Date: 2026-04-18
- Task: Research and design direction for single-asset Pine-like UX versus future multi-asset strategy architecture
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal:
  - Define the problem behind the current `symbol=...` friction in strategy
    APIs, research how representative quant libraries model single-asset and
    multi-asset strategies, and recommend a future-proof architecture direction
    for `quantleet` that preserves Pine-like ergonomics for simple strategies
    without boxing the engine out of multi-asset use cases.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/design-docs/backtest-execution-semantics.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Why these are governing:
  - They define the current public strategy surface, current backtest scope,
    topology rules, and reliability/safety boundaries that any future
    architecture recommendation must respect.
- In-repo scope:
  - Current strategy API, backtest/trading boundaries, and product-scope docs.
- Out-of-repo scope:
  - Official documentation and authoritative examples for representative
    external libraries and platforms.
- Tier A progression requested: `no`
- Approval record, if required:
  - None. This is read-only research and design guidance.
- Verification commands:
  - targeted local `sed -n`, `nl -ba`, and `rg -n` reads
  - official external documentation lookups
- Success criteria:
  - Define the problem precisely rather than as a taste argument.
  - Distinguish UX-layer concerns from engine/runtime concerns.
  - Compare at least several representative external systems.
  - Recommend a future architecture direction with trade-offs and why it avoids
    a later rewrite.
- Out of scope:
  - Implementing the API redesign.

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - The recommendation must be evidence-based, must distinguish single-asset
    and multi-asset contexts, and must not assume that one user-facing DSL has
    to be the only engine-facing abstraction.
- Acceptance artifact location:
  - `docs/plans/2026-04-18-single-vs-multi-asset-strategy-architecture-research.md`
  - `docs/design-docs/unified-strategy-runtime-design.md`
- How the generator and evaluator agreed on done before execution:
  - Done means a defensible problem framing plus a recommended architecture
    direction, not just a library popularity survey.
- Checks the evaluator will use:
  - local doc/source inspection
  - official external docs
  - explicit trade-off analysis
- Auto-fail conditions:
  - conflating current MVP scope with long-term engine architecture
  - presenting only one approach without alternatives
  - making external claims without sources

## Generator Work Log

- Planned slice order:
  - inspect current local strategy API and scope docs
  - clarify one key product-direction preference
  - research external official docs
  - synthesize 2-3 architecture approaches and recommend one
- Notes:
  - Research/design only. No implementation.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
  - Representative libraries do not converge on one standard inheritance
    pattern such as `SingleAssetStrategy` / `MultiAssetStrategy`.
  - Instead, they cluster into several distinct architectural families:
    - single-chart / single-feed strategy DSLs
    - multi-asset portfolio APIs with explicit asset handles
    - execution-native strategy engines with explicit instrument/order objects
    - pair-centric bot frameworks that iterate one pair at a time while still
      exposing wider-market reference data
  - Family 1: single-chart DSL
    - `backtesting.py` centers strategy ergonomics on a single data series and
      exposes `self.buy()` / `self.sell()` with no symbol parameter in the
      common path.
    - `backtrader` uses one `Strategy` base class, but `buy(data=None, ...)`
      defaults to the first feed, so single-feed usage remains symbol-free
      while multi-feed usage can opt into explicit targeting.
  - Family 2: multi-asset portfolio API
    - `Zipline` does not hide the asset handle; order calls are
      `order(asset, amount)` or target-based variants such as
      `order_target_percent(asset, target)`.
    - `QuantConnect` similarly requires a `Symbol` on order helpers such as
      `buy("AAPL", 10)` and is designed around a broader securities universe.
    - `vectorbt` sidesteps imperative order helpers for the common case:
      asset identity travels in array columns and portfolio constructors such as
      `Portfolio.from_signals(...)`.
  - Family 3: execution-native engine
    - `NautilusTrader` uses a single `Strategy` base class and explicit
      `instrument_id` in configuration and order objects. It is much closer to
      a live-trading engine than a Pine-like chart DSL, and a single strategy
      can work with one or many instruments depending on configuration and
      subscriptions.
  - Family 4: pair-centric bot framework
    - `Freqtrade` also uses a single strategy base, but the strategy logic is
      effectively evaluated per pair/dataframe. It supports cross-pair context
      through informative pairs, dynamic whitelists, and pair metadata rather
      than through a separate multi-asset strategy class.
  - Architecture implication:
    - libraries are usually not choosing between “one base class” and “two base
      classes” in isolation
    - they choose a primary mental model first:
      - chart-centric discretionary DSL
      - portfolio allocator
      - venue/execution engine
      - pair-scanning bot
    - the class hierarchy follows that choice rather than the other way around
  - For `quantleet`, the current product promise is still a single-symbol
    backtest/research UX. That makes Pine-like single-asset ergonomics a
    natural top-level user DSL. But the long-term engine should still use
    explicit symbol-bearing internal intents/targets, because every multi-asset
    family above ultimately carries asset identity explicitly at the engine
    layer.
- Verification evidence:
  - Local governing docs:
    - `docs/product-specs/backtest-mvp.md`
    - `docs/product-specs/research-ergonomics.md`
    - `src/quantleet/research/strategy.py`
  - Official external docs reviewed:
    - Backtesting.py:
      - `https://kernc.github.io/backtesting.py/`
      - `https://kernc.github.io/backtesting.py/doc/examples/Quick%20Start%20User%20Guide.html`
      - `https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html`
    - Backtrader:
      - `https://www.backtrader.com/docu/strategy/`
    - Zipline:
      - `https://zipline.ml4trading.io/`
      - `https://zipline.ml4trading.io/beginner-tutorial.html`
      - `https://zipline.ml4trading.io/appendix.html`
    - QuantConnect:
      - `https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-types/market-orders`
      - `https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/security-identifiers`
    - vectorbt:
      - `https://vectorbt.dev/`
      - `https://vectorbt.dev/api/portfolio/base/`
    - NautilusTrader:
      - `https://nautilustrader.io/docs/latest/concepts/strategies/`
      - `https://nautilustrader.io/docs/latest/concepts/orders/`
      - `https://nautilustrader.io/docs/latest/api_reference/trading/`
    - Freqtrade:
      - `https://www.freqtrade.io/en/stable/strategy-customization/`
- Final disposition:
  - Complete for the comparison slice. Conclusion: other libraries are often
    fundamentally different; there is no universal inheritance structure to
    copy. The right design move is to choose the primary user mental model for
    `quantleet`, then let the public strategy DSL and the engine contracts
    diverge where necessary. The resulting design baseline is recorded in
    `docs/design-docs/unified-strategy-runtime-design.md`.
