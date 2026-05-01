from __future__ import annotations


def drawdown_for_equity(*, running_peak: float, equity: float) -> float:
    if running_peak <= 0.0:
        return 0.0
    return round(max((running_peak - equity) / running_peak, 0.0), 12)


def drawdown_curve_for_equity(equity_curve: tuple[float, ...]) -> tuple[float, ...]:
    running_peak: float | None = None
    drawdowns: list[float] = []
    for equity in equity_curve:
        running_peak = equity if running_peak is None else max(running_peak, equity)
        drawdowns.append(drawdown_for_equity(running_peak=running_peak, equity=equity))
    return tuple(drawdowns)


def max_drawdown_from_curve(drawdown_curve: tuple[float, ...]) -> float:
    return max(drawdown_curve) if drawdown_curve else 0.0
