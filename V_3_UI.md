The core tension:

Hide the operator algebra enough to be usable, but expose it enough to teach.

The right solution is layered abstraction with progressive reveal, aligned to the V3 architecture.

## Core UI Principle

Users think in phenomena, not operators.

Preferred flow:

Phenomenon -> Experiment -> Behavior -> (Reveal) Operators -> (Reveal) Math

Not:

Operators -> Composition -> Behavior

## 1. Preset Mode: Behavior First

Default preset cards should present:

- what happens (plain language)
- what to observe (behavior/readout expectation)
- quick graph preview

Operator details remain hidden by default.

Behind the scenes, each preset binds:

- protocol
- learner family
- operator bundle
- parameter template

## 2. Progressive Reveal (Most Important)

Each preset should support four layers:

1. Intuition (default)
- plain language, timeline, expected graphs

2. Mechanism ("How it works")
- stimulus -> representation -> prediction -> error -> update
- no symbolic notation yet

3. Operator View ("Mathematical view")
- explicit operator sequence labels
- concise tooltips and mappings to mechanism layer

4. Full Algebra (advanced)
- trial-state and full pipeline view for expert users

## 3. Presets as Locked Recipes

Preset should be immutable as shipped:

- protocol
- learner
- operator set
- parameter defaults

Allowed actions:

- run
- inspect
- clone and edit in Builder Mode

## 4. Operator Visualization

Represent operators as pipeline nodes, not static text lists.

Each node should support:

- hover explanation
- click-to-expand details:
  - what it computes
  - which `TrialState` fields it reads/writes

Advanced view should show state flow per trial.

## 5. Behavior-to-Operator Explanation

Every graph should be explainable in operator terms.

On trial hover, show values like:

- prediction
- outcome
- error
- update effect

This links observed behavior directly to mechanism.

## 6. Preset Taxonomy by Operator Differences

Group presets by what changes in operator terms, for example:

- core learning
- stimulus interaction
- context effects
- attention/memory effects

This teaches operator structure implicitly.

## 7. "Why This Works" Panel

Each preset should include a short causal explanation grounded in mechanism/operator language.

Example:

"Prediction error is already near zero, so update to the new cue is minimal."

## 8. Builder Mode: Controlled Exposure

Builder Mode should expose:

- learner selection
- attention model choice
- trace/policy options

Builder Mode should not expose raw operator wiring controls.

## 9. Keep Operators Indirect in Controls

Prefer controls like:

- Learning rule: Rescorla-Wagner
- Learning rule: TD(lambda)
- Learning rule: Q-learning

Internally these map to operator tuples.

## 10. Visual Consistency

Use a stable concept-to-visual mapping for operator families across all UI surfaces.

## Final UI Architecture

Modes:

1. Preset Mode (default)
2. Teaching Mode (overlay)
3. Builder Mode (controlled editing)
4. Expert Mode (full pipeline and trial-state inspection)

## Final Insight

Operators should feel like explanations, not controls.

Users should understand behavior first, then mechanism, then operators.

## One-Sentence Design Principle

Design the UI so users learn operator algebra by explaining behavior, not by configuring raw algebra directly.
