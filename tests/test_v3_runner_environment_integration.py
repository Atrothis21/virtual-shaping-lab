from __future__ import annotations

from experiment.runner import Runner
from virtual_shaping_lab.vsl.environment import CompiledProgramTestEnvironment
from virtual_shaping_lab.vsl.environment.contracts import (
    EnvironmentReset,
    EnvironmentStep,
    EnvironmentTermination,
)
from virtual_shaping_lab.vsl.environment.trial_state import TrialState
from virtual_shaping_lab.vsl.operator import OperatorPipeline, OperatorStage
from virtual_shaping_lab.vsl.program import compile_environment_program


def _compiled_classical_env() -> CompiledProgramTestEnvironment:
    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Acq",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 3, "outcome": 1.0},
                },
                {
                    "name": "Ext",
                    "protocol": "extinction",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 2, "outcome": 0.0},
                },
            ]
        }
    )
    return CompiledProgramTestEnvironment(program)


def _compiled_operant_env() -> CompiledProgramTestEnvironment:
    program = compile_environment_program(
        {
            "phases": [
                {
                    "name": "Operant",
                    "protocol": "operant_conditioning",
                    "stimuli": {"cs_plus": ["lever"]},
                    "params": {"n_trials": 3, "reward": 1.0},
                }
            ]
        }
    )
    return CompiledProgramTestEnvironment(program)


def test_runner_executes_environment_contract_end_to_end():
    records = Runner(_compiled_classical_env(), seed=11).run()
    assert len(records) == 5
    assert records[0]["phase_name"] == "acquisition"
    assert records[-1]["phase_name"] == "extinction"
    assert records[-1]["done"] is True


def test_runner_environment_path_emits_trial_state_metadata():
    records = Runner(_compiled_classical_env(), seed=3).run()
    assert records
    for rec in records:
        ts = rec["metadata"]["trial_state"]
        assert isinstance(ts, dict)
        assert set(("s", "x", "z", "w", "a", "u", "y", "m")).issubset(ts.keys())
        op = rec["metadata"]["operator_pipeline"]
        assert "declared_stage_keys" in op
        assert "executed_stage_keys" in op
        assert "pipeline_hash" in op


def test_runner_environment_replay_is_hash_identical_for_10_of_10_runs():
    streams = [Runner(_compiled_classical_env(), seed=17).run() for _ in range(10)]
    baseline = streams[0]
    assert all(stream == baseline for stream in streams[1:])


def test_runner_executes_operant_environment_contract_with_action_semantics():
    records = Runner(_compiled_operant_env(), seed=19).run()
    assert records
    for rec in records:
        ts = rec["metadata"]["trial_state"]
        assert ts["u"] is None
        assert ts["a"] == []
        assert rec["metadata"]["termination"]["reason"] in {"running", "terminal"}


def test_runner_environment_execution_uses_declared_operator_pipeline_stage_sequence():
    pipeline = OperatorPipeline(
        stages=[
            OperatorStage(key="Phi"),
            OperatorStage(key="Policy"),
            OperatorStage(key="Env"),
            OperatorStage(key="Err"),
            OperatorStage(key="Measure"),
        ]
    )
    records = Runner(
        _compiled_classical_env(),
        seed=5,
        settings={"operator_pipeline": pipeline.to_dict()},
    ).run()
    assert records
    for rec in records:
        op = rec["metadata"]["operator_pipeline"]
        assert op["declared_stage_keys"] == list(pipeline.stage_keys())
        assert op["executed_stage_keys"] == list(pipeline.stage_keys())


def test_runner_environment_execution_rejects_pipeline_without_env_stage():
    pipeline = OperatorPipeline(
        stages=[OperatorStage(key="Phi"), OperatorStage(key="Policy"), OperatorStage(key="Err")]
    )
    try:
        Runner(
            _compiled_classical_env(),
            seed=5,
            settings={"operator_pipeline": pipeline.to_dict()},
        ).run()
        assert False, "Expected runner to reject environment pipeline without Env stage."
    except ValueError as exc:
        assert "must declare an 'Env' stage" in str(exc)


def test_runner_environment_execution_rejects_pipeline_without_measure_stage():
    pipeline = OperatorPipeline(
        stages=[OperatorStage(key="Policy"), OperatorStage(key="Env"), OperatorStage(key="Err")]
    )
    try:
        Runner(
            _compiled_classical_env(),
            seed=5,
            settings={"operator_pipeline": pipeline.to_dict()},
        ).run()
        assert False, "Expected runner to reject environment pipeline without Measure stage."
    except ValueError as exc:
        assert "must declare a 'Measure' stage" in str(exc)


def test_runner_environment_pipeline_noncommutativity_guard_under_stage_order_mutation():
    class _PolicyAgent:
        def act(self, state=None, actions=None, rng=None):
            _ = state, actions, rng
            return "press"

    class _ActionSensitiveEnv:
        def __init__(self):
            self._done = False
            self.agent = _PolicyAgent()

        @property
        def done(self):
            return self._done

        def reset(self, *, seed=None):
            _ = seed
            self._done = False
            return EnvironmentReset(seed=seed, done=False, metadata={})

        def step(self, action=None):
            self._done = True
            reward = 1.0 if action == "press" else 0.0
            ts = TrialState.with_action_semantics(
                s={"step": 0},
                x={},
                z={"context": "A"},
                w={},
                y=reward,
                is_operant=True,
                action=action,
                available_actions=["press"],
                prediction=None,
                error=None,
            )
            return EnvironmentStep(
                step_index=0,
                segment_key="mut_0",
                protocol="operant_conditioning",
                trial_type="operant_trial",
                trial_index=0,
                action=action,
                stimulus={},
                reward=reward,
                done=True,
                trial_state=ts,
                termination=EnvironmentTermination(done=True, reason="terminal"),
                metadata={},
            )

    pipeline_policy_first = OperatorPipeline(
        stages=[OperatorStage(key="Policy"), OperatorStage(key="Env"), OperatorStage(key="Err"), OperatorStage(key="Measure")]
    )
    pipeline_env_first = OperatorPipeline(
        stages=[OperatorStage(key="Env"), OperatorStage(key="Policy"), OperatorStage(key="Err"), OperatorStage(key="Measure")]
    )

    records_policy_first = Runner(
        _ActionSensitiveEnv(),
        seed=7,
        settings={"operator_pipeline": pipeline_policy_first.to_dict()},
    ).run()
    records_env_first = Runner(
        _ActionSensitiveEnv(),
        seed=7,
        settings={"operator_pipeline": pipeline_env_first.to_dict()},
    ).run()

    assert records_policy_first[0]["reward"] == 1.0
    assert records_env_first[0]["reward"] == 0.0


def test_runner_environment_path_requires_typed_trial_state():
    class _BadEnv:
        def __init__(self):
            self._done = False

        def reset(self, *, seed=None):
            _ = seed
            self._done = False

        @property
        def done(self):
            return self._done

        def step(self, action=None):
            _ = action
            self._done = True
            return EnvironmentStep(
                step_index=0,
                segment_key="bad_0",
                protocol="acquisition",
                trial_type="acquisition_trial",
                trial_index=0,
                action=None,
                stimulus={},
                reward=0.0,
                done=True,
                trial_state=None,
                termination=EnvironmentTermination(done=True, reason="terminal"),
                metadata={},
            )

    try:
        Runner(_BadEnv(), seed=1).run()
        assert False, "Expected runner to reject environment step without typed TrialState."
    except TypeError as exc:
        assert "typed TrialState" in str(exc)
