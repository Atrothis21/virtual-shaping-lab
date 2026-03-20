from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "v3_namespace_migration_map.md"


def _read() -> str:
    return DOC.read_text(encoding="utf-8")


def test_v3_slice1_namespace_migration_map_exists():
    assert DOC.exists()


def test_v3_slice1_namespace_migration_map_declares_required_columns():
    text = _read()
    assert "Legacy Import Path" in text
    assert "Target Import Path" in text
    assert "Warning Window" in text
    assert "Removal Release" in text
    assert "Release Owner" in text


def test_v3_slice1_namespace_migration_map_declares_warning_and_removal_policy():
    text = _read()
    assert "V3.9.0-V3.9.2" in text
    assert "V3.10.0" in text


def test_v3_slice1_namespace_migration_map_covers_entry_roots():
    text = _read()
    required_roots = [
        "vsl/spec/",
        "vsl/program/",
        "vsl/environment/",
        "vsl/agent/representation/",
        "vsl/agent/learning/",
        "vsl/agent/policy/",
        "vsl/rollout/",
        "vsl/records/",
        "vsl/analysis/",
        "vsl/registry/",
    ]
    for root in required_roots:
        assert root in text
