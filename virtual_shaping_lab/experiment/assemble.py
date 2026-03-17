# experiment/assemble.py

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from virtual_shaping_lab.agents.policies.null_policy import NullPolicy
from virtual_shaping_lab.agents.math_objects.attention_objects import build_attention_mechanism
from virtual_shaping_lab.agents.math_objects.prediction_error_objects import (
    RescorlaWagnerPredictionError,
    TD0PredictionError,
)
from virtual_shaping_lab.agents.math_objects.representation_objects import (
    DefaultContextMap,
    MatrixSimilarityKernel,
)
from virtual_shaping_lab.agents.math_objects.salience_objects import DiagonalSalienceOperator
from virtual_shaping_lab.agents.math_objects.temporal_objects import build_temporal_basis
from experiment.factories.learner_factory import build_learner
from experiment.factories.agent_factory import build_agent
from experiment.factories.protocol_factory import build_protocol, PROTOCOL_REGISTRY
from experiment.factories.representation_factory import build_representation
from experiment.factories.reward_schedule_factory import build_reward_schedule
from experiment.factories.policy_factory import build_policy
from experiment.phases.public import build_phase
from experiment.config import PhaseConfig
from experiment.domain.types import ExperimentPlan
from experiment.parameters import validate_composed_parameter_ownership

OPERANT_AGENT_NAME = "operant_agent"


def _get_composed_parameters(config) -> dict[str, Any]:
    composed = getattr(config, "composed_parameters", None)
    if isinstance(composed, dict):
        return composed
    return {}


def _get_composed_representation(config) -> dict[str, Any]:
    composed = _get_composed_parameters(config)
    rep = composed.get("representation", {})
    return rep if isinstance(rep, dict) else {}


def _get_composed_learner(config) -> dict[str, Any]:
    composed = _get_composed_parameters(config)
    learner = composed.get("learner", {})
    return learner if isinstance(learner, dict) else {}


def _get_composed_policy(config) -> dict[str, Any]:
    composed = _get_composed_parameters(config)
    policy = composed.get("policy", {})
    return policy if isinstance(policy, dict) else {}


def _get_composed_units(config) -> list[dict[str, Any]]:
    composed = _get_composed_parameters(config)
    units = composed.get("units", [])
    if isinstance(units, list):
        return [u for u in units if isinstance(u, dict)]
    return []


def _resolve_learner_name(config) -> str:
    learning_config = getattr(config, "learning_config", None)
    if isinstance(learning_config, dict):
        rule = learning_config.get("rule")
        if isinstance(rule, str) and rule:
            return rule
    composed_learner = _get_composed_learner(config)
    algorithm = composed_learner.get("algorithm")
    if isinstance(algorithm, str) and algorithm:
        return algorithm
    return config.learner


def _typed_similarity_to_matrix(similarity_map: dict[str, Any], stimuli: list[str]) -> dict[str, Any]:
    if not isinstance(similarity_map, dict) or not similarity_map:
        return {}

    labels = list(stimuli)
    if not labels:
        keys = set()
        for key, row in similarity_map.items():
            keys.add(str(key))
            if isinstance(row, dict):
                for inner in row.keys():
                    keys.add(str(inner))
        labels = sorted(keys)
    if not labels:
        return {}

    values = []
    for i, a in enumerate(labels):
        row = []
        typed_row = similarity_map.get(a, {})
        typed_row = typed_row if isinstance(typed_row, dict) else {}
        for j, b in enumerate(labels):
            if a == b:
                v = typed_row.get(b, 1.0)
            else:
                v = typed_row.get(b, 0.0)
            row.append(float(v))
        values.append(row)

    return {
        "type": "matrix",
        "stimuli": labels,
        "values": values,
    }


# Context inference: consolidates any context_* params across phases/protocols.
# Keeps representation assembly independent of protocol structure.
def _infer_contexts(rep_params, config):
    contexts = set(rep_params.get("contexts", []))

    if config.phases:
        for phase in config.phases:
            for key, value in phase.params.items():
                if key == "context" and value:
                    contexts.add(value)
                if key.startswith("context_") and value:
                    contexts.add(value)
    else:
        proto_params = getattr(config, "params", {}) or {}
        for key, value in proto_params.items():
            if key == "context" and value:
                contexts.add(value)
            if key.startswith("context_") and value:
                contexts.add(value)

    if not contexts:
        contexts.add("A")

    rep_params["contexts"] = sorted(contexts)
    return rep_params


def _has_explicit_phase_context(phase) -> bool:
    params = getattr(phase, "params", {}) or {}
    return bool(params.get("context"))


def _has_explicit_unit_context(phase, typed_unit: dict[str, Any] | None) -> bool:
    if _has_explicit_phase_context(phase):
        return True
    if isinstance(typed_unit, dict) and typed_unit.get("context_id"):
        return True
    return False


def _infer_phase_contexts(config) -> list[str | None]:
    """
    Heuristic latent context assignment per phase.

    - Assign new context when phase name changes.
    - Reuse context for consecutive phases with the same name.
    - Cap at max_contexts (defaults to 3).
    """
    inference = getattr(config, "context_inference", {}) or {}
    if not inference.get("enabled"):
        return [None] * len(config.phases)

    max_contexts = int(inference.get("max_contexts", 3))
    max_contexts = max(1, min(3, max_contexts))
    labels = ["A", "B", "C"][:max_contexts]

    inferred = []
    last_name = None
    idx = 0
    for phase in config.phases:
        if phase.name == last_name and inferred:
            inferred.append(inferred[-1])
            continue

        label = labels[idx] if idx < len(labels) else labels[-1]
        inferred.append(label)
        last_name = phase.name
        if idx < len(labels) - 1:
            idx += 1

    return inferred


# Learner params: derive alpha/gamma (+ policy actions) from config.
# Salience is representation-owned and applied during encoding.
def _extract_learner_params(config, representation, policy_actions):
    learner_params = {}
    composed_learner = _get_composed_learner(config)
    composed_policy = _get_composed_policy(config)

    if config.phases:
        first_params = config.phases[0].params
        if "alpha" in first_params:
            learner_params["alpha"] = first_params["alpha"]
        if "gamma" in first_params:
            learner_params["gamma"] = first_params["gamma"]
    if "alpha" not in learner_params and "alpha" in composed_learner:
        learner_params["alpha"] = composed_learner["alpha"]
    if (
        "gamma" not in learner_params
        and "gamma" in composed_learner
        and composed_learner.get("gamma") is not None
    ):
        learner_params["gamma"] = composed_learner["gamma"]

    if policy_actions:
        learner_params.setdefault("actions", policy_actions)
    elif isinstance(composed_policy.get("actions"), list):
        learner_params.setdefault("actions", composed_policy["actions"])

    return learner_params


def _build_context_map(config, rep_params: dict[str, Any]):
    composed_rep = _get_composed_representation(config)
    context_cfg = composed_rep.get("context_map", {})
    default_context = rep_params.get("default_context", None)
    if isinstance(context_cfg, dict):
        default_context = context_cfg.get("default_context", default_context)
    return DefaultContextMap(default_context=default_context)


def _build_similarity_kernel(config, rep_params: dict[str, Any]):
    composed_rep = _get_composed_representation(config)
    kernel_cfg = composed_rep.get("similarity_kernel", {})
    if isinstance(kernel_cfg, dict) and kernel_cfg.get("enabled"):
        matrix = kernel_cfg.get("matrix", {})
        return MatrixSimilarityKernel(matrix if isinstance(matrix, dict) else {})

    similarity = rep_params.get("similarity")
    if isinstance(similarity, dict) and similarity.get("type") == "matrix":
        labels = similarity.get("stimuli", [])
        values = similarity.get("values", [])
        if isinstance(labels, list) and isinstance(values, list) and len(labels) == len(values):
            matrix: dict[str, dict[str, float]] = {}
            for i, label in enumerate(labels):
                row = values[i]
                if not isinstance(row, list):
                    continue
                matrix[str(label)] = {}
                for j, inner_label in enumerate(labels):
                    if j < len(row):
                        matrix[str(label)][str(inner_label)] = float(row[j])
            return MatrixSimilarityKernel(matrix)
    return None


def _build_temporal_basis_object(config):
    composed_rep = _get_composed_representation(config)
    basis_cfg = composed_rep.get("temporal_basis")
    if isinstance(basis_cfg, dict):
        return build_temporal_basis(basis_cfg)
    return None


def _build_salience_operator_for_representation(representation):
    salience = getattr(representation, "salience", None)
    if salience is None:
        return None
    try:
        return DiagonalSalienceOperator(salience)
    except (TypeError, ValueError):
        return None


def _build_prediction_error_rule(config):
    composed_learner = _get_composed_learner(config)
    rule_cfg = composed_learner.get("prediction_error_rule", {})
    if not isinstance(rule_cfg, dict):
        return None
    variant = str(rule_cfg.get("variant", "")).strip().lower()
    params = rule_cfg.get("params", {})
    params = params if isinstance(params, dict) else {}
    if variant in {"rescorla_wagner", "rw"}:
        return RescorlaWagnerPredictionError()
    if variant in {"td_value", "td_0", "td0"}:
        gamma = composed_learner.get("gamma", params.get("gamma", 0.0))
        return TD0PredictionError(gamma=float(gamma or 0.0))
    return None


def _build_attention_mechanism_object(config):
    composed_learner = _get_composed_learner(config)
    mech_cfg = composed_learner.get("attention_mechanism", {})
    if isinstance(mech_cfg, dict):
        variant = str(mech_cfg.get("variant", "none")).strip().lower()
        params = mech_cfg.get("params", {})
        params = dict(params) if isinstance(params, dict) else {}
        if "default" in mech_cfg and "default" not in params:
            params["default"] = mech_cfg.get("default")
        if "overrides" in mech_cfg and "overrides" not in params:
            params["overrides"] = mech_cfg.get("overrides")
        return build_attention_mechanism(variant, params=params)

    attention_cfg = getattr(config, "attention_config", None)
    if isinstance(attention_cfg, dict) and isinstance(attention_cfg.get("name"), str):
        params = attention_cfg.get("params", {})
        return build_attention_mechanism(
            attention_cfg["name"],
            params=params if isinstance(params, dict) else {},
        )
    return None


def _assign_attention_map(config, learner):
    attention_cfg = getattr(config, "attention_config", None)
    learning_config = getattr(config, "learning_config", None)
    if isinstance(learning_config, dict):
        attention_block = learning_config.get("attention", {})
        if isinstance(attention_block, dict) and isinstance(attention_block.get("config"), dict):
            attention_cfg = attention_block.get("config")
    if isinstance(attention_cfg, dict):
        cfg_name = attention_cfg.get("name")
        cfg_params = attention_cfg.get("params", {})
        if isinstance(cfg_name, str) and hasattr(learner, "set_attention_config"):
            learner.set_attention_config(
                name=cfg_name,
                params=cfg_params if isinstance(cfg_params, dict) else {},
            )

    attention_map = dict(getattr(config, "attention", None) or {})
    if isinstance(learning_config, dict):
        attention_block = learning_config.get("attention", {})
        if isinstance(attention_block, dict) and isinstance(attention_block.get("initial"), dict):
            attention_map = dict(attention_block.get("initial", {}))
    if not attention_map:
        composed_learner = _get_composed_learner(config)
        composed_attention = composed_learner.get("attention", {}) if isinstance(composed_learner.get("attention"), dict) else {}
        overrides = composed_attention.get("overrides", {})
        if isinstance(overrides, dict):
            attention_map = dict(overrides)

    if attention_map:
        if hasattr(learner, "set_attention_map"):
            learner.set_attention_map(attention_map)
        else:
            learner.attention_map = dict(attention_map)


def _build_policy_from_config(config):
    policy_config = getattr(config, "policy_config", None)
    if policy_config is None:
        policy_config = getattr(config, "policy", None)

    if not policy_config:
        composed_policy = _get_composed_policy(config)
        policy_name = composed_policy.get("name")
        if isinstance(policy_name, str) and policy_name and policy_name != "null":
            policy_params = {
                k: v
                for k, v in composed_policy.items()
                if k != "name"
            }
            policy = build_policy(policy_name, **policy_params)
            policy_actions = policy_params.get("actions")
            if policy_actions is None and "action" in policy_params:
                policy_actions = [policy_params.get("action")]
            return policy, policy_actions
        return NullPolicy(), None

    if isinstance(policy_config, dict):
        policy_name = policy_config.get("name")
        if policy_name == "null":
            return NullPolicy(), None
        policy_params = policy_config.get("params", {})
        policy = build_policy(policy_name, **policy_params)
        policy_actions = policy_params.get("actions")
        if policy_actions is None and "action" in policy_params:
            policy_actions = [policy_params.get("action")]
        return policy, policy_actions

    if isinstance(policy_config, str):
        if policy_config == "null":
            return NullPolicy(), None
        return build_policy(policy_config), None

    return NullPolicy(), None


def _build_agent_stack(config, representation):
    policy, policy_actions = _build_policy_from_config(config)
    learner_params = _extract_learner_params(config, representation, policy_actions)
    learner_params.setdefault("prediction_error_rule", _build_prediction_error_rule(config))
    learner_params.setdefault("attention_mechanism", _build_attention_mechanism_object(config))
    learner = build_learner(
        _resolve_learner_name(config),
        state_dim=representation.dimension,
        **learner_params,
    )
    _assign_attention_map(config, learner)

    agent = build_agent(
        config.agent,
        learner=learner,
        representation=representation,
        policy=policy,
    )
    return agent


# Phase vs protocol routing helper
def _is_protocol_phase(protocol_name: str) -> bool:
    """
    Return True if a name refers to a protocol (multi-phase behavior).
    """
    return protocol_name in PROTOCOL_REGISTRY


def _is_atomic_phase(protocol_name: str) -> bool:
    """
    Return True if a name refers to a phase.
    """
    return not _is_protocol_phase(protocol_name)


# Assembly pipeline: build representation -> policy (optional) -> learner -> agent -> runtime units.
def _plan_to_config(plan: ExperimentPlan):
    settings = plan.settings or {}
    program_spec = plan.program_spec or {}
    agent_spec = plan.agent_spec or {}
    runtime_spec = plan.runtime_spec or {}
    phases = []
    phase_source = program_spec.get("phases") if isinstance(program_spec.get("phases"), list) else plan.units
    for i, unit in enumerate(phase_source):
        if isinstance(unit, PhaseConfig):
            phases.append(unit)
            continue
        if not isinstance(unit, dict):
            raise TypeError(
                f"ExperimentPlan.units[{i}] must be dict or PhaseConfig, got {type(unit).__name__}."
            )
        phases.append(
            PhaseConfig(
                name=unit.get("name", f"Phase {i}"),
                protocol=unit["protocol"],
                stimuli=unit.get("stimuli"),
                params=unit.get("params") or {},
            )
        )

    return SimpleNamespace(
        learner=(
            ((agent_spec.get("learning") or {}).get("rule"))
            if isinstance(agent_spec.get("learning"), dict)
            else settings["learner"]
        ),
        agent=agent_spec.get("agent", settings["agent"]),
        representation=agent_spec.get("representation", settings["representation"]),
        policy=agent_spec.get("policy", settings.get("policy")),
        representation_config=agent_spec.get("representation", settings["representation"]),
        learning_config=agent_spec.get("learning", {"rule": settings["learner"], "params": {}}),
        policy_config=agent_spec.get("policy", settings.get("policy")),
        stimuli=agent_spec.get("stimuli", settings.get("stimuli", [])),
        salience=agent_spec.get("salience", settings.get("salience", {})),
        attention=agent_spec.get("attention", settings.get("attention", {})),
        context_inference=runtime_spec.get("context_inference", settings.get("context_inference", {})),
        attention_config=agent_spec.get("attention_config", settings.get("attention_config", {})),
        phases=phases,
        composed_parameters=runtime_spec.get("composed_parameters", settings.get("composed_parameters", {})),
        resolved_plan=bool(runtime_spec.get("resolved_plan", settings.get("resolved_plan", False))),
        resolved_phase_contexts=list(program_spec.get("resolved_phase_contexts", settings.get("resolved_phase_contexts", []))),
    )


@dataclass
class AgentAssembler:
    config: Any

    def build_representation_and_contexts(self):
        composed_rep = _get_composed_representation(self.config)
        composed_context = composed_rep.get("context", {}) if isinstance(composed_rep.get("context"), dict) else {}
        composed_salience = composed_rep.get("salience", {}) if isinstance(composed_rep.get("salience"), dict) else {}
        composed_similarity = composed_rep.get("similarity", {}) if isinstance(composed_rep.get("similarity"), dict) else {}

        rep = self.config.representation
        if isinstance(rep, dict):
            rep_name = rep.get("name")
            rep_params = rep.get("params", {}).copy()
        else:
            rep_name = rep
            rep_params = {}

        if getattr(self.config, "stimuli", None):
            rep_params.setdefault("stimuli", self.config.stimuli)

        if getattr(self.config, "salience", None):
            rep_params.setdefault("salience", self.config.salience)
        if "salience" not in rep_params and isinstance(composed_salience.get("overrides"), dict):
            rep_params["salience"] = dict(composed_salience.get("overrides", {}))
        if "contexts" not in rep_params and isinstance(composed_context.get("contexts"), list):
            rep_params["contexts"] = list(composed_context.get("contexts", []))
        if "similarity" not in rep_params and composed_similarity.get("enabled") and isinstance(composed_similarity.get("matrix"), dict):
            rep_stimuli = rep_params.get("stimuli", [])
            rep_stimuli = [str(s) for s in rep_stimuli] if isinstance(rep_stimuli, list) else []
            typed_similarity = _typed_similarity_to_matrix(composed_similarity["matrix"], rep_stimuli)
            if typed_similarity:
                rep_params["similarity"] = typed_similarity
        rep_params.setdefault("context_map", _build_context_map(self.config, rep_params))
        similarity_kernel = _build_similarity_kernel(self.config, rep_params)
        if similarity_kernel is not None:
            rep_params.setdefault("similarity_kernel", similarity_kernel)
        rep_params.setdefault("temporal_basis_object", _build_temporal_basis_object(self.config))

        resolved_plan = bool(getattr(self.config, "resolved_plan", False))
        if resolved_plan:
            inferred_contexts = list(getattr(self.config, "resolved_phase_contexts", []) or [])
        else:
            rep_params = _infer_contexts(rep_params, self.config)
            inferred_contexts = _infer_phase_contexts(self.config)
            if any(label is not None for label in inferred_contexts):
                contexts = set(rep_params.get("contexts", []))
                contexts.update(label for label in inferred_contexts if label is not None)
                rep_params["contexts"] = sorted(contexts)

        representation = build_representation(rep_name, **rep_params)
        if getattr(representation, "salience_operator", None) is None:
            representation.salience_operator = _build_salience_operator_for_representation(representation)
        return representation, inferred_contexts

    def build_agent(self, representation):
        return _build_agent_stack(self.config, representation)


@dataclass
class UnitAssembler:
    config: Any

    @staticmethod
    def _apply_typed_unit_defaults(params: dict[str, Any], typed_unit: dict[str, Any] | None) -> dict[str, Any]:
        if not isinstance(typed_unit, dict):
            return params

        typed_context = typed_unit.get("context_id")
        if typed_context and not params.get("context"):
            params["context"] = typed_context

        typed_trials = typed_unit.get("n_trials")
        if "n_trials" not in params and typed_trials is not None:
            params["n_trials"] = typed_trials

        typed_time = typed_unit.get("time")
        if isinstance(typed_time, dict):
            if "duration_s" not in params and typed_time.get("duration_s") is not None:
                params["duration_s"] = typed_time["duration_s"]
            if "dt_s" not in params and typed_time.get("dt_s") is not None:
                params["dt_s"] = typed_time["dt_s"]
            if "iti_s" not in params and typed_time.get("iti_s") is not None:
                params["iti_s"] = typed_time["iti_s"]
            if (
                "allow_partial_last_step" not in params
                and typed_time.get("allow_partial_last_step") is not None
            ):
                params["allow_partial_last_step"] = typed_time["allow_partial_last_step"]

        typed_contingency = typed_unit.get("contingency")
        if isinstance(typed_contingency, dict):
            for key, value in typed_contingency.items():
                params.setdefault(key, value)

        typed_schedule = typed_unit.get("schedule_runtime")
        if isinstance(typed_schedule, dict) and "schedule_runtime" not in params:
            params["schedule_runtime"] = typed_schedule

        typed_learning = typed_unit.get("learning_gate")
        if isinstance(typed_learning, dict) and "learning_enabled" not in params:
            if "enabled" in typed_learning:
                params["learning_enabled"] = bool(typed_learning["enabled"])

        return params

    def build_units(self, *, agent, inferred_contexts):
        runtime_units = []
        typed_units = _get_composed_units(self.config)
        for i, phase in enumerate(self.config.phases):
            params = phase.params.copy()
            typed_unit = typed_units[i] if i < len(typed_units) else None
            params = self._apply_typed_unit_defaults(params, typed_unit)

            if "reward_schedule" in params:
                params["reward_schedule"] = build_reward_schedule(params["reward_schedule"])

            if _is_protocol_phase(phase.protocol):
                unit = build_protocol(
                    phase.protocol,
                    agent=agent,
                    stimuli=phase.stimuli,
                    params=params,
                )
            else:
                unit = build_phase(
                    phase.protocol,
                    agent=agent,
                    stimuli=phase.stimuli,
                    **params,
                )

            inferred_context = inferred_contexts[i] if i < len(inferred_contexts) else None
            if inferred_context and not _has_explicit_unit_context(phase, typed_unit):
                if hasattr(unit, "context"):
                    unit.context = inferred_context
                unit.context_source = "inferred"

            runtime_units.append(unit)
        return runtime_units


@dataclass
class ExperimentAssembler:
    config: Any

    def assemble(self):
        agent_assembler = AgentAssembler(self.config)
        representation, inferred_contexts = agent_assembler.build_representation_and_contexts()
        agent = agent_assembler.build_agent(representation)
        units = UnitAssembler(self.config).build_units(agent=agent, inferred_contexts=inferred_contexts)
        return units, agent, representation


def _assemble_from_config(config):
    """
    Assemble runtime objects from an ExperimentConfig.

    Returns:
        runtime_units: list of phase/protocol instances in execution order
        agent: shared agent instance
        representation: shared representation instance
    """
    return ExperimentAssembler(config).assemble()


def assemble_experiment(config):
    """
    Assemble runtime objects from an ExperimentConfig or ExperimentPlan.
    """
    if isinstance(config, ExperimentPlan):
        config = _plan_to_config(config)
    composed = _get_composed_parameters(config)
    if composed:
        validate_composed_parameter_ownership(composed)
    return _assemble_from_config(config)
