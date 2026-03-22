# Cross-Exchange Comparison Notebook Implementation Plan

## Steps

1. Add a new notebook

- create `notebooks/spot-cross-exchange-price-comparison.ipynb`
- keep the existing Binance validation notebook intact

2. Implement the notebook flow

- fetch Binance / Bybit / Bitget spot BTC/USDT 1h bars
- validate row presence and ordering
- build a shared timestamp index
- compute aligned close-price comparison
- print spread summary
- render a comparison chart

3. Execute the notebook

- use `nbclient` to run it from the command line
- persist executed outputs into the notebook

4. Verification

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy src`
- `uv build`
- notebook execution log

5. QA review

- request isolated QA review for the new notebook scope
- fix blocking issues until approval
