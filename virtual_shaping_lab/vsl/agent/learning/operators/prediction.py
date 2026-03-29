"""Prediction operators for executable learner core (V3.18.5 slice 2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, MutableMapping, Sequence

from .base import PredictionOperator


def _coerce_features(features: Mapping[str, float]) -> dict[str, float]:
    out: dict[str, float] = {}
    for key, value in features.items():
        out[str(key)] = float(value)
    return out


def _dot(features: Mapping[str, float], weights: Mapping[str, float]) -> float:
    total = 0.0
    for key, value in features.items():
        total += float(value) * float(weights.get(key, 0.0))
    return total


@dataclass(frozen=True)
class PredictionOutput:
    """Unified prediction output contract for all prediction operators."""

    state_value: float
    action_values: dict[Any, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "state_value", float(self.state_value))
        if not isinstance(self.action_values, dict):
            raise ValueError("PredictionOutput.action_values must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("PredictionOutput.metadata must be an object.")
        normalized_actions: dict[Any, float] = {}
        for action, value in self.action_values.items():
            normalized_actions[action] = float(value)
        object.__setattr__(self, "action_values", normalized_actions)

    @classmethod
    def from_state_value(
        cls,
        value: float,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> "PredictionOutput":
        return cls(state_value=float(value), action_values={}, metadata=dict(metadata or {}))

    @classmethod
    def from_action_values(
        cls,
        action_values: Mapping[Any, float],
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> "PredictionOutput":
        if not isinstance(action_values, Mapping) or not action_values:
            raise ValueError("PredictionOutput.from_action_values requires a non-empty mapping.")
        normalized = {action: float(value) for action, value in action_values.items()}
        return cls(
            state_value=max(normalized.values()),
            action_values=normalized,
            metadata=dict(metadata or {}),
        )


@dataclass
class LinearStateValuePredictionOperator(PredictionOperator):
    """Linear state-value predictor: V(s) = w^T x."""

    parameter_key: str = "weights"

    def __call__(
        self,
        *,
        features: Mapping[str, float],
        state: MutableMapping[str, Any] | None = None,
    ) -> PredictionOutput:
        x = _coerce_features(features)
        carrier = state if isinstance(state, MutableMapping) else {}
        raw_weights = carrier.get(self.parameter_key, {})
        weights = raw_weights if isinstance(raw_weights, Mapping) else {}
        prediction = _dot(x, {str(k): float(v) for k, v in weights.items()})
        return PredictionOutput.from_state_value(prediction)


@dataclass
class TabularStateValuePredictionOperator(PredictionOperator):
    """Tabular state-value predictor over hashed/explicit state IDs."""

    table_key: str = "value_table"
    state_id_key: str = "state_id"

    def _state_id(
        self,
        *,
        features: Mapping[str, float],
        state: MutableMapping[str, Any] | None,
    ) -> str:
        if isinstance(state, Mapping):
            raw = state.get(self.state_id_key)
            if isinstance(raw, str) and raw.strip():
                return raw.strip()
        normalized = _coerce_features(features)
        items = tuple(sorted(normalized.items(), key=lambda item: item[0]))
        return repr(items)

    def __call__(
        self,
        *,
        features: Mapping[str, float],
        state: MutableMapping[str, Any] | None = None,
    ) -> PredictionOutput:
        carrier = state if isinstance(state, MutableMapping) else {}
        raw_table = carrier.get(self.table_key, {})
        table = raw_table if isinstance(raw_table, Mapping) else {}
        sid = self._state_id(features=features, state=carrier)
        value = float(table.get(sid, 0.0))
        return PredictionOutput.from_state_value(value, metadata={"state_id": sid})


@dataclass
class LinearActionValuePredictionOperator(PredictionOperator):
    """Linear action-value predictor: Q(s, a) = w_a^T x."""

    actions: Sequence[Any]
    parameter_key: str = "weights_by_action"

    def __post_init__(self) -> None:
        if not isinstance(self.actions, Sequence) or not list(self.actions):
            raise ValueError("LinearActionValuePredictionOperator.actions must be a non-empty sequence.")

    def __call__(
        self,
        *,
        features: Mapping[str, float],
        state: MutableMapping[str, Any] | None = None,
    ) -> PredictionOutput:
        x = _coerce_features(features)
        carrier = state if isinstance(state, MutableMapping) else {}
        raw_weights = carrier.get(self.parameter_key, {})
        weights_by_action = raw_weights if isinstance(raw_weights, Mapping) else {}

        action_values: dict[Any, float] = {}
        for action in self.actions:
            raw = weights_by_action.get(action, {})
            action_weights = raw if isinstance(raw, Mapping) else {}
            action_values[action] = _dot(x, {str(k): float(v) for k, v in action_weights.items()})
        return PredictionOutput.from_action_values(action_values)

