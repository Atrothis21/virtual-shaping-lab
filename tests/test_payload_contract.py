from experiment.payload_contract import to_canonical_payload


def _legacy_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["tone"], "max_compound_size": 2},
            },
            "phases": [
                {
                    "name": "Acq",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 10},
                }
            ],
            "runtime": {"update_mode": "trial", "record_mode": "trial"},
        },
        "report": {"preset": "acquisition"},
    }


def _canonical_payload():
    return {
        "experiment": {
            "program": {
                "phases": [
                    {
                        "name": "Acq",
                        "protocol": "acquisition",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 10},
                        "trials": 10,
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


def test_canonical_payload_passthrough():
    payload = _canonical_payload()
    canonical = to_canonical_payload(payload)
    assert canonical["experiment"]["program"]["phases"][0]["trials"] == 10
    assert canonical["report"]["preset"] == "acquisition"


def test_legacy_payload_rejected_at_runtime_contract():
    try:
        to_canonical_payload(_legacy_payload())
    except ValueError as exc:
        assert "Legacy payload shape is no longer accepted at runtime" in str(exc)
    else:
        raise AssertionError("Expected legacy payload rejection.")


def test_mixed_payload_rejected():
    payload = _legacy_payload()
    payload["experiment"]["program"] = {"phases": []}
    try:
        to_canonical_payload(payload)
    except ValueError as exc:
        assert "Mixed payload shape" in str(exc)
    else:
        raise AssertionError("Expected mixed-shape payload rejection.")


def test_missing_trials_rejected():
    payload = _canonical_payload()
    payload["experiment"]["program"]["phases"][0].pop("trials")
    try:
        to_canonical_payload(payload)
    except ValueError as exc:
        assert "missing required 'trials'" in str(exc)
    else:
        raise AssertionError("Expected trials validation failure.")
