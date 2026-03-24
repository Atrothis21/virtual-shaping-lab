# api/run.py

import copy
import traceback

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.contracts import (
    build_plan_resolve_response,
    build_report_create_response,
    build_run_create_response,
    build_run_status_response,
)
from api.errors import raise_internal_error, raise_not_found, raise_validation_error
from api.extensions import ExtensionCatalog
from api.services import PlanService, ReportService, RunService
from paths import REPORTS_DIR, UI_DIR
from ui.contracts.preset_basis_authoring import (
    PresetBasisAuthoringError,
    build_acquisition_basis_authoring_contract,
    materialize_acquisition_basis_payload,
)
from ui.validate_payload import validate_payload


app = FastAPI(title="Virtual Shaping Lab API")

app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")

reports_dir = REPORTS_DIR
reports_dir.mkdir(parents=True, exist_ok=True)
app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")


@app.get("/")
def root():
    return FileResponse(str(UI_DIR / "index.html"))


@app.get("/catalog/extensions")
def extensions_api():
    try:
        return {
            "status": "success",
            "extensions": ExtensionCatalog.snapshot(),
            "versions": ExtensionCatalog.version_info(),
        }
    except Exception as exc:
        raise_internal_error(
            "Extension catalog discovery failed.",
            details={"reason": str(exc)},
        )


@app.post("/plan")
def plan_api(payload: dict):
    try:
        raw_payload = copy.deepcopy(payload)
        validate_payload(raw_payload)
    except Exception as exc:
        raise_validation_error(
            "Payload validation failed.",
            details={"reason": str(exc)},
        )

    try:
        resolved = PlanService.resolve(raw_payload)
        return build_plan_resolve_response(
            plan=resolved["plan"],
            stable_hash=resolved["stable_hash"],
        )
    except Exception as exc:
        raise_internal_error(
            "Plan resolution failed.",
            details={"reason": str(exc)},
        )


@app.post("/run")
def run_api(payload: dict):
    print("=== /run called ===", flush=True)

    try:
        raw_payload = copy.deepcopy(payload)
        expected_plan_hash = raw_payload.pop("expected_plan_hash", None)
        validate_payload(raw_payload)
        print("Payload validated", flush=True)
    except Exception as exc:
        raise_validation_error(
            "Payload validation failed.",
            details={"reason": str(exc)},
        )

    try:
        print("Executing RunService", flush=True)
        result = RunService.execute(
            raw_payload,
            reports_dir=reports_dir,
            expected_plan_hash=expected_plan_hash,
        )

        print(f"Run complete ({result['record_count']} records)", flush=True)
        print("=== /run completed successfully ===", flush=True)

        return build_run_create_response(
            run_id=result["run_id"],
            artifacts=result["artifacts"],
            state=result["state"],
            metadata=result["metadata"],
        )

    except ValueError as exc:
        reason = str(exc)
        if "Plan hash mismatch" in reason:
            raise_validation_error(
                "Plan hash mismatch.",
                details={
                    "reason": reason,
                    "hint": "Re-resolve the plan and run again.",
                },
            )
        print("=== /run ERROR ===", flush=True)
        traceback.print_exc()
        raise_internal_error(
            "Run execution failed.",
            details={"reason": reason},
        )
    except Exception as exc:
        print("=== /run ERROR ===", flush=True)
        traceback.print_exc()
        raise_internal_error(
            "Run execution failed.",
            details={"reason": str(exc)},
        )


@app.get("/catalog/presets/acquisition/basis-authoring")
def acquisition_basis_authoring_contract_api():
    try:
        return build_acquisition_basis_authoring_contract()
    except Exception as exc:
        raise_internal_error(
            "Acquisition basis authoring contract generation failed.",
            details={"reason": str(exc)},
        )


@app.post("/catalog/presets/acquisition/materialize-basis")
def materialize_acquisition_basis_api(payload: dict):
    try:
        return materialize_acquisition_basis_payload(payload)
    except PresetBasisAuthoringError as exc:
        raise_validation_error(
            "Acquisition basis authoring payload validation failed.",
            details={"reason": str(exc)},
        )
    except Exception as exc:
        raise_internal_error(
            "Acquisition basis payload materialization failed.",
            details={"reason": str(exc)},
        )


@app.get("/runs/{run_id}")
def run_status_api(run_id: str):
    status = RunService.status(run_id)
    if status is None:
        raise_not_found(
            f"Run '{run_id}' not found.",
            details={"run_id": run_id},
        )
    return build_run_status_response(
        run_id=run_id,
        state=status["state"],
        artifacts=status.get("artifacts", {}),
        metadata=status.get("metadata", {}),
        error=status.get("error"),
    )


@app.post("/runs/{run_id}/report")
def run_report_api(run_id: str, payload: dict | None = None):
    try:
        preset_override = None
        if payload and isinstance(payload, dict):
            preset_override = payload.get("preset")
        result = ReportService.create_default(
            run_id,
            reports_dir=reports_dir,
            preset_override=preset_override,
        )
        return build_report_create_response(
            run_id=result["run_id"],
            artifacts=result["artifacts"],
            metadata=result["metadata"],
        )
    except FileNotFoundError as exc:
        raise_not_found(
            str(exc),
            details={"run_id": run_id},
        )
    except Exception as exc:
        raise_internal_error(
            "Report generation failed.",
            details={"reason": str(exc), "run_id": run_id},
        )
