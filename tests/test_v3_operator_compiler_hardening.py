from __future__ import annotations

import time

from ui.contracts.operator_compiler_fixtures import (
    CANONICAL_COMPILED_PRESET_FIXTURES_VERSION,
    get_canonical_compiled_preset_fixtures,
)
from ui.contracts.operator_plan_materialization import (
    compile_and_materialize_operator_plan,
)
from ui.contracts.operator_selection_compiler import stable_selection_compile_hash


def test_compiler_fixture_inventory_covers_canonical_presets():
    fixtures = get_canonical_compiled_preset_fixtures()
    assert CANONICAL_COMPILED_PRESET_FIXTURES_VERSION == "3.12.5"
    fixture_ids = [f["fixture_id"] for f in fixtures]
    assert fixture_ids == ["acquisition", "extinction", "differential_acquisition"]
    families = [f["protocol_family"] for f in fixtures]
    assert families == ["acquisition", "extinction", "differential_acquisition"]


def test_full_legality_and_compile_sweep_over_canonical_fixtures():
    fixtures = get_canonical_compiled_preset_fixtures()
    for fixture in fixtures:
        payload = compile_and_materialize_operator_plan(
            fixture["preset_definition"],
            protocol_family=fixture["protocol_family"],
            stimuli_catalog=["tone", "noise"],
        )
        assert payload["experiment"]["program"]["phases"][0]["protocol"] == fixture["protocol_family"]
        assert payload["experiment"]["runtime"]["operator_routes"]
        assert payload["materialization"]["compiled_hash"]
        assert payload["materialization"]["materialized_hash"]


def test_deterministic_hash_regression_on_canonical_fixtures():
    fixtures = get_canonical_compiled_preset_fixtures()
    for fixture in fixtures:
        definition = fixture["preset_definition"]
        first_compile_hash = stable_selection_compile_hash(definition)
        first_materialized_hash = compile_and_materialize_operator_plan(
            definition,
            protocol_family=fixture["protocol_family"],
            stimuli_catalog=["tone", "noise"],
        )["materialization"]["materialized_hash"]
        for _ in range(20):
            assert stable_selection_compile_hash(definition) == first_compile_hash
            payload = compile_and_materialize_operator_plan(
                definition,
                protocol_family=fixture["protocol_family"],
                stimuli_catalog=["tone", "noise"],
            )
            assert payload["materialization"]["materialized_hash"] == first_materialized_hash


def test_compile_latency_guardrail_for_canonical_fixture_set():
    fixtures = get_canonical_compiled_preset_fixtures()
    start = time.perf_counter()
    rounds = 30
    for _ in range(rounds):
        for fixture in fixtures:
            compile_and_materialize_operator_plan(
                fixture["preset_definition"],
                protocol_family=fixture["protocol_family"],
                stimuli_catalog=["tone", "noise"],
            )
    elapsed = time.perf_counter() - start
    # Generous guardrail to catch severe performance regressions without CI flakiness.
    assert elapsed < 5.0

