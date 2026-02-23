from __future__ import annotations

import copy

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import (
    acquisition_payload,
    compound_acquisition_payload,
    differential_acquisition_payload,
)


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


def test_salience_variant_acquisition_high_exceeds_low():
    high = acquisition_payload()
    low = copy.deepcopy(high)

    high["experiment"]["salience"] = {"tone": {"salience": 1.0}}
    low["experiment"]["salience"] = {"tone": {"salience": 0.2}}

    high_records = _run_records(high)
    low_records = _run_records(low)

    assert _tail_mean_prediction(high_records) > _tail_mean_prediction(low_records) + 0.1


def test_salience_variant_compound_high_exceeds_low():
    high = compound_acquisition_payload()
    low = copy.deepcopy(high)

    high["experiment"]["salience"] = {
        "tone": {"salience": 1.0},
        "noise": {"salience": 1.0},
    }
    low["experiment"]["salience"] = {
        "tone": {"salience": 0.2},
        "noise": {"salience": 0.2},
    }

    high_records = _run_records(high)
    low_records = _run_records(low)

    assert _tail_mean_prediction(high_records) > _tail_mean_prediction(low_records) + 0.1


def test_salience_variant_differential_cs_plus_high_exceeds_low():
    high = differential_acquisition_payload()
    low = copy.deepcopy(high)

    high["experiment"]["salience"] = {
        "tone": {"salience": 1.0},
        "noise": {"salience": 1.0},
    }
    low["experiment"]["salience"] = {
        "tone": {"salience": 0.2},
        "noise": {"salience": 1.0},
    }

    high_records = [r for r in _run_records(high) if r.get("stimulus_type") == "cs_plus"]
    low_records = [r for r in _run_records(low) if r.get("stimulus_type") == "cs_plus"]

    assert high_records and low_records
    assert _tail_mean_prediction(high_records) > _tail_mean_prediction(low_records) + 0.1
