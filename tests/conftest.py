from __future__ import annotations

import pytest

from tests.support import ensure_repo_root_on_path

ensure_repo_root_on_path()


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="run live tests under tests/smoke/live",
    )
    parser.addoption(
        "--run-perf",
        action="store_true",
        default=False,
        help="run performance tests under tests/perf",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    _apply_explicit_only_skips(
        items,
        skip_live=not _should_run_live(config),
        skip_perf=not _should_run_perf(config),
    )


def _selected_path(config: pytest.Config, fragment: str) -> bool:
    return any(fragment in str(arg) for arg in config.invocation_params.args)


def _should_run_live(config: pytest.Config) -> bool:
    return config.getoption("--run-live") or _selected_path(config, "tests/smoke/live")


def _should_run_perf(config: pytest.Config) -> bool:
    return config.getoption("--run-perf") or _selected_path(config, "tests/perf")


def _apply_explicit_only_skips(
    items: list[pytest.Item],
    *,
    skip_live: bool,
    skip_perf: bool,
) -> None:
    skip_live_marker = pytest.mark.skip(reason="live tests are explicit-only")
    skip_perf_marker = pytest.mark.skip(reason="performance tests are explicit-only")

    for item in items:
        if skip_live and "live" in item.keywords:
            item.add_marker(skip_live_marker)
        if skip_perf and "tests/perf/" in item.nodeid:
            item.add_marker(skip_perf_marker)
