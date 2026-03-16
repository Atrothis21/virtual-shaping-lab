import numpy as np
import pytest

from agents.representations.base import RepresentationBase
from agents.math_objects.representation_objects import DefaultContextMap, MatrixSimilarityKernel
from agents.math_objects.salience_objects import DiagonalSalienceOperator
from agents.math_objects.temporal_objects import (
    BinnedTemporalBasis,
    IdentityTemporalBasis,
    TraceTemporalBasis,
    build_temporal_basis,
)
from agents.representations.identity import IdentityRepresentation
from agents.representations.observation import make_observation, DEFAULT_CONTEXT
from agents.representations.observation_encoder import ObservationVectorEncoder
from agents.representations.mechanisms import encode_with_mechanisms
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
from domain.types import EncodedState


class DummyRepresentation(RepresentationBase):
    name = "dummy"

    def encode(self, observation):
        return EncodedState(x=np.asarray([1.0, 2.0], dtype=float))

    @property
    def dimension(self):
        return 2


def test_representation_base_hooks():
    rep = DummyRepresentation()
    assert rep.dimension == 2
    assert rep.encode({}).x.shape == (2,)
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
    rep = IdentityRepresentation(params={"dimension": 2})
    obs = make_observation(["tone"], "A", metadata={"vector": [1.0, 0.5]})
    state = rep.encode(obs)
    np.testing.assert_allclose(state.x, np.asarray([1.0, 0.5], dtype=float))


def test_make_observation_defaults():
    with pytest.raises(ValueError):
        make_observation(None, "A")

    obs = make_observation(["tone"], None)
    assert obs.context == DEFAULT_CONTEXT
    assert obs.compound is False


def test_default_context_map_normalizes_missing_context():
    ctx_map = DefaultContextMap()
    obs = make_observation(["tone"], None)
    normalized = ctx_map.apply(obs, obs.context)
    assert normalized.context == DEFAULT_CONTEXT


def test_matrix_similarity_kernel_contract_and_spread():
    kernel = MatrixSimilarityKernel({"tone": {"noise": 0.4}})
    assert kernel.similarity("tone", "tone") == pytest.approx(1.0)
    assert kernel.similarity("tone", "noise") == pytest.approx(0.4)
    assert kernel.similarity("noise", "tone") == pytest.approx(0.0)

    weights = kernel.spread_weights(["tone"])
    assert weights["tone"] == pytest.approx(1.0)
    assert weights["noise"] == pytest.approx(0.4)


def test_diagonal_salience_operator_scales_and_handles_short_vectors():
    operator = DiagonalSalienceOperator(np.asarray([0.5, 0.25], dtype=float))
    np.testing.assert_allclose(
        operator.apply(np.asarray([1.0, 2.0], dtype=float)),
        np.asarray([0.5, 0.5], dtype=float),
    )

    np.testing.assert_allclose(
        operator.apply(np.asarray([1.0, 2.0, 3.0], dtype=float)),
        np.asarray([0.5, 0.5, 3.0], dtype=float),
    )


def test_temporal_basis_objects_encode_fixed_dimension_vectors():
    identity = IdentityTemporalBasis(dimension=2, scale=2.0)
    np.testing.assert_allclose(identity.encode(t_s=1.0, dt_s=0.5), np.asarray([0.5, 0.5]))

    bins = BinnedTemporalBasis(dimension=4, max_time_s=2.0)
    assert bins.encode(t_s=0.6).shape == (4,)
    assert bins.encode(t_s=0.6).sum() == pytest.approx(1.0)

    traces = TraceTemporalBasis(dimension=3, decay=1.0)
    out = traces.encode(t_s=1.0)
    assert out.shape == (3,)
    assert out[0] > out[1] > out[2]


def test_build_temporal_basis_from_representation_config():
    basis = build_temporal_basis(
        {"enabled": True, "variant": "identity", "dimension": 1, "params": {"scale": 2.0}}
    )
    assert isinstance(basis, IdentityTemporalBasis)

    assert build_temporal_basis({"enabled": False, "variant": "identity", "dimension": 1}) is None


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

    assert e_vec.x.shape == (elemental.dimension,)
    assert c_vec.x.shape == (configural.dimension,)
    assert h_vec.x.shape == (hybrid.dimension,)

    with pytest.raises(ValueError, match="learner-owned"):
        VectorConfiguralRepresentation(
            params={
                "stimuli": ["tone", "noise"],
                "contexts": ["A"],
                "attention": {"tone": 0.6},
            }
        )

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

    vec = rep.encode(make_observation(["tone"], "A")).x
    idx_global_tone = rep._encoder._index["global:tone"]
    idx_ctx_tone = rep._encoder._index["ctx:A|tone"]
    idx_global_noise = rep._encoder._index["global:noise"]

    assert vec[idx_global_tone] == pytest.approx(0.5)
    assert vec[idx_ctx_tone] == pytest.approx(0.5)
    assert vec[idx_global_noise] == pytest.approx(0.0)


def test_temporal_basis_augments_representation_dimension_and_uses_time_fields():
    rep = VectorElementalRepresentation(
        params={
            "stimuli": ["tone"],
            "contexts": ["A"],
            "include_global": True,
            "include_context": True,
            "temporal_basis": {
                "enabled": True,
                "variant": "identity",
                "dimension": 2,
                "params": {"scale": 2.0},
            },
        }
    )

    obs = make_observation(["tone"], "A", t_s=1.0, dt_s=0.25)
    vec = rep.encode(obs).x
    assert rep.dimension == vec.shape[0]
    np.testing.assert_allclose(vec[-2:], np.asarray([0.5, 0.25]))


def test_temporal_basis_preserves_compatibility_when_time_fields_absent():
    rep = VectorElementalRepresentation(
        params={
            "stimuli": ["tone"],
            "contexts": ["A"],
            "include_global": True,
            "include_context": True,
            "temporal_basis": {
                "enabled": True,
                "variant": "identity",
                "dimension": 1,
            },
        }
    )

    vec = rep.encode(make_observation(["tone"], "A")).x
    assert vec[-1] == pytest.approx(0.0)


def test_disabled_temporal_basis_matches_no_temporal_augmentation_baseline():
    base = VectorElementalRepresentation(
        params={
            "stimuli": ["tone"],
            "contexts": ["A"],
            "include_global": True,
            "include_context": True,
        }
    )
    disabled = VectorElementalRepresentation(
        params={
            "stimuli": ["tone"],
            "contexts": ["A"],
            "include_global": True,
            "include_context": True,
            "temporal_basis": {
                "enabled": False,
                "variant": "identity",
                "dimension": 2,
            },
        }
    )

    obs = make_observation(["tone"], "A")
    np.testing.assert_allclose(base.encode(obs).x, disabled.encode(obs).x)


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


def test_similarity_identity_matrix_matches_no_similarity_elemental():
    base_params = {
        "stimuli": ["tone", "noise"],
        "contexts": ["A"],
        "include_global": True,
        "include_context": True,
        "max_compound_size": 2,
    }
    identity_params = {
        **base_params,
        "similarity": {
            "type": "matrix",
            "stimuli": ["tone", "noise"],
            "values": [
                [1.0, 0.0],
                [0.0, 1.0],
            ],
        },
    }

    rep_no_sim = VectorElementalRepresentation(params=base_params)
    rep_identity = VectorElementalRepresentation(params=identity_params)

    obs_single = make_observation(["tone"], "A", compound=False)
    obs_compound = make_observation(["tone", "noise"], "A", compound=True)

    np.testing.assert_allclose(rep_no_sim.encode(obs_single).x, rep_identity.encode(obs_single).x)
    np.testing.assert_allclose(rep_no_sim.encode(obs_compound).x, rep_identity.encode(obs_compound).x)


def test_similarity_non_identity_spreads_activation_elemental():
    params = {
        "stimuli": ["tone", "noise"],
        "contexts": ["A"],
        "include_global": True,
        "include_context": True,
        "max_compound_size": 2,
        "similarity": {
            "type": "matrix",
            "stimuli": ["tone", "noise"],
            "values": [
                [1.0, 0.4],
                [0.4, 1.0],
            ],
        },
    }
    rep = VectorElementalRepresentation(params=params)
    vec = rep.encode(make_observation(["tone"], "A", compound=False)).x

    idx_global_noise = rep._encoder._index["global:noise"]
    idx_ctx_noise = rep._encoder._index["ctx:A|noise"]
    idx_global_tone = rep._encoder._index["global:tone"]
    idx_ctx_tone = rep._encoder._index["ctx:A|tone"]

    assert vec[idx_global_tone] == pytest.approx(1.0)
    assert vec[idx_ctx_tone] == pytest.approx(1.0)
    assert vec[idx_global_noise] == pytest.approx(0.4)
    assert vec[idx_ctx_noise] == pytest.approx(0.4)


def test_similarity_then_salience_order_is_deterministic():
    rep = VectorElementalRepresentation(
        params={
            "stimuli": ["tone", "noise"],
            "contexts": ["A"],
            "include_global": True,
            "include_context": True,
            "salience": {"tone": 0.5, "noise": 0.25},
            "similarity": {
                "type": "matrix",
                "stimuli": ["tone", "noise"],
                "values": [
                    [1.0, 0.4],
                    [0.4, 1.0],
                ],
            },
        }
    )
    vec = rep.encode(make_observation(["tone"], "A", compound=False)).x
    idx_global_tone = rep._encoder._index["global:tone"]
    idx_global_noise = rep._encoder._index["global:noise"]

    # tone activation: 1.0 then salience 0.5 -> 0.5
    assert vec[idx_global_tone] == pytest.approx(0.5)
    # similarity spread to noise: 0.4 then salience 0.25 -> 0.1
    assert vec[idx_global_noise] == pytest.approx(0.1)


def test_representation_mechanism_chain_order_is_context_similarity_encoder_then_salience():
    calls = []

    class TracingContextMap:
        def apply(self, observation, context):
            calls.append("context")
            return observation

    class TracingSimilarityKernel:
        def spread_weights(self, present):
            calls.append("similarity")
            return {str(item): 1.0 for item in present}

    class TracingSalienceOperator:
        def apply(self, vector):
            calls.append("salience")
            return vector

    class TracingEncoder:
        mode = "elemental"
        dimension = 2

        def add_elemental_features(self, vec, features, context, weights=None):
            calls.append("encoder")
            vec[0] = 1.0

        def add_compound_feature(self, vec, features, context):
            calls.append("compound")

    encode_with_mechanisms(
        TracingEncoder(),
        make_observation(["tone"], "A"),
        similarity_map={},
        salience=np.asarray([1.0, 1.0], dtype=float),
        context_map=TracingContextMap(),
        similarity_kernel=TracingSimilarityKernel(),
        salience_operator=TracingSalienceOperator(),
    )

    assert calls == ["context", "similarity", "encoder", "salience"]


def test_similarity_then_salience_order_is_not_equivalent_to_salience_then_similarity():
    observation = make_observation(["tone"], "A", compound=False)
    encoder = ObservationVectorEncoder(
        feature_vocab=["global:tone", "ctx:A|tone", "global:noise", "ctx:A|noise"],
        mode="elemental",
    )
    similarity_kernel = MatrixSimilarityKernel({"tone": {"noise": 0.4}})
    salience_operator = DiagonalSalienceOperator(np.asarray([0.5, 0.5, 0.25, 0.25], dtype=float))

    ordered = encode_with_mechanisms(
        encoder,
        observation,
        similarity_map={},
        salience=np.asarray([0.5, 0.5, 0.25, 0.25], dtype=float),
        context_map=DefaultContextMap(),
        similarity_kernel=similarity_kernel,
        salience_operator=salience_operator,
    )

    # Forbidden alternative: salience on the direct observation vector before similarity spread.
    pre_scaled = np.zeros(encoder.dimension, dtype=float)
    encoder.add_elemental_features(pre_scaled, ["tone"], "A", weights={"tone": 1.0})
    pre_scaled = salience_operator.apply(pre_scaled)
    reordered = pre_scaled.copy()
    reordered[encoder._index["global:noise"]] += 0.4
    reordered[encoder._index["ctx:A|noise"]] += 0.4

    assert ordered[encoder._index["global:noise"]] == pytest.approx(0.1)
    assert reordered[encoder._index["global:noise"]] == pytest.approx(0.4)
    assert not np.allclose(ordered, reordered)
