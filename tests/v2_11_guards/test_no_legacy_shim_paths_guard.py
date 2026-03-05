from __future__ import annotations

import ast
import importlib
from pathlib import Path


def test_removed_legacy_shim_modules_remain_unimportable():
    for module_name in (
        "experiment.assembly",
        "experiment.assembly.assemble",
        "experiment.assembly.plan_builder",
        "experiment.runtime",
        "experiment.runtime.runner",
        "experiment.runtime.hooks",
        "experiment.runtime.sinks",
        "experiment.runtime.records",
        "experiment.runtime.trial_executor",
        "experiment.units",
        "experiment.units.phases",
        "experiment.units.protocols",
    ):
        try:
            importlib.import_module(module_name)
            assert False, f"Expected ModuleNotFoundError for removed shim module '{module_name}'"
        except ModuleNotFoundError:
            pass


def test_source_tree_contains_no_legacy_shim_import_paths():
    root = Path(__file__).resolve().parents[2]
    source_roots = [root / "virtual_shaping_lab", root / "tests"]
    forbidden = (
        "experiment.assembly",
        "experiment.runtime.",
        "experiment.units",
    )

    for src_root in source_roots:
        for path in src_root.rglob("*.py"):
            if path.name == "test_no_legacy_shim_paths_guard.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imported: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported.add(node.module)
            for needle in forbidden:
                for mod in imported:
                    assert not (mod == needle or mod.startswith(f"{needle}")), (
                        f"Found forbidden import path '{needle}' in {path} via module '{mod}'"
                    )
