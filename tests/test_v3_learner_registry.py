from __future__ import annotations

from virtual_shaping_lab.vsl.agent.learning import (
    COMPATIBILITY_MATRIX,
    SLOT_REGISTRIES,
    compatibility_matrix,
    learner_registry_hash,
    learner_registry_payload,
    slot_registries,
)
from virtual_shaping_lab.vsl.agent.learning.validator import (
    ATTENTION_TO_UPDATERS_STRICT,
    ATTENTION_VALUES,
    ERROR_VALUES,
    POLICY_VALUES,
    PREDICTOR_TO_ERRORS,
    PREDICTOR_TO_POLICIES,
    PREDICTOR_VALUES,
    TRACE_TO_UPDATERS,
    TRACE_VALUES,
    UPDATER_VALUES,
)


def test_v3_learner_slot_registries_are_machine_readable():
    payload = slot_registries()
    assert set(payload.keys()) == {"trace", "predictor", "error", "attention", "updater", "policy"}
    assert all(isinstance(values, list) for values in payload.values())
    assert payload == SLOT_REGISTRIES


def test_v3_learner_compatibility_matrix_is_machine_readable():
    matrix = compatibility_matrix()
    assert set(matrix.keys()) == {
        "predictor_to_error",
        "predictor_to_policy",
        "trace_to_updater",
        "attention_to_updater_strict",
    }
    assert matrix == COMPATIBILITY_MATRIX


def test_v3_learner_registry_parity_with_validator_constants():
    assert SLOT_REGISTRIES["trace"] == sorted(TRACE_VALUES)
    assert SLOT_REGISTRIES["predictor"] == sorted(PREDICTOR_VALUES)
    assert SLOT_REGISTRIES["error"] == sorted(ERROR_VALUES)
    assert SLOT_REGISTRIES["attention"] == sorted(ATTENTION_VALUES)
    assert SLOT_REGISTRIES["updater"] == sorted(UPDATER_VALUES)
    assert SLOT_REGISTRIES["policy"] == sorted(POLICY_VALUES)

    assert COMPATIBILITY_MATRIX["predictor_to_error"] == {
        key: sorted(values) for key, values in sorted(PREDICTOR_TO_ERRORS.items())
    }
    assert COMPATIBILITY_MATRIX["predictor_to_policy"] == {
        key: sorted(values) for key, values in sorted(PREDICTOR_TO_POLICIES.items())
    }
    assert COMPATIBILITY_MATRIX["trace_to_updater"] == {
        key: sorted(values) for key, values in sorted(TRACE_TO_UPDATERS.items())
    }
    assert COMPATIBILITY_MATRIX["attention_to_updater_strict"] == {
        key: sorted(values) for key, values in sorted(ATTENTION_TO_UPDATERS_STRICT.items())
    }


def test_v3_learner_registry_payload_and_hash_are_stable():
    payload = learner_registry_payload()
    assert payload["version"] == "3.5.0"
    assert payload["slot_registries"] == SLOT_REGISTRIES
    assert payload["compatibility_matrix"] == COMPATIBILITY_MATRIX
    hashes = [learner_registry_hash() for _ in range(20)]
    assert len(set(hashes)) == 1

