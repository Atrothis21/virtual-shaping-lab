"""Boundary ownership guards for composed parameter objects."""

from __future__ import annotations

from typing import Any, Mapping


def _require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object.")
    return value


def _format_keys(keys: set[str]) -> str:
    return ", ".join(sorted(keys))


def validate_composed_parameter_ownership(composed_parameters: Mapping[str, Any]) -> None:
    """
    Fail-fast contract guard for subsystem ownership boundaries.

    This is intentionally strict at assembly/runtime boundaries so malformed
    plan settings cannot silently leak cross-concern fields.
    """
    composed = _require_mapping(composed_parameters, "composed_parameters")

    rep = composed.get("representation", {})
    if rep is not None:
        rep = _require_mapping(rep, "composed_parameters.representation")
        bad = {"attention", "attention_compound"} & set(rep.keys())
        if bad:
            raise ValueError(
                "Ownership contract violation: representation object must not contain learner-owned keys: "
                f"{_format_keys(bad)}."
            )

    learner = composed.get("learner", {})
    if learner is not None:
        learner = _require_mapping(learner, "composed_parameters.learner")
        bad = {"salience", "similarity", "context", "contexts"} & set(learner.keys())
        if bad:
            raise ValueError(
                "Ownership contract violation: learner object must not contain representation-owned keys: "
                f"{_format_keys(bad)}."
            )

    policy = composed.get("policy", {})
    if policy is not None:
        policy = _require_mapping(policy, "composed_parameters.policy")
        bad = {
            "alpha",
            "gamma",
            "attention",
            "salience",
            "similarity",
            "context",
            "contexts",
            "seed",
            "update_mode",
            "record_mode",
            "strict_records",
        } & set(policy.keys())
        if bad:
            raise ValueError(
                "Ownership contract violation: policy object contains non-policy keys: "
                f"{_format_keys(bad)}."
            )

    runtime = composed.get("runtime", {})
    if runtime is not None:
        runtime = _require_mapping(runtime, "composed_parameters.runtime")
        bad = {
            "alpha",
            "gamma",
            "attention",
            "salience",
            "similarity",
            "context",
            "contexts",
            "actions",
            "epsilon",
            "temperature",
        } & set(runtime.keys())
        if bad:
            raise ValueError(
                "Ownership contract violation: runtime object contains non-runtime keys: "
                f"{_format_keys(bad)}."
            )

    units = composed.get("units", [])
    if units is None:
        return
    if not isinstance(units, list):
        raise ValueError("composed_parameters.units must be an array.")
    for idx, unit in enumerate(units):
        if not isinstance(unit, Mapping):
            raise ValueError(f"composed_parameters.units[{idx}] must be an object.")
        top_bad = {"attention", "salience", "similarity"} & set(unit.keys())
        if top_bad:
            raise ValueError(
                "Ownership contract violation: unit object must not contain representation/learner-owned keys: "
                f"{_format_keys(top_bad)} (units[{idx}])."
            )
        contingency = unit.get("contingency", {})
        if contingency is None:
            contingency = {}
        if not isinstance(contingency, Mapping):
            raise ValueError(f"composed_parameters.units[{idx}].contingency must be an object.")
        c_bad = {"attention", "attention_compound", "salience", "similarity"} & set(contingency.keys())
        if c_bad:
            raise ValueError(
                "Ownership contract violation: unit contingency must not contain learner/representation-owned keys: "
                f"{_format_keys(c_bad)} (units[{idx}].contingency)."
            )
