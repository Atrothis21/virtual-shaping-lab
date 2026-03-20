from dataclasses import dataclass
from typing import Dict, Any, List, Union, Tuple, Optional
from experiment.payload_contract import to_canonical_payload

OPERANT_PROTOCOLS = {
    "operant_conditioning",
    "matching_law",
    "shaping",
    "resurgence",
    "superextinction",
    "spontaneous_recovery",
}
_TEMPLATE_PHASE_KEY_SUFFIX = "_template"
_FORBIDDEN_TEMPLATE_PHASE_PARAM_KEYS = {
    "attention",
    "attention_compound",
    "salience",
    "similarity",
}
_CANONICAL_TEMPLATE_BACKED_PHASE_KEYS = {
    "acquisition",
    "nonreinforcement",
    "compound_acquisition",
    "compound_nonreinforcement",
    "differential_acquisition",
    "probe",
    "pavlovian_phase_template",
    "operant_phase_template",
}
_ALLOWED_ATTENTION_STRATEGIES = {
    "none",
    "static",
    "pearce_hall",
    "mackintosh",
}
_ATTENTION_CONFIG_ALLOWED_PARAM_KEYS = {
    "none": set(),
    "static": {"default", "overrides"},
    "pearce_hall": {"default", "overrides", "eta"},
    "mackintosh": {"default", "overrides", "kappa"},
}


def _is_template_param_guard_protocol(protocol_name: Any) -> bool:
    if not isinstance(protocol_name, str):
        return False
    return (
        protocol_name.endswith(_TEMPLATE_PHASE_KEY_SUFFIX)
        or protocol_name in _CANONICAL_TEMPLATE_BACKED_PHASE_KEYS
    )


class PayloadNormalizer:
    """Config normalization pipeline (defaults/coercions only)."""

    @staticmethod
    def normalize_experiment(
        exp: Dict[str, Any],
        parser: "ConfigParser",
    ) -> Dict[str, Any]:
        representation = parser.parse_representation(exp)
        program = parser.parse_program(exp)
        learning = parser.parse_learning(exp)
        policy = parser.parse_policy(exp)
        runtime = parser.parse_runtime(exp)
        exp_stimuli, exp_salience = parser.parse_representation_fields(representation)
        exp_context_inference = parser.parse_runtime_context(exp)
        return {
            "representation": representation,
            "policy": policy,
            "runtime": runtime,
            "stimuli": exp_stimuli,
            "salience": exp_salience,
            "attention": learning["attention"],
            "attention_config": learning["attention_config"],
            "context_inference": exp_context_inference,
            "phases": program["phases"],
        }

    @staticmethod
    def normalize_report(report: Dict[str, Any]) -> Dict[str, Any]:
        preset = report.get("preset")
        if not isinstance(preset, str) or not preset.strip():
            raise ValueError("report.preset must be a non-empty string")
        return {"preset": preset.strip()}

    @staticmethod
    def normalize_experiment_identity(exp: Dict[str, Any]) -> Dict[str, str]:
        agent = exp.get("agent", {})
        learning = agent.get("learning", {}) if isinstance(agent, dict) else {}
        return {
            "learner": str(learning["rule"]).strip(),
            "agent": str(agent["name"]).strip(),
        }


class PayloadValidator:
    """Semantic/runtime constraint validation pipeline."""

    @staticmethod
    def validate_payload_shape(payload: Dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise ValueError("Payload must be an object")
        if "experiment" not in payload:
            raise ValueError("Payload missing 'experiment' section")
        if "report" not in payload:
            raise ValueError("Payload missing 'report' section")
        if not isinstance(payload["experiment"], dict):
            raise ValueError("Payload 'experiment' section must be an object")
        if not isinstance(payload["report"], dict):
            raise ValueError("Payload 'report' section must be an object")

    @staticmethod
    def validate_phase_shape(exp: Dict[str, Any]) -> None:
        program = exp.get("program")
        if not isinstance(program, dict):
            raise ValueError("experiment.program must be an object")
        if "phases" not in program or not isinstance(program["phases"], list):
            raise ValueError("experiment.program.phases must be an array")

    @staticmethod
    def validate_required_fields(require_fields, exp: Dict[str, Any], rep: Dict[str, Any]) -> None:
        require_fields(exp, ["program", "agent", "runtime"], "experiment")
        require_fields(rep, ["preset"], "report")

    @staticmethod
    def validate_experiment_identity_fields(exp: Dict[str, Any]) -> None:
        agent = exp.get("agent")
        if not isinstance(agent, dict):
            raise ValueError("experiment.agent must be an object")
        if not isinstance(agent.get("name"), str) or not agent["name"].strip():
            raise ValueError("experiment.agent.name must be a non-empty string")
        learning = agent.get("learning")
        if not isinstance(learning, dict):
            raise ValueError("experiment.agent.learning must be an object")
        if not isinstance(learning.get("rule"), str) or not learning["rule"].strip():
            raise ValueError("experiment.agent.learning.rule must be a non-empty string")

    @staticmethod
    def validate_agent_policy_consistency(exp: Dict[str, Any]) -> None:
        agent = exp.get("agent")
        if not isinstance(agent, dict):
            raise ValueError("experiment.agent must be an object")
        agent_name = agent.get("name")
        policy = agent.get("policy")
        if agent_name == "classical_agent" and policy is not None:
            raise ValueError(
                "Classical assembly path does not accept policy; use operant_agent for policy-driven runs."
            )
        if agent_name == "operant_agent" and policy is None:
            raise ValueError("Operant assembly path requires an explicit policy.")

    @staticmethod
    def validate_runtime(validate_runtime_constraints, phases: List["PhaseConfig"]) -> None:
        validate_runtime_constraints(phases)


class PlanBuilder:
    """Declarative plan construction pipeline."""

    @staticmethod
    def build(config: "ExperimentConfig", *, build_experiment_plan):
        return build_experiment_plan(config)


class ConfigParser:
    """Parser composite that adapts ExperimentConfig parse methods."""

    def __init__(self, config_cls: "type[ExperimentConfig]"):
        self._config_cls = config_cls

    def parse_representation(self, exp: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        return self._config_cls._parse_representation(exp)

    def parse_program(self, exp: Dict[str, Any]) -> Dict[str, Any]:
        return self._config_cls._parse_program(exp)

    def parse_learning(self, exp: Dict[str, Any]) -> Dict[str, Any]:
        return self._config_cls._parse_learning(exp)

    def parse_policy(self, exp: Dict[str, Any]) -> Optional[Union[str, Dict[str, Any]]]:
        return self._config_cls._parse_policy(exp)

    def parse_runtime(self, exp: Dict[str, Any]) -> Dict[str, Any]:
        return self._config_cls._parse_runtime(exp)

    def parse_representation_fields(
        self,
        representation: Union[str, Dict[str, Any]],
    ) -> Tuple[List[str], Dict[str, float]]:
        return self._config_cls._parse_representation_fields(representation)

    def parse_runtime_context(self, exp: Dict[str, Any]) -> Dict[str, Any]:
        return self._config_cls._parse_runtime_context(exp)

    def parse_experiment_fields(
        self,
        exp: Dict[str, Any],
    ) -> Tuple[List[str], Dict[str, float], Dict[str, float], Dict[str, Any], Dict[str, Any]]:
        representation = self.parse_representation(exp)
        learning = self.parse_learning(exp)
        return (
            *self.parse_representation_fields(representation),
            learning["attention"],
            self.parse_runtime_context(exp),
            learning["attention_config"],
        )

    def parse_phases(self, exp: Dict[str, Any]) -> List["PhaseConfig"]:
        return self.parse_program(exp)["phases"]


class ConfigPipeline:
    """End-to-end payload -> ExperimentConfig pipeline."""

    def __init__(
        self,
        config_cls: "type[ExperimentConfig]",
        *,
        parser: Optional[ConfigParser] = None,
        normalizer=PayloadNormalizer,
        validator=PayloadValidator,
    ):
        self._config_cls = config_cls
        self._parser = parser or ConfigParser(config_cls)
        self._normalizer = normalizer
        self._validator = validator

    @staticmethod
    def _resolve_component_method(component: Any, method_name: str, fallback_component: Any):
        method = getattr(component, method_name, None)
        if callable(method):
            return method
        return getattr(fallback_component, method_name)

    def build(self, payload: Dict[str, Any]) -> "ExperimentConfig":
        validate_payload_shape = self._resolve_component_method(
            self._validator,
            "validate_payload_shape",
            PayloadValidator,
        )
        validate_phase_shape = self._resolve_component_method(
            self._validator,
            "validate_phase_shape",
            PayloadValidator,
        )
        validate_required_fields = self._resolve_component_method(
            self._validator,
            "validate_required_fields",
            PayloadValidator,
        )
        validate_experiment_identity_fields = self._resolve_component_method(
            self._validator,
            "validate_experiment_identity_fields",
            PayloadValidator,
        )
        validate_agent_policy_consistency = self._resolve_component_method(
            self._validator,
            "validate_agent_policy_consistency",
            PayloadValidator,
        )
        validate_runtime = self._resolve_component_method(
            self._validator,
            "validate_runtime",
            PayloadValidator,
        )

        normalize_experiment = self._resolve_component_method(
            self._normalizer,
            "normalize_experiment",
            PayloadNormalizer,
        )
        normalize_report = self._resolve_component_method(
            self._normalizer,
            "normalize_report",
            PayloadNormalizer,
        )
        normalize_experiment_identity = self._resolve_component_method(
            self._normalizer,
            "normalize_experiment_identity",
            PayloadNormalizer,
        )

        validate_payload_shape(payload)
        canonical_payload = to_canonical_payload(payload)
        exp = canonical_payload["experiment"]
        rep = canonical_payload["report"]

        validate_phase_shape(exp)
        validate_required_fields(self._config_cls._require_fields, exp, rep)
        validate_experiment_identity_fields(exp)
        validate_agent_policy_consistency(exp)

        normalized = normalize_experiment(
            exp,
            parser=self._parser,
        )
        normalized_report = normalize_report(rep)
        normalized_identity = normalize_experiment_identity(exp)
        validate_runtime(
            self._config_cls.validate_runtime_constraints,
            normalized["phases"],
        )

        return self._config_cls(
            learner=normalized_identity["learner"],
            agent=normalized_identity["agent"],
            representation=normalized["representation"],
            policy=normalized["policy"],
            runtime=normalized["runtime"],
            stimuli=normalized["stimuli"],
            salience=normalized["salience"],
            attention=normalized["attention"],
            attention_config=normalized["attention_config"],
            context_inference=normalized["context_inference"],
            phases=normalized["phases"],
            report_preset=normalized_report["preset"],
        )

    def build_plan(self, payload: Dict[str, Any], *, build_experiment_plan):
        config = self.build(payload)
        return PlanBuilder.build(config, build_experiment_plan=build_experiment_plan)


@dataclass
class PhaseConfig:
    """
    Declarative configuration for a single experimental phase.
    """
    name: str
    protocol: str
    stimuli: Any
    params: Optional[Dict[str, Any]]

    def __post_init__(self) -> None:
        if self.params is None:
            self.params = {}
        if not isinstance(self.params, dict):
            raise TypeError("PhaseConfig.params must be a dict")


@dataclass
class ExperimentConfig:
    """
    Declarative configuration for an experiment run.
    May consist of one or more phases.
    """

    # --- experiment-level definition ---
    learner: str
    agent: str
    representation: Union[str, Dict[str, Any]]
    policy: Optional[Union[str, Dict[str, Any]]]
    runtime: Dict[str, Any]

    stimuli: List[str]
    salience: Dict[str, float]
    attention: Dict[str, float]
    attention_config: Dict[str, Any]
    context_inference: Dict[str, Any]

    phases: List[PhaseConfig]

    # --- report definition ---
    report_preset: str

    @staticmethod
    def _normalize_stimuli(stimuli_field: Any) -> Tuple[List[str], Dict[str, float]]:
        """
        Accepts either:
          - list of stimulus names
          - dict of {stimulus: {salience: number}}
        Returns:
          (stimulus_names, salience_map)
        """
        if isinstance(stimuli_field, list):
            return stimuli_field, {}

        if isinstance(stimuli_field, dict):
            names = []
            salience = {}
            for key, val in stimuli_field.items():
                if isinstance(val, dict) and "salience" in val:
                    names.append(key)
                    try:
                        salience[key] = float(val["salience"])
                    except (TypeError, ValueError):
                        raise ValueError(f"Invalid salience value for '{key}'")
                else:
                    return [], {}
            return names, salience

        return [], {}

    @staticmethod
    def _normalize_attention(attention_field: Any) -> Dict[str, float]:
        """
        Accepts either:
          - dict of {stimulus: attention_value}
          - dict of {stimulus: {attention: value}}
        Returns:
          attention_map
        """
        if isinstance(attention_field, dict):
            if "name" in attention_field or "params" in attention_field:
                # Strategy-form attention object is parsed by _normalize_attention_config.
                return {}
            attention = {}
            for key, val in attention_field.items():
                if isinstance(val, dict) and "attention" in val:
                    try:
                        parsed = float(val["attention"])
                    except (TypeError, ValueError):
                        raise ValueError(f"Invalid attention value for '{key}'")
                    if parsed < 0.0 or parsed > 1.0:
                        raise ValueError(f"Invalid attention value for '{key}': must be in [0,1]")
                    attention[key] = parsed
                else:
                    try:
                        parsed = float(val)
                    except (TypeError, ValueError):
                        raise ValueError(f"Invalid attention value for '{key}'")
                    if parsed < 0.0 or parsed > 1.0:
                        raise ValueError(f"Invalid attention value for '{key}': must be in [0,1]")
                    attention[key] = parsed
            return attention
        return {}

    @staticmethod
    def _parse_unit_interval(value: Any, field: str) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field} must be numeric")
        if parsed < 0.0 or parsed > 1.0:
            raise ValueError(f"{field} must be in [0,1]")
        return parsed

    @classmethod
    def _normalize_attention_config_params(
        cls,
        *,
        strategy_name: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        allowed = _ATTENTION_CONFIG_ALLOWED_PARAM_KEYS[strategy_name]
        unknown = sorted(k for k in params.keys() if k not in allowed)
        if unknown:
            raise ValueError(
                "experiment.attention_config.params contains unsupported keys for "
                f"'{strategy_name}': {', '.join(unknown)}"
            )

        if strategy_name == "none":
            return {}

        normalized: Dict[str, Any] = {}
        if "default" in allowed:
            normalized["default"] = cls._parse_unit_interval(
                params.get("default", 1.0 if strategy_name == "static" else 0.5),
                "experiment.attention_config.params.default",
            )
        if "overrides" in allowed:
            overrides = params.get("overrides", {})
            if not isinstance(overrides, dict):
                raise ValueError("experiment.attention_config.params.overrides must be an object")
            normalized["overrides"] = cls._normalize_attention(overrides)
        if strategy_name == "pearce_hall":
            normalized["eta"] = cls._parse_unit_interval(
                params.get("eta", 0.2),
                "experiment.attention_config.params.eta",
            )
        if strategy_name == "mackintosh":
            normalized["kappa"] = cls._parse_unit_interval(
                params.get("kappa", 0.1),
                "experiment.attention_config.params.kappa",
            )
        return normalized

    @classmethod
    def _normalize_attention_config(
        cls,
        *,
        attention_config_field: Any,
    ) -> Dict[str, Any]:
        """
        Normalize canonical attention strategy config.

        Supported canonical form:
          - experiment.agent.learning.attention.config = {"name": str, "params": {...}}
        """
        cfg = attention_config_field

        if cfg is not None:
            if not isinstance(cfg, dict):
                raise ValueError("experiment.attention_config must be an object")
            if "name" not in cfg or "params" not in cfg:
                raise ValueError("experiment.attention_config must include 'name' and 'params'")
            name = cfg.get("name")
            params = cfg.get("params")
            if not isinstance(name, str) or not name.strip():
                raise ValueError("experiment.attention_config.name must be a non-empty string")
            if not isinstance(params, dict):
                raise ValueError("experiment.attention_config.params must be an object")
            normalized_name = name.strip().lower()
            if normalized_name not in _ALLOWED_ATTENTION_STRATEGIES:
                raise ValueError(
                    "Unsupported experiment.attention_config.name "
                    f"'{name}'. Allowed: {', '.join(sorted(_ALLOWED_ATTENTION_STRATEGIES))}"
                )
            return {
                "name": normalized_name,
                "params": cls._normalize_attention_config_params(
                    strategy_name=normalized_name,
                    params=dict(params),
                ),
            }

        return {"name": "none", "params": {}}

    @staticmethod
    def _normalize_phase_stimuli(phase_stimuli: Any) -> Any:
        """
        Preserve phase stimuli structure (e.g., cs_plus/cs_minus dicts).
        If a salience map is provided at phase level, convert to list of names.
        """
        if isinstance(phase_stimuli, list):
            return phase_stimuli

        if isinstance(phase_stimuli, dict):
            all_salience = True
            for val in phase_stimuli.values():
                if not (isinstance(val, dict) and "salience" in val):
                    all_salience = False
                    break
            if all_salience:
                return list(phase_stimuli.keys())
            return phase_stimuli

        return phase_stimuli

    @staticmethod
    def _validate_similarity_matrix(
        similarity: Dict[str, Any],
        stimuli: List[str],
    ) -> None:
        """
        Validate similarity matrix shape against stimuli list.
        """
        if not isinstance(similarity, dict):
            raise ValueError("similarity must be an object")

        if similarity.get("type") != "matrix":
            raise ValueError("similarity.type must be 'matrix'")

        values = similarity.get("values")
        if not isinstance(values, list) or not values:
            raise ValueError("similarity.values must be a non-empty matrix")

        matrix_size = len(values)
        for row in values:
            if not isinstance(row, list) or len(row) != matrix_size:
                raise ValueError("similarity.values must be a square matrix")

        matrix_stimuli = similarity.get("stimuli")
        if matrix_stimuli is not None:
            if not isinstance(matrix_stimuli, list) or not matrix_stimuli:
                raise ValueError("similarity.stimuli must be a non-empty list")
            if len(matrix_stimuli) != matrix_size:
                raise ValueError(
                    "similarity.stimuli length must match similarity.values size"
                )
            if stimuli and set(matrix_stimuli) != set(stimuli):
                raise ValueError(
                    "similarity.stimuli must match representation stimuli list"
                )
        else:
            if stimuli and len(stimuli) != matrix_size:
                raise ValueError(
                    "similarity.values size must match representation stimuli list"
                )

    @classmethod
    def _validate_representation_name(cls, rep_name: str) -> None:
        allowed_reps = {
            "vector_configural",
            "vector_elemental",
            "vector_hybrid",
        }
        if rep_name not in allowed_reps:
            raise ValueError(
                f"Unknown representation '{rep_name}'. "
                f"Allowed: {', '.join(sorted(allowed_reps))}"
            )

    @classmethod
    def _parse_representation(cls, exp: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        agent = exp.get("agent")
        if not isinstance(agent, dict):
            raise ValueError("experiment.agent must be an object")
        representation = agent.get("representation")
        if isinstance(representation, dict):
            if "name" not in representation:
                raise ValueError("experiment.agent.representation must include 'name'")
            if "params" in representation and not isinstance(representation["params"], dict):
                raise ValueError("experiment.agent.representation.params must be an object")
            params = representation.get("params", {}) or {}
            if "attention" in params or "attention_compound" in params:
                raise ValueError(
                    "experiment.agent.representation.params must not include attention fields; use experiment.agent.learning.attention."
                )
            if "similarity" in params:
                cls._validate_similarity_matrix(
                    params["similarity"],
                    params.get("stimuli", []) or [],
                )
            cls._validate_representation_name(representation.get("name"))
            return representation

        if not isinstance(representation, str):
            raise ValueError("experiment.agent.representation must be a string or object")
        cls._validate_representation_name(representation)
        return representation

    @staticmethod
    def _parse_policy(exp: Dict[str, Any]) -> Optional[Union[str, Dict[str, Any]]]:
        agent = exp.get("agent")
        if not isinstance(agent, dict):
            raise ValueError("experiment.agent must be an object")
        policy = agent.get("policy")
        if policy is None:
            return None
        if isinstance(policy, dict):
            if "name" not in policy:
                raise ValueError("experiment.agent.policy must include 'name'")
            if "params" in policy and not isinstance(policy["params"], dict):
                raise ValueError("experiment.agent.policy.params must be an object")
            return policy
        if not isinstance(policy, str):
            raise ValueError("experiment.agent.policy must be a string or object")
        return policy

    @staticmethod
    def _parse_runtime(exp: Dict[str, Any]) -> Dict[str, Any]:
        runtime = exp.get("runtime", {})
        if runtime is None:
            runtime = {}
        if not isinstance(runtime, dict):
            raise ValueError("experiment.runtime must be an object")

        normalized = {
            "seed": runtime.get("seed"),
            "update_mode": str(runtime.get("update_mode", "trial")),
            "record_mode": str(runtime.get("record_mode", "trial")),
            "strict_records": bool(runtime.get("strict_records", False)),
            "debug": bool(runtime.get("debug", False)),
        }
        if normalized["update_mode"] not in {"trial", "tick"}:
            raise ValueError("experiment.runtime.update_mode must be 'trial' or 'tick'")
        if normalized["record_mode"] not in {"trial", "tick"}:
            raise ValueError("experiment.runtime.record_mode must be 'trial' or 'tick'")
        if "operator_pipeline" in runtime:
            operator_pipeline = runtime.get("operator_pipeline")
            if not isinstance(operator_pipeline, dict):
                raise ValueError("experiment.runtime.operator_pipeline must be an object when provided")
            normalized["operator_pipeline"] = dict(operator_pipeline)
        if "episode" in runtime:
            episode = runtime.get("episode")
            if not isinstance(episode, dict):
                raise ValueError("experiment.runtime.episode must be an object when provided")
            normalized["episode"] = dict(episode)
        if "horizon" in runtime:
            horizon = runtime.get("horizon")
            if not isinstance(horizon, dict):
                raise ValueError("experiment.runtime.horizon must be an object when provided")
            normalized["horizon"] = dict(horizon)
        if "episode_id" in runtime:
            normalized["episode_id"] = runtime.get("episode_id")
        if "rollout_id" in runtime:
            normalized["rollout_id"] = runtime.get("rollout_id")
        return normalized

    @classmethod
    def _parse_program(cls, exp: Dict[str, Any]) -> Dict[str, Any]:
        return {"phases": cls._parse_phases(exp)}

    @classmethod
    def _parse_phases(cls, exp: Dict[str, Any]) -> List[PhaseConfig]:
        phases: List[PhaseConfig] = []
        program = exp.get("program")
        if not isinstance(program, dict):
            raise ValueError("experiment.program must be an object")
        raw_phases = program.get("phases")
        if not isinstance(raw_phases, list) or not raw_phases:
            raise ValueError("experiment.program.phases must be a non-empty array")
        for i, phase in enumerate(raw_phases):
            if not isinstance(phase, dict):
                raise ValueError(f"Phase {i} must be an object")
            for key in ["protocol", "params"]:
                if key not in phase:
                    raise ValueError(f"Phase {i} missing required field '{key}'")
            params = phase.get("params") or {}
            if not isinstance(params, dict):
                raise ValueError(f"Phase {i} params must be an object")
            protocol_name = phase["protocol"]
            if _is_template_param_guard_protocol(protocol_name):
                leaked = sorted(k for k in _FORBIDDEN_TEMPLATE_PHASE_PARAM_KEYS if k in params)
                if leaked:
                    raise ValueError(
                        f"Phase {i} template params must not include representation/learner-owned keys: {', '.join(leaked)}"
                    )
            stimuli = phase.get("stimuli")
            phases.append(
                PhaseConfig(
                    name=phase.get("name", f"Phase {i}"),
                    protocol=protocol_name,
                    stimuli=cls._normalize_phase_stimuli(stimuli) if stimuli is not None else None,
                    params=params,
                )
            )
        return phases

    @classmethod
    def _parse_learning(cls, exp: Dict[str, Any]) -> Dict[str, Any]:
        agent = exp.get("agent", {})
        if not isinstance(agent, dict):
            raise ValueError("experiment.agent must be an object")
        learning = agent.get("learning", {})
        if not isinstance(learning, dict):
            raise ValueError("experiment.agent.learning must be an object")
        attention_block = learning.get("attention", {})
        exp_attention: Dict[str, float] = {}
        exp_attention_config: Dict[str, Any] = {"name": "none", "params": {}}
        if isinstance(attention_block, dict):
            exp_attention = cls._normalize_attention(attention_block.get("initial"))
            exp_attention_config = cls._normalize_attention_config(
                attention_config_field=(
                    attention_block.get("config")
                    if isinstance(attention_block.get("config"), dict) and attention_block.get("config")
                    else None
                ),
            )
        return {
            "attention": exp_attention,
            "attention_config": exp_attention_config,
        }

    @classmethod
    def _parse_representation_fields(
        cls,
        representation: Union[str, Dict[str, Any]],
    ) -> Tuple[List[str], Dict[str, float]]:
        exp_stimuli, exp_salience = [], {}
        if isinstance(representation, dict):
            rep_params = representation.get("params", {})
            if isinstance(rep_params, dict):
                if "stimuli" in rep_params:
                    exp_stimuli = list(rep_params.get("stimuli", []))
                salience_field = rep_params.get("salience", representation.get("salience"))
                if salience_field is not None:
                    if isinstance(salience_field, dict):
                        try:
                            exp_salience = {
                                str(k): float(v.get("salience") if isinstance(v, dict) and "salience" in v else v)
                                for k, v in salience_field.items()
                            }
                        except (TypeError, ValueError):
                            _, exp_salience = cls._normalize_stimuli(salience_field)
        return exp_stimuli, exp_salience

    @staticmethod
    def _parse_runtime_context(exp: Dict[str, Any]) -> Dict[str, Any]:
        exp_context_inference: Dict[str, Any] = {}
        if "runtime" in exp and isinstance(exp["runtime"], dict):
            context_inference = exp["runtime"].get("context_inference")
            if isinstance(context_inference, dict):
                exp_context_inference = context_inference
        return exp_context_inference

    @classmethod
    def validate_runtime_constraints(cls, phases: List[PhaseConfig]) -> None:
        """
        Runtime-only checks that go beyond schema validation.
        """
        has_learning = False
        for phase in phases:
            if phase.protocol in {"acquisition", "compound_acquisition", "differential_acquisition"}:
                has_learning = True
                break

        for idx, phase in enumerate(phases):
            if phase.protocol in {"nonreinforcement", "compound_nonreinforcement"} and not has_learning:
                raise ValueError(
                    f"Phase '{phase.protocol}' at position {idx} requires a prior learning phase."
                )

    @classmethod
    def from_payload(cls, payload: dict) -> "ExperimentConfig":
        """
        Construct an ExperimentConfig from a validated UI payload.
        """
        return ConfigPipeline(cls).build(payload)

    @classmethod
    def plan_from_payload(cls, payload: dict):
        """Build a declarative ExperimentPlan directly from payload."""
        from experiment.plan_builder import build_experiment_plan

        return ConfigPipeline(cls).build_plan(
            payload,
            build_experiment_plan=build_experiment_plan,
        )

    @staticmethod
    def _require_fields(data: Dict[str, Any], fields: List[str], label: str) -> None:
        missing = [k for k in fields if k not in data]
        if missing:
            raise ValueError(
                f"Missing required {label} fields: {', '.join(missing)}"
            )

    def to_plan(self):
        """Build a declarative ExperimentPlan from this config."""
        from experiment.plan_builder import build_experiment_plan

        return PlanBuilder.build(self, build_experiment_plan=build_experiment_plan)
