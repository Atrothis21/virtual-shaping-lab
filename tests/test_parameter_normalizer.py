from experiment.parameters.pipeline import ParameterNormalizerPipeline


def test_parameter_normalizer_normalizes_protocol_keys_and_runtime_defaults():
    payload = {
        "experiment": {
            "protocol": "Operant-Conditioning",
            "phases": [
                {"protocol": "Acquisition", "params": {"n_trials": "5"}},
                {"protocol": "Rapid-Reacquisition", "params": {}},
            ],
            "policy": {"name": "Epsilon-Greedy", "params": {"epsilon": 0.1}},
        }
    }
    out = ParameterNormalizerPipeline.normalize(payload)
    exp = out["experiment"]
    assert exp["protocol"] == "operant_conditioning"
    assert exp["phases"][0]["protocol"] == "acquisition"
    assert exp["phases"][1]["protocol"] == "rapid_reacquisition"
    assert exp["phases"][0]["params"]["n_trials"] == 5
    assert exp["policy"]["name"] == "epsilon_greedy"
    assert exp["runtime"]["update_mode"] == "trial"
    assert exp["runtime"]["record_mode"] == "trial"
    assert exp["runtime"]["strict_records"] is False


def test_parameter_normalizer_rejects_non_object_payload():
    try:
        ParameterNormalizerPipeline.normalize("bad")  # type: ignore[arg-type]
    except ValueError as exc:
        assert "payload must be an object" in str(exc)

