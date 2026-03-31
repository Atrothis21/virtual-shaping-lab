from __future__ import annotations

import importlib
from pathlib import Path

from virtual_shaping_lab.vsl.agent.policy.spec import PolicySpec as CanonicalPolicySpec
from virtual_shaping_lab.vsl.spec import RuntimePolicyConfig
from virtual_shaping_lab.vsl.spec.contracts import PolicySpec as RuntimePolicySpec


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "virtual_shaping_lab"


_DISALLOWED_RUNTIME_IMPORT_TOKEN = "from virtual_shaping_lab.vsl.spec.contracts import PolicySpec"
_ALLOWED_RUNTIME_IMPORT_PATHS = {
    "virtual_shaping_lab/vsl/agent/policy/adapters.py",
    "virtual_shaping_lab/vsl/agent/policy/instantiate.py",
}

_REMOVED_POLICY_SURFACES = [
    "virtual_shaping_lab.vsl.agent.policy.boundary",
    "virtual_shaping_lab.vsl.agent.policy.validator",
    "virtual_shaping_lab.vsl.agent.policy.runtime_contracts",
]


def test_v3_20_0_policy_contract_ownership_is_explicit_and_non_duplicated():
    assert CanonicalPolicySpec is not RuntimePolicySpec
    assert RuntimePolicyConfig is RuntimePolicySpec


def test_v3_20_0_no_shadow_runtime_policy_spec_imports_outside_boundaries():
    violations: list[str] = []
    for path in PKG.rglob("*.py"):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        if _DISALLOWED_RUNTIME_IMPORT_TOKEN in text and rel not in _ALLOWED_RUNTIME_IMPORT_PATHS:
            violations.append(rel)
    assert not violations, (
        "Runtime PolicySpec import is only allowed in adapter/instantiation boundaries. "
        f"Violations: {violations}"
    )


def test_v3_20_0_removed_legacy_policy_surfaces_fail_fast():
    for path in _REMOVED_POLICY_SURFACES:
        try:
            importlib.import_module(path)
            assert False, f"Expected ModuleNotFoundError for removed legacy policy surface: {path}"
        except ModuleNotFoundError:
            pass

