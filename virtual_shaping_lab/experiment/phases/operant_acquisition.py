# experiment/phases/operant_acquisition.py

from typing import Any, Dict, List

import numpy as np

from experiment.phases.base import PhaseBase
from experiment.phases.learning_helpers import apply_attention_update
from virtual_shaping_lab.agents.representations.observation import make_observation
from virtual_shaping_lab.domain.types import Observation
from virtual_shaping_lab.experiment.domain.types import ExperimentContext, StepResult, TrialSchedule


def _classify_operant_outcome(reward: float) -> str:
    if reward > 0:
        return "reinforcement"
    if reward < 0:
        return "punishment"
    return "extinction"


class OperantAcquisitionPhase(PhaseBase):
    """
    Operant acquisition phase.

    Reinforcement is delivered according to a reward schedule
    contingent on the agent's emitted actions.
    """

    name = "operant_acquisition"
    allows_learning = True
    requires_prior_learning = False

    @staticmethod
    def _reset_reward_schedule(schedule, rng) -> None:
        reset = getattr(schedule, "reset", None)
        if reset is None:
            return
        try:
            reset(rng)
        except TypeError:
            reset()

    def __init__(
        self,
        agent,
        stimuli: Dict[str, List[Any]] | List[Any],
        n_trials: int,
        reward_schedule,
        params: Dict[str, Any] | None = None,
    ):
        # Normalize stimuli if provided as dict
        if isinstance(stimuli, dict):
            cs_plus = stimuli.get("cs_plus", [])
            stimuli = cs_plus if isinstance(cs_plus, list) else []
        elif stimuli is None:
            stimuli = []

        super().__init__(
            agent=agent,
            stimuli=stimuli,
            n_trials=n_trials,
            params=params,
        )

        self.reward_schedule = reward_schedule

        self._reset_reward_schedule(self.reward_schedule, self._rng)

        if hasattr(self.agent, "reset"):
            self.agent.reset()

    # ------------------------------------------------------------------
    # Trial definition
    # ------------------------------------------------------------------

    def _default_observation_label(self) -> str:
        if isinstance(self.stimuli, list) and self.stimuli:
            return str(self.stimuli[0])
        rep = getattr(self.agent, "representation", None)
        rep_params = getattr(rep, "params", {}) if rep is not None else {}
        rep_stimuli = rep_params.get("stimuli") if isinstance(rep_params, dict) else None
        if isinstance(rep_stimuli, list) and rep_stimuli:
            return str(rep_stimuli[0])
        return "lever"

    def sample_trial(self) -> Dict[str, Any]:
        """
        Operant trials do not require stimulus sampling.
        """
        return {}

    def run_trial(self, trial_spec: Dict[str, Any]) -> Any:
        """
        Select action and compute reward from schedule.
        """
        observation = self._default_observation_label()
        obs = make_observation(
            stimuli=[observation],
            context=self.context,
            compound=False
        )
        state = self.agent.observe(obs)
        prediction = self.agent.value(state)
        action = self.select_action(state, trial_spec)

        reward = float(self.reward_schedule.step(
            action=action,
            t=self.trial_index,
        ))

        return {
            "action": action,
            "reward": reward,
            "outcome_type": _classify_operant_outcome(reward),
            "state": state,
            "prediction": prediction,
        }

    def apply_learning(self, trial_spec: Dict[str, Any], outcome: Any) -> None:
        """
        In operant learning, the action itself serves as the learning state.
        """
        apply_attention_update(
            self.agent,
            outcome["state"],
            outcome["reward"],
            outcome.get("action")
        )

    def record_trial(
        self,
        trial_spec: Dict[str, Any],
        outcome: Any,
    ) -> Dict[str, Any]:
        """
        Record operant trial.
        """
        return {
            "phase": self.name,
            "trial": self.trial_index,
            "stimulus": None,
            "action": outcome["action"],
            "response": outcome["action"] if outcome["action"] is not None else outcome["prediction"],
            "reward": outcome["reward"],
            "outcome_type": outcome.get("outcome_type", _classify_operant_outcome(float(outcome["reward"]))),
            "consequence_mode": self.params.get("consequence_mode"),
            "prediction": outcome["prediction"],
            "schedule": getattr(self.reward_schedule, "name", None),
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
        self._reset_reward_schedule(self.reward_schedule, self._rng)

    def iter_steps(self, ctx: ExperimentContext):
        if self.trial_index != 0:
            self.reset(ctx)
        while self.has_next_trial():
            record = self.step()
            if record is None:
                continue
            observation = Observation(stimuli=[], context=record.get("context", self.context))
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
        metadata: dict[str, Any] = {}
        if hasattr(self.reward_schedule, "build_tick_runtime"):
            runtime = self.reward_schedule.build_tick_runtime(spec)
            if runtime is not None:
                metadata["schedule_runtime"] = runtime
        return TrialSchedule(
            time=spec,
            base_stimuli=[],
            available_actions=list(self.get_available_actions()),
            metadata=metadata,
        )



