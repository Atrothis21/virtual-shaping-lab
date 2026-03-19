from __future__ import annotations

from experiment.config import ExperimentConfig
from virtual_shaping_lab.vsl.spec import ExperimentSpec


def _payload() -> dict:
    return {
        "experiment": {
            "program": {
                "phases": [
                    {
                        "name": "Phase 1",
                        "protocol": "acquisition",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 1, "alpha": 0.2, "gamma": 0},
                        "trials": 1,
                    }
                ],
            },
            "agent": {
                "name": "classical_agent",
                "representation": {
                    "name": "vector_elemental",
                    "params": {"stimuli": ["tone", "noise"], "max_compound_size": 2},
                },
                "learning": {"rule": "rescorla_wagner", "params": {}},
                "policy": None,
            },
            "runtime": {},
        },
        "report": {"preset": "acquisition"},
    }


def test_plan_builder_populates_typed_specs_non_breaking():
    plan = ExperimentConfig.plan_from_payload(_payload())

    # Existing dict surfaces remain intact.
    assert isinstance(plan.program_spec, dict)
    assert isinstance(plan.agent_spec, dict)
    assert isinstance(plan.runtime_spec, dict)
    assert isinstance(plan.analysis_spec, dict)

    # New typed surfaces are populated.
    assert plan.typed_program_spec is not None
    assert plan.typed_agent_spec is not None
    assert plan.typed_runtime_spec is not None
    assert plan.typed_analysis_spec is not None
    assert plan.typed_experiment_spec is not None

    # Typed experiment spec aligns to current dict surfaces.
    typed = plan.typed_experiment_spec
    assert isinstance(typed, ExperimentSpec)
    assert typed.program.to_dict() == plan.program_spec
    assert typed.analysis.to_dict() == plan.analysis_spec


def test_plan_typed_accessors_work_when_typed_fields_absent():
    plan = ExperimentConfig.plan_from_payload(_payload())
    blob = plan.to_dict()
    rebuilt = type(plan).from_dict(blob)

    # from_dict does not carry typed fields, accessors should synthesize safely.
    assert rebuilt.typed_experiment_spec is None
    synthesized = rebuilt.as_typed_experiment_spec()
    assert isinstance(synthesized, ExperimentSpec)
    assert synthesized.program.to_dict() == rebuilt.program_spec

