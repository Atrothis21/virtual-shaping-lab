## Overview
V2.7 completes phase objectification and template runtime migration for classical phase composition.

Primary outcomes:
- introduced declarative phase spec contracts (`PhaseSpec`, trial types, contingencies, learning gate)
- implemented a runnable template composite (`PhaseTemplate`) with pluggable mechanics
- integrated template-backed phase keys into factory/registry
- migrated canonical parameter-only phases to template variants
- migrated selected multi-phase protocols to compose template-backed phases
- enforced ownership guardrails for template behavior params
- documented template authoring, migration map, and extension patterns

---

## Delivered Changes

### 1) Phase Spec Domain Foundation
Added declarative domain contracts for template-driven phase execution:
- `TrialTypeSpec`
- `LearningGateSpec`
- `PavlovianContingencySpec`
- `OperantContingencySpec`
- `PhaseSpec`

These are serializable and compatible with plan/unit composition.

### 2) `PhaseTemplate` Runnable Composite
Added `PhaseTemplate` as a thin orchestrator:
- `reset(ctx)`
- `iter_steps(ctx)`

The template composes:
- `ITrialSampler`
- `ITrialScheduleBuilder`
- `ILearningGate`
- `IRecordBuilder`

### 3) Baseline Template Mechanics
Added strategy implementations:
- samplers: `WeightedRandomSampler`, `BlockedSampler`, `FixedSequenceSampler`
- schedule builders: `PavlovianScheduleBuilder`, `OperantScheduleBuilder`
- learning gates: `AlwaysLearn`, `NeverLearn`, `SpecLearningGate`
- record builder: `DefaultRecordBuilder`

### 4) Factory/Registry Integration
Integrated template-backed phase keys in phase factory/registry:
- `pavlovian_phase_template`
- `operant_phase_template`
- canonical template variants:
  - `acquisition_template`
  - `nonreinforcement_template`
  - `compound_acquisition_template`
  - `compound_nonreinforcement_template`
  - `differential_acquisition_template`
  - `probe_template`

### 5) Canonical Template Migration
Migrated parameter-only canonical phase behavior to template variants while preserving legacy compatibility path.

### 6) Protocol Composition Migration
Updated selected high-value protocols to compose template-backed phases:
- `blocking`
- `conditioned_inhibition`
- renewal family:
  - `aab_renewal`
  - `aba_renewal`
  - `abc_renewal`

Behavioral expectations and subphase naming were preserved for existing signature tests.

### 7) Guardrails and Policy
Added explicit template ownership guards:
- template phase params reject representation/learner-owned keys:
  - `attention`
  - `attention_compound`
  - `salience`
  - `similarity`

Defined explicit custom class policy in phase catalog:
- `CUSTOM_PHASE_CLASS_ALLOWLIST = {"context_shift", "criterion_shift"}`

Context precedence is enforced and tested:
- explicit phase/unit context wins over inferred context.

### 8) Authoring and Architecture Docs
Added authoring guide:
- `docs/phase_template_authoring.md`

Updated architecture doc link:
- `docs/core_engine_architecture.md`

The authoring guide includes:
- template-first workflow
- migration map (legacy -> template keys)
- extension examples for sampler/gate/schedule composition

---

## Test Gates

Phase gates run during implementation included:
- `python -m pytest -q tests/test_domain_types.py tests/test_config.py`
- `python -m pytest -q tests/test_phases.py tests/test_runner_protocol.py`
- `python -m pytest -q tests/test_phases.py tests/test_protocols.py tests/test_trial_executor.py`
- `python -m pytest -q tests/test_factories.py tests/test_assemble_coverage.py tests/test_phases.py`
- `python -m pytest -q tests/test_phases.py tests/test_protocols.py tests/behavioral_signatures/test_blocking.py tests/behavioral_signatures/test_extinction_reacquisition.py`
- `python -m pytest -q tests/test_protocols.py tests/test_protocol_catalog.py tests/behavioral_signatures/test_blocking.py tests/behavioral_signatures/test_conditioned_inhibition.py tests/behavioral_signatures/test_renewal.py`
- `python -m pytest -q tests/test_parameter_ownership_guards.py tests/test_assemble_coverage.py tests/test_config.py`
- `python -m pytest -q tests/test_factories.py tests/test_assemble_coverage.py`

V2.7 closeout gate:
- `python -m pytest -q`

---

## Remaining Legacy Classes (Intentional)

Legacy phase classes still exist for compatibility and non-template migration paths.  
Template/spec-first authoring is now the default for new parameterized phase behavior.

---

## Net State After V2.7

- Phase authoring is template/spec-first by default.
- Canonical parameter-only phase behaviors no longer require dedicated subclasses.
- Protocol composition can consume declarative, template-backed phase behavior cleanly.
- Runner remains generic and runnable-only.
- V2.6 ownership boundaries remain enforced with explicit guardrails.
