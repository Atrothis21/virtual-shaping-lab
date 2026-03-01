from dataclasses import dataclass
from typing import Dict, Any, List, Union, Tuple, Optional

OPERANT_PROTOCOLS = {
    "operant_conditioning",
    "matching_law",
    "shaping",
    "resurgence",
    "superextinction",
    "spontaneous_recovery",
}


class PayloadNormalizer:
    """Config normalization pipeline (defaults/coercions only)."""

    @staticmethod
    def normalize_experiment(
        exp: Dict[str, Any],
        *,
        parse_representation,
        parse_policy,
        parse_experiment_fields,
        parse_phases,
    ) -> Dict[str, Any]:
        representation = parse_representation(exp)
        policy = parse_policy(exp)
        exp_stimuli, exp_salience, exp_attention, exp_context_inference = parse_experiment_fields(exp)
        phases = parse_phases(exp)
        return {
            "representation": representation,
            "policy": policy,
            "stimuli": exp_stimuli,
            "salience": exp_salience,
            "attention": exp_attention,
            "context_inference": exp_context_inference,
            "phases": phases,
        }


class PayloadValidator:
    """Semantic/runtime constraint validation pipeline."""

    @staticmethod
    def validate_required_fields(require_fields, exp: Dict[str, Any], rep: Dict[str, Any]) -> None:
        require_fields(exp, ["learner", "agent", "representation"], "experiment")
        require_fields(rep, ["preset"], "report")

    @staticmethod
    def validate_runtime(validate_runtime_constraints, phases: List["PhaseConfig"]) -> None:
        validate_runtime_constraints(phases)


class PlanBuilder:
    """Declarative plan construction pipeline."""

    @staticmethod
    def build(config: "ExperimentConfig", *, build_experiment_plan):
        return build_experiment_plan(config)


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

    stimuli: List[str]
    salience: Dict[str, float]
    attention: Dict[str, float]
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
            attention = {}
            for key, val in attention_field.items():
                if isinstance(val, dict) and "attention" in val:
                    try:
                        attention[key] = float(val["attention"])
                    except (TypeError, ValueError):
                        raise ValueError(f"Invalid attention value for '{key}'")
                else:
                    try:
                        attention[key] = float(val)
                    except (TypeError, ValueError):
                        raise ValueError(f"Invalid attention value for '{key}'")
            return attention
        return {}

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
        representation = exp["representation"]
        if isinstance(representation, dict):
            if "name" not in representation:
                raise ValueError("representation object must include 'name'")
            if "params" in representation and not isinstance(representation["params"], dict):
                raise ValueError("representation.params must be an object")
            params = representation.get("params", {}) or {}
            if "attention" in params or "attention_compound" in params:
                raise ValueError(
                    "representation.params must not include attention fields; use experiment.attention (learner-owned)."
                )
            if "similarity" in params:
                cls._validate_similarity_matrix(
                    params["similarity"],
                    params.get("stimuli", []) or [],
                )
            cls._validate_representation_name(representation.get("name"))
            return representation

        if not isinstance(representation, str):
            raise ValueError("representation must be a string or object")
        cls._validate_representation_name(representation)
        return representation

    @staticmethod
    def _parse_policy(exp: Dict[str, Any]) -> Optional[Union[str, Dict[str, Any]]]:
        policy = exp.get("policy")
        if policy is None:
            return None
        if isinstance(policy, dict):
            if "name" not in policy:
                raise ValueError("policy object must include 'name'")
            if "params" in policy and not isinstance(policy["params"], dict):
                raise ValueError("policy.params must be an object")
            return policy
        if not isinstance(policy, str):
            raise ValueError("policy must be a string or object")
        return policy

    @classmethod
    def _parse_phases(cls, exp: Dict[str, Any]) -> List[PhaseConfig]:
        phases: List[PhaseConfig] = []
        if "phases" in exp:
            for i, phase in enumerate(exp["phases"]):
                for key in ["protocol", "params"]:
                    if key not in phase:
                        raise ValueError(
                            f"Phase {i} missing required field '{key}'"
                        )

                params = phase.get("params") or {}
                if not isinstance(params, dict):
                    raise ValueError(
                        f"Phase {i} params must be an object"
                    )
                stimuli = phase.get("stimuli")

                phases.append(
                    PhaseConfig(
                        name=phase.get("name", f"Phase {i}"),
                        protocol=phase["protocol"],
                        stimuli=cls._normalize_phase_stimuli(stimuli) if stimuli is not None else None,
                        params=params,
                    )
                )
            return phases

        required = ["protocol", "params"]
        missing = [k for k in required if k not in exp]
        if missing:
            raise ValueError(
                f"Missing required experiment fields: {', '.join(missing)}"
            )

        protocol_name = exp["protocol"]
        if protocol_name not in OPERANT_PROTOCOLS and "stimuli" not in exp:
            raise ValueError("Missing required experiment fields: stimuli")

        params = exp.get("params") or {}
        if not isinstance(params, dict):
            raise ValueError("experiment.params must be an object")
        phases.append(
            PhaseConfig(
                name="Phase 0",
                protocol=protocol_name,
                stimuli=cls._normalize_phase_stimuli(exp["stimuli"]) if "stimuli" in exp else None,
                params=params,
            )
        )
        return phases

    @classmethod
    def _parse_experiment_fields(
        cls,
        exp: Dict[str, Any],
    ) -> Tuple[List[str], Dict[str, float], Dict[str, float], Dict[str, Any]]:
        exp_stimuli, exp_salience = [], {}
        exp_attention: Dict[str, float] = {}
        exp_context_inference: Dict[str, Any] = {}

        if "stimuli" in exp:
            exp_stimuli, exp_salience = cls._normalize_stimuli(exp["stimuli"])

        if "salience" in exp:
            _, exp_salience = cls._normalize_stimuli(exp["salience"])

        if "attention" in exp:
            exp_attention = cls._normalize_attention(exp["attention"])

        if "context_inference" in exp and isinstance(exp["context_inference"], dict):
            exp_context_inference = exp["context_inference"]

        return exp_stimuli, exp_salience, exp_attention, exp_context_inference

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

        if "experiment" not in payload:
            raise ValueError("Payload missing 'experiment' section")

        if "report" not in payload:
            raise ValueError("Payload missing 'report' section")

        exp = payload["experiment"]
        rep = payload["report"]

        PayloadValidator.validate_required_fields(cls._require_fields, exp, rep)

        normalized = PayloadNormalizer.normalize_experiment(
            exp,
            parse_representation=cls._parse_representation,
            parse_policy=cls._parse_policy,
            parse_experiment_fields=cls._parse_experiment_fields,
            parse_phases=cls._parse_phases,
        )

        config = cls(
            learner=exp["learner"],
            agent=exp["agent"],
            representation=normalized["representation"],
            policy=normalized["policy"],
            stimuli=normalized["stimuli"],
            salience=normalized["salience"],
            attention=normalized["attention"],
            context_inference=normalized["context_inference"],
            phases=normalized["phases"],
            report_preset=rep["preset"],
        )
        PayloadValidator.validate_runtime(cls.validate_runtime_constraints, normalized["phases"])
        return config

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
