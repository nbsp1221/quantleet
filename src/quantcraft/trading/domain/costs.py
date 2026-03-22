from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CostConfig:
    tick_size: float
    slippage_ticks: float
    fee_rate: float
