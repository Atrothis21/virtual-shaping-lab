# V2.18.5 Summary - Assembly Ownership Unification and Policy-Semantics Composition

## Overview
V2.18.5 tightens assembly as the single composition root and reduces the remaining classical/operant split to policy semantics.

Primary outcomes:
- assembly now sources representation, learner, and policy from canonical agent-owned structure first
- typed plan `agent_spec.learning` is now treated as the learner ownership source during assembly
- policy construction is now unified through a single policy-driven agent stack
- actionless/classical paths now use `NullPolicy` semantics through assembly instead of a separate construction path
- plan fixtures and assembly tests now reflect nested ownership rather than flattened settings assumptions

This slice turns assembly into a cleaner ownership-preserving composition root instead of a place where canonical ownership is partially flattened again.

---

## Canonical Ownership Sourcing

### Agent-Owned Construction
Assembly now prefers nested agent-owned specs when reconstructing runtime config from plans:
- representation from `agent_spec.representation`
- learner from `agent_spec.learning.rule`
- attention state/config from `agent_spec.learning.attention`
- policy from `agent_spec.policy`

This is the most important structural change in V2.18.5:
- runtime object ownership now matches canonical payload ownership more closely during assembly itself

### Plan Builder Alignment
The plan builder now carries learner ownership under:
- `agent_spec.learning.rule`
- `agent_spec.learning.params`
- `agent_spec.learning.attention`

This reduces the amount of semantic flattening that previously happened between config, plan, and assembly.

Net effect:
- the `F = pi o L o R` ownership model is more visible in the composition root

---

## Assembly as Composition Root

### Reduced Dependence on Flattened Settings
V2.18.5 shifts assembly toward typed ownership sources and away from direct dependence on:
- `settings["learner"]`
- `settings["agent"]`
- `settings["representation"]`
- `settings["policy"]`

Compatibility fallbacks still exist, but they are no longer the preferred ownership path.

### Procedural-Only Phase Params
This slice preserves the boundary that:
- phase/program params remain procedural
- representation/learner/policy ownership stays outside phase params

That keeps program structure from silently reclaiming cognitive/control ownership.

---

## Policy-Semantics Unification

### Single Agent Stack
Assembly now uses a single policy-driven stack rather than separate classical/operant construction branches.

Policy behavior now resolves as:
- explicit policy -> built policy instance
- no explicit policy -> `NullPolicy`

This reduces the architectural split to the thing that actually matters:
- whether the control path has an action-producing policy or an actionless/null policy

### NullPolicy for Actionless Paths
Classical/actionless paths now receive `NullPolicy` semantics directly through assembly.

This means:
- actionless control is represented by a policy object rather than a separate agent-construction regime
- classical and operant paths differ more by control semantics than by agent architecture shape

Net effect:
- the codebase is incrementally moving toward “one composed agent, different policies” rather than “different agent assembly families”

---

## Test and Fixture Realignment

### Typed Plan Fixture Updates
Assembly tests were updated so typed plan fixtures now express ownership through:
- `agent_spec`
- `runtime_spec`

instead of relying on flattened settings-only construction assumptions.

This matters because the tests now validate the intended architecture instead of migration-era convenience paths.

### New Regression
Added/locked:
- classical/actionless assembly yields `NullPolicy` semantics

This protects the unification step from regressing back into a branchy classical-only construction path.

---

## Validation

### Ownership-Sourcing Gates
Validated through:
- `tests/test_assemble_coverage.py`
- `tests/test_factories.py`
- `tests/test_agents.py`

These cover:
- typed ownership sourcing during assembly
- representation/policy/learner construction seams
- compatibility behavior under the new ownership layout

### Policy-Semantics Gates
Validated through:
- `tests/test_assemble_coverage.py`
- `tests/test_runner_protocol.py`
- `tests/test_interface_policy.py`

These cover:
- `NullPolicy` actionless behavior
- policy-driven timed control paths
- unified policy semantics under runtime execution

---

## Net State After V2.18.5

- assembly is more clearly the single composition root
- runtime object ownership is sourced from canonical agent-owned structure more directly
- typed plans now carry learner ownership in a way assembly actually consumes
- classical and operant assembly are less architecturally distinct and more policy-semantics-driven
- flattened settings assumptions have been reduced further in runtime construction paths

V2.18.5 therefore closes one of the largest remaining gaps between the canonical ownership model and the actual assembly implementation.

## Validation Commands

Targeted gates exercised during implementation:
- `python -m pytest -q tests/test_assemble_coverage.py tests/test_factories.py tests/test_agents.py`
- `python -m pytest -q tests/test_assemble_coverage.py tests/test_runner_protocol.py tests/test_interface_policy.py`
