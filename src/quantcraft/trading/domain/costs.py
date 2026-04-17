from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CostConfig:
    tick_size: float
    slippage_ticks: float
    fee_rate: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.tick_size) or self.tick_size <= 0.0:
            raise ValueError("tick_size must be a positive finite float")
        if not math.isfinite(self.slippage_ticks) or self.slippage_ticks < 0.0:
            raise ValueError("slippage_ticks must be a non-negative finite float")
        if not math.isfinite(self.fee_rate) or self.fee_rate < 0.0:
            raise ValueError("fee_rate must be a non-negative finite float")
