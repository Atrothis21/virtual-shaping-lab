from dataclasses import dataclass, field
from typing import Any, Dict, Optional


def _require_fields(data: Dict[str, Any], required: tuple[str, ...], label: str) -> None:
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing required {label} fields: {', '.join(missing)}")


@dataclass(frozen=True)
class ErrorEnvelope:
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": dict(self.details),
        }


@dataclass(frozen=True)
class PlanResolveRequest:
    payload: Dict[str, Any]


@dataclass(frozen=True)
class PlanResolveResponse:
    status: str
    plan: Dict[str, Any]
    stable_hash: str
    lifecycle: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "plan": self.plan,
            "stable_hash": self.stable_hash,
            "lifecycle": dict(self.lifecycle),
        }


@dataclass(frozen=True)
class RunCreateRequest:
    payload: Dict[str, Any]


@dataclass(frozen=True)
class RunCreateResponse:
    status: str
    run_id: str
    state: str
    artifacts: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    lifecycle: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "state": self.state,
            "artifacts": self.artifacts,
            "metadata": dict(self.metadata),
            "lifecycle": dict(self.lifecycle),
        }


@dataclass(frozen=True)
class RunStatusResponse:
    status: str
    run_id: str
    state: str
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None
    lifecycle: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "state": self.state,
            "artifacts": dict(self.artifacts),
            "metadata": dict(self.metadata),
            "error": self.error,
            "lifecycle": dict(self.lifecycle),
        }


@dataclass(frozen=True)
class ReportCreateRequest:
    run_id: str
    preset: Optional[str] = None


@dataclass(frozen=True)
class ReportCreateResponse:
    status: str
    run_id: str
    artifacts: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    lifecycle: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "artifacts": self.artifacts,
            "metadata": dict(self.metadata),
            "lifecycle": dict(self.lifecycle),
        }


def _lifecycle(state: str, next_actions: list[str]) -> Dict[str, Any]:
    return {
        "state": state,
        "next_actions": list(next_actions),
    }


def build_run_create_response(
    run_id: str,
    artifacts: Dict[str, Any],
    state: str = "completed",
    *,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    lifecycle_state = "RunComplete" if state == "completed" else "RunInProgress"
    response = RunCreateResponse(
        status="success",
        run_id=run_id,
        state=state,
        artifacts=artifacts,
        metadata=metadata or {},
        lifecycle=_lifecycle(lifecycle_state, ["get_run_status", "create_report"]),
    ).to_dict()
    _require_fields(
        response,
        ("status", "run_id", "state", "artifacts", "metadata", "lifecycle"),
        "RunCreateResponse",
    )
    return response


def build_plan_resolve_response(plan: Dict[str, Any], stable_hash: str) -> Dict[str, Any]:
    response = PlanResolveResponse(
        status="success",
        plan=plan,
        stable_hash=stable_hash,
        lifecycle=_lifecycle("PlanResolved", ["create_run"]),
    ).to_dict()
    _require_fields(response, ("status", "plan", "stable_hash", "lifecycle"), "PlanResolveResponse")
    return response


def build_run_status_response(
    run_id: str,
    state: str,
    *,
    artifacts: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    lifecycle_state = "RunComplete" if state == "completed" else "RunInProgress"
    response = RunStatusResponse(
        status="success",
        run_id=run_id,
        state=state,
        artifacts=artifacts or {},
        metadata=metadata or {},
        error=error,
        lifecycle=_lifecycle(lifecycle_state, ["create_report"] if state == "completed" else ["get_run_status"]),
    ).to_dict()
    _require_fields(
        response,
        ("status", "run_id", "state", "artifacts", "metadata", "error", "lifecycle"),
        "RunStatusResponse",
    )
    return response


def build_report_create_response(
    run_id: str,
    artifacts: Dict[str, Any],
    *,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    response = ReportCreateResponse(
        status="success",
        run_id=run_id,
        artifacts=artifacts,
        metadata=metadata or {},
        lifecycle=_lifecycle("ReportComplete", ["view_report", "resolve_plan"]),
    ).to_dict()
    _require_fields(response, ("status", "run_id", "artifacts", "metadata", "lifecycle"), "ReportCreateResponse")
    return response
