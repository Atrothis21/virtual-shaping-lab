"""Normalization and validation pipelines for parameter composition."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from virtual_shaping_lab.domain.naming import normalize_protocol_key


def _as_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be numeric")


def _is_grid_aligned(duration_s: float, dt_s: float, tol: float = 1e-9) -> bool:
    steps = duration_s / dt_s
    return abs(steps - round(steps)) <= tol


class ParameterNormalizerPipeline:
    """Normalize draft payloads into deterministic config-like dictionaries."""

    @staticmethod
    def normalize(payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be an object")

        out = deepcopy(dict(payload))
        exp = out.setdefault("experiment", {})
        if not isinstance(exp, dict):
            raise ValueError("experiment must be an object")

        # Normalize protocol keys.
        if "protocol" in exp:
            exp["protocol"] = normalize_protocol_key(exp["protocol"])
        phases = exp.get("phases")
        if isinstance(phases, list):
            for phase in phases:
                if isinstance(phase, dict) and "protocol" in phase:
                    phase["protocol"] = normalize_protocol_key(phase["protocol"])
                params = phase.get("params") if isinstance(phase, dict) else None
                if isinstance(params, dict) and "n_trials" in params:
                    try:
                        params["n_trials"] = int(params["n_trials"])
                    except (TypeError, ValueError):
                        pass

        # Normalize policy key.
        policy = exp.get("policy")
        if isinstance(policy, dict) and "name" in policy:
            policy["name"] = normalize_protocol_key(policy["name"])

        # Runtime defaults.
        runtime = exp.setdefault("runtime", {})
        if not isinstance(runtime, dict):
            raise ValueError("experiment.runtime must be an object")
        runtime.setdefault("seed", None)
        runtime.setdefault("update_mode", "trial")
        runtime.setdefault("record_mode", "trial")
        runtime.setdefault("strict_records", False)
        runtime.setdefault("debug", False)

        return out


class ParameterValidatorPipeline:
    """Semantic and ownership-boundary validation for normalized payloads."""

    _LEAK_KEYS = {"attention", "attention_compound", "salience", "similarity"}
    _REPRESENTATION_OWNED_KEYS = {
        "salience",
        "similarity",
        "context",
        "contexts",
        "context_map",
        "similarity_kernel",
        "salience_operator",
        "temporal_basis",
    }
    _ALLOWED_ATTENTION_STRATEGIES = {"none", "static", "pearce_hall", "mackintosh"}
    _ATTENTION_CONFIG_ALLOWED_PARAM_KEYS = {
        "none": set(),
        "static": {"default", "overrides"},
        "pearce_hall": {"default", "overrides", "eta"},
        "mackintosh": {"default", "overrides", "kappa"},
    }
    _ALLOWED_TEMPORAL_BASIS_VARIANTS = {"identity", "bins", "traces"}
    _ALLOWED_PREDICTION_ERROR_VARIANTS = {"rescorla_wagner", "td_value", "td_0", "q_learner"}

    @classmethod
    def validate(cls, payload: Mapping[str, Any]) -> None:
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be an object")
        exp = payload.get("experiment")
        if not isinstance(exp, Mapping):
            raise ValueError("payload.experiment must be an object")

        rep = exp.get("representation")
        if rep is None:
            raise ValueError("experiment.representation is required")

        cls._validate_representation(rep, exp)
        cls._validate_attention_config(exp)
        cls._validate_prediction_error_config(exp)
        cls._validate_attention_keys(exp, rep)
        cls._validate_runtime(exp)
        cls._validate_phases(exp)
        cls._validate_contexts(exp, rep)

    @classmethod
    def _validate_attention_config(cls, exp: Mapping[str, Any]) -> None:
        cfg = exp.get("attention_config")
        if cfg is None:
            attn = exp.get("attention")
            if isinstance(attn, Mapping) and ("name" in attn or "params" in attn):
                cfg = attn
            else:
                return
        if not isinstance(cfg, Mapping):
            raise ValueError("experiment.attention_config must be an object")
        if "name" not in cfg or "params" not in cfg:
            raise ValueError("experiment.attention_config must include 'name' and 'params'")
        name = cfg.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("experiment.attention_config.name must be a non-empty string")
        if name.strip().lower() not in cls._ALLOWED_ATTENTION_STRATEGIES:
            raise ValueError(
                "Unsupported experiment.attention_config.name "
                f"'{name}'. Allowed: {', '.join(sorted(cls._ALLOWED_ATTENTION_STRATEGIES))}"
            )
        params = cfg.get("params")
        if not isinstance(params, Mapping):
            raise ValueError("experiment.attention_config.params must be an object")
        cls._validate_no_representation_owned_keys(
            params,
            field="experiment.attention_config.params",
        )
        strategy = name.strip().lower()
        allowed = cls._ATTENTION_CONFIG_ALLOWED_PARAM_KEYS[strategy]
        unknown = sorted(k for k in params.keys() if k not in allowed)
        if unknown:
            raise ValueError(
                "experiment.attention_config.params contains unsupported keys for "
                f"'{strategy}': {', '.join(unknown)}"
            )
        if "default" in params:
            cls._validate_unit_interval(
                params["default"], "experiment.attention_config.params.default"
            )
        if "eta" in params:
            cls._validate_unit_interval(
                params["eta"], "experiment.attention_config.params.eta"
            )
        if "kappa" in params:
            cls._validate_unit_interval(
                params["kappa"], "experiment.attention_config.params.kappa"
            )
        if "overrides" in params:
            overrides = params["overrides"]
            if not isinstance(overrides, Mapping):
                raise ValueError("experiment.attention_config.params.overrides must be an object")
            for key, value in overrides.items():
                cls._validate_unit_interval(
                    value, f"experiment.attention_config.params.overrides['{key}']"
                )

    @staticmethod
    def _validate_unit_interval(value: Any, field: str) -> None:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field} must be numeric")
        if parsed < 0.0 or parsed > 1.0:
            raise ValueError(f"{field} must be in [0,1]")

    @staticmethod
    def _validate_runtime(exp: Mapping[str, Any]) -> None:
        runtime = exp.get("runtime", {})
        if not isinstance(runtime, Mapping):
            raise ValueError("experiment.runtime must be an object")

        update_mode = runtime.get("update_mode", "trial")
        record_mode = runtime.get("record_mode", "trial")
        if str(update_mode) not in {"trial", "tick"}:
            raise ValueError("runtime.update_mode must be 'trial' or 'tick'")
        if str(record_mode) not in {"trial", "tick"}:
            raise ValueError("runtime.record_mode must be 'trial' or 'tick'")
        if not isinstance(runtime.get("strict_records", False), bool):
            raise ValueError("runtime.strict_records must be boolean")
        if not isinstance(runtime.get("debug", False), bool):
            raise ValueError("runtime.debug must be boolean")

    @classmethod
    def _validate_representation(cls, rep: Any, exp: Mapping[str, Any]) -> None:
        if isinstance(rep, str):
            return
        if not isinstance(rep, Mapping):
            raise ValueError("representation must be string or object")
        params = rep.get("params", {})
        if not isinstance(params, Mapping):
            raise ValueError("representation.params must be an object")
        if "attention" in params or "attention_compound" in params:
            raise ValueError("representation.params must not include attention fields")
        temporal_basis = params.get("temporal_basis")
        if temporal_basis is not None:
            cls._validate_temporal_basis(temporal_basis)
        similarity = params.get("similarity")
        if similarity is not None:
            cls._validate_similarity(similarity)
        cls._validate_salience(exp.get("salience"))

    @classmethod
    def _validate_temporal_basis(cls, temporal_basis: Any) -> None:
        if not isinstance(temporal_basis, Mapping):
            raise ValueError("temporal_basis must be an object")
        variant = str(temporal_basis.get("variant", temporal_basis.get("name", "identity"))).strip().lower()
        if variant not in cls._ALLOWED_TEMPORAL_BASIS_VARIANTS:
            raise ValueError(
                "temporal_basis.variant must be one of: "
                + ", ".join(sorted(cls._ALLOWED_TEMPORAL_BASIS_VARIANTS))
            )
        enabled = bool(temporal_basis.get("enabled", True))
        if not enabled:
            return
        dimension = temporal_basis.get("dimension")
        try:
            parsed_dimension = int(dimension)
        except (TypeError, ValueError):
            raise ValueError("temporal_basis.dimension must be an integer")
        if parsed_dimension <= 0:
            raise ValueError("temporal_basis.dimension must be > 0 when temporal_basis is enabled")

    @classmethod
    def _validate_salience(cls, salience: Any) -> None:
        if salience is None:
            return
        if isinstance(salience, Mapping):
            for key, value in salience.items():
                raw = value.get("salience") if isinstance(value, Mapping) and "salience" in value else value
                cls._validate_unit_interval(raw, f"salience['{key}']")
            return
        cls._validate_unit_interval(salience, "salience")

    @staticmethod
    def _validate_similarity(similarity: Any) -> None:
        if not isinstance(similarity, Mapping):
            raise ValueError("similarity must be an object")
        if similarity.get("type") != "matrix":
            raise ValueError("similarity.type must be 'matrix'")
        values = similarity.get("values")
        if not isinstance(values, list) or not values:
            raise ValueError("similarity.values must be a non-empty matrix")
        n = len(values)
        for row in values:
            if not isinstance(row, list) or len(row) != n:
                raise ValueError("similarity.values must be a square matrix")
        for i in range(n):
            for j in range(n):
                left = float(values[i][j])
                right = float(values[j][i])
                if abs(left - right) > 1e-9:
                    raise ValueError("similarity.values must be symmetric")
                if left < 0.0 or left > 1.0:
                    raise ValueError("similarity.values entries must be in [0,1]")

    @classmethod
    def _validate_prediction_error_config(cls, exp: Mapping[str, Any]) -> None:
        cfg = exp.get("prediction_error")
        if cfg is None:
            return
        if isinstance(cfg, str):
            variant = cfg.strip().lower()
        elif isinstance(cfg, Mapping):
            variant = str(cfg.get("variant", cfg.get("name", ""))).strip().lower()
            params = cfg.get("params", {})
            if not isinstance(params, Mapping):
                raise ValueError("prediction_error.params must be an object")
            cls._validate_no_representation_owned_keys(
                params,
                field="prediction_error.params",
            )
        else:
            raise ValueError("prediction_error must be a string or object")
        if variant not in cls._ALLOWED_PREDICTION_ERROR_VARIANTS:
            raise ValueError(
                "prediction_error variant must be one of: "
                + ", ".join(sorted(cls._ALLOWED_PREDICTION_ERROR_VARIANTS))
            )

    @classmethod
    def _validate_no_representation_owned_keys(
        cls,
        value: Mapping[str, Any],
        *,
        field: str,
    ) -> None:
        bad = cls._REPRESENTATION_OWNED_KEYS & set(value.keys())
        if bad:
            raise ValueError(
                f"{field} must not contain representation-owned keys: {', '.join(sorted(bad))}"
            )

    @classmethod
    def _validate_attention_keys(cls, exp: Mapping[str, Any], rep: Any) -> None:
        attention = exp.get("attention")
        if attention is None:
            return
        if not isinstance(attention, Mapping):
            raise ValueError("experiment.attention must be an object")
        if "name" in attention or "params" in attention:
            # Strategy-form attention is validated by _validate_attention_config.
            return

        known_stimuli: set[str] = set()
        stimuli = exp.get("stimuli")
        if isinstance(stimuli, list):
            known_stimuli.update(str(s) for s in stimuli)
        elif isinstance(stimuli, Mapping):
            known_stimuli.update(str(k) for k in stimuli.keys())

        if isinstance(rep, Mapping):
            params = rep.get("params", {})
            if isinstance(params, Mapping):
                rep_stimuli = params.get("stimuli", [])
                if isinstance(rep_stimuli, list):
                    known_stimuli.update(str(s) for s in rep_stimuli)

        if known_stimuli:
            unknown = sorted([k for k in attention.keys() if str(k) not in known_stimuli])
            if unknown:
                raise ValueError(f"attention keys not in known stimuli: {', '.join(unknown)}")

    @classmethod
    def _validate_phases(cls, exp: Mapping[str, Any]) -> None:
        phases = exp.get("phases")
        if not isinstance(phases, list):
            return
        for idx, phase in enumerate(phases):
            if not isinstance(phase, Mapping):
                raise ValueError(f"phase[{idx}] must be an object")
            params = phase.get("params", {})
            if not isinstance(params, Mapping):
                raise ValueError(f"phase[{idx}].params must be an object")

            leak = sorted([k for k in params.keys() if k in cls._LEAK_KEYS])
            if leak:
                raise ValueError(
                    f"phase[{idx}] params contain forbidden cross-concern keys: {', '.join(leak)}"
                )

            if "duration_s" in params and "dt_s" in params:
                duration = _as_float(params["duration_s"], "duration_s")
                dt = _as_float(params["dt_s"], "dt_s")
                if dt <= 0.0:
                    raise ValueError("dt_s must be > 0")
                if duration <= 0.0:
                    raise ValueError("duration_s must be > 0")
                if not _is_grid_aligned(duration, dt):
                    raise ValueError("dt_s must divide duration_s")

    @staticmethod
    def _validate_contexts(exp: Mapping[str, Any], rep: Any) -> None:
        known_contexts: set[str] = set()
        if isinstance(rep, Mapping):
            params = rep.get("params", {})
            if isinstance(params, Mapping):
                contexts = params.get("contexts")
                if isinstance(contexts, list):
                    known_contexts.update(str(c) for c in contexts)
        phases = exp.get("phases")
        if not isinstance(phases, list):
            return
        for idx, phase in enumerate(phases):
            if not isinstance(phase, Mapping):
                continue
            params = phase.get("params", {})
            if not isinstance(params, Mapping):
                continue
            ctx = params.get("context")
            if ctx is None:
                continue
            if known_contexts and str(ctx) not in known_contexts:
                raise ValueError(
                    f"phase[{idx}] context '{ctx}' not declared in representation contexts"
                )

