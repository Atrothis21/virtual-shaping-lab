from __future__ import annotations

import pytest

from virtual_shaping_lab.vsl.operator import OperatorPipeline, OperatorStage


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

