from __future__ import annotations

import importlib.util
from pathlib import Path

from experiment.config import ExperimentConfig
from experiment.domain.types import ExperimentPlan
from ui.validate_payload import validate_payload
from virtual_shaping_lab.vsl.registry import (
    PHENOMENON_REGISTRY,
    registry_fixture_matrix,
    validate_registry_fixture_links,
)


def _resolve_fixture_callable(fixture_ref: str):
    module_path, callable_name = fixture_ref.split("::", 1)
    absolute = Path(module_path).resolve()
    spec = importlib.util.spec_from_file_location("v3_registry_fixture_module", str(absolute))
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load fixture module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, callable_name):
        raise AssertionError(f"Fixture callable '{callable_name}' missing from module '{module_path}'.")
    value = getattr(module, callable_name)
    if not callable(value):
        raise AssertionError(f"Fixture target '{fixture_ref}' must be callable.")
    return value


def test_v3_slice4_fixture_matrix_covers_all_registry_entries():
    matrix = registry_fixture_matrix()
    assert set(matrix.keys()) == set(PHENOMENON_REGISTRY.keys())
    validate_registry_fixture_links()


def test_v3_slice4_registry_fixtures_are_buildable():
    for key, entry in PHENOMENON_REGISTRY.items():
        fixture_builder = _resolve_fixture_callable(entry.fixture)
        payload = fixture_builder()
        validate_payload(payload)
        plan = ExperimentConfig.plan_from_payload(payload)
        assert isinstance(plan, ExperimentPlan)
        phase_protocol = (
            plan.canonical_payload.get("experiment", {})
            .get("program", {})
            .get("phases", [{}])[0]
            .get("protocol")
        )
        assert phase_protocol == entry.recipe.get("protocol"), (
            f"Registry protocol mismatch for '{key}': "
            f"fixture built protocol '{phase_protocol}' != registry recipe '{entry.recipe.get('protocol')}'."
        )

