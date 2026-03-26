from __future__ import annotations

from abc import ABC, abstractmethod

from quantcraft.data.domain.bars import OHLCVBar


class HistoricalDataSource(ABC):
    @abstractmethod
    def load(self) -> tuple[OHLCVBar, ...]:
        raise NotImplementedError
