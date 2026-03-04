from experiment.domain.types import ExperimentPlan
from experiment.public import build_plan


def _payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["tone", "noise"], "max_compound_size": 2},
            },
            "phases": [
                {
                    "name": "Acquisition",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 3, "alpha": 0.2, "gamma": 0.0},
                }
            ],
        },
        "report": {"preset": "acquisition"},
    }


def test_public_plan_build_is_deterministic_for_same_payload():
    p1 = build_plan(_payload())
    p2 = build_plan(_payload())
    assert p1.to_dict() == p2.to_dict()
    assert p1.stable_hash() == p2.stable_hash()


def test_experiment_plan_roundtrip_preserves_stable_hash():
    plan = build_plan(_payload())
    blob = plan.to_dict()
    rebuilt = ExperimentPlan.from_dict(blob)
    assert rebuilt.to_dict() == blob
    assert rebuilt.stable_hash() == plan.stable_hash()
