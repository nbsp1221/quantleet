from __future__ import annotations

from quantleet.backtest.analytics import drawdown_curve_for_equity, max_drawdown_from_curve
from quantleet.backtest.execution_model import (
    BacktestExecutionModel,
    ConservativeOHLCVExecutionModel,
)
from quantleet.backtest.reporting import _ReportBuilder
from quantleet.backtest.results import (
    BacktestResult,
    BacktestSummary,
    ExposureSummary,
    _BacktestRunSnapshot,
)
from quantleet.backtest.strategy_runtime import StrategyLike, _StrategyDriver
from quantleet.data import BarSeries
from quantleet.trading.domain.costs import CostConfig
from quantleet.trading.domain.events import BarEvent, FillEvent, OrderRejectedEvent
from quantleet.trading.domain.matching import is_order_triggered, match_order
from quantleet.trading.domain.orders import Order
from quantleet.trading.domain.state import TradingState, apply_fill


def _run_backtest(
    *,
    bars: BarSeries,
    strategy: StrategyLike,
    initial_cash: float,
    costs: CostConfig,
    label: str | None,
) -> BacktestResult:
    runtime = _StrategyDriver(strategy)
    runtime.initialize(bars=bars)
    execution_model: BacktestExecutionModel = ConservativeOHLCVExecutionModel()
    report_builder = _ReportBuilder()
    state = TradingState(cash=initial_cash, equity=initial_cash)
    trade_log: list[FillEvent] = []
    order_events: list[OrderRejectedEvent] = []
    buy_reservations: dict[int, float] = {}
    equity_curve: list[float] = []
    closing_trade_pnls: list[float] = []
    open_entry_fee_pool = 0.0
    bars_in_position = 0
    report_bars_in_position = 0
    total_bars = 0
    latest_mark_price: float | None = None

    previous_close: float | None = None
    previous_timestamp: int | None = None

    for bar_index, bar in enumerate(bars.rows):
        if previous_timestamp is not None and previous_timestamp >= bar.timestamp:
            raise ValueError("out-of-order time bars")
        bar_had_position = state.position_quantity > 0.0

        runtime.activate_pending_order_requests(
            bar=bar,
            state=state,
            costs=costs,
        )
        order_events.extend(runtime.drain_order_events())
        buy_reservations = _sync_buy_reservations(
            orders=runtime.order_state().active,
            existing=buy_reservations,
            costs=costs,
        )
        tick_events = execution_model.tick_events_for_bar(
            symbol=bars.symbol,
            previous_close=previous_close,
            bar=bar,
            active_orders=runtime.order_state().active,
        )

        for event in tick_events:
            latest_mark_price = event.last
            active_orders = runtime.order_state().active
            remaining_orders: list[Order] = []
            newly_triggered_orders: list[Order] = []

            for order in active_orders:
                if _is_flat_exit_order(order=order, state=state):
                    continue
                if not order.is_executable:
                    if is_order_triggered(order, event):
                        newly_triggered_orders.append(order.trigger(timestamp=event.timestamp))
                    else:
                        remaining_orders.append(order)
                    continue

                fill = match_order(order, event, costs)
                if fill is None:
                    remaining_orders.append(order)
                    continue
                rejection = _runtime_fill_rejection(
                    state=state,
                    order=order,
                    fill=fill,
                    buy_reservations=buy_reservations,
                    timestamp=event.timestamp,
                )
                if rejection is not None:
                    order_events.append(rejection)
                    buy_reservations.pop(order.id, None)
                    continue

                state_before = state
                original_order = order
                state, open_entry_fee_pool, order = _apply_runtime_fill(
                    state=state,
                    order=order,
                    fill=fill,
                    mark_price=event.last,
                    open_entry_fee_pool=open_entry_fee_pool,
                    closing_trade_pnls=closing_trade_pnls,
                    trade_log=trade_log,
                )
                bar_had_position = (
                    bar_had_position
                    or state_before.position_quantity > 0.0
                    or state.position_quantity > 0.0
                )
                report_builder.record_fill(
                    order=original_order,
                    fill=fill,
                    state_before=state_before,
                    state_after=state,
                    bar_index=bar_index,
                )
                _update_buy_reservation_after_fill(
                    reservations=buy_reservations,
                    order=order,
                    fill=fill,
                    costs=costs,
                )
                if order.is_open:
                    remaining_orders.append(order)
                else:
                    buy_reservations.pop(order.id, None)

            for order in newly_triggered_orders:
                if _is_flat_exit_order(order=order, state=state):
                    continue

                fill = match_order(order, event, costs)
                if fill is None:
                    remaining_orders.append(order)
                    continue
                rejection = _runtime_fill_rejection(
                    state=state,
                    order=order,
                    fill=fill,
                    buy_reservations=buy_reservations,
                    timestamp=event.timestamp,
                )
                if rejection is not None:
                    order_events.append(rejection)
                    buy_reservations.pop(order.id, None)
                    continue

                state_before = state
                original_order = order
                state, open_entry_fee_pool, order = _apply_runtime_fill(
                    state=state,
                    order=order,
                    fill=fill,
                    mark_price=event.last,
                    open_entry_fee_pool=open_entry_fee_pool,
                    closing_trade_pnls=closing_trade_pnls,
                    trade_log=trade_log,
                )
                bar_had_position = (
                    bar_had_position
                    or state_before.position_quantity > 0.0
                    or state.position_quantity > 0.0
                )
                report_builder.record_fill(
                    order=original_order,
                    fill=fill,
                    state_before=state_before,
                    state_after=state,
                    bar_index=bar_index,
                )
                _update_buy_reservation_after_fill(
                    reservations=buy_reservations,
                    order=order,
                    fill=fill,
                    costs=costs,
                )
                if order.is_open:
                    remaining_orders.append(order)
                else:
                    buy_reservations.pop(order.id, None)

            runtime.replace_active_orders(tuple(remaining_orders))

        bar_event = BarEvent(
            bar_type=bars.bar_type,
            bar_spec=bars.timeframe,
            symbol=bars.symbol,
            timestamp=bar.timestamp,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            is_closed=True,
        )
        runtime.handle_bar(bar_event, state=state)
        total_bars += 1
        if latest_mark_price is not None:
            marked_state = _mark_state_to_market(state, mark_price=latest_mark_price)
        else:
            marked_state = state
        equity_curve.append(marked_state.equity)
        report_builder.record_equity(
            bar_index=bar_index,
            timestamp=bar.timestamp,
            mark_price=latest_mark_price if latest_mark_price is not None else bar.close,
            state=marked_state,
        )
        if marked_state.position_quantity > 0.0:
            bars_in_position += 1
        if bar_had_position:
            report_bars_in_position += 1
        previous_close = bar.close
        previous_timestamp = bar.timestamp

    if latest_mark_price is not None:
        state = _mark_state_to_market(state, mark_price=latest_mark_price)

    equity_curve_tuple = tuple(equity_curve)
    drawdown_curve = drawdown_curve_for_equity(equity_curve_tuple)
    total_fees = round(sum(fill.fee for fill in trade_log), 12)
    total_return = round((state.equity - initial_cash) / initial_cash, 12)
    average_win, average_loss, win_rate, profit_factor = _trade_statistics(
        tuple(closing_trade_pnls)
    )
    summary = BacktestSummary(
        total_trades=len(closing_trade_pnls),
        total_fills=len(trade_log),
        total_fees=total_fees,
        final_balance=state.cash,
        final_equity=state.equity,
        total_return=total_return,
        max_drawdown=max_drawdown_from_curve(drawdown_curve),
        realized_pnl=state.realized_pnl,
        unrealized_pnl=state.unrealized_pnl,
        win_rate=win_rate,
        average_win=average_win,
        average_loss=average_loss,
        profit_factor=profit_factor,
        exposure=ExposureSummary(
            bars_in_position=bars_in_position,
            total_bars=total_bars,
            exposure_ratio=(bars_in_position / total_bars) if total_bars else 0.0,
        ),
    )
    order_events_tuple = tuple(order_events)
    report = report_builder.build(
        bars=bars,
        initial_cash=initial_cash,
        costs=costs,
        execution_model_name=execution_model.name,
        strategy=strategy,
        run_label=label,
        final_state=state,
        order_rejections=order_events_tuple,
        bars_in_position=report_bars_in_position,
    )
    return BacktestResult(
        trade_log=tuple(trade_log),
        equity_curve=equity_curve_tuple,
        final_state=state,
        summary=summary,
        order_events=order_events_tuple,
        execution_model_name=execution_model.name,
        drawdown_curve=drawdown_curve,
        _report=report,
        _run_snapshot=_snapshot_from_bars(bars),
    )


def _snapshot_from_bars(bars: BarSeries) -> _BacktestRunSnapshot:
    return _BacktestRunSnapshot(
        symbol=bars.symbol,
        timeframe=bars.timeframe,
        bar_type=bars.bar_type,
        timestamps=tuple(row.timestamp for row in bars.rows),
        closes=tuple(row.close for row in bars.rows),
    )


def _runtime_fill_rejection(
    *,
    state: TradingState,
    order: Order,
    fill: FillEvent,
    buy_reservations: dict[int, float],
    timestamp: int,
) -> OrderRejectedEvent | None:
    if order.side == "buy":
        required_cash = round((fill.price * fill.quantity) + fill.fee, 12)
        available_for_order = round(
            buy_reservations.get(order.id, 0.0) + _unreserved_cash(state, buy_reservations),
            12,
        )
        if required_cash - available_for_order > 1e-12:
            return OrderRejectedEvent(
                symbol=order.symbol,
                side=order.side,
                order_type=order.order_type,
                reason="execution_affordability",
                timestamp=timestamp,
                quantity=order.remaining_quantity,
                order_id=order.id,
                tag=order.tag,
            )
    return None


def _sync_buy_reservations(
    *,
    orders: tuple[Order, ...],
    existing: dict[int, float],
    costs: CostConfig,
) -> dict[int, float]:
    live_order_ids = {order.id for order in orders if order.is_open and order.side == "buy"}
    next_reservations = {
        order_id: cash for order_id, cash in existing.items() if order_id in live_order_ids
    }
    for order in orders:
        if order.side != "buy" or not order.is_open or order.id in next_reservations:
            continue
        next_reservations[order.id] = _buy_order_reserved_cash(order=order, costs=costs)
    return next_reservations


def _buy_order_reserved_cash(*, order: Order, costs: CostConfig) -> float:
    if order.side != "buy":
        return 0.0
    if order.order_type == "stop_market":
        if order.trigger_price is None:
            raise ValueError("stop_market buy orders require a trigger_price")
        anchor = order.trigger_price + (costs.tick_size * costs.slippage_ticks)
    elif order.executable_order_type == "limit":
        if order.limit_price is None:
            raise ValueError("limit buy orders require a limit_price")
        anchor = order.limit_price
    else:
        return 0.0
    position_budget = round(order.remaining_quantity * anchor, 12)
    return round(position_budget + (position_budget * costs.fee_rate), 12)


def _unreserved_cash(state: TradingState, reservations: dict[int, float]) -> float:
    return max(round(state.cash - sum(reservations.values()), 12), 0.0)


def _update_buy_reservation_after_fill(
    *,
    reservations: dict[int, float],
    order: Order,
    fill: FillEvent,
    costs: CostConfig,
) -> None:
    if order.side != "buy":
        return
    current_reservation = reservations.get(order.id)
    if current_reservation is None:
        return
    consumed_cash = round((fill.price * fill.quantity) + fill.fee, 12)
    next_reservation = max(round(current_reservation - consumed_cash, 12), 0.0)
    if order.remaining_quantity <= 0.0:
        reservations.pop(order.id, None)
        return
    minimum_remaining_reservation = _buy_order_reserved_cash(order=order, costs=costs)
    reservations[order.id] = max(next_reservation, minimum_remaining_reservation)


def _mark_state_to_market(state: TradingState, *, mark_price: float) -> TradingState:
    if state.position_quantity <= 0.0:
        return TradingState(
            cash=state.cash,
            position_quantity=state.position_quantity,
            average_entry_price=state.average_entry_price,
            realized_pnl=state.realized_pnl,
            unrealized_pnl=0.0,
            equity=round(state.cash, 12),
        )

    unrealized_pnl = round(
        (mark_price - state.average_entry_price) * state.position_quantity,
        12,
    )
    equity = round(state.cash + (state.position_quantity * mark_price), 12)
    return TradingState(
        cash=state.cash,
        position_quantity=state.position_quantity,
        average_entry_price=state.average_entry_price,
        realized_pnl=state.realized_pnl,
        unrealized_pnl=unrealized_pnl,
        equity=equity,
    )


def _trade_statistics(closing_trade_pnls: tuple[float, ...]) -> tuple[float, float, float, float]:
    if not closing_trade_pnls:
        return 0.0, 0.0, 0.0, 0.0

    wins = tuple(pnl for pnl in closing_trade_pnls if pnl > 0.0)
    losses = tuple(pnl for pnl in closing_trade_pnls if pnl < 0.0)
    average_win = round(sum(wins) / len(wins), 12) if wins else 0.0
    average_loss = round(abs(sum(losses)) / len(losses), 12) if losses else 0.0
    win_rate = round(len(wins) / len(closing_trade_pnls), 12)
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    if gross_loss == 0.0:
        profit_factor = float("inf") if gross_profit > 0.0 else 0.0
    else:
        profit_factor = round(gross_profit / gross_loss, 12)
    return average_win, average_loss, win_rate, profit_factor


def _allocated_entry_fee(
    *,
    open_entry_fee_pool: float,
    fill: FillEvent,
    state: TradingState,
) -> float:
    if state.position_quantity <= 0.0:
        raise ValueError("cannot allocate entry fees without an open position")
    allocated = open_entry_fee_pool * (fill.quantity / state.position_quantity)
    return round(allocated, 12)


def _is_flat_exit_order(*, order: Order, state: TradingState) -> bool:
    return order.side == "sell" and state.position_quantity <= 0.0


def _net_closed_trade_pnl(
    *,
    state: TradingState,
    fill: FillEvent,
    allocated_entry_fee: float,
) -> float:
    gross = (fill.price - state.average_entry_price) * fill.quantity
    net = gross - allocated_entry_fee - fill.fee
    return round(net, 12)


def _apply_runtime_fill(
    *,
    state: TradingState,
    order: Order,
    fill: FillEvent,
    mark_price: float,
    open_entry_fee_pool: float,
    closing_trade_pnls: list[float],
    trade_log: list[FillEvent],
) -> tuple[TradingState, float, Order]:
    previous_state = state
    allocated_entry_fee = 0.0
    if fill.side == "sell":
        allocated_entry_fee = _allocated_entry_fee(
            open_entry_fee_pool=open_entry_fee_pool,
            fill=fill,
            state=previous_state,
        )

    state = apply_fill(state, fill, mark_price=mark_price)
    if fill.side == "buy":
        open_entry_fee_pool = round(open_entry_fee_pool + fill.fee, 12)
    if fill.side == "sell":
        closing_trade_pnls.append(
            _net_closed_trade_pnl(
                state=previous_state,
                fill=fill,
                allocated_entry_fee=allocated_entry_fee,
            )
        )
        open_entry_fee_pool = round(open_entry_fee_pool - allocated_entry_fee, 12)
        if state.position_quantity == 0.0:
            open_entry_fee_pool = 0.0
    trade_log.append(fill)
    return state, open_entry_fee_pool, order.apply_fill(fill)


__all__ = ["_run_backtest"]
