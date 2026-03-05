"""Protocol builder catalog for runtime assembly."""

from __future__ import annotations

from typing import Any, Callable

from virtual_shaping_lab.domain.naming import normalize_protocol_key
from virtual_shaping_lab.domain.catalog_metadata import (
    UICatalogMetadata,
    make_default_ui_metadata,
    validate_ui_metadata_map,
)

from protocols.aab_renewal import AABRenewalProtocol
from protocols.aba_renewal import ABARenewalProtocol
from protocols.abc_renewal import ABCRenewalProtocol
from protocols.blocking import BlockingProtocol
from protocols.conditioned_inhibition import ConditionedInhibitionProtocol
from protocols.extinction import ExtinctionProtocol
from protocols.matching_law import MatchingLawProtocol
from protocols.occasion_setting import OccasionSettingProtocol
from protocols.operant import OperantConditioningProtocol
from protocols.rapid_reacquisition import RapidReacquisitionProtocol
from protocols.resurgence import ResurgenceProtocol
from protocols.shaping import ShapingProtocol
from protocols.spontaneous_recovery import SpontaneousRecoveryProtocol
from protocols.superextinction import SuperextinctionProtocol


ProtocolBuilder = Callable[..., Any]


PROTOCOL_BUILDERS: dict[str, ProtocolBuilder] = {
    "operant_conditioning": OperantConditioningProtocol,
    "extinction": ExtinctionProtocol,
    "conditioned_inhibition": ConditionedInhibitionProtocol,
    "aba_renewal": ABARenewalProtocol,
    "abc_renewal": ABCRenewalProtocol,
    "aab_renewal": AABRenewalProtocol,
    "rapid_reacquisition": RapidReacquisitionProtocol,
    "occasion_setting": OccasionSettingProtocol,
    "blocking": BlockingProtocol,
    "matching_law": MatchingLawProtocol,
    "shaping": ShapingProtocol,
    "resurgence": ResurgenceProtocol,
    "superextinction": SuperextinctionProtocol,
    "spontaneous_recovery": SpontaneousRecoveryProtocol,
}

_COMMON_PROTOCOL_SCHEMA = {
    "n_trials": {"type": "int", "min": 1},
    "context": {"type": "str"},
}

_COMMON_PROTOCOL_DEFAULTS = {
    "n_trials": 20,
    "context": "A",
}

PROTOCOL_METADATA: dict[str, UICatalogMetadata] = {
    "operant_conditioning": UICatalogMetadata(
        label="Operant Conditioning",
        description="Canonical operant conditioning protocol with response-contingent reinforcement schedule phases.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA, "schedule_type": {"type": "str"}},
        defaults={**_COMMON_PROTOCOL_DEFAULTS, "schedule_type": "fixed_ratio"},
        constraints=("operant_only",),
        examples=({"params": {"n_trials": 100, "schedule_type": "variable_ratio"}},),
    ),
    "extinction": UICatalogMetadata(
        label="Extinction",
        description="Acquisition followed by nonreinforcement to measure decline in conditioned responding.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA},
        defaults={**_COMMON_PROTOCOL_DEFAULTS},
        constraints=("pavlovian_only",),
        examples=({"params": {"n_trials": 40}},),
    ),
    "conditioned_inhibition": UICatalogMetadata(
        label="Conditioned Inhibition",
        description="Trains an inhibitory cue by nonreinforced compound presentations against reinforced trials.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA},
        defaults={**_COMMON_PROTOCOL_DEFAULTS},
        constraints=("pavlovian_only", "requires_compound_trials"),
        examples=({"params": {"n_trials": 40}},),
    ),
    "aba_renewal": UICatalogMetadata(
        label="Renewal (ABA)",
        description="Acquisition in context A, nonreinforcement in B, probe in A.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA, "test_context": {"type": "str"}},
        defaults={**_COMMON_PROTOCOL_DEFAULTS, "test_context": "A"},
        constraints=("pavlovian_only", "context_shift_protocol"),
        examples=({"params": {"context": "A", "test_context": "A"}},),
    ),
    "abc_renewal": UICatalogMetadata(
        label="Renewal (ABC)",
        description="Acquisition in context A, nonreinforcement in B, probe in novel context C.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA, "test_context": {"type": "str"}},
        defaults={**_COMMON_PROTOCOL_DEFAULTS, "test_context": "C"},
        constraints=("pavlovian_only", "context_shift_protocol"),
        examples=({"params": {"context": "A", "test_context": "C"}},),
    ),
    "aab_renewal": UICatalogMetadata(
        label="Renewal (AAB)",
        description="Acquisition and nonreinforcement in context A, probe in context B.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA, "test_context": {"type": "str"}},
        defaults={**_COMMON_PROTOCOL_DEFAULTS, "test_context": "B"},
        constraints=("pavlovian_only", "context_shift_protocol"),
        examples=({"params": {"context": "A", "test_context": "B"}},),
    ),
    "rapid_reacquisition": UICatalogMetadata(
        label="Rapid Reacquisition",
        description="Reinforcement returns after extinction to assess faster relearning.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA},
        defaults={**_COMMON_PROTOCOL_DEFAULTS},
        constraints=("pavlovian_only",),
        examples=({"params": {"n_trials": 60}},),
    ),
    "occasion_setting": UICatalogMetadata(
        label="Occasion Setting",
        description="Uses an occasion setter cue to modulate reinforcement of target cues.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA},
        defaults={**_COMMON_PROTOCOL_DEFAULTS},
        constraints=("pavlovian_only", "requires_compound_trials"),
        examples=({"params": {"n_trials": 50}},),
    ),
    "blocking": UICatalogMetadata(
        label="Blocking",
        description="Pretraining on one cue reduces acquisition to added cue in compound phase.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA},
        defaults={**_COMMON_PROTOCOL_DEFAULTS},
        constraints=("pavlovian_only", "requires_compound_trials"),
        examples=({"params": {"n_trials": 40}},),
    ),
    "matching_law": UICatalogMetadata(
        label="Matching Law",
        description="Concurrent operant schedules to evaluate response allocation against reinforcement ratios.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA, "schedule_left": {"type": "dict"}, "schedule_right": {"type": "dict"}},
        defaults={**_COMMON_PROTOCOL_DEFAULTS, "schedule_left": {}, "schedule_right": {}},
        constraints=("operant_only", "concurrent_schedule"),
        examples=(
            {
                "params": {
                    "schedule_left": {"type": "variable_interval", "value": 10},
                    "schedule_right": {"type": "variable_interval", "value": 30},
                }
            },
        ),
    ),
    "shaping": UICatalogMetadata(
        label="Shaping",
        description="Progressive schedule progression to train target operant behavior.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA},
        defaults={**_COMMON_PROTOCOL_DEFAULTS},
        constraints=("operant_only",),
        examples=({"params": {"n_trials": 100}},),
    ),
    "resurgence": UICatalogMetadata(
        label="Resurgence",
        description="Previously extinguished response returns when alternative reinforcement is removed.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA},
        defaults={**_COMMON_PROTOCOL_DEFAULTS},
        constraints=("operant_only",),
        examples=({"params": {"n_trials": 80}},),
    ),
    "superextinction": UICatalogMetadata(
        label="Superextinction",
        description="Extended nonreinforcement schedule to suppress responding beyond standard extinction.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA},
        defaults={**_COMMON_PROTOCOL_DEFAULTS},
        constraints=("pavlovian_only",),
        examples=({"params": {"n_trials": 60}},),
    ),
    "spontaneous_recovery": UICatalogMetadata(
        label="Spontaneous Recovery",
        description="Recovery of conditioned responding after delay following extinction.",
        params_schema={**_COMMON_PROTOCOL_SCHEMA},
        defaults={**_COMMON_PROTOCOL_DEFAULTS},
        constraints=("pavlovian_only",),
        examples=({"params": {"n_trials": 40}},),
    ),
}

for protocol_key in PROTOCOL_BUILDERS.keys():
    if protocol_key not in PROTOCOL_METADATA:
        PROTOCOL_METADATA[protocol_key] = make_default_ui_metadata(
            protocol_key,
            description_prefix="Protocol",
        )

validate_ui_metadata_map(
    keys=set(PROTOCOL_BUILDERS.keys()),
    metadata_map=PROTOCOL_METADATA,
    namespace="protocols.catalog",
)


def available_protocols() -> list[str]:
    return sorted(PROTOCOL_BUILDERS.keys())


def get_protocol_metadata(name: str) -> UICatalogMetadata:
    normalized = normalize_protocol_key(name)
    validate_protocol_name(normalized)
    return PROTOCOL_METADATA[normalized]


def validate_protocol_name(name: str) -> None:
    normalized = normalize_protocol_key(name)
    if normalized not in PROTOCOL_BUILDERS:
        available = ", ".join(available_protocols())
        raise KeyError(f"Unknown protocol '{name}' (normalized='{normalized}'). Available protocols: {available}")


def build_protocol(
    name: str,
    *,
    agent: Any,
    stimuli: Any = None,
    params: dict[str, Any] | None = None,
) -> Any:
    normalized = normalize_protocol_key(name)
    validate_protocol_name(normalized)
    protocol_cls = PROTOCOL_BUILDERS[normalized]
    return protocol_cls(agent=agent, stimuli=stimuli, params=params or {})
