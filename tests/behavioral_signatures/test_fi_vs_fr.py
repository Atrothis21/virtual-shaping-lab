from __future__ import annotations

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import operant_conditioning_payload


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


def _operant_payload(schedule_type: str, schedule_value: int, n_trials: int = 120) -> dict:
    payload = operant_conditioning_payload()
    payload["experiment"]["params"]["n_trials"] = n_trials
    payload["experiment"]["params"]["reward_schedule"] = {
        "type": schedule_type,
        "value": schedule_value,
    }
    return payload


def _reinforcement_rate(records: list[dict]) -> float:
    rewards = [float(r.get("reward", 0.0) or 0.0) for r in records]
    if not rewards:
        raise ValueError("No rewards found in records.")
    return sum(1.0 for r in rewards if r > 0.0) / float(len(rewards))


def test_schedule_proxy_fixed_ratio_yields_higher_reinforcement_density_than_fixed_interval():
    fr_records = _run_records(_operant_payload("fixed_ratio", 1))
    fi_records = _run_records(_operant_payload("fixed_interval", 10))

    fr_rate = _reinforcement_rate(fr_records)
    fi_rate = _reinforcement_rate(fi_records)

    # Proxy signal only: this asserts schedule-level reinforcement density under
    # current operant implementation; it is not a within-trial FI hallmark test.
    assert fr_rate > fi_rate + 0.6
