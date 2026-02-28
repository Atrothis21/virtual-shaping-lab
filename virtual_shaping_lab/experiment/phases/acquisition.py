# experiment/phases/acquisition.py

from typing import Any, Dict, List

import numpy as np

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from virtual_shaping_lab.agents.representations.observation import make_observation
from virtual_shaping_lab.domain.types import Observation
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult, TrialSchedule, TrialTimeSpec


class AcquisitionPhase(PhaseBase):
    """
    Reinforcement phase.

    A stimulus or action predicts an outcome (US / reward).
    This phase builds associative strength.
    """

    name = "acquisition"
    allows_learning = True
    requires_prior_learning = False

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]],
        n_trials: int,
        params: Dict[str, Any] | None = None,
    ):
        """
        Parameters
        ----------
        agent :
            Learning agent.
        stimuli :
            Dict with cs_plus/cs_minus.
        n_trials :
            Number of trials.
        params :
            Phase-specific settings (single source of truth).
            Advanced: outcome (US magnitude).
        """
        if not isinstance(stimuli, dict):
            raise ValueError("AcquisitionPhase expects stimuli as a dict with cs_plus/cs_minus.")

        cs_plus = stimuli.get("cs_plus", [])
        if not isinstance(cs_plus, list) or len(cs_plus) == 0:
            raise ValueError("AcquisitionPhase requires stimuli['cs_plus'] to be a non-empty list.")

        # Only train on cs_plus
        stimuli = cs_plus

        super().__init__(agent, stimuli, n_trials, params)

        # Advanced parameter: reinforcement magnitude (US)
        self.outcome = self.params.get("outcome", 1.0)

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        """
        Sample a single stimulus for the trial.
        """
        stimulus = self.stimuli[0] if len(self.stimuli) == 1 else self.stimuli[
            self.trial_index % len(self.stimuli)
        ]

        return {
            "stimulus": stimulus,
        }

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        """
        Deliver reinforcement.
        """
        stimulus = trial_spec["stimulus"]

        if isinstance(stimulus, tuple):
            obs = make_observation(
                stimuli=list(stimulus),
                context=self.context,
                compound=True
            )
        else:
            obs = make_observation(
                stimuli=[stimulus],
                context=self.context,
                compound=False
            )

        state = self.agent.observe(obs)
        prediction = self.agent.value(state)

        action = self.select_action(state, trial_spec)

        return {
            "stimulus": stimulus,
            "action": action,
            "reward": self.outcome,
            "state": state,
            "prediction": prediction,
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        Apply learning via the agent.
        """
        apply_attention_update(
            self.agent,
            outcome["state"],
            outcome["reward"],
            outcome.get("action"),
            cue_labels=outcome.get("stimulus"),
        )

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        """
        Record acquisition trial.
        """
        stimulus = outcome["stimulus"]
        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": stimulus,
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
            "a_stimulus": stimulus,
            "b_stimulus": None,
            "series_labels": {"label_1": "CS1", "label_2": "CS2"},
            "series_values": {"CS1": outcome["prediction"], "CS2": None},
        }

    # ------------------------------------------------------------------
    # v2.1 runnable-unit hooks
    # ------------------------------------------------------------------

    def reset(self, ctx: ExperimentContext) -> None:
        self.trial_index = 0
        self.records = []
        if self.params.get("rng_seed") is None:
            self._rng = ctx.rng
        else:
            self._rng = np.random.default_rng(self.params.get("rng_seed"))

    def iter_steps(self, ctx: ExperimentContext):
        if self.trial_index != 0:
            self.reset(ctx)
        while self.has_next_trial():
            record = self.step()
            if record is None:
                continue
            stimulus = record.get("stimulus")
            stimuli = list(stimulus) if isinstance(stimulus, tuple) else ([stimulus] if stimulus is not None else [])
            observation = Observation(stimuli=stimuli, context=record.get("context", self.context))
            metadata = {"record": record}
            trial_schedule = self.build_trial_schedule(ctx, int(record.get("trial", self.trial_index)))
            if trial_schedule is not None:
                metadata["trial_schedule"] = trial_schedule
            yield StepResult(
                observation=observation,
                reward=float(record.get("reward", 0.0)),
                learning_enabled=self.allows_learning,
                done=not self.has_next_trial(),
                metadata=metadata,
            )

    def build_trial_schedule(
        self,
        ctx: ExperimentContext,
        trial_index: int,
    ) -> TrialSchedule | None:
        spec = self.params.get("trial_time_spec")
        if not isinstance(spec, TrialTimeSpec):
            return None
        return TrialSchedule(
            time=spec,
            base_stimuli=[],
            available_actions=list(self.get_available_actions()),
        )



