from __future__ import annotations

import math
import re
from dataclasses import dataclass
from statistics import mean, median, stdev
from typing import Any

from quantcraft.backtest.analytics import drawdown_for_equity, max_drawdown_from_curve
from quantcraft.data import BarSeries
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import FillEvent, OrderRejectedEvent
from quantcraft.trading.domain.orders import Order
from quantcraft.trading.domain.state import TradingState

_SECONDS_PER_YEAR = 365.2425 * 24 * 60 * 60
_TIMEFRAME_RE = re.compile(r"^(?P<count>\d+)(?P<unit>ms|s|m|h|d|w)$")
_TIMEFRAME_SECONDS = {
    "ms": 0.001,
    "s": 1.0,
    "m": 60.0,
    "h": 60.0 * 60.0,
    "d": 24.0 * 60.0 * 60.0,
    "w": 7.0 * 24.0 * 60.0 * 60.0,
}


@dataclass(frozen=True, slots=True)
class RunManifest:
    symbol: str
    timeframe: str
    start_timestamp: int
    end_timestamp: int
    bar_count: int
    initial_cash: float
    execution_model_name: str
    strategy_class_name: str
    strategy_display_name: str | None
    strategy_parameters: dict[str, object]
    run_label: str | None


@dataclass(frozen=True, slots=True)
class ExecutionAssumptions:
    execution_model_name: str
    order_activation_timing: str
    fill_price_basis: str
    open_position_finalization: str
    tick_size: float
    slippage_ticks: float
    fee_rate: float
    order_rejection_count: int
    annual_risk_free_rate: float
    periods_per_year: float | None


@dataclass(frozen=True, slots=True)
class EquityPoint:
    bar_index: int
    timestamp: int
    equity: float
    cash: float
    position_quantity: float
    mark_price: float
    drawdown: float


@dataclass(frozen=True, slots=True)
class ReportingFill:
    order_id: int
    order_type: str
    tag: str | None
    timestamp: int
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float


@dataclass(frozen=True, slots=True)
class ClosedTrade:
    entry_timestamp: int
    exit_timestamp: int
    entry_bar_index: int
    exit_bar_index: int
    duration_bars: int
    quantity: float
    entry_price: float
    exit_price: float
    gross_pnl: float
    net_pnl: float
    allocated_entry_fee: float
    exit_fee: float
    total_fees: float
    net_return: float | None
    entry_tag: str | None
    entry_tags: tuple[str, ...]
    exit_tag: str | None


@dataclass(frozen=True, slots=True)
class ReturnMetrics:
    final_equity: float
    equity_peak: float
    total_return: float
    buy_and_hold_return: float | None
    active_return: float | None
    annualized_return: float | None
    final_cash: float
    gross_realized_pnl: float
    net_realized_pnl: float
    unrealized_pnl: float


@dataclass(frozen=True, slots=True)
class RiskMetrics:
    max_drawdown: float
    longest_drawdown_bar_count: int
    volatility: float | None
    sharpe_ratio: float | None
    annual_risk_free_rate: float
    periods_per_year: float | None


@dataclass(frozen=True, slots=True)
class TradeMetrics:
    closed_trade_count: int
    fill_count: int
    win_rate: float | None
    best_trade: float | None
    worst_trade: float | None
    average_win: float | None
    average_loss: float | None
    profit_factor: float | None
    average_trade_return: float | None
    expectancy_return: float | None


@dataclass(frozen=True, slots=True)
class CostMetrics:
    total_fees: float
    fees_as_initial_cash: float
    closed_trade_fees: float
    gross_realized_pnl: float
    net_realized_pnl: float
    fees_to_gross_pnl_ratio: float | None


@dataclass(frozen=True, slots=True)
class ExposureMetrics:
    bars_in_position: int
    total_bars: int
    exposure_ratio: float
    ending_state: str
    final_position_quantity: float
    final_average_entry_price: float | None


@dataclass(frozen=True, slots=True)
class BacktestReport:
    run: RunManifest
    execution: ExecutionAssumptions
    returns: ReturnMetrics
    risk: RiskMetrics
    trades: TradeMetrics
    costs: CostMetrics
    exposure: ExposureMetrics
    equity: tuple[EquityPoint, ...]
    fills: tuple[ReportingFill, ...]
    closed_trades: tuple[ClosedTrade, ...]
    order_rejections: tuple[OrderRejectedEvent, ...]

    def to_text(self) -> str:
        return "\n".join(
            (
                "Return",
                f"  final equity: {_format_value(self.returns.final_equity)}",
                f"  total return: {_format_ratio(self.returns.total_return)}",
                f"  buy and hold: {_format_ratio(self.returns.buy_and_hold_return)}",
                f"  active return: {_format_ratio(self.returns.active_return)}",
                "Risk",
                f"  max drawdown: {_format_ratio(self.risk.max_drawdown)}",
                f"  volatility: {_format_ratio(self.risk.volatility)}",
                f"  sharpe ratio: {_format_value(self.risk.sharpe_ratio)}",
                "Trade Quality",
                f"  closed trades: {self.trades.closed_trade_count}",
                f"  win rate: {_format_ratio(self.trades.win_rate)}",
                f"  profit factor: {_format_value(self.trades.profit_factor)}",
                "Costs",
                f"  gross realized pnl: {_format_value(self.costs.gross_realized_pnl)}",
                f"  net realized pnl: {_format_value(self.costs.net_realized_pnl)}",
                f"  total fees: {_format_value(self.costs.total_fees)}",
                f"  fees / initial cash: {_format_ratio(self.costs.fees_as_initial_cash)}",
                "Exposure And Ending State",
                f"  exposure: {_format_ratio(self.exposure.exposure_ratio)}",
                f"  ending state: {self.exposure.ending_state}",
                f"  final quantity: {_format_value(self.exposure.final_position_quantity)}",
                f"  final average entry: {_format_value(self.exposure.final_average_entry_price)}",
                "Execution Assumptions",
                f"  order activation: {self.execution.order_activation_timing}",
                f"  fill price basis: {self.execution.fill_price_basis}",
                f"  open position finalization: {self.execution.open_position_finalization}",
            )
        )

    def __str__(self) -> str:
        return self.to_text()


@dataclass(slots=True)
class _OpenAggregate:
    entry_timestamp: int
    entry_bar_index: int
    quantity: float
    gross_entry_value: float
    entry_fee_pool: float
    entry_tags: list[str]

    @property
    def average_entry_price(self) -> float:
        if self.quantity <= 0.0:
            return 0.0
        return self.gross_entry_value / self.quantity


class _ReportBuilder:
    def __init__(self) -> None:
        self._equity: list[EquityPoint] = []
        self._fills: list[ReportingFill] = []
        self._closed_trades: list[ClosedTrade] = []
        self._open: _OpenAggregate | None = None
        self._equity_peak: float | None = None

    def record_fill(
        self,
        *,
        order: Order,
        fill: FillEvent,
        state_before: TradingState,
        state_after: TradingState,
        bar_index: int,
    ) -> None:
        self._fills.append(
            ReportingFill(
                order_id=order.id,
                order_type=order.order_type,
                tag=order.tag,
                timestamp=fill.timestamp,
                symbol=fill.symbol,
                side=fill.side,
                quantity=fill.quantity,
                price=fill.price,
                fee=fill.fee,
            )
        )
        if fill.side == "buy":
            self._record_buy(order=order, fill=fill, state_before=state_before, bar_index=bar_index)
            return
        self._record_sell(
            order=order,
            fill=fill,
            state_before=state_before,
            state_after=state_after,
            bar_index=bar_index,
        )

    def record_equity(
        self,
        *,
        bar_index: int,
        timestamp: int,
        mark_price: float,
        state: TradingState,
    ) -> None:
        peak = state.equity if self._equity_peak is None else max(self._equity_peak, state.equity)
        self._equity_peak = peak
        drawdown = drawdown_for_equity(running_peak=peak, equity=state.equity)
        self._equity.append(
            EquityPoint(
                bar_index=bar_index,
                timestamp=timestamp,
                equity=state.equity,
                cash=state.cash,
                position_quantity=state.position_quantity,
                mark_price=mark_price,
                drawdown=drawdown,
            )
        )

    def build(
        self,
        *,
        bars: BarSeries,
        initial_cash: float,
        costs: CostConfig,
        execution_model_name: str,
        strategy: Any,
        run_label: str | None,
        final_state: TradingState,
        order_rejections: tuple[OrderRejectedEvent, ...],
        bars_in_position: int,
        annual_risk_free_rate: float = 0.0,
    ) -> BacktestReport:
        periods_per_year = periods_per_year_for_timeframe(
            timeframe=bars.timeframe,
            timestamps=tuple(row.timestamp for row in bars.rows),
        )
        equity_values = tuple(point.equity for point in self._equity)
        returns = _periodic_returns(initial_cash=initial_cash, equity_values=equity_values)
        final_equity = final_state.equity
        equity_peak = max(equity_values) if equity_values else final_equity
        total_return = round((final_equity - initial_cash) / initial_cash, 12)
        buy_and_hold = _buy_and_hold_return(bars)
        active_return = (
            round(total_return - buy_and_hold, 12) if buy_and_hold is not None else None
        )
        gross_realized_pnl = round(final_state.realized_pnl, 12)
        net_realized_pnl = round(sum(trade.net_pnl for trade in self._closed_trades), 12)
        trade_returns = tuple(
            trade.net_return for trade in self._closed_trades if trade.net_return is not None
        )
        total_fees = round(sum(fill.fee for fill in self._fills), 12)
        closed_trade_fees = round(sum(trade.total_fees for trade in self._closed_trades), 12)
        closed_trade_gross_abs_pnl = round(
            sum(abs(trade.gross_pnl) for trade in self._closed_trades),
            12,
        )

        drawdown_curve = tuple(point.drawdown for point in self._equity)

        return BacktestReport(
            run=RunManifest(
                symbol=bars.symbol,
                timeframe=bars.timeframe,
                start_timestamp=bars.rows[0].timestamp,
                end_timestamp=bars.rows[-1].timestamp,
                bar_count=len(bars.rows),
                initial_cash=initial_cash,
                execution_model_name=execution_model_name,
                strategy_class_name=type(strategy).__name__,
                strategy_display_name=_strategy_display_name(strategy),
                strategy_parameters=_strategy_parameters(strategy),
                run_label=run_label,
            ),
            execution=ExecutionAssumptions(
                execution_model_name=execution_model_name,
                order_activation_timing="next_bar",
                fill_price_basis="conservative_ohlcv",
                open_position_finalization="mark_to_market",
                tick_size=costs.tick_size,
                slippage_ticks=costs.slippage_ticks,
                fee_rate=costs.fee_rate,
                order_rejection_count=len(order_rejections),
                annual_risk_free_rate=annual_risk_free_rate,
                periods_per_year=periods_per_year,
            ),
            returns=ReturnMetrics(
                final_equity=final_equity,
                equity_peak=equity_peak,
                total_return=total_return,
                buy_and_hold_return=buy_and_hold,
                active_return=active_return,
                annualized_return=_annualized_return(
                    initial_cash=initial_cash,
                    final_equity=final_equity,
                    period_count=len(equity_values),
                    periods_per_year=periods_per_year,
                ),
                final_cash=final_state.cash,
                gross_realized_pnl=gross_realized_pnl,
                net_realized_pnl=net_realized_pnl,
                unrealized_pnl=final_state.unrealized_pnl,
            ),
            risk=RiskMetrics(
                max_drawdown=max_drawdown_from_curve(drawdown_curve),
                longest_drawdown_bar_count=_longest_drawdown_bar_count(self._equity),
                volatility=_annualized_volatility(
                    returns=returns,
                    periods_per_year=periods_per_year,
                ),
                sharpe_ratio=_sharpe_ratio(
                    returns=returns,
                    annual_risk_free_rate=annual_risk_free_rate,
                    periods_per_year=periods_per_year,
                ),
                annual_risk_free_rate=annual_risk_free_rate,
                periods_per_year=periods_per_year,
            ),
            trades=_trade_metrics(
                self._closed_trades,
                trade_returns,
                fill_count=len(self._fills),
            ),
            costs=CostMetrics(
                total_fees=total_fees,
                fees_as_initial_cash=round(total_fees / initial_cash, 12),
                closed_trade_fees=closed_trade_fees,
                gross_realized_pnl=gross_realized_pnl,
                net_realized_pnl=net_realized_pnl,
                fees_to_gross_pnl_ratio=_fees_to_gross_ratio(
                    fees=closed_trade_fees,
                    closed_trade_gross_abs_pnl=closed_trade_gross_abs_pnl,
                ),
            ),
            exposure=ExposureMetrics(
                bars_in_position=bars_in_position,
                total_bars=len(bars.rows),
                exposure_ratio=bars_in_position / len(bars.rows),
                ending_state="open" if final_state.position_quantity > 0.0 else "flat",
                final_position_quantity=final_state.position_quantity,
                final_average_entry_price=(
                    final_state.average_entry_price
                    if final_state.position_quantity > 0.0
                    else None
                ),
            ),
            equity=tuple(self._equity),
            fills=tuple(self._fills),
            closed_trades=tuple(self._closed_trades),
            order_rejections=order_rejections,
        )

    def _record_buy(
        self,
        *,
        order: Order,
        fill: FillEvent,
        state_before: TradingState,
        bar_index: int,
    ) -> None:
        tag = () if order.tag is None else (order.tag,)
        if state_before.position_quantity <= 0.0 or self._open is None:
            self._open = _OpenAggregate(
                entry_timestamp=fill.timestamp,
                entry_bar_index=bar_index,
                quantity=fill.quantity,
                gross_entry_value=fill.price * fill.quantity,
                entry_fee_pool=fill.fee,
                entry_tags=list(tag),
            )
            return
        self._open.quantity = round(self._open.quantity + fill.quantity, 12)
        self._open.gross_entry_value = round(
            self._open.gross_entry_value + (fill.price * fill.quantity),
            12,
        )
        self._open.entry_fee_pool = round(self._open.entry_fee_pool + fill.fee, 12)
        self._open.entry_tags.extend(tag)

    def _record_sell(
        self,
        *,
        order: Order,
        fill: FillEvent,
        state_before: TradingState,
        state_after: TradingState,
        bar_index: int,
    ) -> None:
        open_trade = self._open
        if open_trade is None or state_before.position_quantity <= 0.0:
            return
        allocated_entry_fee = round(
            open_trade.entry_fee_pool * (fill.quantity / state_before.position_quantity),
            12,
        )
        entry_price = round(state_before.average_entry_price, 12)
        gross_pnl = round((fill.price - entry_price) * fill.quantity, 12)
        net_pnl = round(gross_pnl - allocated_entry_fee - fill.fee, 12)
        entry_value = round((entry_price * fill.quantity) + allocated_entry_fee, 12)
        entry_tags = tuple(open_trade.entry_tags)
        self._closed_trades.append(
            ClosedTrade(
                entry_timestamp=open_trade.entry_timestamp,
                exit_timestamp=fill.timestamp,
                entry_bar_index=open_trade.entry_bar_index,
                exit_bar_index=bar_index,
                duration_bars=bar_index - open_trade.entry_bar_index + 1,
                quantity=fill.quantity,
                entry_price=entry_price,
                exit_price=fill.price,
                gross_pnl=gross_pnl,
                net_pnl=net_pnl,
                allocated_entry_fee=allocated_entry_fee,
                exit_fee=fill.fee,
                total_fees=round(allocated_entry_fee + fill.fee, 12),
                net_return=round(net_pnl / entry_value, 12) if entry_value > 0.0 else None,
                entry_tag=_single_entry_tag(entry_tags),
                entry_tags=entry_tags,
                exit_tag=order.tag,
            )
        )
        if state_after.position_quantity <= 0.0:
            self._open = None
            return
        open_trade.quantity = round(state_after.position_quantity, 12)
        open_trade.gross_entry_value = round(entry_price * state_after.position_quantity, 12)
        open_trade.entry_fee_pool = round(open_trade.entry_fee_pool - allocated_entry_fee, 12)


def periods_per_year_for_timeframe(
    *,
    timeframe: str,
    timestamps: tuple[int, ...],
) -> float | None:
    parsed = _parse_timeframe_seconds(timeframe)
    if parsed is not None and parsed > 0.0:
        return _SECONDS_PER_YEAR / parsed
    if len(timestamps) < 2:
        return None
    positive_deltas = tuple(
        (current - previous) / 1000
        for previous, current in zip(timestamps, timestamps[1:])
        if current > previous
    )
    if not positive_deltas:
        return None
    return _SECONDS_PER_YEAR / median(positive_deltas)


def _parse_timeframe_seconds(timeframe: str) -> float | None:
    match = _TIMEFRAME_RE.fullmatch(timeframe)
    if match is None:
        return None
    return float(match.group("count")) * _TIMEFRAME_SECONDS[match.group("unit")]


def _periodic_returns(
    *,
    initial_cash: float,
    equity_values: tuple[float, ...],
) -> tuple[float, ...]:
    if initial_cash <= 0.0:
        return ()
    returns: list[float] = []
    if equity_values:
        returns.append(round((equity_values[0] - initial_cash) / initial_cash, 12))
    for previous, current in zip(equity_values, equity_values[1:]):
        if previous <= 0.0:
            continue
        returns.append(round((current - previous) / previous, 12))
    return tuple(returns)


def _annualized_return(
    *,
    initial_cash: float,
    final_equity: float,
    period_count: int,
    periods_per_year: float | None,
) -> float | None:
    if initial_cash <= 0.0 or final_equity < 0.0 or period_count <= 0:
        return None
    if periods_per_year is None or periods_per_year <= 0.0:
        return None
    ratio = final_equity / initial_cash
    if ratio == 0.0:
        return -1.0
    try:
        value: float = float(ratio ** (periods_per_year / period_count) - 1)
    except OverflowError:
        return math.inf if ratio > 1.0 else None
    if math.isinf(value):
        return value
    return _finite_or_none(value)


def _volatility(returns: tuple[float, ...]) -> float | None:
    if len(returns) < 2:
        return None
    return _finite_or_none(stdev(returns))


def _annualized_volatility(
    *,
    returns: tuple[float, ...],
    periods_per_year: float | None,
) -> float | None:
    volatility = _volatility(returns)
    if volatility is None:
        return None
    if periods_per_year is None or periods_per_year <= 0.0:
        return None
    return _finite_or_none(volatility * math.sqrt(periods_per_year))


def _sharpe_ratio(
    *,
    returns: tuple[float, ...],
    annual_risk_free_rate: float,
    periods_per_year: float | None,
) -> float | None:
    if periods_per_year is None or periods_per_year <= 0.0:
        return None
    period_rf = _period_risk_free(annual_risk_free_rate, periods_per_year)
    if period_rf is None:
        return None
    excess = tuple(value - period_rf for value in returns)
    if len(excess) < 2:
        return None
    volatility = _volatility(excess)
    if volatility is None or volatility == 0.0:
        average_excess = mean(excess)
        if average_excess > 0.0:
            return math.inf
        if average_excess < 0.0:
            return -math.inf
        return None
    return _finite_or_none((mean(excess) / volatility) * math.sqrt(periods_per_year))


def _period_risk_free(
    annual_risk_free_rate: float,
    periods_per_year: float | None,
) -> float | None:
    if periods_per_year is None or periods_per_year <= 0.0:
        return None if annual_risk_free_rate != 0.0 else 0.0
    return float((1.0 + annual_risk_free_rate) ** (1.0 / periods_per_year) - 1.0)


def _buy_and_hold_return(bars: BarSeries) -> float | None:
    first_close = bars.rows[0].close
    if first_close <= 0.0:
        return None
    return round((bars.rows[-1].close - first_close) / first_close, 12)


def _longest_drawdown_bar_count(equity: list[EquityPoint]) -> int:
    current = 0
    longest = 0
    for point in equity:
        if point.drawdown > 0.0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _trade_metrics(
    closed_trades: list[ClosedTrade],
    trade_returns: tuple[float, ...],
    *,
    fill_count: int,
) -> TradeMetrics:
    if not closed_trades:
        return TradeMetrics(
            closed_trade_count=0,
            fill_count=fill_count,
            win_rate=None,
            best_trade=None,
            worst_trade=None,
            average_win=None,
            average_loss=None,
            profit_factor=None,
            average_trade_return=None,
            expectancy_return=None,
        )
    pnls = tuple(trade.net_pnl for trade in closed_trades)
    wins = tuple(value for value in pnls if value > 0.0)
    losses = tuple(value for value in pnls if value < 0.0)
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor: float | None
    if gross_loss == 0.0:
        profit_factor = math.inf if gross_profit > 0.0 else None
    else:
        profit_factor = round(gross_profit / gross_loss, 12)
    return TradeMetrics(
        closed_trade_count=len(closed_trades),
        fill_count=fill_count,
        win_rate=round(len(wins) / len(closed_trades), 12),
        best_trade=max(trade_returns) if trade_returns else None,
        worst_trade=min(trade_returns) if trade_returns else None,
        average_win=round(sum(wins) / len(wins), 12) if wins else None,
        average_loss=round(abs(sum(losses)) / len(losses), 12) if losses else None,
        profit_factor=profit_factor,
        average_trade_return=_geometric_average(trade_returns),
        expectancy_return=round(mean(trade_returns), 12) if trade_returns else None,
    )


def _geometric_average(values: tuple[float, ...]) -> float | None:
    if not values:
        return None
    product = 1.0
    for value in values:
        if value < -1.0:
            return None
        product *= 1.0 + value
    return _finite_or_none(product ** (1.0 / len(values)) - 1.0)


def _fees_to_gross_ratio(
    *,
    fees: float,
    closed_trade_gross_abs_pnl: float,
) -> float | None:
    if closed_trade_gross_abs_pnl == 0.0:
        return None
    return round(fees / closed_trade_gross_abs_pnl, 12)


def _single_entry_tag(entry_tags: tuple[str, ...]) -> str | None:
    unique = tuple(dict.fromkeys(entry_tags))
    return unique[0] if len(unique) == 1 else None


def _strategy_display_name(strategy: Any) -> str | None:
    value = getattr(strategy, "display_name", None)
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ValueError("Strategy.display_name must be a non-empty string or None")
    return value


def _strategy_parameters(strategy: Any) -> dict[str, object]:
    parameters = strategy.parameters()
    if not isinstance(parameters, dict):
        parameters = dict(parameters)
    for key in parameters:
        if not isinstance(key, str) or not key:
            raise ValueError("Strategy.parameters() keys must be non-empty strings")
    return {key: _normalize_public_value(value) for key, value in parameters.items()}


def _normalize_public_value(value: object) -> object:
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _finite_or_none(value: float) -> float | None:
    if not math.isfinite(value):
        return None
    return round(value, 12)


def _format_value(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float) and math.isinf(value):
        return "inf" if value > 0 else "-inf"
    return f"{value:.12g}" if isinstance(value, float) else str(value)


def _format_ratio(value: float | None) -> str:
    if value is None:
        return "n/a"
    if math.isinf(value):
        return "inf" if value > 0 else "-inf"
    return f"{value:.2%}"


__all__ = [
    "BacktestReport",
    "ClosedTrade",
    "CostMetrics",
    "EquityPoint",
    "ExecutionAssumptions",
    "ExposureMetrics",
    "ReportingFill",
    "ReturnMetrics",
    "RiskMetrics",
    "RunManifest",
    "TradeMetrics",
    "periods_per_year_for_timeframe",
]
