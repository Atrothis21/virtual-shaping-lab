from __future__ import annotations

from pathlib import Path

from virtual_shaping_lab.vsl.agent.learning.bundle import LearnerStepResult
from virtual_shaping_lab.vsl.agent.learning.operators import PredictionOutput
from virtual_shaping_lab.vsl.agent.policy import PolicyOutput
from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.runtime import build_runtime_observation_adapter


ROOT = Path(__file__).resolve().parents[1]


def test_v3_20_10_protocol_loop_is_pre_outcome_policy_then_post_outcome_learner():
    events: list[str] = []

    class _ObservationAdapter:
        def step(self, *, stimulus, context_state=None, metadata=None):
            events.append("observe")
            return build_runtime_observation_adapter(preset_name="identity_observation").step(
                stimulus=stimulus,
                context_state=context_state,
                metadata=metadata,
            )

    class _PolicyAdapter:
        def __init__(self):
            self.calls: list[dict] = []

        def step(self, **kwargs):
            events.append("policy")
            self.calls.append(dict(kwargs))
            return PolicyOutput(
                action="leverpress",
                available_actions=("leverpress",),
                action_scores={"leverpress": 1.0},
                action_probabilities={"leverpress": 1.0},
                metadata={"variant": "test_policy"},
            )

    class _LearnerAdapter:
        def __init__(self):
            self.calls: list[dict] = []

        def step(self, **kwargs):
            events.append("learner")
            self.calls.append(dict(kwargs))
            return LearnerStepResult(
                prediction_output=PredictionOutput.from_state_value(0.0),
                prediction=0.0,
                next_prediction=0.0,
                error=float(kwargs.get("reward", 0.0)),
                done=bool(kwargs.get("done", False)),
                reward=float(kwargs.get("reward", 0.0)),
                features={"tone": 1.0},
                next_features={"tone": 1.0},
                update_features={"tone": 1.0},
                state={},
                attention_state={},
                eligibility_state={},
                measurements={},
            )

    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Operant",
                    "protocol": "operant_conditioning",
                    "stimuli": {"cs_plus": ["lever"]},
                    "params": {"n_trials": 1, "reward": 1.0},
                }
            ]
        }
    )
    policy_adapter = _PolicyAdapter()
    learner_adapter = _LearnerAdapter()
    env = CompiledProgramTestEnvironment(
        program,
        observation_adapter=_ObservationAdapter(),
        policy_adapter=policy_adapter,
        learner_adapter=learner_adapter,
    )

    _ = env.reset(seed=4)
    step = env.step(action=None)

    assert events == ["observe", "policy", "learner"]
    assert step.action == "leverpress"

    assert len(policy_adapter.calls) == 1
    policy_call = policy_adapter.calls[0]
    assert "reward" not in policy_call
    assert "outcome" not in policy_call
    assert "prediction_error" not in policy_call

    assert len(learner_adapter.calls) == 1
    learner_call = learner_adapter.calls[0]
    assert "reward" in learner_call
    assert "observation_features" in learner_call
    assert "stimulus" not in learner_call


def test_v3_20_10_runtime_harness_owns_policy_seam_dispatch():
    text = (ROOT / "virtual_shaping_lab" / "vsl" / "rollout" / "harness.py").read_text(encoding="utf-8")
    assert "from virtual_shaping_lab.vsl.runtime.policy_adapter import" in text
    assert "RuntimePolicyAdapter" in text
    assert "build_runtime_policy_adapter" in text
    assert "self._policy_adapter.step(" in text
    assert text.find("self._policy_adapter.step(") < text.find("self._learner_adapter.step(")
