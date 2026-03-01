from experiment.runtime_records import (
    FinalizationContext,
    ProtocolMetadataNormalizer,
    RecordFinalizationPipeline,
    SchemaDefaultsNormalizer,
    finalize_record,
)


def test_finalize_record_sets_fields():
    record = {"phase": "acquisition"}
    finalize_record(
        record,
        phase_name="Phase 1",
        protocol_phase_index=0,
        protocol_phase_name="acquisition",
    )
    assert record["phase_name"] == "Phase 1"
    assert record["subphase"] == 0
    assert record["subphase_name"] == "acquisition"


def test_finalize_record_applies_stable_trial_record_schema_defaults():
    record = {"phase": "acquisition", "trial": 2, "reward": 1.0}
    out = finalize_record(record, phase_name="acquisition")
    for key in (
        "phase",
        "phase_name",
        "protocol_name",
        "unit_path",
        "subphase",
        "subphase_name",
        "trial",
        "tick",
        "t_s",
        "dt_s",
        "trial_step",
        "trial_id",
        "context",
        "stimulus",
        "stimulus_type",
        "action",
        "response",
        "reward",
        "prediction",
        "outcome_type",
        "schedule",
        "done",
        "learning_enabled",
        "metadata",
    ):
        assert key in out
    assert out["metadata"] == {}


def test_record_finalization_pipeline_matches_finalize_record_contract():
    pipeline = RecordFinalizationPipeline(
        normalizers=[SchemaDefaultsNormalizer(), ProtocolMetadataNormalizer()]
    )
    rec = {"phase": "acquisition", "trial": 1}
    out = pipeline.finalize(
        rec,
        FinalizationContext(
            phase_name="acquisition",
            protocol_phase_index=0,
            protocol_phase_name="acquisition",
        ),
    )
    assert out["phase_name"] == "acquisition"
    assert out["subphase"] == 0
    assert out["subphase_name"] == "acquisition"
    assert "metadata" in out
