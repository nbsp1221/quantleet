# Binance Notebook Validation Design

**Goal:** Validate that an external developer can use the current `quantcraft` package from a Jupyter notebook to fetch Binance spot and USD-M OHLCV data and plot simple charts.

**Scope:**
- One notebook only.
- Binance only.
- `BTC/USDT`, `1h`, `limit=200`.
- Spot and USD-M futures.
- Simple chart output using `matplotlib`.

**Why this scope:**
- It validates the current public API without adding new abstraction.
- It exercises both supported Binance market modes.
- It keeps the notebook short and debuggable.

**Dependencies:**
- `matplotlib` for plotting.
- `nbformat` and `nbclient` for execution validation.

**Output expectations:**
- Both fetches return non-empty rows.
- The notebook renders two line charts from close prices.
- The notebook prints row counts and timestamp ranges for both markets.
