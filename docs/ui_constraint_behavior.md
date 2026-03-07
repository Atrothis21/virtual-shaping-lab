# UI Constraint Behavior (First-Pass)

## Purpose
Define canonical UI responses to machine-checkable constraint symbols so behavior is consistent across first-pass surfaces.

Surfaces covered:
- phase controls
- protocol selection/config controls
- report/template controls
- runtime/debug controls

## Canonical Actions
- `hide`
- `disable`
- `warn`
- `auto-correct` (strictly limited; see guardrails section)

## Action Semantics

### `hide`
- Use when:
  - control is not applicable in the current mode/context
  - exposing the control would imply unsupported capability
- UI behavior:
  - control is not rendered
  - no dead/disabled placeholder unless discoverability is required by product spec

### `disable`
- Use when:
  - control is relevant but temporarily invalid due to unmet prerequisites
- UI behavior:
  - control is rendered disabled
  - disabled reason is visible (tooltip, inline note, or helper text)

### `warn`
- Use when:
  - action is valid but has trade-offs (performance, interpretability, degraded UX)
- UI behavior:
  - allow action
  - show non-blocking warning with consequence summary

### `auto-correct`
- Use when:
  - deterministic normalization is safe and non-semantic
- UI behavior:
  - apply correction deterministically
  - show explicit "value adjusted" notice

## Cross-Surface Consistency Rule
- The same constraint symbol must map to the same default action on all covered surfaces.
- Any exception must be documented with:
  - symbol
  - surface
  - why default mapping is unsafe
  - compensating UX behavior

## Surface Mapping Guidance
- Phases/protocols:
  - prefer `hide` for inapplicable structural options
  - prefer `disable` for sequence/context prerequisites
- Reports:
  - prefer `disable` for unavailable report controls pending run/report readiness
  - prefer `warn` for costly optional views
- Runtime/debug:
  - prefer `warn` for high-volume debug options
  - prefer `hide` for unsupported debug modes in current run mode

## Auto-Correct Guardrails (Strict)

Auto-correct is allowed only when all conditions below are true:
- change is deterministic
- change is non-semantic (does not alter experiment meaning/contingency intent)
- corrected value is directly implied by canonical constraints/catalog metadata
- user receives immediate visible notice

Allowed auto-correct examples:
- canonical key normalization (`FI_10` -> canonical normalized key, case/hyphen normalization)
- clamping numeric values to declared hard bounds when user input exceeds domain
- clearing stale dependent UI selections after catalog refresh (for example a removed report option)
- resetting derived display-only controls when upstream mode changes

Prohibited auto-correct examples:
- changing protocol/phase semantics automatically (for example swapping schedule family)
- silently changing reinforcement/reward or contingency-defining parameters
- replacing user-selected phenomenon intent with a different phenomenon
- any correction that changes scientific interpretation without explicit user confirmation

Mandatory UX when auto-correct is applied:
- inline notice adjacent to affected control(s)
- before/after value visibility
- short reason tied to constraint/catalog source
- one-click undo if technically feasible; otherwise explicit manual edit affordance

## Message Requirements
- Constraint-driven UI messaging must include:
  - affected control label
  - constraint implication (what is restricted and why)
  - recovery path (if user can satisfy prerequisite)

## Non-Goals
- This document does not define backend constraint symbols themselves.
- This document does not override version mismatch behavior rules.
