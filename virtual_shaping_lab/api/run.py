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
    build_preset_basis_authoring_contract,
    materialize_preset_basis_payload,
    materialize_acquisition_basis_payload,
)
from ui.contracts.tuple_authoring_api import (
    TupleAuthoringAPIError,
    build_tuple_guided_catalog,
    materialize_tuple_authoring_payload,
)
from ui.contracts.behavioral_compatibility_engine import (
    evaluate_behavioral_compatibility,
)
from ui.contracts.preset_ux_catalog import (
    build_preset_ux_catalog,
)
from ui.contracts.preset_route_migration import (
    get_preset_route_migration_contract,
)
from ui.contracts.smart_preset_projection import (
    SmartPresetProjectionValidationError,
    build_smart_preset_catalog,
    project_smart_preset_to_tuple_payload,
)
from ui.validate_payload import validate_payload


app = FastAPI(title="Virtual Shaping Lab API")

app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")

reports_dir = REPORTS_DIR
reports_dir.mkdir(parents=True, exist_ok=True)
app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")


_PAYLOAD_MODE_ERROR_DETAILS = {
    "accepted_payload_modes": [
        "canonical_v3",
        "canonical_v3_with_basis_authoring_metadata",
    ],
    "rejected_payload_modes": [
        "legacy_flat_experiment",
        "mixed_legacy_and_canonical",
    ],
}


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
        reason = str(exc)
        if "Mixed payload shape detected" in reason or "Legacy payload shape is no longer accepted" in reason:
            raise_validation_error(
                "Mixed or legacy payload mode is not supported.",
                details={
                    "reason": reason,
                    "hint": "Submit canonical experiment.program/experiment.agent/experiment.runtime payloads only.",
                    **_PAYLOAD_MODE_ERROR_DETAILS,
                },
            )
        raise_validation_error(
            "Payload validation failed.",
            details={"reason": reason},
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


@app.get("/catalog/presets/{preset_id}/basis-authoring")
def preset_basis_authoring_contract_api(preset_id: str):
    try:
        return build_preset_basis_authoring_contract(preset_id)
    except PresetBasisAuthoringError as exc:
        raise_validation_error(
            "Preset basis authoring contract generation failed.",
            details={"reason": str(exc), "preset_id": preset_id},
        )
    except Exception as exc:
        raise_internal_error(
            "Preset basis authoring contract generation failed.",
            details={"reason": str(exc), "preset_id": preset_id},
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


@app.post("/catalog/presets/{preset_id}/materialize-basis")
def materialize_preset_basis_api(preset_id: str, payload: dict):
    try:
        merged = dict(payload or {})
        merged["preset_id"] = preset_id
        return materialize_preset_basis_payload(merged)
    except PresetBasisAuthoringError as exc:
        raise_validation_error(
            "Preset basis authoring payload validation failed.",
            details={"reason": str(exc), "preset_id": preset_id},
        )
    except Exception as exc:
        raise_internal_error(
            "Preset basis payload materialization failed.",
            details={"reason": str(exc), "preset_id": preset_id},
        )


@app.get("/catalog/tuple-authoring")
def tuple_authoring_catalog_api(arrangement: str | None = None, task: str | None = None):
    try:
        return build_tuple_guided_catalog(arrangement=arrangement, task=task)
    except TupleAuthoringAPIError as exc:
        raise_validation_error(
            "Tuple guided catalog contract generation failed.",
            details={"reason": str(exc), "arrangement": arrangement, "task": task},
        )
    except Exception as exc:
        raise_internal_error(
            "Tuple guided catalog contract generation failed.",
            details={"reason": str(exc), "arrangement": arrangement, "task": task},
        )


@app.post("/catalog/tuple-authoring/materialize")
def materialize_tuple_authoring_api(payload: dict):
    try:
        raw_payload = dict(payload or {})
        uses_deprecated_shape = (
            "preset_id" in raw_payload
            and not any(key in raw_payload for key in ("arrangement", "task", "agent"))
        )
        materialized = materialize_tuple_authoring_payload(raw_payload)
        # Preserve preset UX context from authoring request through materialization.
        preset_ux = raw_payload.get("preset_ux")
        if isinstance(preset_ux, dict):
            normalized_preset_ux = {}
            for key in ("smart_preset_id", "entry_mode", "compatibility_status"):
                value = preset_ux.get(key)
                if isinstance(value, str) and value.strip():
                    normalized_preset_ux[key] = value.strip()
            if normalized_preset_ux:
                materialized["preset_ux"] = dict(normalized_preset_ux)
                tuple_meta = materialized.get("tuple_authoring")
                if isinstance(tuple_meta, dict):
                    tuple_meta["preset_ux"] = dict(normalized_preset_ux)
        if uses_deprecated_shape:
            tuple_meta = materialized.get("tuple_authoring", {})
            diagnostics = tuple_meta.get("translation_diagnostics", {}) if isinstance(tuple_meta, dict) else {}
            deprecations = diagnostics.get("deprecation_diagnostics", [])
            if not isinstance(deprecations, list):
                deprecations = []
            route_contract = get_preset_route_migration_contract()
            materialized["tuple_route_migration_diagnostics"] = {
                "deprecated_input_detected": True,
                "deprecated_input_mode": diagnostics.get("source_mode", "preset_basis_v1"),
                "recommended_input_mode": diagnostics.get("target_mode", "tuple_v1"),
                "messages": [str(msg) for msg in deprecations],
                "route_migration_strategy": route_contract.get("strategy"),
                "tuple_first_preset_routes": list(route_contract.get("tuple_first_preset_routes", [])),
                "basis_first_preset_routes": list(route_contract.get("basis_first_preset_routes", [])),
            }
        return materialized
    except TupleAuthoringAPIError as exc:
        raise_validation_error(
            "Tuple authoring payload validation/materialization failed.",
            details={"reason": str(exc)},
        )
    except Exception as exc:
        raise_internal_error(
            "Tuple authoring payload materialization failed.",
            details={"reason": str(exc)},
        )


@app.post("/catalog/tuple-authoring/compatibility")
def tuple_authoring_compatibility_api(payload: dict):
    try:
        raw = dict(payload or {})
        arrangement = raw.get("arrangement")
        task = raw.get("task")
        agent = raw.get("agent")
        edits = raw.get("edits", {})
        if not isinstance(edits, dict):
            raise ValueError("edits must be an object.")
        return evaluate_behavioral_compatibility(
            arrangement_id=str(arrangement or ""),
            phenomenon_id=str(task or ""),
            agent_bundle_id=str(agent or ""),
            edits=edits,
        )
    except ValueError as exc:
        raise_validation_error(
            "Tuple compatibility payload validation failed.",
            details={"reason": str(exc)},
        )
    except Exception as exc:
        raise_internal_error(
            "Tuple compatibility evaluation failed.",
            details={"reason": str(exc)},
        )


@app.get("/catalog/preset-ux")
def preset_ux_catalog_api():
    try:
        return build_preset_ux_catalog()
    except Exception as exc:
        raise_internal_error(
            "Preset UX catalog generation failed.",
            details={"reason": str(exc)},
        )


@app.get("/catalog/preset-route-migration")
def preset_route_migration_api():
    try:
        return get_preset_route_migration_contract()
    except Exception as exc:
        raise_internal_error(
            "Preset route migration contract generation failed.",
            details={"reason": str(exc)},
        )


@app.get("/catalog/smart-presets")
def smart_preset_catalog_api():
    try:
        return build_smart_preset_catalog()
    except SmartPresetProjectionValidationError as exc:
        raise_validation_error(
            "Smart preset catalog generation failed.",
            details={"reason": str(exc)},
        )
    except Exception as exc:
        raise_internal_error(
            "Smart preset catalog generation failed.",
            details={"reason": str(exc)},
        )


@app.post("/catalog/smart-presets/{smart_preset_id}/project")
def smart_preset_project_api(smart_preset_id: str, payload: dict | None = None):
    try:
        raw = dict(payload or {})
        edits = raw.get("edits", {})
        if not isinstance(edits, dict):
            raise ValueError("edits must be an object.")
        return project_smart_preset_to_tuple_payload(smart_preset_id, edits=edits)
    except (ValueError, SmartPresetProjectionValidationError) as exc:
        raise_validation_error(
            "Smart preset projection failed.",
            details={"reason": str(exc), "smart_preset_id": smart_preset_id},
        )
    except Exception as exc:
        raise_internal_error(
            "Smart preset projection failed.",
            details={"reason": str(exc), "smart_preset_id": smart_preset_id},
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
