- Date: 2026-04-18
- Task: Research whether explicit `symbol=...` on `buy()`/`sell()` matches common quant-library practice
- Status: `complete`
- Risk class: `Tier B`
- Requestor: user
- Owner: Codex

## Planner Contract

- Goal:
  - Compare the current `quantleet` strategy order API against representative
    external quant and backtesting libraries, with emphasis on whether
    `buy()`/`sell()` require an explicit instrument symbol in the strategy
    callback and how single-asset versus multi-asset engines typically model
    that responsibility.
- Governing docs:
  - `AGENTS.md`
  - `README.md`
  - `ARCHITECTURE.md`
  - `docs/product-specs/research-ergonomics.md`
  - `docs/product-specs/backtest-mvp.md`
  - `docs/RELIABILITY.md`
  - `docs/SECURITY.md`
- Why these are governing:
  - They define the current public strategy surface, current MVP scope, and
    the repository workflow contract this research must follow.
- In-repo scope:
  - Current `quantleet` docs and source related to strategy order API.
- Out-of-repo scope:
  - Official documentation and authoritative examples for external libraries.
- Tier A progression requested: `no`
- Approval record, if required:
  - None. This is read-only API research.
- Verification commands:
  - targeted local `sed -n`, `nl -ba`, and `rg -n` reads
  - official web documentation lookups for representative external libraries
- Success criteria:
  - Report whether the current explicit-symbol requirement is common or unusual.
  - Distinguish single-asset and multi-asset API patterns.
  - Cite local repository evidence and external authoritative sources.
  - Give a concise conclusion about whether the current API likely feels odd to users.
- Out of scope:
  - Changing the API.

## Evaluator Acceptance Contract

- Evaluator owner:
  - Codex
- Evaluator-owned done contract for this slice:
  - The report must separate verified local facts from external comparison and
    avoid overgeneralizing one library's design choice as industry law.
- Acceptance artifact location:
  - `docs/plans/2026-04-18-order-api-symbol-research.md`
- How the generator and evaluator agreed on done before execution:
  - Done means local API inspection plus official-source comparison across
    multiple representative libraries.
- Checks the evaluator will use:
  - local doc/source inspection
  - official-doc comparisons from external libraries
- Auto-fail conditions:
  - claims about other libraries without authoritative sources
  - failure to distinguish single-asset and multi-asset cases

## Generator Work Log

- Planned slice order:
  - inspect current local strategy API and docs
  - research representative external libraries
  - synthesize comparison and user-facing judgment
- Notes:
  - Read-only research slice.
- Blockers or scope changes:
  - None so far.

## Evaluator Review

- Findings:
  - Local fact: the current `quantleet` research strategy contract explicitly
    requires `symbol=...` on `buy()` and `sell()`, and the concrete method
    signatures enforce that requirement.
  - Comparative result: this is unusual for single-asset strategy DSLs, but
    normal for multi-asset engines and execution platforms.
  - Official-source pattern split:
    - single-asset strategy libraries usually infer the instrument from the
      active data context or data passed into the backtest object
    - multi-asset engines usually require an `asset`, `data`, or `symbol`
      handle on each order, because the strategy is expected to trade across a
      universe rather than one implicit instrument
  - Representative external findings:
    - `backtesting.py` examples and API show `self.buy()` / `self.sell()`
      without symbol arguments for the common strategy flow.
    - `backtrader` uses `buy(data=None, ...)` and defaults `data=None` to
      `self.datas[0]`, so symbol selection is optional in the common case and
      only needed when trading non-default feeds.
    - `vectorbt` does not expose an imperative `buy(symbol=...)` strategy DSL
      at all in the common path; asset identity is carried by the price/signal
      arrays and their columns.
    - `Zipline` and `QuantConnect` require an explicit asset/symbol handle on
      orders because their API is built around broader multi-asset algorithm
      contexts.
  - User-facing judgment:
    - because `quantleet` currently documents itself as a deterministic
      single-symbol backtest MVP, requiring `symbol=...` on every `buy()` and
      `sell()` call will feel odd to many users coming from `backtesting.py`,
      `backtrader`, or vectorized signal frameworks
    - the current shape is easier to defend as future-facing API discipline
      than as present-day ergonomics
- Verification evidence:
  - Local evidence:
    - `docs/product-specs/research-ergonomics.md`
    - `src/quantleet/research/strategy.py`
  - External official docs reviewed:
    - backtesting.py docs and quickstart:
      - `https://kernc.github.io/backtesting.py/`
      - `https://kernc.github.io/backtesting.py/doc/examples/Quick%20Start%20User%20Guide.html`
    - backtrader strategy docs:
      - `https://www.backtrader.com/docu/strategy/`
    - vectorbt docs:
      - `https://vectorbt.dev/`
      - `https://vectorbt.dev/api/portfolio/base/`
    - QuantConnect docs:
      - `https://www.quantconnect.com/docs/v2/writing-algorithms/trading-and-orders/order-types/market-orders`
      - `https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/security-identifiers`
    - Zipline docs:
      - `https://zipline.ml4trading.io/`
      - `https://zipline.ml4trading.io/beginner-tutorial.html`
      - `https://zipline.ml4trading.io/appendix.html`
- Final disposition:
  - Complete. The current explicit-symbol requirement is locally verified and
    externally benchmarked against representative official docs. Conclusion:
    the API is defensible for future multi-asset expansion, but it is not the
    dominant ergonomic pattern for today's single-symbol strategy libraries.
