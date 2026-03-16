from experiment.domain.types import ExperimentPlan
from experiment.public import assemble_from_plan, build_plan, run_from_plan, validate_plan


def _classical_payload():
    return {
        "experiment": {
            "program": {
                "phases": [
                    {
                        "name": "Acquisition",
                        "protocol": "acquisition",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 2, "alpha": 0.2, "gamma": 0.0},
                        "trials": 2,
                    }
                ],
            },
            "agent": {
                "name": "classical_agent",
                "representation": {
                    "name": "vector_elemental",
                    "params": {"stimuli": ["tone"], "max_compound_size": 2},
                },
                "learning": {
                    "rule": "rescorla_wagner",
                    "params": {},
                },
                "policy": None,
            },
            "runtime": {},
        },
        "report": {"preset": "acquisition"},
    }


def test_build_and_validate_plan_via_public_facade():
    plan = build_plan(_classical_payload())
    assert isinstance(plan, ExperimentPlan)
    assert validate_plan(plan) is plan
    assert isinstance(plan.stable_hash(), str) and plan.stable_hash()


def test_assemble_from_plan_via_public_facade():
    plan = build_plan(_classical_payload())
    runtime_units, agent, representation = assemble_from_plan(plan)
    assert runtime_units
    assert agent is not None
    assert representation is not None


def test_run_from_plan_via_public_facade():
    plan = build_plan(_classical_payload())
    result = run_from_plan(plan, seed=123)
    assert isinstance(result.records, list)
    assert isinstance(result.unit_records, list)
    assert result.runtime_units
