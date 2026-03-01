from __future__ import annotations

from domain.types import Observation
from experiment.domain.types import StepResult
from protocols.step_adapter import ProtocolStepAdapter


def test_protocol_step_adapter_enriches_record_and_metadata():
    adapter = ProtocolStepAdapter("dummy_protocol")
    records = []
    step = StepResult(
        observation=Observation(stimuli=["tone"], context="A"),
        reward=0.1,
        done=False,
        metadata={"record": {"trial": 0, "prediction": 0.2}},
    )

    out = adapter.adapt(
        step=step,
        phase_name="dummy_phase",
        phase_index=0,
        is_last_phase=False,
        trial_index=0,
        n_trials=2,
        records_sink=records,
    )

    assert len(records) == 1
    assert out.metadata["protocol_name"] == "dummy_protocol"
    assert out.metadata["phase_name"] == "dummy_phase"
    assert out.metadata["record"]["subphase"] == 0
    assert out.metadata["record"]["phase_name"] == "dummy_phase"
    assert out.done is False


def test_protocol_step_adapter_marks_done_for_last_step_of_last_phase():
    adapter = ProtocolStepAdapter("dummy_protocol")
    records = []
    step = StepResult(
        observation=Observation(stimuli=["tone"], context="A"),
        reward=0.0,
        done=True,
        metadata={},
    )
    out = adapter.adapt(
        step=step,
        phase_name="dummy_phase",
        phase_index=1,
        is_last_phase=True,
        trial_index=1,
        n_trials=2,
        records_sink=records,
    )
    assert out.done is True

