from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.spec import (
    AgentSpec,
    AnalysisSpec,
    EnvironmentProgramSpec,
    ExperimentSpec,
    LearnerSpec,
    PolicySpec,
    ProgramSpec,
    RepresentationSpec,
    RuntimeSpec,
)


def _sample_spec() -> ExperimentSpec:
    return ExperimentSpec(
        program=ProgramSpec(
            phases=[{"name": "Phase 1", "protocol": "acquisition", "params": {"n_trials": 1}}],
            resolved_phase_contexts=["A"],
        ),
        agent=AgentSpec(
            agent="classical_agent",
            representation=RepresentationSpec(name="vector_elemental", params={"stimuli": ["tone"]}),
            learner=LearnerSpec(
                rule="rescorla_wagner",
                params={},
                attention_initial={"tone": 1.0},
                attention_config={"name": "none", "params": {}},
            ),
            policy=None,
        ),
        runtime=RuntimeSpec(
            runtime={"seed": 11, "record_mode": "trial"},
            context_inference={"enabled": False, "max_contexts": 3},
            resolved_plan=True,
            composed_parameters={"learner": {"algorithm": "rescorla_wagner"}},
        ),
        analysis=AnalysisSpec(report_preset="acquisition"),
        environment_program=EnvironmentProgramSpec(segments=[{"key": "acq"}], metadata={"version": 1}),
        canonical_payload={"experiment": {"program": {"phases": []}, "agent": {}, "runtime": {}}, "report": {"preset": "acquisition"}},
    )


def test_v3_typed_spec_roundtrip():
    spec = _sample_spec()
    blob = spec.to_dict()
    rebuilt = ExperimentSpec.from_dict(blob)
    assert rebuilt.to_dict() == blob


def test_v3_typed_spec_json_roundtrip_is_deterministic():
    spec = _sample_spec()
    blob = spec.to_json()
    rebuilt = ExperimentSpec.from_json(blob)
    assert rebuilt.to_dict() == spec.to_dict()
    assert rebuilt.to_json() == blob


def test_v3_typed_spec_stable_hash_repeats():
    spec = _sample_spec()
    hashes = [spec.stable_hash() for _ in range(10)]
    assert len(set(hashes)) == 1


def test_v3_typed_spec_validation_rejects_bad_types():
    with pytest.raises(ValueError, match="RepresentationSpec.name"):
        RepresentationSpec(name="", params={})

    with pytest.raises(ValueError, match="LearnerSpec.rule"):
        LearnerSpec(rule="", params={})

    with pytest.raises(ValueError, match="AnalysisSpec.report_preset"):
        AnalysisSpec(report_preset="")

    with pytest.raises(ValueError, match="AgentSpec.policy"):
        AgentSpec(
            agent="classical_agent",
            representation=RepresentationSpec(name="vector_elemental", params={}),
            learner=LearnerSpec(rule="rescorla_wagner", params={}),
            policy="bad",  # type: ignore[arg-type]
        )


def test_v3_policy_spec_serialization():
    policy = PolicySpec(name="epsilon_greedy", params={"epsilon": 0.1, "actions": ["left", "right"]})
    assert PolicySpec.from_dict(policy.to_dict()) == policy
