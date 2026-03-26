from __future__ import annotations

from typing import get_type_hints

from quantcraft.data import HistoricalDataSource, OHLCVBar


def test_public_data_namespace_exports_domain_level_contract_only() -> None:
    assert HistoricalDataSource is not None
    assert OHLCVBar is not None


def test_source_contract_is_minimal_load_to_typed_bars_shape() -> None:
    annotations = get_type_hints(HistoricalDataSource.load)
    assert annotations["return"] == tuple[OHLCVBar, ...]
