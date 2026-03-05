from __future__ import annotations

import ast
import os
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2] / "virtual_shaping_lab"
STRICT = os.getenv("V2_11_GUARDS_STRICT", "0") == "1"

# Intended target state:
# - factory internals are consumed by composition/adaptor seams only.
ALLOWED_IMPORTER_PATHS = {
    "experiment/assemble.py",
    "api/extensions.py",
    "tools/audit_registries.py",
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
    return out


def _assert_or_soft_xfail(*, violations: list[tuple[str, str]], guard_name: str):
    if violations and not STRICT:
        pytest.xfail(
            f"[soft-guard:{guard_name}] violations found (non-blocking until strict mode): {violations}"
        )
    assert not violations, f"{guard_name} violations: {violations}"


def test_factory_boundary_usage_guard():
    violations: list[tuple[str, str]] = []
    for path in _iter_python_files(ROOT):
        rel = path.relative_to(ROOT).as_posix()
        imports = _import_modules(path)
        for mod in imports:
            if mod == "experiment.factories" or mod.startswith("experiment.factories."):
                if rel not in ALLOWED_IMPORTER_PATHS:
                    violations.append((rel, mod))
            if mod == "virtual_shaping_lab.experiment.factories" or mod.startswith("virtual_shaping_lab.experiment.factories."):
                if rel not in ALLOWED_IMPORTER_PATHS:
                    violations.append((rel, mod))

    _assert_or_soft_xfail(
        violations=sorted(violations),
        guard_name="factory_boundary_usage",
    )
