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


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if config.getoption("--run-live"):
        return

    selected_live_path = any(
        "tests/smoke/live" in str(arg) for arg in config.invocation_params.args
    )
    if selected_live_path:
        return

    skip_live = pytest.mark.skip(reason="live tests are explicit-only")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)
