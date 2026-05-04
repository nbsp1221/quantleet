# Orders And Sizing

The first beta supports fixed quantity and percentage sizing in the
single-symbol historical backtest workflow.

```python
class OrdersAndSizingStrategy(Strategy):
    def on_bar(self, bar) -> None:
        if len(self.data.close) == 1:
            self.buy(quantity=1.0, tag="fixed-market")
            self.buy(qty_percent=10.0, order_type="limit", limit_price=99.0, tag="limit")
        elif len(self.data.close) == 2 and self.position.is_open:
            self.sell(
                qty_percent=50.0,
                order_type="stop_market",
                stop_price=95.0,
                tag="stop-market",
            )
        elif len(self.data.close) == 3 and self.position.is_open:
            self.sell(
                qty_percent=100.0,
                order_type="stop_limit",
                stop_price=94.0,
                limit_price=94.0,
                tag="stop-limit",
            )
```

Supported order families:

- `market`
- `limit`
- `stop_market`
- `stop_limit`

Use `result.trade_log`, `result.report.fills`, `result.order_events`, and
`result.final_state.position_quantity` to inspect fills, order events,
reservations, and positions.

The current beta is long-or-flat. A sell while flat is treated as an exit-only
no-op, not as a short entry.
