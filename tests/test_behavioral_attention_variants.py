from __future__ import annotations

import copy

import pytest

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import acquisition_payload, compound_acquisition_payload


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


def test_attention_invariance_defaults_match_attention_one():
    base = acquisition_payload()
    attn_one = copy.deepcopy(base)
    attn_one["experiment"]["agent"]["learning"]["attention"] = {"initial": {"tone": {"attention": 1.0}}, "config": {}}

    base_records = _run_records(base)
    attn_records = _run_records(attn_one)

    assert _tail_mean_prediction(base_records, n=10) == pytest.approx(
        _tail_mean_prediction(attn_records, n=10),
        abs=1e-6,
    )


def test_attention_variant_acquisition_short_horizon_high_exceeds_low():
    high = acquisition_payload()
    low = copy.deepcopy(high)

    # Shorter horizon exposes attention-driven learning-rate differences.
    high["experiment"]["program"]["phases"][0]["trials"] = 20
    high["experiment"]["program"]["phases"][0]["params"]["n_trials"] = 20
    low["experiment"]["program"]["phases"][0]["trials"] = 20
    low["experiment"]["program"]["phases"][0]["params"]["n_trials"] = 20

    high["experiment"]["agent"]["learning"]["attention"] = {"initial": {"tone": {"attention": 1.0}}, "config": {}}
    low["experiment"]["agent"]["learning"]["attention"] = {"initial": {"tone": {"attention": 0.2}}, "config": {}}

    high_records = _run_records(high)
    low_records = _run_records(low)

    assert _tail_mean_prediction(high_records, n=5) > _tail_mean_prediction(low_records, n=5) + 0.1


def test_attention_variant_compound_high_exceeds_low():
    high = compound_acquisition_payload()
    low = copy.deepcopy(high)

    high["experiment"]["agent"]["learning"]["attention"] = {
        "initial": {"tone": {"attention": 1.0}, "noise": {"attention": 1.0}},
        "config": {},
    }
    low["experiment"]["agent"]["learning"]["attention"] = {
        "initial": {"tone": {"attention": 0.2}, "noise": {"attention": 0.2}},
        "config": {},
    }

    high_records = _run_records(high)
    low_records = _run_records(low)

    assert _tail_mean_prediction(high_records, n=10) > _tail_mean_prediction(low_records, n=10) + 0.1
