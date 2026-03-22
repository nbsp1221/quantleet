import tomllib

from tests.support import ROOT


def test_pytest_markers_are_registered() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    marker_entries = pyproject["tool"]["pytest"]["ini_options"]["markers"]

    for marker_name in ["unit", "integration", "structure", "smoke", "live", "slow"]:
        assert any(entry.startswith(f"{marker_name}:") for entry in marker_entries)


def test_repository_guidance_excludes_live_tests_from_default_lane() -> None:
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    assert "live tests" in agents or "live tests" in readme
    assert "default" in agents or "default" in readme
    assert "exclude" in agents or "exclude" in readme
