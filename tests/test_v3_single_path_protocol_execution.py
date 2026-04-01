from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v3_21_15_harness_routes_protocol_flow_through_single_runtime_seam():
    text = (ROOT / "virtual_shaping_lab" / "vsl" / "rollout" / "harness.py").read_text(encoding="utf-8")
    assert "protocol_adapter = self._protocol_adapter_for_step(" in text
    assert "protocol_pre = protocol_adapter.emit(" in text
    assert "protocol_post = protocol_adapter.resolve(" in text
    assert "build_executable_protocol_preset(" not in text
    assert ".consequence_operator." not in text
    assert ".advance_operator." not in text
    assert ".stop_operator." not in text
