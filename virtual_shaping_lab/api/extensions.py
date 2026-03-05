"""Unified extension discovery facade for browser/API consumers."""

from __future__ import annotations

from typing import Any

from analysis.public import list_protocol_default_templates
from experiment.factories.learner_factory import LEARNER_REGISTRY
from experiment.factories.policy_factory import POLICY_REGISTRY
from experiment.factories.representation_factory import REPRESENTATION_REGISTRY
from experiment.phenomena.catalog import available_phenomena, get_phenomenon
from protocols.catalog import available_protocols
from virtual_shaping_lab.domain.naming import normalize_protocol_key


class ExtensionCatalog:
    @staticmethod
    def protocols() -> list[str]:
        return sorted({normalize_protocol_key(name) for name in available_protocols()})

    @staticmethod
    def learners() -> list[str]:
        return sorted(LEARNER_REGISTRY.keys())

    @staticmethod
    def policies() -> list[str]:
        return sorted(POLICY_REGISTRY.keys())

    @staticmethod
    def representations() -> list[str]:
        return sorted(REPRESENTATION_REGISTRY.keys())

    @staticmethod
    def report_templates() -> dict[str, dict[str, Any]]:
        return list_protocol_default_templates()

    @staticmethod
    def phenomena() -> dict[str, dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for key in available_phenomena():
            spec = get_phenomenon(key)
            out[key] = {
                "name": spec.name,
                "description": spec.description,
                "protocol_key": normalize_protocol_key(spec.protocol_key),
                "expected_signatures": list(spec.expected_signatures),
                "default_template_key": spec.default_template_key,
                "recommended_presets": [dict(p) for p in spec.recommended_presets],
            }
        return out

    @classmethod
    def snapshot(cls) -> dict[str, Any]:
        return {
            "protocols": cls.protocols(),
            "phenomena": cls.phenomena(),
            "learners": cls.learners(),
            "policies": cls.policies(),
            "representations": cls.representations(),
            "report_templates": cls.report_templates(),
        }

