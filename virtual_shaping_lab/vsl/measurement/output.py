"""Typed outputs for executable measurement operators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AnalysisOutput:
    """Typed output from analysis operator stage."""

    metrics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.metrics, dict):
            raise ValueError("AnalysisOutput.metrics must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("AnalysisOutput.metadata must be an object.")
        object.__setattr__(self, "metrics", dict(self.metrics))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class VisualizationOutput:
    """Typed output from visualization operator stage."""

    figures: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.figures, list):
            raise ValueError("VisualizationOutput.figures must be an array.")
        if not isinstance(self.metadata, dict):
            raise ValueError("VisualizationOutput.metadata must be an object.")
        normalized: list[dict[str, Any]] = []
        for figure in self.figures:
            if not isinstance(figure, dict):
                raise ValueError("VisualizationOutput.figures entries must be objects.")
            normalized.append(dict(figure))
        object.__setattr__(self, "figures", normalized)
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True)
class MeasurementStepResult:
    """Canonical finalize output for measurement execution bundle."""

    analysis: AnalysisOutput
    visualization: VisualizationOutput
    report: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.analysis, AnalysisOutput):
            raise ValueError("MeasurementStepResult.analysis must be AnalysisOutput.")
        if not isinstance(self.visualization, VisualizationOutput):
            raise ValueError("MeasurementStepResult.visualization must be VisualizationOutput.")
        if not isinstance(self.report, dict):
            raise ValueError("MeasurementStepResult.report must be an object.")
        if not isinstance(self.metadata, dict):
            raise ValueError("MeasurementStepResult.metadata must be an object.")
        object.__setattr__(self, "report", dict(self.report))
        object.__setattr__(self, "metadata", dict(self.metadata))
