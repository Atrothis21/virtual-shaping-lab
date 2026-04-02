from __future__ import annotations

from virtual_shaping_lab.vsl.measurement import (
    MEASUREMENT_REGISTRY_VERSION,
    compatibility_matrix,
    measurement_registry_hash,
    measurement_registry_payload,
    slot_registries,
)


def test_v3_measurement_registry_slots_and_compatibility_are_present():
    slots = slot_registries()
    matrix = compatibility_matrix()
    assert set(slots.keys()) == {"analysis_ops", "visualization_ops", "report_op"}
    assert "analysis_to_visualization" in matrix
    assert "report_requires_visualization" in matrix


def test_v3_measurement_registry_payload_is_versioned():
    payload = measurement_registry_payload()
    assert payload["version"] == MEASUREMENT_REGISTRY_VERSION
    assert "slot_registries" in payload
    assert "compatibility_matrix" in payload


def test_v3_measurement_registry_hash_is_stable():
    hashes = [measurement_registry_hash() for _ in range(20)]
    assert len(set(hashes)) == 1
