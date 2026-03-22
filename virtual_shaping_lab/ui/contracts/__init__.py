"""UI-facing typed contracts."""

from ui.contracts.builder_draft import (
    BuilderDraftValidationError,
    BuilderExperimentDraft,
    BuilderPhaseDraft,
    BuilderRuntimeDraft,
)
from ui.contracts.operator_registry import (
    OPERATOR_REGISTRY,
    OPERATOR_REGISTRY_VERSION,
    REQUIRED_OPERATOR_FAMILIES,
    REQUIRED_OPERATORS,
    OperatorRegistryValidationError,
    get_operator,
    get_operator_registry,
    list_operator_ids,
    validate_operator_registry,
)
from ui.contracts.trialstate_registry import (
    REQUIRED_TRIALSTATE_FIELDS,
    REQUIRED_TRIALSTATE_FIELD_GROUPS,
    TRIALSTATE_FIELD_REGISTRY,
    TRIALSTATE_FIELD_REGISTRY_VERSION,
    TrialStateRegistryValidationError,
    get_trialstate_field,
    get_trialstate_field_registry,
    list_trialstate_field_ids,
    validate_trialstate_field_registry,
)
from ui.contracts.translator import draft_to_payload

__all__ = [
    "BuilderDraftValidationError",
    "BuilderExperimentDraft",
    "BuilderPhaseDraft",
    "BuilderRuntimeDraft",
    "draft_to_payload",
    "OperatorRegistryValidationError",
    "OPERATOR_REGISTRY_VERSION",
    "OPERATOR_REGISTRY",
    "REQUIRED_OPERATOR_FAMILIES",
    "REQUIRED_OPERATORS",
    "validate_operator_registry",
    "get_operator_registry",
    "list_operator_ids",
    "get_operator",
    "TrialStateRegistryValidationError",
    "TRIALSTATE_FIELD_REGISTRY_VERSION",
    "TRIALSTATE_FIELD_REGISTRY",
    "REQUIRED_TRIALSTATE_FIELD_GROUPS",
    "REQUIRED_TRIALSTATE_FIELDS",
    "validate_trialstate_field_registry",
    "get_trialstate_field_registry",
    "list_trialstate_field_ids",
    "get_trialstate_field",
]
