from __future__ import annotations

from experiment.phases.catalog_runtime import PHASE_BUILDERS


def test_no_legacy_phase_keys_guard():
    violations = sorted([name for name in PHASE_BUILDERS.keys() if "_legacy" in str(name)])
    assert not violations, f"no_legacy_phase_keys violations: {violations}"
