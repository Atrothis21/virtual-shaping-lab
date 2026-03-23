from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

from ui.contracts.operator_selection_compiler import (
    OperatorSelectionCompilerError,
    compile_operator_selection_artifact,
)
from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE
from ui.contracts.preset_registry import get_preset_registry


def _contracts_root() -> Path:
    return Path(__file__).resolve().parents[1] / "virtual_shaping_lab" / "ui" / "contracts"


def _compiler_files() -> list[Path]:
    root = _contracts_root()
    return [
        root / "operator_legality_engine.py",
        root / "operator_selection_compiler.py",
        root / "operator_plan_materialization.py",
    ]


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
    return modules


def test_compiler_modules_do_not_import_runtime_execution_paths():
    banned_prefixes = (
        "experiment",
        "virtual_shaping_lab.experiment",
        "virtual_shaping_lab.analysis",
        "virtual_shaping_lab.api",
        "virtual_shaping_lab.vsl.environment.harness",
        "virtual_shaping_lab.vsl.runner",
        "virtual_shaping_lab.vsl.agents",
    )

    offenders: list[str] = []
    for path in _compiler_files():
        for module in _imported_modules(path):
            if module.startswith("ui.contracts"):
                continue
            if module.startswith("typing") or module in {"__future__", "copy", "ast", "hashlib", "json", "pathlib"}:
                continue
            if module.startswith(banned_prefixes):
                offenders.append(f"{path.name}: {module}")
    assert not offenders, "Compiler boundary violation imports detected: " + ", ".join(offenders)


def test_legality_and_selection_compiler_are_not_preset_hardcoded():
    preset_ids = set(get_preset_registry()["presets"].keys())
    sources = [
        (_contracts_root() / "operator_legality_engine.py").read_text(encoding="utf-8"),
        (_contracts_root() / "operator_selection_compiler.py").read_text(encoding="utf-8"),
    ]
    combined = "\n".join(sources)

    offenders = [preset_id for preset_id in sorted(preset_ids) if f"'{preset_id}'" in combined or f'"{preset_id}"' in combined]
    assert not offenders, "Legality/compiler modules must be registry-driven; found preset literals: " + ", ".join(offenders)


def test_selection_compiler_unsupported_selection_has_contract_error_code():
    payload = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    payload["operator_subset"]["phi"] = "non_registry_impl"
    with pytest.raises(OperatorSelectionCompilerError) as exc:
        compile_operator_selection_artifact(payload)
    assert exc.value.code == "CMP_E_UNKNOWN_SELECTION"
    assert exc.value.details.get("slot") == "phi"


def test_selection_compiler_unknown_slot_has_contract_error_code():
    payload = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    payload["operator_subset"]["not_a_slot"] = "anything"
    with pytest.raises(OperatorSelectionCompilerError) as exc:
        compile_operator_selection_artifact(payload)
    assert exc.value.code == "CMP_E_UNKNOWN_SLOT"
    assert "not_a_slot" in (exc.value.details.get("slots") or [])

