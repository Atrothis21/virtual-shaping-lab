from __future__ import annotations

from pathlib import Path

from virtual_shaping_lab.vsl.agent.observation import (
    executable_observation_preset_names,
    observation_preset_hash,
    observation_registry_hash,
)


ROOT = Path(__file__).resolve().parents[1]

_PHASE_FILES = [
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "acquisition.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "compound_acquisition.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "compound_nonreinforcement.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "concurrent_schedule.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "criterion_shift.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "differential_acquisition.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "nonreinforcement.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "operant_acquisition.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "probe.py",
]


def test_v3_19_15_phase_surfaces_do_not_use_legacy_make_observation_helper():
    violations: list[str] = []
    for path in _PHASE_FILES:
        text = path.read_text(encoding="utf-8")
        if "make_observation(" in text:
            violations.append(str(path.relative_to(ROOT)))
        if "agents.representations.observation import make_observation" in text:
            violations.append(str(path.relative_to(ROOT)))
    assert not violations, f"Legacy make_observation usage found in phase surfaces: {violations}"


def test_v3_19_15_runtime_learner_adapter_no_longer_exposes_raw_stimulus_branch():
    text = (
        ROOT
        / "virtual_shaping_lab"
        / "vsl"
        / "runtime"
        / "learner_adapter.py"
    ).read_text(encoding="utf-8")
    assert "_coerce_features_from_stimulus" not in text
    assert "stimulus: Mapping[str, Any]" not in text
    assert "next_stimulus" not in text
    assert "observation_features" in text


def test_v3_19_15_observation_contract_hash_snapshots_are_stable():
    assert executable_observation_preset_names() == [
        "identity_observation",
        "elemental_identity",
        "elemental_context_tag",
        "configural_identity",
        "elemental_kernel_generalization",
    ]
    registry_hashes = [observation_registry_hash() for _ in range(10)]
    preset_hashes = [observation_preset_hash("classical_identity") for _ in range(10)]
    assert len(set(registry_hashes)) == 1
    assert len(set(preset_hashes)) == 1
    assert isinstance(registry_hashes[0], str) and len(registry_hashes[0]) == 64
    assert isinstance(preset_hashes[0], str) and len(preset_hashes[0]) == 64
