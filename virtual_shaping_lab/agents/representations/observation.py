# representations/observation.py

from typing import Any, Dict, List, TypedDict


DEFAULT_CONTEXT = "A"


class Observation(TypedDict):
    """
    Canonical observation format emitted by phases.

    Vector-first contract:
      - stimuli are feature keys used by vector encoders
      - context is always present (used for context-gated features)
      - compound indicates whether stimuli should be treated as a single
        configural unit by configural encoders
      - metadata holds optional auxiliary info (e.g., timing, modality)

    This structure supports two-component representations:
      - global features (context-independent)
      - context-gated features (context-dependent)
    """
    stimuli: List[Any]
    context: Any
    compound: bool
    metadata: Dict[str, Any]


def make_observation(
    stimuli: List[Any],
    context: Any,
    compound: bool = False,
    metadata: Dict[str, Any] | None = None,
) -> Observation:
    """
    Build a canonical observation with required context.

    Parameters
    ----------
    stimuli :
        List of feature keys. These are the atomic units for vector encoding.
    context :
        Required context key (e.g., "A", "B"). If None, DEFAULT_CONTEXT is used.
    compound :
        If True, configural encoders may treat the entire stimulus list as
        a single compound unit.
    metadata :
        Optional extra info.

    Returns
    -------
    Observation
    """
    if stimuli is None:
        raise ValueError("make_observation requires a non-empty stimuli list")

    if context is None:
        context = DEFAULT_CONTEXT

    obs: Observation = {
        "stimuli": list(stimuli),
        "context": context,
        "compound": compound,
        "metadata": metadata or {},
    }
    return obs
