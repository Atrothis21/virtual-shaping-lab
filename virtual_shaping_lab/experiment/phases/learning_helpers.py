# experiment/phases/learning_helpers.py

from typing import Any, Optional

from virtual_shaping_lab.domain.types import META_CUE_LABELS, META_EVENT_TYPE, Transition


def _dispatch_transition(agent: Any, transition: Transition) -> None:
    if hasattr(agent, "learn"):
        agent.learn(transition)
        return
    raise AttributeError(
        "Agent must implement learn(Transition). "
        "Legacy update-only dispatch path has been removed."
    )


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
    trial_step: int | None = None,
    trial_id: Any = None,
    event_type: str | None = None,
) -> None:
    """
    Build a Transition and delegate learning via a single update pathway.
    Attention is handled inside the learner from transition metadata.
    """
    metadata = {META_CUE_LABELS: cue_labels}
    if event_type is not None:
        metadata[META_EVENT_TYPE] = event_type

    transition = Transition(
        s=state,
        r=reward,
        a=action,
        s_next=next_state,
        done=done,
        t_s=t_s,
        dt_s=dt_s,
        trial_step=trial_step,
        trial_id=trial_id,
        metadata=metadata,
    )
    _dispatch_transition(agent, transition)

