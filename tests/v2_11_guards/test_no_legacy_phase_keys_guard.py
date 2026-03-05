from __future__ import annotations

from experiment.factories.phase_factory import PHASE_REGISTRY


def test_no_legacy_phase_keys_guard():
    violations = sorted([name for name in PHASE_REGISTRY.keys() if "_legacy" in str(name)])
    assert not violations, f"no_legacy_phase_keys violations: {violations}"
