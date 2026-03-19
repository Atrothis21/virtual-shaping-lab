from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRAM_DIR = ROOT / "virtual_shaping_lab" / "vsl" / "program"


def _iter_compiler_modules() -> list[Path]:
    return sorted(
        path
        for path in PROGRAM_DIR.rglob("*.py")
        if "__pycache__" not in path.parts and path.stem.endswith("compiler")
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


def test_v3_program_compilers_do_not_import_runtime_or_learner_layers():
    compiler_modules = _iter_compiler_modules()
    assert compiler_modules, "Expected at least one v3 program compiler module."

    forbidden_prefixes = (
        "agents",
        "protocols",
        "analysis",
        "experiment",
        "virtual_shaping_lab.agents",
        "virtual_shaping_lab.protocols",
        "virtual_shaping_lab.analysis",
        "virtual_shaping_lab.experiment",
    )

    violations: list[tuple[str, str]] = []
    for path in compiler_modules:
        rel = str(path.relative_to(ROOT))
        for mod in _import_modules(path):
            if mod.startswith("typing") or mod.startswith("__future__"):
                continue
            if any(mod == prefix or mod.startswith(f"{prefix}.") for prefix in forbidden_prefixes):
                violations.append((rel, mod))

    assert not violations, f"V3 compiler purity import violations: {violations}"
