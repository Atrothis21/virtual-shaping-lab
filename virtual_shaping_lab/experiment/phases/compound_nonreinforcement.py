# experiment/phases/compound_nonreinforcement.py

from typing import Any, Dict, List

import numpy as np

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from experiment.phases.series_helpers import make_dual_series
from virtual_shaping_lab.domain.types import Observation
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult, TrialSchedule


class CompoundNonReinforcementPhase(PhaseBase):
    """
    Compound nonreinforcement phase.

    A compound stimulus (e.g., A + X) predicts omission of an expected outcome.
    This is the canonical conditioned inhibition training structure.

        Prior: A -> US
        This phase: AX -> no US
    """

    name = "compound_nonreinforcement"
    allows_learning = True
    requires_prior_learning = True

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
            Dict with key {"compound"} mapping to a list of 2 stimuli.
            Example: {"compound": [A, X]}
        n_trials :
            Number of compound nonreinforcement trials.
        """
        # Enforce dict-only stimuli with compound key
        if not isinstance(stimuli, dict):
            raise ValueError("CompoundNonReinforcementPhase expects stimuli as a dict with key 'compound'.")

        compound = stimuli.get("compound", [])
        if not isinstance(compound, list) or len(compound) < 2:
            raise ValueError("CompoundNonReinforcementPhase requires stimuli['compound'] with at least two items.")

        super().__init__(
            agent=agent,
            stimuli=compound,
            n_trials=n_trials,
            params=params,
        )

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
        Present compound stimulus and omit reinforcement.
        """
        compound = trial_spec["compound"]
        excitor = compound[0]
        inhibitor = compound[1]

        # Observe compound (actual trial)
        obs = Observation(
            stimuli=[excitor, inhibitor],
            context=self.context if self.context is not None else "A",
            compound=True,
        )
        state = self.agent.observe(obs)

        prediction = self.agent.value(state)
        action = self.select_action(state, trial_spec)

        # Compute excitor-only prediction without mutating agent state
        obs_a = Observation(
            stimuli=[excitor],
            context=self.context if self.context is not None else "A",
            compound=False,
        )
        state_a = self.agent.representation.encode(obs_a)
        excitor_prediction = self.agent.value(state_a)

        # Compute inhibitor-only prediction without mutating agent state
        obs_b = Observation(
            stimuli=[inhibitor],
            context=self.context if self.context is not None else "A",
            compound=False,
        )
        state_b = self.agent.representation.encode(obs_b)
        inhibitor_prediction = self.agent.value(state_b)

        return {
            "excitor": excitor,
            "inhibitor": inhibitor,
            "compound": (excitor, inhibitor),
            "action": action,
            "reward": 0.0,
            "state": state,
            "prediction": prediction,
            "excitor_prediction": excitor_prediction,
            "inhibitor_prediction": inhibitor_prediction,
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        Apply learning from outcome omission.
        """
        apply_attention_update(
            self.agent,
            outcome["state"],
            outcome["reward"],
            outcome.get("action"),
            cue_labels=list(outcome.get("compound", [])),
        )

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        """
        Record compound nonreinforcement trial.
        """
        series = make_dual_series(
            outcome["excitor"], outcome.get("excitor_prediction"),
            outcome["inhibitor"], outcome.get("inhibitor_prediction"),
        )

        return {
            "phase": self.name,
            "trial": self.trial_index,
            "excitor": outcome["excitor"],
            "inhibitor": outcome["inhibitor"],
            "compound": outcome["compound"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
            "excitor_prediction": outcome.get("excitor_prediction"),
            "inhibitor_prediction": outcome.get("inhibitor_prediction"),
            "stimulus": outcome["compound"],
            **series,
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




