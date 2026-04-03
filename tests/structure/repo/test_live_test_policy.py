from types import SimpleNamespace

import pytest

from tests import conftest as root_conftest
from tests.support import ROOT


def test_conftest_declares_explicit_live_test_policy() -> None:
    conftest = (ROOT / "tests/conftest.py").read_text(encoding="utf-8")

    assert "--run-live" in conftest
    assert "tests/smoke/live" in conftest


def test_conftest_declares_explicit_perf_test_policy() -> None:
    conftest = (ROOT / "tests/conftest.py").read_text(encoding="utf-8")

    assert "--run-perf" in conftest
    assert "tests/perf" in conftest


class _FakeConfig:
    def __init__(
        self,
        *,
        run_live: bool = False,
        run_perf: bool = False,
        args: tuple[str, ...] = (),
    ) -> None:
        self._options = {
            "--run-live": run_live,
            "--run-perf": run_perf,
        }
        self.invocation_params = SimpleNamespace(args=args)

    def getoption(self, name: str) -> bool:
        return self._options[name]


class _FakeItem:
    def __init__(self, *, nodeid: str, live: bool = False) -> None:
        self.nodeid = nodeid
        self.keywords = {"live": True} if live else {}
        self.markers: list[pytest.MarkDecorator] = []

    def add_marker(self, marker: pytest.MarkDecorator) -> None:
        self.markers.append(marker)

    def has_skip_reason(self, reason: str) -> bool:
        return any(
            mark.name == "skip" and mark.kwargs.get("reason") == reason for mark in self.markers
        )


def test_default_collection_skips_live_and_perf_items() -> None:
    items = [
        _FakeItem(nodeid="tests/smoke/live/test_exchange_live_smoke.py::test_example", live=True),
        _FakeItem(nodeid="tests/perf/test_rsi_backtest_benchmark.py::test_example"),
    ]

    root_conftest.pytest_collection_modifyitems(_FakeConfig(), items)

    assert items[0].has_skip_reason("live tests are explicit-only")
    assert items[1].has_skip_reason("performance tests are explicit-only")


def test_live_explicit_run_still_skips_perf_items() -> None:
    items = [
        _FakeItem(nodeid="tests/smoke/live/test_exchange_live_smoke.py::test_example", live=True),
        _FakeItem(nodeid="tests/perf/test_rsi_backtest_benchmark.py::test_example"),
    ]

    root_conftest.pytest_collection_modifyitems(
        _FakeConfig(run_live=True),
        items,
    )

    assert not items[0].has_skip_reason("live tests are explicit-only")
    assert items[1].has_skip_reason("performance tests are explicit-only")


def test_perf_explicit_run_still_skips_live_items() -> None:
    items = [
        _FakeItem(nodeid="tests/smoke/live/test_exchange_live_smoke.py::test_example", live=True),
        _FakeItem(nodeid="tests/perf/test_rsi_backtest_benchmark.py::test_example"),
    ]

    root_conftest.pytest_collection_modifyitems(
        _FakeConfig(run_perf=True),
        items,
    )

    assert items[0].has_skip_reason("live tests are explicit-only")
    assert not items[1].has_skip_reason("performance tests are explicit-only")
