from __future__ import annotations

import copy

import pytest

from experiment.assemble import assemble_experiment
from experiment.config import ExperimentConfig
from experiment.protocol_phase_boundary import (
    ProtocolPhaseBoundaryError,
    derive_unit_build_key,
    resolve_unit_build_boundary,
)
from ui.contracts.operator_plan_materialization import compile_and_materialize_operator_plan
from ui.contracts.operator_subset_contract import PRESET_DEFINITION_TEMPLATE


def _canonical_fixture_payload(payload):
    exp = payload["experiment"]
    phases = exp.get("phases")
    if phases is None:
        phases = [
            {
                "name": "Phase 0",
                "protocol": exp.get("protocol"),
                "stimuli": exp.get("stimuli", {}),
                "params": exp.get("params", {}),
            }
        ]
    canonical_phases = []
    for idx, phase in enumerate(phases):
        params = dict(phase.get("params", {}) or {})
        trials = int(phase.get("trials", params.get("n_trials", 1)))
        params.setdefault("n_trials", trials)
        canonical_phases.append(
            {
                "name": phase.get("name") or f"Phase {idx}",
                "protocol": phase.get("protocol"),
                "stimuli": phase.get("stimuli", {}),
                "params": params,
                "trials": trials,
            }
        )

    return {
        "experiment": {
            "program": {"phases": canonical_phases},
            "agent": {
                "name": exp.get("agent"),
                "representation": exp.get("representation"),
                "learning": {"rule": exp.get("learner"), "params": {}},
                "policy": exp.get("policy"),
            },
            "runtime": exp.get("runtime", {}),
        },
        "report": payload.get("report", {}),
    }


def test_resolve_protocol_phase_boundary_defaults():
    protocol_registry = {"extinction": object()}
    phase_registry = {"acquisition": object()}
    assert (
        resolve_unit_build_boundary(
            "acquisition",
            protocol_registry=protocol_registry,
            phase_registry=phase_registry,
        )
        == "phase"
    )
    assert (
        resolve_unit_build_boundary(
            "extinction",
            protocol_registry=protocol_registry,
            phase_registry=phase_registry,
        )
        == "protocol"
    )


def test_resolve_protocol_phase_boundary_override_to_phase_rejects_protocol_only_keys():
    protocol_registry = {"extinction": object()}
    phase_registry = {"acquisition": object()}
    with pytest.raises(ProtocolPhaseBoundaryError, match="no atomic phase builder"):
        resolve_unit_build_boundary(
            "extinction",
            protocol_registry=protocol_registry,
            phase_registry=phase_registry,
            requested_boundary="phase",
        )


def test_acquisition_assembly_path_invariant_is_atomic_phase_by_default():
    payload = _canonical_fixture_payload(
        {
            "experiment": {
                "learner": "rescorla_wagner",
                "agent": "classical_agent",
                "representation": {
                    "name": "vector_elemental",
                    "params": {"stimuli": ["tone"], "max_compound_size": 2},
                },
                "phases": [
                    {
                        "name": "Acquisition",
                        "protocol": "acquisition",
                        "stimuli": {"cs_plus": ["tone"]},
                        "params": {"n_trials": 1},
                    }
                ],
            },
            "report": {"preset": "acquisition"},
        }
    )
    config = ExperimentConfig.from_payload(payload)
    runtime_units, _agent, _representation = assemble_experiment(config)
    assert runtime_units
    assert runtime_units[0].build_boundary == "phase"
    assert isinstance(runtime_units[0].unit_build_key, str) and runtime_units[0].unit_build_key


def test_basis_materialized_boundary_override_is_honored_for_protocol_units():
    preset = copy.deepcopy(PRESET_DEFINITION_TEMPLATE)
    materialized = compile_and_materialize_operator_plan(
        preset,
        protocol_family="extinction",
        stimuli_catalog=["tone", "noise"],
    )
    phase = materialized["experiment"]["program"]["phases"][0]
    phase.setdefault("params", {})["build_boundary"] = "phase"

    payload = {
        "experiment": materialized["experiment"],
        "report": {"preset": "extinction"},
    }
    config = ExperimentConfig.from_payload(payload)
    with pytest.raises(ProtocolPhaseBoundaryError, match="no atomic phase builder"):
        assemble_experiment(config)


def test_unit_build_key_is_deterministic():
    key_a = derive_unit_build_key(
        phase_index=0,
        phase_name="Acquisition",
        protocol_name="acquisition",
        build_boundary="phase",
        context_id="A",
    )
    key_b = derive_unit_build_key(
        phase_index=0,
        phase_name="Acquisition",
        protocol_name="acquisition",
        build_boundary="phase",
        context_id="A",
    )
    assert key_a == key_b
