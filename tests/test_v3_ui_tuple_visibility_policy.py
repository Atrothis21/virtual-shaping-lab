from __future__ import annotations

from pathlib import Path

from api import run as api_run


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_tuple_visibility_policy_hides_structurally_impossible_agents_and_disables_invalid():
    catalog = api_run.tuple_authoring_catalog_api(arrangement="operant", task="acquisition")
    agents = {entry["id"]: entry for entry in catalog["agents"]}
    assert "rw_operant" in agents
    assert "rw_classical" in agents
    assert agents["rw_operant"]["enabled"] is True
    assert agents["rw_classical"]["enabled"] is False
    assert isinstance(agents["rw_classical"]["reason"], str) and agents["rw_classical"]["reason"]


def test_tuple_visibility_policy_contract_is_explicit_in_ui_flow_module():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "VISIBILITY_POLICY" in src
    assert "hide_structurally_impossible_agents" in src
    assert "show_disabled_behaviorally_invalid_agents" in src
    assert "disabled_reason" in src


def test_tuple_route_level_authoring_contract_is_migrated():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "fetchTupleCatalog" in src
    assert "deriveTupleSelectionModel" in src
    assert "authoring_mode" in src
    assert "tuple_v1" not in src  # mode identity comes from API contract payload, not hardcoded route literals

