from __future__ import annotations

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
            text = path.read_text(encoding="utf-8")
            for needle in forbidden:
                assert needle not in text, f"Found forbidden import path '{needle}' in {path}"
