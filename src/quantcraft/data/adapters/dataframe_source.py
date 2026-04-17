from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, cast

from quantcraft.data.bars import BarSeries, TimeBar
from quantcraft.data.sources import HistoricalDataSource


class _RecordsFrame(Protocol):
    def to_dict(self, orient: str) -> Sequence[Mapping[str, object]]: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class DataFrameDataSource(HistoricalDataSource):
    frame: _RecordsFrame | Sequence[Mapping[str, object]]
    symbol: str
    timeframe: str

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol must be non-empty")
        if not self.timeframe:
            raise ValueError("timeframe must be non-empty")

    def load(self) -> BarSeries:
        rows = _coerce_rows(self.frame)
        return BarSeries(
            symbol=self.symbol,
            timeframe=self.timeframe,
            bar_type="time",
            rows=tuple(_normalize_row(row) for row in rows),
        )


def _coerce_rows(
    frame: _RecordsFrame | Sequence[Mapping[str, object]],
) -> list[Mapping[str, object]]:
    if hasattr(frame, "to_dict"):
        table = cast(_RecordsFrame, frame)
        return list(table.to_dict("records"))
    return list(frame)


def _normalize_row(row: Mapping[str, object]) -> TimeBar:
    _validate_required_columns(row)

    return TimeBar(
        timestamp=_normalize_timestamp(row["timestamp"]),
        open=_as_float(row["open"], field="open"),
        high=_as_float(row["high"], field="high"),
        low=_as_float(row["low"], field="low"),
        close=_as_float(row["close"], field="close"),
        volume=_as_float(row.get("volume", 0.0), field="volume"),
    )


def _validate_required_columns(row: Mapping[str, object]) -> None:
    required = {"timestamp", "open", "high", "low", "close"}
    missing = sorted(required - set(row))
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"missing required columns: {joined}")
    if "symbol" in row or "timeframe" in row:
        raise ValueError("symbol/timeframe columns are not allowed")


def _normalize_timestamp(value: object) -> int:
    if isinstance(value, datetime):
        return _datetime_to_millis(value)

    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError("timestamp must be explicitly parseable and timezone-aware") from exc
        return _datetime_to_millis(parsed)

    raise ValueError("timestamp must be timezone-aware or explicitly parseable")


def _datetime_to_millis(value: datetime) -> int:
    if value.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return int(value.astimezone(UTC).timestamp() * 1000)


def _as_float(value: object, *, field: str) -> float:
    try:
        return float(cast(float | str, value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be numeric") from exc
