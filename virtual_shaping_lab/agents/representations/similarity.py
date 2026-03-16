# representations/similarity.py

from typing import Dict, Iterable, List, Any

from virtual_shaping_lab.agents.math_objects.representation_objects import MatrixSimilarityKernel


def parse_similarity_matrix(similarity: Dict[str, Any] | None, stimuli: Iterable[str]) -> Dict[str, Dict[str, float]]:
    """
    Parse an explicit similarity matrix into a lookup map.

    Expected format:
      {
        "type": "matrix",
        "stimuli": ["tone", "noise", ...],  # optional
        "values": [[1.0, 0.3, ...], ...]
      }
    """
    if not similarity:
        return {}

    if similarity.get("type") != "matrix":
        raise ValueError("similarity.type must be 'matrix'")

    stim_list = similarity.get("stimuli") or list(stimuli)
    values = similarity.get("values")
    if not isinstance(values, list) or not values:
        raise ValueError("similarity.values must be a non-empty matrix")

    if len(values) != len(stim_list):
        raise ValueError("similarity.values row count must match stimuli length")

    out: Dict[str, Dict[str, float]] = {}
    for i, row in enumerate(values):
        if not isinstance(row, list) or len(row) != len(stim_list):
            raise ValueError("similarity.values must be a square matrix")
        row_map: Dict[str, float] = {}
        for j, val in enumerate(row):
            try:
                weight = float(val)
            except (TypeError, ValueError):
                raise ValueError("similarity.values entries must be numbers")
            if weight < 0 or weight > 1:
                raise ValueError("similarity.values must be between 0 and 1")
            row_map[stim_list[j]] = weight
        out[stim_list[i]] = row_map
    return out


def build_similarity_weights(
    present: Iterable[str],
    similarity_map: Dict[str, Dict[str, float]],
) -> Dict[str, float]:
    """
    Build per-stimulus weights using a similarity map.

    Each presented stimulus starts at weight 1.0.
    Similar stimuli inherit weights using max aggregation.
    """
    return MatrixSimilarityKernel(similarity_map).spread_weights(present)
