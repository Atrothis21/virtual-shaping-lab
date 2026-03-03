# experiment/factories/phase_factory.py

"""Phase factory.

Template-first policy:
- canonical classical keys resolve to template-backed builders
- legacy class-based canonical phases remain available via explicit *_legacy keys
- control-flow phases remain class-based (context/criterion shift)
"""

from typing import Any, Callable, Dict

from experiment.phases.base import PhaseBase
from experiment.phases.acquisition import AcquisitionPhase
from experiment.phases.nonreinforcement import NonReinforcementPhase
from experiment.phases.compound_acquisition import CompoundAcquisitionPhase
from experiment.phases.compound_nonreinforcement import CompoundNonReinforcementPhase
from experiment.phases.differential_acquisition import DifferentialAcquisitionPhase
from experiment.phases.probe import ProbePhase
from experiment.phases.context_shift import ContextShiftPhase
from experiment.phases.criterion_shift import CriterionShiftPhase
from experiment.phases.templates import (
    BlockedSampler,
    DefaultRecordBuilder,
    NeverLearn,
    OperantScheduleBuilder,
    PavlovianScheduleBuilder,
    PhaseTemplate,
    SpecLearningGate,
    WeightedRandomSampler,
)
from experiment.domain.types import (
    LearningGateSpec,
    OperantContingencySpec,
    PavlovianContingencySpec,
    PhaseSpec,
    TrialTimeSpec,
    TrialTypeSpec,
)

_FORBIDDEN_TEMPLATE_BEHAVIOR_KEYS = {
    "attention",
    "attention_compound",
    "salience",
    "similarity",
}


def _validate_template_behavior_params(params: dict[str, Any]) -> None:
    leaked = sorted(k for k in _FORBIDDEN_TEMPLATE_BEHAVIOR_KEYS if k in params)
    if leaked:
        raise ValueError(
            "Template phase params must not include representation/learner-owned keys: "
            + ", ".join(leaked)
        )


def _coerce_trial_types(stimuli: Any) -> list[TrialTypeSpec]:
    if isinstance(stimuli, dict):
        out: list[TrialTypeSpec] = []
        for label, values in stimuli.items():
            key = str(label)
            if key == "compound":
                if isinstance(values, (list, tuple)):
                    vals = [str(v) for v in values if isinstance(v, str) and v]
                elif isinstance(values, str) and values:
                    vals = [values]
                else:
                    vals = []
                if vals:
                    out.append(TrialTypeSpec(label=key, stimuli=vals))
                continue

            entries = list(values) if isinstance(values, (list, tuple)) else [values]
            valid_entries: list[list[str]] = []
            for entry in entries:
                if isinstance(entry, str) and entry:
                    valid_entries.append([entry])
                elif isinstance(entry, (list, tuple)):
                    compound_vals = [str(v) for v in entry if isinstance(v, str) and v]
                    if compound_vals:
                        valid_entries.append(compound_vals)

            for idx, entry_vals in enumerate(valid_entries):
                trial_label = key if len(valid_entries) == 1 and idx == 0 else f"{key}:{idx}"
                out.append(TrialTypeSpec(label=trial_label, stimuli=entry_vals))
        if out:
            return out
    if isinstance(stimuli, (list, tuple)):
        vals = [str(v) for v in stimuli if isinstance(v, str) and v]
        if vals:
            return [TrialTypeSpec(label="default", stimuli=vals)]
    raise ValueError("Template phases require non-empty stimuli to derive trial types.")


def _coerce_time_spec(params: dict[str, Any]) -> TrialTimeSpec:
    explicit = params.get("trial_time_spec")
    if isinstance(explicit, TrialTimeSpec):
        return explicit
    return TrialTimeSpec(
        duration_s=float(params.get("duration_s", 1.0)),
        dt_s=float(params.get("dt_s", 1.0)),
        iti_s=float(params.get("iti_s", 0.0)),
        allow_partial_last_step=bool(params.get("allow_partial_last_step", False)),
    )


def _build_pavlovian_phase_template(
    *,
    agent: Any,
    stimuli: Any = None,
    n_trials: int | None = None,
    params: dict[str, Any] | None = None,
):
    params = dict(params or {})
    _validate_template_behavior_params(params)
    spec = PhaseSpec(
        key="pavlovian_phase_template",
        name=str(params.get("phase_name", "Pavlovian Template")),
        context_id=(str(params["context"]) if params.get("context") else "A"),
        n_trials=int(n_trials or params.get("n_trials", 1)),
        time=_coerce_time_spec(params),
        trial_types=_coerce_trial_types(stimuli),
        contingency=PavlovianContingencySpec(
            us_magnitude=float(params.get("outcome", params.get("reward_value", 1.0))),
            us_event_type=str(params.get("us_event_type", "reward")),
        ),
        learning=LearningGateSpec(enabled=bool(params.get("learning_enabled", True))),
        metadata={"factory_phase_key": "pavlovian_phase_template"},
    )
    return PhaseTemplate(
        agent=agent,
        spec=spec,
        trial_sampler=WeightedRandomSampler(),
        trial_schedule_builder=PavlovianScheduleBuilder(),
        learning_gate=SpecLearningGate(),
        record_builder=DefaultRecordBuilder(),
    )


def _build_operant_phase_template(
    *,
    agent: Any,
    stimuli: Any = None,
    n_trials: int | None = None,
    params: dict[str, Any] | None = None,
):
    params = dict(params or {})
    _validate_template_behavior_params(params)
    actions = params.get("available_actions")
    if actions is None:
        actions = getattr(getattr(agent, "policy", None), "actions", None)
    action_labels = [str(a) for a in (actions or [])]
    schedule_runtime = params.get("schedule_runtime")
    if schedule_runtime is not None and not isinstance(schedule_runtime, dict):
        schedule_runtime = None
    spec = PhaseSpec(
        key="operant_phase_template",
        name=str(params.get("phase_name", "Operant Template")),
        context_id=(str(params["context"]) if params.get("context") else "A"),
        n_trials=int(n_trials or params.get("n_trials", 1)),
        time=_coerce_time_spec(params),
        trial_types=_coerce_trial_types(stimuli),
        contingency=OperantContingencySpec(
            task_key=str(params.get("task_key", "operant")),
            action_labels=action_labels,
            schedule_runtime=schedule_runtime,
        ),
        learning=LearningGateSpec(enabled=bool(params.get("learning_enabled", True))),
        metadata={"factory_phase_key": "operant_phase_template"},
    )
    return PhaseTemplate(
        agent=agent,
        spec=spec,
        trial_sampler=WeightedRandomSampler(),
        trial_schedule_builder=OperantScheduleBuilder(),
        learning_gate=SpecLearningGate(),
        record_builder=DefaultRecordBuilder(),
    )


def _build_acquisition_template(
    *,
    agent: Any,
    stimuli: Any = None,
    n_trials: int | None = None,
    params: dict[str, Any] | None = None,
):
    params = dict(params or {})
    return _build_pavlovian_phase_template(
        agent=agent,
        stimuli=stimuli,
        n_trials=n_trials,
        params={
            **params,
            "phase_name": params.get("phase_name", "Acquisition"),
            "outcome": float(params.get("outcome", 1.0)),
        },
    )


def _build_nonreinforcement_template(
    *,
    agent: Any,
    stimuli: Any = None,
    n_trials: int | None = None,
    params: dict[str, Any] | None = None,
):
    params = dict(params or {})
    return _build_pavlovian_phase_template(
        agent=agent,
        stimuli=stimuli,
        n_trials=n_trials,
        params={
            **params,
            "phase_name": params.get("phase_name", "Nonreinforcement"),
            "outcome": 0.0,
        },
    )


def _build_compound_acquisition_template(
    *,
    agent: Any,
    stimuli: Any = None,
    n_trials: int | None = None,
    params: dict[str, Any] | None = None,
):
    params = dict(params or {})
    if isinstance(stimuli, dict) and "compound" in stimuli:
        stimuli = {"compound": stimuli.get("compound", [])}
    return _build_pavlovian_phase_template(
        agent=agent,
        stimuli=stimuli,
        n_trials=n_trials,
        params={
            **params,
            "phase_name": params.get("phase_name", "Compound Acquisition"),
            "outcome": float(params.get("outcome", 1.0)),
        },
    )


def _build_compound_nonreinforcement_template(
    *,
    agent: Any,
    stimuli: Any = None,
    n_trials: int | None = None,
    params: dict[str, Any] | None = None,
):
    params = dict(params or {})
    if isinstance(stimuli, dict) and "compound" in stimuli:
        stimuli = {"compound": stimuli.get("compound", [])}
    return _build_pavlovian_phase_template(
        agent=agent,
        stimuli=stimuli,
        n_trials=n_trials,
        params={
            **params,
            "phase_name": params.get("phase_name", "Compound Nonreinforcement"),
            "outcome": 0.0,
        },
    )


def _build_differential_acquisition_template(
    *,
    agent: Any,
    stimuli: Any = None,
    n_trials: int | None = None,
    params: dict[str, Any] | None = None,
):
    params = dict(params or {})
    rewards_by_label = {}
    if isinstance(stimuli, dict):
        # Keep deterministic label mapping to existing cs_plus/cs_minus usage.
        rewards_by_label = {
            "cs_plus": float(params.get("reinforced_outcome", 1.0)),
            "cs_minus": float(params.get("nonreinforced_outcome", 0.0)),
        }
    template = _build_pavlovian_phase_template(
        agent=agent,
        stimuli=stimuli,
        n_trials=n_trials,
        params={
            **params,
            "phase_name": params.get("phase_name", "Differential Acquisition"),
            "outcome": float(params.get("reinforced_outcome", 1.0)),
        },
    )
    if isinstance(template.spec.contingency, PavlovianContingencySpec):
        c = template.spec.contingency
        template.spec = PhaseSpec(
            key=template.spec.key,
            name=template.spec.name,
            context_id=template.spec.context_id,
            n_trials=template.spec.n_trials,
            time=template.spec.time,
            trial_types=template.spec.trial_types,
            contingency=PavlovianContingencySpec(
                us_magnitude=c.us_magnitude,
                us_event_type=c.us_event_type,
                metadata={**c.metadata, "rewards_by_label": rewards_by_label},
            ),
            learning=template.spec.learning,
            metadata=dict(template.spec.metadata),
        )
    return template


def _build_probe_template(
    *,
    agent: Any,
    stimuli: Any = None,
    n_trials: int | None = None,
    params: dict[str, Any] | None = None,
):
    params = dict(params or {})
    deliver_reward = bool(params.get("deliver_reward", False))
    reward_value = float(params.get("reward_value", 1.0 if deliver_reward else 0.0))
    template = _build_pavlovian_phase_template(
        agent=agent,
        stimuli=stimuli,
        n_trials=n_trials,
        params={
            **params,
            "phase_name": params.get("phase_name", "Probe"),
            "outcome": reward_value,
            "learning_enabled": False,
        },
    )
    template.trial_sampler = BlockedSampler()
    template.learning_gate = NeverLearn()
    return template


PHASE_REGISTRY: Dict[str, Callable[..., Any]] = {
    # Canonical template-first defaults.
    "acquisition": _build_acquisition_template,
    "nonreinforcement": _build_nonreinforcement_template,
    "compound_acquisition": _build_compound_acquisition_template,
    "compound_nonreinforcement": _build_compound_nonreinforcement_template,
    # Keep class-based until template record semantics reach parity.
    "differential_acquisition": DifferentialAcquisitionPhase,
    "probe": _build_probe_template,
    # Legacy compatibility aliases for explicit class-based usage.
    "acquisition_legacy": AcquisitionPhase,
    "nonreinforcement_legacy": NonReinforcementPhase,
    "compound_acquisition_legacy": CompoundAcquisitionPhase,
    "compound_nonreinforcement_legacy": CompoundNonReinforcementPhase,
    "differential_acquisition_legacy": DifferentialAcquisitionPhase,
    "probe_legacy": ProbePhase,
    # Custom control-flow phases remain class-based.
    "context_shift": ContextShiftPhase,
    "criterion_shift": CriterionShiftPhase,
    # Explicit template keys (kept for direct authoring clarity).
    "acquisition_template": _build_acquisition_template,
    "nonreinforcement_template": _build_nonreinforcement_template,
    "compound_acquisition_template": _build_compound_acquisition_template,
    "compound_nonreinforcement_template": _build_compound_nonreinforcement_template,
    "differential_acquisition_template": _build_differential_acquisition_template,
    "probe_template": _build_probe_template,
    "pavlovian_phase_template": _build_pavlovian_phase_template,
    "operant_phase_template": _build_operant_phase_template,
}


def validate_phase(name: str) -> None:
    if name not in PHASE_REGISTRY:
        available = ", ".join(sorted(PHASE_REGISTRY.keys()))
        raise KeyError(
            f"Unknown phase '{name}'. "
            f"Available phases: {available}"
        )


def build_phase(name: str, *, agent: Any, stimuli: Any = None, **phase_params):
    """
    Construct a phase instance.

    Required:
      - agent
      - n_trials (if the phase expects trials)

    All other phase-specific values live in `params`.
    """
    validate_phase(name)
    phase_cls = PHASE_REGISTRY[name]

    # Extract trial count if present; keep the rest in params
    n_trials = phase_params.pop("n_trials", None)
    params = phase_params

    if stimuli is None:
        if n_trials is None:
            return phase_cls(agent=agent, params=params)
        return phase_cls(agent=agent, n_trials=n_trials, params=params)

    if n_trials is None:
        return phase_cls(agent=agent, stimuli=stimuli, params=params)
    return phase_cls(agent=agent, stimuli=stimuli, n_trials=n_trials, params=params)

