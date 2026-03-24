from __future__ import annotations

from pathlib import Path

from api import run as api_run


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_preset_route_migration_catalog_endpoint_shape():
    body = api_run.preset_route_migration_api()
    assert isinstance(body.get("contract_version"), str) and body["contract_version"]
    assert body["strategy"] == "overlay_gradual"
    assert isinstance(body["tuple_first_preset_routes"], list)
    assert isinstance(body["basis_first_preset_routes"], list)
    assert isinstance(body["legacy_fallback_preset_routes"], list)
    assert not set(body["tuple_first_preset_routes"]).intersection(set(body["legacy_fallback_preset_routes"]))
    assert not set(body["basis_first_preset_routes"]).intersection(set(body["legacy_fallback_preset_routes"]))


def test_tuple_materialization_deprecated_shape_includes_route_strategy_diagnostics():
    body = api_run.materialize_tuple_authoring_api(
        {
            "preset_id": "acquisition",
            "edits": {"n_trials": 7, "cs_plus": ["tone"]},
        }
    )
    diagnostics = body.get("tuple_route_migration_diagnostics", {})
    assert diagnostics.get("deprecated_input_detected") is True
    assert diagnostics.get("route_migration_strategy") == "overlay_gradual"
    assert isinstance(diagnostics.get("basis_first_preset_routes"), list)
    assert "acquisition" in diagnostics.get("basis_first_preset_routes", [])


def test_teaching_panel_declares_explicit_route_migration_map_contract():
    src = _read(JS_DIR / "teaching_panel.jsx")
    assert "PRESET_ROUTE_MIGRATION_MAP" in src
    assert "LEGACY_FALLBACK_PRESET_ROUTES" in src
    assert "tuple_first_preset_routes" in src
    assert "basis_first_preset_routes" in src
    assert "legacy_fallback_preset_routes" in src
