from __future__ import annotations

from virtual_shaping_lab.vsl.agent.observation import (
    ContextOperator,
    GeneralizationOperator,
    NullContextOperator,
    NullGeneralizationOperator,
    RepresentationOperator,
)


def test_v3_19_5_null_context_operator_is_noop():
    op = NullContextOperator()
    representation = {"x": [1.0, 0.0]}
    out = op.contextualize(representation=representation, context_state={"ctx": "A"})
    assert out == representation
    assert op.axis == "C"
    assert op.variant == "null_context"


def test_v3_19_5_null_generalization_operator_is_noop():
    op = NullGeneralizationOperator()
    contextual_state = {"x_ctx": [1.0, 0.0, 1.0]}
    out = op.generalize(contextual_state=contextual_state)
    assert out == contextual_state
    assert op.axis == "G"
    assert op.variant == "null_generalization"


def test_v3_19_5_observation_operator_protocols_are_runtime_checkable():
    class _Representation:
        def represent(self, *, raw_stimulus, metadata=None):
            _ = metadata
            return raw_stimulus

    class _Context:
        def contextualize(self, *, representation, context_state=None, metadata=None):
            _ = metadata
            return {"representation": representation, "context_state": context_state}

    class _Generalization:
        def generalize(self, *, contextual_state, metadata=None):
            _ = metadata
            return contextual_state

    assert isinstance(_Representation(), RepresentationOperator)
    assert isinstance(_Context(), ContextOperator)
    assert isinstance(_Generalization(), GeneralizationOperator)

