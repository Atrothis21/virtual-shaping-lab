# experiment/phases/learning_helpers.py

from typing import Any, Optional

from virtual_shaping_lab.domain.types import Transition


def _dispatch_transition(agent: Any, transition: Transition) -> None:
    # Preferred v2 path.
    if hasattr(agent, "learn"):
        agent.learn(transition)
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
    Build a Transition and delegate learning via a single update pathway.
    Attention is handled inside the learner from transition metadata.
    """
    transition = Transition(
        s=state,
        r=reward,
        a=action,
        s_next=next_state,
        done=done,
        t_s=t_s,
        dt_s=dt_s,
        metadata={"cue_labels": cue_labels},
    )
    _dispatch_transition(agent, transition)

