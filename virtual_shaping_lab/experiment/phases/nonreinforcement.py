# experiment/phases/nonreinforcement.py

from typing import Any, Dict, List

import numpy as np

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from virtual_shaping_lab.agents.representations.observation import make_observation
from virtual_shaping_lab.domain.types import Observation
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult, TrialSchedule


class NonReinforcementPhase(PhaseBase):
    """
    Non-reinforcement / extinction phase.

    Expected outcomes are omitted.
    Learning is allowed by default (extinction),
    but this same phase can be used as a probe
    by setting allows_learning = False.
    """

    name = "nonreinforcement"
    allows_learning = True
    requires_prior_learning = True

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]],
        n_trials: int,
        params: Dict[str, Any] | None = None,
    ):
        params = params or {}

        # Enforce dict-only stimuli
        if not isinstance(stimuli, dict):
            raise ValueError("NonReinforcementPhase expects stimuli as a dict with cs_plus/cs_minus.")

        cs_plus = stimuli.get("cs_plus", [])
        if not isinstance(cs_plus, list) or len(cs_plus) == 0:
            raise ValueError("NonReinforcementPhase requires stimuli['cs_plus'] to be a non-empty list.")

        # Allow user to specify a target stimulus to extinguish
        target = params.get("target_stimulus")
        if target is None:
            target = cs_plus[0]

        # Reference stimuli (for plotting only, no learning)
        reference = params.get("reference_stimuli")
        if reference is None:
            if target in cs_plus:
                reference = [s for s in cs_plus if s != target]
            else:
                reference = list(cs_plus)

        self.target_stimulus = target
        self.reference_stimuli = list(reference)

        # Only extinguish the target stimulus
        stimuli = [self.target_stimulus]

        super().__init__(agent, stimuli, n_trials, params)

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def sample_trial(self) -> Dict[str, Any]:
        return {
            "stimulus": self.stimuli[0],
        }

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        """
        Omit reinforcement.
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
            "reward": 0.0,
            "state": state,
            "prediction": prediction,
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        Apply extinction learning (prediction error from omission).
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
        Record extinction / omission trial.
        Include reference stimuli predictions for plotting.
        """
        series_values = {self.target_stimulus: outcome["prediction"]}

        reference_stimuli = (
            getattr(self, "reference_stimuli", None)
            or self.params.get("reference_stimuli")
            or []
        )
        for ref in reference_stimuli:
            obs_ref = make_observation(
                stimuli=[ref],
                context=self.context,
                compound=False
            )
            ref_state = self.agent.representation.encode(obs_ref)
            ref_prediction = self.agent.value(ref_state)
            series_values[ref] = ref_prediction

        labels = {
            "label_1": self.target_stimulus,
            "label_2": reference_stimuli[0] if reference_stimuli else "CS2"
        }

        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": outcome["stimulus"],
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "prediction": outcome["prediction"],
            "series_labels": labels,
            "series_values": series_values,
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



