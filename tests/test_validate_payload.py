import pytest

from ui.validate_payload import ValidationError, validate_payload


def _base_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["tone"], "max_compound_size": 2},
            },
            "protocol": "acquisition",
            "stimuli": {"cs_plus": ["tone"]},
            "params": {"n_trials": 1},
        },
        "report": {"preset": "acquisition"},
    }


def test_validate_payload_accepts_shallow_valid_protocol_mode():
    validate_payload(_base_payload())


def test_validate_payload_rejects_missing_required_sections():
    with pytest.raises(ValidationError):
        validate_payload({"report": {"preset": "acquisition"}})
    with pytest.raises(ValidationError):
        validate_payload({"experiment": {}})


def test_validate_payload_rejects_protocol_and_phases_both_or_neither():
    payload = _base_payload()
    payload["experiment"]["phases"] = [{"protocol": "acquisition", "params": {"n_trials": 1}}]
    with pytest.raises(ValidationError, match="either 'protocol' or 'phases'"):
        validate_payload(payload)

    payload = _base_payload()
    payload["experiment"].pop("protocol")
    payload["experiment"].pop("stimuli")
    payload["experiment"].pop("params")
    with pytest.raises(ValidationError, match="either 'protocol' or 'phases'"):
        validate_payload(payload)


def test_validate_payload_rejects_bad_shallow_shapes():
    payload = _base_payload()
    payload["experiment"]["protocol"] = 123
    with pytest.raises(ValidationError, match="protocol"):
        validate_payload(payload)

    payload = _base_payload()
    payload["experiment"]["params"] = "bad"
    with pytest.raises(ValidationError, match="params"):
        validate_payload(payload)

    payload = _base_payload()
    payload["experiment"]["stimuli"] = ["tone"]
    with pytest.raises(ValidationError, match="stimuli"):
        validate_payload(payload)


def test_validate_payload_accepts_shallow_phase_mode():
    payload = _base_payload()
    payload["experiment"].pop("protocol")
    payload["experiment"].pop("stimuli")
    payload["experiment"].pop("params")
    payload["experiment"]["phases"] = [
        {
            "name": "Acq",
            "protocol": "acquisition",
            "stimuli": {"cs_plus": ["tone"]},
            "params": {"n_trials": 1},
        }
    ]
    validate_payload(payload)


def test_validate_payload_phase_mode_rejects_bad_phase_shapes():
    payload = _base_payload()
    payload["experiment"].pop("protocol")
    payload["experiment"].pop("stimuli")
    payload["experiment"].pop("params")
    payload["experiment"]["phases"] = ["bad"]
    with pytest.raises(ValidationError, match="phase\\[0\\] must be an object"):
        validate_payload(payload)

    payload["experiment"]["phases"] = [{"params": {}}]
    with pytest.raises(ValidationError, match="phase\\[0\\]\\.protocol is required"):
        validate_payload(payload)

    payload["experiment"]["phases"] = [{"protocol": "acquisition", "params": "bad"}]
    with pytest.raises(ValidationError, match="phase\\[0\\]\\.params must be an object"):
        validate_payload(payload)


def test_validate_payload_does_not_perform_engine_semantic_guards():
    payload = _base_payload()
    # This is semantically invalid at engine-level, but UI layer is now shallow-only.
    payload["experiment"]["policy"] = {"name": "fixed", "params": {"action": "left"}}
    payload["experiment"]["representation"]["params"]["attention"] = {"tone": 0.8}
    validate_payload(payload)
