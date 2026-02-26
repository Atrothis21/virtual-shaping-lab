# experiment/phases/learning_helpers.py

from typing import Any, Optional

from virtual_shaping_lab.domain.types import Transition


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
            agent.learn(transition)
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
        agent.learn(transition)
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
    agent.learn(transition)
