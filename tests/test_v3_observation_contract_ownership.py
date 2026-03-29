from __future__ import annotations

import importlib
from pathlib import Path

from virtual_shaping_lab.vsl.agent.observation.spec import ObservationSpec as CanonicalObservationSpec
from virtual_shaping_lab.vsl.spec.contracts import RepresentationSpec as RuntimeRepresentationSpec


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "virtual_shaping_lab"


_DISALLOWED_RUNTIME_IMPORT_TOKEN = "from virtual_shaping_lab.vsl.spec.contracts import RepresentationSpec"
_ALLOWED_RUNTIME_IMPORT_PATHS: set[str] = set()

_REMOVED_OBSERVATION_SURFACES = [
    "virtual_shaping_lab.vsl.agent.observation.boundary",
    "virtual_shaping_lab.vsl.agent.observation.validator",
    "virtual_shaping_lab.vsl.agent.observation.runtime_contracts",
]


def test_v3_19_0_observation_contract_ownership_is_explicit_and_non_duplicated():
    # Canonical observation tuple semantics are not owned by runtime transport contracts.
    assert CanonicalObservationSpec is not RuntimeRepresentationSpec


def test_v3_19_0_no_shadow_runtime_observation_spec_imports_outside_boundaries():
    violations: list[str] = []
    for path in PKG.rglob("*.py"):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        if _DISALLOWED_RUNTIME_IMPORT_TOKEN in text and rel not in _ALLOWED_RUNTIME_IMPORT_PATHS:
            violations.append(rel)
    assert not violations, (
        "Runtime RepresentationSpec import is not allowed in observation ownership surfaces. "
        f"Violations: {violations}"
    )


def test_v3_19_0_removed_legacy_observation_surfaces_fail_fast():
    for path in _REMOVED_OBSERVATION_SURFACES:
        try:
            importlib.import_module(path)
            assert False, f"Expected ModuleNotFoundError for removed legacy observation surface: {path}"
        except ModuleNotFoundError:
            pass

