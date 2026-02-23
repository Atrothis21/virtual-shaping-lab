from __future__ import annotations

import copy

import pytest

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import differential_acquisition_payload


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


def _tail_mean_prediction(records: list[dict], n: int = 10) -> float:
    values = [float(r["prediction"]) for r in records if "prediction" in r]
    if not values:
        raise ValueError("No prediction values available.")
    tail = values[-max(1, min(n, len(values))):]
    return sum(tail) / len(tail)


def _with_similarity(payload: dict, offdiag: float) -> dict:
    out = copy.deepcopy(payload)
    stimuli = out["experiment"]["representation"]["params"]["stimuli"]
    values = []
    for i in range(len(stimuli)):
        row = []
        for j in range(len(stimuli)):
            row.append(1.0 if i == j else offdiag)
        values.append(row)
    out["experiment"]["representation"]["params"]["similarity"] = {
        "type": "matrix",
        "stimuli": stimuli,
        "values": values,
    }
    return out


def test_similarity_identity_matrix_matches_zero_offdiag_behavior():
    base = differential_acquisition_payload()
    base["experiment"]["representation"]["params"]["stimuli"] = ["tone", "noise"]
    base["experiment"]["salience"] = {
        "tone": {"salience": 1.0},
        "noise": {"salience": 1.0},
    }

    identity_payload = _with_similarity(base, offdiag=0.0)
    no_similarity_payload = copy.deepcopy(base)

    rec_identity = _run_records(identity_payload)
    rec_no_similarity = _run_records(no_similarity_payload)

    id_minus = [r for r in rec_identity if r.get("stimulus_type") == "cs_minus"]
    no_minus = [r for r in rec_no_similarity if r.get("stimulus_type") == "cs_minus"]

    assert id_minus and no_minus
    assert _tail_mean_prediction(id_minus, n=10) == pytest.approx(
        _tail_mean_prediction(no_minus, n=10),
        abs=1e-6,
    )


def test_similarity_non_identity_increases_cs_minus_generalization():
    base = differential_acquisition_payload()
    base["experiment"]["representation"]["params"]["stimuli"] = ["tone", "noise"]
    base["experiment"]["salience"] = {
        "tone": {"salience": 1.0},
        "noise": {"salience": 1.0},
    }

    identity_payload = _with_similarity(base, offdiag=0.0)
    generalized_payload = _with_similarity(base, offdiag=0.6)

    rec_identity = _run_records(identity_payload)
    rec_generalized = _run_records(generalized_payload)

    id_minus = [r for r in rec_identity if r.get("stimulus_type") == "cs_minus"]
    gen_minus = [r for r in rec_generalized if r.get("stimulus_type") == "cs_minus"]

    assert id_minus and gen_minus
    assert _tail_mean_prediction(gen_minus, n=10) > _tail_mean_prediction(id_minus, n=10) + 0.005
