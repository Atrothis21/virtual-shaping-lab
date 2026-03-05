from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "virtual_shaping_lab"

# Intended target state:
# - factory internals are consumed by composition/adaptor seams only.
ALLOWED_IMPORTER_PATHS = {
    "experiment/assemble.py",
    "api/extensions.py",
    "tools/audit_registries.py",
}

PHASE_FACTORY_MODULES = {
    "experiment.factories.phase_factory",
    "virtual_shaping_lab.experiment.factories.phase_factory",
}


def _iter_python_files(base: Path):
    for path in base.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _import_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.add(node.module)
                if node.module in {"experiment.factories", "virtual_shaping_lab.experiment.factories"}:
                    for alias in node.names:
                        # Treat "from ...factories import phase_factory" as direct phase_factory usage.
                        imported_name = alias.name
                        if imported_name == "phase_factory":
                            out.add(f"{node.module}.phase_factory")
    return out


def test_factory_boundary_usage_guard():
    violations: list[tuple[str, str]] = []
    phase_factory_violations: list[tuple[str, str]] = []
    for path in _iter_python_files(ROOT):
        rel = path.relative_to(ROOT).as_posix()
        imports = _import_modules(path)
        for mod in imports:
            if mod in PHASE_FACTORY_MODULES:
                phase_factory_violations.append((rel, mod))
            if mod == "experiment.factories" or mod.startswith("experiment.factories."):
                if rel not in ALLOWED_IMPORTER_PATHS:
                    violations.append((rel, mod))
            if mod == "virtual_shaping_lab.experiment.factories" or mod.startswith("virtual_shaping_lab.experiment.factories."):
                if rel not in ALLOWED_IMPORTER_PATHS:
                    violations.append((rel, mod))

    assert not phase_factory_violations, (
        "Direct phase_factory imports are forbidden; use experiment.phases.public "
        f"or experiment.phases.catalog_runtime. Violations: {sorted(phase_factory_violations)}"
    )
    assert not violations, f"factory_boundary_usage violations: {sorted(violations)}"
