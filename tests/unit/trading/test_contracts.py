from __future__ import annotations

from dataclasses import MISSING, Field, fields
from typing import Callable, Literal, get_args, get_type_hints

from quantcraft.trading.domain import __all__ as trading_domain_exports
from quantcraft.trading.domain import events as trading_events
from quantcraft.trading.domain.costs import CostConfig
from quantcraft.trading.domain.events import BarEvent, FillEvent, TickEvent
from quantcraft.trading.domain.intents import OrderIntent


def test_order_intent_matches_backtest_mvp_minimum_contract() -> None:
    order_intent_fields = fields(OrderIntent)

    assert_dataclass_includes_fields(
        order_intent_fields,
        required=("symbol", "side", "quantity", "order_type"),
        optional_none=("limit_price", "tag"),
    )

    hints = get_type_hints(OrderIntent)
    assert_field_type_hints(
        hints,
        exact={
            "symbol": str,
            "quantity": float,
        },
        predicates={
            "side": lambda annotation: get_origin_and_args(annotation)
            == (Literal, ("buy", "sell")),
            "order_type": lambda annotation: get_origin_and_args(annotation)
            == (Literal, ("market", "limit")),
            "limit_price": lambda annotation: set(get_args(annotation)) == {float, type(None)},
            "tag": lambda annotation: set(get_args(annotation)) == {str, type(None)},
        },
    )


def test_tick_event_matches_l2_snapshot_contract() -> None:
    tick_event_fields = fields(TickEvent)

    assert tuple(field.name for field in tick_event_fields) == (
        "timestamp",
        "symbol",
        "bids",
        "asks",
        "last",
        "last_size",
    )
    assert_required_fields(tick_event_fields[:-1])
    assert_optional_none_fields((tick_event_fields[-1],))

    hints = get_type_hints(TickEvent)
    assert hints["timestamp"] is int
    assert hints["symbol"] is str
    assert hints["last"] is float
    assert set(get_args(hints["last_size"])) == {float, type(None)}
    assert_l2_snapshot_annotation(hints["bids"])
    assert_l2_snapshot_annotation(hints["asks"])

    tick = TickEvent(
        timestamp=1,
        symbol="BTC/USDT",
        bids=((101.0, 2.0), (100.5, 1.5)),
        asks=((101.5, 1.0),),
        last=101.25,
    )

    assert all(len(level) == 2 for level in tick.bids)
    assert all(len(level) == 2 for level in tick.asks)


def test_bar_event_matches_backtest_mvp_minimum_contract() -> None:
    bar_event_fields = fields(BarEvent)

    assert_dataclass_includes_fields(
        bar_event_fields,
        required=(
            "bar_type",
            "bar_spec",
            "symbol",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "is_closed",
        ),
    )

    hints = get_type_hints(BarEvent)
    assert_field_type_hints(
        hints,
        exact={
            "bar_type": str,
            "bar_spec": object,
            "symbol": str,
            "timestamp": int,
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float,
            "is_closed": bool,
        },
    )


def test_fill_event_matches_backtest_mvp_minimum_contract() -> None:
    fill_event_fields = fields(FillEvent)

    assert_dataclass_includes_fields(
        fill_event_fields,
        required=(
            "symbol",
            "side",
            "quantity",
            "price",
            "timestamp",
            "fee",
        ),
    )

    hints = get_type_hints(FillEvent)
    assert_field_type_hints(
        hints,
        exact={
            "symbol": str,
            "quantity": float,
            "price": float,
            "timestamp": int,
            "fee": float,
        },
        predicates={
            "side": lambda annotation: get_origin_and_args(annotation)
            == (Literal, ("buy", "sell")),
        },
    )


def test_cost_config_matches_injected_backtest_mvp_cost_inputs() -> None:
    cost_config_fields = fields(CostConfig)

    assert_dataclass_includes_fields(
        cost_config_fields,
        required=("tick_size", "slippage_ticks", "fee_rate"),
    )

    assert_field_type_hints(
        get_type_hints(CostConfig),
        exact={
            "tick_size": float,
            "slippage_ticks": float,
            "fee_rate": float,
        },
    )


def test_order_and_timer_events_remain_absent_from_slice_1_trading_surface() -> None:
    expected_public_event_types = {"TickEvent", "BarEvent", "FillEvent"}
    deferred_event_types = {"OrderEvent", "TimerEvent"}
    exported_event_types = {name for name in trading_domain_exports if name.endswith("Event")}
    module_event_types = {
        name
        for name, value in vars(trading_events).items()
        if name.endswith("Event") and not name.startswith("_") and isinstance(value, type)
    }

    assert exported_event_types == expected_public_event_types
    assert module_event_types == expected_public_event_types
    assert deferred_event_types.isdisjoint(exported_event_types)
    assert deferred_event_types.isdisjoint(module_event_types)


def get_origin_and_args(annotation: object) -> tuple[object | None, tuple[object, ...]]:
    from typing import get_origin

    return get_origin(annotation), get_args(annotation)


def assert_l2_snapshot_annotation(annotation: object) -> None:
    origin, args = get_origin_and_args(annotation)

    assert origin is tuple
    assert len(args) == 2
    assert args[1] is Ellipsis
    assert get_origin_and_args(args[0]) == (tuple, (float, float))


def assert_required_fields(contract_fields: tuple[object, ...]) -> None:
    for field in contract_fields:
        assert field.default is MISSING
        assert field.default_factory is MISSING


def assert_optional_none_fields(contract_fields: tuple[object, ...]) -> None:
    for field in contract_fields:
        assert field.default is None
        assert field.default_factory is MISSING


def assert_dataclass_includes_fields(
    contract_fields: tuple[Field[object], ...],
    *,
    required: tuple[str, ...] = (),
    optional_none: tuple[str, ...] = (),
) -> None:
    fields_by_name = {field.name: field for field in contract_fields}

    assert set(required) <= fields_by_name.keys()
    assert set(optional_none) <= fields_by_name.keys()
    assert_required_fields(tuple(fields_by_name[name] for name in required))
    assert_optional_none_fields(tuple(fields_by_name[name] for name in optional_none))


def assert_field_type_hints(
    hints: dict[str, object],
    *,
    exact: dict[str, object],
    predicates: dict[str, Callable[[object], bool]] | None = None,
) -> None:
    for field_name, expected_annotation in exact.items():
        assert hints[field_name] is expected_annotation

    for field_name, predicate in (predicates or {}).items():
        message = f"unexpected annotation for {field_name}: {hints[field_name]!r}"
        assert predicate(hints[field_name]), message
