import tomllib

from tests.support import ROOT


def test_public_beta_package_metadata() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]

    assert project["name"] == "quantcraft"
    assert project["version"] == "0.1.0b1"
    assert project["requires-python"] == ">=3.13"
    assert project["license"] == "MIT"
    assert "Single-symbol Python backtesting" in project["description"]

    assert set(project["keywords"]) >= {"quant", "backtesting", "research", "trading", "finance"}
    assert set(project["classifiers"]) >= {
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Typing :: Typed",
    }

    urls = project["urls"]
    assert urls["Homepage"] == "https://github.com/nbsp1221/quantcraft"
    assert urls["Repository"] == "https://github.com/nbsp1221/quantcraft"
    assert urls["Issues"] == "https://github.com/nbsp1221/quantcraft/issues"
    assert urls["Changelog"] == "https://github.com/nbsp1221/quantcraft/blob/dev/CHANGELOG.md"
    assert "Documentation" not in urls
