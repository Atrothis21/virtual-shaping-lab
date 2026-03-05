from __future__ import annotations

from experiment.public import build_plan, run_from_plan


def _template_backed_payload() -> dict:
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": ["tone", "noise"], "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "phases": [
                {
                    "name": "Acquisition",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 6, "alpha": 0.2, "gamma": 0.0},
                },
                {
                    "name": "Differential Acquisition",
                    "protocol": "differential_acquisition",
                    "stimuli": {"cs_plus": ["tone"], "cs_minus": ["noise"]},
                    "params": {
                        "n_trials": 12,
                        "reinforced_outcome": 1.0,
                        "nonreinforced_outcome": 0.0,
                        "alpha": 0.2,
                    },
                },
            ],
        },
        "report": {"preset": "acquisition"},
    }


def test_template_backed_plan_run_is_deterministic_for_same_seed():
    plan = build_plan(_template_backed_payload())

    result_1 = run_from_plan(plan, seed=123)
    result_2 = run_from_plan(plan, seed=123)

    assert result_1.records == result_2.records
    assert result_1.unit_records == result_2.unit_records


def test_template_backed_differential_sampling_changes_with_different_seed():
    plan = build_plan(_template_backed_payload())

    result_1 = run_from_plan(plan, seed=123)
    result_2 = run_from_plan(plan, seed=456)

    # The first unit is single-trial-type acquisition; differential behavior appears in later records.
    # This check ensures template trial sampling is seeded and not globally fixed.
    assert result_1.records != result_2.records

