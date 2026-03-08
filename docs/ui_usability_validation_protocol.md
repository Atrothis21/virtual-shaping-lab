# UI Usability Validation Protocol (V2.17.5)

## Purpose
Provide a lightweight, repeatable check that first-open usability changes are validated by observed behavior, not only internal design review.

## Participant Profile
- 1 new/fresh user (no prior VSL workflow context preferred).
- 1 returning user (has previously run preset or report flow).

## Session Setup
- Start from `http://127.0.0.1:8000/ui/index.html` with a clean browser refresh.
- Do not explain route architecture or implementation details before tasks.
- Ask participant to think out loud while navigating.

## Task Script
1. First-open orientation:
   - Prompt: "What would you do first?"
   - Pass signal: user identifies `Run preset` within 5 seconds.
2. Quick success:
   - Prompt: "Run a preset and get to a run status view."
   - Pass signal: user completes flow without detouring to builder/legacy links.
3. Builder comprehension:
   - Prompt: "Now build your own experiment."
   - Pass signal: user recognizes guided builder sequence (`Start -> Configure phases -> Runtime/report choices -> Resolve plan`).
4. Advanced/debug discoverability:
   - Prompt: "Find diagnostics, then hide them."
   - Pass signal: user can open/close advanced panel without losing context.
5. Recovery path:
   - Prompt: "If something fails, where would you go next?"
   - Pass signal: user identifies retry/presets/builder navigation options.

## Data Capture Template
- Timestamp:
- Build/branch:
- Participant type: `fresh` | `returning`
- Task outcomes:
  - T1 first-open orientation: `pass` | `fail`
  - T2 quick success: `pass` | `fail`
  - T3 builder comprehension: `pass` | `fail`
  - T4 advanced/debug: `pass` | `fail`
  - T5 recovery path: `pass` | `fail`
- Hesitation points (time + screen + action):
- Confusing terms:
- Mis-clicks:
- Follow-up recommendations:

## Acceptance Rule
- Slice accepted when:
  - T1 and T2 are `pass` for both participants.
  - No blocker-level confusion is observed on T3-T5.
  - Follow-up items are recorded with explicit owner/slice target.
