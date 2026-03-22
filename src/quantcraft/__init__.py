from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = ["Exchange", "MarketType", "TimeBar"]

if TYPE_CHECKING:
    from quantcraft.exchange import Exchange, MarketType, TimeBar


def __getattr__(name: str) -> Any:
    if name in __all__:
        from quantcraft.exchange import Exchange, MarketType, TimeBar

        exports = {
            "Exchange": Exchange,
            "MarketType": MarketType,
            "TimeBar": TimeBar,
        }
        return exports[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
