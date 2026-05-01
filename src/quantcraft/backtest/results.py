from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from quantcraft.backtest.reporting import BacktestReport
from quantcraft.trading.domain.events import FillEvent, OrderRejectedEvent
from quantcraft.trading.domain.state import TradingState

if TYPE_CHECKING:
    from matplotlib.figure import Figure


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


@dataclass(frozen=True, slots=True, kw_only=True)
class _BacktestRunSnapshot:
    symbol: str
    timeframe: str
    bar_type: str
    timestamps: tuple[int, ...]
    closes: tuple[float, ...]


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
    order_events: tuple[OrderRejectedEvent, ...] = ()
    drawdown_curve: tuple[float, ...] = field(default=(), kw_only=True)
    _report: BacktestReport | None = field(
        default=None,
        compare=False,
        repr=False,
        kw_only=True,
    )
    _run_snapshot: _BacktestRunSnapshot | None = field(
        default=None,
        compare=False,
        repr=False,
        kw_only=True,
    )

    @property
    def report(self) -> BacktestReport:
        if self._report is None:
            raise ValueError("report is only available for engine-produced BacktestResult values")
        return self._report

    def plot(self) -> "Figure":
        from quantcraft.backtest.plotting import plot_backtest_result

        return plot_backtest_result(self)


__all__ = ["BacktestResult", "BacktestSummary", "ExposureSummary"]
