# experiment/phases/compound_acquisition.py

from typing import Any, Dict, List

import numpy as np

from experiment.phases.base import PhaseBase
from experiment.phases.series_helpers import make_dual_series
from virtual_shaping_lab.agents.representations.observation import make_observation
from virtual_shaping_lab.domain.types import META_CUE_LABELS, Observation, Transition
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult, TrialSchedule


class CompoundAcquisitionPhase(PhaseBase):
    """
    Compound acquisition phase.

    A compound stimulus (e.g., A + B) predicts reinforcement.
    This phase supports overshadowing, blocking, and summation effects
    depending on prior phase history.
    """

    name = "compound_acquisition"
    allows_learning = True
    requires_prior_learning = False

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]],
        n_trials: int,
        outcome: float = 1.0,
        params: Dict[str, Any] | None = None,
    ):
        """
        Parameters
        ----------
        agent :
            Learning agent.
        stimuli :
            Dict with key {"compound"} mapping to a list of 2 stimuli.
            Example: {"compound": [A, X]}
        n_trials :
            Number of compound acquisition trials.
        outcome :
            Reinforcement magnitude.
        """
        # Enforce dict-only stimuli with compound key
        if not isinstance(stimuli, dict):
            raise ValueError("CompoundAcquisitionPhase expects stimuli as a dict with key 'compound'.")

        compound = stimuli.get("compound", [])
        if not isinstance(compound, list) or len(compound) < 2:
            raise ValueError("CompoundAcquisitionPhase requires stimuli['compound'] with at least two items.")

        super().__init__(
            agent=agent,
            stimuli=compound,
            n_trials=n_trials,
            params=params,
        )

        self.outcome = outcome

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        """
        Present the full compound on every trial.
        """
        return {
            "compound": tuple(self.stimuli),
        }

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        """
        Present compound stimulus and deliver reinforcement.
        """
        compound = trial_spec["compound"]
        a = compound[0]
        b = compound[1]

        # Observe compound (actual trial)
        obs = make_observation(
            stimuli=list(compound),
            context=self.context,
            compound=True
        )
        state = self.agent.observe(obs)

        # Compute A/B predictions without mutating agent internal state
        obs_a = make_observation(
            stimuli=[a],
            context=self.context,
            compound=False
        )
        obs_b = make_observation(
            stimuli=[b],
            context=self.context,
            compound=False
        )

        state_a = self.agent.representation.encode(obs_a)
        state_b = self.agent.representation.encode(obs_b)

        a_prediction = self.agent.value(state_a)
        b_prediction = self.agent.value(state_b)

        prediction = self.agent.value(state)
        action = self.select_action(state, trial_spec)

        return {
            "compound": compound,
            "action": action,
            "reward": self.outcome,
            "state": state,
            "prediction": prediction,
            "a_prediction": a_prediction,
            "b_prediction": b_prediction,
            "a_stimulus": a,
            "b_stimulus": b,
            "state_a": state_a,
            "state_b": state_b,
            "prediction_by_stimulus": {
                a: a_prediction,
                b: b_prediction,
                "compound": prediction
            }
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        Apply cue-specific learning via transition metadata and learner-owned attention.
        """
        stim_a = outcome.get("a_stimulus")
        stim_b = outcome.get("b_stimulus")

        state_a = outcome.get("state_a")
        state_b = outcome.get("state_b")

        reward = outcome["reward"]
        action = outcome.get("action")

        self.agent.learn(Transition(s=state_a, r=reward, a=action, metadata={META_CUE_LABELS: [stim_a]}))
        self.agent.learn(Transition(s=state_b, r=reward, a=action, metadata={META_CUE_LABELS: [stim_b]}))

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        """
        Record compound acquisition trial.
        """
        series = make_dual_series(
            "CS1", outcome.get("a_prediction"),
            "CS2", outcome.get("b_prediction"),
        )

        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": outcome["compound"],
            "stimulus_type": "compound",
            "stimulus_components": list(outcome["compound"]),
            "compound": outcome["compound"],
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
            "a_prediction": outcome.get("a_prediction"),
            "b_prediction": outcome.get("b_prediction"),
            "a_stimulus": outcome.get("a_stimulus"),
            "b_stimulus": outcome.get("b_stimulus"),
            "prediction_by_stimulus": outcome.get("prediction_by_stimulus"),
            **series,
            "compound_series": {
                "label": "AX",
                "value": outcome.get("prediction")
            },
        }

    # ------------------------------------------------------------------
    # v2.2 runnable-unit hooks
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
        if spec is None or not hasattr(spec, "duration_s") or not hasattr(spec, "dt_s"):
            return None
        return TrialSchedule(
            time=spec,
            base_stimuli=[],
            available_actions=list(self.get_available_actions()),
        )





