import json
from pathlib import Path

import pytest

from ui import validate_payload as vp
from ui.validate_payload import validate_payload


def test_validate_payload_accepts_phase_mode():
    payload = {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["tone"], "max_compound_size": 2},
            },
            "phases": [
                {
                    "name": "Phase 1",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 1, "alpha": 0.2, "gamma": 0},
                }
            ],
        },
        "report": {"preset": "acquisition"},
    }
    validate_payload(payload)


def test_validate_payload_rejects_missing_experiment():
    with pytest.raises(Exception):
        validate_payload({"report": {"preset": "acquisition"}})


def test_schema_key_and_schema_map(tmp_path):
    assert vp._schema_key(Path("foo.schema.json")) == "foo"
    assert vp._schema_key(Path("bar.json")) == "bar"

    missing_dir = tmp_path / "missing"
    assert vp._build_schema_map(missing_dir) == {}

    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    (schema_dir / "a.schema.json").write_text("{}")
    (schema_dir / "b.schema.json").write_text("{}")
    schema_map = vp._build_schema_map(schema_dir)
    assert set(schema_map.keys()) == {"a", "b"}


def test_validate_top_level_errors(monkeypatch):
    with pytest.raises(vp.ValidationError):
        vp._validate_top_level("bad")

    with pytest.raises(vp.ValidationError):
        vp._validate_top_level({"report": {}})

    with pytest.raises(vp.ValidationError):
        vp._validate_top_level({"experiment": {}})

    with pytest.raises(vp.ValidationError):
        vp._validate_top_level({"experiment": {}, "report": "bad"})

    with pytest.raises(vp.ValidationError):
        vp._validate_top_level({"experiment": "bad", "report": {}})

    def fake_validate(*_):
        raise vp.ValidationError("schema error")

    monkeypatch.setattr(vp, "_validate_schema", fake_validate)
    with pytest.raises(vp.ValidationError):
        vp._validate_top_level({"experiment": {"learner": "x", "agent": "y", "representation": "vector_elemental"}, "report": {}})

    monkeypatch.setattr(vp, "_validate_schema", lambda *_: None)
    with pytest.raises(vp.ValidationError):
        vp._validate_top_level({"experiment": {"agent": "y", "representation": "vector_elemental"}, "report": {}})


def test_validate_policy_guard(monkeypatch):
    exp = {"learner": "x", "agent": "y", "representation": "vector_elemental"}
    vp._validate_policy_guard(exp)

    exp = {
        "learner": "x",
        "agent": "y",
        "representation": "vector_elemental",
        "policy": {"name": "fixed"},
        "protocol": "acquisition",
    }
    with pytest.raises(vp.ValidationError):
        vp._validate_policy_guard(exp)

    called = {}
    monkeypatch.setattr(vp, "_validate_schema", lambda *_: called.setdefault("ok", True))
    exp = {
        "learner": "x",
        "agent": "y",
        "representation": "vector_elemental",
        "policy": {"name": "fixed"},
        "protocol": "operant_conditioning",
    }
    vp._validate_policy_guard(exp)
    assert called.get("ok") is True


def test_validate_protocol_or_phases_branches(monkeypatch):
    exp = {"protocol": "acquisition", "phases": [{"protocol": "acquisition"}]}
    with pytest.raises(vp.ValidationError):
        vp._validate_protocol_or_phases(exp)

    with pytest.raises(vp.ValidationError):
        vp._validate_protocol_or_phases({})

    monkeypatch.setattr(vp, "PROTOCOL_SCHEMA_MAP", {})
    with pytest.raises(vp.ValidationError):
        vp._validate_protocol_or_phases({"protocol": "acquisition"})

    monkeypatch.setattr(vp, "_validate_schema", lambda *_: None)
    monkeypatch.setattr(vp, "PROTOCOL_SCHEMA_MAP", {"acquisition": Path("a.schema.json")})
    vp._validate_protocol_or_phases({"protocol": "acquisition"})

    monkeypatch.setattr(vp, "PHASE_SCHEMA_MAP", {})
    with pytest.raises(vp.ValidationError):
        vp._validate_protocol_or_phases({"phases": ["bad"]})

    with pytest.raises(vp.ValidationError):
        vp._validate_protocol_or_phases({"phases": [{"params": {}}]})

    monkeypatch.setattr(vp, "PHASE_SCHEMA_MAP", {"acquisition": Path("a.schema.json")})
    with pytest.raises(vp.ValidationError):
        vp._validate_protocol_or_phases({"phases": [{"protocol": "unknown"}]})


def test_validate_phase_order_constraints():
    phases = [{"protocol": "nonreinforcement"}]
    with pytest.raises(ValueError):
        vp.validate_phase_order(phases)


def test_validate_payload_top_level_path(monkeypatch):
    monkeypatch.setattr(vp, "_validate_top_level", lambda payload: {"protocol": "acquisition"})
    monkeypatch.setattr(vp, "_validate_policy_guard", lambda exp: None)
    monkeypatch.setattr(vp, "_validate_protocol_or_phases", lambda exp: None)

    vp.validate_payload({"experiment": {}, "report": {}})


def test_validate_payload_accepts_operant_negative_reward_schedule():
    payload = {
        "experiment": {
            "learner": "q_learner",
            "agent": "operant_agent",
            "policy": {
                "name": "epsilon_greedy",
                "params": {"actions": ["action_0"], "epsilon": 0.1},
            },
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["lever"], "max_compound_size": 2},
            },
            "protocol": "operant_conditioning",
            "stimuli": {"cs_plus": ["lever"]},
            "params": {
                "n_trials": 5,
                "consequence_mode": "positive_punishment",
                "reward_schedule": {"type": "fixed_ratio", "value": 1, "reward": -0.5},
            },
        },
        "report": {"preset": "operant_conditioning"},
    }
    validate_payload(payload)


def test_validate_payload_accepts_operant_phase_mode():
    payload = {
        "experiment": {
            "learner": "q_learner",
            "agent": "operant_agent",
            "policy": {
                "name": "epsilon_greedy",
                "params": {"actions": ["action_0"], "epsilon": 0.1},
            },
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["lever"], "max_compound_size": 2},
            },
            "phases": [
                {
                    "name": "Operant Conditioning",
                    "protocol": "operant_conditioning",
                    "stimuli": {"cs_plus": ["lever"]},
                    "params": {
                        "n_trials": 5,
                        "consequence_mode": "positive_reinforcement",
                        "reward_schedule": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
                    },
                }
            ],
        },
        "report": {"preset": "operant_conditioning"},
    }
    validate_payload(payload)


def test_validate_operant_semantics_requires_policy():
    exp = {
        "protocol": "operant_conditioning",
        "params": {"n_trials": 10, "reward_schedule": {"type": "fixed_ratio", "value": 1}},
    }
    with pytest.raises(vp.ValidationError, match="operant experiments require a policy object"):
        vp._validate_operant_payload_semantics(exp)

    shaping_exp = {
        "protocol": "shaping",
        "params": {
            "n_stage_1_trials": 5,
            "n_stage_2_trials": 5,
            "schedule_stage_1": {"type": "fixed_ratio", "value": 1},
            "schedule_stage_2": {"type": "fixed_ratio", "value": 2},
        },
    }
    with pytest.raises(vp.ValidationError, match="operant experiments require a policy object"):
        vp._validate_operant_payload_semantics(shaping_exp)


def test_validate_operant_semantics_rejects_bad_actions():
    exp = {
        "protocol": "operant_conditioning",
        "policy": {"name": "epsilon_greedy", "params": {"actions": [], "epsilon": 0.1}},
        "params": {"n_trials": 10, "reward_schedule": {"type": "fixed_ratio", "value": 1}},
    }
    with pytest.raises(vp.ValidationError, match="at least one action"):
        vp._validate_operant_payload_semantics(exp)

    exp["policy"]["params"]["actions"] = ["a0", "a1"]
    with pytest.raises(vp.ValidationError, match="operant_conditioning requires exactly 1"):
        vp._validate_operant_payload_semantics(exp)

    exp["policy"]["params"]["actions"] = ["a0", "a0"]
    with pytest.raises(vp.ValidationError, match="must be unique"):
        vp._validate_operant_payload_semantics(exp)


def test_validate_operant_semantics_requires_two_actions_for_resurgence():
    exp = {
        "protocol": "resurgence",
        "policy": {"name": "softmax", "params": {"actions": ["a0"], "temperature": 1.0}},
        "params": {
            "n_acquisition_trials": 5,
            "n_suppression_trials": 5,
            "n_resurgence_trials": 5,
        },
    }
    with pytest.raises(vp.ValidationError, match="resurgence requires exactly 2"):
        vp._validate_operant_payload_semantics(exp)


def test_validate_operant_semantics_matching_law_action_shape():
    exp = {
        "protocol": "matching_law",
        "policy": {"name": "softmax", "params": {"actions": ["left", "right", "extra"], "temperature": 1.0}},
        "params": {
            "n_trials": 20,
            "schedule_left": {"type": "variable_interval", "value": 30},
            "schedule_right": {"type": "variable_interval", "value": 60},
            "action_labels": ["left", "left"],
        },
    }
    with pytest.raises(vp.ValidationError, match="two distinct labels"):
        vp._validate_operant_payload_semantics(exp)

    exp["params"]["action_labels"] = ["left", "right"]
    with pytest.raises(vp.ValidationError, match="requires exactly 2"):
        vp._validate_operant_payload_semantics(exp)

    exp["policy"]["params"]["actions"] = ["right", "left"]
    with pytest.raises(vp.ValidationError, match="must match policy params.actions order"):
        vp._validate_operant_payload_semantics(exp)


def test_validate_operant_semantics_matching_law_action_shape_in_phase_mode():
    exp = {
        "phases": [
            {
                "protocol": "matching_law",
                "params": {
                    "n_trials": 20,
                    "schedule_left": {"type": "variable_interval", "value": 30},
                    "schedule_right": {"type": "variable_interval", "value": 60},
                    "action_labels": ["left", "left"],
                },
            }
        ],
        "policy": {"name": "softmax", "params": {"actions": ["left", "right", "extra"], "temperature": 1.0}},
    }
    with pytest.raises(vp.ValidationError, match="two distinct labels"):
        vp._validate_operant_payload_semantics(exp)

    exp["phases"][0]["params"]["action_labels"] = ["left", "right"]
    with pytest.raises(vp.ValidationError, match="requires exactly 2"):
        vp._validate_operant_payload_semantics(exp)
