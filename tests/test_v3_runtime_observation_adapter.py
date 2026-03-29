from __future__ import annotations

from virtual_shaping_lab.vsl.agent.observation import ObservationStepResult
from virtual_shaping_lab.vsl.runtime import RuntimeObservationAdapter, build_runtime_observation_adapter


def test_v3_19_10_build_runtime_observation_adapter_returns_canonical_runtime_surface():
    adapter = build_runtime_observation_adapter()
    assert isinstance(adapter, RuntimeObservationAdapter)
    assert adapter.preset_name == "identity_observation"


def test_v3_19_10_runtime_observation_adapter_normalizes_mapping_sequence_payloads():
    adapter = build_runtime_observation_adapter(preset_name="identity_observation")
    out = adapter.step(
        stimulus={"cs_plus": ["tone"], "us": 1.0},
        metadata={"source": "runtime_observation_test"},
    )
    assert isinstance(out, ObservationStepResult)
    assert out.output.feature_names == ["tone", "us"]
    assert out.output.features == [1.0, 1.0]
    assert out.output.metadata["runtime_observation"]["preset_name"] == "identity_observation"


def test_v3_19_10_runtime_observation_adapter_infers_context_state_from_stimulus_when_missing():
    adapter = build_runtime_observation_adapter(preset_name="identity_observation")
    out = adapter.step(
        stimulus={"cs_plus": ["tone"], "context": "A"},
        context_state=None,
    )
    assert out.output.context_state == "A"


def test_v3_19_10_runtime_observation_adapter_coerces_non_numeric_scalars_to_presence():
    adapter = build_runtime_observation_adapter(preset_name="identity_observation")
    out = adapter.step(stimulus={"phase": "acquisition"})
    assert out.output.feature_names == ["phase"]
    assert out.output.features == [1.0]

