from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl import (
    EpisodeSpec,
    HorizonSpec,
    RolloutRecord,
    SUPPORTED_TEMPORAL_BASIS_VARIANTS,
    TemporalBasisSpec,
    TerminationCondition,
)
from virtual_shaping_lab.vsl.spec import ExperimentSpec


def test_v3_7_entry_rollout_schema_has_episode_identity():
    record = RolloutRecord(
        rollout_id="r0",
        episode_id=1,
        segment_key="seg0",
        protocol="acquisition",
        trial_type="cs_plus",
    )
    assert record.episode_id == 1


def test_v3_7_entry_typed_plan_identity_surface_exists():
    spec = ExperimentSpec.from_dict(
        {
            "program": {"phases": [], "resolved_phase_contexts": []},
            "agent": {
                "agent": "classical_agent",
                "representation": {"name": "vector_elemental", "params": {"stimuli": ["tone"]}},
                "learning": {"rule": "rescorla_wagner", "params": {}, "attention": {"initial": {}, "config": {}}},
                "policy": None,
            },
            "runtime": {"runtime": {}, "context_inference": {}, "resolved_plan": True, "composed_parameters": {}},
            "analysis": {"report_preset": "acquisition"},
            "environment_program": {"segments": [], "metadata": {}},
            "canonical_payload": {"experiment": {"program": {"phases": []}, "agent": {}, "runtime": {}}, "report": {}},
        }
    )
    assert isinstance(spec.stable_hash(), str) and spec.stable_hash()


def test_v3_temporal_basis_spec_roundtrip_and_hash():
    spec = TemporalBasisSpec(variant="trace", dimension=4, enabled=True, params={"decay": 0.9})
    rebuilt = TemporalBasisSpec.from_dict(spec.to_dict())
    assert spec.variant == "traces"
    assert rebuilt.to_dict() == spec.to_dict()
    hashes = [spec.stable_hash() for _ in range(10)]
    assert len(set(hashes)) == 1


def test_v3_temporal_basis_spec_rejects_invalid_shape():
    with pytest.raises(ValueError, match="variant"):
        TemporalBasisSpec(variant="missing_variant", dimension=2, enabled=True)
    with pytest.raises(ValueError, match="dimension"):
        TemporalBasisSpec(variant="identity", dimension=0, enabled=True)


def test_v3_temporal_fixture_coverage_has_two_fixtures_per_supported_basis():
    fixtures = [
        TemporalBasisSpec(variant="identity", dimension=1, enabled=False, params={}),
        TemporalBasisSpec(variant="identity", dimension=2, enabled=True, params={"scale": 1.0}),
        TemporalBasisSpec(variant="bins", dimension=3, enabled=True, params={"max_time_s": 2.0}),
        TemporalBasisSpec(variant="binned", dimension=4, enabled=True, params={"max_time_s": 4.0}),
        TemporalBasisSpec(variant="traces", dimension=2, enabled=True, params={"decay": 0.9}),
        TemporalBasisSpec(variant="trace", dimension=3, enabled=True, params={"decay": 0.8}),
    ]
    counts = {variant: 0 for variant in SUPPORTED_TEMPORAL_BASIS_VARIANTS}
    for spec in fixtures:
        counts[spec.variant] += 1
    for variant in SUPPORTED_TEMPORAL_BASIS_VARIANTS:
        assert counts[variant] >= 2


def test_v3_horizon_spec_requires_positive_bound_and_roundtrips():
    spec = HorizonSpec(max_steps=50, max_duration_s=30.0, stop_reason="horizon_exhausted")
    rebuilt = HorizonSpec.from_dict(spec.to_dict())
    assert rebuilt.to_dict() == spec.to_dict()
    with pytest.raises(ValueError, match="requires max_steps and/or max_duration_s"):
        HorizonSpec(max_steps=None, max_duration_s=None)
    with pytest.raises(ValueError, match="max_steps"):
        HorizonSpec(max_steps=0, max_duration_s=None)


def test_v3_episode_spec_and_termination_condition_types():
    term = TerminationCondition(reason="running", terminal=False, metadata={"source": "runtime"})
    episode = EpisodeSpec(
        episode_id=3,
        rollout_id="rollout_A",
        seed=11,
        horizon=HorizonSpec(max_steps=10),
        termination=term,
    )
    rebuilt = EpisodeSpec.from_dict(episode.to_dict())
    assert rebuilt.to_dict() == episode.to_dict()
    assert isinstance(episode.stable_hash(), str) and episode.stable_hash()
    with pytest.raises(ValueError, match="rollout_id"):
        EpisodeSpec(episode_id=0, rollout_id="", horizon=HorizonSpec(max_steps=1))
    with pytest.raises(ValueError, match="TerminationCondition.reason"):
        TerminationCondition(reason=" ", terminal=True)
