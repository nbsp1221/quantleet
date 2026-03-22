# Cross-Exchange Comparison Notebook Design

## Goal

Add a practical notebook that uses the current public API to compare spot BTC/USDT prices across multiple overseas exchanges.

The notebook should answer a real usage question:

- can an external developer fetch the same market from multiple exchanges through the same `Exchange` API?
- does that produce useful insight such as observable cross-exchange price spreads?

## Scope

Included:

- one new notebook
- exchanges:
  - Binance spot
  - Bybit spot
  - Bitget spot
- symbol:
  - `BTC/USDT`
- timeframe:
  - `1h`
- a small practical comparison:
  - fetch
  - validate
  - align on common timestamps
  - plot close prices
  - compute simple spread statistics

Excluded:

- cache
- retries
- multiple symbols
- derivatives comparison
- production reporting

## Notebook Shape

The notebook will:

1. import the public API:
   - `Exchange`
   - `MarketType`
2. fetch 200 one-hour bars from each exchange
3. assert:
   - non-empty rows
   - strictly ascending timestamps
4. align rows by shared timestamps
5. plot close prices on one chart
6. compute simple spread metrics versus Binance:
   - latest spread
   - mean absolute spread
   - max absolute spread

## Success Criteria

This notebook is successful when:

- it executes end to end through `nbclient`
- all three exchanges return data
- aligned timestamps exist
- the spread table is printed
- the chart renders in stored notebook output
- existing gates still pass
