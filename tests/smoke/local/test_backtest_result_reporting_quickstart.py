from __future__ import annotations

from quantleet.backtest import BacktestEngine, CostConfig
from quantleet.data import DataFrameDataSource
from quantleet.research import Strategy


class QuickstartStrategy(Strategy):
    def on_bar(self, bar) -> None:
        if len(self.data.close) == 1:
            self.buy(quantity=1.0, tag="entry")
        elif self.position.is_open:
            self.sell(quantity=1.0, tag="exit")


def test_dataframe_quickstart_produces_direct_result_report() -> None:
    source = DataFrameDataSource(
        frame=[
            {
                "timestamp": "1970-01-01T00:01:00+00:00",
                "open": 100.0,
                "high": 100.0,
                "low": 100.0,
                "close": 100.0,
                "volume": 1.0,
            },
            {
                "timestamp": "1970-01-01T00:02:00+00:00",
                "open": 101.0,
                "high": 101.0,
                "low": 101.0,
                "close": 101.0,
                "volume": 1.0,
            },
            {
                "timestamp": "1970-01-01T00:03:00+00:00",
                "open": 102.0,
                "high": 102.0,
                "low": 102.0,
                "close": 102.0,
                "volume": 1.0,
            },
        ],
        symbol="BTC/USDT",
        timeframe="1m",
    )
    result = BacktestEngine(
        initial_cash=1_000.0,
        costs=CostConfig(tick_size=1.0, slippage_ticks=0.0, fee_rate=0.0),
    ).run(source=source, strategy=QuickstartStrategy(), label="quickstart")

    assert result.report.run.run_label == "quickstart"
    assert result.report.run.symbol == "BTC/USDT"
    assert "Return" in str(result.report)
    assert "Execution Assumptions" in str(result.report)
