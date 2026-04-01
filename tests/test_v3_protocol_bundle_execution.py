from __future__ import annotations

from virtual_shaping_lab.vsl.protocol import (
    ActionConditionedConsequenceOperator,
    ProtocolBundle,
    ProtocolStepResult,
    ScheduledEmissionOperator,
    TrialAdvanceOperator,
    TrialCountStopOperator,
)


def test_v3_21_5_protocol_bundle_step_canonical_execution_and_output_shape():
    bundle = ProtocolBundle(
        emission_operator=ScheduledEmissionOperator(
            schedule=(
                {"stimulus": {"tone": 1.0}, "context": "A", "available_actions": ("leverpress",)},
            ),
            loop=True,
        ),
        consequence_operator=ActionConditionedConsequenceOperator(
            reward_by_action={"leverpress": 1.0},
            default_reward=0.0,
        ),
        advance_operator=TrialAdvanceOperator(dt_s=1.0),
        stop_operator=TrialCountStopOperator(max_trials=2),
    )

    out = bundle.step(action="leverpress", metadata={"source": "bundle_test"})

    assert isinstance(out, ProtocolStepResult)
    assert out.emission.stimulus == {"tone": 1.0}
    assert out.consequence.reward == 1.0
    assert out.advance.t == 1
    assert out.stop.should_stop is False
    assert out.metadata["pipeline_order"] == ["emit", "consequence", "advance", "stop", "finalize"]
    traces = out.metadata["stage_traces"]
    assert set(traces.keys()) == {"emission", "consequence", "advance", "stop"}
    assert traces["emission"]["context"] == "A"
    assert traces["consequence"]["reward"] == 1.0
    assert traces["advance"]["t"] == 1
    assert traces["stop"]["should_stop"] is False


def test_v3_21_5_protocol_bundle_step_order_is_emit_consequence_advance_stop_finalize():
    calls: list[str] = []

    class _Emission:
        def emit(self, *, state, metadata=None):
            calls.append("emit")
            _ = state, metadata
            return {
                "stimulus": {"tone": 1.0},
                "context": "A",
                "available_actions": ("leverpress",),
                "metadata": {"variant": "emit_stub"},
            }

    class _Consequence:
        def consequence(self, *, emission, action, state, metadata=None):
            calls.append("consequence")
            _ = emission, action, state, metadata
            return {
                "reward": 0.5,
                "done": False,
                "metadata": {"variant": "con_stub"},
            }

    class _Advance:
        def advance(self, *, state, consequence, metadata=None):
            calls.append("advance")
            _ = state, consequence, metadata
            return {
                "t": 1,
                "dt_s": 0.5,
                "phase_step": 1,
                "metadata": {"variant": "adv_stub"},
            }

    class _Stop:
        def should_stop(self, *, state, advance, consequence, metadata=None):
            calls.append("stop")
            _ = state, advance, consequence, metadata
            return {
                "should_stop": False,
                "reason": None,
                "metadata": {"variant": "stop_stub"},
            }

    bundle = ProtocolBundle(
        emission_operator=_Emission(),
        consequence_operator=_Consequence(),
        advance_operator=_Advance(),
        stop_operator=_Stop(),
    )
    out = bundle.step(action="leverpress")

    assert out.advance.t == 1
    assert out.consequence.reward == 0.5
    assert calls == ["emit", "consequence", "advance", "stop"]
