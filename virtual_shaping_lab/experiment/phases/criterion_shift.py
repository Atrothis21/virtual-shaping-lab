# experiment/phases/criterion_shift.py

from collections import deque
from typing import Any, Dict, List, Optional

import numpy as np

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from virtual_shaping_lab.domain.types import Observation
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult, TrialSchedule


class CriterionShiftPhase(PhaseBase):
    """
    Criterion shift phase.

    Reuses the same task structure as acquisition but ends early when a
    performance criterion is reached. Learning proceeds normally.

    Supported criteria (v1):
      - prediction_threshold
    """

    name = "criterion_shift"
    allows_learning = True
    requires_prior_learning = True

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]],
        n_trials: int,
        outcome: float = 1.0,
        params: Optional[Dict[str, Any]] = None,
    ):
        # Enforce dict-only stimuli
        if not isinstance(stimuli, dict):
            raise ValueError("CriterionShiftPhase expects stimuli as a dict with cs_plus/cs_minus.")

        cs_plus = stimuli.get("cs_plus", [])
        if not isinstance(cs_plus, list) or len(cs_plus) == 0:
            raise ValueError("CriterionShiftPhase requires stimuli['cs_plus'] to be a non-empty list.")

        # Only train on cs_plus
        stimuli = cs_plus

        super().__init__(agent, stimuli, n_trials, params)

        self.outcome = outcome

        # Criterion configuration
        criterion = (self.params or {}).get("criterion", {}) or {}
        self.criterion_type = criterion.get("type", "prediction_threshold")
        self.threshold = float(criterion.get("threshold", 0.8))
        self.window = int(criterion.get("window", 10))

        # Safety cap to prevent infinite loops
        self.safety_cap = self.params.get("safety_cap", None)

        # Phase-local tracking
        self.criterion_met = False
        self.trials_to_criterion = None
        self._prediction_window = deque(maxlen=max(self.window, 1))

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    def has_next_trial(self) -> bool:
        if self.criterion_met:
            return False
        if self.safety_cap is not None and self.trial_index >= self.safety_cap:
            return False
        return super().has_next_trial()

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        stimulus = self.stimuli[0] if len(self.stimuli) == 1 else self.stimuli[
            self.trial_index % len(self.stimuli)
        ]

        return {"stimulus": stimulus}

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        stimulus = trial_spec["stimulus"]

        if isinstance(stimulus, tuple):
            obs = Observation(
                stimuli=list(stimulus),
                context=self.context if self.context is not None else "A",
                compound=True,
            )
        else:
            obs = Observation(
                stimuli=[stimulus],
                context=self.context if self.context is not None else "A",
                compound=False,
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
        apply_attention_update(
            self.agent,
            outcome["state"],
            outcome["reward"],
            outcome.get("action"),
            cue_labels=outcome.get("stimulus"),
        )

    # ------------------------------------------------------------------
    # Criterion tracking
    # ------------------------------------------------------------------

    def _update_criterion(self, prediction: float) -> Dict[str, Any]:
        self._prediction_window.append(float(prediction))
        current_mean = sum(self._prediction_window) / len(self._prediction_window)

        met = current_mean >= self.threshold

        if met and not self.criterion_met:
            self.criterion_met = True
            self.trials_to_criterion = self.trial_index + 1

        return {
            "criterion_type": self.criterion_type,
            "criterion_value": current_mean,
            "criterion_threshold": self.threshold,
            "criterion_met": self.criterion_met,
            "trials_to_criterion": self.trials_to_criterion,
            "criterion_window": self.window,
        }

    def record_trial(self, trial_spec: Dict[str, Any], outcome: Any) -> Dict[str, Any]:
        crit = self._update_criterion(outcome["prediction"])

        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": outcome["stimulus"],
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
            **crit,
        }

    # ------------------------------------------------------------------
    # v2.2 runnable-unit hooks
    # ------------------------------------------------------------------

    def reset(self, ctx: ExperimentContext) -> None:
        self.trial_index = 0
        self.records = []
        self.criterion_met = False
        self.trials_to_criterion = None
        self._prediction_window.clear()
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



