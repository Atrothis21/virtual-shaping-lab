import inspect

from agents.math_objects.interfaces import (
    IAttentionMechanism,
    IContextMap,
    IPredictionErrorRule,
    ISalienceOperator,
    ISimilarityKernel,
    ITemporalBasis,
)


def test_math_object_interfaces_expose_expected_contracts():
    expected = {
        IContextMap: ("apply",),
        ISimilarityKernel: ("similarity",),
        ISalienceOperator: ("apply",),
        ITemporalBasis: ("encode",),
        IPredictionErrorRule: ("compute",),
        IAttentionMechanism: ("current_alpha", "update_state"),
    }

    for iface, methods in expected.items():
        assert inspect.isclass(iface)
        for method_name in methods:
            assert callable(getattr(iface, method_name, None))


def test_math_object_interfaces_document_domain_and_codomain():
    interfaces = (
        IContextMap,
        ISimilarityKernel,
        ISalienceOperator,
        ITemporalBasis,
        IPredictionErrorRule,
        IAttentionMechanism,
    )

    for iface in interfaces:
        doc = inspect.getdoc(iface)
        assert doc is not None
        assert "Domain/codomain" in doc
