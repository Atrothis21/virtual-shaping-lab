# analysis/report/config.py

from dataclasses import dataclass, field
from typing import Any, Dict, List

from analysis.metrics.registry import METRIC_REGISTRY
from analysis.visualizations.registry import VISUALIZATION_REGISTRY


# -------------------------------------------------
# Resolved report item
# -------------------------------------------------

@dataclass
class ReportItem:
    """
    A fully resolved report unit:
    one metric + one visualization.
    """
    metric: Any
    visualization: Any
    params: Dict[str, Any] = field(default_factory=dict)


# -------------------------------------------------
# Declarative report configuration
# -------------------------------------------------

@dataclass
class ReportConfig:
    """
    Declarative report configuration.

    Metrics and visualizations are specified by string keys
    and resolved via registries. This class is responsible
    for adapting semantic parameters into concrete runtime
    objects.
    """

    metrics: List[str]
    visualizations: List[str]
    params: Dict[str, Any] = field(default_factory=dict)

    # ---------------------------------------------
    # Metric construction (explicit, no guessing)
    # ---------------------------------------------

    def _build_metric(self, metric_name: str):
        if metric_name not in METRIC_REGISTRY:
            raise KeyError(f"Unknown metric '{metric_name}'")

        metric_cls = METRIC_REGISTRY[metric_name]

        # ---- parameterized metrics ----
        if metric_name == "discrimination_index":
            return metric_cls(
                positive_key=self.params["cs_plus"][0],
                negative_key=self.params["cs_minus"][0],
            )

        # ---- parameterless metrics ----
        return metric_cls()

    # ---------------------------------------------
    # Visualization construction (robust)
    # ---------------------------------------------

    def _build_visualization(self, viz_name: str):
        if viz_name not in VISUALIZATION_REGISTRY:
            raise KeyError(f"Unknown visualization '{viz_name}'")

        viz_cls = VISUALIZATION_REGISTRY[viz_name]

        # visualizations may or may not accept params
        try:
            return viz_cls(**self.params)
        except TypeError:
            return viz_cls()

    # ---------------------------------------------
    # Public resolution API
    # ---------------------------------------------

    @property
    def items(self) -> List[ReportItem]:
        if len(self.metrics) != len(self.visualizations):
            raise ValueError(
                "ReportConfig.metrics and ReportConfig.visualizations "
                "must be the same length"
            )

        items: List[ReportItem] = []

        for metric_name, viz_name in zip(self.metrics, self.visualizations):
            metric = self._build_metric(metric_name)
            visualization = self._build_visualization(viz_name)

            items.append(
                ReportItem(
                    metric=metric,
                    visualization=visualization,
                    params=self.params,
                )
            )

        return items
