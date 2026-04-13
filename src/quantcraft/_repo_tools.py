from __future__ import annotations

import ast
import re
import subprocess
import tomllib
from pathlib import Path
from typing import cast

REQUIRED_DOCS = (
    "README.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "docs/DESIGN.md",
    "docs/PLANS.md",
    "docs/RELIABILITY.md",
    "docs/SECURITY.md",
    "docs/design-docs/index.md",
    "docs/product-specs/index.md",
)

PLACEHOLDER_TOKENS = ("Add your description here",)
SUPPORTED_TEST_DIRS = ("unit", "integration", "structure", "smoke")

TIER_A = {"trading", "execution"}
TIER_B = {"data", "research"}
TIER_C = {"ml"}
SHARED_DOMAINS = {"shared"}
KNOWN_DOMAINS = TIER_A | TIER_B | TIER_C | SHARED_DOMAINS
ALLOWED_CROSS_DOMAIN_DEPENDENCIES = {
    ("research", "data"),
    ("research", "trading"),
    ("execution", "trading"),
}
ALLOWED_ROOT_MODULE_DEPENDENCIES = {
    ("quantcraft", "quantcraft.exchange"),
    ("quantcraft._repo_tools", "quantcraft.exchange"),
}

ROUTING_INDEX_COLUMNS = ("Task Area", "Document", "Role", "Scope", "Read When")
LEGACY_INDEX_STATUS_MAP_COLUMNS = (
    "Document",
    "Status",
    "Canonical",
    "Applicability",
    "Read When",
    "Notes",
)
ROUTING_INDEX_REQUIRED_FIELDS = ("task_area", "role", "scope", "read_when")
ROUTING_INDEX_CONFIG = {
    "docs/design-docs/index.md": {
        "directory": "docs/design-docs",
        "label": "design doc",
        "allowed_roles": {"Governing", "Draft"},
    },
    "docs/product-specs/index.md": {
        "directory": "docs/product-specs",
        "label": "product spec",
        "allowed_roles": {"Governing", "Pointer", "Future-only"},
    },
}
REQUIRED_POE_TASKS = (
    "lint",
    "format",
    "perf-check",
    "verify-runtime",
    "typecheck",
    "test",
    "test-unit",
    "test-integration",
    "test-structure",
    "test-smoke",
    "test-live",
    "coverage",
    "build",
    "repo-check",
    "notebook-validate",
    "live-smoke",
    "verify",
)


def git_has_head(root: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def git_untracked_paths(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {line for line in result.stdout.splitlines() if line}


def referenced_repo_paths(content: str) -> set[str]:
    pattern = re.compile(
        r"(docs/[^\s`)\]]+|notebooks/[^\s`)\]]+|tests/[^\s`)\]]+|src/[^\s`)\]]+|scripts/[^\s`)\]]+|AGENTS\.md|ARCHITECTURE\.md|README\.md|agent-development-guide-ko\.md|pyproject\.toml)"
    )
    return {match.group(1) for match in pattern.finditer(content)}


def missing_markdown_link_targets(doc_path: Path) -> list[str]:
    content = doc_path.read_text(encoding="utf-8")
    pattern = re.compile(r"\[[^\]]+\]\(([^)#]+)\)")
    missing: list[str] = []

    for match in pattern.finditer(content):
        target = match.group(1).strip()
        if not target or "://" in target:
            continue
        resolved = (doc_path.parent / target).resolve()
        if not resolved.exists():
            missing.append(target)

    return missing


def poe_executor_type(pyproject: dict[str, object]) -> str | None:
    tool_config = pyproject.get("tool")
    if not isinstance(tool_config, dict):
        return None

    poe_config = tool_config.get("poe")
    if not isinstance(poe_config, dict):
        return None

    executor = poe_config.get("executor")
    if isinstance(executor, str):
        return executor
    if isinstance(executor, dict):
        executor_type = executor.get("type")
        return executor_type if isinstance(executor_type, str) else None

    return None


def markdown_section(content: str, title: str) -> str | None:
    pattern = re.compile(
        rf"^## {re.escape(title)}\s*$\n(?P<body>.*?)(?=^##\s+\S|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    if match is None:
        return None
    return match.group("body").strip()


def parse_bullet_metadata_section(section: str | None) -> dict[str, str]:
    if section is None:
        return {}
    metadata: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"^\s*[-*]\s*([a-z_]+):\s*(.+?)\s*$", line)
        if match is None:
            continue
        key, value = match.groups()
        metadata[key] = value.strip()

    return metadata


def parse_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def find_markdown_table_lines(content: str, header_columns: tuple[str, ...]) -> list[str]:
    lines = [line.strip() for line in content.splitlines()]
    for index, line in enumerate(lines):
        if tuple(parse_markdown_row(line)) != header_columns:
            continue

        table_lines = [line]
        cursor = index + 1
        while cursor < len(lines):
            candidate = lines[cursor]
            if not candidate.startswith("|"):
                break
            table_lines.append(candidate)
            cursor += 1
        return table_lines

    return []


def parse_index_status_map_entries(content: str) -> tuple[list[dict[str, str]], list[str]]:
    table_lines = find_markdown_table_lines(content, LEGACY_INDEX_STATUS_MAP_COLUMNS)
    if len(table_lines) < 2:
        documents_section = markdown_section(content, "Documents")
        if documents_section is None:
            return [], []
        table_lines = [
            line.strip() for line in documents_section.splitlines() if line.strip().startswith("|")
        ]
        if len(table_lines) < 2:
            return [], []
        header = parse_markdown_row(table_lines[0])
        if tuple(header) != LEGACY_INDEX_STATUS_MAP_COLUMNS:
            return [], []

    entries: list[dict[str, str]] = []
    duplicates: list[str] = []
    seen_targets: set[str] = set()
    for line in table_lines[2:]:
        cells = parse_markdown_row(line)
        if len(cells) != len(LEGACY_INDEX_STATUS_MAP_COLUMNS):
            continue
        target_cell, status, canonical, applicability, read_when, notes = cells
        match = re.search(r"\(([^)#]+\.md)\)", target_cell)
        if match is None:
            stripped = target_cell.strip().strip("`")
            if stripped.endswith(".md"):
                target = stripped
            else:
                continue
        else:
            target = match.group(1).strip()
        if target in seen_targets:
            duplicates.append(target)
            continue
        seen_targets.add(target)
        entries.append(
            {
                "target": target,
                "status": status.strip(),
                "canonical": canonical.strip(),
                "applicability": applicability.strip(),
                "read_when": read_when.strip(),
                "notes": notes.strip(),
            }
        )

    return entries, duplicates


def parse_routing_index_entries(
    content: str,
    *,
    allowed_roles: set[str] | None = None,
) -> tuple[list[dict[str, str]], list[str]]:
    table_lines = find_markdown_table_lines(content, ROUTING_INDEX_COLUMNS)
    if len(table_lines) >= 2:
        entries: list[dict[str, str]] = []
        duplicates: list[str] = []
        seen_targets: set[str] = set()
        for line in table_lines[2:]:
            cells = parse_markdown_row(line)
            if len(cells) != len(ROUTING_INDEX_COLUMNS):
                continue
            task_area, target_cell, role, scope, read_when = cells
            match = re.search(r"\(([^)#]+\.md)\)", target_cell)
            if match is None:
                stripped = target_cell.strip().strip("`")
                if stripped.endswith(".md"):
                    target = stripped
                else:
                    continue
            else:
                target = match.group(1).strip()
            if target in seen_targets:
                duplicates.append(target)
                continue
            seen_targets.add(target)
            entries.append(
                {
                    "task_area": task_area.strip(),
                    "target": target,
                    "role": role.strip(),
                    "scope": scope.strip(),
                    "read_when": read_when.strip(),
                    "schema": "routing_index",
                }
            )
        return entries, duplicates

    legacy_entries, duplicates = parse_index_status_map_entries(content)
    normalized_entries: list[dict[str, str]] = []
    for entry in legacy_entries:
        role = normalize_legacy_routing_role(entry, allowed_roles=allowed_roles)

        normalized_entries.append(
            {
                "task_area": entry["notes"] or Path(entry["target"]).stem.replace("-", " "),
                "target": entry["target"],
                "role": role,
                "scope": entry["applicability"],
                "read_when": entry["read_when"],
                "schema": "legacy_status_map",
            }
        )

    return normalized_entries, duplicates


def normalize_legacy_routing_role(
    entry: dict[str, str],
    *,
    allowed_roles: set[str] | None = None,
) -> str:
    status = entry["status"].strip().lower()
    canonical = entry["canonical"].strip().lower()
    if canonical == "yes":
        return "Governing"
    if status == "draft":
        return "Draft"
    if status == "future":
        if allowed_roles is None or "Future-only" in allowed_roles:
            return "Future-only"
        return "Draft"
    if allowed_roles is None or "Pointer" in allowed_roles:
        return "Pointer"
    return "Draft"

def resolve_routing_index_target(root: Path, *, index_path: Path, target: str) -> str | None:
    relative_base = index_path.parent.relative_to(root)
    relative_path = (relative_base / target).as_posix()
    if relative_path.startswith("../"):
        return None
    return relative_path

def collect_doc_issues(root: Path) -> list[str]:
    issues: list[str] = []

    for relative_path in REQUIRED_DOCS:
        path = root / relative_path
        if not path.exists():
            issues.append(f"Missing required document: {relative_path}")
            continue

        content = path.read_text(encoding="utf-8").strip()
        if not content:
            issues.append(f"Required document is empty: {relative_path}")
            continue

        for token in PLACEHOLDER_TOKENS:
            if token in content:
                issues.append(f"Found placeholder content in {relative_path}: {token}")

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    if "## Setup" not in readme:
        issues.append("README.md is missing the setup section")
    if "uv run poe" not in readme:
        issues.append("README.md is missing uv run poe guidance")

    plans_doc_path = root / "docs/PLANS.md"
    plans_doc = plans_doc_path.read_text(encoding="utf-8") if plans_doc_path.exists() else ""
    required_plan_references = ("plans/", "plans/trials/")
    for required_reference in required_plan_references:
        if required_reference not in plans_doc:
            issues.append(f"docs/PLANS.md is missing plan reference: {required_reference}")
    if "Durable architecture or contract drafts do not belong in `docs/plans/`" not in plans_doc:
        issues.append("docs/PLANS.md is missing design-docs versus plans guidance")

    agents_path = root / "AGENTS.md"
    agents = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    if "uv run poe" not in agents:
        issues.append("AGENTS.md is missing uv run poe guidance")
    if "repo-local harness commands" not in agents:
        issues.append("AGENTS.md is missing repo-local harness command guidance")

    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.exists():
        issues.append("Missing pyproject.toml for Poe task checks")
    else:
        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        dev_dependencies = pyproject.get("dependency-groups", {}).get("dev", [])
        if not any(dependency.startswith("poethepoet") for dependency in dev_dependencies):
            issues.append("pyproject.toml is missing poethepoet in dependency-groups.dev")

        executor_type = poe_executor_type(pyproject)
        if executor_type != "uv":
            issues.append('pyproject.toml is missing Poe executor = "uv" configuration')

        poe_tasks = pyproject.get("tool", {}).get("poe", {}).get("tasks", {})
        for task_name in REQUIRED_POE_TASKS:
            if task_name not in poe_tasks:
                issues.append(f"Missing required Poe task: {task_name}")

    indexed_doc_dirs = (
        (
            "design-docs",
            (root / "docs" / "design-docs" / "index.md").read_text(encoding="utf-8")
            if (root / "docs" / "design-docs" / "index.md").exists()
            else "",
            "design doc",
        ),
        (
            "references",
            (root / "docs" / "references" / "index.md").read_text(encoding="utf-8")
            if (root / "docs" / "references" / "index.md").exists()
            else "",
            "reference doc",
        ),
        (
            "product-specs",
            (root / "docs" / "product-specs" / "index.md").read_text(encoding="utf-8")
            if (root / "docs" / "product-specs" / "index.md").exists()
            else "",
            "product spec",
        ),
        (
            "generated",
            (root / "docs" / "generated" / "index.md").read_text(encoding="utf-8")
            if (root / "docs" / "generated" / "index.md").exists()
            else "",
            "generated artifact",
        ),
    )
    for index_relative_path, config in ROUTING_INDEX_CONFIG.items():
        index_path = root / index_relative_path
        if not index_path.exists():
            continue

        content = index_path.read_text(encoding="utf-8")
        entries, duplicates = parse_routing_index_entries(
            content,
            allowed_roles=cast(set[str], config["allowed_roles"]),
        )
        if not entries:
            issues.append(f"{index_relative_path} is missing routing index table")

        for duplicate in duplicates:
            issues.append(f"{index_relative_path} has duplicate document row: {duplicate}")

        indexed_targets: set[str] = set()
        for entry in entries:
            target = entry["target"]
            resolved_target = resolve_routing_index_target(
                root,
                index_path=index_path,
                target=target,
            )
            if resolved_target is None:
                issues.append(
                    f"{index_relative_path} references document outside its directory: {target}"
                )
                continue
            if not (root / resolved_target).exists():
                issues.append(
                    f"{index_relative_path} references missing document: {resolved_target}"
                )
                continue

            indexed_targets.add(Path(resolved_target).name)
            if entry["role"] not in config["allowed_roles"]:
                issues.append(
                    f"{index_relative_path} has invalid Role field for document "
                    f"{Path(target).name}: {entry['role']}"
                )
            for field in ROUTING_INDEX_REQUIRED_FIELDS:
                if entry[field]:
                    continue
                label = field.replace("_", " ").title()
                issues.append(
                    f"{index_relative_path} has blank {label} field for document: "
                    f"{Path(target).name}"
                )

        directory = root / cast(str, config["directory"])
        if directory.exists():
            for path in sorted(directory.glob("*.md")):
                if path.name == "index.md":
                    continue
                if path.name not in indexed_targets:
                    issues.append(
                        f"{index_relative_path} is missing {cast(str, config['label'])}: "
                        f"{path.name}"
                    )

    for directory_name, index_content, label in indexed_doc_dirs:
        directory = root / "docs" / directory_name
        if not directory.exists():
            continue
        if f"docs/{directory_name}/index.md" in ROUTING_INDEX_CONFIG:
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name == "index.md":
                continue
            if path.name not in index_content:
                issues.append(f"docs/{directory_name}/index.md is missing {label}: {path.name}")

    architecture_doc_path = root / "ARCHITECTURE.md"
    architecture_doc = (
        architecture_doc_path.read_text(encoding="utf-8") if architecture_doc_path.exists() else ""
    )
    if "docs/design-docs/" not in architecture_doc:
        issues.append("ARCHITECTURE.md is missing a design-docs architecture reference")
    if "docs/plans/2026-03-18-quantcraft-architecture-draft-ko.md" in architecture_doc:
        issues.append("ARCHITECTURE.md still references the old plan-path architecture draft")

    old_architecture_draft = (
        root / "docs" / "plans" / "2026-03-18-quantcraft-architecture-draft-ko.md"
    )
    if old_architecture_draft.exists():
        issues.append("Old plan-path Korean architecture draft should not exist")

    linked_index_docs = (
        root / "ARCHITECTURE.md",
        root / "docs" / "DESIGN.md",
        root / "docs" / "PLANS.md",
        root / "docs" / "design-docs" / "index.md",
        root / "docs" / "references" / "index.md",
        root / "docs" / "product-specs" / "index.md",
        root / "docs" / "generated" / "index.md",
    )
    for doc_path in linked_index_docs:
        if not doc_path.exists():
            continue
        for target in missing_markdown_link_targets(doc_path):
            issues.append(f"{doc_path.relative_to(root)} points to missing target: {target}")

    tests_dir = root / "tests"
    if tests_dir.exists():
        for supported_dir in SUPPORTED_TEST_DIRS:
            if not (tests_dir / supported_dir).exists():
                issues.append(f"Missing test taxonomy directory: tests/{supported_dir}")

        for path in sorted(tests_dir.glob("test_*.py")):
            issues.append(
                f"Found flat root-level test file outside taxonomy: tests/{path.name}",
            )

    return issues


def collect_doc_advisories(root: Path) -> list[str]:
    if not git_has_head(root):
        return []

    advisories: list[str] = []
    architecture_path = root / "ARCHITECTURE.md"
    plans_path = root / "docs" / "PLANS.md"
    architecture_doc = (
        architecture_path.read_text(encoding="utf-8") if architecture_path.exists() else ""
    )
    plans_doc = plans_path.read_text(encoding="utf-8") if plans_path.exists() else ""
    indexed_doc_dir_names = ("design-docs", "references", "product-specs", "generated")

    referenced_paths: set[str] = set()
    for content in (architecture_doc, plans_doc):
        referenced_paths.update(referenced_repo_paths(content))

    for directory_name in indexed_doc_dir_names:
        directory = root / "docs" / directory_name
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name == "index.md":
                continue
            referenced_paths.add(path.relative_to(root).as_posix())

    untracked_paths = git_untracked_paths(root)
    for relative_path in sorted(referenced_paths):
        if relative_path in untracked_paths and (root / relative_path).exists():
            advisories.append(f"Indexed artifact is untracked: {relative_path}")

    return advisories


def domain_for_module_parts(parts: tuple[str, ...]) -> str | None:
    if len(parts) < 2 or parts[0] != "quantcraft":
        return None

    candidate = parts[1]
    return candidate if candidate in KNOWN_DOMAINS else None


def module_name_for_parts(parts: tuple[str, ...]) -> str | None:
    if not parts:
        return None

    normalized_parts = parts[:-1] if parts[-1] == "__init__" else parts
    if not normalized_parts:
        return None

    return ".".join(normalized_parts)


def root_non_domain_module_for_parts(parts: tuple[str, ...]) -> str | None:
    if len(parts) < 2 or parts[0] != "quantcraft":
        return None

    if parts[1] in KNOWN_DOMAINS:
        return None

    return ".".join(parts[:2])


def validate_domain_dependency(source_domain: str | None, target_domain: str | None) -> str | None:
    if source_domain is None or target_domain is None:
        return None

    if source_domain == target_domain or target_domain in SHARED_DOMAINS:
        return None

    if (source_domain, target_domain) in ALLOWED_CROSS_DOMAIN_DEPENDENCIES:
        return None

    if target_domain in TIER_A and source_domain not in TIER_A:
        return f"Tier A boundary violation: {source_domain} cannot depend on {target_domain}"

    return f"Cross-domain dependency violation: {source_domain} cannot depend on {target_domain}"


def validate_root_module_dependency(
    source_module_parts: tuple[str, ...],
    source_domain: str | None,
    target_parts: tuple[str, ...],
) -> str | None:
    source_module = module_name_for_parts(source_module_parts)
    target_root_module = root_non_domain_module_for_parts(target_parts)

    if source_module is None or target_root_module is None:
        return None

    if source_module == target_root_module or source_module.startswith(f"{target_root_module}."):
        return None

    if (source_module, target_root_module) in ALLOWED_ROOT_MODULE_DEPENDENCIES:
        return None

    source_label = source_domain or source_module
    return (
        "Root-level module dependency violation: "
        f"{source_label} cannot depend on {target_root_module}"
    )


def resolve_import_from_module_parts(
    source_module_parts: tuple[str, ...], node: ast.ImportFrom
) -> tuple[str, ...] | None:
    if node.level == 0:
        return tuple(node.module.split(".")) if node.module is not None else None

    current_package_parts = source_module_parts[:-1]
    levels_up = node.level - 1
    if levels_up > len(current_package_parts):
        return None

    base_parts = current_package_parts[: len(current_package_parts) - levels_up]
    if node.module is None:
        return base_parts

    return base_parts + tuple(node.module.split("."))


def import_targets_for_node(
    source_module_parts: tuple[str, ...], node: ast.ImportFrom
) -> tuple[tuple[str, ...], ...]:
    base_parts = resolve_import_from_module_parts(source_module_parts, node)
    if base_parts is None:
        return ()

    if domain_for_module_parts(base_parts) is not None:
        return (base_parts,)

    targets = []
    for alias in node.names:
        if alias.name == "*":
            targets.append(base_parts)
            continue
        targets.append(base_parts + tuple(alias.name.split(".")))
    return tuple(targets)


def collect_architecture_issues(root: Path) -> list[str]:
    src_root = root / "src" / "quantcraft"
    if not src_root.exists():
        return ["Missing src/quantcraft package root"]

    issues: list[str] = []

    for path in src_root.rglob("*.py"):
        module_parts = ("quantcraft",) + path.relative_to(src_root).with_suffix("").parts
        source_domain = domain_for_module_parts(module_parts)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

        for node in ast.walk(tree):
            target_parts: tuple[str, ...] | None = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target_parts = tuple(alias.name.split("."))
                    issue = validate_domain_dependency(
                        source_domain,
                        domain_for_module_parts(target_parts),
                    )
                    if issue is not None:
                        issues.append(f"{path}: {issue}")
                    issue = validate_root_module_dependency(
                        module_parts,
                        source_domain,
                        target_parts,
                    )
                    if issue is not None:
                        issues.append(f"{path}: {issue}")
            elif isinstance(node, ast.ImportFrom):
                for target_parts in import_targets_for_node(module_parts, node):
                    issue = validate_domain_dependency(
                        source_domain,
                        domain_for_module_parts(target_parts),
                    )
                    if issue is not None:
                        issues.append(f"{path}: {issue}")
                    issue = validate_root_module_dependency(
                        module_parts,
                        source_domain,
                        target_parts,
                    )
                    if issue is not None:
                        issues.append(f"{path}: {issue}")

    return sorted(set(issues))


def run_live_smoke() -> list[str]:
    from quantcraft.exchange import Exchange, MarketType

    cases = [
        ("binance", MarketType.SPOT, "BTC/USDT"),
        ("binance", MarketType.USDM, "BTC/USDT:USDT"),
        ("bybit", MarketType.SPOT, "BTC/USDT"),
        ("bitget", MarketType.SPOT, "BTC/USDT"),
    ]

    results: list[str] = []
    for name, market_type, symbol in cases:
        rows = Exchange(name=name, market_type=market_type).fetch_ohlcv(
            symbol=symbol,
            timeframe="1h",
            limit=3,
        )
        if not rows:
            raise RuntimeError(f"Live smoke returned no rows for {name} {market_type}")
        results.append(f"{name}:{market_type}:{len(rows)}")

    return results
