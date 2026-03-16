import numpy as np
import pytest

from agents.learners.attention_strategies import AttentionContext
from agents.math_objects.attention_objects import build_attention_mechanism
from agents.math_objects.prediction_error_objects import (
    RescorlaWagnerPredictionError,
    TD0PredictionError,
)
from agents.math_objects.representation_objects import DefaultContextMap, MatrixSimilarityKernel
from agents.math_objects.salience_objects import DiagonalSalienceOperator
from agents.math_objects.temporal_objects import (
    BinnedTemporalBasis,
    IdentityTemporalBasis,
    TraceTemporalBasis,
)
from agents.representations.observation import DEFAULT_CONTEXT, make_observation


def test_context_map_preserves_observation_shape_and_normalizes_missing_context():
    context_map = DefaultContextMap()
    obs = make_observation(["tone"], None)

    normalized = context_map.apply(obs, obs.context)

    assert normalized.stimuli == obs.stimuli
    assert normalized.context == DEFAULT_CONTEXT


def test_similarity_kernel_is_bounded_and_identity_preserving():
    kernel = MatrixSimilarityKernel(
        {
            "tone": {"noise": 1.7, "light": -0.5},
            "noise": {"tone": 0.25},
        }
    )

    assert kernel.similarity("tone", "tone") == pytest.approx(1.0)
    assert kernel.similarity("tone", "noise") == pytest.approx(1.0)
    assert kernel.similarity("tone", "light") == pytest.approx(0.0)
    assert kernel.similarity("noise", "tone") == pytest.approx(0.25)


def test_similarity_kernel_spread_weights_are_bounded_and_include_present_features():
    kernel = MatrixSimilarityKernel({"tone": {"noise": 0.4, "light": 2.0}})

    weights = kernel.spread_weights(["tone"])

    assert weights["tone"] == pytest.approx(1.0)
    assert weights["noise"] == pytest.approx(0.4)
    assert weights["light"] == pytest.approx(1.0)
    assert all(0.0 <= value <= 1.0 for value in weights.values())


def test_salience_operator_preserves_vector_shape():
    operator = DiagonalSalienceOperator(np.asarray([0.5, 0.25], dtype=float))
    vector = np.asarray([2.0, 4.0, 8.0], dtype=float)

    out = operator.apply(vector)

    assert out.shape == vector.shape
    np.testing.assert_allclose(out, np.asarray([1.0, 1.0, 8.0], dtype=float))


@pytest.mark.parametrize(
    "basis,t_s,dt_s,expected_dim",
    [
        (IdentityTemporalBasis(dimension=2, scale=2.0), 1.0, 0.25, 2),
        (BinnedTemporalBasis(dimension=4, max_time_s=2.0), 0.75, None, 4),
        (TraceTemporalBasis(dimension=3, decay=1.0), 1.0, None, 3),
    ],
)
def test_temporal_basis_outputs_fixed_dimension_and_is_deterministic(basis, t_s, dt_s, expected_dim):
    first = basis.encode(t_s=t_s, dt_s=dt_s)
    second = basis.encode(t_s=t_s, dt_s=dt_s)

    assert first.shape == (expected_dim,)
    np.testing.assert_allclose(first, second)


def test_binned_temporal_basis_is_one_hot():
    basis = BinnedTemporalBasis(dimension=5, max_time_s=2.0)
    encoded = basis.encode(t_s=0.8)

    assert encoded.sum() == pytest.approx(1.0)
    assert np.count_nonzero(encoded) == 1


def test_trace_temporal_basis_is_monotone_decreasing():
    basis = TraceTemporalBasis(dimension=4, decay=1.0)
    encoded = basis.encode(t_s=1.0)

    assert np.all(encoded[:-1] > encoded[1:])


def test_prediction_error_rule_formula_parity():
    state = np.asarray([1.0, 0.0], dtype=float)
    next_state = np.asarray([1.0, 0.0], dtype=float)
    parameters = np.asarray([0.2, 0.0], dtype=float)

    rw = RescorlaWagnerPredictionError()
    td0 = TD0PredictionError(gamma=0.5)

    assert rw.compute(state=state, reward=1.0, parameters=parameters) == pytest.approx(0.8)
    assert td0.compute(
        state=state,
        reward=1.0,
        next_state=next_state,
        parameters=parameters,
    ) == pytest.approx(0.9)


@pytest.mark.parametrize(
    "name,params",
    [
        ("none", {}),
        ("static", {"default": 0.4, "overrides": {"tone": 0.8}}),
        ("pearce_hall", {"default": 0.4, "eta": 0.5}),
        ("mackintosh", {"default": 0.4, "kappa": 0.5}),
    ],
)
def test_attention_mechanisms_return_bounded_alpha_maps(name, params):
    mechanism = build_attention_mechanism(name, params=params)

    alpha_map = mechanism.current_alpha(["tone", "noise"])

    assert set(alpha_map.keys()) == {"tone", "noise"}
    assert all(0.0 <= float(value) <= 1.0 for value in alpha_map.values())


def test_dynamic_attention_mechanism_updates_state_deterministically():
    mechanism = build_attention_mechanism("pearce_hall", params={"default": 0.4, "eta": 0.5})
    context = AttentionContext(
        active_features=("tone", "noise"),
        feature_contributions={"tone": 0.2, "noise": 0.1},
        total_prediction=0.3,
        reward=1.0,
        prediction_error=0.7,
    )

    state = mechanism.update_state(context)
    alpha_map = mechanism.current_alpha(["tone", "noise"])

    assert state is not None
    assert set(alpha_map.keys()) == {"tone", "noise"}
    assert all(0.0 <= float(value) <= 1.0 for value in alpha_map.values())
