from __future__ import annotations

import importlib
from pathlib import Path

from virtual_shaping_lab.vsl.protocol.spec import ProtocolSpec as CanonicalProtocolSpec
from virtual_shaping_lab.vsl.spec import RuntimeProtocolConfig
from virtual_shaping_lab.vsl.spec.contracts import ProtocolSpec as RuntimeProtocolSpec


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "virtual_shaping_lab"


_DISALLOWED_RUNTIME_IMPORT_TOKEN = "from virtual_shaping_lab.vsl.spec.contracts import ProtocolSpec"
_ALLOWED_RUNTIME_IMPORT_PATHS = {
    "virtual_shaping_lab/vsl/protocol/adapters.py",
    "virtual_shaping_lab/vsl/protocol/instantiate.py",
}

_REMOVED_PROTOCOL_SURFACES = [
    "virtual_shaping_lab.vsl.protocol.boundary",
    "virtual_shaping_lab.vsl.protocol.validator",
    "virtual_shaping_lab.vsl.protocol.runtime_contracts",
]


def test_v3_21_0_protocol_contract_ownership_is_explicit_and_non_duplicated():
    assert CanonicalProtocolSpec is not RuntimeProtocolSpec
    assert RuntimeProtocolConfig is RuntimeProtocolSpec


def test_v3_21_0_no_shadow_runtime_protocol_spec_imports_outside_boundaries():
    violations: list[str] = []
    for path in PKG.rglob("*.py"):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        if _DISALLOWED_RUNTIME_IMPORT_TOKEN in text and rel not in _ALLOWED_RUNTIME_IMPORT_PATHS:
            violations.append(rel)
    assert not violations, (
        "Runtime ProtocolSpec import is only allowed in adapter/instantiation boundaries. "
        f"Violations: {violations}"
    )


def test_v3_21_0_removed_legacy_protocol_surfaces_fail_fast():
    for path in _REMOVED_PROTOCOL_SURFACES:
        try:
            importlib.import_module(path)
            assert False, f"Expected ModuleNotFoundError for removed legacy protocol surface: {path}"
        except ModuleNotFoundError:
            pass
