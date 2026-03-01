from __future__ import annotations

from fastapi import HTTPException

from api.contracts import ErrorEnvelope


def raise_validation_error(message: str, *, details: dict | None = None) -> None:
    envelope = ErrorEnvelope(
        code="validation_error",
        message=message,
        details=details or {},
    ).to_dict()
    raise HTTPException(status_code=400, detail=envelope)


def raise_not_found(message: str, *, details: dict | None = None) -> None:
    envelope = ErrorEnvelope(
        code="not_found",
        message=message,
        details=details or {},
    ).to_dict()
    raise HTTPException(status_code=404, detail=envelope)


def raise_internal_error(message: str, *, details: dict | None = None) -> None:
    envelope = ErrorEnvelope(
        code="internal_error",
        message=message,
        details=details or {},
    ).to_dict()
    raise HTTPException(status_code=500, detail=envelope)

