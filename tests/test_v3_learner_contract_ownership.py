from __future__ import annotations

import importlib
from pathlib import Path

from virtual_shaping_lab.vsl.agent.learning.spec import LearnerSpec as CanonicalLearnerSpec
from virtual_shaping_lab.vsl.spec import RuntimeLearnerConfig
from virtual_shaping_lab.vsl.spec.contracts import LearnerSpec as RuntimeLearnerSpec


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "virtual_shaping_lab"


_DISALLOWED_RUNTIME_IMPORT_TOKEN = "from virtual_shaping_lab.vsl.spec.contracts import LearnerSpec"
_ALLOWED_RUNTIME_IMPORT_PATHS = {
    "virtual_shaping_lab/vsl/agent/learning/adapters.py",
    "virtual_shaping_lab/vsl/agent/learning/instantiate.py",
}

_REMOVED_LEARNER_SURFACES = [
    "virtual_shaping_lab.vsl.agent.learning.boundary",
    "virtual_shaping_lab.vsl.agent.learning.validator",
    "virtual_shaping_lab.vsl.agent.learning.runtime_contracts",
]


def test_v3_18_0_learner_contract_ownership_is_explicit_and_non_duplicated():
    # Canonical tuple semantics are not owned by runtime transport contracts.
    assert CanonicalLearnerSpec is not RuntimeLearnerSpec
    assert RuntimeLearnerConfig is RuntimeLearnerSpec


def test_v3_18_0_no_shadow_runtime_learner_spec_imports_outside_adapters():
    violations: list[str] = []
    for path in PKG.rglob("*.py"):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        if _DISALLOWED_RUNTIME_IMPORT_TOKEN in text and rel not in _ALLOWED_RUNTIME_IMPORT_PATHS:
            violations.append(rel)
    assert not violations, (
        "Runtime LearnerSpec import is only allowed in adapter/instantiation boundaries. "
        f"Violations: {violations}"
    )


def test_v3_18_0_plan_builder_and_assembly_depend_on_canonical_resolution_surface():
    plan_builder_text = (ROOT / "virtual_shaping_lab" / "experiment" / "plan_builder.py").read_text(encoding="utf-8")
    assemble_text = (ROOT / "virtual_shaping_lab" / "experiment" / "assemble.py").read_text(encoding="utf-8")
    expected_import = "from virtual_shaping_lab.vsl.agent.learning import resolve_learner_spec"
    assert expected_import in plan_builder_text
    assert expected_import in assemble_text
    assert _DISALLOWED_RUNTIME_IMPORT_TOKEN not in plan_builder_text
    assert _DISALLOWED_RUNTIME_IMPORT_TOKEN not in assemble_text


def test_v3_18_0_removed_legacy_learner_surfaces_fail_fast():
    for path in _REMOVED_LEARNER_SURFACES:
        try:
            importlib.import_module(path)
            assert False, f"Expected ModuleNotFoundError for removed legacy learner surface: {path}"
        except ModuleNotFoundError:
            pass

