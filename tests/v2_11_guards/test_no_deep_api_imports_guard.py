from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "virtual_shaping_lab"

FORBIDDEN_DEEP_IMPORTS = (
    "experiment.assemble",
    "experiment.config",
    "experiment.runner",
    "analysis.registry",
    "analysis.report.catalog",
    "analysis.report.report",
    "virtual_shaping_lab.experiment.assemble",
    "virtual_shaping_lab.experiment.config",
    "virtual_shaping_lab.experiment.runner",
    "virtual_shaping_lab.analysis.registry",
    "virtual_shaping_lab.analysis.report.catalog",
    "virtual_shaping_lab.analysis.report.report",
)


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


def _collect_violations(paths: list[Path], forbidden_prefixes: tuple[str, ...]) -> list[tuple[str, str]]:
    bad: list[tuple[str, str]] = []
    for path in paths:
        for mod in _import_modules(path):
            if mod.startswith("typing") or mod.startswith("__future__"):
                continue
            if any(mod == p or mod.startswith(f"{p}.") for p in forbidden_prefixes):
                bad.append((str(path.relative_to(ROOT)), mod))
    return sorted(bad)


def test_no_deep_api_imports_guard():
    api_paths = list(_iter_python_files(ROOT / "api"))
    violations = _collect_violations(api_paths, FORBIDDEN_DEEP_IMPORTS)
    assert not violations, f"no_deep_api_imports violations: {violations}"
