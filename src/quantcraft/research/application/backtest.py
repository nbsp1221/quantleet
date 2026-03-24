from __future__ import annotations

from dataclasses import dataclass

from quantcraft.research.adapters.synthetic_events import OHLCVBar, convert_ohlcv_to_backtest_events
from quantcraft.research.application._runtime import _StrategyDriver
from quantcraft.research.application.strategy import Strategy
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BarEvent, FillEvent, TickEvent
from quantcraft.trading.domain.intents import OrderIntent
from quantcraft.trading.domain.matching import match_order_intent
from quantcraft.trading.domain.state import TradingState, apply_fill


@dataclass(frozen=True, slots=True)
class ExposureSummary:
    bars_in_position: int
    total_bars: int
    exposure_ratio: float


@dataclass(frozen=True, slots=True)
class BacktestSummary:
    total_trades: int
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
    runtime = _StrategyDriver(strategy)
    runtime.initialize()
    state = TradingState(cash=initial_cash, equity=initial_cash)
    trade_log: list[FillEvent] = []
    equity_curve: list[float] = []
    closing_trade_pnls: list[float] = []
    bars_in_position = 0
    total_bars = 0
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
                runtime.activate_pending_order_intents()

            remaining_intents: list[OrderIntent] = []
            for intent in runtime.order_state().active:
                fill = match_order_intent(intent, event, costs)
                if fill is None:
                    remaining_intents.append(intent)
                    continue

                previous_realized_pnl = state.realized_pnl
                state = apply_fill(state, fill, mark_price=event.last)
                realized_delta = round(state.realized_pnl - previous_realized_pnl, 12)
                if fill.side == "sell":
                    closing_trade_pnls.append(realized_delta)
                trade_log.append(fill)
            runtime.replace_active_order_intents(tuple(remaining_intents))
            continue

        if isinstance(event, BarEvent):
            runtime.handle_bar(event)
            total_bars += 1
            if latest_mark_price is not None:
                marked_state = _mark_state_to_market(state, mark_price=latest_mark_price)
            else:
                marked_state = state
            equity_curve.append(marked_state.equity)
            if marked_state.position_quantity > 0.0:
                bars_in_position += 1

    if latest_mark_price is not None:
        state = _mark_state_to_market(state, mark_price=latest_mark_price)

    total_fees = round(sum(fill.fee for fill in trade_log), 12)
    total_return = round((state.equity - initial_cash) / initial_cash, 12)
    max_drawdown = _max_drawdown(tuple(equity_curve))
    average_win, average_loss, win_rate, profit_factor = _trade_statistics(
        tuple(closing_trade_pnls)
    )
    summary = BacktestSummary(
        total_trades=len(trade_log),
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
