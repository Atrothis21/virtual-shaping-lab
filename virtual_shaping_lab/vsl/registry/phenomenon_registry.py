"""Typed phenomenon-registry contracts for V3 scientific coverage."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

SUPPORTED_CAVEAT_TIERS: tuple[str, ...] = (
    "none",
    "minor",
    "moderate",
    "major",
)


def _to_primitive(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _to_primitive(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, list):
        return [_to_primitive(v) for v in value]
    if isinstance(value, tuple):
        return [_to_primitive(v) for v in value]
    if hasattr(value, "to_dict"):
        return _to_primitive(value.to_dict())
    return value


@dataclass(frozen=True)
class OperatorBundleSpec:
    """Minimal operator bundle declaration for a phenomenon entry."""

    key: str
    operators: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("OperatorBundleSpec.key must be a non-empty string.")
        if not isinstance(self.operators, tuple) or not self.operators:
            raise ValueError("OperatorBundleSpec.operators must be a non-empty tuple[str, ...].")
        if not all(isinstance(value, str) and value.strip() for value in self.operators):
            raise ValueError("OperatorBundleSpec.operators must contain non-empty strings.")
        if not isinstance(self.metadata, dict):
            raise ValueError("OperatorBundleSpec.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "operators": list(self.operators),
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OperatorBundleSpec":
        return cls(
            key=str(data.get("key", "")).strip(),
            operators=tuple(str(v).strip() for v in (data.get("operators", ()) or ())),
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class ConstraintSpec:
    """Constraint contract used to enforce operator requirements."""

    required_operators: tuple[str, ...] = ()
    forbidden_operators: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.required_operators, tuple):
            raise ValueError("ConstraintSpec.required_operators must be tuple[str, ...].")
        if not isinstance(self.forbidden_operators, tuple):
            raise ValueError("ConstraintSpec.forbidden_operators must be tuple[str, ...].")
        if not all(isinstance(value, str) and value.strip() for value in self.required_operators):
            raise ValueError("ConstraintSpec.required_operators must contain non-empty strings.")
        if not all(isinstance(value, str) and value.strip() for value in self.forbidden_operators):
            raise ValueError("ConstraintSpec.forbidden_operators must contain non-empty strings.")
        overlap = set(self.required_operators).intersection(self.forbidden_operators)
        if overlap:
            names = ", ".join(sorted(overlap))
            raise ValueError(f"ConstraintSpec overlap is not allowed; found in required/forbidden: {names}.")
        if not isinstance(self.metadata, dict):
            raise ValueError("ConstraintSpec.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "required_operators": list(self.required_operators),
            "forbidden_operators": list(self.forbidden_operators),
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConstraintSpec":
        return cls(
            required_operators=tuple(str(v).strip() for v in (data.get("required_operators", ()) or ())),
            forbidden_operators=tuple(str(v).strip() for v in (data.get("forbidden_operators", ()) or ())),
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class ReadoutSpec:
    """Named readout contract for a phenomenon entry."""

    key: str
    metric: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("ReadoutSpec.key must be a non-empty string.")
        if not isinstance(self.metric, str) or not self.metric.strip():
            raise ValueError("ReadoutSpec.metric must be a non-empty string.")
        if not isinstance(self.metadata, dict):
            raise ValueError("ReadoutSpec.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "metric": self.metric,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReadoutSpec":
        return cls(
            key=str(data.get("key", "")).strip(),
            metric=str(data.get("metric", "")).strip(),
            metadata=dict(data.get("metadata", {}) or {}),
        )


@dataclass(frozen=True)
class PhenomenonRegistryEntry:
    """Schema contract for a single phenomenon registry entry."""

    key: str
    recipe: dict[str, Any]
    bundles: tuple[OperatorBundleSpec, ...]
    constraints: ConstraintSpec
    readouts: tuple[ReadoutSpec, ...]
    fixture: str
    caveat_tier: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("PhenomenonRegistryEntry.key must be a non-empty string.")
        if not isinstance(self.recipe, dict):
            raise ValueError("PhenomenonRegistryEntry.recipe must be an object.")
        if not isinstance(self.bundles, tuple) or not self.bundles:
            raise ValueError("PhenomenonRegistryEntry.bundles must be a non-empty tuple[OperatorBundleSpec, ...].")
        if not all(isinstance(value, OperatorBundleSpec) for value in self.bundles):
            raise ValueError("PhenomenonRegistryEntry.bundles must contain OperatorBundleSpec values.")
        if not isinstance(self.constraints, ConstraintSpec):
            raise ValueError("PhenomenonRegistryEntry.constraints must be a ConstraintSpec.")
        if not isinstance(self.readouts, tuple) or not self.readouts:
            raise ValueError("PhenomenonRegistryEntry.readouts must be a non-empty tuple[ReadoutSpec, ...].")
        if not all(isinstance(value, ReadoutSpec) for value in self.readouts):
            raise ValueError("PhenomenonRegistryEntry.readouts must contain ReadoutSpec values.")
        if not isinstance(self.fixture, str) or not self.fixture.strip():
            raise ValueError("PhenomenonRegistryEntry.fixture must be a non-empty string.")
        if not isinstance(self.caveat_tier, str) or not self.caveat_tier.strip():
            raise ValueError("PhenomenonRegistryEntry.caveat_tier must be a non-empty string.")
        if self.caveat_tier not in SUPPORTED_CAVEAT_TIERS:
            allowed = ", ".join(SUPPORTED_CAVEAT_TIERS)
            raise ValueError(
                f"PhenomenonRegistryEntry.caveat_tier must be one of: {allowed}."
            )
        if not isinstance(self.metadata, dict):
            raise ValueError("PhenomenonRegistryEntry.metadata must be an object.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "recipe": _to_primitive(self.recipe),
            "bundles": [_to_primitive(bundle) for bundle in self.bundles],
            "constraints": _to_primitive(self.constraints),
            "readouts": [_to_primitive(readout) for readout in self.readouts],
            "fixture": self.fixture,
            "caveat_tier": self.caveat_tier,
            "metadata": _to_primitive(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PhenomenonRegistryEntry":
        raw_bundles = list(data.get("bundles", ()) or ())
        raw_readouts = list(data.get("readouts", ()) or ())
        raw_constraints = data.get("constraints", {}) or {}
        return cls(
            key=str(data.get("key", "")).strip(),
            recipe=dict(data.get("recipe", {}) or {}),
            bundles=tuple(
                OperatorBundleSpec.from_dict(item) if isinstance(item, dict) else item for item in raw_bundles
            ),
            constraints=ConstraintSpec.from_dict(raw_constraints) if isinstance(raw_constraints, dict) else raw_constraints,
            readouts=tuple(ReadoutSpec.from_dict(item) if isinstance(item, dict) else item for item in raw_readouts),
            fixture=str(data.get("fixture", "")).strip(),
            caveat_tier=str(data.get("caveat_tier", "")).strip(),
            metadata=dict(data.get("metadata", {}) or {}),
        )


PHENOMENON_REGISTRY: dict[str, PhenomenonRegistryEntry] = {}


def _entry(
    *,
    key: str,
    protocol: str,
    readouts: tuple[str, ...],
    fixture: str,
    caveat_tier: str,
    bundle_key: str,
    operators: tuple[str, ...],
    required_operators: tuple[str, ...],
    metadata: dict[str, Any] | None = None,
) -> PhenomenonRegistryEntry:
    return PhenomenonRegistryEntry(
        key=key,
        recipe={"protocol": protocol, "variant": "canonical"},
        bundles=(
            OperatorBundleSpec(
                key=bundle_key,
                operators=operators,
                metadata={"claim": "minimal_bundle"},
            ),
        ),
        constraints=ConstraintSpec(
            required_operators=required_operators,
            forbidden_operators=(),
            metadata={"enforcement": "build_and_run"},
        ),
        readouts=tuple(
            ReadoutSpec(
                key=readout,
                metric=f"signature.{readout}",
                metadata={"source": "behavioral_signature"},
            )
            for readout in readouts
        ),
        fixture=fixture,
        caveat_tier=caveat_tier,
        metadata=metadata or {},
    )


_PAVL_OVERVIEW = ("Phi", "P", "E", "W", "Omega", "M")
_CTX_OVERVIEW = ("Phi", "C", "P", "E", "W", "Omega", "M")
_OPERANT_OVERVIEW = ("Phi", "P", "E", "W", "Pi", "Omega", "M")

_PAVL_REQUIRED = ("Env", "Err", "Measure")
_CTX_REQUIRED = ("C", "Env", "Err", "Measure")
_OPERANT_REQUIRED = ("Policy", "Env", "Err", "Measure")


PHENOMENON_REGISTRY = {
    "blocking": _entry(
        key="blocking",
        protocol="blocking",
        readouts=("blocked_cue_lower_than_pretrained_cue",),
        fixture="tests/preset_payloads.py::blocking_payload",
        caveat_tier="minor",
        bundle_key="pavlovian_error_driven",
        operators=_PAVL_OVERVIEW,
        required_operators=_PAVL_REQUIRED,
        metadata={"family": "cue_competition"},
    ),
    "conditioned_inhibition": _entry(
        key="conditioned_inhibition",
        protocol="conditioned_inhibition",
        readouts=("compound_nonreinforcement_suppression", "summation_probe_below_excitatory_baseline"),
        fixture="tests/preset_payloads.py::conditioned_inhibition_payload",
        caveat_tier="minor",
        bundle_key="pavlovian_error_driven",
        operators=_PAVL_OVERVIEW,
        required_operators=_PAVL_REQUIRED,
        metadata={"family": "cue_competition"},
    ),
    "renewal_aba": _entry(
        key="renewal_aba",
        protocol="aba_renewal",
        readouts=("probe_above_extinction_tail",),
        fixture="tests/preset_payloads.py::aba_renewal_payload",
        caveat_tier="minor",
        bundle_key="contextual_pavlovian",
        operators=_CTX_OVERVIEW,
        required_operators=_CTX_REQUIRED,
        metadata={"family": "context"},
    ),
    "renewal_abc": _entry(
        key="renewal_abc",
        protocol="abc_renewal",
        readouts=("probe_above_extinction_tail",),
        fixture="tests/preset_payloads.py::abc_renewal_payload",
        caveat_tier="minor",
        bundle_key="contextual_pavlovian",
        operators=_CTX_OVERVIEW,
        required_operators=_CTX_REQUIRED,
        metadata={"family": "context"},
    ),
    "renewal_aab": _entry(
        key="renewal_aab",
        protocol="aab_renewal",
        readouts=("probe_near_extinction_tail",),
        fixture="tests/preset_payloads.py::aab_renewal_payload",
        caveat_tier="minor",
        bundle_key="contextual_pavlovian",
        operators=_CTX_OVERVIEW,
        required_operators=_CTX_REQUIRED,
        metadata={"family": "context"},
    ),
    "extinction": _entry(
        key="extinction",
        protocol="extinction",
        readouts=("late_extinction_prediction_below_early_extinction",),
        fixture="tests/preset_payloads.py::extinction_payload",
        caveat_tier="none",
        bundle_key="pavlovian_error_driven",
        operators=_PAVL_OVERVIEW,
        required_operators=_PAVL_REQUIRED,
        metadata={"family": "acquisition_extinction"},
    ),
    "rapid_reacquisition": _entry(
        key="rapid_reacquisition",
        protocol="rapid_reacquisition",
        readouts=("reacquisition_above_extinction_tail",),
        fixture="tests/preset_payloads.py::rapid_reacquisition_payload",
        caveat_tier="moderate",
        bundle_key="contextual_pavlovian",
        operators=_CTX_OVERVIEW,
        required_operators=_CTX_REQUIRED,
        metadata={"family": "acquisition_extinction", "note": "persistence-sensitive"},
    ),
    "occasion_setting": _entry(
        key="occasion_setting",
        protocol="occasion_setting",
        readouts=("probe_between_acquisition_and_nonreinforcement",),
        fixture="tests/preset_payloads.py::occasion_setting_payload",
        caveat_tier="minor",
        bundle_key="contextual_pavlovian",
        operators=_CTX_OVERVIEW,
        required_operators=_CTX_REQUIRED,
        metadata={"family": "context"},
    ),
    "operant_conditioning": _entry(
        key="operant_conditioning",
        protocol="operant_conditioning",
        readouts=("reward_and_prediction_increase",),
        fixture="tests/preset_payloads.py::operant_conditioning_payload",
        caveat_tier="none",
        bundle_key="operant_core",
        operators=_OPERANT_OVERVIEW,
        required_operators=_OPERANT_REQUIRED,
        metadata={"family": "operant"},
    ),
    "matching_law": _entry(
        key="matching_law",
        protocol="matching_law",
        readouts=("choice_bias_under_unequal_schedules",),
        fixture="tests/preset_payloads.py::matching_law_payload",
        caveat_tier="minor",
        bundle_key="operant_core",
        operators=_OPERANT_OVERVIEW,
        required_operators=_OPERANT_REQUIRED,
        metadata={"family": "operant"},
    ),
    "shaping": _entry(
        key="shaping",
        protocol="shaping",
        readouts=("stage_reward_density_shift",),
        fixture="tests/preset_payloads.py::shaping_payload",
        caveat_tier="minor",
        bundle_key="operant_core",
        operators=_OPERANT_OVERVIEW,
        required_operators=_OPERANT_REQUIRED,
        metadata={"family": "operant"},
    ),
    "resurgence": _entry(
        key="resurgence",
        protocol="resurgence",
        readouts=("recovery_above_suppression",),
        fixture="tests/preset_payloads.py::resurgence_payload",
        caveat_tier="moderate",
        bundle_key="operant_core",
        operators=_OPERANT_OVERVIEW,
        required_operators=_OPERANT_REQUIRED,
        metadata={"family": "operant", "note": "context/persistence-sensitive"},
    ),
    "superextinction": _entry(
        key="superextinction",
        protocol="superextinction",
        readouts=("punishment_phase_negative_rewards",),
        fixture="tests/preset_payloads.py::superextinction_payload",
        caveat_tier="minor",
        bundle_key="operant_core",
        operators=_OPERANT_OVERVIEW,
        required_operators=_OPERANT_REQUIRED,
        metadata={"family": "operant"},
    ),
    "spontaneous_recovery": _entry(
        key="spontaneous_recovery",
        protocol="spontaneous_recovery",
        readouts=("probe_above_extinction_tail",),
        fixture="tests/preset_payloads.py::spontaneous_recovery_payload",
        caveat_tier="major",
        bundle_key="contextual_pavlovian",
        operators=_CTX_OVERVIEW,
        required_operators=_CTX_REQUIRED,
        metadata={"family": "acquisition_extinction", "note": "requires persistence assumptions"},
    ),
}


def match_phenomenon_registry_entry_for_protocol(
    protocol: str,
    registry: dict[str, PhenomenonRegistryEntry] | None = None,
) -> PhenomenonRegistryEntry | None:
    target = str(protocol or "").strip().lower()
    if not target:
        return None
    active = registry if registry is not None else PHENOMENON_REGISTRY
    for entry in active.values():
        recipe = entry.recipe if isinstance(entry.recipe, dict) else {}
        candidate = str(recipe.get("protocol", "")).strip().lower()
        if candidate == target:
            return entry
    return None


def registry_fixture_matrix(
    registry: dict[str, PhenomenonRegistryEntry] | None = None,
) -> dict[str, str]:
    active = registry if registry is not None else PHENOMENON_REGISTRY
    return {key: active[key].fixture for key in sorted(active.keys())}


def validate_registry_fixture_links(
    registry: dict[str, PhenomenonRegistryEntry] | None = None,
) -> None:
    active = registry if registry is not None else PHENOMENON_REGISTRY
    for key, entry in active.items():
        fixture = str(entry.fixture or "").strip()
        if "::" not in fixture:
            raise ValueError(
                f"Phenomenon '{key}' fixture must use '<module_path>::<callable>' format."
            )
        module_path, callable_name = fixture.split("::", 1)
        if not module_path.strip() or not callable_name.strip():
            raise ValueError(
                f"Phenomenon '{key}' fixture must include both module path and callable name."
            )


def validate_phenomenon_registry(
    registry: dict[str, PhenomenonRegistryEntry] | None = None,
) -> None:
    active = registry if registry is not None else PHENOMENON_REGISTRY
    for key, value in active.items():
        if not isinstance(value, PhenomenonRegistryEntry):
            raise ValueError(f"Phenomenon registry value for '{key}' must be PhenomenonRegistryEntry.")
        if key != value.key:
            raise ValueError(f"Phenomenon registry key mismatch: '{key}' != '{value.key}'.")


def phenomenon_registry_payload(
    registry: dict[str, PhenomenonRegistryEntry] | None = None,
) -> dict[str, Any]:
    active = registry if registry is not None else PHENOMENON_REGISTRY
    validate_phenomenon_registry(active)
    return {
        "entries": {key: active[key].to_dict() for key in sorted(active.keys())},
        "supported_caveat_tiers": list(SUPPORTED_CAVEAT_TIERS),
        "version": "3.8.0",
    }


def phenomenon_registry_hash(
    registry: dict[str, PhenomenonRegistryEntry] | None = None,
) -> str:
    payload = phenomenon_registry_payload(registry)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


validate_phenomenon_registry()
validate_registry_fixture_links()
