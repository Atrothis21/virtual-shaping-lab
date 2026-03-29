from __future__ import annotations

from virtual_shaping_lab.vsl.agent.observation import (
    IdentityGeneralizationOperator,
    IdentityRepresentationOperator,
    ObservationBundle,
    ObservationOutput,
    ObservationStepResult,
    StaticContextTagOperator,
)


def test_v3_19_5_observation_bundle_step_canonical_execution_and_output_shape():
    bundle = ObservationBundle(
        representation_operator=IdentityRepresentationOperator(),
        context_operator=StaticContextTagOperator(context_tags=["A", "B"]),
        generalization_operator=IdentityGeneralizationOperator(),
    )

    out = bundle.step(
        raw_stimulus={"tone": 1.0, "noise": 0.2},
        context_state="B",
        metadata={"source": "bundle_test"},
    )

    assert isinstance(out, ObservationStepResult)
    assert isinstance(out.output, ObservationOutput)
    assert out.output.feature_names == ["noise", "tone", "ctx:A", "ctx:B"]
    assert out.output.features == [0.2, 1.0, 0.0, 1.0]
    assert out.output.metadata["pipeline_order"] == ["represent", "contextualize", "generalize", "finalize"]
    traces = out.output.metadata["stage_traces"]
    assert set(traces.keys()) == {"representation", "context", "generalization"}
    assert traces["representation"]["feature_names"] == ["noise", "tone"]
    assert traces["context"]["feature_names"] == ["noise", "tone", "ctx:A", "ctx:B"]
    assert traces["generalization"]["metadata"]["variant"] == "identity_generalization"


def test_v3_19_5_observation_bundle_step_order_is_represent_context_generalize_finalize():
    calls: list[str] = []

    class _Rep:
        def represent(self, *, raw_stimulus, metadata=None):
            calls.append("represent")
            _ = metadata
            return {
                "representation_state": {"raw": raw_stimulus},
                "features": [1.0],
                "feature_names": ["tone"],
                "metadata": {"variant": "rep"},
            }

    class _Ctx:
        def contextualize(self, *, representation, context_state=None, metadata=None):
            calls.append("contextualize")
            _ = context_state, metadata
            return {
                "representation_state": representation["representation_state"],
                "context_state": "A",
                "features": [1.0, 1.0],
                "feature_names": ["tone", "ctx:A"],
                "metadata": {"variant": "ctx"},
            }

    class _Gen:
        def generalize(self, *, contextual_state, metadata=None):
            calls.append("generalize")
            _ = metadata
            return {
                "representation_state": contextual_state["representation_state"],
                "context_state": contextual_state["context_state"],
                "generalized_state": {"kind": "passthrough"},
                "features": [1.0, 1.0, 0.5],
                "feature_names": ["tone", "ctx:A", "gen:sim"],
                "metadata": {"variant": "gen"},
            }

    bundle = ObservationBundle(
        representation_operator=_Rep(),
        context_operator=_Ctx(),
        generalization_operator=_Gen(),
    )
    out = bundle.step(raw_stimulus={"tone": 1.0}, context_state="A")

    assert out.output.feature_names == ["tone", "ctx:A", "gen:sim"]
    assert out.output.features == [1.0, 1.0, 0.5]
    assert calls == ["represent", "contextualize", "generalize"]

