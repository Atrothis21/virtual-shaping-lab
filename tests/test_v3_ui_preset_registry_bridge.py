from __future__ import annotations

from ui.contracts.preset_registry import list_preset_ids
from ui.contracts.preset_registry_bridge import (
    REGISTRY_BRIDGE_VERSION,
    build_v3_ui_preset_catalog,
    build_v3_ui_preset_descriptors,
    discover_measurement_presets,
    discover_policy_presets,
    discover_protocol_presets,
)
from virtual_shaping_lab.vsl.agent.policy.presets import policy_preset_names
from virtual_shaping_lab.vsl.measurement.presets import measurement_preset_names
from virtual_shaping_lab.vsl.protocol.presets import protocol_preset_names


def test_v3_ui_preset_registry_bridge_discovers_policy_protocol_measurement_presets():
    assert sorted(discover_policy_presets().keys()) == policy_preset_names()
    assert sorted(discover_protocol_presets().keys()) == protocol_preset_names()
    assert sorted(discover_measurement_presets().keys()) == measurement_preset_names()


def test_v3_ui_preset_registry_bridge_builds_descriptors_for_all_ui_presets():
    descriptors = build_v3_ui_preset_descriptors()
    assert [descriptor.preset_id for descriptor in descriptors] == sorted(list_preset_ids())
    for descriptor in descriptors:
        assert descriptor.protocol_preset_id in protocol_preset_names()
        assert descriptor.measurement_preset_id in measurement_preset_names()
        if descriptor.family == "classical":
            assert descriptor.policy_preset_id == "none"
        else:
            assert descriptor.policy_preset_id in policy_preset_names()


def test_v3_ui_preset_registry_bridge_catalog_hash_is_stable():
    a = build_v3_ui_preset_catalog()
    b = build_v3_ui_preset_catalog()
    assert a.contract_version == REGISTRY_BRIDGE_VERSION
    assert a.metadata["registry_driven"] is True
    assert a.stable_hash() == b.stable_hash()

