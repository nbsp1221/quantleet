from __future__ import annotations

from time import perf_counter

import pytest

from tests.support_backtest import load_canonical_rsi_bars, run_canonical_rsi_backtest

FIRST_RUN_THRESHOLD_SECONDS = 1.0
STEADY_STATE_THRESHOLD_SECONDS = 1.0
STEADY_STATE_ROUNDS = 5


def _assert_canonical_result_shape(result) -> None:
    assert result.summary.total_trades == 118
    assert result.summary.total_fills == 236
    assert result.summary.final_equity == pytest.approx(1_038_523.5766)


@pytest.mark.slow
def test_rsi_backtest_first_run_is_within_threshold() -> None:
    bars = load_canonical_rsi_bars()

    first_run_started_at = perf_counter()
    first_result = run_canonical_rsi_backtest(bars)
    first_run_seconds = perf_counter() - first_run_started_at

    _assert_canonical_result_shape(first_result)

    assert first_run_seconds < FIRST_RUN_THRESHOLD_SECONDS, (
        "canonical RSI first-run runtime exceeded the perf gate: "
        f"{first_run_seconds:.6f}s >= {FIRST_RUN_THRESHOLD_SECONDS:.1f}s"
    )


@pytest.mark.slow
def test_rsi_backtest_steady_state_median_is_within_threshold(benchmark) -> None:
    bars = load_canonical_rsi_bars()

    steady_result = benchmark.pedantic(
        run_canonical_rsi_backtest,
        args=(bars,),
        rounds=STEADY_STATE_ROUNDS,
        iterations=1,
        warmup_rounds=0,
    )

    _assert_canonical_result_shape(steady_result)
    steady_state_median = benchmark.stats.stats.median

    assert steady_state_median < STEADY_STATE_THRESHOLD_SECONDS, (
        "canonical RSI steady-state median runtime exceeded the perf gate: "
        f"{steady_state_median:.6f}s >= {STEADY_STATE_THRESHOLD_SECONDS:.1f}s"
    )
