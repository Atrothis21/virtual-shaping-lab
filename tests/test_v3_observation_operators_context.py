from __future__ import annotations

from virtual_shaping_lab.vsl.agent.observation import (
    ContextArtifact,
    ContextOperator,
    IdentityRepresentationOperator,
    StaticContextTagOperator,
    null_contextualize,
)


def test_v3_19_5_null_context_helper_preserves_representation_features():
    rep = IdentityRepresentationOperator().represent(raw_stimulus={"tone": 1.0, "noise": 0.2})
    out = null_contextualize(representation=rep, context_state="A")
    assert isinstance(out, ContextArtifact)
    assert out.features == rep.features
    assert out.feature_names == rep.feature_names
    assert out.metadata["variant"] == "null_context"


def test_v3_19_5_static_context_tag_operator_appends_one_hot_context():
    rep = IdentityRepresentationOperator().represent(raw_stimulus={"tone": 1.0})
    op = StaticContextTagOperator(context_tags=["A", "B"])
    out = op.contextualize(representation=rep, context_state="B")

    assert isinstance(op, ContextOperator)
    assert isinstance(out, ContextArtifact)
    assert out.feature_names == ["tone", "ctx:A", "ctx:B"]
    assert out.features == [1.0, 0.0, 1.0]
    assert out.metadata["variant"] == "static_context_tag"

