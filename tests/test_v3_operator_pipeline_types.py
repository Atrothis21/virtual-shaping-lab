from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.rollout.operator_pipeline import (
    LookaheadContract,
    NORMATIVE_STAGE_LOOKAHEAD,
    NORMATIVE_STAGE_CONTRACTS,
    NORMATIVE_STAGE_ORDER,
    PIPELINE_BASE_FIELDS,
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


def test_v3_operator_stage_lookahead_contract_roundtrip():
    stage = OperatorStage(
        key="Err",
        required_fields=("x", "y"),
        produced_fields=("z",),
        lookahead=LookaheadContract(source_stage="Env", relation="post", required_fields=("y", "z")),
    )
    rebuilt = OperatorStage.from_dict(stage.to_dict())
    assert rebuilt == stage


def test_v3_operator_stage_lookahead_contract_validation():
    with pytest.raises(ValueError, match="source_stage"):
        LookaheadContract(source_stage="")
    with pytest.raises(ValueError, match="relation must be 'post'"):
        LookaheadContract(source_stage="Env", relation="pre")
    with pytest.raises(ValueError, match="required_fields must be unique"):
        LookaheadContract(source_stage="Env", required_fields=("y", "y"))


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


def test_v3_operator_pipeline_type_chain_gate_rejects_missing_required_field():
    with pytest.raises(ValueError, match="type-chain violation"):
        OperatorPipeline(
            stages=[
                OperatorStage(key="Phi", required_fields=("s",), produced_fields=("x",)),
                OperatorStage(key="Policy", required_fields=("x", "w", "a"), produced_fields=("u",)),
            ]
        )


def test_v3_operator_pipeline_type_chain_gate_accepts_base_fields():
    pipeline = OperatorPipeline(
        stages=[
            OperatorStage(key="Phi", required_fields=("s",), produced_fields=("x",)),
            OperatorStage(key="Policy", required_fields=("x", "a"), produced_fields=("u",)),
        ]
    )
    assert pipeline.stage_keys() == ("Phi", "Policy")
    assert "a" in PIPELINE_BASE_FIELDS


def test_v3_operator_pipeline_normative_lookahead_attaches_to_err_stage():
    pipeline = default_operator_pipeline()
    stage_map = {stage.key: stage for stage in pipeline.stages}
    err = stage_map["Err"]
    assert err.lookahead is not None
    assert err.lookahead.source_stage == "Env"
    assert err.lookahead.relation == "post"
    assert err.lookahead.required_fields == NORMATIVE_STAGE_LOOKAHEAD["Err"]["required_fields"]


def test_v3_operator_pipeline_rejects_invalid_post_lookahead_ordering():
    with pytest.raises(ValueError, match="post-lookahead"):
        OperatorPipeline(
            stages=[
                OperatorStage(
                    key="Err",
                    lookahead=LookaheadContract(source_stage="Env", relation="post", required_fields=("y",)),
                ),
                OperatorStage(key="Env"),
            ]
        )
