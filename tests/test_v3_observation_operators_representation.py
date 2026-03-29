from __future__ import annotations

from virtual_shaping_lab.vsl.agent.observation import (
    ElementalRepresentationOperator,
    IdentityRepresentationOperator,
    MinimalConfiguralRepresentationOperator,
    RepresentationArtifact,
    RepresentationOperator,
)


def test_v3_19_5_identity_representation_operator_contract_shape():
    op = IdentityRepresentationOperator()
    out = op.represent(raw_stimulus={"noise": 0.2, "tone": 1.0})

    assert isinstance(op, RepresentationOperator)
    assert isinstance(out, RepresentationArtifact)
    assert out.feature_names == ["noise", "tone"]
    assert out.features == [0.2, 1.0]
    assert out.metadata["variant"] == "identity"


def test_v3_19_5_elemental_representation_operator_respects_universe_order():
    op = ElementalRepresentationOperator(stimulus_universe=["tone", "noise", "light"])
    out = op.represent(raw_stimulus={"noise": 0.5, "tone": 1.0})

    assert out.feature_names == ["tone", "noise", "light"]
    assert out.features == [1.0, 0.5, 0.0]
    assert out.metadata["variant"] == "elemental"


def test_v3_19_5_minimal_configural_representation_adds_pairwise_conjunctions():
    op = MinimalConfiguralRepresentationOperator(stimulus_universe=["tone", "noise", "light"])
    out = op.represent(raw_stimulus={"tone": 1.0, "noise": 0.6, "light": 0.0})

    assert out.feature_names[:3] == ["tone", "noise", "light"]
    assert out.features[:3] == [1.0, 0.6, 0.0]
    assert "cfg:tone&noise" in out.feature_names
    idx = out.feature_names.index("cfg:tone&noise")
    assert out.features[idx] == 0.6
    assert all(not name.endswith("light") for name in out.feature_names[3:])
    assert out.metadata["variant"] == "minimal_configural"

