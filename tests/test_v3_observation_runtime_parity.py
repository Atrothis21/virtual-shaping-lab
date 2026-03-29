from __future__ import annotations

from pathlib import Path

from virtual_shaping_lab.vsl.agent.learning.bundle import LearnerStepResult
from virtual_shaping_lab.vsl.agent.learning.operators import PredictionOutput
from virtual_shaping_lab.vsl.agent.observation import build_executable_observation_preset
from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.program import compile_environment_program
from virtual_shaping_lab.vsl.runtime import build_runtime_observation_adapter


ROOT = Path(__file__).resolve().parents[1]


def test_v3_19_10_runtime_observation_adapter_matches_direct_bundle_execution():
    runtime_adapter = build_runtime_observation_adapter(preset_name="identity_observation")
    executable = build_executable_observation_preset("identity_observation")

    runtime_out = runtime_adapter.step(
        stimulus={"cs_plus": ["tone"], "us": 1.0},
        context_state="A",
    )
    direct_out = executable.bundle.step(
        raw_stimulus={"tone": 1.0, "us": 1.0},
        context_state="A",
        metadata={
            "runtime_observation": {
                "preset_name": "identity_observation",
                "normalization": "runtime_stimulus_v1",
            }
        },
    )

    assert runtime_out.output.to_dict() == direct_out.output.to_dict()


def test_v3_19_10_compiled_environment_routes_observation_through_runtime_adapter_seam():
    class _ObservationAdapter:
        def __init__(self):
            self.calls: list[dict] = []

        def step(self, *, stimulus, context_state=None, metadata=None):
            self.calls.append(
                {
                    "stimulus": stimulus,
                    "context_state": context_state,
                    "metadata": dict(metadata or {}),
                }
            )
            return build_runtime_observation_adapter(preset_name="identity_observation").step(
                stimulus=stimulus,
                context_state=context_state,
                metadata=metadata,
            )

    class _LearnerAdapter:
        def __init__(self):
            self.calls: list[dict] = []

        def step(self, **kwargs):
            self.calls.append(dict(kwargs))
            return LearnerStepResult(
                prediction_output=PredictionOutput.from_state_value(0.0),
                prediction=0.0,
                next_prediction=0.0,
                error=0.0,
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

    observation_adapter = _ObservationAdapter()
    learner_adapter = _LearnerAdapter()

    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Acq",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 2, "outcome": 1.0},
                }
            ]
        }
    )
    env = CompiledProgramTestEnvironment(
        program,
        learner_adapter=learner_adapter,
        observation_adapter=observation_adapter,
    )
    _ = env.reset(seed=1)
    _ = env.step(action=None)

    assert len(observation_adapter.calls) >= 1
    assert len(learner_adapter.calls) == 1
    learner_call = learner_adapter.calls[0]
    assert "observation_features" in learner_call
    assert "observation_feature_names" in learner_call
    assert "stimulus" not in learner_call
    assert "next_stimulus" not in learner_call


def test_v3_19_10_runtime_ownership_harness_uses_canonical_observation_adapter_surface():
    text = (ROOT / "virtual_shaping_lab" / "vsl" / "rollout" / "harness.py").read_text(encoding="utf-8")
    assert "from virtual_shaping_lab.vsl.runtime.observation_adapter import" in text
    assert "RuntimeObservationAdapter" in text
    assert "build_runtime_observation_adapter" in text
    assert "self._observation_adapter.step(" in text

