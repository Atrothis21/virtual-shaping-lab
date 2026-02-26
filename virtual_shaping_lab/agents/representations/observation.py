# representations/observation.py

from __future__ import annotations

from typing import Any, Dict, List

from virtual_shaping_lab.domain.types import Observation


DEFAULT_CONTEXT = "A"


def make_observation(
    stimuli: List[Any],
    context: Any,
    compound: bool = False,
    metadata: Dict[str, Any] | None = None,
    t_s: float | None = None,
    dt_s: float | None = None,
) -> Observation:
    """Build a canonical Observation dataclass with required context."""
    if stimuli is None:
        raise ValueError("make_observation requires a non-empty stimuli list")

    ctx = DEFAULT_CONTEXT if context is None else context
    return Observation(
        stimuli=list(stimuli),
        context=ctx,
        compound=bool(compound),
        t_s=t_s,
        dt_s=dt_s,
        metadata=metadata or {},
    )
