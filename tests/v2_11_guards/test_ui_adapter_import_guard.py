from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "virtual_shaping_lab"
UI_ADAPTER_PATHS = [ROOT / "api" / "extensions.py"]
FORBIDDEN_RUNTIME_IMPORTS = (
    "experiment.runner",
    "experiment.trial_executor",
    "experiment.runtime_records",
    "experiment.sinks",
    "experiment.hooks",
    "virtual_shaping_lab.experiment.runner",
    "virtual_shaping_lab.experiment.trial_executor",
    "virtual_shaping_lab.experiment.runtime_records",
    "virtual_shaping_lab.experiment.sinks",
    "virtual_shaping_lab.experiment.hooks",
)


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


def test_ui_adapter_import_guard_disallows_runtime_internal_imports():
    violations: list[tuple[str, str]] = []
    for path in UI_ADAPTER_PATHS:
        rel = path.relative_to(ROOT).as_posix()
        for mod in _import_modules(path):
            if any(mod == p or mod.startswith(f"{p}.") for p in FORBIDDEN_RUNTIME_IMPORTS):
                violations.append((rel, mod))
    assert not violations, f"UI adapter runtime-import violations: {sorted(violations)}"
