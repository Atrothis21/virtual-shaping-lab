from __future__ import annotations

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import conditioned_inhibition_payload


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


def test_signature_conditioned_inhibition_compound_suppresses_prediction():
    records = _run_records(conditioned_inhibition_payload())
    acquisition = [r for r in records if r.get("subphase_name") == "acquisition"]
    inhibition = [r for r in records if r.get("subphase_name") == "compound_nonreinforcement"]

    assert acquisition, "Expected acquisition records."
    assert inhibition, "Expected compound nonreinforcement records."

    acq_tail = _first_last_n(acquisition, n=10)[1]
    inh_tail = _first_last_n(inhibition, n=10)[1]
    assert _mean_prediction(inh_tail) < _mean_prediction(acq_tail) - 0.4


def test_signature_conditioned_inhibition_summation_probe_below_excitor_baseline():
    records = _run_records(conditioned_inhibition_payload())
    summation_acq = [r for r in records if r.get("subphase_name") == "summation_acquisition"]
    summation_probe = [r for r in records if r.get("subphase_name") == "summation_probe"]

    assert summation_acq, "Expected summation acquisition records."
    assert summation_probe, "Expected summation probe records."

    acq_tail = _first_last_n(summation_acq, n=10)[1]
    probe_mean = _mean_prediction(summation_probe)
    assert probe_mean < _mean_prediction(acq_tail) - 0.1


def test_signature_conditioned_inhibition_retardation_starts_lower_than_initial_acquisition():
    records = _run_records(conditioned_inhibition_payload())
    acquisition = [r for r in records if r.get("subphase_name") == "acquisition"]
    retardation = [r for r in records if r.get("subphase_name") == "retardation"]

    assert acquisition, "Expected acquisition records."
    assert retardation, "Expected retardation records."

    acq_head = _first_last_n(acquisition, n=10)[0]
    ret_head = _first_last_n(retardation, n=10)[0]
    assert _mean_prediction(ret_head) < _mean_prediction(acq_head) - 0.1
