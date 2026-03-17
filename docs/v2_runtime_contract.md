# V2 Runtime Contract

## Purpose
This document is the closeout-facing description of the final V2 runtime contract.

It is intended to answer four questions directly:
- what the canonical payload shape is
- how ownership is split across the system
- how execution flows from payload to analysis
- how the runtime behaves when legacy payloads are submitted

---

## End-to-End Flow

The finalized V2 execution path is:

1. payload
2. config
3. plan
4. assembly
5. runtime
6. records
7. analysis/report

In concrete terms:

1. canonical payload is validated
2. `ExperimentConfig` parses canonical ownership sections
3. `ExperimentPlan` captures deterministic replay identity
4. assembly constructs representation, learner, policy, composed agent, and runtime units
5. runner executes runtime units with deterministic seed-governed behavior
6. runtime emits finalized records
7. analysis/report consumes records and canonical artifacts only

The corresponding implementation seams are:
- payload validation: `virtual_shaping_lab/experiment/payload_contract.py`
- config: `virtual_shaping_lab/experiment/config.py`
- plan: `virtual_shaping_lab/experiment/plan_builder.py`
- assembly: `virtual_shaping_lab/experiment/assemble.py`
- runtime: `virtual_shaping_lab/experiment/runner.py`, `virtual_shaping_lab/experiment/trial_executor.py`
- records: `virtual_shaping_lab/experiment/runtime_records.py`
- analysis/report: `virtual_shaping_lab/analysis/*`

---

## Canonical Payload

The canonical runtime payload shape is:

```json
{
  "experiment": {
    "program": {
      "phases": [
        {
          "name": "Acquisition",
          "protocol": "acquisition",
          "stimuli": { "cs_plus": ["tone"] },
          "params": { "n_trials": 10, "alpha": 0.2, "gamma": 0.0 },
          "trials": 10
        }
      ]
    },
    "agent": {
      "name": "classical_agent",
      "representation": {
        "name": "vector_elemental",
        "params": {
          "stimuli": ["tone"],
          "max_compound_size": 2
        }
      },
      "learning": {
        "rule": "rescorla_wagner",
        "params": {},
        "attention": {
          "initial": { "tone": { "attention": 1.0 } },
          "config": { "name": "none", "params": {} }
        }
      },
      "policy": null
    },
    "runtime": {
      "seed": 7,
      "update_mode": "trial",
      "record_mode": "trial"
    }
  },
  "report": {
    "preset": "acquisition"
  }
}
```

Non-negotiable runtime rules:
- runtime accepts canonical payloads only
- `experiment.program.phases` must be present and non-empty
- each phase must include integer `trials`
- canonical ownership is:
  - `experiment.program`
  - `experiment.agent.representation`
  - `experiment.agent.learning`
  - `experiment.agent.policy`
  - `experiment.runtime`

---

## Ownership Table

| Ownership Domain | Canonical Path | Responsibility |
|---|---|---|
| Program | `experiment.program` | behavioral program, phases, contingencies, trial counts |
| Representation | `experiment.agent.representation` | observation encoding, context, similarity, salience, temporal basis |
| Learning | `experiment.agent.learning` | value update rule, prediction error, attention, learner parameters |
| Policy | `experiment.agent.policy` | action-selection semantics |
| Runtime | `experiment.runtime` | seed, update mode, record mode, execution controls |
| Analysis | persisted records + canonical artifacts | metrics, figures, reports |

Rules:
- phase params remain procedural
- program must not own representation/learner/policy state
- representation must not own learner or policy state
- learner must not own representation or runtime state
- runtime must not redefine cognition semantics

---

## Cognitive Pipeline

The V2 cognitive pipeline is fixed:

`observation -> representation -> learner -> policy -> action`

This corresponds to:
- `R`: representation
- `L`: learner
- `pi`: policy

The runtime/assembly contract is therefore:

`F = pi o L o R`

Implications:
- representation transforms observations into encoded state
- learner owns prediction/value state and update dynamics
- policy reads state/value and selects actions
- analysis reads emitted records, not live cognitive objects

---

## Deterministic Runtime Contract

V2 guarantees deterministic replay given:
- identical canonical payload
- identical version metadata
- identical seed

Determinism must hold for:
- record emission order
- prediction error values
- learner weight-update trajectories
- seeded policy action selection
- seeded schedule stochasticity

Allowed stochasticity is runtime-governed only:
- policy exploration
- schedule stochasticity
- explicit runtime stochastic events

Randomness must not originate from:
- representation mechanisms
- learner internals outside runtime-owned RNG
- protocol logic using ad hoc generators
- analysis/report code

---

## Records Boundary

Records are the stable public boundary between runtime and analysis.

Minimum required finalized fields:
- `step`
- `trial`
- `tick`
- `stimulus`
- `action`
- `reward`
- `prediction`
- `prediction_error`
- `policy_state`

Optional fields may include:
- `weights`
- `attention`
- `feature_vector`
- mechanism/debug metadata

Analysis and reporting consume records and canonical artifacts only.

---

## Artifact Contract

Each run artifact set must include canonical reproducibility identity.

Canonical artifact expectations:
- `payload.json` is canonical-only
- `records.json` is finalized to minimum schema
- `mechanism_provenance.json` records resolved mechanism stack
- `artifact_identity.json` records:
  - `engine_version`
  - `record_schema_version`
  - `plan_hash`
  - `seed_identity`
  - `mechanism_identity`

Report regeneration is artifact-driven:
- canonical payload
- persisted records
- report template configuration
- artifact metadata

It does not require re-executing runtime.

---

## Legacy Payload Hard-Fail Behavior

Legacy payloads are no longer accepted at runtime.

The runtime rejects:
- legacy-only payloads
- mixed canonical/legacy payloads
- malformed canonical phase structures
- canonical payloads missing required ownership sections

Expected hard-fail classes include:
- missing `experiment`
- missing `report`
- missing `experiment.program`
- missing `experiment.agent`
- missing `experiment.runtime`
- missing or invalid `experiment.program.phases`
- missing or invalid phase `trials`

The intended operational rule is:
- legacy payload adapters may exist for migration utilities or test fixture construction
- runtime entrypoints must fail hard on legacy payload submission

---

## V2 Boundary

V2 remains a virtual behavioral lab simulator first.

V2 does not introduce a first-class environment abstraction.
In V2:
- protocols and phases remain the behavioral program layer
- runtime executes that program directly
- analysis/report interprets emitted records

Deferred to V3:
- environment objects
- transition/state abstractions
- observation/action spaces as first-class architecture
- episode/horizon semantics as primary organizing structure

---

## Summary

The finalized V2 runtime contract is:
- canonical payload in
- deterministic plan and runtime execution
- composed agent with explicit `R / L / pi` ownership
- stable records out
- artifact-driven analysis and report regeneration

This is the architecture that documentation, tests, persisted artifacts, and runtime behavior now agree on.
