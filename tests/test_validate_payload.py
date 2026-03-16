import pytest

from ui.validate_payload import ValidationError, validate_payload


def _canonical_payload():
    return {
        "experiment": {
            "program": {
                "phases": [
                    {
                        "name": "Acq",
                        "protocol": "acquisition",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 1},
                        "trials": 1,
                    }
                ]
            },
            "agent": {
                "name": "classical_agent",
                "representation": {
                    "name": "vector_elemental",
                    "params": {"stimuli": ["tone"], "max_compound_size": 2},
                },
                "learning": {"rule": "rescorla_wagner", "params": {}},
                "policy": None,
            },
            "runtime": {"update_mode": "trial", "record_mode": "trial"},
        },
        "report": {"preset": "acquisition"},
    }


def _legacy_payload():
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


def test_validate_payload_accepts_canonical_payload():
    validate_payload(_canonical_payload())


def test_validate_payload_rejects_missing_required_sections():
    with pytest.raises(ValidationError):
        validate_payload({"report": {"preset": "acquisition"}})
    with pytest.raises(ValidationError):
        validate_payload({"experiment": {}})


def test_validate_payload_rejects_legacy_payload_shape():
    with pytest.raises(ValidationError, match="Legacy payload shape is no longer accepted at runtime"):
        validate_payload(_legacy_payload())


def test_validate_payload_rejects_mixed_payload_shape():
    payload = _canonical_payload()
    payload["experiment"]["learner"] = "rescorla_wagner"
    with pytest.raises(ValidationError, match="Mixed payload shape detected"):
        validate_payload(payload)


def test_validate_payload_rejects_missing_canonical_sections():
    payload = _canonical_payload()
    payload["experiment"].pop("program")
    with pytest.raises(ValidationError, match="Payload experiment must use canonical keys"):
        validate_payload(payload)

    payload = _canonical_payload()
    payload["experiment"].pop("runtime")
    with pytest.raises(ValidationError, match="Payload experiment must use canonical keys"):
        validate_payload(payload)


def test_validate_payload_rejects_bad_canonical_phase_shapes():
    payload = _canonical_payload()
    payload["experiment"]["program"]["phases"] = ["bad"]
    with pytest.raises(ValidationError, match="experiment.program.phases entries must be objects"):
        validate_payload(payload)

    payload = _canonical_payload()
    payload["experiment"]["program"]["phases"][0].pop("trials")
    payload["experiment"]["program"]["phases"][0]["params"].pop("n_trials")
    with pytest.raises(ValidationError, match="missing required 'trials'"):
        validate_payload(payload)

    payload = _canonical_payload()
    payload["experiment"]["program"]["phases"][0]["trials"] = "bad"
    with pytest.raises(ValidationError, match="program.phases\\[0\\]\\.trials must be an integer"):
        validate_payload(payload)


def test_validate_payload_rejects_bad_canonical_agent_shapes():
    payload = _canonical_payload()
    payload["experiment"]["agent"] = "bad"
    with pytest.raises(ValidationError, match="experiment.agent must be an object"):
        validate_payload(payload)

    payload = _canonical_payload()
    payload["experiment"]["agent"]["representation"] = "bad"
    with pytest.raises(ValidationError, match="experiment.agent.representation must be an object"):
        validate_payload(payload)

    payload = _canonical_payload()
    payload["experiment"]["agent"]["learning"] = "bad"
    with pytest.raises(ValidationError, match="experiment.agent.learning must be an object"):
        validate_payload(payload)
