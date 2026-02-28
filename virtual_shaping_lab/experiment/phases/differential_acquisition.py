# experiment/phases/differential_acquisition.py

import random
from typing import Any, Dict, List

import numpy as np

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from experiment.phases.series_helpers import make_dual_series
from virtual_shaping_lab.agents.representations.observation import make_observation
from virtual_shaping_lab.domain.types import Observation
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult, TrialSchedule


class DifferentialAcquisitionPhase(PhaseBase):
    """
    Differential conditioning phase.

    CS+ trials are reinforced.
    CS- trials are not reinforced.

    Learning occurs for both stimulus types within a single phase.
    """

    name = "differential_acquisition"
    allows_learning = True
    requires_prior_learning = False

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]],
        n_trials: int,
        reinforced_outcome: float = 1.0,
        params: Dict[str, Any] | None = None,
    ):
        """
        Parameters
        ----------
        agent :
            Learning agent.
        stimuli :
            Dict with keys {"cs_plus", "cs_minus"} mapping to stimulus lists.
        n_trials :
            Total number of trials.
        reinforced_outcome :
            Reward magnitude for CS+ trials.
        """
        # Enforce dict-only stimuli
        if not isinstance(stimuli, dict):
            raise ValueError(
                "DifferentialAcquisitionPhase expects stimuli as a dict "
                "with keys {'cs_plus', 'cs_minus'}"
            )

        if not {"cs_plus", "cs_minus"} <= stimuli.keys():
            raise ValueError(
                "DifferentialAcquisitionPhase requires "
                "stimuli with keys {'cs_plus', 'cs_minus'}"
            )

        if not stimuli["cs_plus"] or not stimuli["cs_minus"]:
            raise ValueError(
                "DifferentialAcquisitionPhase requires non-empty cs_plus and cs_minus lists"
            )

        super().__init__(agent, stimuli=[], n_trials=n_trials, params=params)

        self.stimuli_by_type = stimuli
        self.reinforced_outcome = reinforced_outcome

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        """
        Alternate CS+ and CS- deterministically.
        """
        stimulus_type = "cs_plus" if self.trial_index % 2 == 0 else "cs_minus"
        stimulus = random.choice(self.stimuli_by_type[stimulus_type])

        return {
            "stimulus": stimulus,
            "stimulus_type": stimulus_type,
        }

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        stimulus = trial_spec["stimulus"]
        stimulus_type = trial_spec["stimulus_type"]

        obs = make_observation(
            stimuli=[stimulus],
            context=self.context,
            compound=False
        )
        state = self.agent.observe(obs)
        prediction = self.agent.value(state)
        action = self.select_action(state, trial_spec)

        reward = self.reinforced_outcome if stimulus_type == "cs_plus" else 0.0

        return {
            "stimulus": stimulus,
            "stimulus_type": stimulus_type,
            "action": action,
            "reward": reward,
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

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        cs_plus_val = outcome["prediction"] if outcome["stimulus_type"] == "cs_plus" else None
        cs_minus_val = outcome["prediction"] if outcome["stimulus_type"] == "cs_minus" else None

        series = make_dual_series(
            "CS+", cs_plus_val,
            "CS-", cs_minus_val,
        )

        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": outcome["stimulus"],
            "stimulus_type": outcome["stimulus_type"],
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
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
            observation = Observation(
                stimuli=[stimulus] if stimulus is not None else [],
                context=record.get("context", self.context),
            )
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



