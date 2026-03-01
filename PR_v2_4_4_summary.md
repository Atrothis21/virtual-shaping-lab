## Overview
V2.4.4 completes config-layer decomposition and hardening by turning payload parsing into a composable pipeline with explicit normalization, validation, and plan-construction paths.

Primary outcomes:
- `ExperimentConfig.from_payload(...)` is now a thin façade over `ConfigPipeline`
- payload-to-plan flow is first-class (`ConfigPipeline.build_plan`, `ExperimentConfig.plan_from_payload`)
- normalization and validation concerns are separated into composable components
- pipeline components support dependency injection (including partial overrides with safe fallback)
- config failure-path behavior is explicitly tested for payload and plan builders

---

## Delivered Changes

### 1) Config Pipeline Composites
Updated:
- `virtual_shaping_lab/experiment/config.py`

Added composites:
- `PayloadNormalizer`
- `PayloadValidator`
- `ConfigParser`
- `ConfigPipeline`
- `PlanBuilder`

Result:
- config parsing no longer depends on a monolithic `from_payload` implementation.

### 2) Thin Public Facades
Updated:
- `ExperimentConfig.from_payload(...)`
- `ExperimentConfig.to_plan(...)`

Added:
- `ExperimentConfig.plan_from_payload(...)`

Behavior:
- public entrypoints remain stable
- orchestration moved to pipeline objects

### 3) Validation/Normalization Hardening
Added pipeline guards:
- payload shape validation (`experiment`/`report` section checks)
- `experiment.phases` shape validation
- experiment identity validation (`learner`, `agent` non-empty strings)
- report preset validation (`report.preset` non-empty string)

Added normalization:
- trimmed `report.preset`
- trimmed `experiment.learner` and `experiment.agent`

### 4) DI-Friendly Pipeline Behavior
`ConfigPipeline` now supports injected:
- parser
- validator
- normalizer

And supports partial injected components via method-level fallback to defaults.

### 5) Payload-to-Plan Path
Added:
- `ConfigPipeline.build_plan(...)`

This makes payload -> config -> plan a composable pipeline path instead of an implicit call chain.

---

## Test Coverage Added/Updated

Updated:
- `tests/test_config.py`

Added/expanded coverage for:
- normalizer/validator/parser/pipeline smoke paths
- payload shape and section type failures
- non-list `phases` rejection
- report preset validation
- learner/agent validation and normalization
- pipeline DI orchestration behavior
- partial override fallback behavior
- payload-to-plan success path
- payload-to-plan failure-path parity with `from_payload`
- validation-error propagation in `build_plan`

---

## Validation

Executed and passing:
- `python -m pytest -q tests/test_config.py tests/test_validate_payload.py tests/test_full_payloads.py`

Note:
- existing visualization warnings remain in `tests/test_full_payloads.py` and are unrelated to config-pipeline changes.

---

## Compatibility Notes

- No intended API break to existing callers of:
  - `ExperimentConfig.from_payload(...)`
  - `ExperimentConfig.to_plan(...)`
- New path `ExperimentConfig.plan_from_payload(...)` is additive.
- Refactor is structural/compositional with behavior parity and stronger validation invariants.

