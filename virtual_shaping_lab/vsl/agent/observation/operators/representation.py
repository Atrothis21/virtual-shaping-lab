"""Executable representation operators (`Phi`) for observation core."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Mapping, Sequence

from .base import RepresentationOperator


def _to_float(value: Any, *, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric.") from exc


@dataclass(frozen=True)
class RepresentationArtifact:
    """Typed representation artifact normalized for downstream operators."""

    representation_state: Any
    features: list[float] = field(default_factory=list)
    feature_names: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.features, list):
            raise ValueError("RepresentationArtifact.features must be a list.")
        if not all(isinstance(value, (int, float)) for value in self.features):
            raise ValueError("RepresentationArtifact.features must contain numeric values.")
        if not isinstance(self.feature_names, list):
            raise ValueError("RepresentationArtifact.feature_names must be a list.")
        if not all(isinstance(value, str) for value in self.feature_names):
            raise ValueError("RepresentationArtifact.feature_names must contain strings.")
        if len(self.feature_names) not in {0, len(self.features)}:
            raise ValueError("RepresentationArtifact.feature_names must be empty or match features length.")
        if not isinstance(self.metadata, dict):
            raise ValueError("RepresentationArtifact.metadata must be an object.")
        object.__setattr__(self, "features", [float(value) for value in self.features])
        object.__setattr__(self, "feature_names", [str(value) for value in self.feature_names])
        object.__setattr__(self, "metadata", dict(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "representation_state": self.representation_state,
            "features": list(self.features),
            "feature_names": list(self.feature_names),
            "metadata": dict(self.metadata),
        }


def _coerce_stimulus_map(raw_stimulus: Any) -> dict[str, float]:
    if raw_stimulus is None:
        return {}
    if isinstance(raw_stimulus, str):
        return {raw_stimulus: 1.0}
    if isinstance(raw_stimulus, Sequence) and not isinstance(raw_stimulus, (str, bytes, bytearray)):
        out: dict[str, float] = {}
        for item in raw_stimulus:
            key = str(item)
            out[key] = 1.0
        return out
    if isinstance(raw_stimulus, Mapping):
        out: dict[str, float] = {}
        for key, value in raw_stimulus.items():
            if isinstance(value, (int, float)):
                out[str(key)] = float(value)
        return out
    raise ValueError("raw_stimulus must be string, sequence, mapping, or None.")


@dataclass(frozen=True)
class IdentityRepresentationOperator(RepresentationOperator):
    """Identity representation: numeric mapping passthrough with sorted feature order."""

    variant: str = "identity"

    def represent(
        self,
        *,
        raw_stimulus: Any,
        metadata: Mapping[str, Any] | None = None,
    ) -> RepresentationArtifact:
        stim_map = _coerce_stimulus_map(raw_stimulus)
        names = sorted(stim_map.keys())
        features = [stim_map[name] for name in names]
        return RepresentationArtifact(
            representation_state=dict(stim_map),
            features=features,
            feature_names=names,
            metadata={"variant": self.variant, **dict(metadata or {})},
        )


@dataclass(frozen=True)
class ElementalRepresentationOperator(RepresentationOperator):
    """Elemental representation over fixed cue universe."""

    stimulus_universe: Sequence[str]
    variant: str = "elemental"

    def __post_init__(self) -> None:
        if not isinstance(self.stimulus_universe, Sequence) or not list(self.stimulus_universe):
            raise ValueError("ElementalRepresentationOperator.stimulus_universe must be a non-empty sequence.")

    def represent(
        self,
        *,
        raw_stimulus: Any,
        metadata: Mapping[str, Any] | None = None,
    ) -> RepresentationArtifact:
        stim_map = _coerce_stimulus_map(raw_stimulus)
        names = [str(cue) for cue in self.stimulus_universe]
        features = [float(stim_map.get(name, 0.0)) for name in names]
        return RepresentationArtifact(
            representation_state=dict(stim_map),
            features=features,
            feature_names=names,
            metadata={"variant": self.variant, **dict(metadata or {})},
        )


@dataclass(frozen=True)
class MinimalConfiguralRepresentationOperator(RepresentationOperator):
    """Elemental + pairwise conjunction features for active cues."""

    stimulus_universe: Sequence[str]
    conjunction_prefix: str = "cfg:"
    variant: str = "minimal_configural"

    def __post_init__(self) -> None:
        if not isinstance(self.stimulus_universe, Sequence) or not list(self.stimulus_universe):
            raise ValueError("MinimalConfiguralRepresentationOperator.stimulus_universe must be a non-empty sequence.")
        if not isinstance(self.conjunction_prefix, str):
            raise ValueError("MinimalConfiguralRepresentationOperator.conjunction_prefix must be a string.")

    def represent(
        self,
        *,
        raw_stimulus: Any,
        metadata: Mapping[str, Any] | None = None,
    ) -> RepresentationArtifact:
        stim_map = _coerce_stimulus_map(raw_stimulus)
        cues = [str(cue) for cue in self.stimulus_universe]

        names: list[str] = list(cues)
        values: list[float] = [float(stim_map.get(cue, 0.0)) for cue in cues]

        active = [cue for cue in cues if float(stim_map.get(cue, 0.0)) > 0.0]
        for left, right in combinations(active, 2):
            cfg_name = f"{self.conjunction_prefix}{left}&{right}"
            cfg_value = min(
                _to_float(stim_map.get(left, 0.0), field_name=left),
                _to_float(stim_map.get(right, 0.0), field_name=right),
            )
            names.append(cfg_name)
            values.append(cfg_value)

        return RepresentationArtifact(
            representation_state=dict(stim_map),
            features=values,
            feature_names=names,
            metadata={"variant": self.variant, **dict(metadata or {})},
        )

