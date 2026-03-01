from types import SimpleNamespace

import pytest

from experiment import assemble as assemble_mod
from experiment.config import (
    ConfigPipeline,
    ConfigParser,
    ExperimentConfig,
    PhaseConfig,
    PayloadNormalizer,
    PayloadValidator,
    PlanBuilder,
)
from experiment.domain.types import ExperimentPlan


def _base_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {
                    "stimuli": ["tone", "noise"],
                    "max_compound_size": 2,
                },
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


def test_attention_normalization_accepts_object():
    payload = _base_payload()
    payload["experiment"]["attention"] = {
        "tone": {"attention": 0.8},
        "noise": 0.4,
    }
    cfg = ExperimentConfig.from_payload(payload)
    assert cfg.attention["tone"] == 0.8
    assert cfg.attention["noise"] == 0.4


def test_similarity_matrix_validation_rejects_bad_size():
    payload = _base_payload()
    payload["experiment"]["representation"]["params"]["similarity"] = {
        "type": "matrix",
        "values": [
            [1.0, 0.2],
            [0.2, 1.0],
            [0.1, 0.3],
        ],
    }
    with pytest.raises(ValueError):
        ExperimentConfig.from_payload(payload)


def test_runtime_constraints_require_prior_learning():
    payload = _base_payload()
    payload["experiment"]["phases"] = [
        {
            "name": "Phase 1",
            "protocol": "nonreinforcement",
            "stimuli": {"cs_plus": ["tone"]},
            "params": {"n_trials": 1, "alpha": 0.2, "gamma": 0},
        }
    ]
    with pytest.raises(ValueError):
        ExperimentConfig.from_payload(payload)


def test_phase_config_params_default_and_type():
    cfg = PhaseConfig(name="p", protocol="acquisition", stimuli={}, params=None)
    assert cfg.params == {}
    with pytest.raises(TypeError):
        PhaseConfig(name="p", protocol="acquisition", stimuli={}, params="bad")


def test_normalize_stimuli_list_and_invalid():
    names, salience = ExperimentConfig._normalize_stimuli(["tone"])
    assert names == ["tone"]
    assert salience == {}
    names, salience = ExperimentConfig._normalize_stimuli({"tone": "bad"})
    assert names == []
    assert salience == {}
    with pytest.raises(ValueError):
        ExperimentConfig._normalize_stimuli({"tone": {"salience": "bad"}})


def test_normalize_attention_invalid():
    with pytest.raises(ValueError):
        ExperimentConfig._normalize_attention({"tone": {"attention": "bad"}})
    with pytest.raises(ValueError):
        ExperimentConfig._normalize_attention({"tone": "bad"})


def test_normalize_phase_stimuli_salience_map():
    phase = {"tone": {"salience": 1.0}, "noise": {"salience": 0.5}}
    out = ExperimentConfig._normalize_phase_stimuli(phase)
    assert set(out) == {"tone", "noise"}


def test_validate_similarity_matrix_branches():
    with pytest.raises(ValueError):
        ExperimentConfig._validate_similarity_matrix("bad", ["tone"])
    with pytest.raises(ValueError):
        ExperimentConfig._validate_similarity_matrix({"type": "bad"}, ["tone"])
    with pytest.raises(ValueError):
        ExperimentConfig._validate_similarity_matrix({"type": "matrix", "values": []}, ["tone"])
    with pytest.raises(ValueError):
        ExperimentConfig._validate_similarity_matrix(
            {"type": "matrix", "values": [[1.0], [1.0]]},
            ["tone"],
        )
    with pytest.raises(ValueError):
        ExperimentConfig._validate_similarity_matrix(
            {"type": "matrix", "stimuli": "bad", "values": [[1.0]]},
            ["tone"],
        )
    with pytest.raises(ValueError):
        ExperimentConfig._validate_similarity_matrix(
            {"type": "matrix", "stimuli": ["tone", "noise"], "values": [[1.0]]},
            ["tone", "noise"],
        )
    with pytest.raises(ValueError):
        ExperimentConfig._validate_similarity_matrix(
            {"type": "matrix", "stimuli": ["tone"], "values": [[1.0]]},
            ["noise"],
        )
    with pytest.raises(ValueError):
        ExperimentConfig._validate_similarity_matrix(
            {"type": "matrix", "values": [[1.0, 0.5], [0.5, 1.0]]},
            ["tone"],
        )


def test_parse_representation_errors():
    exp = {"representation": {"params": {}}}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_representation(exp)
    exp = {"representation": {"name": "vector_elemental", "params": "bad"}}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_representation(exp)
    exp = {"representation": {"name": "bad", "params": {}}}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_representation(exp)
    exp = {"representation": 123}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_representation(exp)
    exp = {"representation": {"name": "vector_elemental", "params": {"attention": {"tone": 0.8}}}}
    with pytest.raises(ValueError, match="must not include attention"):
        ExperimentConfig._parse_representation(exp)


def test_parse_policy_errors():
    exp = {"policy": {"params": {}}}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_policy(exp)
    exp = {"policy": {"name": "epsilon_greedy", "params": "bad"}}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_policy(exp)
    exp = {"policy": 123}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_policy(exp)


def test_parse_phases_errors_and_legacy():
    exp = {"phases": [{"params": {}}]}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_phases(exp)
    exp = {"phases": [{"protocol": "acquisition", "params": "bad"}]}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_phases(exp)
    exp = {"protocol": "acquisition", "stimuli": {}, "params": "bad"}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_phases(exp)
    exp = {"protocol": "acquisition", "stimuli": {}}
    with pytest.raises(ValueError):
        ExperimentConfig._parse_phases(exp)


def test_from_payload_missing_sections():
    with pytest.raises(ValueError):
        ExperimentConfig.from_payload({"report": {}})
    with pytest.raises(ValueError):
        ExperimentConfig.from_payload({"experiment": {}})


def test_from_payload_rejects_invalid_section_shapes():
    with pytest.raises(ValueError, match="Payload must be an object"):
        ExperimentConfig.from_payload("bad")
    with pytest.raises(ValueError, match="Payload 'experiment' section must be an object"):
        ExperimentConfig.from_payload({"experiment": "bad", "report": {}})
    with pytest.raises(ValueError, match="Payload 'report' section must be an object"):
        ExperimentConfig.from_payload({"experiment": {}, "report": "bad"})


def test_from_payload_rejects_non_list_phases():
    payload = _base_payload()
    payload["experiment"]["phases"] = {"protocol": "acquisition"}
    with pytest.raises(ValueError, match="experiment.phases must be an array"):
        ExperimentConfig.from_payload(payload)


def test_from_payload_rejects_invalid_report_preset():
    payload = _base_payload()
    payload["report"]["preset"] = "   "
    with pytest.raises(ValueError, match="report.preset must be a non-empty string"):
        ExperimentConfig.from_payload(payload)


def test_from_payload_rejects_invalid_experiment_identity_fields():
    payload = _base_payload()
    payload["experiment"]["learner"] = "  "
    with pytest.raises(ValueError, match="experiment.learner must be a non-empty string"):
        ExperimentConfig.from_payload(payload)

    payload = _base_payload()
    payload["experiment"]["agent"] = 123
    with pytest.raises(ValueError, match="experiment.agent must be a non-empty string"):
        ExperimentConfig.from_payload(payload)


def test_infer_contexts_from_protocol_params():
    rep_params = {}
    config = SimpleNamespace(
        phases=[],
        params={"context": "B", "context_alt": "C"},
    )
    out = assemble_mod._infer_contexts(rep_params, config)
    assert set(out["contexts"]) == {"B", "C"}


def test_assemble_experiment_string_rep_and_inferred_context(monkeypatch):
    class DummyRep:
        dimension = 3
        salience = "sal"

    class DummyUnit:
        def __init__(self):
            self.context = None

    def fake_build_rep(name, **params):
        assert name == "vector_elemental"
        assert params.get("stimuli") == ["tone"]
        return DummyRep()

    def fake_build_learner(name, **params):
        return SimpleNamespace()

    def fake_build_agent(name, **params):
        return SimpleNamespace()

    def fake_build_policy(name, **params):
        return SimpleNamespace()

    def fake_build_phase(name, **kwargs):
        return DummyUnit()

    monkeypatch.setattr(assemble_mod, "build_representation", fake_build_rep)
    monkeypatch.setattr(assemble_mod, "build_learner", fake_build_learner)
    monkeypatch.setattr(assemble_mod, "build_agent", fake_build_agent)
    monkeypatch.setattr(assemble_mod, "build_policy", fake_build_policy)
    monkeypatch.setattr(assemble_mod, "build_phase", fake_build_phase)

    phases = [
        SimpleNamespace(
            name="Phase 1",
            protocol="acquisition",
            stimuli={"cs_plus": ["tone"]},
            params={"n_trials": 1, "context": "B", "context_alt": "C"},
        ),
        SimpleNamespace(
            name="Phase 2",
            protocol="acquisition",
            stimuli={"cs_plus": ["tone"]},
            params={"n_trials": 1},
        ),
    ]

    config = SimpleNamespace(
        representation="vector_elemental",
        learner="rescorla_wagner",
        agent="classical_agent",
        policy=None,
        stimuli=["tone"],
        salience={},
        attention={},
        context_inference={"enabled": True, "max_contexts": 2},
        phases=phases,
    )

    units, agent, representation = assemble_mod.assemble_experiment(config)
    assert len(units) == 2
    assert not hasattr(units[0], "context_source")
    assert getattr(units[1], "context_source") == "inferred"


def test_config_normalization_edge_cases():
    assert ExperimentConfig._normalize_stimuli("bad") == ([], {})
    assert ExperimentConfig._normalize_stimuli({"tone": 1.0}) == ([], {})

    assert ExperimentConfig._normalize_attention(["tone"]) == {}

    assert ExperimentConfig._normalize_phase_stimuli(["tone"]) == ["tone"]
    assert ExperimentConfig._normalize_phase_stimuli("tone") == "tone"

    rep = ExperimentConfig._parse_representation({"representation": "vector_elemental"})
    assert rep == "vector_elemental"


def test_require_fields_error():
    try:
        ExperimentConfig._require_fields({"a": 1}, ["a", "b"], "experiment")
    except ValueError as exc:
        assert "Missing required experiment fields" in str(exc)


def test_experiment_config_to_plan_contains_units_and_settings():
    payload = _base_payload()
    cfg = ExperimentConfig.from_payload(payload)
    plan = cfg.to_plan()

    assert isinstance(plan, ExperimentPlan)
    assert len(plan.units) == 1
    assert plan.units[0]["protocol"] == "acquisition"
    assert plan.settings["learner"] == "rescorla_wagner"
    assert plan.settings["agent"] == "classical_agent"
    assert plan.settings["resolved_plan"] is True


def test_assemble_experiment_accepts_plan():
    payload = _base_payload()
    cfg = ExperimentConfig.from_payload(payload)
    plan = cfg.to_plan()
    units, agent, representation = assemble_mod.assemble_experiment(plan)
    assert units
    assert agent is not None
    assert representation is not None


def test_experiment_plan_round_trip_and_stable_hash():
    payload = _base_payload()
    cfg = ExperimentConfig.from_payload(payload)
    plan = cfg.to_plan()
    blob = plan.to_dict()
    rebuilt = ExperimentPlan.from_dict(blob)

    assert rebuilt.to_dict() == blob
    assert rebuilt.stable_hash() == plan.stable_hash()


def test_payload_normalizer_and_validator_pipeline_smoke():
    payload = _base_payload()
    exp = payload["experiment"]
    rep = payload["report"]
    parser = ConfigParser(ExperimentConfig)

    PayloadValidator.validate_required_fields(ExperimentConfig._require_fields, exp, rep)
    normalized = PayloadNormalizer.normalize_experiment(
        exp,
        parser=parser,
    )

    assert "representation" in normalized
    assert "phases" in normalized
    PayloadValidator.validate_runtime(ExperimentConfig.validate_runtime_constraints, normalized["phases"])


def test_plan_builder_pipeline_smoke():
    from experiment.plan_builder import build_experiment_plan

    payload = _base_payload()
    cfg = ExperimentConfig.from_payload(payload)
    plan = PlanBuilder.build(cfg, build_experiment_plan=build_experiment_plan)
    assert isinstance(plan, ExperimentPlan)


def test_config_parser_composite_smoke():
    payload = _base_payload()
    exp = payload["experiment"]
    parser = ConfigParser(ExperimentConfig)
    assert parser.parse_representation(exp)["name"] == "vector_elemental"
    assert parser.parse_policy(exp) is None
    assert len(parser.parse_phases(exp)) == 1


def test_config_pipeline_build_smoke():
    payload = _base_payload()
    cfg = ConfigPipeline(ExperimentConfig).build(payload)
    assert isinstance(cfg, ExperimentConfig)
    assert cfg.learner == "rescorla_wagner"


def test_assemble_plan_does_not_require_runtime_context_inference(monkeypatch):
    payload = _base_payload()
    payload["experiment"]["context_inference"] = {"enabled": True, "max_contexts": 2}
    payload["experiment"]["phases"] = [
        {
            "name": "Acq",
            "protocol": "acquisition",
            "stimuli": {"cs_plus": ["tone"]},
            "params": {"n_trials": 1},
        },
        {
            "name": "Ext",
            "protocol": "nonreinforcement",
            "stimuli": {"cs_plus": ["tone"]},
            "params": {"n_trials": 1},
        },
    ]
    cfg = ExperimentConfig.from_payload(payload)
    plan = cfg.to_plan()

    monkeypatch.setattr(
        assemble_mod,
        "_infer_contexts",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("should not be called")),
    )
    units, _agent, _rep = assemble_mod.assemble_experiment(plan)
    assert len(units) == 2
