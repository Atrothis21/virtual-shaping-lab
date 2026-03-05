from __future__ import annotations

from experiment.factories.phase_factory import PHASE_REGISTRY
from experiment.factories.phase_factory import build_phase
from experiment.phases.templates import PhaseTemplate


class _DummyAgent:
    policy = type("P", (), {"actions": ["left", "right"]})()

    def observe(self, obs):
        return obs

    def act(self, state, actions=None, rng=None):
        return actions[0] if actions else None

    def learn(self, transition):
        return None


_CANONICAL_CLASSICAL_PHASE_INPUTS = {
    "acquisition": {"stimuli": {"cs_plus": ["tone"]}},
    "nonreinforcement": {"stimuli": {"cs_plus": ["tone"]}},
    "compound_acquisition": {"stimuli": {"compound": ["tone", "noise"]}},
    "compound_nonreinforcement": {"stimuli": {"compound": ["tone", "noise"]}},
    "differential_acquisition": {"stimuli": {"cs_plus": ["tone"], "cs_minus": ["noise"]}},
    "probe": {"stimuli": {"cs_plus": ["tone"]}},
}

_REMOVED_LEGACY_KEYS = {
    "acquisition_legacy",
    "nonreinforcement_legacy",
    "compound_acquisition_legacy",
    "compound_nonreinforcement_legacy",
    "differential_acquisition_legacy",
    "probe_legacy",
}


def test_canonical_classical_phase_keys_resolve_to_template_only():
    agent = _DummyAgent()
    for phase_key, kwargs in _CANONICAL_CLASSICAL_PHASE_INPUTS.items():
        phase = build_phase(
            phase_key,
            agent=agent,
            n_trials=1,
            **kwargs,
        )
        assert isinstance(
            phase, PhaseTemplate
        ), f"Canonical key '{phase_key}' must resolve to PhaseTemplate."


def test_legacy_aliases_are_removed():
    for key in _REMOVED_LEGACY_KEYS:
        assert key not in PHASE_REGISTRY
