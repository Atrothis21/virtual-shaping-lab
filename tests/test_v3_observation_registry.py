from __future__ import annotations

from virtual_shaping_lab.vsl.agent.observation import (
    COMPATIBILITY_MATRIX,
    OBSERVATION_REGISTRY_VERSION,
    SLOT_REGISTRIES,
    compatibility_matrix,
    observation_registry_hash,
    observation_registry_payload,
    slot_registries,
)
from virtual_shaping_lab.vsl.agent.observation.validation import (
    CONTEXT_TO_GENERALIZATION,
    CONTEXT_VALUES,
    GENERALIZATION_REQUIRES_CONTEXT,
    GENERALIZATION_REQUIRES_REPRESENTATION,
    GENERALIZATION_VALUES,
    REPRESENTATION_TO_GENERALIZATION,
    REPRESENTATION_VALUES,
)


def test_v3_observation_slot_registries_are_machine_readable():
    payload = slot_registries()
    assert set(payload.keys()) == {"representation", "context", "generalization"}
    assert all(isinstance(values, list) for values in payload.values())
    assert payload == SLOT_REGISTRIES


def test_v3_observation_compatibility_matrix_is_machine_readable():
    matrix = compatibility_matrix()
    assert set(matrix.keys()) == {
        "representation_to_generalization",
        "context_to_generalization",
        "generalization_requires_context",
        "generalization_requires_representation",
    }
    assert matrix == COMPATIBILITY_MATRIX


def test_v3_observation_registry_parity_with_validator_constants():
    assert SLOT_REGISTRIES["representation"] == sorted(REPRESENTATION_VALUES)
    assert SLOT_REGISTRIES["context"] == sorted(CONTEXT_VALUES)
    assert SLOT_REGISTRIES["generalization"] == sorted(GENERALIZATION_VALUES)

    assert COMPATIBILITY_MATRIX["representation_to_generalization"] == {
        key: sorted(values) for key, values in sorted(REPRESENTATION_TO_GENERALIZATION.items())
    }
    assert COMPATIBILITY_MATRIX["context_to_generalization"] == {
        key: sorted(values) for key, values in sorted(CONTEXT_TO_GENERALIZATION.items())
    }
    assert COMPATIBILITY_MATRIX["generalization_requires_context"] == {
        key: sorted(values) for key, values in sorted(GENERALIZATION_REQUIRES_CONTEXT.items())
    }
    assert COMPATIBILITY_MATRIX["generalization_requires_representation"] == {
        key: sorted(values) for key, values in sorted(GENERALIZATION_REQUIRES_REPRESENTATION.items())
    }


def test_v3_observation_registry_payload_and_hash_are_stable():
    payload = observation_registry_payload()
    assert payload["version"] == OBSERVATION_REGISTRY_VERSION
    assert payload["slot_registries"] == SLOT_REGISTRIES
    assert payload["compatibility_matrix"] == COMPATIBILITY_MATRIX
    hashes = [observation_registry_hash() for _ in range(20)]
    assert len(set(hashes)) == 1

