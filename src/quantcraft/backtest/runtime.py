from __future__ import annotations

from quantcraft.backtest.execution_model import (
    BacktestExecutionModel,
    ConservativeOHLCVExecutionModel,
)
from quantcraft.backtest.order_activation import OrderActivationPolicy
from quantcraft.backtest.results import BacktestResult, BacktestSummary, ExposureSummary
from quantcraft.backtest.strategy_runtime import StrategyLike, _StrategyDriver
from quantcraft.data import BarSeries
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BarEvent, FillEvent
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.matching import match_order_intent
from quantcraft.trading.domain.state import TradingState, apply_fill


def _run_backtest(
    *,
    bars: BarSeries,
    strategy: StrategyLike,
    initial_cash: float,
    costs: CostConfig,
) -> BacktestResult:
    runtime = _StrategyDriver(strategy)
    runtime.initialize(bars=bars)
    activation_policy = OrderActivationPolicy()
    execution_model: BacktestExecutionModel = ConservativeOHLCVExecutionModel()
    state = TradingState(cash=initial_cash, equity=initial_cash)
    trade_log: list[FillEvent] = []
    equity_curve: list[float] = []
    closing_trade_pnls: list[float] = []
    open_entry_fee_pool = 0.0
    bars_in_position = 0
    total_bars = 0
    latest_mark_price: float | None = None

    previous_close: float | None = None
    previous_timestamp: int | None = None

    for bar in bars.rows:
        if previous_timestamp is not None and previous_timestamp >= bar.timestamp:
            raise ValueError("out-of-order time bars")

        order_state = runtime.order_state()
        tick_events = execution_model.tick_events_for_bar(
            symbol=bars.symbol,
            previous_close=previous_close,
            bar=bar,
            active_intents=order_state.active + order_state.pending,
        )

        for event in tick_events:
            latest_mark_price = event.last
            if activation_policy.begin_tick(event.timestamp):
                runtime.activate_pending_order_intents()

            remaining_intents: list[OrderIntent] = []
            for intent in runtime.order_state().active:
                if _is_flat_exit_intent(intent=intent, state=state):
                    continue

                fill = match_order_intent(intent, event, costs)
                if fill is None:
                    remaining_intents.append(intent)
                    continue

                previous_state = state
                allocated_entry_fee = 0.0
                if fill.side == "sell":
                    allocated_entry_fee = _allocated_entry_fee(
                        open_entry_fee_pool=open_entry_fee_pool,
                        fill=fill,
                        state=previous_state,
                    )

                state = apply_fill(state, fill, mark_price=event.last)
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
            runtime.replace_active_order_intents(tuple(remaining_intents))

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
        if marked_state.position_quantity > 0.0:
            bars_in_position += 1
        previous_close = bar.close
        previous_timestamp = bar.timestamp

    if latest_mark_price is not None:
        state = _mark_state_to_market(state, mark_price=latest_mark_price)

    total_fees = round(sum(fill.fee for fill in trade_log), 12)
    total_return = round((state.equity - initial_cash) / initial_cash, 12)
    max_drawdown = _max_drawdown(tuple(equity_curve))
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
        max_drawdown=max_drawdown,
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
    return BacktestResult(
        trade_log=tuple(trade_log),
        equity_curve=tuple(equity_curve),
        final_state=state,
        summary=summary,
        execution_model_name=execution_model.name,
    )


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


def _max_drawdown(equity_curve: tuple[float, ...]) -> float:
    if not equity_curve:
        return 0.0
    peak = equity_curve[0]
    max_drawdown = 0.0
    for equity in equity_curve:
        peak = max(peak, equity)
        if peak == 0.0:
            continue
        max_drawdown = max(max_drawdown, (peak - equity) / peak)
    return round(max_drawdown, 12)


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


def _is_flat_exit_intent(*, intent: OrderIntent, state: TradingState) -> bool:
    return intent.side == "sell" and state.position_quantity <= 0.0


def _net_closed_trade_pnl(
    *,
    state: TradingState,
    fill: FillEvent,
    allocated_entry_fee: float,
) -> float:
    gross = (fill.price - state.average_entry_price) * fill.quantity
    net = gross - allocated_entry_fee - fill.fee
    return round(net, 12)


__all__ = ["_run_backtest"]
