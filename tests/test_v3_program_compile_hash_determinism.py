from __future__ import annotations

from preset_payloads import PRESET_PAYLOADS

from virtual_shaping_lab.vsl.program import compile_environment_program, supported_compile_protocols


def _phase_payload_from_canonical_payload(payload: dict) -> dict:
    phases = payload["experiment"]["program"]["phases"]
    return {"phases": phases}


def test_compile_hash_is_stable_for_supported_canonical_fixtures():
    supported = set(supported_compile_protocols())
    candidate_payloads: list[tuple[str, dict]] = []

    for name, payload in PRESET_PAYLOADS:
        phases = payload["experiment"]["program"]["phases"]
        protocols = {str(p.get("protocol", "")).strip().lower() for p in phases}
        if protocols and protocols.issubset(supported):
            candidate_payloads.append((name, payload))

    assert candidate_payloads, "Expected at least one canonical fixture supported by V3.2 compiler."

    for name, payload in candidate_payloads:
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
