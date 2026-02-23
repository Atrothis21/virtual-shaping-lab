import numpy as np
import pytest

from agents.representations.base import RepresentationBase
from agents.representations.identity import IdentityRepresentation
from agents.representations.observation import make_observation, DEFAULT_CONTEXT
from agents.representations.observation_encoder import ObservationVectorEncoder
from agents.representations.similarity import parse_similarity_matrix, build_similarity_weights
from agents.representations.vector_encoder import (
    VectorEncoder,
    IdentityVectorEncoder,
    FeatureListVectorEncoder,
)
from agents.representations.vector_elemental import VectorElementalRepresentation
from agents.representations.vector_configural import VectorConfiguralRepresentation
from agents.representations.vector_hybrid import VectorHybridRepresentation
from agents.representations.vocab import (
    build_feature_vocab,
    build_feature_weight_vector,
)


class DummyRepresentation(RepresentationBase):
    name = "dummy"

    def encode(self, observation):
        return np.asarray([1.0, 2.0])

    @property
    def dimension(self):
        return 2


def test_representation_base_hooks():
    rep = DummyRepresentation()
    assert rep.dimension == 2
    assert rep.encode({}).shape == (2,)
    assert rep.reset() is None
    assert rep.get_summary() == {}

    class BadRepresentation(RepresentationBase):
        name = "bad"

        def encode(self, observation):
            return super().encode(observation)

        @property
        def dimension(self):
            return super().dimension

    bad = BadRepresentation()
    with pytest.raises(NotImplementedError):
        bad.encode({})
    with pytest.raises(NotImplementedError):
        _ = bad.dimension


def test_identity_representation():
    rep = IdentityRepresentation()
    assert rep.encode("tone") == "tone"


def test_make_observation_defaults():
    with pytest.raises(ValueError):
        make_observation(None, "A")

    obs = make_observation(["tone"], None)
    assert obs["context"] == DEFAULT_CONTEXT
    assert obs["compound"] is False


def test_observation_vector_encoder_errors_and_encode():
    with pytest.raises(ValueError):
        ObservationVectorEncoder(feature_vocab=[])

    with pytest.raises(ValueError):
        ObservationVectorEncoder(feature_vocab=["x"], mode="bad")

    with pytest.raises(ValueError):
        ObservationVectorEncoder(feature_vocab=["x"], include_global=False, include_context=False)

    vocab = [
        "global:tone",
        "ctx:A|tone",
        "global:noise",
        "ctx:A|noise",
        "global:compound:noise|tone",
        "ctx:A|compound:noise|tone",
    ]
    enc = ObservationVectorEncoder(feature_vocab=vocab, mode="hybrid")

    obs = make_observation(["tone", "noise"], "A", compound=True)
    vec = enc.encode(obs)
    assert vec.shape == (len(vocab),)

    with pytest.raises(ValueError):
        enc.encode(make_observation(["unknown"], "A"))


def test_similarity_parsing_and_weights():
    assert parse_similarity_matrix(None, ["a"]) == {}
    with pytest.raises(ValueError):
        parse_similarity_matrix({"type": "other"}, ["a"])

    with pytest.raises(ValueError):
        parse_similarity_matrix({"type": "matrix", "values": []}, ["a"])

    with pytest.raises(ValueError):
        parse_similarity_matrix({"type": "matrix", "values": [[1.0]]}, ["a", "b"])

    with pytest.raises(ValueError):
        parse_similarity_matrix({"type": "matrix", "values": [[1.0, 0.2], [0.3]]}, ["a", "b"])

    with pytest.raises(ValueError):
        parse_similarity_matrix({"type": "matrix", "values": [[1.0, "x"], [0.3, 1.0]]}, ["a", "b"])

    with pytest.raises(ValueError):
        parse_similarity_matrix({"type": "matrix", "values": [[1.2, 0.2], [0.3, 1.0]]}, ["a", "b"])

    sim = parse_similarity_matrix(
        {"type": "matrix", "stimuli": ["a", "b"], "values": [[1.0, 0.5], [0.2, 1.0]]},
        ["a", "b"],
    )
    weights = build_similarity_weights(["a"], sim)
    assert weights["a"] == 1.0
    assert weights["b"] == 0.5

    weights = build_similarity_weights(["b"], {"b": {"a": -1, "b": 2, "c": "bad"}})
    assert weights["a"] == 0.0
    assert weights["b"] == 1.0


def test_vector_encoder_variants():
    class BadVectorEncoder(VectorEncoder):
        def encode(self, observation):
            return super().encode(observation)

        @property
        def dimension(self):
            return super().dimension

    bad = BadVectorEncoder()
    with pytest.raises(NotImplementedError):
        bad.encode([])
    with pytest.raises(NotImplementedError):
        _ = bad.dimension

    enc = IdentityVectorEncoder(dimension=2)
    with pytest.raises(ValueError):
        enc.encode(np.asarray([1.0, 2.0, 3.0]))

    vec = enc.encode(np.asarray([1.0, 2.0]))
    assert vec.shape == (2,)
    assert enc.dimension == 2

    fl = FeatureListVectorEncoder(feature_vocab=["A", "B"])
    assert fl.encode("A").tolist() == [1.0, 0.0]
    assert fl.encode(["A", "B"]).tolist() == [1.0, 1.0]

    with pytest.raises(ValueError):
        FeatureListVectorEncoder(feature_vocab=[])
    with pytest.raises(ValueError):
        fl.encode(123)
    with pytest.raises(ValueError):
        fl.encode(["C"])


def test_vocab_builders_and_weight_vector():
    with pytest.raises(ValueError):
        build_feature_vocab(["tone"], include_global=False, include_context=False)

    vocab, salience = build_feature_vocab(
        stimuli=["tone", "noise"],
        include_compounds=True,
        max_compound_size=2,
        contexts=["A"],
        salience={"tone": 0.5},
        compound_salience="product",
    )
    assert vocab
    assert len(vocab) == len(salience)

    vocab_min, _ = build_feature_vocab(
        stimuli=["tone", "noise"],
        include_compounds=True,
        max_compound_size=2,
        contexts=["A"],
        compound_salience="min",
    )
    assert vocab_min

    vocab_mean, _ = build_feature_vocab(
        stimuli=["tone", "noise"],
        include_compounds=True,
        max_compound_size=2,
        contexts=["A"],
        compound_salience="mean",
    )
    assert vocab_mean

    weights = build_feature_weight_vector(
        features=vocab,
        weights={"tone": 0.2, "noise": 0.8},
        compound_rule="max",
    )
    assert len(weights) == len(vocab)

    weights_min = build_feature_weight_vector(
        features=["global:compound:noise|tone"],
        weights={"tone": 0.2, "noise": 0.8},
        compound_rule="min",
    )
    assert weights_min == [0.2]

    weights_prod = build_feature_weight_vector(
        features=["global:compound:noise|tone"],
        weights={"tone": 0.5, "noise": 0.5},
        compound_rule="product",
    )
    assert weights_prod == [0.25]

    weights_empty = build_feature_weight_vector(
        features=["global:compound:"],
        weights={},
    )
    assert weights_empty == [1.0]


def test_vector_representations():
    with pytest.raises(ValueError):
        VectorElementalRepresentation(params={})
    with pytest.raises(ValueError):
        VectorConfiguralRepresentation(params={})
    with pytest.raises(ValueError):
        VectorHybridRepresentation(params={})

    params = {
        "stimuli": ["tone", "noise"],
        "contexts": ["A"],
        "max_compound_size": 2,
        "similarity": {
            "type": "matrix",
            "stimuli": ["tone", "noise"],
            "values": [[1.0, 0.4], [0.4, 1.0]],
        },
    }

    elemental = VectorElementalRepresentation(params=params)
    configural = VectorConfiguralRepresentation(params=params)
    hybrid = VectorHybridRepresentation(params=params)

    obs = make_observation(["tone", "noise"], "A", compound=True)

    e_vec = elemental.encode(obs)
    c_vec = configural.encode(obs)
    h_vec = hybrid.encode(obs)

    assert e_vec.shape == (elemental.dimension,)
    assert c_vec.shape == (configural.dimension,)
    assert h_vec.shape == (hybrid.dimension,)

    configural_attn = VectorConfiguralRepresentation(
        params={
            "stimuli": ["tone", "noise"],
            "contexts": ["A"],
            "attention": {"tone": 0.6},
        }
    )
    _ = configural_attn.encode(make_observation(["tone"], "A", compound=True))

    configural_sim = VectorConfiguralRepresentation(
        params={
            "stimuli": ["tone", "noise"],
            "contexts": ["A"],
            "max_compound_size": 2,
            "include_global": True,
            "include_context": True,
            "similarity": {
                "type": "matrix",
                "stimuli": ["tone", "noise"],
                "values": [[1.0, 0.4], [0.4, 1.0]],
            },
        }
    )
    configural_sim._encoder._mode = "hybrid"
    _ = configural_sim.encode(make_observation(["tone", "noise"], "A", compound=True))

    elemental_sim = VectorElementalRepresentation(
        params={
            "stimuli": ["tone", "noise"],
            "contexts": ["A"],
            "max_compound_size": 2,
            "include_global": True,
            "include_context": True,
            "similarity": {
                "type": "matrix",
                "stimuli": ["tone", "noise"],
                "values": [[1.0, 0.4], [0.4, 1.0]],
            },
        }
    )
    compound_key = "compound:noise|tone"
    global_comp = f"global:{compound_key}"
    ctx_comp = f"ctx:A|{compound_key}"
    if global_comp not in elemental_sim._encoder._index:
        elemental_sim._encoder._vocab.append(global_comp)
        elemental_sim._encoder._index[global_comp] = len(elemental_sim._encoder._vocab) - 1
    if ctx_comp not in elemental_sim._encoder._index:
        elemental_sim._encoder._vocab.append(ctx_comp)
        elemental_sim._encoder._index[ctx_comp] = len(elemental_sim._encoder._vocab) - 1

    elemental_sim._encoder._mode = "hybrid"
    _ = elemental_sim.encode(make_observation(["tone", "noise"], "A", compound=True))


def test_salience_applies_in_representation_encoding():
    rep = VectorElementalRepresentation(
        params={
            "stimuli": ["tone", "noise"],
            "contexts": ["A"],
            "salience": {"tone": 0.5, "noise": 1.0},
            "include_global": True,
            "include_context": True,
        }
    )

    vec = rep.encode(make_observation(["tone"], "A"))
    idx_global_tone = rep._encoder._index["global:tone"]
    idx_ctx_tone = rep._encoder._index["ctx:A|tone"]
    idx_global_noise = rep._encoder._index["global:noise"]

    assert vec[idx_global_tone] == pytest.approx(0.5)
    assert vec[idx_ctx_tone] == pytest.approx(0.5)
    assert vec[idx_global_noise] == pytest.approx(0.0)


def test_parse_similarity_matrix_happy_path():
    sim = {
        "type": "matrix",
        "stimuli": ["tone", "noise"],
        "values": [
            [1.0, 0.2],
            [0.2, 1.0],
        ],
    }
    out = parse_similarity_matrix(sim, ["tone", "noise"])
    assert out["tone"]["noise"] == 0.2


def test_parse_similarity_matrix_rejects_out_of_range():
    sim = {
        "type": "matrix",
        "stimuli": ["tone"],
        "values": [[1.5]],
    }
    with pytest.raises(ValueError):
        parse_similarity_matrix(sim, ["tone"])


def test_build_similarity_weights_max_aggregation():
    sim_map = {
        "tone": {"noise": 0.3},
        "noise": {"tone": 0.6},
    }
    weights = build_similarity_weights(["tone"], sim_map)
    assert weights["tone"] == 1.0
    assert weights["noise"] == 0.3
