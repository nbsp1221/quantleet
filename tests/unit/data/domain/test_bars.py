from __future__ import annotations

from dataclasses import is_dataclass

from quantcraft.data.domain import OHLCVBar


def test_data_domain_exports_canonical_ohlcv_bar() -> None:
    bar = OHLCVBar(
        timestamp=1_700_000_000_000,
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=10.0,
    )

    assert is_dataclass(bar)
    assert bar.close == 1.5
    assert bar.volume == 10.0
