import pytest

from quantcraft._repo_tools import run_live_smoke

pytestmark = pytest.mark.live


def test_exchange_live_smoke() -> None:
    results = run_live_smoke()

    assert results
