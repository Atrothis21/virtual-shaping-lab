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


def test_fixed_policy_localizes_behavior_change_without_representation_change():
    left_payload = matching_law_payload()
    right_payload = matching_law_payload()

    left_payload["experiment"]["agent"]["policy"] = {
        "name": "fixed",
        "params": {"action": "left"},
    }
    right_payload["experiment"]["agent"]["policy"] = {
        "name": "fixed",
        "params": {"action": "right"},
    }

    left_phase = left_payload["experiment"]["program"]["phases"][0]
    right_phase = right_payload["experiment"]["program"]["phases"][0]
    left_phase.setdefault("params", {})
    right_phase.setdefault("params", {})
    left_phase["params"]["schedule_left"] = {"type": "fixed_ratio", "value": 1}
    left_phase["params"]["schedule_right"] = {"type": "fixed_ratio", "value": 10}
    right_phase["params"]["schedule_left"] = {"type": "fixed_ratio", "value": 1}
    right_phase["params"]["schedule_right"] = {"type": "fixed_ratio", "value": 10}

    left_records = _run_records(left_payload)
    right_records = _run_records(right_payload)

    left_actions = {record.get("action") for record in left_records if record.get("action") is not None}
    right_actions = {record.get("action") for record in right_records if record.get("action") is not None}

    assert len(left_actions) == 1
    assert len(right_actions) == 1
    assert left_actions != right_actions
    assert left_records[0].get("stimulus") == right_records[0].get("stimulus")
