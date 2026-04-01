# V3.21.0 Legacy Protocol Path Inventory

## Purpose
Establish a concrete ownership matrix for protocol-like runtime paths before canonical `vsl/protocol/*` implementation.

This inventory follows `agent_protocol_interaction.md` boundary rules:
- Protocol/environment owns: emission, consequence, advance, stop, time progression.
- Agent owns: observe, predict, act, learn, advance_internal_time.
- Experiment-protocol must provide outcomes, not internal learner error/update terms.

---

## Scope Scanned
- `virtual_shaping_lab/experiment/phases/*`
- `virtual_shaping_lab/experiment/protocol_phase_boundary.py`
- `virtual_shaping_lab/experiment/runner.py`
- `virtual_shaping_lab/experiment/trial_executor.py`
- `virtual_shaping_lab/vsl/rollout/harness.py`

---

## Ownership Matrix

### Keep (Canonical Runtime Ownership)
- `virtual_shaping_lab/vsl/rollout/harness.py`
  - Keep as runtime integration shell.
  - Must remain protocol-seam consumer once `RuntimeProtocolAdapter` exists.
- `virtual_shaping_lab/experiment/protocol_phase_boundary.py`
  - Keep as explicit experiment/protocol contract surface.
- `virtual_shaping_lab/experiment/phases/catalog_runtime.py`
  - Keep as registry/selection mapping input for runtime protocol resolution.

### Bridge (Compatibility Surface, Expiry Required)
- `virtual_shaping_lab/experiment/phases/public.py`
  - Bridge for existing call sites while runtime protocol adapter is introduced.
- `virtual_shaping_lab/experiment/runner.py`
  - Bridge legacy orchestrator entrypoints; must delegate to canonical runtime seams.
- `virtual_shaping_lab/experiment/trial_executor.py`
  - Bridge for older execution flow; should not reintroduce protocol-side agent internals.

### Delete-Now (Once V3.21 Runtime Protocol Seam Lands)
- Direct phase-local emission/consequence logic in concrete phase modules that bypass a protocol seam:
  - `acquisition.py`
  - `nonreinforcement.py`
  - `differential_acquisition.py`
  - `compound_acquisition.py`
  - `compound_nonreinforcement.py`
  - `operant_acquisition.py`
  - `concurrent_schedule.py`
  - `probe.py`
  - `criterion_shift.py`
  - `context_shift.py`
  - `series_helpers.py`
  - `learning_helpers.py` (retain learner dispatch helper only if still needed; no protocol ownership here)

### Delete-Later (After Runtime Migration and CI Guardrails Are Green)
- `virtual_shaping_lab/experiment/phases/catalog.py`
  - Legacy/dual catalog path if superseded by runtime protocol registry.
- Legacy factory-style wiring in non-vsl orchestration paths discovered during V3.21.10+.

---

## Boundary Risk Notes
- High risk: protocol-side computation of learner internals (prediction error, weight updates) must remain forbidden.
- High risk: agent-side mutation of phase/protocol timeline state must remain forbidden.
- Medium risk: hidden learn-inside-pre-outcome helper wrappers.
- Medium risk: parallel environment loops that bypass single canonical protocol seam.

---

## Migration Guidance for V3.21.0+
- First establish canonical symbolic ownership under `virtual_shaping_lab/vsl/protocol/*`.
- Then route runtime environment stepping through one protocol adapter seam.
- Preserve typed boundaries (`TaskInput`, `Action`, `Outcome`, `TrialRecord`) at integration points.
- Track each bridge path with owner + expiry note in PR summaries until removed.
