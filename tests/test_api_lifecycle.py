import pytest

from api.lifecycle import (
    LIFECYCLE_PLAN_DRAFT,
    LIFECYCLE_PLAN_RESOLVED,
    LIFECYCLE_REPORT_COMPLETE,
    LIFECYCLE_RUN_COMPLETE,
    LIFECYCLE_RUN_IN_PROGRESS,
    validate_lifecycle_transition,
)
from api.services import RunStatusStore


def test_validate_lifecycle_transition_accepts_valid_edges():
    validate_lifecycle_transition(None, LIFECYCLE_RUN_COMPLETE)
    validate_lifecycle_transition(LIFECYCLE_PLAN_DRAFT, LIFECYCLE_PLAN_RESOLVED)
    validate_lifecycle_transition(LIFECYCLE_PLAN_RESOLVED, LIFECYCLE_RUN_IN_PROGRESS)
    validate_lifecycle_transition(LIFECYCLE_RUN_IN_PROGRESS, LIFECYCLE_RUN_COMPLETE)
    validate_lifecycle_transition(LIFECYCLE_RUN_COMPLETE, LIFECYCLE_REPORT_COMPLETE)


def test_validate_lifecycle_transition_rejects_invalid_edges():
    with pytest.raises(ValueError):
        validate_lifecycle_transition(None, LIFECYCLE_PLAN_RESOLVED)
    with pytest.raises(ValueError):
        validate_lifecycle_transition(LIFECYCLE_PLAN_DRAFT, LIFECYCLE_REPORT_COMPLETE)
    with pytest.raises(ValueError):
        validate_lifecycle_transition(LIFECYCLE_REPORT_COMPLETE, LIFECYCLE_RUN_COMPLETE)


def test_run_status_store_enforces_transition_guard():
    run_id = "lifecycle-test-run"
    # reset any previous test residue
    RunStatusStore.clear(run_id)

    RunStatusStore.set(run_id, state="completed", artifacts={})
    # idempotent write is allowed
    RunStatusStore.set(run_id, state="completed", artifacts={})
    with pytest.raises(ValueError):
        # backward transition is invalid
        RunStatusStore.set(run_id, state=LIFECYCLE_RUN_IN_PROGRESS, artifacts={})
