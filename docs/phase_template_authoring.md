# Phase Template Authoring Guide (V2.7)

## Purpose
This guide defines the default way to add or migrate phases in V2.7:

- author phase behavior as declarative data (`PhaseSpec` + mechanics)
- compose runtime behavior with `PhaseTemplate`
- keep runner/protocol execution generic (`reset`, `iter_steps`)

Use custom phase classes only for approved control-flow/runtime cases.

## Default Authoring Flow

1. Choose or add a phase key in the phase factory/catalog.
2. Build a `PhaseSpec`:
   - `key`, `name`, `context_id`, `n_trials`
   - `time` (`TrialTimeSpec`)
   - `trial_types` (`TrialTypeSpec` list)
   - `contingency` (`PavlovianContingencySpec` or `OperantContingencySpec`)
   - `learning` (`LearningGateSpec`)
3. Compose a `PhaseTemplate`:
   - sampler (`ITrialSampler`)
   - schedule builder (`ITrialScheduleBuilder`)
   - learning gate (`ILearningGate`)
   - record builder (`IRecordBuilder`)
4. Register the key in `PHASE_REGISTRY` and `PHASE_CATALOG`.

## Ownership Boundaries (Non-Negotiable)

Template phase behavior params must not contain representation/learner mechanism fields:

- `attention`
- `attention_compound`
- `salience`
- `similarity`

These are enforced in config/factory guards and belong to other subsystems.

## Context Precedence Rule

When context inference is enabled:

- explicit phase context wins over inferred context
- explicit typed unit context (`context_id`) also wins over inferred context
- inferred context is only applied when no explicit context is provided

This applies to both legacy and template-backed phase keys.

## Custom Phase Class Policy

Template/spec-first is default for new parameterized phase behavior.

Custom class phases are currently reserved for control-flow/runtime roles:

- `context_shift`
- `criterion_shift`

If a new custom class is proposed, it should not duplicate parameter-only behavior that can be expressed as `PhaseSpec` + mechanics.

## Legacy -> Template Migration Map

- `acquisition` -> `acquisition_template`
- `nonreinforcement` -> `nonreinforcement_template`
- `compound_acquisition` -> `compound_acquisition_template`
- `compound_nonreinforcement` -> `compound_nonreinforcement_template`
- `differential_acquisition` -> `differential_acquisition_template`
- `probe` -> `probe_template`

Notes:

- canonical template variants are opt-in keys; legacy keys still exist during migration
- protocol composition in V2.7 should prefer template variants where behavior is parameter-only

## Extension Examples

### Example 1: Add a New Trial Sampler

Implement `ITrialSampler`:

```python
from experiment.phases.templates.interfaces import ITrialSampler

class ReverseBlockedSampler(ITrialSampler):
    def reset(self) -> None:
        return None

    def select_trial_type(self, *, spec, trial_index, rng):
        idx = len(spec.trial_types) - 1 - (trial_index % len(spec.trial_types))
        return spec.trial_types[idx]
```

Wire it into template construction:

```python
template = PhaseTemplate(
    agent=agent,
    spec=spec,
    trial_sampler=ReverseBlockedSampler(),
    trial_schedule_builder=PavlovianScheduleBuilder(),
    learning_gate=SpecLearningGate(),
    record_builder=DefaultRecordBuilder(),
)
```

### Example 2: Add a New Learning Gate

Implement `ILearningGate`:

```python
from experiment.phases.templates.interfaces import ILearningGate

class FirstHalfLearnOnly(ILearningGate):
    def allows_learning(self, *, spec, trial_index):
        return trial_index < max(1, spec.n_trials // 2)
```

Use in a template-backed phase:

```python
template.learning_gate = FirstHalfLearnOnly()
```

### Example 3: Add an Operant Schedule Runtime Adapter

If a contingency exposes schedule runtime metadata, `OperantScheduleBuilder` attaches it to `TrialSchedule.metadata["schedule_runtime"]`.

To add a new schedule type:

1. add/extend schedule adapter in `protocols/reward_schedules.py`
2. ensure contingency carries `schedule_runtime` dict
3. keep `TrialExecutor` contract unchanged (metadata-driven)

## Minimal Checklist for New Template-Backed Phase

1. Factory builder returns a `PhaseTemplate` with valid `PhaseSpec`.
2. Builder validates ownership boundaries (no mechanism leakage).
3. Phase key is added to:
   - `PHASE_REGISTRY`
   - `PHASE_CATALOG`
4. Protocol usage (if any) preserves expected subphase naming for reporting/tests.
5. Add/update tests in:
   - `tests/test_factories.py`
   - `tests/test_assemble_coverage.py`
   - protocol/behavior tests if semantics change.
