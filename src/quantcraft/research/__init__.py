from __future__ import annotations

from importlib import import_module

__all__ = ["GridSearchResult", "GridSearchRow", "ParameterStudy", "Strategy", "qc", "ta"]


def __getattr__(name: str) -> object:
    if name == "Strategy":
        return getattr(import_module("quantcraft.research.strategy"), name)
    if name in {"GridSearchResult", "GridSearchRow", "ParameterStudy"}:
        return getattr(import_module("quantcraft.research.parameter_exploration"), name)
    if name in {"qc", "ta"}:
        return import_module(f"quantcraft.research.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
