from __future__ import annotations

import math

from virtual_shaping_lab.vsl.agent.observation import (
    GeneralizationArtifact,
    GeneralizationOperator,
    IdentityGeneralizationOperator,
    SimilarityKernelGeneralizationOperator,
    StaticContextTagOperator,
)
from virtual_shaping_lab.vsl.agent.observation.operators.representation import IdentityRepresentationOperator


def _contextual_state():
    rep = IdentityRepresentationOperator().represent(raw_stimulus={"tone": 1.0, "noise": 0.5})
    ctx = StaticContextTagOperator(context_tags=["A", "B"])
    return ctx.contextualize(representation=rep, context_state="A")


def test_v3_19_5_identity_generalization_operator_passthrough():
    op = IdentityGeneralizationOperator()
    out = op.generalize(contextual_state=_contextual_state())

    assert isinstance(op, GeneralizationOperator)
    assert isinstance(out, GeneralizationArtifact)
    assert out.feature_names == ["noise", "tone", "ctx:A", "ctx:B"]
    assert out.features == [0.5, 1.0, 1.0, 0.0]
    assert out.generalized_state["kind"] == "identity"
    assert out.metadata["variant"] == "identity_generalization"


def test_v3_19_5_similarity_kernel_generalization_operator_appends_similarity_signal():
    op = SimilarityKernelGeneralizationOperator(sigma=2.0)
    out = op.generalize(contextual_state=_contextual_state())

    assert isinstance(out, GeneralizationArtifact)
    assert out.feature_names[-1] == "gen:similarity_kernel"

    # Expected RBF signal exp(-||x||^2 / (2 * sigma^2)).
    base = [0.5, 1.0, 1.0, 0.0]
    expected = math.exp(-(sum(v * v for v in base) / (2.0 * 4.0)))
    assert out.features[-1] == expected
    assert out.metadata["variant"] == "similarity_kernel"

