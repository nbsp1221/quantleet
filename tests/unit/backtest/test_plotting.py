from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

import matplotlib
import pytest

matplotlib.use("Agg")

from matplotlib import colors as mcolors
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.markers import MarkerStyle

from quantcraft.backtest import BacktestResult, BacktestSummary, ExposureSummary
from quantcraft.backtest.analytics import drawdown_curve_for_equity
from quantcraft.backtest.results import _BacktestRunSnapshot
from quantcraft.trading.domain.events import FillEvent
from quantcraft.trading.domain.state import TradingState


@pytest.fixture(autouse=True)
def close_figures() -> Iterable[None]:
    yield
    plt.close("all")


def _summary() -> BacktestSummary:
    return BacktestSummary(
        total_trades=1,
        total_fills=2,
        total_fees=0.0,
        final_balance=1_002.0,
        final_equity=1_002.0,
        total_return=0.002,
        max_drawdown=0.05,
        realized_pnl=2.0,
        unrealized_pnl=0.0,
        win_rate=1.0,
        average_win=2.0,
        average_loss=0.0,
        profit_factor=float("inf"),
        exposure=ExposureSummary(
            bars_in_position=2,
            total_bars=3,
            exposure_ratio=2 / 3,
        ),
    )


def _result(
    *,
    timestamps: tuple[int, ...] = (0, 60_000, 120_000),
    closes: tuple[float, ...] = (100.0, 90.0, 110.0),
    equity_curve: tuple[float, ...] = (1_000.0, 950.0, 1_002.0),
    drawdown_curve: tuple[float, ...] = (0.0, 0.05, 0.0),
    trade_log: tuple[FillEvent, ...] | None = None,
) -> BacktestResult:
    if trade_log is None:
        trade_log = (
            FillEvent(
                symbol="BTC/USDT",
                side="buy",
                quantity=1.0,
                price=90.0,
                timestamp=60_000,
                fee=0.0,
            ),
            FillEvent(
                symbol="BTC/USDT",
                side="sell",
                quantity=1.0,
                price=110.0,
                timestamp=120_000,
                fee=0.0,
            ),
        )
    return BacktestResult(
        trade_log=trade_log,
        equity_curve=equity_curve,
        final_state=TradingState(cash=1_002.0, equity=1_002.0),
        summary=_summary(),
        drawdown_curve=drawdown_curve,
        _run_snapshot=_BacktestRunSnapshot(
            symbol="BTC/USDT",
            timeframe="1m",
            bar_type="time",
            timestamps=timestamps,
            closes=closes,
        ),
    )


@pytest.mark.parametrize(
    ("equity", "expected"),
    [
        ((100.0, 100.0, 100.0), (0.0, 0.0, 0.0)),
        ((100.0, 110.0, 120.0), (0.0, 0.0, 0.0)),
        ((100.0, 90.0, 95.0), (0.0, 0.1, 0.05)),
        ((100.0, 90.0, 120.0, 108.0), (0.0, 0.1, 0.0, 0.1)),
        ((0.0, -5.0, -1.0), (0.0, 0.0, 0.0)),
        ((100.0, -20.0), (0.0, 1.2)),
    ],
)
def test_drawdown_curve_uses_positive_loss_fraction(
    equity: tuple[float, ...],
    expected: tuple[float, ...],
) -> None:
    assert drawdown_curve_for_equity(equity) == expected


def test_plot_returns_three_axis_figure_with_expected_contract() -> None:
    result = _result()

    fig = result.plot()

    assert isinstance(fig, Figure)
    assert tuple(fig.get_size_inches()) == pytest.approx((12.0, 8.0))
    assert len(fig.axes) == 3
    price_ax, equity_ax, drawdown_ax = fig.axes
    assert fig._suptitle is not None
    assert fig._suptitle.get_text() == "BTC/USDT 1m Backtest"
    assert price_ax.get_ylabel() == "Price"
    assert equity_ax.get_ylabel() == "Equity"
    assert drawdown_ax.get_ylabel() == "Drawdown (%)"
    assert drawdown_ax.get_xlabel() == "Time (UTC)"
    assert price_ax.get_shared_x_axes().joined(price_ax, equity_ax)
    assert price_ax.get_shared_x_axes().joined(price_ax, drawdown_ax)
    heights = [axis.get_position().height for axis in fig.axes]
    assert heights[0] > heights[1] > heights[2]

    legend_text = {
        text.get_text()
        for axis in fig.axes
        for text in (axis.get_legend().get_texts() if axis.get_legend() else ())
    }
    assert {"Close", "Buy", "Sell", "Equity", "Drawdown"} <= legend_text
    assert _grid_is_enabled(price_ax)
    assert _grid_is_enabled(equity_ax)
    assert _grid_is_enabled(drawdown_ax)

    expected_x = tuple(mdates.date2num(_dt(timestamp)) for timestamp in (0, 60_000, 120_000))
    assert tuple(price_ax.lines[0].get_xdata()) == expected_x
    assert tuple(equity_ax.lines[0].get_xdata()) == expected_x
    assert tuple(drawdown_ax.lines[0].get_xdata()) == expected_x
    assert tuple(price_ax.lines[0].get_ydata()) == (100.0, 90.0, 110.0)
    assert tuple(equity_ax.lines[0].get_ydata()) == (1_000.0, 950.0, 1_002.0)
    assert tuple(drawdown_ax.lines[0].get_ydata()) == (0.0, -0.05, 0.0)
    assert mcolors.same_color(price_ax.lines[0].get_color(), "#334155")
    assert mcolors.same_color(equity_ax.lines[0].get_color(), "#2563eb")
    assert mcolors.same_color(drawdown_ax.lines[0].get_color(), "#dc2626")
    assert any(tuple(line.get_ydata()) == (0.0, 0.0) for line in drawdown_ax.lines[1:])
    assert any(mcolors.same_color(line.get_color(), "#6b7280") for line in drawdown_ax.lines[1:])
    assert _collection_facecolor(drawdown_ax.collections[0]) == pytest.approx(
        mcolors.to_rgba("#dc2626", alpha=0.16)
    )
    assert _scatter_points(price_ax, "Buy") == ((mdates.date2num(_dt(60_000)), 90.0),)
    assert _scatter_points(price_ax, "Sell") == ((mdates.date2num(_dt(120_000)), 110.0),)
    assert _collection_facecolor(_scatter_collection(price_ax, "Buy")) == pytest.approx(
        mcolors.to_rgba("#16a34a")
    )
    assert _collection_facecolor(_scatter_collection(price_ax, "Sell")) == pytest.approx(
        mcolors.to_rgba("#dc2626")
    )
    assert _collection_edgecolor(_scatter_collection(price_ax, "Buy")) == pytest.approx(
        mcolors.to_rgba("#ffffff")
    )
    assert _collection_edgecolor(_scatter_collection(price_ax, "Sell")) == pytest.approx(
        mcolors.to_rgba("#ffffff")
    )
    assert _collection_size(_scatter_collection(price_ax, "Buy")) == 56.0
    assert _collection_size(_scatter_collection(price_ax, "Sell")) == 56.0
    assert _collection_linewidth(_scatter_collection(price_ax, "Buy")) == 0.8
    assert _collection_linewidth(_scatter_collection(price_ax, "Sell")) == 0.8
    assert _collection_marker_vertices(_scatter_collection(price_ax, "Buy")) == _marker_vertices(
        "^"
    )
    assert _collection_marker_vertices(_scatter_collection(price_ax, "Sell")) == _marker_vertices(
        "v"
    )


def test_no_fill_result_omits_buy_and_sell_marker_series() -> None:
    fig = _result(trade_log=()).plot()

    price_ax, equity_ax, drawdown_ax = fig.axes
    legend_text = {
        text.get_text()
        for axis in fig.axes
        for text in (axis.get_legend().get_texts() if axis.get_legend() else ())
    }
    assert {"Close", "Equity", "Drawdown"} <= legend_text
    assert "Buy" not in legend_text
    assert "Sell" not in legend_text
    assert len(price_ax.collections) == 0
    assert equity_ax
    assert drawdown_ax


def test_no_drawdown_result_plots_visible_zero_panel() -> None:
    fig = _result(
        closes=(100.0, 110.0, 120.0),
        equity_curve=(1_000.0, 1_010.0, 1_020.0),
        drawdown_curve=(0.0, 0.0, 0.0),
        trade_log=(),
    ).plot()

    drawdown_ax = fig.axes[2]
    assert tuple(drawdown_ax.lines[0].get_ydata()) == (0.0, 0.0, 0.0)
    assert any(tuple(line.get_ydata()) == (0.0, 0.0) for line in drawdown_ax.lines[1:])
    assert drawdown_ax.get_legend() is not None


@pytest.mark.parametrize(
    ("timestamps", "closes", "equity_curve", "drawdown_curve", "expected"),
    [
        (
            (0, 60_000),
            (100.0, 90.0),
            (1_000.0, 950.0, 1_002.0),
            (0.0, 0.05, 0.0),
            "timestamps=2.*equity_curve=3.*drawdown_curve=3",
        ),
        (
            (0, 60_000, 120_000),
            (100.0, 90.0, 110.0),
            (1_000.0, 950.0),
            (0.0, 0.05, 0.0),
            "timestamps=3.*equity_curve=2.*drawdown_curve=3",
        ),
        (
            (0, 60_000, 120_000),
            (100.0, 90.0, 110.0),
            (1_000.0, 950.0, 1_002.0),
            (0.0, 0.05),
            "timestamps=3.*equity_curve=3.*drawdown_curve=2",
        ),
    ],
)
def test_plot_validates_mismatched_series_lengths(
    timestamps: tuple[int, ...],
    closes: tuple[float, ...],
    equity_curve: tuple[float, ...],
    drawdown_curve: tuple[float, ...],
    expected: str,
) -> None:
    result = _result(
        timestamps=timestamps,
        closes=closes,
        equity_curve=equity_curve,
        drawdown_curve=drawdown_curve,
    )

    with pytest.raises(ValueError, match=expected):
        result.plot()


def test_plot_validates_empty_run_data() -> None:
    result = _result(timestamps=(), closes=(), equity_curve=(), drawdown_curve=())

    with pytest.raises(ValueError, match="empty run data"):
        result.plot()


def test_plot_accepts_single_bar_result() -> None:
    fig = _result(
        timestamps=(60_000,),
        closes=(100.0,),
        equity_curve=(1_000.0,),
        drawdown_curve=(0.0,),
        trade_log=(),
    ).plot()

    assert len(fig.axes) == 3
    assert len(fig.axes[0].lines[0].get_xdata()) == 1
    assert tuple(fig.axes[2].lines[0].get_ydata()) == (0.0,)


def test_plot_does_not_show_save_close_or_mutate(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _result()
    before = (
        result.trade_log,
        result.equity_curve,
        result.drawdown_curve,
        result.summary,
    )
    calls: list[str] = []

    monkeypatch.setattr(plt, "show", lambda *_, **__: calls.append("show"))
    monkeypatch.setattr(plt, "close", lambda *_, **__: calls.append("close"))
    monkeypatch.setattr(Figure, "savefig", lambda *_, **__: calls.append("savefig"))

    first = result.plot()
    second = result.plot()

    assert isinstance(first, Figure)
    assert isinstance(second, Figure)
    assert calls == []
    assert (
        result.trade_log,
        result.equity_curve,
        result.drawdown_curve,
        result.summary,
    ) == before


def _dt(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp / 1000, tz=UTC)


def _grid_is_enabled(axis) -> bool:
    return any(line.get_visible() for line in axis.get_xgridlines() + axis.get_ygridlines())


def _scatter_points(axis, label: str) -> tuple[tuple[float, float], ...]:
    collection = _scatter_collection(axis, label)
    if collection is None:
        return ()
    return tuple((float(x), float(y)) for x, y in collection.get_offsets())


def _scatter_collection(axis, label: str):
    for collection in axis.collections:
        if collection.get_label() == label:
            return collection
    return None


def _collection_facecolor(collection) -> tuple[float, float, float, float]:
    return tuple(float(value) for value in collection.get_facecolors()[0])


def _collection_edgecolor(collection) -> tuple[float, float, float, float]:
    return tuple(float(value) for value in collection.get_edgecolors()[0])


def _collection_size(collection) -> float:
    return float(collection.get_sizes()[0])


def _collection_linewidth(collection) -> float:
    return float(collection.get_linewidths()[0])


def _collection_marker_vertices(collection) -> tuple[tuple[float, float], ...]:
    vertices = collection.get_paths()[0].vertices
    return tuple(tuple(float(coord) for coord in point) for point in vertices)


def _marker_vertices(marker: str) -> tuple[tuple[float, float], ...]:
    marker_style = MarkerStyle(marker)
    path = marker_style.get_path().transformed(marker_style.get_transform())
    return tuple(tuple(float(coord) for coord in point) for point in path.vertices)
