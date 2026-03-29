from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.agent.observation import (
    ObservationSpec,
    ObservationSpecValidationError,
    validate_observation_spec,
)


def _legal_spec() -> ObservationSpec:
    return ObservationSpec(
        representation="stimulus_vector",
        context="discrete_context",
        generalization="stimulus_similarity",
    )


def test_validate_observation_spec_accepts_legal_tuple():
    spec = _legal_spec()
    validate_observation_spec(spec)


@pytest.mark.parametrize(
    "patch,code",
    [
        ({"context": "none", "generalization": "context_gate", "representation": "temporal_basis"}, "OBS_E_GENERALIZATION_REQUIRES_CONTEXT"),
        ({"representation": "stimulus_vector", "generalization": "context_gate", "context": "discrete_context"}, "OBS_E_GENERALIZATION_REQUIRES_REPRESENTATION"),
        ({"context": "latent_context", "generalization": "stimulus_similarity", "representation": "temporal_basis"}, "OBS_E_CONTEXT_GENERALIZATION_MISMATCH"),
    ],
)
def test_validate_observation_spec_rejects_illegal_tuples_with_named_error_codes(patch, code):
    payload = _legal_spec().to_dict()
    payload.update(patch)
    with pytest.raises(ObservationSpecValidationError) as exc:
        ObservationSpec.from_dict(payload)
    assert exc.value.code == code
