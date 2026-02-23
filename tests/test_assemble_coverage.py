import pytest

from experiment.assemble import (
    _infer_contexts,
    _infer_phase_contexts,
    _extract_learner_params,
    _is_protocol_phase,
    _is_atomic_phase,
    assemble_experiment,
)
from experiment.config import ExperimentConfig, PhaseConfig


class DummyConfig:
    def __init__(self, phases=None, params=None):
        self.phases = phases or []
        self.params = params or {}


def test_infer_contexts_from_phases_and_params():
    phases = [
        PhaseConfig(
            name="Phase 1",
            protocol="acquisition",
            stimuli={},
            params={"context_a": "A"},
        )
    ]
    config = DummyConfig(phases=phases)
    out = _infer_contexts({}, config)
    assert out["contexts"] == ["A"]

    config = DummyConfig(phases=[], params={"context_b": "B"})
    out = _infer_contexts({}, config)
    assert out["contexts"] == ["B"]


def test_infer_phase_contexts_enabled_and_disabled():
    cfg = DummyConfig(
        phases=[
            PhaseConfig("Same", "acquisition", {}, {}),
            PhaseConfig("Same", "acquisition", {}, {}),
            PhaseConfig("Other", "acquisition", {}, {}),
        ],
        params={},
    )
    cfg.context_inference = {"enabled": True, "max_contexts": 2}
    inferred = _infer_phase_contexts(cfg)
    assert inferred == ["A", "A", "B"]

    cfg.context_inference = {"enabled": False}
    assert _infer_phase_contexts(cfg) == [None, None, None]


def test_extract_learner_params():
    cfg = DummyConfig(
        phases=[PhaseConfig("P", "acquisition", {}, {"alpha": 0.2, "gamma": 0.1})]
    )
    rep = type("Rep", (), {"salience": [1.0, 1.0]})()
    params = _extract_learner_params(cfg, rep, policy_actions=["a0"])
    assert params["alpha"] == 0.2
    assert params["gamma"] == 0.1
    assert params["actions"] == ["a0"]


def test_protocol_phase_helpers():
    assert _is_protocol_phase("extinction") is True
    assert _is_atomic_phase("acquisition") is True


def test_assemble_experiment_phase_mode_with_reward_schedule():
    payload = {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["lever"], "max_compound_size": 2},
            },
            "phases": [
                {
                    "name": "Operant",
                    "protocol": "operant_conditioning",
                    "stimuli": {"cs_plus": ["lever"]},
                    "params": {
                        "n_trials": 1,
                        "reward_schedule": {"type": "fixed_ratio", "value": 1},
                    },
                }
            ],
        },
        "report": {"preset": "acquisition"},
    }
    config = ExperimentConfig.from_payload(payload)
    runtime_units, agent, rep = assemble_experiment(config)
    assert runtime_units


def test_assemble_experiment_protocol_mode_with_policy_string(monkeypatch):
    payload = {
        "experiment": {
            "learner": "td_value",
            "agent": "operant_agent",
            "policy": "epsilon_greedy",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["lever"], "max_compound_size": 2},
            },
            "protocol": "matching_law",
            "stimuli": {"cs_plus": ["lever"]},
            "params": {
                "n_trials": 1,
                "schedule_left": {"type": "fixed_ratio", "value": 1},
                "schedule_right": {"type": "fixed_ratio", "value": 1},
            },
        },
        "report": {"preset": "matching_law"},
    }

    def _fake_build_policy(name, **params):
        return object()

    monkeypatch.setattr("experiment.assemble.build_policy", _fake_build_policy)

    config = ExperimentConfig.from_payload(payload)
    runtime_units, agent, rep = assemble_experiment(config)
    assert runtime_units
