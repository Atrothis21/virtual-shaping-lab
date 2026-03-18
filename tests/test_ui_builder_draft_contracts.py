from ui.contracts.builder_draft import (
    BuilderDraftValidationError,
    BuilderExperimentDraft,
    BuilderPhaseDraft,
    BuilderRuntimeDraft,
)


def test_builder_runtime_draft_defaults():
    runtime = BuilderRuntimeDraft()
    assert runtime.update_mode == "trial"
    assert runtime.record_mode == "trial"
    assert runtime.strict_records is False
    assert runtime.debug is False


def test_builder_runtime_draft_rejects_invalid_modes():
    try:
        BuilderRuntimeDraft(update_mode="bad")
        assert False, "Expected BuilderDraftValidationError for update_mode"
    except BuilderDraftValidationError:
        pass

    try:
        BuilderRuntimeDraft(record_mode="bad")
        assert False, "Expected BuilderDraftValidationError for record_mode"
    except BuilderDraftValidationError:
        pass


def test_builder_experiment_draft_protocol_mode_round_trip():
    draft = BuilderExperimentDraft.from_dict(
        {
            "program": {"protocol": "acquisition", "params": {"n_trials": 10}},
            "agent": {
                "name": "classical_agent",
                "representation": "vector_elemental",
                "learning": {"rule": "rescorla_wagner", "params": {}, "attention": {"config": {"name": "none", "params": {}}, "initial": {}}},
                "policy": None,
            },
            "runtime": {"update_mode": "trial", "record_mode": "trial"},
        }
    )
    as_dict = draft.to_dict()
    assert as_dict["program"]["phases"][0]["protocol"] == "acquisition"
    assert as_dict["program"]["phases"][0]["params"]["n_trials"] == 10


def test_builder_experiment_draft_phase_mode_round_trip():
    draft = BuilderExperimentDraft.from_dict(
        {
            "program": {
                "phases": [
                    {"protocol": "acquisition", "params": {"n_trials": 5}},
                    {"protocol": "nonreinforcement", "params": {"n_trials": 5}},
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
    as_dict = draft.to_dict()
    assert len(as_dict["program"]["phases"]) == 2
    assert as_dict["program"]["phases"][0]["protocol"] == "acquisition"


def test_builder_experiment_draft_rejects_protocol_and_phases_both():
    try:
        BuilderExperimentDraft.from_dict(
            {
                "program": {
                    "protocol": "acquisition",
                    "phases": [{"protocol": "acquisition", "params": {"n_trials": 1}}],
                },
                "agent": {
                    "name": "classical_agent",
                    "representation": "vector_elemental",
                    "learning": {"rule": "rescorla_wagner", "params": {}, "attention": {"config": {"name": "none", "params": {}}, "initial": {}}},
                    "policy": None,
                },
            }
        )
        assert False, "Expected BuilderDraftValidationError for protocol/phases xor rule"
    except BuilderDraftValidationError:
        pass


def test_builder_phase_draft_rejects_blank_protocol():
    try:
        BuilderPhaseDraft.from_dict({"protocol": "", "params": {}})
        assert False, "Expected BuilderDraftValidationError for blank phase protocol"
    except BuilderDraftValidationError:
        pass

