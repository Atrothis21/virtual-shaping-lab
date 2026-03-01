from __future__ import annotations

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import blocking_payload


def _run_records(payload: dict) -> list[dict]:
    validate_payload(payload)
    config = ExperimentConfig.from_payload(payload)
    units, _agent, _representation = assemble_experiment(config)

    records: list[dict] = []
    for phase_index, unit in enumerate(units):
        unit_records = Runner(unit).run()
        for rec in unit_records:
            rec["phase"] = phase_index
            finalize_record(rec, phase_name=config.phases[phase_index].name)
        records.extend(unit_records)
    return records


def _tail(values: list[float], n: int = 10) -> list[float]:
    if not values:
        raise ValueError("Cannot take tail of empty list.")
    return values[-min(n, len(values)) :]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _cue_predictions(records: list[dict], cue: str) -> list[float]:
    out: list[float] = []
    for rec in records:
        by_stim = rec.get("prediction_by_stimulus")
        if isinstance(by_stim, dict) and cue in by_stim:
            out.append(float(by_stim[cue]))
    return out


def test_signature_blocking_retains_primary_cue_dominance():
    block_records = _run_records(blocking_payload())

    tone = _cue_predictions(block_records, cue="tone")
    noise = _cue_predictions(block_records, cue="noise")

    assert tone, "Expected primary-cue predictions for blocking condition."
    assert noise, "Expected blocked-cue predictions for blocking condition."

    tone_tail = _tail(tone, n=10)
    noise_tail = _tail(noise, n=10)

    # Current default blocking dynamics preserve primary-cue dominance.
    assert _mean(tone_tail) >= _mean(noise_tail)
