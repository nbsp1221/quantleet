from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

from quantcraft.trading.domain.events import FillEvent

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from quantcraft.backtest.results import BacktestResult

PRICE_COLOR = "#334155"
EQUITY_COLOR = "#2563eb"
DRAWDOWN_COLOR = "#dc2626"
DRAWDOWN_FILL_ALPHA = 0.16
DRAWDOWN_ZERO_COLOR = "#6b7280"
BUY_COLOR = "#16a34a"
SELL_COLOR = "#dc2626"
MARKER_EDGE_COLOR = "#ffffff"
FILL_MARKER_SIZE = 56
FILL_MARKER_LINEWIDTH = 0.8


def plot_backtest_result(result: "BacktestResult") -> "Figure":
    from matplotlib import dates as mdates
    from matplotlib import pyplot as plt
    from matplotlib import ticker

    snapshot = result._run_snapshot
    if snapshot is None:
        raise ValueError("run snapshot is required to plot BacktestResult")

    _validate_plot_lengths(
        timestamps=snapshot.timestamps,
        closes=snapshot.closes,
        equity_curve=result.equity_curve,
        drawdown_curve=result.drawdown_curve,
    )
    x_values = _utc_date_numbers(snapshot.timestamps)
    drawdown_values = tuple(-value for value in result.drawdown_curve)

    figure, axes = plt.subplots(
        3,
        1,
        figsize=(12, 8),
        sharex=True,
        gridspec_kw={"height_ratios": (3, 2, 1)},
    )
    price_axis, equity_axis, drawdown_axis = axes

    price_axis.plot(x_values, snapshot.closes, label="Close", color=PRICE_COLOR)
    _plot_fill_markers(price_axis, result.trade_log)
    equity_axis.plot(x_values, result.equity_curve, label="Equity", color=EQUITY_COLOR)
    drawdown_axis.plot(x_values, drawdown_values, label="Drawdown", color=DRAWDOWN_COLOR)
    drawdown_axis.fill_between(
        x_values,
        drawdown_values,
        0.0,
        color=DRAWDOWN_COLOR,
        alpha=DRAWDOWN_FILL_ALPHA,
    )
    drawdown_axis.axhline(0.0, color=DRAWDOWN_ZERO_COLOR, linewidth=1.0)
    drawdown_axis.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))

    figure.suptitle(f"{snapshot.symbol} {snapshot.timeframe} Backtest")
    price_axis.set_ylabel("Price")
    equity_axis.set_ylabel("Equity")
    drawdown_axis.set_ylabel("Drawdown (%)")
    drawdown_axis.set_xlabel("Time (UTC)")
    date_formatter = cast(Any, mdates.DateFormatter)("%Y-%m-%d %H:%M", tz=UTC)
    price_axis.xaxis.set_major_formatter(date_formatter)

    for axis in axes:
        axis.grid(True, alpha=0.25)
        axis.legend()

    figure.tight_layout()
    return figure


def _validate_plot_lengths(
    *,
    timestamps: tuple[int, ...],
    closes: tuple[float, ...],
    equity_curve: tuple[float, ...],
    drawdown_curve: tuple[float, ...],
) -> None:
    if not timestamps:
        raise ValueError("run snapshot contains empty run data")

    lengths = {
        "timestamps": len(timestamps),
        "closes": len(closes),
        "equity_curve": len(equity_curve),
        "drawdown_curve": len(drawdown_curve),
    }
    if len(set(lengths.values())) == 1:
        return

    joined = ", ".join(f"{name}={length}" for name, length in lengths.items())
    raise ValueError(f"plot series length mismatch: {joined}")


def _plot_fill_markers(axis: "Axes", trade_log: tuple[FillEvent, ...]) -> None:
    buys = tuple(fill for fill in trade_log if fill.side == "buy")
    sells = tuple(fill for fill in trade_log if fill.side == "sell")
    _plot_side_markers(axis, fills=buys, label="Buy", marker="^", color=BUY_COLOR)
    _plot_side_markers(axis, fills=sells, label="Sell", marker="v", color=SELL_COLOR)


def _plot_side_markers(
    axis: "Axes",
    *,
    fills: tuple[FillEvent, ...],
    label: str,
    marker: str,
    color: str,
) -> None:
    if not fills:
        return
    axis.scatter(
        _utc_date_numbers(tuple(fill.timestamp for fill in fills)),
        tuple(fill.price for fill in fills),
        label=label,
        marker=marker,
        s=FILL_MARKER_SIZE,
        color=color,
        edgecolors=MARKER_EDGE_COLOR,
        linewidths=FILL_MARKER_LINEWIDTH,
        zorder=3,
    )


def _utc_datetimes(timestamps: tuple[int, ...]) -> tuple[datetime, ...]:
    return tuple(datetime.fromtimestamp(timestamp / 1000, tz=UTC) for timestamp in timestamps)


def _utc_date_numbers(timestamps: tuple[int, ...]) -> tuple[float, ...]:
    from matplotlib import dates as mdates

    date2num = cast(Any, mdates.date2num)
    return tuple(float(value) for value in date2num(_utc_datetimes(timestamps)))


__all__: tuple[str, ...] = ()
