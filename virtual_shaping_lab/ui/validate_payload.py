# ui/validate_payload.py

import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError


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
OPERANT_PROTOCOLS = {
    "operant_conditioning",
    "matching_law",
    "shaping",
    "resurgence",
    "superextinction",
    "spontaneous_recovery",
}
OPERANT_PROTOCOL_ACTION_COUNTS = {
    "operant_conditioning": 1,
    "shaping": 1,
    "superextinction": 1,
    "spontaneous_recovery": 1,
    "matching_law": 2,
    "resurgence": 2,
}


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

    for key in ("learner", "agent", "representation"):
        if key not in exp:
            raise ValidationError(f"experiment.{key} is required")

    return exp


# Shallow policy shape guard only.
def _validate_policy_guard(exp: dict) -> None:
    policy = exp.get("policy")
    if not policy:
        return

    if not isinstance(policy, (dict, str)):
        raise ValidationError("policy must be an object or string")
    if isinstance(policy, dict):
        _validate_schema(policy, POLICY_SCHEMA_PATH, "policy")


def _uses_operant_path(exp: dict) -> bool:
    if "protocol" in exp and exp.get("protocol"):
        return exp.get("protocol") in OPERANT_PROTOCOLS
    return any(
        p.get("protocol") in OPERANT_PROTOCOLS
        for p in exp.get("phases", [])
        if isinstance(p, dict)
    )


def _iter_operant_entries(exp: dict):
    if "protocol" in exp and exp.get("protocol") in OPERANT_PROTOCOLS:
        yield exp.get("protocol"), exp.get("params") if isinstance(exp.get("params"), dict) else {}

    for phase in exp.get("phases", []):
        if not isinstance(phase, dict):
            continue
        proto = phase.get("protocol")
        if proto in OPERANT_PROTOCOLS:
            params = phase.get("params") if isinstance(phase.get("params"), dict) else {}
            yield proto, params


def _validate_operant_payload_semantics(exp: dict) -> None:
    # Semantic validation is engine-owned (ExperimentConfig/parameter pipeline).
    return None


def _validate_representation_mechanism_split(exp: dict) -> None:
    # Semantic ownership validation is engine-owned.
    return None


# Shallow mode validation: enforce protocol-mode XOR phase-mode and basic shape checks.
def _validate_protocol_or_phases(exp: dict) -> None:
    has_protocol = "protocol" in exp and exp.get("protocol")
    has_phases = "phases" in exp and isinstance(exp.get("phases"), list) and len(exp["phases"]) > 0

    if has_protocol and has_phases:
        raise ValidationError("experiment must provide either 'protocol' or 'phases', not both")
    if not has_protocol and not has_phases:
        raise ValidationError("experiment must provide either 'protocol' or 'phases'")

    if has_protocol:
        if not isinstance(exp.get("protocol"), str):
            raise ValidationError("experiment.protocol must be a string")
        if "params" in exp and not isinstance(exp.get("params"), dict):
            raise ValidationError("experiment.params must be an object")
        if "stimuli" in exp and not isinstance(exp.get("stimuli"), dict):
            raise ValidationError("experiment.stimuli must be an object")
        return

    phases = exp.get("phases", [])
    for idx, phase in enumerate(phases):
        if not isinstance(phase, dict):
            raise ValidationError(f"phase[{idx}] must be an object")

        phase_name = phase.get("protocol")
        if not isinstance(phase_name, str) or not phase_name:
            raise ValidationError(f"phase[{idx}].protocol is required")
        if "params" in phase and not isinstance(phase.get("params"), dict):
            raise ValidationError(f"phase[{idx}].params must be an object")
        if "stimuli" in phase and not isinstance(phase.get("stimuli"), dict):
            raise ValidationError(f"phase[{idx}].stimuli must be an object")


def validate_phase_order(phases):
    """
    Deprecated UI hook; phase ordering semantics are engine-owned.
    """
    return None


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
