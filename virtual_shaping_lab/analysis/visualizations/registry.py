# analysis/visualizations/registry.py

from typing import Dict, Type, Any
from analysis.visualizations.base import Visualization

# ---- Import concrete visualizations ----
from analysis.visualizations.time_series import (
    LinePlot,
)

from analysis.visualizations.stimulus import (
    StimulusBarPlot,
)

from analysis.visualizations.discrimination import (
    DiscriminationCurvePlot,
)

from analysis.visualizations.dual_time_series import (
    DualTimeSeriesPlot,
)

from analysis.visualizations.summation import (
    SummationPlot,
)

from analysis.visualizations.extinction import (
    ExtinctionCurvePlot,
)

from analysis.visualizations.dual_time_series import DualTimeSeriesPlot
from analysis.visualizations.retardation import RetardationCurvePlot
from analysis.visualizations.probe_bar import ProbeBarPlot
from analysis.visualizations.auto_time_series import AutoTimeSeriesPlot

from analysis.visualizations.operant import (
    CumulativeResponsePlot,
    CumulativeRewardPlot,
)
from analysis.visualizations.matching_law import (
    MatchingLawPlot,
)

# ---- Registry ----

VISUALIZATION_REGISTRY: Dict[str, Type[Visualization]] = {
    LinePlot.name: LinePlot,
    StimulusBarPlot.name: StimulusBarPlot,
    DiscriminationCurvePlot.name: DiscriminationCurvePlot,
    SummationPlot.name: SummationPlot,
    ExtinctionCurvePlot.name: ExtinctionCurvePlot,
    DualTimeSeriesPlot.name: DualTimeSeriesPlot,
    DualTimeSeriesPlot.name: DualTimeSeriesPlot,
    RetardationCurvePlot.name: RetardationCurvePlot,
    ProbeBarPlot.name: ProbeBarPlot,
    AutoTimeSeriesPlot.name: AutoTimeSeriesPlot,

    # ---- operant conditioning ----
    CumulativeResponsePlot.name: CumulativeResponsePlot,
    CumulativeRewardPlot.name: CumulativeRewardPlot,
    MatchingLawPlot.name: MatchingLawPlot,
}


def list_visualizations() -> Dict[str, Type[Visualization]]:
    """Return all registered visualizations."""
    return dict(VISUALIZATION_REGISTRY)


def build_visualization(name: str, **params) -> Visualization:
    """Construct a visualization by name."""
    if name not in VISUALIZATION_REGISTRY:
        raise ValueError(f"Unknown visualization: {name}")

    return VISUALIZATION_REGISTRY[name](**params)


def render_visualization(
    name: str,
    data: Any,
    **params
) -> None:
    """
    Convenience function: build and render in one call.
    """
    viz = build_visualization(name)
    viz.render(data, **params)
