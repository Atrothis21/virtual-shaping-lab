# representations/vocab.py

from itertools import combinations
from typing import Iterable, List, Optional, Dict, Tuple


def build_feature_vocab(
    stimuli: Iterable[str],
    include_compounds: bool = False,
    compound_prefix: str = "compound:",
    max_compound_size: int = 2,
    contexts: Optional[Iterable[str]] = None,
    context_prefix: str = "ctx:",
    global_prefix: str = "global:",
    include_global: bool = True,
    include_context: bool = True,
    salience: Optional[Dict[str, float]] = None,
    compound_salience: str = "max",
) -> Tuple[List[str], List[float]]:
    """
    Build a feature vocabulary and aligned salience vector.

    Two-channel encoding:
      - global:<stimulus>
      - ctx:<context>|<stimulus>

    Compound features are built similarly:
      - global:compound:<stim1>|<stim2>
      - ctx:<context>|compound:<stim1>|<stim2>

    If contexts is None or empty, a single default context ("A") is used.
    """

    stim_list = list(stimuli)
    vocab: List[str] = []
    salience_vector: List[float] = []

    salience = salience or {}
    ctx_list = list(contexts) if contexts else ["A"]

    if not include_global and not include_context:
        raise ValueError("build_feature_vocab requires at least one channel enabled.")

    def base_salience(key: str) -> float:
        return float(salience.get(key, 1.0))

    def combine_salience(values: List[float]) -> float:
        if not values:
            return 1.0
        if compound_salience == "max":
            return max(values)
        if compound_salience == "min":
            return min(values)
        if compound_salience == "product":
            out = 1.0
            for v in values:
                out *= v
            return out
        # default mean
        return sum(values) / len(values)

    def ctx_key(ctx: str, feature: str) -> str:
        return f"{context_prefix}{ctx}|{feature}"

    def global_key(feature: str) -> str:
        return f"{global_prefix}{feature}"

    # Base stimuli
    for stim in stim_list:
        if include_global:
            vocab.append(global_key(stim))
            salience_vector.append(base_salience(stim))
        if include_context:
            for ctx in ctx_list:
                vocab.append(ctx_key(ctx, stim))
                salience_vector.append(base_salience(stim))

    if include_compounds:
        # Include size-1 compounds so configural encoders can represent single stimuli
        start = 1 if max_compound_size >= 1 else 2
        for r in range(start, max_compound_size + 1):
            for combo in combinations(sorted(stim_list), r):
                comp_key = compound_prefix + "|".join(combo)
                vals = [base_salience(s) for s in combo]
                comp_sal = combine_salience(vals)

                if include_global:
                    vocab.append(global_key(comp_key))
                    salience_vector.append(comp_sal)

                if include_context:
                    for ctx in ctx_list:
                        vocab.append(ctx_key(ctx, comp_key))
                        salience_vector.append(comp_sal)

    return vocab, salience_vector


def build_feature_weight_vector(
    features: Iterable[str],
    weights: Optional[Dict[str, float]] = None,
    compound_rule: str = "mean",
    context_prefix: str = "ctx:",
    global_prefix: str = "global:",
    compound_prefix: str = "compound:",
) -> List[float]:
    """
    Build a feature-aligned weight vector (e.g., attention) from a stimulus map.
    """
    weights = weights or {}

    def base_weight(key: str) -> float:
        return float(weights.get(key, 1.0))

    def combine(vals: List[float]) -> float:
        if not vals:
            return 1.0
        if compound_rule == "max":
            return max(vals)
        if compound_rule == "min":
            return min(vals)
        if compound_rule == "product":
            out = 1.0
            for v in vals:
                out *= v
            return out
        return sum(vals) / len(vals)

    out: List[float] = []
    for feature in features:
        raw = feature
        if raw.startswith(context_prefix):
            raw = raw[len(context_prefix):]
            if "|" in raw:
                raw = raw.split("|", 1)[1]
        elif raw.startswith(global_prefix):
            raw = raw[len(global_prefix):]

        if raw.startswith(compound_prefix):
            comp = raw[len(compound_prefix):]
            parts = comp.split("|") if comp else []
            vals = [base_weight(p) for p in parts]
            out.append(combine(vals))
        else:
            out.append(base_weight(raw))

    return out
