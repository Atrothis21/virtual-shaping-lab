# experiment/assemble.py

from experiment.factories.learner_factory import build_learner
from experiment.factories.agent_factory import build_agent
from experiment.factories.protocol_factory import build_protocol, PROTOCOL_REGISTRY
from experiment.factories.phase_factory import build_phase
from experiment.factories.representation_factory import build_representation
from experiment.factories.reward_schedule_factory import build_reward_schedule
from experiment.factories.policy_factory import build_policy


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

    if config.phases:
        first_params = config.phases[0].params
        if "alpha" in first_params:
            learner_params["alpha"] = first_params["alpha"]
        if "gamma" in first_params:
            learner_params["gamma"] = first_params["gamma"]

    if policy_actions:
        learner_params.setdefault("actions", policy_actions)

    return learner_params


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
def assemble_experiment(config):
    """
    Assemble runtime objects from an ExperimentConfig.

    Returns:
        runtime_units: list of phase/protocol instances in execution order
        agent: shared agent instance
        representation: shared representation instance
    """

    # ----------------------------
    # Representation (shared)
    # ----------------------------
    rep = config.representation
    if isinstance(rep, dict):
        rep_name = rep.get("name")
        rep_params = rep.get("params", {}).copy()
    else:
        rep_name = rep
        rep_params = {}

    if getattr(config, "stimuli", None):
        rep_params.setdefault("stimuli", config.stimuli)

    if getattr(config, "salience", None):
        rep_params.setdefault("salience", config.salience)

    rep_params = _infer_contexts(rep_params, config)

    representation = build_representation(rep_name, **rep_params)

    # ----------------------------
    # Policy (optional, shared)
    # ----------------------------
    policy = None
    policy_actions = None

    if hasattr(config, "policy") and config.policy:
        if isinstance(config.policy, dict):
            policy_name = config.policy.get("name")
            policy_params = config.policy.get("params", {})
            policy = build_policy(policy_name, **policy_params)
            policy_actions = policy_params.get("actions")
        elif isinstance(config.policy, str):
            policy = build_policy(config.policy)

    # ----------------------------
    # Learner (shared)
    # ----------------------------
    learner_params = _extract_learner_params(config, representation, policy_actions)

    learner = build_learner(
        config.learner,
        state_dim=representation.dimension,
        **learner_params,
    )
    if getattr(config, "attention", None):
        if hasattr(learner, "set_attention_map"):
            learner.set_attention_map(config.attention)
        else:
            learner.attention_map = dict(config.attention)

    # ----------------------------
    # Agent (shared)
    # ----------------------------
    agent = build_agent(
        config.agent,
        learner=learner,
        representation=representation,
        policy=policy,
    )

    # ----------------------------
    # Runtime units
    # - Atomic phases via phase_factory
    # - Multi-phase protocols via protocol_factory
    # ----------------------------
    runtime_units = []

    inferred_contexts = _infer_phase_contexts(config)

    for i, phase in enumerate(config.phases):
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

        runtime_units.append(unit)

        inferred_context = inferred_contexts[i] if i < len(inferred_contexts) else None
        if inferred_context:
            if hasattr(unit, "context"):
                unit.context = inferred_context
            unit.context_source = "inferred"

    return runtime_units, agent, representation
