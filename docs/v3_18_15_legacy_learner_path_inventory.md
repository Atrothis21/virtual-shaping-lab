# V3.18.15 Legacy Learner Path Inventory and Ownership Matrix

## Scope
Inventory learner-execution branches outside the canonical V3 path:
- canonical execution core: `virtual_shaping_lab/vsl/agent/learning/*`
- canonical runtime seam: `virtual_shaping_lab/vsl/runtime/learner_adapter.py`

This inventory classifies each surface as `keep`, `bridge`, `delete-now`, or `delete-later`.

---

## Entry Criteria Verification Snapshot

1. V3.18.10 runtime adapter path active: **met**
- Evidence: `virtual_shaping_lab/vsl/rollout/harness.py` uses `build_runtime_learner_adapter(...)` and calls `self._learner_adapter.step(...)`.

2. Executable presets RW/TD/PH/Mackintosh/TD-lambda present: **met**
- Evidence: `virtual_shaping_lab/vsl/agent/learning/executable_presets.py` exposes:
  - `rescorla_wagner`
  - `td0`
  - `pearce_hall_rw`
  - `mackintosh_rw`
  - `td_lambda`

3. Record/report learner-internal propagation present: **met**
- Evidence:
  - `virtual_shaping_lab/vsl/records/adapters/rollout_records.py` emits `metadata.learner_traces`
  - `virtual_shaping_lab/analysis/report/report.py` normalizes `v`, `delta`, `theta`, `attention`, `memory`

---

## Ownership Matrix

| Surface | Current role | Classification | Owner | Action |
|---|---|---|---|---|
| `virtual_shaping_lab/vsl/agent/learning/*` | Canonical learner composition and executable bundle | keep | VSL runtime/learning | Retain as sole execution core |
| `virtual_shaping_lab/vsl/runtime/learner_adapter.py` | Canonical runtime seam | keep | VSL runtime | Retain and enforce as only runtime learner seam |
| `virtual_shaping_lab/vsl/rollout/harness.py` | Runtime call site using adapter seam | keep | VSL rollout | Retain; keep adapter-only execution path |
| `virtual_shaping_lab/experiment/assemble.py` (`resolve_learner_spec` path) | Spec-resolution assembly bridge | bridge | Experiment assembly | Keep temporarily while runtime cleanup proceeds; no direct learner-step execution should be introduced |
| `virtual_shaping_lab/experiment/plan_builder.py` (`resolve_learner_spec`) | Plan-time spec resolution | bridge | Experiment planning | Keep as compatibility bridge; constrain to symbolic spec selection only |
| `virtual_shaping_lab/vsl/agent/learning/adapters.py` | Grammar/runtime config adapters | keep | VSL learning contracts | Retain as contract adapter layer (not execution bypass) |
| `virtual_shaping_lab/agents/learners/*` | Legacy learner implementations outside canonical VSL execution core | delete-later | Legacy cleanup | Remove after import/use audit and adapter fallback expiry documentation |
| `virtual_shaping_lab/agents/math_objects/*` | Legacy math objects tied to pre-VSL learner surfaces | delete-later | Legacy cleanup | Remove or isolate with explicit expiry once no runtime/import dependency remains |
| Tracked `__pycache__/` under `virtual_shaping_lab/agents/*` | Generated artifacts committed in tree | delete-now | Repo hygiene | Remove in slice 3 and enforce ignore policy |

---

## Deletion Notes (for Slice 2+)

- `delete-now` items should be removed with no behavior change and verified via targeted namespace/import tests.
- `delete-later` items require two checks before deletion:
  1. no import references in runtime/assembly/api execution paths
  2. no compatibility contract tests depending on those modules

---

## Single-Path Definition (V3.18.15)

For V3.18.15 closeout, learner execution is single-path only when:
- runtime stepping executes through `RuntimeLearnerAdapter -> LearnerBundle.step(...)`
- no alternate learner-step branch exists in `experiment/*`, `api/*`, or legacy `agents/*`
- non-canonical surfaces are either removed or explicitly marked as temporary non-execution bridges with expiry notes
