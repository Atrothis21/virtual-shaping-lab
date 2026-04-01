from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_v3_20_15_harness_routes_through_compositional_agent_single_path():
    text = (ROOT / "virtual_shaping_lab" / "vsl" / "rollout" / "harness.py").read_text(encoding="utf-8")
    assert "self._agent.pre_outcome_step(" in text
    assert "self._agent.learn(" in text
    assert "self._observation_adapter.step(" not in text
    assert "self._policy_adapter.step(" not in text
    assert "self._learner_adapter.step(" not in text
