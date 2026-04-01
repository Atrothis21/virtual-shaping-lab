from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.protocol import (
    AdvanceOperator,
    AdvanceOutput,
    ConsequenceOperator,
    ConsequenceOutput,
    EmissionOperator,
    EmissionOutput,
    ProtocolStepResult,
    StopOperator,
    StopOutput,
)


def test_v3_21_5_protocol_operator_protocols_are_runtime_checkable():
    class _Emission:
        def emit(self, *, state, metadata=None):
            _ = state, metadata
            return EmissionOutput(stimulus={"tone": 1.0})

    class _Consequence:
        def consequence(self, *, emission, action, state, metadata=None):
            _ = emission, action, state, metadata
            return ConsequenceOutput(reward=1.0, done=False)

    class _Advance:
        def advance(self, *, state, consequence, metadata=None):
            _ = state, consequence, metadata
            return AdvanceOutput(t=1, dt_s=1.0, phase_step=1)

    class _Stop:
        def should_stop(self, *, state, advance, consequence, metadata=None):
            _ = state, advance, consequence, metadata
            return StopOutput(should_stop=False, reason=None)

    assert isinstance(_Emission(), EmissionOperator)
    assert isinstance(_Consequence(), ConsequenceOperator)
    assert isinstance(_Advance(), AdvanceOperator)
    assert isinstance(_Stop(), StopOperator)


def test_v3_21_5_protocol_stage_outputs_require_object_metadata():
    with pytest.raises(ValueError, match="metadata"):
        EmissionOutput(stimulus={"tone": 1.0}, metadata="bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="metadata"):
        ConsequenceOutput(reward=1.0, metadata="bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="metadata"):
        AdvanceOutput(t=1, metadata="bad")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="metadata"):
        StopOutput(should_stop=False, metadata="bad")  # type: ignore[arg-type]


def test_v3_21_5_protocol_step_result_requires_typed_stage_outputs():
    with pytest.raises(ValueError, match="emission"):
        ProtocolStepResult(  # type: ignore[arg-type]
            emission={"stimulus": {"tone": 1.0}},
            consequence=ConsequenceOutput(),
            advance=AdvanceOutput(t=0),
            stop=StopOutput(should_stop=False),
        )

