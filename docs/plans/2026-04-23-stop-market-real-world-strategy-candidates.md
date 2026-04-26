# Stop-Market Real-World Validation Strategy Candidates

This note records three realistic strategy patterns that can be expressed with
the **currently shipped** standalone `stop_market` slice.

The goal is not to prove alpha. The goal is to validate that the shared kernel
behaves credibly when strategy authors use stop orders that are already within
the current product scope.

## Current Shipped Constraints

These candidates are limited by the current shipped scope:

- supported order types:
  - `market`
  - `limit`
  - `stop_market`
- `sell()` is an exit operation in the current long-only slice, not short entry
- `sell()` while flat is treated as a no-op
- `qty_percent + stop_market` is still deferred
- `stop_limit` is not shipped
- trailing stops are not shipped
- true OTO, OCO, and bracket lifecycle semantics are not shipped as first-class
  order primitives
- order intake happens from `on_bar()` against the active closed bar

Because of that, the current validation candidates must use standalone
`stop_market` orders. Strategies that need a stop-loss or take-profit order to
be attached to a parent entry fill are **future attached-order validation work**,
not current `stop_market` validation candidates.

## Selection Rule

A candidate is valid for the current validation set only if it can be expressed
without parent-child order lifecycle semantics.

Allowed:

- place a standalone `buy(order_type="stop_market", stop_price=...)` from
  `on_bar()`
- exit later with an independent market-like `sell(quantity=...)` signal
- ignore stale entry stop orders by relying on current single-position
  long-only semantics and flat `sell()` no-op behavior where applicable

Not allowed for this validation set:

- entry order with attached stop-loss or take-profit
- entry fill event that immediately activates child orders
- bracket order behavior
- OTO or OCO cancellation relationships
- protective stops computed before entry and submitted only after a delayed
  parent fill

## Candidate 1: Opening Range Breakout Stop Entry

### Pattern

- define a fixed opening range, such as the first `N` bars of a UTC session or
  the first `N` bars after a configured market open
- when the range is complete, place a standalone
  `buy(order_type="stop_market", stop_price=range_high + buffer)`
- if the stop entry is filled, exit later with an independent signal such as:
  - end-of-session market exit
  - close back below the range midpoint
  - close below a short moving average

### Why it is realistic

Opening range breakout strategies commonly place a buy stop just above the
opening range high and let the market trigger the entry. This is a direct
real-world use of a stop order as an entry order.

### Why it is possible today

This pattern only requires:

- a standalone `buy stop_market` entry
- a later independent market-style exit

It does not require linked child orders.

### Why it is a good validation candidate

This candidate tests:

- stop entry activation above a known range boundary
- gap-through entry behavior
- intrabar stop-entry crossing
- ordinary non-linked exit after a stop entry

## Candidate 2: Donchian / Turtle-Style Breakout Stop Entry

### Pattern

- compute a rolling breakout level such as the prior 20-bar high
- place a standalone
  `buy(order_type="stop_market", stop_price=prior_high + buffer)`
- if filled, exit later with an independent signal such as:
  - close below a shorter Donchian low
  - close below a moving average
  - time-based market exit after a fixed holding window

### Why it is realistic

Turtle-style breakout systems enter when price exceeds a prior channel high.
The core entry idea is specifically designed to avoid waiting for bar close
confirmation after the breakout has already happened.

### Why it is possible today

The entry is a standalone stop-market order submitted from `on_bar()` after the
breakout level is known. The exit is deliberately modeled as an independent
market signal for this validation candidate, because attached stop-loss and
position-scale risk management are outside the current shipped scope.

### Why it is a good validation candidate

This candidate tests:

- long-lived stop entry orders
- repeated channel-breakout opportunities
- stop crossing across rolling technical levels
- cancellation-free behavior when only one position is allowed

## Candidate 3: Inside-Bar Breakout Stop Entry

### Pattern

- detect an inside bar, where the latest closed bar's high and low are inside
  the previous bar's range
- place a standalone
  `buy(order_type="stop_market", stop_price=mother_bar_high + buffer)`
- if filled, exit later with an independent failure or time signal such as:
  - close back inside the mother bar range
  - close below the inside bar low
  - fixed-bar holding period exit

### Why it is realistic

Inside-bar breakout strategies commonly use buy stop or sell stop orders around
the pattern range so that entry occurs only if price expands out of the
consolidation.

### Why it is possible today

The current long-only slice can validate the bullish side:

- detect inside-bar compression on a closed bar
- submit a standalone `buy stop_market` above the pattern
- exit later with an independent market-style signal

No OTO, OCO, bracket, or attached protective stop is required.

### Why it is a good validation candidate

This candidate tests:

- stop entry after a compression pattern
- stop triggers near recent high/low structure
- invalidation through independent signal exits
- repeated standalone stop entries across a volatile dataset

## Deferred Candidates

The following patterns are realistic but are not current validation candidates:

- limit entry with attached ATR stop-loss
- market entry with immediate protective stop-loss
- entry order with simultaneous take-profit and stop-loss
- bracket-style TP/SL management

These require parent-fill child activation and likely OTO/OCO semantics. They
should be revisited after the order lifecycle supports attached orders.

## External Research Notes

The replacement candidates are grounded in common stop-entry patterns:

- Opening range breakout guides commonly describe placing a buy stop above the
  opening range high.
  Reference: `https://www.tradapt.com/resources/strategies/opening-range-breakout`
- Original Turtle-style systems use channel breakout entries, with long entry
  triggered when price exceeds a prior high.
  Reference: `https://www.tradingblox.com/originalturtles/originalturtlerules.pdf`
- Inside-bar breakout guides commonly describe buy stop entries above the
  mother bar or pattern high.
  Reference:
  `https://priceaction.com/price-action-university/strategies/inside-bar/`

## Recommendation

All three candidates are feasible today and can be used to validate the shipped
standalone `stop_market` slice.

If only one is added first, prefer **Candidate 2**:

- it is simple to express on the existing BTC/USDT 1h dataset
- it directly stresses long-lived stop-entry behavior
- it does not require session-specific market-open logic

If multiple are added, the best progression is:

1. Candidate 2
2. Candidate 3
3. Candidate 1

That sequence moves from the simplest rolling breakout entry, to pattern-based
breakout entry, to session/range-based breakout entry.
