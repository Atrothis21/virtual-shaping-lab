from __future__ import annotations

from virtual_shaping_lab.vsl.agent.learning.operators import (
    AttentionOperator,
    EligibilityOperator,
    ErrorOperator,
    NullAttentionOperator,
    NullEligibilityOperator,
    NullTraceOperator,
    PredictionOperator,
    UpdateOperator,
)


class _PredictionImpl:
    def __call__(self, *, features, state=None):
        _ = state
        return float(sum(float(v) for v in features.values()))


class _ErrorImpl:
    def __call__(self, *, reward, prediction, next_prediction=None, done=False):
        _ = next_prediction, done
        return float(reward) - float(prediction)


class _UpdateImpl:
    def __call__(self, *, state, features, error, step_size):
        total = sum(float(v) for v in features.values())
        state["w"] = float(state.get("w", 0.0)) + float(step_size) * float(error) * total
        return state


class _AttentionImpl:
    def apply(self, *, attention_state, features, error):
        state = dict(attention_state or {})
        for key, value in features.items():
            state[str(key)] = float(state.get(str(key), 0.0)) + float(error) * float(value)
        return state


class _EligibilityImpl:
    def apply(self, *, eligibility_state, features, discount, trace_decay):
        state = dict(eligibility_state or {})
        coeff = float(discount) * float(trace_decay)
        for key, value in features.items():
            state[str(key)] = coeff * float(state.get(str(key), 0.0)) + float(value)
        return state


def test_v3_18_5_operator_protocols_are_runtime_checkable():
    assert isinstance(_PredictionImpl(), PredictionOperator)
    assert isinstance(_ErrorImpl(), ErrorOperator)
    assert isinstance(_UpdateImpl(), UpdateOperator)
    assert isinstance(_AttentionImpl(), AttentionOperator)
    assert isinstance(_EligibilityImpl(), EligibilityOperator)


def test_v3_18_5_null_optional_operators_are_stable_noops():
    attn = NullAttentionOperator()
    elig = NullEligibilityOperator()
    trace = NullTraceOperator()

    assert attn.slot == "A"
    assert attn.variant == "null_attention"
    assert elig.slot == "E"
    assert elig.variant == "null_trace"
    assert trace.slot == "E"
    assert trace.variant == "null_trace"

    attention_state = {"tone": 0.3}
    eligibility_state = {"tone": 0.7}
    features = {"tone": 1.0}

    assert attn.apply(attention_state=attention_state, features=features, error=0.2) == attention_state
    assert (
        elig.apply(
            eligibility_state=eligibility_state,
            features=features,
            discount=0.9,
            trace_decay=0.8,
        )
        == eligibility_state
    )

