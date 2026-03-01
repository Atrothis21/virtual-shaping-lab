"""Lifecycle contract constants and transition validation."""

from __future__ import annotations


LIFECYCLE_PLAN_DRAFT = "PlanDraft"
LIFECYCLE_PLAN_RESOLVED = "PlanResolved"
LIFECYCLE_RUN_IN_PROGRESS = "RunInProgress"
LIFECYCLE_RUN_COMPLETE = "RunComplete"
LIFECYCLE_REPORT_COMPLETE = "ReportComplete"
LIFECYCLE_FAILURE = "Failure"


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    LIFECYCLE_PLAN_DRAFT: {LIFECYCLE_PLAN_RESOLVED, LIFECYCLE_FAILURE},
    LIFECYCLE_PLAN_RESOLVED: {LIFECYCLE_RUN_IN_PROGRESS, LIFECYCLE_RUN_COMPLETE, LIFECYCLE_FAILURE},
    LIFECYCLE_RUN_IN_PROGRESS: {LIFECYCLE_RUN_COMPLETE, LIFECYCLE_FAILURE},
    LIFECYCLE_RUN_COMPLETE: {LIFECYCLE_REPORT_COMPLETE, LIFECYCLE_FAILURE},
    LIFECYCLE_REPORT_COMPLETE: set(),
    LIFECYCLE_FAILURE: set(),
}


def validate_lifecycle_transition(previous_state: str | None, next_state: str) -> None:
    if previous_state is None:
        if next_state in {LIFECYCLE_RUN_IN_PROGRESS, LIFECYCLE_RUN_COMPLETE, LIFECYCLE_FAILURE}:
            return
        raise ValueError(f"Invalid initial lifecycle state '{next_state}'.")

    if previous_state not in ALLOWED_TRANSITIONS:
        raise ValueError(f"Unknown previous lifecycle state '{previous_state}'.")

    if next_state not in ALLOWED_TRANSITIONS:
        raise ValueError(f"Unknown next lifecycle state '{next_state}'.")

    # Idempotent writes are allowed (e.g., re-persisting completed status).
    if previous_state == next_state:
        return

    if next_state not in ALLOWED_TRANSITIONS[previous_state]:
        raise ValueError(
            f"Invalid lifecycle transition '{previous_state}' -> '{next_state}'."
        )
