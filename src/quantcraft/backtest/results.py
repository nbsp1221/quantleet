from __future__ import annotations

from dataclasses import dataclass, field

from quantcraft.trading.domain.events import FillEvent
from quantcraft.trading.domain.state import TradingState


@dataclass(frozen=True, slots=True)
class ExposureSummary:
    bars_in_position: int
    total_bars: int
    exposure_ratio: float


@dataclass(frozen=True, slots=True)
class BacktestSummary:
    total_trades: int
    total_fills: int
    total_fees: float
    final_balance: float
    final_equity: float
    total_return: float
    max_drawdown: float
    realized_pnl: float
    unrealized_pnl: float
    win_rate: float
    average_win: float
    average_loss: float
    profit_factor: float
    exposure: ExposureSummary

    @property
    def trade_count(self) -> int:
        return self.total_trades

    @property
    def ending_equity(self) -> float:
        return self.final_equity


@dataclass(frozen=True, slots=True)
class BacktestResult:
    trade_log: tuple[FillEvent, ...]
    equity_curve: tuple[float, ...]
    final_state: TradingState
    summary: BacktestSummary
    execution_model_name: str = field(
        default="conservative_ohlcv",
        compare=False,
        repr=False,
    )


__all__ = ["BacktestResult", "BacktestSummary", "ExposureSummary"]
