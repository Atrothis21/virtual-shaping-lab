from __future__ import annotations

from pathlib import Path

from api import run as api_run


ROOT = Path(__file__).resolve().parents[1]
JS_DIR = ROOT / "virtual_shaping_lab" / "ui" / "js" / "react"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_tuple_compatibility_api_returns_expected_outcome_status_and_explanation():
    body = api_run.tuple_authoring_compatibility_api(
        {
            "arrangement": "pavlovian",
            "task": "acquisition",
            "agent": "rw_classical",
            "edits": {"n_trials": 20},
        }
    )
    assert body["status"] == "success"
    assert isinstance(body["explanation"], str) and body["explanation"]
    assert isinstance(body.get("key_operator_factors"), list)


def test_tuple_compatibility_api_structurally_invalid_tuple_blocks_run_path():
    body = api_run.tuple_authoring_compatibility_api(
        {
            "arrangement": "hybrid",
            "task": "acquisition",
            "agent": "legacy_hybrid_bundle",
            "edits": {},
        }
    )
    assert body["status"] == "structurally_invalid"
    assert body["source"] == "legality_engine"


def test_tuple_compatibility_api_behaviorally_unsupported_guidance_surface():
    body = api_run.tuple_authoring_compatibility_api(
        {
            "arrangement": "operant",
            "task": "extinction",
            "agent": "rw_operant",
            "edits": {},
        }
    )
    assert body["status"] == "behaviorally_unsupported"
    assert isinstance(body["unmet_behavioral_requirements"], list)
    assert body["unmet_behavioral_requirements"]


def test_ui_expected_outcome_panel_contract_is_present_and_run_blocking_is_explicit():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert "EXPECTED_OUTCOME_STATUSES" in src
    assert "fetchTupleCompatibility(" in src
    assert "/catalog/tuple-authoring/compatibility" in src
    assert "deriveExpectedOutcomePanelModel(" in src
    assert "canRunForExpectedOutcome(" in src
    assert 'status !== "structurally_invalid"' in src


def test_ui_expected_outcome_panel_enforces_explanation_source_integrity():
    src = _read(JS_DIR / "tuple_authoring_flow.jsx")
    assert 'source === "behavioral_registry"' in src
    assert 'source === "behavioral_registry_fallback"' in src
    assert 'source === "legality_engine"' in src
    assert "source_integrity_ok" in src

