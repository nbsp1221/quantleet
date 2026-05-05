from __future__ import annotations


class OrderActivationPolicy:
    __slots__ = ("_current_tick_timestamp",)

    def __init__(self) -> None:
        self._current_tick_timestamp: int | None = None

    def begin_tick(self, timestamp: int) -> bool:
        if timestamp == self._current_tick_timestamp:
            return False
        self._current_tick_timestamp = timestamp
        return True

    def reset(self) -> None:
        self._current_tick_timestamp = None


__all__ = ["OrderActivationPolicy"]
