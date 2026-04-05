from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from quantcraft.data import BarSeries, DataFrameDataSource
from quantcraft.research import BacktestEngine, Strategy, qc, ta
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import FillEvent

CANONICAL_BACKTEST_FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "backtest" / "binance_usdm_btcusdtusdt_1h_2025.csv"
)
CANONICAL_BACKTEST_EXPECTED_COLUMNS = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
)
CANONICAL_BACKTEST_EXPECTED_ROWS = 8_760


class CanonicalRsi3070Strategy(Strategy):
    def init(self) -> None:
        self.rsi = ta.rsi(self.data.close, length=14)

    def on_bar(self, bar) -> None:
        if qc.is_na(self.rsi[0]):
            return
        if (not self.position.is_open) and self.rsi[0] < 30:
            self.buy(symbol=bar.symbol, quantity=1.0)
        elif self.position.is_open and self.rsi[0] > 70:
            self.sell(symbol=bar.symbol, quantity=1.0)


def load_canonical_rsi_bars() -> BarSeries:
    with CANONICAL_BACKTEST_FIXTURE_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == CANONICAL_BACKTEST_EXPECTED_COLUMNS
        rows = list(reader)

    assert len(rows) == CANONICAL_BACKTEST_EXPECTED_ROWS
    assert rows[0]["timestamp"] == "2025-01-01T00:00:00+00:00"
    assert rows[-1]["timestamp"] == "2025-12-31T23:00:00+00:00"
    assert rows == sorted(rows, key=lambda row: str(row["timestamp"]))

    return DataFrameDataSource(
        frame=rows,
        symbol="BTC/USDT:USDT",
        timeframe="1h",
    ).load()


def run_canonical_rsi_backtest(bars: BarSeries):
    engine = BacktestEngine(
        initial_cash=1_000_000.0,
        costs=CostConfig(tick_size=0.1, slippage_ticks=1.0, fee_rate=0.0004),
    )
    return engine.run(bars=bars, strategy=CanonicalRsi3070Strategy())


def canonical_rsi_trade_log_samples(
    trade_log: tuple[FillEvent, ...],
) -> tuple[tuple[dict[str, float | int | str], ...], tuple[dict[str, float | int | str], ...]]:
    return (
        tuple(_normalize_fill(fill) for fill in trade_log[:5]),
        tuple(_normalize_fill(fill) for fill in trade_log[-5:]),
    )


def canonical_rsi_trade_log_digest(trade_log: tuple[FillEvent, ...]) -> str:
    payload = json.dumps(
        [_normalize_fill(fill) for fill in trade_log],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _normalize_fill(fill: FillEvent) -> dict[str, float | int | str]:
    return {
        "timestamp": fill.timestamp,
        "side": fill.side,
        "quantity": round(fill.quantity, 12),
        "price": round(fill.price, 12),
        "fee": round(fill.fee, 12),
    }
