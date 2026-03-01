from __future__ import annotations

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import extinction_payload, rapid_reacquisition_payload


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


def _mean_prediction(rows: list[dict]) -> float:
    vals = [float(r["prediction"]) for r in rows if r.get("prediction") is not None]
    if not vals:
        raise ValueError("No prediction values available.")
    return sum(vals) / len(vals)


def _head_tail(rows: list[dict], ratio: float = 0.2) -> tuple[list[dict], list[dict]]:
    n = max(1, int(len(rows) * ratio))
    return rows[:n], rows[-n:]


def _first_last_n(rows: list[dict], n: int = 10) -> tuple[list[dict], list[dict]]:
    w = max(1, min(n, len(rows)))
    return rows[:w], rows[-w:]


def test_signature_extinction_reduces_prediction_after_acquisition():
    records = _run_records(extinction_payload())
    acq = [r for r in records if r.get("subphase_name") == "acquisition"]
    ext = [r for r in records if r.get("subphase_name") == "nonreinforcement"]

    assert acq, "Expected acquisition records."
    assert ext, "Expected extinction records."

    ext_early, ext_late = _head_tail(ext, ratio=0.2)
    assert _mean_prediction(ext_late) < _mean_prediction(ext_early) - 0.2
    assert _mean_prediction(ext_late) < _mean_prediction(acq[-10:]) - 0.2


def test_signature_rapid_reacquisition_exceeds_extinction_tail():
    records = _run_records(rapid_reacquisition_payload())
    rewards = [float(r.get("reward", 0.0) or 0.0) for r in records]

    first_zero = next((i for i, rv in enumerate(rewards) if rv == 0.0), None)
    last_zero = next((i for i in range(len(rewards) - 1, -1, -1) if rewards[i] == 0.0), None)
    assert first_zero is not None and last_zero is not None and first_zero <= last_zero

    extinction = records[first_zero:last_zero + 1]
    reacq = records[last_zero + 1:]
    assert extinction, "Expected extinction block."
    assert reacq, "Expected reacquisition block."

    ext_tail = _first_last_n(extinction, n=10)[1]
    reacq_tail = _first_last_n(reacq, n=min(10, len(reacq)))[1]

    assert _mean_prediction(reacq_tail) > _mean_prediction(ext_tail) + 0.2
    assert _mean_prediction(reacq_tail) > 0.8
