# ui/validate_payload.py

import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError
from experiment.phases.catalog import PHASE_CONSTRAINTS
from experiment.migrations import SUPPORTED_SCHEMA_VERSIONS


SCHEMA_DIR = Path(__file__).parent / "schema"
PHASE_SCHEMA_DIR = SCHEMA_DIR / "phases"
PROTOCOL_SCHEMA_DIR = SCHEMA_DIR / "protocols"
POLICY_SCHEMA_PATH = SCHEMA_DIR / "policy.schema.json"
EXPERIMENT_SCHEMA_PATH = SCHEMA_DIR / "experiment.schema.json"
REPORT_SCHEMA_PATH = SCHEMA_DIR / "report.schema.json"


def _load_schema(path: Path) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def _schema_key(path: Path) -> str:
    name = path.name
    if name.endswith(".schema.json"):
        return name[: -len(".schema.json")]
    return path.stem


def _build_schema_map(schema_dir: Path) -> dict:
    if not schema_dir.exists():
        return {}
    return {_schema_key(p): p for p in schema_dir.glob("*.schema.json")}


PHASE_SCHEMA_MAP = _build_schema_map(PHASE_SCHEMA_DIR)
PROTOCOL_SCHEMA_MAP = _build_schema_map(PROTOCOL_SCHEMA_DIR)


def _validate_schema(obj: dict, schema_path: Path, label: str) -> None:
    schema = _load_schema(schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(obj), key=lambda e: e.path)
    if errors:
        err = errors[0]
        path = ".".join([str(p) for p in err.path]) or f"<{label}>"
        raise ValidationError(f"{label} {path}: {err.message}")


# Structural validation only: verify required top-level keys and experiment shape.
def _validate_top_level(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValidationError("payload must be an object")

    if "experiment" not in payload:
        raise ValidationError("<root>: missing required key 'experiment'")
    if "report" not in payload:
        raise ValidationError("<root>: missing required key 'report'")

    report = payload.get("report", {})
    if not isinstance(report, dict):
        raise ValidationError("report must be an object")

    if REPORT_SCHEMA_PATH.exists():
        _validate_schema(report, REPORT_SCHEMA_PATH, "report")

    exp = payload.get("experiment", {})
    if not isinstance(exp, dict):
        raise ValidationError("experiment must be an object")

    if EXPERIMENT_SCHEMA_PATH.exists():
        _validate_schema(exp, EXPERIMENT_SCHEMA_PATH, "experiment")

    schema_version = exp.get("schema_version")
    if schema_version is not None and schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValidationError(
            "experiment.schema_version must be one of: "
            + ", ".join(sorted(SUPPORTED_SCHEMA_VERSIONS))
        )

    for key in ("learner", "agent", "representation"):
        if key not in exp:
            raise ValidationError(f"experiment.{key} is required")

    return exp


# Semantic guard: policies are only valid for operant protocols.
def _validate_policy_guard(exp: dict) -> None:
    policy = exp.get("policy")
    if not policy:
        return

    if "protocol" in exp and exp.get("protocol"):
        is_operant = exp.get("protocol") in {"operant_conditioning", "matching_law"}
    else:
        is_operant = any(
            p.get("protocol") in {"operant_conditioning", "matching_law"}
            for p in exp.get("phases", [])
        )

    if not is_operant:
        raise ValidationError("policy is only allowed for operant_conditioning protocols")

    _validate_schema(policy, POLICY_SCHEMA_PATH, "policy")


# Schema validation: enforce protocol-mode XOR phase-mode and validate schemas.
def _validate_protocol_or_phases(exp: dict) -> None:
    has_protocol = "protocol" in exp and exp.get("protocol")
    has_phases = "phases" in exp and isinstance(exp.get("phases"), list) and len(exp["phases"]) > 0

    if has_protocol and has_phases:
        raise ValidationError("experiment must provide either 'protocol' or 'phases', not both")
    if not has_protocol and not has_phases:
        raise ValidationError("experiment must provide either 'protocol' or 'phases'")

    if has_protocol:
        protocol = exp.get("protocol")
        schema_path = PROTOCOL_SCHEMA_MAP.get(protocol)
        if not schema_path:
            raise ValidationError(
                f"experiment.protocol uses unknown protocol '{protocol}' "
                f"(no protocol schema registered)"
            )

        protocol_payload = {
            "name": exp.get("name", protocol),
            "protocol": protocol,
            "stimuli": exp.get("stimuli", {}),
            "params": exp.get("params", {}),
        }

        _validate_schema(protocol_payload, schema_path, f"protocol[{protocol}]")
        return

    phases = exp.get("phases", [])
    for idx, phase in enumerate(phases):
        if not isinstance(phase, dict):
            raise ValidationError(f"phase[{idx}] must be an object")

        phase_name = phase.get("protocol")
        if not phase_name:
            raise ValidationError(f"phase[{idx}].protocol is required")

        schema_path = PHASE_SCHEMA_MAP.get(phase_name)
        if not schema_path:
            raise ValidationError(
                f"phase[{idx}] uses unknown phase '{phase_name}' "
                f"(no phase schema registered)"
            )

        _validate_schema(phase, schema_path, f"phase[{idx}] ({phase_name})")

    validate_phase_order(phases)


def validate_phase_order(phases):
    """
    Validate phase ordering using PHASE_CONSTRAINTS.
    """
    seen_learning = False
    seen_acquisition = False

    for idx, phase in enumerate(phases):
        protocol = phase.get("protocol")

        if protocol in {"acquisition", "compound_acquisition", "differential_acquisition"}:
            seen_learning = True
            seen_acquisition = True

        if protocol in PHASE_CONSTRAINTS["requires_prior_learning"] and not seen_learning:
            raise ValueError(
                f"Phase '{protocol}' at position {idx} requires a prior learning phase."
            )

        if protocol in PHASE_CONSTRAINTS["requires_prior_acquisition"] and not seen_acquisition:
            raise ValueError(
                f"Phase '{protocol}' at position {idx} requires a prior acquisition phase."
            )


# Public entry point: thin wrapper that composes all validation steps.
def validate_payload(payload: dict) -> None:
    """
    Validate a UI payload using either:
    - protocol schema (single protocol mode)
    - per-phase schemas (builder mode)
    """
    exp = _validate_top_level(payload)
    _validate_policy_guard(exp)
    _validate_protocol_or_phases(exp)
