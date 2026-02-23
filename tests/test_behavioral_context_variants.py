from __future__ import annotations

import copy

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload


def _run_records(payload: dict) -> list[dict]:
    validate_payload(payload)
    config = ExperimentConfig.from_payload(payload)
    protocols, _agent, _representation = assemble_experiment(config)

    records: list[dict] = []
    for phase_index, protocol in enumerate(protocols):
        phase_records = Runner(protocol).run()
        for record in phase_records:
            record["phase"] = phase_index
            finalize_record(record, phase_name=config.phases[phase_index].name)
        records.extend(phase_records)
    return records


def _base_payload() -> dict:
    return {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_hybrid",
                "params": {
                    "stimuli": ["tone", "noise"],
                    "max_compound_size": 2,
                    "include_global": True,
                    "include_context": True,
                },
            },
            "attention": {"tone": {"attention": 1.0}},
            "salience": {"tone": {"salience": 1.0}},
            "context_inference": {"enabled": False, "max_contexts": 3},
            "phases": [
                {
                    "name": "Acquisition",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 60, "alpha": 0.2, "gamma": 0.0},
                },
                {
                    "name": "Extinction",
                    "protocol": "nonreinforcement",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 60, "alpha": 0.2, "gamma": 0.0},
                },
            ],
        },
        "report": {"preset": "custom_protocol"},
    }


def test_context_inference_assigns_distinct_phase_contexts_when_enabled():
    base = _base_payload()
    inferred = copy.deepcopy(base)
    inferred["experiment"]["context_inference"] = {"enabled": True, "max_contexts": 2}

    rec_base = _run_records(base)
    rec_inferred = _run_records(inferred)

    ext_base = [r for r in rec_base if r.get("phase") == 1]
    ext_inferred = [r for r in rec_inferred if r.get("phase") == 1]

    assert ext_base and ext_inferred
    assert all(r.get("context") == "A" for r in ext_base)
    assert all("inferred_context" not in r for r in ext_base)

    assert all(r.get("context") == "B" for r in ext_inferred)
    assert all(r.get("context_source") == "inferred" for r in ext_inferred)
    assert all(r.get("inferred_context") == "B" for r in ext_inferred)


def test_explicit_context_is_preserved_when_inference_enabled():
    payload = {
        "experiment": {
            "learner": "rescorla_wagner",
            "agent": "classical_agent",
            "representation": {
                "name": "vector_hybrid",
                "params": {
                    "stimuli": ["tone"],
                    "max_compound_size": 2,
                    "include_global": True,
                    "include_context": True,
                },
            },
            "attention": {"tone": {"attention": 1.0}},
            "salience": {"tone": {"salience": 1.0}},
            "context_inference": {"enabled": True, "max_contexts": 2},
            "phases": [
                {
                    "name": "Acquisition",
                    "protocol": "acquisition",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 20, "alpha": 0.2, "gamma": 0.0},
                },
                {
                    "name": "Probe",
                    "protocol": "probe",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 10, "context": "C"},
                },
            ],
        },
        "report": {"preset": "custom_protocol"},
    }

    records = _run_records(payload)
    acq = [r for r in records if r.get("phase") == 0]
    probe = [r for r in records if r.get("phase") == 1]

    assert acq and probe
    assert all(r.get("context") == "A" for r in acq)
    assert all(r.get("context_source") == "inferred" for r in acq)
    assert all(r.get("inferred_context") == "A" for r in acq)

    assert all(r.get("context") == "C" for r in probe)
    assert all("inferred_context" not in r for r in probe)
