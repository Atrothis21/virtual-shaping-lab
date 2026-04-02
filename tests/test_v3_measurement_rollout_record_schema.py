from __future__ import annotations

from virtual_shaping_lab.vsl.environment import EnvironmentStep, EnvironmentTermination
from virtual_shaping_lab.vsl.rollout import step_to_rollout_record


def test_v3_22_15_rollout_step_adapter_promotes_measurement_traces_into_record_metadata():
    step = EnvironmentStep(
        step_index=8,
        segment_key="seg_measurement",
        protocol="acquisition",
        trial_type="cs_plus",
        trial_index=0,
        action=None,
        stimulus={"cs_plus": ["tone"]},
        reward=1.0,
        done=False,
        termination=EnvironmentTermination(done=False, reason="running"),
        metadata={
            "measurement_traces": {
                "metrics": {"trial_count": 3, "mean_reward": 0.5},
                "figures": [{"kind": "line", "title": "Learning Curve"}],
                "summary": {"format": "markdown", "title": "Measurement Report"},
                "provenance": {"preset_name": "learning_curve_basic"},
            }
        },
    )
    record = step_to_rollout_record(step)

    assert record.metadata["measurement_traces"] == {
        "metrics": {"trial_count": 3, "mean_reward": 0.5},
        "figures": [{"kind": "line", "title": "Learning Curve"}],
        "summary": {"format": "markdown", "title": "Measurement Report"},
        "provenance": {"preset_name": "learning_curve_basic"},
    }


def test_v3_22_15_rollout_step_adapter_materializes_measurement_trace_defaults():
    step = EnvironmentStep(
        step_index=9,
        segment_key="seg_measurement_default",
        protocol="acquisition",
        trial_type="cs_plus",
        trial_index=1,
        action=None,
        stimulus={"cs_plus": ["tone"]},
        reward=0.0,
        done=False,
        termination=EnvironmentTermination(done=False, reason="running"),
        metadata={"source": "env"},
    )
    record = step_to_rollout_record(step)

    assert record.metadata["measurement_traces"] == {
        "metrics": {},
        "figures": [],
        "summary": {},
        "provenance": {},
    }
