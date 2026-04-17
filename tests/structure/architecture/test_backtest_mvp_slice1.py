from __future__ import annotations

import importlib
import pkgutil
import re
from pathlib import Path
from types import ModuleType

import quantcraft.research as research_package
import quantcraft.trading.domain as trading_domain_package
from quantcraft.trading.domain import __all__ as trading_domain_exports
from quantcraft.trading.domain import events as trading_events
from scripts import check_architecture
from tests.support import ROOT


def test_backtest_mvp_spec_marks_order_and_timer_events_as_deferred() -> None:
    spec_text = (ROOT / "docs" / "product-specs" / "backtest-mvp.md").read_text(encoding="utf-8")

    event_contract = parse_engine_and_events_contract(spec_text)

    assert event_contract["implemented"] == {"TickEvent", "BarEvent", "FillEvent"}
    assert {"OrderEvent", "TimerEvent"} <= event_contract["deferred"]
    assert event_contract["implemented"].isdisjoint({"OrderEvent", "TimerEvent"})


def test_current_package_skeletons_exist() -> None:
    expected_paths = (
        Path("src/quantcraft/data/__init__.py"),
        Path("src/quantcraft/data/adapters/__init__.py"),
        Path("src/quantcraft/research/__init__.py"),
        Path("src/quantcraft/research/strategy.py"),
        Path("src/quantcraft/backtest/__init__.py"),
        Path("src/quantcraft/integrations/venues/ccxt/__init__.py"),
        Path("src/quantcraft/trading/domain/__init__.py"),
    )

    for relative_path in expected_paths:
        assert (ROOT / relative_path).exists(), f"missing package skeleton: {relative_path}"


def test_research_to_trading_dependency_is_allowed() -> None:
    assert check_architecture.validate_domain_dependency("research", "trading") is None


def test_trading_to_research_dependency_is_rejected() -> None:
    issue = check_architecture.validate_domain_dependency("trading", "research")

    assert issue == "Cross-domain dependency violation: trading cannot depend on research"


def test_research_public_surface_exposes_slice_1_entrypoints() -> None:
    assert set(research_package.__all__) == {
        "Strategy",
        "ta",
        "qc",
    }


def test_slice_1_public_trading_surface_excludes_deferred_event_types() -> None:
    spec_text = (ROOT / "docs" / "product-specs" / "backtest-mvp.md").read_text(encoding="utf-8")
    event_contract = parse_engine_and_events_contract(spec_text)

    exported_event_types = {name for name in trading_domain_exports if name.endswith("Event")}
    module_event_types = {
        name
        for name, value in vars(trading_events).items()
        if name.endswith("Event") and not name.startswith("_") and isinstance(value, type)
    }
    public_definition_types = collect_importable_public_event_definitions()
    public_surface_types = collect_importable_public_event_surface()

    assert exported_event_types == event_contract["implemented"]
    assert module_event_types == event_contract["implemented"]
    assert public_definition_types == event_contract["implemented"]
    assert public_surface_types == event_contract["implemented"]
    assert event_contract["deferred"].isdisjoint(exported_event_types)
    assert event_contract["deferred"].isdisjoint(module_event_types)
    assert event_contract["deferred"].isdisjoint(public_definition_types)
    assert event_contract["deferred"].isdisjoint(public_surface_types)


def parse_engine_and_events_contract(spec_text: str) -> dict[str, set[str]]:
    section_lines = extract_markdown_section_matching(spec_text, ("engine", "event"))
    event_contract = {"implemented": set(), "deferred": set()}
    current_group: str | None = None

    for line in section_lines:
        bullet_match = re.match(r"^\s*[-*]\s+(.*)$", line)
        if bullet_match:
            bullet_text = bullet_match.group(1).strip().lower()
            if "implemented" in bullet_text and "event" in bullet_text:
                current_group = "implemented"
            elif "deferred" in bullet_text and "event" in bullet_text:
                current_group = "deferred"
            elif current_group is not None:
                event_names = extract_event_names_from_list_bullet(bullet_match.group(1))
                if event_names is not None:
                    event_contract[current_group].update(event_names)
                else:
                    current_group = None

    assert event_contract["implemented"], "missing implemented event set in Engine And Events"
    assert event_contract["deferred"], "missing deferred event set in Engine And Events"
    return event_contract


def extract_markdown_section_matching(spec_text: str, heading_terms: tuple[str, ...]) -> list[str]:
    lines = spec_text.splitlines()
    in_section = False
    collected: list[str] = []

    for line in lines:
        if in_section and re.match(r"^##+\s+", line):
            break
        if in_section:
            collected.append(line)
        elif heading_matches_terms(line, heading_terms):
            in_section = True

    assert collected, f"missing markdown section matching: {heading_terms}"
    return collected


def heading_matches_terms(line: str, heading_terms: tuple[str, ...]) -> bool:
    heading_match = re.match(r"^##+\s+(.*)$", line)
    if heading_match is None:
        return False

    heading_text = heading_match.group(1).lower()
    return all(term in heading_text for term in heading_terms)


def collect_importable_public_event_definitions() -> set[str]:
    return {
        name
        for module in iter_importable_trading_domain_modules()
        for name, value in vars(module).items()
        if is_public_event_type(name, value)
        and getattr(value, "__module__", None) == module.__name__
    }


def collect_importable_public_event_surface() -> set[str]:
    return {
        name
        for module in iter_importable_trading_domain_modules()
        for name, value in vars(module).items()
        if is_public_event_type(name, value)
    }


def iter_importable_trading_domain_modules() -> tuple[ModuleType, ...]:
    modules = [trading_domain_package]
    module_infos = sorted(
        pkgutil.iter_modules(
            trading_domain_package.__path__,
            prefix=f"{trading_domain_package.__name__}.",
        ),
        key=lambda module_info: module_info.name,
    )
    modules.extend(importlib.import_module(module_info.name) for module_info in module_infos)
    return tuple(modules)


def is_public_event_type(name: str, value: object) -> bool:
    return name.endswith("Event") and not name.startswith("_") and isinstance(value, type)


def extract_event_names_from_list_bullet(bullet_text: str) -> set[str] | None:
    event_names = set(re.findall(r"`([A-Z][A-Za-z0-9]*Event)`", bullet_text))
    if not event_names:
        return None

    remainder = re.sub(r"`[A-Z][A-Za-z0-9]*Event`", "", bullet_text)
    remainder = re.sub(r"[\s,;/()-]+", "", remainder)
    return event_names if remainder == "" else None
