from __future__ import annotations

from quantleet.backtest.order_activation import OrderActivationPolicy


def test_policy_activates_only_on_new_tick_timestamp() -> None:
    policy = OrderActivationPolicy()

    assert policy.begin_tick(60) is True
    assert policy.begin_tick(60) is False
    assert policy.begin_tick(120) is True
    assert policy.begin_tick(120) is False


def test_policy_reset_restores_first_tick_activation() -> None:
    policy = OrderActivationPolicy()

    assert policy.begin_tick(60) is True
    assert policy.begin_tick(60) is False

    policy.reset()

    assert policy.begin_tick(60) is True
