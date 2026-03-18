from ui.contracts.builder_draft import BuilderExperimentDraft
from ui.contracts.translator import draft_to_payload
from ui.validate_payload import validate_payload


def test_draft_to_payload_classical_protocol_mode_validates():
    draft = BuilderExperimentDraft.from_dict(
        {
            "program": {
                "protocol": "acquisition",
                "stimuli": {"cs_plus": ["tone"]},
                "params": {"n_trials": 10},
            },
            "agent": {
                "name": "classical_agent",
                "representation": "vector_elemental",
                "learning": {"rule": "rescorla_wagner", "params": {}, "attention": {"config": {"name": "none", "params": {}}, "initial": {}}},
                "policy": None,
            },
            "runtime": {"update_mode": "trial", "record_mode": "trial"},
        }
    )
    payload = draft_to_payload(draft)
    assert payload["report"]["preset"] == "acquisition"
    assert set(payload["experiment"].keys()) == {"program", "agent", "runtime"}
    assert payload["experiment"]["program"]["phases"][0]["protocol"] == "acquisition"
    assert payload["experiment"]["program"]["phases"][0]["trials"] == 10
    assert payload["experiment"]["agent"]["learning"]["rule"] == "rescorla_wagner"
    assert payload["experiment"]["agent"]["representation"]["name"] == "vector_elemental"
    validate_payload(payload)


def test_draft_to_payload_operant_protocol_mode_validates():
    draft = BuilderExperimentDraft.from_dict(
        {
            "program": {
                "protocol": "matching_law",
                "params": {
                    "n_trials": 30,
                    "schedule_left": {"type": "variable_interval", "value": 30},
                    "schedule_right": {"type": "variable_interval", "value": 60},
                    "action_labels": ["left", "right"],
                },
            },
            "agent": {
                "name": "operant_agent",
                "representation": "vector_elemental",
                "learning": {"rule": "q_learner", "params": {}, "attention": {"config": {"name": "none", "params": {}}, "initial": {}}},
                "policy": {
                    "name": "epsilon_greedy",
                    "params": {"actions": ["left", "right"], "epsilon": 0.1},
                },
            },
            "runtime": {"update_mode": "tick", "record_mode": "trial"},
        }
    )
    payload = draft_to_payload(draft)
    assert payload["report"]["preset"] == "matching_law"
    assert set(payload["experiment"].keys()) == {"program", "agent", "runtime"}
    assert payload["experiment"]["program"]["phases"][0]["protocol"] == "matching_law"
    assert payload["experiment"]["program"]["phases"][0]["trials"] == 30
    assert payload["experiment"]["agent"]["policy"]["name"] == "epsilon_greedy"
    validate_payload(payload)


def test_draft_to_payload_phase_mode_defaults_to_custom_protocol_preset():
    draft = BuilderExperimentDraft.from_dict(
        {
            "program": {
                "phases": [
                    {
                        "protocol": "acquisition",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 10},
                    },
                    {
                        "protocol": "nonreinforcement",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 5},
                    },
                ]
            },
            "agent": {
                "name": "classical_agent",
                "representation": "vector_elemental",
                "learning": {"rule": "rescorla_wagner", "params": {}, "attention": {"config": {"name": "none", "params": {}}, "initial": {}}},
                "policy": None,
            },
        }
    )
    payload = draft_to_payload(draft)
    assert payload["report"]["preset"] == "custom_protocol"
    assert set(payload["experiment"].keys()) == {"program", "agent", "runtime"}
    assert len(payload["experiment"]["program"]["phases"]) == 2
    assert payload["experiment"]["program"]["phases"][0]["trials"] == 10
    assert payload["experiment"]["program"]["phases"][1]["trials"] == 5
    validate_payload(payload)
