from __future__ import annotations

from pathlib import Path

from virtual_shaping_lab.vsl import MeasurementSpec as PublicMeasurementSpec
from virtual_shaping_lab.vsl.measurement.spec import MeasurementSpec as CanonicalMeasurementSpec


ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "virtual_shaping_lab"

_ALLOWED_MEASUREMENT_SPEC_OWNER = "virtual_shaping_lab/vsl/measurement/spec.py"
_BANNED_MEASUREMENT_RUNTIME_IMPORT_TOKENS = (
    "from virtual_shaping_lab.vsl.runtime",
    "from virtual_shaping_lab.vsl.rollout",
)


def test_v3_22_0_measurement_contract_owner_is_canonical_spec():
    assert PublicMeasurementSpec is CanonicalMeasurementSpec


def test_v3_22_0_measurement_spec_owner_is_unique():
    owners: list[str] = []
    for path in PKG.rglob("*.py"):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        if "class MeasurementSpec" in text:
            owners.append(rel)
    assert owners == [_ALLOWED_MEASUREMENT_SPEC_OWNER]


def test_v3_22_0_measurement_module_stays_runtime_independent():
    violations: list[str] = []
    measurement_pkg = PKG / "vsl" / "measurement"
    for path in measurement_pkg.rglob("*.py"):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        if any(token in text for token in _BANNED_MEASUREMENT_RUNTIME_IMPORT_TOKENS):
            violations.append(rel)
    assert not violations, f"Measurement module must stay runtime-independent. Violations: {violations}"
