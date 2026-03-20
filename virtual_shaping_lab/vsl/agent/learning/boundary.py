"""Learner-grammar boundary resolution for spec-build and runtime assembly."""

from __future__ import annotations

from typing import Any, Mapping

from .presets import expand_learner_preset
from .spec import LearnerSpec
from .validator import LearnerSpecValidationError

_POLICY_ALIASES = {
    "null": "none",
    "fixed": "greedy",
}

_ATTENTION_ALIASES = {
    "none": "fixed",
    "static": "fixed",
}


def _normalize_policy_name(policy_config: Any) -> str:
    if policy_config is None:
        return "none"
    if isinstance(policy_config, str):
        name = policy_config.strip().lower()
    elif isinstance(policy_config, Mapping):
        name = str(policy_config.get("name", "none")).strip().lower()
    else:
        name = "none"
    return _POLICY_ALIASES.get(name, name)


def _normalize_attention_name(learning_config: Mapping[str, Any] | None) -> str:
    if not isinstance(learning_config, Mapping):
        return "fixed"
    attention = learning_config.get("attention", {})
    if not isinstance(attention, Mapping):
        return "fixed"
    config = attention.get("config", {})
    if not isinstance(config, Mapping):
        return "fixed"
    raw_name = str(config.get("name", "none")).strip().lower()
    return _ATTENTION_ALIASES.get(raw_name, raw_name)


def _derive_legacy_learner_spec(
    *,
    learner_rule: str,
    policy_name: str,
    attention_name: str,
    metadata: Mapping[str, Any] | None,
) -> LearnerSpec:
    updater = "attention_delta_rule" if attention_name in {"pearce_hall", "mackintosh", "hybrid_attention"} else "delta_rule"
    rule = learner_rule.strip().lower()
    payload = {
        "trace": "none",
        "attention": attention_name,
        "updater": updater,
        "metadata": dict(metadata or {}),
    }
    payload["metadata"].setdefault("source", "legacy_rule_map")
    payload["metadata"].setdefault("legacy_rule", rule)

    if rule in {"rescorla_wagner", "rw"}:
        payload.update({"predictor": "state_value", "error": "rw_error", "policy": "none"})
        return LearnerSpec.from_dict(payload)
    if rule in {"td_value", "td0", "td_0"}:
        payload.update({"predictor": "state_value", "error": "td_error", "policy": "none"})
        return LearnerSpec.from_dict(payload)
    if rule in {"q_learner", "q_learning"}:
        payload.update({"predictor": "q_value", "error": "q_error", "policy": policy_name})
        return LearnerSpec.from_dict(payload)

    raise LearnerSpecValidationError(
        code="LGR_E_UNMAPPED_LEGACY_LEARNER",
        message=f"Learner rule '{learner_rule}' is not mapped to a V3 learner grammar tuple.",
    )


def resolve_learner_spec(
    *,
    learner_rule: Any,
    policy_config: Any,
    learning_config: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> LearnerSpec:
    """
    Resolve and validate a learner grammar tuple at enforcement boundaries.

    Resolution order:
    1) explicit learning.learner_spec
    2) explicit learning.learner_preset
    3) legacy learner/policy/attention mapping
    """

    learning = learning_config if isinstance(learning_config, Mapping) else {}

    explicit_spec = learning.get("learner_spec")
    if explicit_spec is not None:
        if not isinstance(explicit_spec, Mapping):
            raise ValueError("learning.learner_spec must be an object when provided.")
        return LearnerSpec.from_dict(dict(explicit_spec))

    preset = learning.get("learner_preset")
    if preset is not None:
        if isinstance(preset, str):
            return expand_learner_preset(preset, metadata=dict(metadata or {}))
        if isinstance(preset, Mapping):
            preset_name = preset.get("name")
            if not isinstance(preset_name, str) or not preset_name.strip():
                raise ValueError("learning.learner_preset.name must be a non-empty string.")
            preset_metadata = dict(metadata or {})
            nested_meta = preset.get("metadata")
            if isinstance(nested_meta, Mapping):
                preset_metadata.update(dict(nested_meta))
            return expand_learner_preset(preset_name, metadata=preset_metadata)
        raise ValueError("learning.learner_preset must be a string or object.")

    policy_name = _normalize_policy_name(policy_config)
    attention_name = _normalize_attention_name(learning)
    return _derive_legacy_learner_spec(
        learner_rule=str(learner_rule or ""),
        policy_name=policy_name,
        attention_name=attention_name,
        metadata=metadata,
    )

