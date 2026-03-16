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
    CATALOG_VERSION = 1
    RECORD_SCHEMA_VERSION = "v1"
    TEMPLATE_VERSION_USED = 1

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
    def math_objects() -> dict[str, list[dict[str, Any]]]:
        return {
            "representation": [
                {"key": "context_map", "variant": "default", "module": "representation_objects"},
                {"key": "similarity_kernel", "variant": "matrix", "module": "representation_objects"},
                {"key": "salience_operator", "variant": "diagonal", "module": "salience_objects"},
                {
                    "key": "temporal_basis",
                    "variant": "identity|bins|traces",
                    "module": "temporal_objects",
                },
            ],
            "learning": [
                {
                    "key": "prediction_error_rule",
                    "variant": "rescorla_wagner|td_value",
                    "module": "prediction_error_objects",
                },
                {
                    "key": "attention_mechanism",
                    "variant": "none|static|pearce_hall|mackintosh",
                    "module": "attention_objects",
                },
            ],
            "control": [
                {
                    "key": "policy_kernel",
                    "variant": "null|fixed|epsilon_greedy|softmax",
                    "module": "policies",
                },
            ],
        }

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
                "expected_signals": list(spec.expected_signals),
                "default_template_key": spec.default_template_key,
                "recommended_template_key": spec.recommended_template_key,
                "recommended_figures": list(spec.recommended_figures),
                "default_run_modes": list(spec.default_run_modes),
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
            "math_objects": cls.math_objects(),
            "report_templates": cls.report_templates(),
        }

    @classmethod
    def version_info(cls) -> dict[str, Any]:
        return {
            "catalog_version": cls.CATALOG_VERSION,
            "record_schema_version": cls.RECORD_SCHEMA_VERSION,
            "template_version_used": cls.TEMPLATE_VERSION_USED,
        }

