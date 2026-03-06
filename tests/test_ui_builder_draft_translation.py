from ui.contracts.builder_draft import BuilderExperimentDraft
from ui.contracts.translator import draft_to_payload
from ui.validate_payload import validate_payload


def test_draft_to_payload_classical_protocol_mode_validates():
    draft = BuilderExperimentDraft.from_dict(
        {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": "vector_elemental",
            "protocol": "acquisition",
            "stimuli": {"cs_plus": ["tone"]},
            "params": {"n_trials": 10},
            "runtime": {"update_mode": "trial", "record_mode": "trial"},
        }
    )
    payload = draft_to_payload(draft)
    assert payload["report"]["preset"] == "acquisition"
    validate_payload(payload)


def test_draft_to_payload_operant_protocol_mode_validates():
    draft = BuilderExperimentDraft.from_dict(
        {
            "learner": "q_learner",
            "agent": "operant_agent",
            "representation": "vector_elemental",
            "policy": {
                "name": "epsilon_greedy",
                "params": {"actions": ["left", "right"], "epsilon": 0.1},
            },
            "protocol": "matching_law",
            "params": {
                "n_trials": 30,
                "schedule_left": {"type": "variable_interval", "value": 30},
                "schedule_right": {"type": "variable_interval", "value": 60},
                "action_labels": ["left", "right"],
            },
            "runtime": {"update_mode": "tick", "record_mode": "trial"},
        }
    )
    payload = draft_to_payload(draft)
    assert payload["report"]["preset"] == "matching_law"
    validate_payload(payload)


def test_draft_to_payload_phase_mode_defaults_to_custom_protocol_preset():
    draft = BuilderExperimentDraft.from_dict(
        {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": "vector_elemental",
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
            ],
        }
    )
    payload = draft_to_payload(draft)
    assert payload["report"]["preset"] == "custom_protocol"
    validate_payload(payload)
