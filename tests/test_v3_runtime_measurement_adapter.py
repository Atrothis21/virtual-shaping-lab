from __future__ import annotations

import hashlib
import json

from virtual_shaping_lab.vsl.runtime import RuntimeMeasurementAdapter, build_runtime_measurement_adapter


def _records() -> list[dict]:
    return [
        {
            "trial_index": 0,
            "reward": 1.0,
            "action": "left",
            "task_input": {"stimuli": {"tone": 1.0}, "available_actions": ["left", "right"]},
            "metadata": {"policy_traces": {"action": "left", "action_probabilities": {"left": 1.0}}},
        },
        {
            "trial_index": 1,
            "reward": 0.0,
            "action": "right",
            "task_input": {"stimuli": {"tone": 1.0}, "available_actions": ["left", "right"]},
            "metadata": {"policy_traces": {"action": "right", "action_probabilities": {"right": 1.0}}},
        },
    ]


def _measurement_hash(result) -> str:
    payload = {
        "analysis": dict(result.analysis.metrics),
        "analysis_meta": dict(result.analysis.metadata),
        "visualization": list(result.visualization.figures),
        "visualization_meta": dict(result.visualization.metadata),
        "report": dict(result.report),
        "metadata": dict(result.metadata),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def test_v3_22_10_runtime_measurement_adapter_step_smoke():
    adapter = build_runtime_measurement_adapter(preset_name="learning_curve_basic")
    out = adapter.step(records=_records(), metadata={"source": "runtime_measurement_smoke"})

    assert isinstance(adapter, RuntimeMeasurementAdapter)
    assert out.metadata["runtime_measurement"]["preset_name"] == "learning_curve_basic"
    assert out.metadata["runtime_measurement"]["normalization"] == "runtime_measurement_records_v1"
    assert out.metadata["pipeline_order"] == ["analyze", "visualize", "report", "finalize"]


def test_v3_22_10_runtime_measurement_adapter_is_hash_stable_for_fixed_records():
    adapter = build_runtime_measurement_adapter(preset_name="learning_curve_basic")
    hashes = [
        _measurement_hash(
            adapter.step(records=_records(), metadata={"source": "runtime_measurement_stability"})
        )
        for _ in range(20)
    ]
    assert len(set(hashes)) == 1
