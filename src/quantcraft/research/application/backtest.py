from __future__ import annotations

from dataclasses import dataclass

from quantcraft.research.adapters.synthetic_events import OHLCVBar, convert_ohlcv_to_backtest_events
from quantcraft.research.application.strategy import Strategy
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BarEvent, FillEvent, TickEvent
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.matching import match_order_intent
from quantcraft.trading.domain.state import TradingState, apply_fill


@dataclass(frozen=True, slots=True)
class BacktestSummary:
    trade_count: int
    total_fees: float
    ending_equity: float
    realized_pnl: float
    unrealized_pnl: float


@dataclass(frozen=True, slots=True)
class BacktestResult:
    trade_log: tuple[FillEvent, ...]
    final_state: TradingState
    summary: BacktestSummary


def run_backtest(
    *,
    symbol: str,
    bar_type: str,
    bar_spec: object,
    rows: tuple[OHLCVBar, ...],
    strategy: Strategy,
    initial_cash: float,
    costs: CostConfig,
) -> BacktestResult:
    state = TradingState(cash=initial_cash, equity=initial_cash)
    trade_log: list[FillEvent] = []
    current_tick_timestamp: int | None = None
    latest_mark_price: float | None = None

    events = convert_ohlcv_to_backtest_events(
        symbol=symbol,
        bar_type=bar_type,
        bar_spec=bar_spec,
        rows=rows,
    )

    for event in events:
        if isinstance(event, TickEvent):
            latest_mark_price = event.last
            if event.timestamp != current_tick_timestamp:
                current_tick_timestamp = event.timestamp
                strategy._roll_order_intents_to_next_bar()

            remaining_intents: list[OrderIntent] = []
            for intent in strategy.active_order_intents():
                fill = match_order_intent(intent, event, costs)
                if fill is None:
                    remaining_intents.append(intent)
                    continue

                state = apply_fill(state, fill, mark_price=event.last)
                trade_log.append(fill)
            strategy._replace_active_order_intents(tuple(remaining_intents))
            continue

        if isinstance(event, BarEvent):
            strategy.handle_bar(event)

    if latest_mark_price is not None:
        state = _mark_state_to_market(state, mark_price=latest_mark_price)

    summary = BacktestSummary(
        trade_count=len(trade_log),
        total_fees=round(sum(fill.fee for fill in trade_log), 12),
        ending_equity=state.equity,
        realized_pnl=state.realized_pnl,
        unrealized_pnl=state.unrealized_pnl,
    )
    return BacktestResult(
        trade_log=tuple(trade_log),
        final_state=state,
        summary=summary,
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
