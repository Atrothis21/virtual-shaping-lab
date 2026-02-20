from abc import ABC, abstractmethod
from typing import Any, Optional


class Visualization(ABC):
    """
    Base class for all visualizations.

    A Visualization:
    - Consumes trial records first
    - May optionally consume metrics
    """

    name: str = "visualization"

    @abstractmethod
    def render(self, records: Any, metrics: Optional[dict] = None, **kwargs) -> None:
        """
        Render the visualization.

        Parameters
        ----------
        records : Any
            Trial records (list of dicts)
        metrics : dict | None
            Optional metric output
        kwargs : dict
            Visualization-specific options
        """
        pass
