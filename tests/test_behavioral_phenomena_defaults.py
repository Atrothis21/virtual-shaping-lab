from __future__ import annotations

from typing import Iterable

import pytest

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import (
    aab_renewal_payload,
    aba_renewal_payload,
    abc_renewal_payload,
    acquisition_payload,
    blocking_payload,
    compound_acquisition_payload,
    differential_acquisition_payload,
    extinction_payload,
    occasion_setting_payload,
    overexpectation_payload,
    overshadowing_payload,
    rapid_reacquisition_payload,
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


def test_overshadowing_shows_secondary_cue_suppression_default_payload():
    records = _run_records(overshadowing_payload())
    compound_records = [r for r in records if r.get("phase_name") == "compound_acquisition"]

    per_cue = {"tone": [], "noise": []}
    for record in compound_records:
        by_stim = record.get("prediction_by_stimulus")
        if not isinstance(by_stim, dict):
            continue
        for cue in per_cue:
            if cue in by_stim:
                per_cue[cue].append(float(by_stim[cue]))

    assert per_cue["tone"], "Expected compound cue predictions for tone."
    assert per_cue["noise"], "Expected compound cue predictions for noise."

    tone_tail = _first_last_n([{"prediction": v} for v in per_cue["tone"]], n=10)[1]
    noise_tail = _first_last_n([{"prediction": v} for v in per_cue["noise"]], n=10)[1]

    assert _mean_prediction(tone_tail) > _mean_prediction(noise_tail) + 0.2


def test_overexpectation_shows_compound_exceeds_single_cue_default_payload():
    records = _run_records(overexpectation_payload())
    compound_records = [r for r in records if r.get("phase_name") == "compound_acquisition"]

    per_compound = []
    per_tone = []
    per_noise = []

    for record in compound_records:
        by_stim = record.get("prediction_by_stimulus")
        if not isinstance(by_stim, dict):
            continue
        if "compound" in by_stim:
            per_compound.append({"prediction": float(by_stim["compound"])})
        if "tone" in by_stim:
            per_tone.append({"prediction": float(by_stim["tone"])})
        if "noise" in by_stim:
            per_noise.append({"prediction": float(by_stim["noise"])})

    assert per_compound, "Expected compound predictions in overexpectation compound phase."
    assert per_tone and per_noise, "Expected single-cue predictions in overexpectation compound phase."

    comp_tail = _first_last_n(per_compound, n=10)[1]
    tone_tail = _first_last_n(per_tone, n=10)[1]
    noise_tail = _first_last_n(per_noise, n=10)[1]

    single_avg = (_mean_prediction(tone_tail) + _mean_prediction(noise_tail)) / 2.0
    assert _mean_prediction(comp_tail) > single_avg + 0.1


def test_blocking_default_payload_retains_primary_cue_dominance_signal():
    records = _run_records(blocking_payload())
    acquisition_records = [r for r in records if r.get("subphase_name") == "acquisition"]
    compound_records = [r for r in records if r.get("subphase_name") == "compound_acquisition"]

    assert acquisition_records, "Expected acquisition subphase records."
    assert compound_records, "Expected compound subphase records."

    acq_tail = _first_last_n(acquisition_records, n=10)[1]
    comp_tail = _first_last_n(compound_records, n=10)[1]

    # Current blocking default payload does not emit separate blocked-cue probe
    # records. This assertion guards the presently observable direction:
    # pretrained cue remains strongly predictive after compound introduction.
    assert _mean_prediction(acq_tail) > 0.8
    assert _mean_prediction(comp_tail) > 0.9


def test_aba_renewal_probe_recovers_from_extinction_context_default_payload():
    records = _run_records(aba_renewal_payload())
    ext_records = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe_records = [r for r in records if r.get("subphase_name") == "probe"]

    assert ext_records, "Expected nonreinforcement records."
    assert probe_records, "Expected probe records."

    ext_tail = _first_last_n(ext_records, n=10)[1]
    probe_tail = _first_last_n(probe_records, n=10)[1]

    assert _mean_prediction(probe_tail) > _mean_prediction(ext_tail) + 0.2


def test_abc_renewal_probe_recovers_above_extinction_default_payload():
    records = _run_records(abc_renewal_payload())
    ext_records = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe_records = [r for r in records if r.get("subphase_name") == "probe"]

    assert ext_records, "Expected nonreinforcement records."
    assert probe_records, "Expected probe records."

    ext_tail = _first_last_n(ext_records, n=10)[1]
    probe_tail = _first_last_n(probe_records, n=10)[1]

    assert _mean_prediction(probe_tail) > _mean_prediction(ext_tail) + 0.1


def test_aab_renewal_probe_stays_near_extinction_level_default_payload():
    records = _run_records(aab_renewal_payload())
    ext_records = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe_records = [r for r in records if r.get("subphase_name") == "probe"]

    assert ext_records, "Expected nonreinforcement records."
    assert probe_records, "Expected probe records."

    ext_tail = _first_last_n(ext_records, n=10)[1]
    probe_tail = _first_last_n(probe_records, n=10)[1]

    assert abs(_mean_prediction(probe_tail) - _mean_prediction(ext_tail)) < 0.1


def test_rapid_reacquisition_returns_to_high_response_after_extinction_default_payload():
    records = _run_records(rapid_reacquisition_payload())
    rewards = [float(r.get("reward", 0.0)) for r in records]

    first_zero = next((i for i, rv in enumerate(rewards) if rv == 0.0), None)
    last_zero = next((i for i in range(len(rewards) - 1, -1, -1) if rewards[i] == 0.0), None)
    assert first_zero is not None and last_zero is not None and first_zero <= last_zero

    first_acq = records[:first_zero]
    extinction = records[first_zero : last_zero + 1]
    reacq = records[last_zero + 1 :]

    assert first_acq, "Expected initial acquisition block."
    assert extinction, "Expected extinction block."
    assert reacq, "Expected reacquisition block."

    reacq_tail = _first_last_n(reacq, n=min(10, len(reacq)))[1]
    ext_tail = _first_last_n(extinction, n=10)[1]

    assert _mean_prediction(reacq_tail) > _mean_prediction(ext_tail) + 0.2
    assert _mean_prediction(reacq_tail) > 0.8


def test_occasion_setting_probe_is_between_acquisition_and_nonreinforcement_default_payload():
    records = _run_records(occasion_setting_payload())
    acquisition = [r for r in records if r.get("subphase_name") == "acquisition"]
    nonreinforcement = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe = [r for r in records if r.get("subphase_name") == "probe"]

    assert acquisition, "Expected acquisition records."
    assert nonreinforcement, "Expected nonreinforcement records."
    assert probe, "Expected probe records."

    acq_tail = _first_last_n(acquisition, n=10)[1]
    nr_tail = _first_last_n(nonreinforcement, n=10)[1]
    probe_tail = _first_last_n(probe, n=10)[1]

    probe_mean = _mean_prediction(probe_tail)
    assert probe_mean > _mean_prediction(nr_tail) + 0.1
    assert probe_mean < _mean_prediction(acq_tail) - 0.1
