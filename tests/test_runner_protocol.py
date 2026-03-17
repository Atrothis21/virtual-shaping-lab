from typing import Any, Dict, List

import pytest
from experiment.runner import Runner
import json

from experiment.sinks import CompositeSink, InMemorySink, JsonlSink
from experiment.phases.base import PhaseBase
from experiment.domain.types import EventSpec, StepResult, TrialSchedule, TrialTimeSpec
from protocols.base import BaseProtocol
from domain.types import Observation


class DummyPhase(PhaseBase):
    name = "dummy"

    def __init__(self, agent, n_trials=2):
        super().__init__(agent=agent, stimuli=["tone"], n_trials=n_trials, params={})

    def sample_trial(self) -> Dict[str, Any]:
        return {"stimulus": "tone"}

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        return {"reward": 0.0, "state": trial_spec["stimulus"], "prediction": 0.5, "action": None}

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        return None

    def record_trial(self, trial_spec: Dict[str, Any], outcome: Any) -> Dict[str, Any]:
        return {
            "phase": self.name,
            "trial": self.trial_index,
            "prediction": outcome["prediction"],
        }

    def reset(self, ctx):
        self.trial_index = 0
        self.records = []
        self._rng = ctx.rng

    def iter_steps(self, ctx):
        if self.trial_index != 0:
            self.reset(ctx)
        while self.has_next_trial():
            record = self.step()
            if record is None:
                continue
            yield StepResult(
                observation=Observation(stimuli=["tone"], context=record.get("context", "A")),
                reward=float(record.get("reward", 0.0)),
                learning_enabled=self.allows_learning,
                done=not self.has_next_trial(),
                metadata={"record": record},
            )


class LegacyOnlyPhase(PhaseBase):
    name = "legacy_only"

    def __init__(self, agent, n_trials=1):
        super().__init__(agent=agent, stimuli=["tone"], n_trials=n_trials, params={})

    def sample_trial(self):
        return {"stimulus": "tone"}

    def run_trial(self, trial_spec):
        return {"reward": 0.0, "state": "s", "prediction": 0.5, "action": None}

    def apply_learning(self, trial_spec, outcome):
        return None

    def record_trial(self, trial_spec, outcome):
        return {"phase": self.name, "trial": self.trial_index, "prediction": outcome["prediction"]}


class DummyProtocol(BaseProtocol):
    name = "dummy_protocol"

    def build_phases(self) -> List[Any]:
        self.n_trials = 2
        return [DummyPhase(self.agent, n_trials=2)]


class DummyAgent:
    def reset(self):
        return None

    def observe(self, observation):
        return observation

    def update(self, state, reward, action=None):
        return None

    def value(self, state, action=None):
        return 0.5


class DummyRunnableUnit:
    def __init__(self):
        self.reset_called = False

    def reset(self, ctx):
        self.reset_called = True

    def iter_steps(self, ctx):
        yield StepResult(
            observation=Observation(stimuli=["tone"], context="A"),
            reward=0.1,
            done=False,
            metadata={"record": {"phase": "iter_phase", "trial": 0, "prediction": 0.2}},
        )
        yield StepResult(
            observation=Observation(stimuli=["tone"], context="A"),
            reward=0.2,
            done=True,
            metadata={"record": {"phase": "iter_phase", "trial": 1, "prediction": 0.3}},
        )


class SeededRunnableUnit:
    def reset(self, ctx):
        return None

    def iter_steps(self, ctx):
        # Deterministic given runner seed/context RNG.
        reward = float(ctx.rng.integers(0, 1000))
        yield StepResult(
            observation=Observation(stimuli=["tone"], context="A"),
            reward=reward,
            done=True,
            metadata={"record": {"phase": "seeded", "trial": 0, "reward": reward}},
        )


class MultiSeededRunnableUnit:
    def reset(self, ctx):
        return None

    def iter_steps(self, ctx):
        for i in range(3):
            reward = float(ctx.rng.integers(0, 1000))
            yield StepResult(
                observation=Observation(stimuli=["tone"], context="A"),
                reward=reward,
                done=(i == 2),
                metadata={"record": {"phase": "seeded_multi", "trial": i, "reward": reward}},
            )


class TimedRunnableUnit:
    def reset(self, ctx):
        return None

    def iter_steps(self, ctx):
        spec = TrialTimeSpec(
            duration_s=1.0,
            dt_s=0.5,
            events=[
                EventSpec(event_type="stimulus", start_s=0.0, end_s=0.5, metadata={"stimulus": "tone"}),
                EventSpec(event_type="reward", start_s=0.5, end_s=1.0, magnitude=1.0),
            ],
        )
        yield StepResult(
            observation=Observation(stimuli=[], context="A"),
            reward=0.0,
            done=True,
            metadata={
                "record": {"phase": "timed", "trial": 0},
                "trial_schedule": TrialSchedule(time=spec, available_actions=[]),
            },
        )


class ClassicalPolicyTrackingAgent:
    def __init__(self):
        self.observe_calls = 0
        self.act_calls = 0

    def reset(self):
        return None

    def observe(self, observation):
        self.observe_calls += 1
        return observation

    def act(self, state, actions=None, rng=None):
        self.act_calls += 1
        return None

    def value(self, state, action=None):
        return 0.0


class OperantPolicyTrackingAgent(ClassicalPolicyTrackingAgent):
    def __init__(self):
        super().__init__()
        self.last_actions = None

    def act(self, state, actions=None, rng=None):
        self.act_calls += 1
        self.last_actions = list(actions) if actions is not None else []
        return self.last_actions[0] if self.last_actions else None


class PerformanceOnlyTrackingAgent(OperantPolicyTrackingAgent):
    def __init__(self):
        super().__init__()
        self.learn_calls = 0

    def learn(self, transition):
        self.learn_calls += 1
        return None


class SeededPolicyLearningAgent:
    def __init__(self):
        self.weight = 0.0
        self.prediction_errors = []
        self.weights_after_update = []
        self.actions = []

    def observe(self, observation):
        return observation

    def act(self, state, actions=None, rng=None):
        pool = list(actions or [])
        if not pool:
            return None
        idx = int(rng.integers(0, len(pool)))
        action = pool[idx]
        self.actions.append(action)
        return action

    def learn(self, transition):
        prediction_error = float(transition.r - self.weight)
        self.prediction_errors.append(prediction_error)
        self.weight += 0.5 * prediction_error
        self.weights_after_update.append(self.weight)

    def value(self, state, action=None):
        return self.weight


class ActionlessTimedRunnableUnit:
    def __init__(self, agent):
        self.agent = agent

    def reset(self, ctx):
        return None

    def iter_steps(self, ctx):
        spec = TrialTimeSpec(duration_s=1.0, dt_s=0.5, events=[])
        yield StepResult(
            observation=Observation(stimuli=["tone"], context="A"),
            reward=0.0,
            done=True,
            metadata={
                "record": {"phase": "classical_timed", "trial": 0},
                "trial_schedule": TrialSchedule(time=spec, available_actions=[]),
            },
        )


class ActionTimedRunnableUnit:
    def __init__(self, agent):
        self.agent = agent

    def reset(self, ctx):
        return None

    def iter_steps(self, ctx):
        spec = TrialTimeSpec(duration_s=1.0, dt_s=0.5, events=[])
        yield StepResult(
            observation=Observation(stimuli=["lever"], context="A"),
            reward=0.0,
            done=True,
            metadata={
                "record": {"phase": "operant_timed", "trial": 0},
                "trial_schedule": TrialSchedule(
                    time=spec,
                    available_actions=["press", "withhold"],
                ),
            },
        )


class CapturingHooks:
    def __init__(self):
        self.events = []

    def on_unit_start(self, *, unit, ctx):
        self.events.append(("unit_start", type(unit).__name__))

    def on_unit_end(self, *, unit, ctx, records):
        self.events.append(("unit_end", type(unit).__name__, len(records)))

    def on_trial_start(self, *, unit, ctx, trial_id, step):
        self.events.append(("trial_start", type(unit).__name__, trial_id))

    def on_tick(self, *, unit, ctx, trial_id, tick, observation, action, reward, metadata):
        self.events.append(("tick", type(unit).__name__, trial_id, tick, reward))

    def on_trial_end(self, *, unit, ctx, trial_id, records):
        self.events.append(("trial_end", type(unit).__name__, trial_id, len(records)))


def test_runner_handles_phase():
    agent = DummyAgent()
    phase = DummyPhase(agent, n_trials=1)
    runner = Runner(phase)
    records = runner.run()
    assert len(records) == 1
    assert records[0]["phase_name"] == "dummy"


def test_runner_handles_protocol():
    agent = DummyAgent()
    protocol = DummyProtocol(agent=agent)
    runner = Runner(protocol)
    records = runner.run()
    assert len(records) == 2
    assert records[0]["subphase_name"] == "dummy"


def test_runner_handles_runnable_unit_iter_steps():
    unit = DummyRunnableUnit()
    runner = Runner(unit)
    records = runner.run()
    assert unit.reset_called is True
    assert len(records) == 2
    assert records[0]["phase_name"] == "iter_phase"


def test_runner_seed_controls_runnable_unit_rng_deterministically():
    r1 = Runner(SeededRunnableUnit(), seed=123).run()
    r2 = Runner(SeededRunnableUnit(), seed=123).run()
    r3 = Runner(SeededRunnableUnit(), seed=456).run()

    assert r1[0]["reward"] == r2[0]["reward"]
    assert r1[0]["reward"] != r3[0]["reward"]


def test_runner_seed_replay_is_identical_for_full_record_stream():
    r1 = Runner(MultiSeededRunnableUnit(), seed=123).run()
    r2 = Runner(MultiSeededRunnableUnit(), seed=123).run()
    r3 = Runner(MultiSeededRunnableUnit(), seed=456).run()

    assert r1 == r2
    assert r1 != r3


def test_runner_emits_to_sink_and_returns_records():
    agent = DummyAgent()
    phase = DummyPhase(agent, n_trials=1)
    sink = InMemorySink()
    runner = Runner(phase, sink=sink)
    records = runner.run()
    assert len(records) == 1
    assert sink.records == records
    assert sink.closed is False


def test_runner_record_mode_tick_emits_tick_records_for_timed_schedule():
    records = Runner(
        TimedRunnableUnit(),
        settings={"record_mode": "tick"},
    ).run()
    assert len(records) == 2
    assert records[0]["phase_name"] == "timed"
    assert records[0]["tick"] == 0
    assert records[1]["reward"] == 1.0


def test_runner_uses_composed_runtime_settings_when_direct_modes_absent():
    records = Runner(
        TimedRunnableUnit(),
        settings={
            "composed_parameters": {
                "runtime": {
                    "update_mode": "trial",
                    "record_mode": "tick",
                }
            }
        },
    ).run()
    assert len(records) == 2
    assert records[0]["tick"] == 0


def test_runner_emits_debug_payload_when_runtime_debug_enabled():
    records = Runner(
        TimedRunnableUnit(),
        settings={
            "composed_parameters": {
                "runtime": {
                    "update_mode": "trial",
                    "record_mode": "tick",
                    "debug": True,
                }
            }
        },
    ).run()
    assert len(records) == 2
    assert "debug" in records[0]
    assert isinstance(records[0]["debug"].get("active_features"), list)
    assert "prediction_error" in records[0]["debug"]


def test_runner_debug_mode_trial_omits_tick_debug_payloads():
    records = Runner(
        TimedRunnableUnit(),
        settings={
            "composed_parameters": {
                "runtime": {
                    "update_mode": "trial",
                    "record_mode": "tick",
                    "debug": True,
                    "debug_mode": "trial",
                }
            }
        },
    ).run()
    assert len(records) == 2
    assert all("debug" not in rec for rec in records)


def test_runner_rejects_legacy_phase_without_iter_steps():
    agent = DummyAgent()
    phase = LegacyOnlyPhase(agent, n_trials=1)
    runner = Runner(phase)
    try:
        runner.run()
        assert False, "Expected runner to reject legacy phase units without iter_steps(context)"
    except TypeError as exc:
        assert "iter_steps(context)" in str(exc)


def test_runner_hooks_emit_unit_and_trial_lifecycle_events():
    hooks = CapturingHooks()
    records = Runner(DummyRunnableUnit(), hooks=hooks).run()
    assert len(records) == 2
    assert hooks.events[0][0] == "unit_start"
    assert hooks.events[1] == ("trial_start", "DummyRunnableUnit", 0)
    assert hooks.events[2] == ("trial_end", "DummyRunnableUnit", 0, 1)
    assert hooks.events[3] == ("trial_start", "DummyRunnableUnit", 1)
    assert hooks.events[4] == ("trial_end", "DummyRunnableUnit", 1, 1)
    assert hooks.events[-1] == ("unit_end", "DummyRunnableUnit", 2)


def test_runner_hooks_emit_tick_events_for_timed_schedule():
    hooks = CapturingHooks()
    records = Runner(
        TimedRunnableUnit(),
        settings={"record_mode": "tick"},
        hooks=hooks,
    ).run()
    assert len(records) == 2
    tick_events = [e for e in hooks.events if e[0] == "tick"]
    assert len(tick_events) == 2
    assert tick_events[0][3] == 0
    assert tick_events[1][4] == 1.0


def test_runner_classical_timed_flow_does_not_call_policy_without_available_actions():
    agent = ClassicalPolicyTrackingAgent()
    records = Runner(ActionlessTimedRunnableUnit(agent), settings={"record_mode": "tick"}).run()

    assert len(records) == 2
    assert agent.observe_calls == 2
    assert agent.act_calls == 0
    assert all(record["action"] is None for record in records)


def test_runner_actionless_timed_flow_is_stable_with_null_action_baseline():
    agent = ClassicalPolicyTrackingAgent()
    records = Runner(ActionlessTimedRunnableUnit(agent), settings={"record_mode": "tick"}).run()

    assert all(record["action"] is None for record in records)
    assert all(record["reward"] == pytest.approx(0.0) for record in records)


def test_runner_operant_timed_flow_calls_policy_when_actions_are_available():
    agent = OperantPolicyTrackingAgent()
    records = Runner(ActionTimedRunnableUnit(agent), settings={"record_mode": "tick"}).run()

    assert len(records) == 2
    assert agent.observe_calls == 2
    assert agent.act_calls == 2
    assert agent.last_actions == ["press", "withhold"]
    assert all(record["action"] == "press" for record in records)


def test_runner_policy_path_does_not_imply_learning_without_update_mode_tick():
    agent = PerformanceOnlyTrackingAgent()
    records = Runner(
        ActionTimedRunnableUnit(agent),
        settings={"record_mode": "tick", "update_mode": "trial"},
    ).run()

    assert len(records) == 2
    assert agent.act_calls == 2
    assert agent.learn_calls == 0


def test_runner_seed_replay_is_identical_for_policy_actions_and_learning_updates():
    def execute(seed):
        agent = SeededPolicyLearningAgent()
        records = Runner(
            ActionTimedRunnableUnit(agent),
            seed=seed,
            settings={"record_mode": "tick", "update_mode": "tick"},
        ).run()
        return records, list(agent.actions), list(agent.prediction_errors), list(agent.weights_after_update)

    rec_a, actions_a, pe_a, weights_a = execute(11)
    rec_b, actions_b, pe_b, weights_b = execute(11)
    rec_c, actions_c, pe_c, weights_c = execute(19)

    assert rec_a == rec_b
    assert actions_a == actions_b
    assert pe_a == pe_b
    assert weights_a == weights_b
    assert (rec_a, actions_a, pe_a, weights_a) != (rec_c, actions_c, pe_c, weights_c)


def test_runner_jsonl_sink_writes_append_only_records(tmp_path):
    path = tmp_path / "records.jsonl"
    sink = JsonlSink(path)
    records = Runner(DummyRunnableUnit(), sink=sink).run()
    assert len(records) == 2
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    parsed = [json.loads(line) for line in lines]
    assert parsed[0]["phase_name"] == "iter_phase"
    assert parsed[1]["trial"] == 1


def test_runner_composite_sink_fanout(tmp_path):
    mem = InMemorySink()
    jsonl = JsonlSink(tmp_path / "records.jsonl")
    sink = CompositeSink([mem, jsonl])
    records = Runner(DummyRunnableUnit(), sink=sink).run()
    assert len(records) == 2
    assert len(mem.records) == 2
    lines = (tmp_path / "records.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert sink.closed is False
