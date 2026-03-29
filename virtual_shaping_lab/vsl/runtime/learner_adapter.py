"""Canonical runtime seam for learner execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from virtual_shaping_lab.vsl.agent.learning.bundle import LearnerBundle, LearnerStepResult
from virtual_shaping_lab.vsl.agent.learning.executable_presets import (
    ExecutableLearnerPreset,
    build_executable_learner_preset,
)


def _coerce_features_from_stimulus(stimulus: Mapping[str, Any]) -> dict[str, float]:
    """
    Normalize environment stimulus payload to learner feature vector.

    Minimal deterministic mapping for runtime seam:
    - list[str] payloads produce one-hot feature presence for each item
    - scalar payloads use the key with float(value) when possible
    - unknown scalar payloads map to feature presence 1.0
    """
    out: dict[str, float] = {}
    for key, value in dict(stimulus).items():
        if isinstance(value, list):
            for item in value:
                out[str(item)] = 1.0
            continue
        try:
            out[str(key)] = float(value)
        except (TypeError, ValueError):
            out[str(key)] = 1.0
    return out


def _coerce_features_payload(
    *,
    features: Mapping[str, Any] | Sequence[float],
    feature_names: Sequence[str] | None = None,
) -> dict[str, float]:
    if isinstance(features, Mapping):
        return {str(key): float(value) for key, value in dict(features).items()}
    if isinstance(features, Sequence) and not isinstance(features, (str, bytes, bytearray)):
        if feature_names is None:
            raise ValueError("feature_names are required when observation features are provided as a sequence.")
        names = [str(name) for name in feature_names]
        values = [float(value) for value in features]
        if len(names) != len(values):
            raise ValueError("observation feature_names length must match features length.")
        return dict(zip(names, values))
    raise ValueError("features must be a mapping or sequence of numeric values.")


@dataclass
class RuntimeLearnerAdapter:
    """Runtime adapter that routes learner execution through one canonical bundle seam."""

    bundle: LearnerBundle

    def step(
        self,
        *,
        stimulus: Mapping[str, Any] | None = None,
        reward: float,
        done: bool,
        next_stimulus: Mapping[str, Any] | None = None,
        observation_features: Mapping[str, Any] | Sequence[float] | None = None,
        observation_feature_names: Sequence[str] | None = None,
        next_observation_features: Mapping[str, Any] | Sequence[float] | None = None,
        next_observation_feature_names: Sequence[str] | None = None,
    ) -> LearnerStepResult:
        if observation_features is not None:
            features = _coerce_features_payload(
                features=observation_features,
                feature_names=observation_feature_names,
            )
        elif stimulus is not None:
            features = _coerce_features_from_stimulus(stimulus)
        else:
            raise ValueError("RuntimeLearnerAdapter.step requires either stimulus or observation_features.")

        if next_observation_features is not None:
            next_features = _coerce_features_payload(
                features=next_observation_features,
                feature_names=next_observation_feature_names,
            )
        else:
            next_features = None if next_stimulus is None else _coerce_features_from_stimulus(next_stimulus)
        return self.bundle.step(
            features=features,
            reward=float(reward),
            next_features=next_features,
            done=bool(done),
        )


def build_runtime_learner_adapter(
    *,
    preset_name: str = "rescorla_wagner",
    step_size: float = 0.1,
    gamma: float = 0.0,
    trace_decay: float = 0.0,
    state: Mapping[str, Any] | None = None,
) -> RuntimeLearnerAdapter:
    executable: ExecutableLearnerPreset = build_executable_learner_preset(
        preset_name,
        step_size=step_size,
        gamma=gamma,
        trace_decay=trace_decay,
        state=state,
    )
    return RuntimeLearnerAdapter(bundle=executable.bundle)
