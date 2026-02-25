STIMULI = ["tone", "noise", "light", "click"]
STIMULI_WITH_LEVER = ["lever", "tone", "noise", "light", "click"]


def _attention_for(stimuli):
    return {s: {"attention": 1.0} for s in stimuli}


def acquisition_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "phases": [
                {
                    "name": "Acquisition",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 100, "alpha": 0.2, "gamma": 0.0},
                }
            ],
            "salience": {"tone": {"salience": 1.0}},
            "attention": _attention_for(["tone"]),
        },
        "report": {"preset": "acquisition"},
    }


def compound_acquisition_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "phases": [
                {
                    "name": "Compound Acquisition",
                    "protocol": "compound_acquisition",
                    "stimuli": {"compound": ["tone", "noise"]},
                    "params": {
                        "n_trials": 100,
                        "alpha_cs1": 0.2,
                        "alpha_cs2": 0.12,
                        "gamma": 0.0,
                    },
                }
            ],
            "salience": {
                "tone": {"salience": 0.2},
                "noise": {"salience": 0.12},
            },
            "attention": _attention_for(["tone", "noise"]),
        },
        "report": {"preset": "compound_acquisition"},
    }


def differential_acquisition_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "phases": [
                {
                    "name": "Differential Acquisition",
                    "protocol": "differential_acquisition",
                    "stimuli": {"cs_plus": ["tone"], "cs_minus": ["noise"]},
                    "params": {"n_trials": 100, "alpha": 0.2},
                }
            ],
            "salience": {"tone": {"salience": 1.0}},
            "attention": _attention_for(["tone", "noise"]),
        },
        "report": {"preset": "differential_acquisition"},
    }


def extinction_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "extinction",
            "stimuli": {"cs_plus": ["tone"]},
            "params": {
                "n_acquisition_trials": 50,
                "n_extinction_trials": 50,
                "alpha": 0.2,
                "gamma": 0.0,
            },
            "salience": {"tone": {"salience": 1.0}},
            "attention": _attention_for(["tone"]),
        },
        "report": {"preset": "extinction"},
    }


def blocking_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "blocking",
            "stimuli": {"cs_plus": ["tone", "noise"]},
            "params": {
                "n_acquisition_trials": 50,
                "n_compound_trials": 50,
                "alpha": 0.2,
            },
            "salience": {"tone": {"salience": 1.0}, "noise": {"salience": 1.0}},
            "attention": _attention_for(["tone", "noise"]),
        },
        "report": {"preset": "blocking"},
    }


def conditioned_inhibition_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "conditioned_inhibition",
            "stimuli": {"cs_plus": ["tone"], "cs_minus": ["noise"]},
            "params": {
                "n_acquisition_trials": 50,
                "n_inhibition_trials": 50,
                "n_retardation_trials": 20,
                "alpha": 0.2,
            },
            "attention": _attention_for(["tone", "noise"]),
        },
        "report": {"preset": "conditioned_inhibition"},
    }


def occasion_setting_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_hybrid",
                "params": {
                    "stimuli": STIMULI,
                    "max_compound_size": 2,
                    "include_global": True,
                    "include_context": True,
                },
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "occasion_setting",
            "stimuli": {"occasion_setter": ["tone"], "target": ["noise"]},
            "params": {"n_training_trials": 100, "n_probe_trials": 20, "alpha": 0.2},
            "salience": {"tone": {"salience": 1.0}, "noise": {"salience": 1.0}},
            "attention": _attention_for(["tone", "noise"]),
        },
        "report": {"preset": "occasion_setting"},
    }


def rapid_reacquisition_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_hybrid",
                "params": {
                    "stimuli": STIMULI,
                    "max_compound_size": 2,
                    "include_global": True,
                    "include_context": True,
                },
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "rapid_reacquisition",
            "stimuli": {"cs_plus": ["tone"]},
            "params": {
                "n_acquisition_trials": 50,
                "n_extinction_trials": 50,
                "n_reacquisition_trials": 20,
                "alpha": 0.2,
                "gamma": 0.0,
                "context_a": "A",
                "context_b": "B",
            },
            "salience": {"tone": {"salience": 1.0}},
            "attention": _attention_for(["tone"]),
        },
        "report": {"preset": "rapid_reacquisition"},
    }


def aab_renewal_payload():
    return _renewal_payload("aab_renewal", context_c=None)


def aba_renewal_payload():
    return _renewal_payload("aba_renewal", context_c=None)


def abc_renewal_payload():
    return _renewal_payload("abc_renewal", context_c="C")


def _renewal_payload(protocol, context_c):
    params = {
        "n_acquisition_trials": 50,
        "n_extinction_trials": 50,
        "n_probe_trials": 20,
        "alpha": 0.2,
        "gamma": 0.0,
        "context_a": "A",
        "context_b": "B",
    }
    if context_c:
        params["context_c"] = context_c
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_hybrid",
                "params": {
                    "stimuli": STIMULI,
                    "max_compound_size": 2,
                    "include_global": True,
                    "include_context": True,
                },
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": protocol,
            "stimuli": {"cs_plus": ["tone"]},
            "params": params,
            "salience": {"tone": {"salience": 1.0}},
            "attention": _attention_for(["tone"]),
        },
        "report": {"preset": protocol},
    }


def operant_conditioning_payload():
    return {
        "experiment": {
            "learner": "q_learner",
            "agent": "operant_agent",
            "policy": {
                "name": "epsilon_greedy",
                "params": {"actions": ["leverpress"], "epsilon": 0.1},
            },
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI_WITH_LEVER, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "operant_conditioning",
            "params": {
                "n_trials": 150,
                "consequence_mode": "positive_reinforcement",
                "reward_schedule": {"type": "fixed_ratio", "value": 5},
            },
        },
        "report": {"preset": "operant_conditioning"},
    }


def matching_law_payload():
    return {
        "experiment": {
            "learner": "q_learner",
            "agent": "operant_agent",
            "policy": {
                "name": "epsilon_greedy",
                "params": {"actions": ["left", "right"], "epsilon": 0.1},
            },
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI_WITH_LEVER, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "matching_law",
            "params": {
                "n_trials": 300,
                "schedule_left": {"type": "variable_interval", "value": 30},
                "schedule_right": {"type": "variable_interval", "value": 60},
                "action_labels": ["left", "right"],
            },
        },
        "report": {"preset": "matching_law"},
    }


def _softmax_operant_policy(actions=("left", "right")):
    return {"name": "softmax", "params": {"actions": list(actions), "temperature": 0.8}}


def shaping_payload():
    return {
        "experiment": {
            "learner": "q_learner",
            "agent": "operant_agent",
            "policy": _softmax_operant_policy(actions=("leverpress",)),
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI_WITH_LEVER, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "shaping",
            "params": {
                "n_stage_1_trials": 60,
                "n_stage_2_trials": 60,
                "schedule_stage_1": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
                "schedule_stage_2": {"type": "fixed_ratio", "value": 5, "reward": 1.0},
            },
        },
        "report": {"preset": "shaping"},
    }


def resurgence_payload():
    return {
        "experiment": {
            "learner": "q_learner",
            "agent": "operant_agent",
            "policy": _softmax_operant_policy(),
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI_WITH_LEVER, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "resurgence",
            "params": {
                "n_acquisition_trials": 40,
                "n_suppression_trials": 40,
                "n_resurgence_trials": 30,
                "acquisition_schedule": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
                "suppression_schedule": {"type": "fixed_ratio", "value": 1, "reward": 0.0},
                "resurgence_schedule": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
            },
        },
        "report": {"preset": "resurgence"},
    }


def superextinction_payload():
    return {
        "experiment": {
            "learner": "q_learner",
            "agent": "operant_agent",
            "policy": _softmax_operant_policy(actions=("leverpress",)),
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI_WITH_LEVER, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "superextinction",
            "params": {
                "n_acquisition_trials": 50,
                "n_superextinction_trials": 50,
                "acquisition_schedule": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
                "superextinction_schedule": {"type": "fixed_ratio", "value": 1, "reward": -1.0},
            },
        },
        "report": {"preset": "superextinction"},
    }


def spontaneous_recovery_payload():
    return {
        "experiment": {
            "learner": "q_learner",
            "agent": "operant_agent",
            "policy": _softmax_operant_policy(actions=("leverpress",)),
            "representation": {
                "name": "vector_hybrid",
                "params": {
                    "stimuli": STIMULI_WITH_LEVER,
                    "max_compound_size": 2,
                    "include_global": True,
                    "include_context": True,
                },
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "protocol": "spontaneous_recovery",
            "params": {
                "n_acquisition_trials": 40,
                "n_extinction_trials": 40,
                "n_probe_trials": 30,
                "context_a": "A",
                "context_b": "B",
                "acquisition_schedule": {"type": "fixed_ratio", "value": 1, "reward": 1.0},
                "extinction_schedule": {"type": "fixed_ratio", "value": 1, "reward": 0.0},
                "probe_schedule": {"type": "fixed_ratio", "value": 1, "reward": 0.0},
            },
        },
        "report": {"preset": "spontaneous_recovery"},
    }


def overshadowing_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "phases": [
                {
                    "name": "Overshadowing: Acquisition",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 50, "alpha": 0.2, "gamma": 0.0},
                },
                {
                    "name": "Overshadowing: Compound",
                    "protocol": "compound_acquisition",
                    "stimuli": {"compound": ["tone", "noise"]},
                    "params": {
                        "n_trials": 100,
                        "alpha_cs1": 0.2,
                        "alpha_cs2": 0.2,
                        "gamma": 0.0,
                    },
                },
            ],
            "attention": {"tone": {"attention": 1.0}, "noise": {"attention": 0.3}},
        },
        "report": {"preset": "custom_protocol"},
    }


def overexpectation_payload():
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_elemental",
                "params": {"stimuli": STIMULI, "max_compound_size": 2},
            },
            "context_inference": {"enabled": False, "max_contexts": 3},
            "phases": [
                {
                    "name": "Overexpectation: Acquisition",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone", "noise"]},
                    "params": {"n_trials": 80, "alpha": 0.2, "gamma": 0.0},
                },
                {
                    "name": "Overexpectation: Compound",
                    "protocol": "compound_acquisition",
                    "stimuli": {"compound": ["tone", "noise"]},
                    "params": {
                        "n_trials": 80,
                        "alpha_cs1": 0.2,
                        "alpha_cs2": 0.2,
                        "gamma": 0.0,
                    },
                },
            ],
            "attention": _attention_for(["tone", "noise"]),
        },
        "report": {"preset": "custom_protocol"},
    }


PRESET_PAYLOADS = [
    ("acquisition", acquisition_payload()),
    ("compound_acquisition", compound_acquisition_payload()),
    ("differential_acquisition", differential_acquisition_payload()),
    ("extinction", extinction_payload()),
    ("blocking", blocking_payload()),
    ("conditioned_inhibition", conditioned_inhibition_payload()),
    ("occasion_setting", occasion_setting_payload()),
    ("rapid_reacquisition", rapid_reacquisition_payload()),
    ("aab_renewal", aab_renewal_payload()),
    ("aba_renewal", aba_renewal_payload()),
    ("abc_renewal", abc_renewal_payload()),
    ("operant_conditioning", operant_conditioning_payload()),
    ("matching_law", matching_law_payload()),
    ("shaping", shaping_payload()),
    ("resurgence", resurgence_payload()),
    ("superextinction", superextinction_payload()),
    ("spontaneous_recovery", spontaneous_recovery_payload()),
    ("overshadowing", overshadowing_payload()),
    ("overexpectation", overexpectation_payload()),
]


# Phase 0 migration-contract fixtures:
# - classical_preset: single-phase classical flow
# - operant_preset: operant protocol flow with policy
# - multi_phase_builder: builder-style multi-phase flow
CONTRACT_FIXTURES = {
    "classical_preset": acquisition_payload(),
    "operant_preset": matching_law_payload(),
    "multi_phase_builder": overshadowing_payload(),
}
