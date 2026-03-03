## Overview
V2.8 delivers boundary-hygiene and ownership cleanup to reduce architectural entropy before further feature growth.

Primary outcomes:
- UI validation is now shallow-only, with semantic validation owned by engine config/parameter pipelines
- world schedule runtime moved under `experiment/world/schedules`
- reward schedule registry ownership consolidated to world schedules
- import-boundary guard tests added for analysis/runtime/cognition/config layers
- deprecated protocol schedule shim modules removed after production import cutover

---

## Delivered Changes

### 1) Validation Authority Cutover
- Updated `ui.validate_payload` to perform shallow structural/schema checks only.
- Removed deep semantic checks from UI validator path.
- Semantic enforcement remains in engine-owned layers (`ExperimentConfig`, parameter composition/ownership guards, assembly/runtime guards).

Updated tests:
- `tests/test_validate_payload.py`

### 2) World Schedule Namespace
Added canonical schedule runtime package:
- `virtual_shaping_lab/experiment/world/schedules/availability.py`
- `virtual_shaping_lab/experiment/world/schedules/gate.py`
- `virtual_shaping_lab/experiment/world/schedules/consequence.py`
- `virtual_shaping_lab/experiment/world/schedules/runtime.py`
- `virtual_shaping_lab/experiment/world/schedules/__init__.py`

Updated core imports to world path:
- `virtual_shaping_lab/experiment/trial_executor.py`
- `virtual_shaping_lab/protocols/reward_schedules.py` (during migration stage)

### 3) Single Registry Ownership
Consolidated reward schedule registry/build logic to world-owned module:
- `virtual_shaping_lab/experiment/world/schedules/reward_schedules.py`

Factory compatibility path now delegates to world-owned registry:
- `virtual_shaping_lab/experiment/factories/reward_schedule_factory.py`

### 4) Boundary Guardrails
Added AST-based import boundary tests:
- `tests/test_import_boundaries.py`

Guards enforced:
- analysis must not import runtime internals/cognition/protocol internals
- runtime must not import analysis
- cognition must not import runtime internals/protocols/analysis
- config must not import runtime/behavior/analysis internals

### 5) Shim Removal + Docs
Removed deprecated protocol schedule shim modules:
- `virtual_shaping_lab/protocols/schedule_runtime.py`
- `virtual_shaping_lab/protocols/reward_schedules.py`

Updated tests to import canonical world schedule modules directly:
- `tests/test_schedule_runtime.py`
- `tests/test_trial_executor.py`
- `tests/behavioral_signatures/test_fi_vs_fr.py`
- `tests/test_protocols.py`

Updated architecture documentation:
- `docs/core_engine_architecture.md` (now V2.8, world schedule namespace reflected)

---

## Validation

Phase gates executed during implementation:
- `python -m pytest -q tests/test_validate_payload.py tests/test_config.py tests/test_run_api_contract.py`
- `python -m pytest -q tests/test_schedule_runtime.py tests/test_trial_executor.py tests/test_protocols.py`
- `python -m pytest -q tests/test_factories.py tests/test_operant_contract_harness.py tests/test_protocols.py`
- `python -m pytest -q tests/test_import_boundaries.py tests/test_analysis_registry.py tests/test_runner_protocol.py`

Closeout:
- `python -m pytest -q`

All passed.

---

## Net State After V2.8

- Semantic validation has a single authoritative engine path.
- World schedule physics is separated from protocol namespace ownership.
- Reward schedule registry ownership is singular and explicit.
- Layer boundaries are enforced by tests.
- Deprecated schedule shim paths have been removed from production and tests.
