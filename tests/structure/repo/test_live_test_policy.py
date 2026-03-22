from tests.support import ROOT


def test_conftest_declares_explicit_live_test_policy() -> None:
    conftest = (ROOT / "tests/conftest.py").read_text(encoding="utf-8")

    assert "--run-live" in conftest
    assert "tests/smoke/live" in conftest
