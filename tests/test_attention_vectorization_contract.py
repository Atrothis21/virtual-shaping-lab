import numpy as np
import pytest
import warnings

from agents.learners.base import BaseLearner
from domain.types import EncodedState, Transition


class _DummyLearner(BaseLearner):
    def update(self, transition: Transition) -> None:
        return None

    def value(self, state: EncodedState, action=None) -> float:
        return float(np.sum(state.x))


def _transition(x, cue_labels):
    return Transition(
        s=EncodedState(x=np.asarray(x, dtype=float)),
        r=1.0,
        metadata={"cue_labels": list(cue_labels)},
    )


def test_attention_modulation_is_cuewise_not_scalar():
    learner = _DummyLearner(alpha=0.1, gamma=0.0)
    learner.set_attention_config(
        name="static",
        params={
            "default": 1.0,
            "overrides": {"f0": 0.5, "f1": 1.0, "f2": 0.25},
        },
    )
    transition = _transition([2.0, 2.0, 2.0], cue_labels=["f0", "f1", "f2"])
    x_mod = learner.attention_modulated_state(
        transition,
        total_prediction=0.0,
        prediction_error=1.0,
        feature_contributions={"f0": 0.0, "f1": 0.0, "f2": 0.0},
    )
    expected = np.asarray([1.0, 2.0, 0.5], dtype=float)
    np.testing.assert_allclose(x_mod, expected, atol=1e-12)


def test_attention_shape_mismatch_fails_fast_with_clear_error():
    learner = _DummyLearner(alpha=0.1, gamma=0.0)
    learner.set_attention_config(
        name="static",
        params={"default": 1.0, "overrides": {"f0": 0.5, "f1": 1.0}},
    )
    transition = _transition([1.0, 2.0, 3.0], cue_labels=["f0", "f1"])
    with pytest.raises(ValueError, match="attention vector shape mismatch"):
        learner.attention_modulated_state(
            transition,
            total_prediction=0.0,
            prediction_error=1.0,
            feature_contributions={"f0": 0.0, "f1": 0.0},
        )


def test_attention_shape_mismatch_error_includes_expected_and_actual_lengths():
    learner = _DummyLearner(alpha=0.1, gamma=0.0)
    learner.set_attention_config(
        name="static",
        params={"default": 1.0, "overrides": {"f0": 0.8}},
    )
    transition = _transition([1.0, 2.0], cue_labels=["f0"])
    with pytest.raises(
        ValueError,
        match=r"attention vector shape mismatch.*expected=2.*actual=1",
    ):
        learner.attention_modulated_state(
            transition,
            total_prediction=0.0,
            prediction_error=1.0,
            feature_contributions={"f0": 0.0},
        )


def test_scalar_attention_compatibility_shim_expands_to_uniform_vector_with_warning():
    learner = _DummyLearner(alpha=0.1, gamma=0.0)
    learner.set_attention_map({"tone": 0.5})
    transition = _transition([2.0, 4.0], cue_labels=["tone"])
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        x_mod = learner.attention_modulated_state(
            transition,
            total_prediction=0.0,
            prediction_error=1.0,
            feature_contributions={"f0": 0.0, "f1": 0.0},
        )
    np.testing.assert_allclose(x_mod, np.asarray([1.0, 2.0], dtype=float), atol=1e-12)
    scalar_shim = [
        w for w in captured
        if issubclass(w.category, DeprecationWarning)
        and "attention scalar compatibility shim applied" in str(w.message)
    ]
    assert len(scalar_shim) == 1


def test_scalar_attention_shim_warning_is_emitted_once_per_learner_instance():
    learner = _DummyLearner(alpha=0.1, gamma=0.0)
    learner.set_attention_map({"tone": 0.5})
    t = _transition([1.0, 1.0], cue_labels=["tone"])
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        learner.attention_modulated_state(
            t,
            total_prediction=0.0,
            prediction_error=1.0,
            feature_contributions={"f0": 0.0, "f1": 0.0},
        )
        learner.attention_modulated_state(
            t,
            total_prediction=0.0,
            prediction_error=1.0,
            feature_contributions={"f0": 0.0, "f1": 0.0},
        )
    scalar_shim = [
        w for w in captured
        if issubclass(w.category, DeprecationWarning)
        and "attention scalar compatibility shim applied" in str(w.message)
    ]
    assert len(scalar_shim) == 1
