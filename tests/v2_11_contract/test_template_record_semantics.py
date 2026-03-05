from __future__ import annotations

from experiment.public import build_plan, run_from_plan

from preset_payloads import aba_renewal_payload, differential_acquisition_payload


def _run_records(payload: dict) -> list[dict]:
    result = run_from_plan(build_plan(payload), seed=123)
    return list(result.records)


def test_differential_acquisition_preserves_record_semantics():
    records = _run_records(differential_acquisition_payload())
    assert records, "Expected differential acquisition records."

    required_keys = {
        "phase_name",
        "subphase_name",
        "stimulus_type",
        "metadata",
        "learning_enabled",
        "context",
    }

    for rec in records:
        missing = required_keys - set(rec.keys())
        assert not missing, f"Missing required record keys: {sorted(missing)}"
        assert isinstance(rec.get("metadata"), dict)
        assert rec.get("phase_name") == "differential_acquisition"
        if rec.get("context_source") == "inferred":
            assert rec.get("inferred_context") == rec.get("context")
        else:
            assert "inferred_context" not in rec or rec.get("inferred_context") is None

    stim_types = {rec.get("stimulus_type") for rec in records}
    assert {"cs_plus", "cs_minus"}.issubset(stim_types)


def test_aba_renewal_preserves_subphase_and_context_semantics():
    records = _run_records(aba_renewal_payload())
    assert records, "Expected ABA renewal records."

    subphases = {rec.get("subphase_name") for rec in records}
    assert {"acquisition", "nonreinforcement", "probe"}.issubset(subphases)

    for rec in records:
        assert "context" in rec
        assert "metadata" in rec and isinstance(rec["metadata"], dict)
        if rec.get("context_source") == "inferred":
            assert rec.get("inferred_context") == rec.get("context")
        else:
            assert "inferred_context" not in rec or rec.get("inferred_context") is None
