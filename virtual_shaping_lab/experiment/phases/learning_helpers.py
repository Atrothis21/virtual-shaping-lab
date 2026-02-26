# experiment/phases/learning_helpers.py

from typing import Any, Optional

from virtual_shaping_lab.domain.types import Transition


def _dispatch_transition(agent: Any, transition: Transition) -> None:
    # Preferred v2 path.
    if hasattr(agent, "learn"):
        agent.learn(transition)
        return

    # Legacy fallback retained for old tests/doubles.
    metadata = transition.metadata or {}
    alpha_override = metadata.get("alpha_override")
    delta_override = metadata.get("delta_override")
    if alpha_override is not None or delta_override is not None:
        if hasattr(agent, "update_with_alpha"):
            agent.update_with_alpha(
                transition.s,
                transition.r,
                action=transition.a,
                alpha_override=alpha_override,
                delta_override=delta_override,
            )
            return

    if hasattr(agent, "update"):
        agent.update(transition.s, transition.r, transition.a)
        return

    raise AttributeError("Agent must implement learn(Transition) or legacy update methods.")


def apply_attention_update(
    agent: Any,
    state: Any,
    reward: float,
    action: Optional[int] = None,
    cue_labels: Any = None,
    next_state: Any = None,
    done: bool = False,
    t_s: float | None = None,
    dt_s: float | None = None,
) -> None:
    """
    Apply an attention-aware learning update if attention is present.
    Falls back to the agent's default update otherwise.
    """
    learner = getattr(agent, "learner", None)
    if learner is not None:
        if hasattr(learner, "attention_multiplier"):
            multiplier = float(learner.attention_multiplier(cue_labels))
        else:
            attention_map = getattr(learner, "attention_map", {}) or {}
            if isinstance(cue_labels, (list, tuple)) and cue_labels:
                values = [float(attention_map.get(str(c), 1.0)) for c in cue_labels]
                multiplier = sum(values) / len(values)
            elif cue_labels is not None:
                multiplier = float(attention_map.get(str(cue_labels), 1.0))
            else:
                multiplier = 1.0

        if multiplier != 1.0:
            base_alpha = getattr(learner, "alpha", 1.0) or 1.0
            alpha_override = multiplier * base_alpha
            transition = Transition(
                s=state,
                r=reward,
                a=action,
                s_next=next_state,
                done=done,
                t_s=t_s,
                dt_s=dt_s,
                metadata={"alpha_override": alpha_override},
            )
            _dispatch_transition(agent, transition)
            return

    # Legacy fallback for old representations carrying scalar attention.
    attention = getattr(getattr(agent, "representation", None), "attention", None)
    if attention is not None and not isinstance(attention, (list, tuple)):
        base_alpha = getattr(learner, "alpha", 1.0) if learner is not None else 1.0
        alpha_override = float(attention) * float(base_alpha or 1.0)
        transition = Transition(
            s=state,
            r=reward,
            a=action,
            s_next=next_state,
            done=done,
            t_s=t_s,
            dt_s=dt_s,
            metadata={"alpha_override": alpha_override},
        )
        _dispatch_transition(agent, transition)
        return

    transition = Transition(
        s=state,
        r=reward,
        a=action,
        s_next=next_state,
        done=done,
        t_s=t_s,
        dt_s=dt_s,
    )
    _dispatch_transition(agent, transition)
