# experiment/assemble.py

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from experiment.factories.learner_factory import build_learner
from experiment.factories.agent_factory import build_agent
from experiment.factories.protocol_factory import build_protocol, PROTOCOL_REGISTRY
from experiment.factories.phase_factory import build_phase
from experiment.factories.representation_factory import build_representation
from experiment.factories.reward_schedule_factory import build_reward_schedule
from experiment.factories.policy_factory import build_policy
from experiment.config import PhaseConfig
from experiment.domain.types import ExperimentPlan

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


def _resolve_learner_name(config) -> str:
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


def _assign_attention_map(config, learner):
    attention_map = dict(getattr(config, "attention", None) or {})
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
    if not (hasattr(config, "policy") and config.policy):
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
        return None, None

    if isinstance(config.policy, dict):
        policy_name = config.policy.get("name")
        policy_params = config.policy.get("params", {})
        policy = build_policy(policy_name, **policy_params)
        policy_actions = policy_params.get("actions")
        if policy_actions is None and "action" in policy_params:
            policy_actions = [policy_params.get("action")]
        return policy, policy_actions

    if isinstance(config.policy, str):
        return build_policy(config.policy), None

    return None, None


def _build_classical_stack(config, representation):
    composed_policy = _get_composed_policy(config)
    if getattr(config, "policy", None):
        raise ValueError("Classical assembly path does not accept policy; use operant_agent for policy-driven runs.")
    if isinstance(composed_policy.get("name"), str) and composed_policy.get("name") not in {"", "null"}:
        raise ValueError("Classical assembly path does not accept policy; use operant_agent for policy-driven runs.")

    learner_params = _extract_learner_params(config, representation, policy_actions=None)
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
        policy=None,
    )
    return agent


def _build_operant_stack(config, representation):
    policy, policy_actions = _build_policy_from_config(config)
    if policy is None:
        raise ValueError("Operant assembly path requires an explicit policy.")

    learner_params = _extract_learner_params(config, representation, policy_actions)
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
    phases = []
    for i, unit in enumerate(plan.units):
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
        learner=settings["learner"],
        agent=settings["agent"],
        representation=settings["representation"],
        policy=settings.get("policy"),
        stimuli=settings.get("stimuli", []),
        salience=settings.get("salience", {}),
        attention=settings.get("attention", {}),
        context_inference=settings.get("context_inference", {}),
        phases=phases,
        composed_parameters=settings.get("composed_parameters", {}),
        resolved_plan=bool(settings.get("resolved_plan", False)),
        resolved_phase_contexts=list(settings.get("resolved_phase_contexts", [])),
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
        return representation, inferred_contexts

    def build_agent(self, representation):
        if self.config.agent == OPERANT_AGENT_NAME:
            return _build_operant_stack(self.config, representation)
        return _build_classical_stack(self.config, representation)


@dataclass
class UnitAssembler:
    config: Any

    def build_units(self, *, agent, inferred_contexts):
        runtime_units = []
        for i, phase in enumerate(self.config.phases):
            params = phase.params.copy()

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
            if inferred_context and not _has_explicit_phase_context(phase):
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
    return _assemble_from_config(config)
