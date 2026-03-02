## Overview
V2.6.0 completes parameter objectification/composition as a first-class execution contract.

Primary outcomes:
- added typed parameter domain models and composition pipeline
- embedded deterministic composed parameter snapshots into experiment plans
- routed assembly/runtime paths to consume typed composed parameters
- enforced ownership-leakage guards at assembly/runtime boundaries
- removed remaining execution-time dependence on raw payload/config dict reads

This closes the V2.6.0 goal: execution now runs from resolved plans plus typed parameter objects.

---

## Delivered Changes

### 1) Parameter Type Foundation
Added typed parameter contracts in:
- `virtual_shaping_lab/experiment/parameters/types.py`
- `virtual_shaping_lab/experiment/parameters/__init__.py`

Core objects:
- `ExperimentParameters`
- `RepresentationParams` / `ContextParams` / `SalienceParams` / `SimilarityParams`
- `LearnerParams` / `AttentionParams`
- `PolicyParams` variants
- `RuntimeParams`
- `UnitParams`

Tests:
- `tests/test_parameter_types.py`

### 2) Normalization + Validation Pipelines
Added parameter pipelines in:
- `virtual_shaping_lab/experiment/parameters/pipeline.py`

Includes:
- `ParameterNormalizerPipeline`
- `ParameterValidatorPipeline`

Tests:
- `tests/test_parameter_normalizer.py`
- `tests/test_parameter_validator.py`

### 3) Composer + Deterministic Serialization
Added composition helpers in:
- `virtual_shaping_lab/experiment/parameters/composer.py`

Includes:
- `ParameterComposer.compose(...)`
- `parameters_to_dict(...)`

Tests:
- `tests/test_parameter_composer.py`

### 4) Plan Builder Integration
Updated:
- `virtual_shaping_lab/experiment/plan_builder.py`

Behavior:
- plan settings now include deterministic `settings["composed_parameters"]`
- existing settings remain intact for backward compatibility

Tests:
- `tests/test_config.py`

### 5) Assembly Routing (Typed Fallbacks)
Updated:
- `virtual_shaping_lab/experiment/assemble.py`

Behavior:
- uses composed parameter fallbacks for policy/learner/attention/representation data
- keeps classical/operant behavior constraints intact

Tests:
- `tests/test_assemble_coverage.py`

### 6) Agent Stack Typed Routing
Updated:
- `virtual_shaping_lab/experiment/assemble.py`

Behavior:
- agent stack now prefers typed composed learner/representation/policy fields where present
- classical/operant path semantics preserved

Tests:
- `tests/test_agents.py`
- `tests/test_learners.py`
- `tests/test_representations.py`
- `tests/test_assemble_coverage.py`

### 7) Runtime + Unit Typed Routing
Updated:
- `virtual_shaping_lab/experiment/assemble.py`
- `virtual_shaping_lab/experiment/runner.py`
- `virtual_shaping_lab/api/services.py`

Behavior:
- `UnitAssembler` consumes typed unit defaults (time, learning gate, contingency, context)
- context precedence enforced: explicit context (phase/unit) wins over inferred context
- `Runner` consumes typed runtime mode fallback from composed parameters
- run service passes plan settings into runner execution

Tests:
- `tests/test_runner_protocol.py`
- `tests/test_phases.py`
- `tests/test_protocols.py`
- `tests/test_assemble_coverage.py`

### 8) Ownership Leakage Guards
Added:
- `virtual_shaping_lab/experiment/parameters/ownership_guards.py`

Updated:
- `virtual_shaping_lab/experiment/parameters/__init__.py`
- `virtual_shaping_lab/experiment/assemble.py`
- `virtual_shaping_lab/experiment/runner.py`

Behavior:
- fail-fast ownership contract validation for `composed_parameters` at assembly/runtime boundaries
- explicit errors for cross-subsystem leakage

Tests:
- `tests/test_parameter_ownership_guards.py`
- `tests/test_config.py`

### 9) Execution Path Raw-Config Read Removal
Updated:
- `virtual_shaping_lab/api/services.py`
- `tests/test_full_payloads.py`

Behavior:
- execution path runs from `ExperimentPlan` + typed/composed plan settings
- report provenance payload for run artifacts is plan-derived, not execution-config-derived

Tests:
- `tests/test_run_api_contract.py`
- `tests/test_full_payloads.py`

### 10) Closeout Documentation
Updated:
- `docs/core_engine_architecture.md` (v2.6 view with parameter composition flow)
- `PR_v2_6_0_summary.md` (this file)

---

## Validation

Targeted gates executed during implementation:
- `python -m pytest -q tests/test_config.py tests/test_assemble_coverage.py`
- `python -m pytest -q tests/test_agents.py tests/test_learners.py tests/test_representations.py`
- `python -m pytest -q tests/test_runner_protocol.py tests/test_phases.py tests/test_protocols.py`
- `python -m pytest -q tests/test_config.py tests/test_parameter_ownership_guards.py`
- `python -m pytest -q tests/test_run_api_contract.py tests/test_full_payloads.py`

Final regression gate:
- `python -m pytest -q`

---

## Net Architectural State After V2.6.0

- Typed parameter composition is now part of the plan contract.
- Assembly/runtime execution consumes composed parameters with explicit boundary guards.
- Context precedence and runtime mode semantics are contract-level and test-covered.
- Execution-time behavior is plan-driven, not raw-payload/config-driven.

V2.6.0 completes parameter objectification/composition as an execution boundary contract.
