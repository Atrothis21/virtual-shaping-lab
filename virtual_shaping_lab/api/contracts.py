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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "plan": self.plan,
            "stable_hash": self.stable_hash,
        }


@dataclass(frozen=True)
class RunCreateRequest:
    payload: Dict[str, Any]


@dataclass(frozen=True)
class RunCreateResponse:
    status: str
    run_id: str
    artifacts: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "artifacts": self.artifacts,
        }


@dataclass(frozen=True)
class RunStatusResponse:
    status: str
    run_id: str
    state: str
    artifacts: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "state": self.state,
            "artifacts": dict(self.artifacts),
            "error": self.error,
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "run_id": self.run_id,
            "artifacts": self.artifacts,
        }


def build_run_create_response(run_id: str, artifacts: Dict[str, Any]) -> Dict[str, Any]:
    response = RunCreateResponse(
        status="success",
        run_id=run_id,
        artifacts=artifacts,
    ).to_dict()
    _require_fields(response, ("status", "run_id", "artifacts"), "RunCreateResponse")
    return response


def build_plan_resolve_response(plan: Dict[str, Any], stable_hash: str) -> Dict[str, Any]:
    response = PlanResolveResponse(
        status="success",
        plan=plan,
        stable_hash=stable_hash,
    ).to_dict()
    _require_fields(response, ("status", "plan", "stable_hash"), "PlanResolveResponse")
    return response
