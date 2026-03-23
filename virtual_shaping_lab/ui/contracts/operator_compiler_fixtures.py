"""Canonical fixture inventory for operator-basis compiler hardening."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE


CANONICAL_COMPILED_PRESET_FIXTURES_VERSION = "3.12.5"


def get_canonical_compiled_preset_fixtures() -> tuple[dict[str, Any], ...]:
    """Return canonical fixture inventory for legality+compile sweeps."""
    acquisition = deepcopy(PRESET_DEFINITION_TEMPLATE)
    acquisition["id"] = "rw_acquisition"
    acquisition["label"] = "RW Acquisition"
    acquisition["description"] = "Canonical acquisition subset fixture."

    extinction = deepcopy(PRESET_DEFINITION_TEMPLATE)
    extinction["id"] = "rw_extinction"
    extinction["label"] = "RW Extinction"
    extinction["description"] = "Canonical extinction subset fixture."

    differential = deepcopy(PRESET_DEFINITION_TEMPLATE)
    differential["id"] = "rw_differential_acquisition"
    differential["label"] = "RW Differential Acquisition"
    differential["description"] = "Canonical differential acquisition subset fixture."

    return (
        {
            "fixture_id": "acquisition",
            "protocol_family": "acquisition",
            "preset_definition": acquisition,
        },
        {
            "fixture_id": "extinction",
            "protocol_family": "extinction",
            "preset_definition": extinction,
        },
        {
            "fixture_id": "differential_acquisition",
            "protocol_family": "differential_acquisition",
            "preset_definition": differential,
        },
    )

