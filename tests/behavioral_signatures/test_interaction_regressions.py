from __future__ import annotations

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.runner import Runner
from experiment.runtime_records import finalize_record
from ui.validate_payload import validate_payload

from preset_payloads import matching_law_payload


def _run_records(payload: dict, *, seed: int = 7) -> list[dict]:
    validate_payload(payload)
    config = ExperimentConfig.from_payload(payload)
    units, _agent, _representation = assemble_experiment(config)

    records: list[dict] = []
    for phase_index, unit in enumerate(units):
        phase_records = Runner(unit, seed=seed).run()
        for record in phase_records:
            record["phase"] = phase_index
            finalize_record(record, phase_name=config.phases[phase_index].name)
        records.extend(phase_records)
    return records


def test_policy_and_prediction_error_interaction_changes_operant_outcomes():
    exploit_payload = matching_law_payload()
    exploit_payload["experiment"]["agent"]["policy"] = {
        "name": "fixed",
        "params": {"action": "left"},
    }
    exploit_phase = exploit_payload["experiment"]["program"]["phases"][0]
    exploit_phase.setdefault("params", {})
    exploit_phase["params"]["schedule_left"] = {
        "type": "fixed_ratio",
        "value": 1,
    }
    exploit_phase["params"]["schedule_right"] = {
        "type": "fixed_ratio",
        "value": 10,
    }

    poor_policy_payload = matching_law_payload()
    poor_policy_payload["experiment"]["agent"]["policy"] = {
        "name": "fixed",
        "params": {"action": "right"},
    }
    poor_phase = poor_policy_payload["experiment"]["program"]["phases"][0]
    poor_phase.setdefault("params", {})
    poor_phase["params"]["schedule_left"] = {
        "type": "fixed_ratio",
        "value": 1,
    }
    poor_phase["params"]["schedule_right"] = {
        "type": "fixed_ratio",
        "value": 10,
    }

    exploit_records = _run_records(exploit_payload)
    poor_records = _run_records(poor_policy_payload)

    exploit_reward = sum(float(r.get("reward", 0.0) or 0.0) for r in exploit_records)
    poor_reward = sum(float(r.get("reward", 0.0) or 0.0) for r in poor_records)
    exploit_prediction = sum(float(r.get("prediction", 0.0) or 0.0) for r in exploit_records) / len(exploit_records)
    poor_prediction = sum(float(r.get("prediction", 0.0) or 0.0) for r in poor_records) / len(poor_records)

    assert exploit_reward > poor_reward
    assert exploit_prediction > poor_prediction
