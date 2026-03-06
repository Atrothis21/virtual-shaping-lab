"""Runtime phase catalog surface.

This module is the authoritative runtime registry for phase construction.
"""

from __future__ import annotations

from typing import Any, Callable

from experiment.domain.types import (
    LearningGateSpec,
    OperantContingencySpec,
    PavlovianContingencySpec,
    PhaseSpec,
    TrialTimeSpec,
    TrialTypeSpec,
)
from experiment.phases.context_shift import ContextShiftPhase
from experiment.phases.criterion_shift import CriterionShiftPhase
from experiment.phases.templates import (
    AlwaysLearn,
    BlockedSampler,
    DefaultRecordBuilder,
    FixedSequenceSampler,
    NeverLearn,
    OperantScheduleBuilder,
    PavlovianScheduleBuilder,
    PhaseTemplate,
    SpecLearningGate,
    WeightedRandomSampler,
)
from virtual_shaping_lab.domain.catalog_metadata import (
    CONSTRAINT_CONTROL_FLOW_PHASE,
    CONSTRAINT_LEARNING_DISABLED_DEFAULT,
    CONSTRAINT_OPERANT_ONLY,
    CONSTRAINT_PAVLOVIAN_ONLY,
    CONSTRAINT_REQUIRES_COMPOUND_STIMULI,
    CONSTRAINT_REQUIRES_CS_PLUS_CS_MINUS_STIMULI,
    CONSTRAINT_TEMPLATE_ALIAS,
    CONSTRAINT_TEMPLATE_PHASE,
    UICatalogMetadata,
    make_default_ui_metadata,
    validate_ui_metadata_map,
)

_FORBIDDEN_TEMPLATE_BEHAVIOR_KEYS = {
    "attention",
    "attention_compound",
    "salience",
    "similarity",
}

_TRIAL_SAMPLER_KEY = "trial_sampler_strategy"
_SCHEDULE_BUILDER_KEY = "schedule_builder_strategy"
_LEARNING_GATE_KEY = "learning_gate_strategy"
_RECORD_BUILDER_KEY = "record_builder_strategy"

_ALLOWED_TRIAL_SAMPLER_STRATEGIES = {"weighted_random", "blocked", "fixed_sequence"}
_ALLOWED_SCHEDULE_BUILDER_STRATEGIES = {"pavlovian", "operant"}
_ALLOWED_LEARNING_GATE_STRATEGIES = {"spec", "always", "never"}
_ALLOWED_RECORD_BUILDER_STRATEGIES = {"default"}


def _validate_template_behavior_params(params: dict[str, Any]) -> None:
    leaked = sorted(k for k in _FORBIDDEN_TEMPLATE_BEHAVIOR_KEYS if k in params)
    if leaked:
        raise ValueError(
            "Template phase params must not include representation/learner-owned keys: "
            + ", ".join(leaked)
        )


def _resolve_trial_sampler(params: dict[str, Any]):
    strategy = str(params.get(_TRIAL_SAMPLER_KEY, "weighted_random"))
    if strategy not in _ALLOWED_TRIAL_SAMPLER_STRATEGIES:
        allowed = ", ".join(sorted(_ALLOWED_TRIAL_SAMPLER_STRATEGIES))
        raise ValueError(f"Unknown {_TRIAL_SAMPLER_KEY}='{strategy}'. Allowed: {allowed}")
    if strategy == "weighted_random":
        return WeightedRandomSampler()
    if strategy == "blocked":
        return BlockedSampler()
    sequence = params.get("trial_sampler_sequence", [])
    if not isinstance(sequence, list):
        raise ValueError("trial_sampler_sequence must be a list when using fixed_sequence sampler.")
    return FixedSequenceSampler([str(v) for v in sequence])


def _resolve_schedule_builder(params: dict[str, Any], *, default: str):
    strategy = str(params.get(_SCHEDULE_BUILDER_KEY, default))
    if strategy not in _ALLOWED_SCHEDULE_BUILDER_STRATEGIES:
        allowed = ", ".join(sorted(_ALLOWED_SCHEDULE_BUILDER_STRATEGIES))
        raise ValueError(f"Unknown {_SCHEDULE_BUILDER_KEY}='{strategy}'. Allowed: {allowed}")
    if strategy == "pavlovian":
        return PavlovianScheduleBuilder()
    return OperantScheduleBuilder()


def _resolve_learning_gate(params: dict[str, Any]):
    strategy = str(params.get(_LEARNING_GATE_KEY, "spec"))
    if strategy not in _ALLOWED_LEARNING_GATE_STRATEGIES:
        allowed = ", ".join(sorted(_ALLOWED_LEARNING_GATE_STRATEGIES))
        raise ValueError(f"Unknown {_LEARNING_GATE_KEY}='{strategy}'. Allowed: {allowed}")
    if strategy == "spec":
        return SpecLearningGate()
    if strategy == "always":
        return AlwaysLearn()
    return NeverLearn()


def _resolve_record_builder(params: dict[str, Any]):
    strategy = str(params.get(_RECORD_BUILDER_KEY, "default"))
    if strategy not in _ALLOWED_RECORD_BUILDER_STRATEGIES:
        allowed = ", ".join(sorted(_ALLOWED_RECORD_BUILDER_STRATEGIES))
        raise ValueError(f"Unknown {_RECORD_BUILDER_KEY}='{strategy}'. Allowed: {allowed}")
    return DefaultRecordBuilder()


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
        spec_version=int(params.get("spec_version", 1)),
        learning=LearningGateSpec(enabled=bool(params.get("learning_enabled", True))),
        metadata={"factory_phase_key": "pavlovian_phase_template"},
    )
    return PhaseTemplate(
        agent=agent,
        spec=spec,
        trial_sampler=_resolve_trial_sampler(params),
        trial_schedule_builder=_resolve_schedule_builder(params, default="pavlovian"),
        learning_gate=_resolve_learning_gate(params),
        record_builder=_resolve_record_builder(params),
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
        spec_version=int(params.get("spec_version", 1)),
        learning=LearningGateSpec(enabled=bool(params.get("learning_enabled", True))),
        metadata={"factory_phase_key": "operant_phase_template"},
    )
    return PhaseTemplate(
        agent=agent,
        spec=spec,
        trial_sampler=_resolve_trial_sampler(params),
        trial_schedule_builder=_resolve_schedule_builder(params, default="operant"),
        learning_gate=_resolve_learning_gate(params),
        record_builder=_resolve_record_builder(params),
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
            "phase_name": params.get("phase_name", "acquisition"),
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
            "phase_name": params.get("phase_name", "nonreinforcement"),
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
            "phase_name": params.get("phase_name", "compound_acquisition"),
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
            "phase_name": params.get("phase_name", "compound_nonreinforcement"),
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
            "phase_name": params.get("phase_name", "differential_acquisition"),
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
            spec_version=template.spec.spec_version,
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
            "phase_name": params.get("phase_name", "probe"),
            "outcome": reward_value,
            "learning_enabled": False,
        },
    )
    template.trial_sampler = BlockedSampler()
    template.learning_gate = NeverLearn()
    return template


PHASE_BUILDERS: dict[str, Callable[..., Any]] = {
    "acquisition": _build_acquisition_template,
    "nonreinforcement": _build_nonreinforcement_template,
    "compound_acquisition": _build_compound_acquisition_template,
    "compound_nonreinforcement": _build_compound_nonreinforcement_template,
    "differential_acquisition": _build_differential_acquisition_template,
    "probe": _build_probe_template,
    "context_shift": ContextShiftPhase,
    "criterion_shift": CriterionShiftPhase,
    "acquisition_template": _build_acquisition_template,
    "nonreinforcement_template": _build_nonreinforcement_template,
    "compound_acquisition_template": _build_compound_acquisition_template,
    "compound_nonreinforcement_template": _build_compound_nonreinforcement_template,
    "differential_acquisition_template": _build_differential_acquisition_template,
    "probe_template": _build_probe_template,
    "pavlovian_phase_template": _build_pavlovian_phase_template,
    "operant_phase_template": _build_operant_phase_template,
}

_COMMON_PAVLOVIAN_SCHEMA = {
    "n_trials": {"type": "int", "min": 1},
    "context": {"type": "str"},
    "outcome": {"type": "float"},
    "learning_enabled": {"type": "bool"},
}

_COMMON_PAVLOVIAN_DEFAULTS = {
    "n_trials": 1,
    "context": "A",
    "outcome": 1.0,
    "learning_enabled": True,
}

_COMMON_TEMPLATE_STRATEGY_SCHEMA = {
    "trial_sampler_strategy": {"type": "enum", "values": sorted(_ALLOWED_TRIAL_SAMPLER_STRATEGIES)},
    "schedule_builder_strategy": {"type": "enum", "values": sorted(_ALLOWED_SCHEDULE_BUILDER_STRATEGIES)},
    "learning_gate_strategy": {"type": "enum", "values": sorted(_ALLOWED_LEARNING_GATE_STRATEGIES)},
    "record_builder_strategy": {"type": "enum", "values": sorted(_ALLOWED_RECORD_BUILDER_STRATEGIES)},
}

_COMMON_TEMPLATE_STRATEGY_DEFAULTS = {
    "trial_sampler_strategy": "weighted_random",
    "schedule_builder_strategy": "pavlovian",
    "learning_gate_strategy": "spec",
    "record_builder_strategy": "default",
}

_PHASE_METADATA_OVERRIDES: dict[str, UICatalogMetadata] = {
    "acquisition": UICatalogMetadata(
        label="Acquisition",
        description="Single-cue reinforced pavlovian phase.",
        params_schema={**_COMMON_PAVLOVIAN_SCHEMA},
        defaults={**_COMMON_PAVLOVIAN_DEFAULTS},
        constraints=(CONSTRAINT_PAVLOVIAN_ONLY,),
        examples=({"stimuli": {"cs_plus": ["tone"]}, "n_trials": 20, "outcome": 1.0},),
    ),
    "nonreinforcement": UICatalogMetadata(
        label="Nonreinforcement",
        description="Single-cue nonreinforced pavlovian phase (extinction-like).",
        params_schema={**_COMMON_PAVLOVIAN_SCHEMA},
        defaults={**_COMMON_PAVLOVIAN_DEFAULTS, "outcome": 0.0},
        constraints=(CONSTRAINT_PAVLOVIAN_ONLY,),
        examples=({"stimuli": {"cs_plus": ["tone"]}, "n_trials": 20, "outcome": 0.0},),
    ),
    "compound_acquisition": UICatalogMetadata(
        label="Compound Acquisition",
        description="Compound-cue reinforced pavlovian phase.",
        params_schema={**_COMMON_PAVLOVIAN_SCHEMA},
        defaults={**_COMMON_PAVLOVIAN_DEFAULTS},
        constraints=(CONSTRAINT_REQUIRES_COMPOUND_STIMULI, CONSTRAINT_PAVLOVIAN_ONLY),
        examples=({"stimuli": {"compound": ["tone", "light"]}, "n_trials": 20, "outcome": 1.0},),
    ),
    "compound_nonreinforcement": UICatalogMetadata(
        label="Compound Nonreinforcement",
        description="Compound-cue nonreinforced pavlovian phase.",
        params_schema={**_COMMON_PAVLOVIAN_SCHEMA},
        defaults={**_COMMON_PAVLOVIAN_DEFAULTS, "outcome": 0.0},
        constraints=(CONSTRAINT_REQUIRES_COMPOUND_STIMULI, CONSTRAINT_PAVLOVIAN_ONLY),
        examples=({"stimuli": {"compound": ["tone", "light"]}, "n_trials": 20, "outcome": 0.0},),
    ),
    "differential_acquisition": UICatalogMetadata(
        label="Differential Acquisition",
        description="Pavlovian phase with reinforced CS+ and nonreinforced CS- trial types.",
        params_schema={
            "n_trials": {"type": "int", "min": 1},
            "context": {"type": "str"},
            "reinforced_outcome": {"type": "float"},
            "nonreinforced_outcome": {"type": "float"},
        },
        defaults={"n_trials": 1, "context": "A", "reinforced_outcome": 1.0, "nonreinforced_outcome": 0.0},
        constraints=(CONSTRAINT_REQUIRES_CS_PLUS_CS_MINUS_STIMULI, CONSTRAINT_PAVLOVIAN_ONLY),
        examples=(
            {
                "stimuli": {"cs_plus": ["tone"], "cs_minus": ["noise"]},
                "n_trials": 40,
                "reinforced_outcome": 1.0,
                "nonreinforced_outcome": 0.0,
            },
        ),
    ),
    "probe": UICatalogMetadata(
        label="Probe",
        description="Pavlovian probe/testing phase with learning disabled by default.",
        params_schema={
            "n_trials": {"type": "int", "min": 1},
            "context": {"type": "str"},
            "deliver_reward": {"type": "bool"},
            "reward_value": {"type": "float"},
        },
        defaults={"n_trials": 1, "context": "A", "deliver_reward": False, "reward_value": 1.0},
        constraints=(CONSTRAINT_LEARNING_DISABLED_DEFAULT, CONSTRAINT_PAVLOVIAN_ONLY),
        examples=({"stimuli": {"cs_plus": ["tone"]}, "n_trials": 10, "deliver_reward": False},),
    ),
    "context_shift": UICatalogMetadata(
        label="Context Shift",
        description="Control-flow phase that changes active context for subsequent phases.",
        params_schema={"context": {"type": "str"}},
        defaults={"context": "B"},
        constraints=(CONSTRAINT_CONTROL_FLOW_PHASE,),
        examples=({"params": {"context": "B"}},),
    ),
    "criterion_shift": UICatalogMetadata(
        label="Criterion Shift",
        description="Control-flow phase that shifts execution based on criterion conditions.",
        params_schema={"criterion": {"type": "dict"}},
        defaults={"criterion": {}},
        constraints=(CONSTRAINT_CONTROL_FLOW_PHASE,),
        examples=({"params": {"criterion": {"type": "prediction_threshold", "threshold": 0.2}}},),
    ),
    "pavlovian_phase_template": UICatalogMetadata(
        label="Pavlovian Phase Template",
        description="Configurable template-backed pavlovian phase.",
        params_schema={**_COMMON_PAVLOVIAN_SCHEMA, **_COMMON_TEMPLATE_STRATEGY_SCHEMA},
        defaults={**_COMMON_PAVLOVIAN_DEFAULTS, **_COMMON_TEMPLATE_STRATEGY_DEFAULTS},
        constraints=(CONSTRAINT_TEMPLATE_PHASE, CONSTRAINT_PAVLOVIAN_ONLY),
        examples=({"stimuli": {"cs_plus": ["tone"]}, "params": {"trial_sampler_strategy": "weighted_random"}},),
    ),
    "operant_phase_template": UICatalogMetadata(
        label="Operant Phase Template",
        description="Configurable template-backed operant phase.",
        params_schema={
            "n_trials": {"type": "int", "min": 1},
            "context": {"type": "str"},
            "available_actions": {"type": "list[str]"},
            "task_key": {"type": "str"},
            **_COMMON_TEMPLATE_STRATEGY_SCHEMA,
        },
        defaults={
            "n_trials": 1,
            "context": "A",
            "available_actions": [],
            "task_key": "operant",
            **{**_COMMON_TEMPLATE_STRATEGY_DEFAULTS, "schedule_builder_strategy": "operant"},
        },
        constraints=(CONSTRAINT_TEMPLATE_PHASE, CONSTRAINT_OPERANT_ONLY),
        examples=(
            {
                "stimuli": {"cs_plus": ["lever"]},
                "params": {"available_actions": ["left", "right"], "schedule_builder_strategy": "operant"},
            },
        ),
    ),
}

PHASE_METADATA: dict[str, UICatalogMetadata] = {}
for phase_key in PHASE_BUILDERS.keys():
    if phase_key in _PHASE_METADATA_OVERRIDES:
        PHASE_METADATA[phase_key] = _PHASE_METADATA_OVERRIDES[phase_key]
    elif phase_key.endswith("_template"):
        base_key = phase_key[: -len("_template")]
        if base_key in _PHASE_METADATA_OVERRIDES:
            base_meta = _PHASE_METADATA_OVERRIDES[base_key]
            PHASE_METADATA[phase_key] = UICatalogMetadata(
                label=f"{base_meta.label} Template",
                description=f"Template alias for {base_meta.label}.",
                params_schema=dict(base_meta.params_schema),
                defaults=dict(base_meta.defaults),
                constraints=tuple(sorted(set(base_meta.constraints + (CONSTRAINT_TEMPLATE_ALIAS,)))),
                examples=base_meta.examples,
            )
            continue
        PHASE_METADATA[phase_key] = make_default_ui_metadata(phase_key, description_prefix="Template phase")
    else:
        PHASE_METADATA[phase_key] = make_default_ui_metadata(phase_key, description_prefix="Phase")

validate_ui_metadata_map(
    keys=set(PHASE_BUILDERS.keys()),
    metadata_map=PHASE_METADATA,
    namespace="experiment.phases.catalog_runtime",
)


def available_phases() -> list[str]:
    return sorted(PHASE_BUILDERS.keys())


def get_phase_metadata(name: str) -> UICatalogMetadata:
    validate_phase_key(name)
    return PHASE_METADATA[name]


def validate_phase_key(name: str) -> None:
    if name not in PHASE_BUILDERS:
        available = ", ".join(sorted(PHASE_BUILDERS.keys()))
        raise KeyError(f"Unknown phase '{name}'. Available phases: {available}")


def build_phase(name: str, *, agent: Any, stimuli: Any = None, **phase_params: Any) -> Any:
    validate_phase_key(name)
    phase_cls = PHASE_BUILDERS[name]

    n_trials = phase_params.pop("n_trials", None)
    params = phase_params

    if stimuli is None:
        if n_trials is None:
            return phase_cls(agent=agent, params=params)
        return phase_cls(agent=agent, n_trials=n_trials, params=params)

    if n_trials is None:
        return phase_cls(agent=agent, stimuli=stimuli, params=params)
    return phase_cls(agent=agent, stimuli=stimuli, n_trials=n_trials, params=params)

