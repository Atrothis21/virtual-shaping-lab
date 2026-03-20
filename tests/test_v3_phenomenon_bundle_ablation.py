from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

from api import services as api_services
from virtual_shaping_lab.vsl.operator import default_operator_pipeline
from virtual_shaping_lab.vsl.registry import PHENOMENON_REGISTRY


def _resolve_fixture_callable(fixture_ref: str):
    module_path, callable_name = fixture_ref.split("::", 1)
    absolute = Path(module_path).resolve()
    spec = importlib.util.spec_from_file_location("v3_registry_fixture_module_ablation", str(absolute))
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


def _pipeline_with_ablated_stage_key(stage_key: str) -> dict:
    payload = default_operator_pipeline().to_dict()
    replacement = f"__ablated_{stage_key}"
    found = False
    for stage in payload["stages"]:
        if stage.get("key") == stage_key:
            stage["key"] = replacement
            stage["name"] = replacement
            found = True
    if not found:
        raise AssertionError(f"Unable to ablate missing stage key '{stage_key}'.")

    for stage in payload["stages"]:
        lookahead = stage.get("lookahead")
        if isinstance(lookahead, dict) and lookahead.get("source_stage") == stage_key:
            lookahead["source_stage"] = replacement
    return payload


def test_v3_slice4_registry_entries_are_resolvable_with_default_pipeline():
    for key, entry in PHENOMENON_REGISTRY.items():
        fixture_builder = _resolve_fixture_callable(entry.fixture)
        payload = fixture_builder()
        resolved = api_services.PlanService.resolve(payload)
        assert isinstance(resolved.get("stable_hash"), str) and resolved["stable_hash"], (
            f"Registry fixture for '{key}' did not resolve through PlanService."
        )


@pytest.mark.parametrize("entry_key", sorted(PHENOMENON_REGISTRY.keys()))
def test_v3_slice4_required_operator_ablation_fails(entry_key: str):
    entry = PHENOMENON_REGISTRY[entry_key]
    fixture_builder = _resolve_fixture_callable(entry.fixture)
    payload = fixture_builder()

    required_ops = tuple(entry.constraints.required_operators)
    assert required_ops, f"Registry entry '{entry_key}' must declare required operators."

    for missing_stage in required_ops:
        candidate = copy.deepcopy(payload)
        runtime = candidate.setdefault("experiment", {}).setdefault("runtime", {})
        runtime["operator_pipeline"] = _pipeline_with_ablated_stage_key(missing_stage)
        with pytest.raises(ValueError, match="Operator-constraint violation"):
            api_services.PlanService.resolve(candidate)
