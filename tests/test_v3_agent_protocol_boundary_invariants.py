from __future__ import annotations

from pathlib import Path

from virtual_shaping_lab.vsl.agent import CompositionalAgent
from virtual_shaping_lab.vsl.agent.learning.bundle import LearnerStepResult
from virtual_shaping_lab.vsl.agent.learning.operators import PredictionOutput
from virtual_shaping_lab.vsl.agent.policy import PolicyOutput
from virtual_shaping_lab.vsl.contracts import Outcome, TaskInput
from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.protocol import (
    AdvanceOutput,
    ConsequenceOutput,
    EmissionOutput,
    ProtocolStepResult,
    StopOutput,
)
from virtual_shaping_lab.vsl.runtime import build_runtime_observation_adapter


ROOT = Path(__file__).resolve().parents[1]


def test_v3_20_15_compositional_agent_keeps_reward_outcome_out_of_policy_path():
    policy_calls: list[dict] = []
    learner_calls: list[dict] = []

    class _PolicyAdapter:
        def step(self, **kwargs):
            policy_calls.append(dict(kwargs))
            return PolicyOutput(
                action="leverpress",
                available_actions=("leverpress",),
                action_scores={"leverpress": 1.0},
                action_probabilities={"leverpress": 1.0},
                metadata={"variant": "policy_stub"},
            )

    class _LearnerAdapter:
        def step(self, **kwargs):
            learner_calls.append(dict(kwargs))
            return LearnerStepResult(
                prediction_output=PredictionOutput.from_state_value(0.0),
                prediction=0.0,
                next_prediction=0.0,
                error=float(kwargs.get("reward", 0.0)),
                done=bool(kwargs.get("done", False)),
                reward=float(kwargs.get("reward", 0.0)),
                features={"tone": 1.0},
                next_features=None,
                update_features={"tone": 1.0},
                state={},
                attention_state={},
                eligibility_state={},
                measurements={},
            )

    agent = CompositionalAgent(
        observation_adapter=build_runtime_observation_adapter(preset_name="identity_observation"),
        policy_adapter=_PolicyAdapter(),
        learner_adapter=_LearnerAdapter(),
    )
    pre = agent.pre_outcome_step(
        TaskInput(
            stimuli={"cs_plus": ["tone"]},
            context="A",
            t=0,
            phase="operant_conditioning",
            available_actions=("leverpress",),
        )
    )
    _ = agent.learn(
        observation=pre.observation_output,
        prediction=pre.prediction_output,
        action=pre.action.value,
        outcome=Outcome(reward=1.0, next_stimuli={}, terminated=True),
    )

    assert len(policy_calls) == 1
    assert "reward" not in policy_calls[0]
    assert "outcome" not in policy_calls[0]
    assert "prediction_error" not in policy_calls[0]

    assert len(learner_calls) == 1
    assert "reward" in learner_calls[0]
    assert "observation_features" in learner_calls[0]
    assert "stimulus" not in learner_calls[0]


def test_v3_21_10_protocol_runtime_does_not_compute_agent_learning_internals():
    events: list[str] = []
    protocol_calls: list[dict] = []

    class _ProtocolAdapter:
        preset_name = "test_protocol"

        def reset(self):
            return None

        def emit(self, *, phase_payload=None, metadata=None):
            events.append("protocol_emit")
            protocol_calls.append({"stage": "emit", "phase_payload": dict(phase_payload or {}), "metadata": dict(metadata or {})})
            return EmissionOutput(
                stimulus={"lever": 1.0},
                context="A",
                available_actions=("leverpress",),
                metadata={"variant": "protocol_emit"},
            )

        def resolve(self, *, action=None, metadata=None):
            events.append("protocol_resolve")
            protocol_calls.append({"stage": "resolve", "action": action, "metadata": dict(metadata or {})})
            return ProtocolStepResult(
                emission=EmissionOutput(
                    stimulus={"lever": 1.0},
                    context="A",
                    available_actions=("leverpress",),
                    metadata={"variant": "protocol_emit"},
                ),
                consequence=ConsequenceOutput(reward=1.0, done=False, metadata={"variant": "protocol_consequence"}),
                advance=AdvanceOutput(t=1, dt_s=1.0, phase_step=1, metadata={"variant": "protocol_advance"}),
                stop=StopOutput(should_stop=False, reason=None, metadata={"variant": "protocol_stop"}),
                metadata={
                    "pipeline_order": ["emit", "consequence", "advance", "stop", "finalize"],
                    "stage_traces": {},
                },
            )

    class _PolicyAdapter:
        def step(self, **kwargs):
            events.append("policy")
            return PolicyOutput(
                action="leverpress",
                available_actions=("leverpress",),
                action_scores={"leverpress": 1.0},
                action_probabilities={"leverpress": 1.0},
                metadata={"variant": "policy_stub"},
            )

    class _LearnerAdapter:
        def step(self, **kwargs):
            events.append("learner")
            return LearnerStepResult(
                prediction_output=PredictionOutput.from_state_value(0.0),
                prediction=0.0,
                next_prediction=0.0,
                error=float(kwargs.get("reward", 0.0)),
                done=bool(kwargs.get("done", False)),
                reward=float(kwargs.get("reward", 0.0)),
                features={"lever": 1.0},
                next_features={"lever": 1.0},
                update_features={"lever": 1.0},
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
    env = CompiledProgramTestEnvironment(
        program,
        observation_adapter=build_runtime_observation_adapter(preset_name="identity_observation"),
        policy_adapter=_PolicyAdapter(),
        learner_adapter=_LearnerAdapter(),
        protocol_adapter=_ProtocolAdapter(),
    )

    _ = env.reset(seed=11)
    _ = env.step(action=None)

    assert events == ["protocol_emit", "policy", "protocol_resolve", "learner"]
    resolve_call = next(call for call in protocol_calls if call["stage"] == "resolve")
    assert resolve_call["action"] == "leverpress"
    assert "prediction_error" not in str(resolve_call)
    assert "delta" not in str(resolve_call)
    assert "weights" not in str(resolve_call)


def test_v3_21_10_pre_outcome_step_has_no_hidden_learn_dispatch():
    learner_calls: list[dict] = []

    class _LearnerAdapter:
        def step(self, **kwargs):
            learner_calls.append(dict(kwargs))
            return LearnerStepResult(
                prediction_output=PredictionOutput.from_state_value(0.0),
                prediction=0.0,
                next_prediction=0.0,
                error=0.0,
                done=False,
                reward=0.0,
                features={"tone": 1.0},
                next_features={"tone": 1.0},
                update_features={"tone": 1.0},
                state={},
                attention_state={},
                eligibility_state={},
                measurements={},
            )

    agent = CompositionalAgent(
        observation_adapter=build_runtime_observation_adapter(preset_name="identity_observation"),
        policy_adapter=type(
            "_PolicyAdapter",
            (),
            {
                "step": lambda self, **kwargs: PolicyOutput(
                    action="leverpress",
                    available_actions=("leverpress",),
                    action_scores={"leverpress": 1.0},
                    action_probabilities={"leverpress": 1.0},
                    metadata={"variant": "policy_stub"},
                )
            },
        )(),
        learner_adapter=_LearnerAdapter(),
    )

    _ = agent.pre_outcome_step(
        TaskInput(
            stimuli={"cs_plus": ["tone"]},
            context="A",
            t=0,
            phase="operant_conditioning",
            available_actions=("leverpress",),
        )
    )
    assert learner_calls == []


def test_v3_21_10_runtime_protocol_adapter_keeps_learning_tokens_outside_protocol_surface():
    text = (ROOT / "virtual_shaping_lab" / "vsl" / "runtime" / "protocol_adapter.py").read_text(encoding="utf-8")
    assert "prediction_error" not in text
    assert "delta" not in text
    assert "weights" not in text
