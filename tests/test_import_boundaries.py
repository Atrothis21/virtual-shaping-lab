from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "virtual_shaping_lab"


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


def _violations(paths: list[Path], forbidden_prefixes: tuple[str, ...]) -> list[tuple[str, str]]:
    bad: list[tuple[str, str]] = []
    for path in paths:
        for mod in _import_modules(path):
            if mod.startswith("typing") or mod.startswith("__future__"):
                continue
            if any(mod == p or mod.startswith(f"{p}.") for p in forbidden_prefixes):
                bad.append((str(path.relative_to(ROOT)), mod))
    return bad


def test_analysis_layer_does_not_import_runtime_cognition_or_protocols():
    paths = list(_iter_python_files(ROOT / "analysis"))
    # Keep self-layer allowed; check explicit forbidden external internals.
    forbidden_external = (
        "experiment.runner",
        "experiment.trial_executor",
        "experiment.runtime_records",
        "experiment.sinks",
        "experiment.hooks",
        "protocols",
        "agents",
        "virtual_shaping_lab.experiment.runner",
        "virtual_shaping_lab.experiment.trial_executor",
        "virtual_shaping_lab.experiment.runtime_records",
        "virtual_shaping_lab.experiment.sinks",
        "virtual_shaping_lab.experiment.hooks",
        "virtual_shaping_lab.protocols",
        "virtual_shaping_lab.agents",
    )
    bad = _violations(paths, forbidden_external)
    assert not bad, f"Analysis import boundary violations: {bad}"


def test_runtime_layer_does_not_import_analysis():
    runtime_paths = [
        ROOT / "experiment" / "runner.py",
        ROOT / "experiment" / "trial_executor.py",
        ROOT / "experiment" / "hooks.py",
        ROOT / "experiment" / "runtime_records.py",
        ROOT / "experiment" / "sinks.py",
    ]
    forbidden = (
        "analysis",
        "virtual_shaping_lab.analysis",
    )
    bad = _violations(runtime_paths, forbidden)
    assert not bad, f"Runtime import boundary violations: {bad}"


def test_cognition_layer_does_not_import_runtime_protocols_or_analysis():
    paths = list(_iter_python_files(ROOT / "agents"))
    forbidden = (
        "experiment.runner",
        "experiment.trial_executor",
        "experiment.runtime_records",
        "experiment.sinks",
        "experiment.hooks",
        "protocols",
        "analysis",
        "virtual_shaping_lab.experiment.runner",
        "virtual_shaping_lab.experiment.trial_executor",
        "virtual_shaping_lab.experiment.runtime_records",
        "virtual_shaping_lab.experiment.sinks",
        "virtual_shaping_lab.experiment.hooks",
        "virtual_shaping_lab.protocols",
        "virtual_shaping_lab.analysis",
    )
    bad = _violations(paths, forbidden)
    assert not bad, f"Cognition import boundary violations: {bad}"


def test_config_layer_does_not_import_runtime_behavior_or_analysis():
    paths = [ROOT / "experiment" / "config.py"]
    forbidden = (
        "experiment.runner",
        "experiment.trial_executor",
        "experiment.hooks",
        "experiment.runtime_records",
        "experiment.sinks",
        "protocols",
        "analysis",
        "virtual_shaping_lab.experiment.runner",
        "virtual_shaping_lab.experiment.trial_executor",
        "virtual_shaping_lab.experiment.hooks",
        "virtual_shaping_lab.experiment.runtime_records",
        "virtual_shaping_lab.experiment.sinks",
        "virtual_shaping_lab.protocols",
        "virtual_shaping_lab.analysis",
    )
    bad = _violations(paths, forbidden)
    assert not bad, f"Config import boundary violations: {bad}"


def test_api_layer_uses_public_facades_not_deep_experiment_analysis_internals():
    paths = list(_iter_python_files(ROOT / "api"))
    forbidden = (
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
    bad = _violations(paths, forbidden)
    assert not bad, f"API facade import boundary violations: {bad}"
