# experiment/phases/learning_helpers.py

from typing import Any, Optional


def apply_attention_update(
    agent: Any,
    state: Any,
    reward: float,
    action: Optional[int] = None,
) -> None:
    """
    Apply an attention-aware learning update if attention is present.
    Falls back to the agent's default update otherwise.
    """
    attention = getattr(getattr(agent, "representation", None), "attention", None)
    if attention is not None:
        base_alpha = getattr(getattr(agent, "learner", None), "alpha", 1.0) or 1.0
        alpha_override = attention * base_alpha
        agent.update_with_alpha(
            state,
            reward,
            action=action,
            alpha_override=alpha_override,
        )
        return

    agent.update(state, reward, action)
