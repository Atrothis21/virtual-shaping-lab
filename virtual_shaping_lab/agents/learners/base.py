# learners/base.py

"""Base learner definitions for transition-based updates.

Attention contract reference:
- docs/core_engine_architecture.md (Agent Cognition Layer)
- canonical attended input form: x'_t = A_t odot x_t
- invariant target: shape(A_t) == shape(x_t)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Mapping

import numpy as np

from virtual_shaping_lab.agents.interfaces import ILearner
from virtual_shaping_lab.agents.learners.attention_strategies import (
    AttentionContext,
    AttentionStrategy,
    build_attention_strategy,
)
from virtual_shaping_lab.domain.types import EncodedState, META_CUE_LABELS, Transition


class BaseLearner(ILearner, ABC):
    """Abstract base class for all learning algorithms."""

    learner_type: str = "pavlovian"  # "pavlovian" | "operant" | "both"

    def __init__(self, alpha: float, gamma: float):
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.attention_map: Dict[str, float] = {}
        self._attention_strategy: AttentionStrategy = build_attention_strategy("none")
        self._last_attention_context: AttentionContext | None = None

    def reset(self) -> None:
        self._attention_strategy.reset()
        return None

    def set_attention_map(self, attention: Optional[Dict[str, float]]) -> None:
        self.attention_map = dict(attention or {})
        self.set_attention_config(
            name="static" if self.attention_map else "none",
            params={
                "default": 1.0,
                "overrides": dict(self.attention_map),
            },
        )

    def set_attention_config(self, *, name: str, params: Optional[Mapping[str, Any]] = None) -> None:
        self._attention_strategy = build_attention_strategy(name=name, params=params)

    def attention_multiplier(self, cue_labels: Any) -> float:
        return float(self._attention_strategy.current_alpha_for_cues(cue_labels))

    def update_attention_state(self, context: AttentionContext) -> None:
        self._last_attention_context = context
        self._attention_strategy.update_state(context)

    def attention_diagnostics(self, cue_labels: Any = None) -> dict[str, Any]:
        active_features = self._coerce_active_features(
            cue_labels,
            self._last_attention_context.feature_contributions
            if self._last_attention_context is not None
            else {},
        )
        alpha_by_stimulus = (
            self._attention_strategy.current_alpha(active_features)
            if active_features
            else {}
        )
        alpha_vals = [float(v) for v in alpha_by_stimulus.values()]
        mean_alpha = (sum(alpha_vals) / len(alpha_vals)) if alpha_vals else 1.0
        out: dict[str, Any] = {
            "alpha_by_stimulus": alpha_by_stimulus,
            "mean_alpha": float(mean_alpha),
        }
        if self._last_attention_context is not None:
            out["prediction_error"] = float(self._last_attention_context.prediction_error)
            out["cuewise_contributions"] = {
                str(k): float(v)
                for k, v in self._last_attention_context.feature_contributions.items()
            }
        return out

    @staticmethod
    def _coerce_active_features(cue_labels: Any, feature_contributions: Mapping[str, float]) -> tuple[str, ...]:
        if cue_labels is not None:
            if isinstance(cue_labels, (str, int, float)):
                return (str(cue_labels),)
            labels = tuple(str(c) for c in cue_labels)
            if labels:
                return labels
        if isinstance(feature_contributions, Mapping) and feature_contributions:
            return tuple(str(k) for k in feature_contributions.keys())
        return ()

    @staticmethod
    def _feature_labels_for_state(cue_labels: Any, state_dim: int) -> tuple[str, ...]:
        if cue_labels is None:
            return tuple(f"f{i}" for i in range(state_dim))
        if isinstance(cue_labels, (str, int, float)):
            labels = (str(cue_labels),)
        else:
            labels = tuple(str(c) for c in cue_labels)
        if len(labels) == state_dim:
            return labels
        return tuple(f"f{i}" for i in range(state_dim))

    def feature_contributions_for_transition(
        self,
        transition: Transition,
        weights: np.ndarray,
    ) -> dict[str, float]:
        x = np.asarray(transition.s.x, dtype=float)
        w = np.asarray(weights, dtype=float)
        if w.shape != x.shape:
            raise ValueError(
                f"feature contribution shape mismatch: weights_shape={w.shape}, state_shape={x.shape}"
            )
        labels = self._feature_labels_for_state(
            transition.metadata.get(META_CUE_LABELS),
            state_dim=int(x.shape[0]),
        )
        return {labels[i]: float(w[i] * x[i]) for i in range(int(x.shape[0]))}

    def attention_modulated_state(
        self,
        transition: Transition,
        *,
        total_prediction: float,
        prediction_error: float,
        feature_contributions: Mapping[str, float],
    ) -> np.ndarray:
        """
        Canonical learner attention path contract:
        - modulate input using current attention state before parameter update
        - update attention state after computing current-trial sufficient statistics
        - canonical math target is x'_t = A_t odot x_t
        """
        x = np.asarray(transition.s.x, dtype=float)
        cue_labels = transition.metadata.get(META_CUE_LABELS)
        active_features = self._coerce_active_features(cue_labels, feature_contributions)
        alpha_vec, context_features = self._resolve_attention_vector(
            x=x,
            cue_labels=cue_labels,
            feature_contributions=feature_contributions,
        )
        x_mod = x * alpha_vec
        self.update_attention_state(
            AttentionContext(
                active_features=context_features if context_features else active_features,
                feature_contributions={str(k): float(v) for k, v in feature_contributions.items()},
                total_prediction=float(total_prediction),
                reward=float(transition.r),
                prediction_error=float(prediction_error),
            )
        )
        return x_mod

    def _resolve_attention_vector(
        self,
        *,
        x: np.ndarray,
        cue_labels: Any,
        feature_contributions: Mapping[str, float],
    ) -> tuple[np.ndarray, tuple[str, ...]]:
        x = np.asarray(x, dtype=float)
        n = int(x.shape[0])
        cue_features = self._coerce_active_features(cue_labels, {})
        contrib_features = self._coerce_active_features(None, feature_contributions)

        # Canonical cuewise path when cue labels are aligned to state basis.
        if cue_features and len(cue_features) == n:
            alpha_map = self._attention_strategy.current_alpha(cue_features)
            alpha_vec = np.asarray([float(alpha_map.get(f, 1.0)) for f in cue_features], dtype=float)
            return alpha_vec, cue_features

        # Compatibility vector path: contribution basis aligned to x; expand cue alpha uniformly.
        if contrib_features and len(contrib_features) == n and cue_features:
            cue_alpha = float(self.attention_multiplier(cue_labels))
            alpha_vec = np.full(n, cue_alpha, dtype=float)
            return alpha_vec, cue_features

        # Contribution-key cuewise path when labels are absent but contribution basis is aligned.
        if contrib_features and len(contrib_features) == n:
            alpha_map = self._attention_strategy.current_alpha(contrib_features)
            alpha_vec = np.asarray([float(alpha_map.get(f, 1.0)) for f in contrib_features], dtype=float)
            return alpha_vec, contrib_features

        # No attention features available; neutral identity modulation.
        if not cue_features and not contrib_features:
            return np.ones(n, dtype=float), ()

        actual = len(cue_features) if cue_features else len(contrib_features)
        raise ValueError(
            f"attention vector shape mismatch: expected={n}, actual={actual}"
        )

    @abstractmethod
    def update(self, transition: Transition) -> None:
        raise NotImplementedError

    def effective_alpha(self, transition: Transition) -> float:
        cue_labels = transition.metadata.get(META_CUE_LABELS)
        return float(self.alpha) * float(self.attention_multiplier(cue_labels))

    @abstractmethod
    def value(self, state: EncodedState, action: Any = None) -> float:
        raise NotImplementedError

    def expects_action(self) -> bool:
        return False

    def start_episode(self) -> None:
        return None

    def end_episode(self) -> None:
        return None

    def get_parameters(self) -> Dict[str, np.ndarray]:
        return {}

