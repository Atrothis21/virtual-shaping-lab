from __future__ import annotations

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import aab_renewal_payload, aba_renewal_payload, abc_renewal_payload


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


def _first_last_n(rows: list[dict], n: int = 10) -> tuple[list[dict], list[dict]]:
    w = max(1, min(n, len(rows)))
    return rows[:w], rows[-w:]


def test_signature_aba_renewal_probe_recovers_above_extinction_tail():
    records = _run_records(aba_renewal_payload())
    ext = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe = [r for r in records if r.get("subphase_name") == "probe"]

    assert ext, "Expected nonreinforcement records."
    assert probe, "Expected probe records."

    ext_tail = _first_last_n(ext, n=10)[1]
    probe_tail = _first_last_n(probe, n=10)[1]
    assert _mean_prediction(probe_tail) > _mean_prediction(ext_tail) + 0.2


def test_signature_abc_renewal_probe_recovers_above_extinction_tail():
    records = _run_records(abc_renewal_payload())
    ext = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe = [r for r in records if r.get("subphase_name") == "probe"]

    assert ext, "Expected nonreinforcement records."
    assert probe, "Expected probe records."

    ext_tail = _first_last_n(ext, n=10)[1]
    probe_tail = _first_last_n(probe, n=10)[1]
    assert _mean_prediction(probe_tail) > _mean_prediction(ext_tail) + 0.1


def test_signature_aab_renewal_probe_stays_near_extinction_level():
    records = _run_records(aab_renewal_payload())
    ext = [r for r in records if r.get("subphase_name") == "nonreinforcement"]
    probe = [r for r in records if r.get("subphase_name") == "probe"]

    assert ext, "Expected nonreinforcement records."
    assert probe, "Expected probe records."

    ext_tail = _first_last_n(ext, n=10)[1]
    probe_tail = _first_last_n(probe, n=10)[1]
    assert abs(_mean_prediction(probe_tail) - _mean_prediction(ext_tail)) < 0.1
