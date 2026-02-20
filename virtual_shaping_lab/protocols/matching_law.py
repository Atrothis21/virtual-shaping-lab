# protocols/matching_law.py

from typing import Any, Dict, List

from protocols.base import BaseProtocol
from experiment.phases.concurrent_schedule import ConcurrentSchedulePhase


class MatchingLawProtocol(BaseProtocol):
    """
    Matching law protocol.

    Implements a concurrent schedule phase with two actions.
    All parameters are read from params.
    """

    name = "matching_law"

    def __init__(
        self,
        agent,
        stimuli: List[Any] | None = None,
        params: Dict[str, Any] | None = None,
        **_,
    ):
        self.agent = agent
        self.stimuli = stimuli or []
        self.params = params or {}

        super().__init__(
            agent=agent,
            stimuli=self.stimuli,
            n_trials=0,
            params=self.params,
        )

    def validate(self, history=None) -> None:
        learner = getattr(self.agent, "learner", None)
        learner_type = getattr(learner, "learner_type", None)
        if learner_type == "pavlovian":
            raise ValueError(
                "matching_law requires an operant learner "
                "(Rescorla-Wagner is not allowed)."
            )

    def build_phases(self):
        n_trials = self.params.get("n_trials", 200)
        schedule_left = self.params.get("schedule_left")
        schedule_right = self.params.get("schedule_right")
        action_labels = self.params.get("action_labels", ["left", "right"])

        phase = ConcurrentSchedulePhase(
            agent=self.agent,
            stimuli=self.stimuli,
            n_trials=n_trials,
            schedule_left=schedule_left,
            schedule_right=schedule_right,
            params={
                **self.params,
                "action_labels": action_labels,
            },
        )

        phase.validate(history=None)

        self.n_trials = n_trials
        return [phase]
