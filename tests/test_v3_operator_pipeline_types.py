from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.operator import (
    NORMATIVE_STAGE_CONTRACTS,
    NORMATIVE_STAGE_ORDER,
    OperatorPipeline,
    OperatorStage,
    default_operator_pipeline,
)


def _sample_pipeline() -> OperatorPipeline:
    return OperatorPipeline(
        stages=[
            OperatorStage(key="Phi"),
            OperatorStage(key="Policy"),
            OperatorStage(key="Env"),
        ],
        metadata={"version": "3.4.5"},
    )


def test_v3_operator_pipeline_roundtrip():
    pipeline = _sample_pipeline()
    blob = pipeline.to_dict()
    rebuilt = OperatorPipeline.from_dict(blob)
    assert rebuilt.to_dict() == blob


def test_v3_operator_pipeline_hash_is_stable():
    pipeline = _sample_pipeline()
    hashes = [pipeline.stable_hash() for _ in range(20)]
    assert len(set(hashes)) == 1


def test_v3_operator_pipeline_validation():
    with pytest.raises(ValueError, match="OperatorStage.key"):
        OperatorStage(key="")

    with pytest.raises(ValueError, match="OperatorPipeline.stages must be non-empty"):
        OperatorPipeline(stages=[])

    with pytest.raises(ValueError, match="unique stage keys"):
        OperatorPipeline(stages=[OperatorStage(key="Phi"), OperatorStage(key="Phi")])


def test_v3_operator_pipeline_stage_names_default_to_key():
    stage = OperatorStage(key="Update")
    assert stage.name == "Update"


def test_v3_operator_stage_contract_metadata_roundtrip():
    stage = OperatorStage(
        key="Err",
        required_fields=("x", "y"),
        produced_fields=("z",),
    )
    rebuilt = OperatorStage.from_dict(stage.to_dict())
    assert rebuilt == stage


def test_v3_operator_stage_contract_metadata_validation():
    with pytest.raises(ValueError, match="required_fields must be unique"):
        OperatorStage(key="Err", required_fields=("x", "x"))
    with pytest.raises(ValueError, match="produced_fields must be unique"):
        OperatorStage(key="Err", produced_fields=("z", "z"))
    with pytest.raises(ValueError, match="required_fields must contain non-empty strings"):
        OperatorStage(key="Err", required_fields=("x", ""))


def test_v3_operator_pipeline_normative_stage_order_contract():
    expected = (
        "Phi",
        "C",
        "G",
        "E",
        "P",
        "Policy",
        "Env",
        "Err",
        "A",
        "Update",
        "Measure",
    )
    assert NORMATIVE_STAGE_ORDER == expected


def test_v3_operator_pipeline_default_declaration_uses_normative_order():
    pipeline = default_operator_pipeline()
    assert pipeline.stage_keys() == NORMATIVE_STAGE_ORDER
    assert pipeline.metadata.get("normative") is True


def test_v3_operator_pipeline_normative_contracts_attach_to_stages():
    pipeline = default_operator_pipeline()
    stage_map = {stage.key: stage for stage in pipeline.stages}
    assert set(stage_map.keys()) == set(NORMATIVE_STAGE_CONTRACTS.keys())
    for key, contract in NORMATIVE_STAGE_CONTRACTS.items():
        stage = stage_map[key]
        assert stage.required_fields == contract["required_fields"]
        assert stage.produced_fields == contract["produced_fields"]
