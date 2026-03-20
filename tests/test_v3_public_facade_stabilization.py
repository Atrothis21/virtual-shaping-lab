from __future__ import annotations

import importlib
import warnings


CANONICAL_FACADE_MODULES = [
    "virtual_shaping_lab.vsl",
    "virtual_shaping_lab.vsl.rollout",
    "virtual_shaping_lab.vsl.spec",
    "virtual_shaping_lab.vsl.records",
    "virtual_shaping_lab.vsl.registry",
    "virtual_shaping_lab.vsl.agent.learning",
    "virtual_shaping_lab.vsl.agent.representation",
    "virtual_shaping_lab.vsl.environment",
]


def test_v3_slice3_canonical_facade_modules_do_not_emit_deprecation_warnings():
    for module_path in CANONICAL_FACADE_MODULES:
        module = importlib.import_module(module_path)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            importlib.reload(module)
        messages = [str(item.message) for item in caught if issubclass(item.category, DeprecationWarning)]
        assert not any("will be removed in V3.10.0" in msg for msg in messages), module_path


def test_v3_slice3_public_facade_exports_match_new_namespace_targets():
    import virtual_shaping_lab.vsl as vsl
    from virtual_shaping_lab.vsl.agent.learning.resolve import resolve_learner_spec
    from virtual_shaping_lab.vsl.records.schema import RolloutRecord
    from virtual_shaping_lab.vsl.registry.phenomena import PhenomenonRegistryEntry
    from virtual_shaping_lab.vsl.rollout.operator_pipeline import OperatorPipeline

    assert vsl.OperatorPipeline is OperatorPipeline
    assert vsl.RolloutRecord.__name__ == RolloutRecord.__name__
    assert vsl.RolloutRecord.__module__ == RolloutRecord.__module__
    assert vsl.PhenomenonRegistryEntry.__name__ == PhenomenonRegistryEntry.__name__
    assert vsl.PhenomenonRegistryEntry.__module__ == PhenomenonRegistryEntry.__module__
    assert vsl.resolve_learner_spec.__name__ == resolve_learner_spec.__name__
    assert vsl.resolve_learner_spec.__module__ == resolve_learner_spec.__module__
