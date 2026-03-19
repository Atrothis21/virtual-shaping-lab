from __future__ import annotations

from preset_payloads import PRESET_PAYLOADS

from virtual_shaping_lab.vsl.program import compile_environment_program, supported_compile_protocols

_REQUIRED_CANONICAL_PHASE_FAMILIES = {
    "acquisition",
    "acquisition_template",
    "nonreinforcement",
    "nonreinforcement_template",
    "extinction",
    "compound_acquisition",
    "compound_acquisition_template",
    "compound_nonreinforcement",
    "compound_nonreinforcement_template",
    "differential_acquisition",
    "differential_acquisition_template",
    "probe",
    "probe_template",
    "context_shift",
    "criterion_shift",
    "pavlovian_phase_template",
    "operant_phase_template",
}


def _phase_payload_from_canonical_payload(payload: dict) -> dict:
    phases = payload["experiment"]["program"]["phases"]
    return {"phases": phases}


def test_supported_protocols_cover_required_canonical_phase_families():
    supported = set(supported_compile_protocols())
    missing = sorted(_REQUIRED_CANONICAL_PHASE_FAMILIES - supported)
    assert not missing, f"Missing canonical phase families: {missing}"


def test_supported_protocols_cover_all_canonical_preset_fixtures():
    supported = set(supported_compile_protocols())
    missing: list[tuple[str, list[str]]] = []
    for name, payload in PRESET_PAYLOADS:
        phases = payload["experiment"]["program"]["phases"]
        protocols = sorted({str(p.get("protocol", "")).strip().lower() for p in phases})
        missing_protocols = [protocol for protocol in protocols if protocol not in supported]
        if missing_protocols:
            missing.append((name, missing_protocols))
    assert not missing, f"Compiler is missing canonical preset protocols: {missing}"


def test_compile_hash_is_stable_for_all_canonical_fixtures():
    assert PRESET_PAYLOADS, "Expected canonical preset fixtures."
    for name, payload in PRESET_PAYLOADS:
        compile_input = _phase_payload_from_canonical_payload(payload)
        hashes = [compile_environment_program(compile_input).stable_hash() for _ in range(20)]
        assert len(set(hashes)) == 1, f"Compile hash drift detected for fixture '{name}'."


def test_compile_hash_is_stable_for_extended_family_reference_fixtures():
    reference = [
        {
            "phases": [
                {
                    "name": "Diff",
                    "protocol": "differential_acquisition",
                    "stimuli": {"cs_plus": ["tone"], "cs_minus": ["noise"]},
                    "params": {"n_trials": 12},
                }
            ]
        },
        {
            "phases": [
                {
                    "name": "Probe",
                    "protocol": "probe",
                    "stimuli": {"cs_plus": ["tone"]},
                    "params": {"n_trials": 8},
                }
            ]
        },
        {
            "phases": [
                {
                    "name": "Context Shift",
                    "protocol": "context_shift",
                    "stimuli": {},
                    "params": {"context": "B", "n_trials": 1},
                }
            ]
        },
    ]

    for payload in reference:
        hashes = [compile_environment_program(payload).stable_hash() for _ in range(20)]
        assert len(set(hashes)) == 1
