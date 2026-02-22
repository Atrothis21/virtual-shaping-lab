from __future__ import annotations

from typing import Iterable

import pytest

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import (
    acquisition_payload,
    compound_acquisition_payload,
    differential_acquisition_payload,
    extinction_payload,
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


def _mean_prediction(records: Iterable[dict]) -> float:
    values = [float(r["prediction"]) for r in records if "prediction" in r]
    if not values:
        raise ValueError("No prediction values available.")
    return sum(values) / len(values)


def _head_tail(records: list[dict], ratio: float = 0.2) -> tuple[list[dict], list[dict]]:
    if not records:
        raise ValueError("Cannot split empty records.")
    window = max(1, int(len(records) * ratio))
    return records[:window], records[-window:]


def _first_last_n(records: list[dict], n: int = 10) -> tuple[list[dict], list[dict]]:
    if not records:
        raise ValueError("Cannot split empty records.")
    window = max(1, min(n, len(records)))
    return records[:window], records[-window:]


def test_acquisition_shows_learning_gain_default_payload():
    records = _run_records(acquisition_payload())
    early, late = _first_last_n(records, n=10)

    assert _mean_prediction(late) > _mean_prediction(early) + 0.1


def test_extinction_shows_response_loss_after_acquisition_default_payload():
    records = _run_records(extinction_payload())

    acquisition_records = [r for r in records if r.get("subphase_name") == "acquisition"]
    extinction_records = [r for r in records if r.get("subphase_name") == "nonreinforcement"]

    assert acquisition_records, "Expected acquisition subphase records."
    assert extinction_records, "Expected nonreinforcement subphase records."

    ext_early, ext_late = _head_tail(extinction_records, ratio=0.2)

    assert _mean_prediction(ext_late) < _mean_prediction(ext_early) - 0.2
    assert _mean_prediction(ext_late) < _mean_prediction(acquisition_records[-10:]) - 0.2


def test_differential_acquisition_separates_cs_plus_and_cs_minus_default_payload():
    records = _run_records(differential_acquisition_payload())

    plus_records = [r for r in records if r.get("stimulus_type") == "cs_plus"]
    minus_records = [r for r in records if r.get("stimulus_type") == "cs_minus"]

    assert plus_records, "Expected CS+ records."
    assert minus_records, "Expected CS- records."

    plus_tail = _head_tail(plus_records, ratio=0.2)[1]
    minus_tail = _head_tail(minus_records, ratio=0.2)[1]

    assert _mean_prediction(plus_tail) > _mean_prediction(minus_tail) + 0.2


def test_compound_acquisition_shows_learning_gain_default_payload():
    records = _run_records(compound_acquisition_payload())
    compound_records = [r for r in records if r.get("stimulus_type") == "compound"]

    assert compound_records, "Expected compound stimulus records."

    early, late = _first_last_n(compound_records, n=10)
    assert _mean_prediction(late) > _mean_prediction(early) + 0.1
