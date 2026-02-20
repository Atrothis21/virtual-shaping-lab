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
