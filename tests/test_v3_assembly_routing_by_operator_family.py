from __future__ import annotations

import copy

import pytest

from experiment.basis_routing import (
    BASIS_ASSEMBLY_ROUTING_VERSION,
    SLOT_TO_BUILDER_FAMILY,
    BasisAssemblyRoutingError,
    build_basis_assembly_routing_contract,
    stable_basis_assembly_routing_hash,
)
from experiment.domain.types import ExperimentPlan
from ui.contracts.operator_compiler_fixtures import get_canonical_compiled_preset_fixtures
from ui.contracts.operator_selection_compiler import compile_operator_selection_artifact
from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE


def _plan_from_definition(definition: dict) -> ExperimentPlan:
    return ExperimentPlan(
        units=[],
        basis_compile_artifact=compile_operator_selection_artifact(definition),
        canonical_payload={"experiment": {"program": {"phases": []}}, "report": {"preset": "acquisition"}},
    )


def test_basis_routing_conforms_to_slot_family_map():
    plan = _plan_from_definition(copy.deepcopy(PRESET_DEFINITION_TEMPLATE))
    contract = build_basis_assembly_routing_contract(plan)
    assert contract["version"] == BASIS_ASSEMBLY_ROUTING_VERSION
    for slot, expected_family in SLOT_TO_BUILDER_FAMILY.items():
        assert contract["slot_routing"][slot]["builder_family"] == expected_family
        for route in contract["slot_routing"][slot]["routes"]:
            assert route["builder_family"] == expected_family


def test_basis_routing_rejects_incorrect_builder_family_mapping():
    definition = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    compiled = compile_operator_selection_artifact(definition)
    compiled["assembly_spec"]["slots"]["delta"]["internal_builder_families"] = ["representation"]
    plan = ExperimentPlan(
        units=[],
        basis_compile_artifact=compiled,
        canonical_payload={"experiment": {"program": {"phases": []}}, "report": {"preset": "acquisition"}},
    )
    with pytest.raises(BasisAssemblyRoutingError, match="invalid builder family"):
        build_basis_assembly_routing_contract(plan)


def test_core_preset_routing_snapshots_are_stable():
    fixtures = get_canonical_compiled_preset_fixtures()
    hashes = []
    for fixture in fixtures:
        plan = _plan_from_definition(copy.deepcopy(fixture["preset_definition"]))
        contract = build_basis_assembly_routing_contract(plan)
        assert contract["slot_routing"]["phi"]["routes"] == [
            {"ui_selection_id": "elemental", "builder_family": "representation"}
        ]
        assert contract["slot_routing"]["omega"]["routes"] == [
            {"ui_selection_id": "classical_contingency", "builder_family": "environment_protocol"}
        ]
        hashes.append(stable_basis_assembly_routing_hash(plan))
    assert len(set(hashes)) == 1


def test_ui_selection_id_is_distinct_from_builder_family_in_contract():
    plan = _plan_from_definition(copy.deepcopy(PRESET_DEFINITION_TEMPLATE))
    contract = build_basis_assembly_routing_contract(plan)
    route = contract["slot_routing"]["phi"]["routes"][0]
    assert set(route.keys()) == {"ui_selection_id", "builder_family"}
    assert route["ui_selection_id"] == "elemental"
    assert route["builder_family"] == "representation"
    assert route["ui_selection_id"] != route["builder_family"]

