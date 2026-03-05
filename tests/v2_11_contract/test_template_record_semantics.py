from __future__ import annotations

from experiment.public import build_plan, run_from_plan

from preset_payloads import aba_renewal_payload, differential_acquisition_payload

_REQUIRED_BASE_RECORD_KEYS = {
    "phase",
    "phase_name",
    "subphase",
    "subphase_name",
    "trial",
    "stimulus",
    "stimulus_type",
    "context",
    "reward",
    "prediction",
    "learning_enabled",
    "metadata",
}


def _run_records(payload: dict) -> list[dict]:
    result = run_from_plan(build_plan(payload), seed=123)
    return list(result.records)


def test_differential_acquisition_preserves_record_semantics():
    records = _run_records(differential_acquisition_payload())
    assert records, "Expected differential acquisition records."

    for rec in records:
        missing = _REQUIRED_BASE_RECORD_KEYS - set(rec.keys())
        assert not missing, f"Missing required record keys: {sorted(missing)}"
        assert isinstance(rec.get("phase"), str) and rec.get("phase")
        assert isinstance(rec.get("phase_name"), str) and rec.get("phase_name")
        assert rec.get("subphase_name") is None or (
            isinstance(rec.get("subphase_name"), str) and rec.get("subphase_name")
        )
        assert rec.get("subphase") is None or isinstance(rec.get("subphase"), int)
        assert isinstance(rec.get("trial"), int)
        assert rec.get("stimulus_type") in {"cs_plus", "cs_minus"}
        assert isinstance(rec.get("context"), str) and rec.get("context")
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
        missing = _REQUIRED_BASE_RECORD_KEYS - set(rec.keys())
        assert not missing, f"Missing required record keys: {sorted(missing)}"
        assert isinstance(rec.get("phase"), str) and rec.get("phase")
        assert isinstance(rec.get("phase_name"), str) and rec.get("phase_name")
        assert rec.get("subphase_name") is None or (
            isinstance(rec.get("subphase_name"), str) and rec.get("subphase_name")
        )
        assert rec.get("subphase") is None or isinstance(rec.get("subphase"), int)
        assert isinstance(rec.get("trial"), int)
        assert "context" in rec
        assert isinstance(rec.get("context"), str) and rec.get("context")
        assert isinstance(rec.get("metadata"), dict)
        if rec.get("context_source") == "inferred":
            assert rec.get("inferred_context") == rec.get("context")
        else:
            assert "inferred_context" not in rec or rec.get("inferred_context") is None
