"""Canonical runtime payload contract helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


def _is_canonical_experiment(exp: dict[str, Any]) -> bool:
    return all(key in exp for key in ("program", "agent", "runtime"))


def _is_legacy_experiment(exp: dict[str, Any]) -> bool:
    legacy_keys = {
        "learner",
        "representation",
        "phases",
        "protocol",
        "stimuli",
        "params",
        "salience",
        "attention",
        "attention_config",
    }
    return any(key in exp for key in legacy_keys)


def _assert_payload_shape(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("Payload must be an object.")
    if not isinstance(payload.get("experiment"), dict):
        raise ValueError("Payload missing 'experiment' object.")
    if not isinstance(payload.get("report"), dict):
        raise ValueError("Payload missing 'report' object.")


def _assert_no_mixed_shape(exp: dict[str, Any]) -> None:
    agent_field = exp.get("agent")
    has_canonical = (
        "program" in exp
        or (
            isinstance(agent_field, dict)
            and ("representation" in agent_field or "learning" in agent_field or "policy" in agent_field)
        )
    )
    has_legacy = _is_legacy_experiment(exp)
    if has_canonical and has_legacy:
        raise ValueError(
            "Mixed payload shape detected: provide either canonical "
            "experiment.program/experiment.agent/experiment.runtime or legacy flat experiment fields, not both."
        )


def normalize_phase_trials(
    phases: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for idx, phase in enumerate(phases):
        if not isinstance(phase, dict):
            raise ValueError(f"program.phases[{idx}] must be an object.")
        out = dict(phase)
        params = out.get("params")
        if params is None:
            params = {}
        if not isinstance(params, dict):
            raise ValueError(f"program.phases[{idx}].params must be an object.")
        out["params"] = dict(params)

        trials = out.get("trials")
        if trials is None:
            raise ValueError(f"program.phases[{idx}] is missing required 'trials'.")
        try:
            trials = int(trials)
        except (TypeError, ValueError):
            raise ValueError(f"program.phases[{idx}].trials must be an integer.")
        if trials <= 0:
            raise ValueError(f"program.phases[{idx}].trials must be > 0.")
        out["trials"] = trials
        out["params"]["n_trials"] = trials
        normalized.append(out)
    return normalized


def _canonical_phases(exp: dict[str, Any]) -> list[dict[str, Any]]:
    program = exp.get("program")
    if not isinstance(program, dict):
        raise ValueError("Canonical payload requires experiment.program object.")
    phases = program.get("phases")
    if not isinstance(phases, list) or not phases:
        raise ValueError("Canonical payload requires non-empty experiment.program.phases.")
    raw = [dict(p) for p in phases if isinstance(p, dict)]
    if len(raw) != len(phases):
        raise ValueError("experiment.program.phases entries must be objects.")
    return normalize_phase_trials(raw)


def to_canonical_payload(payload: dict[str, Any]) -> dict[str, Any]:
    _assert_payload_shape(payload)
    src = deepcopy(payload)
    exp = src["experiment"]
    _assert_no_mixed_shape(exp)

    if _is_legacy_experiment(exp):
        raise ValueError(
            "Legacy payload shape is no longer accepted at runtime; "
            "provide canonical experiment.program/experiment.agent/experiment.runtime."
        )

    if not _is_canonical_experiment(exp):
        raise ValueError(
            "Payload experiment must use canonical keys "
            "(program, agent, runtime)."
        )

    phases = _canonical_phases(exp)
    runtime = exp.get("runtime")
    if runtime is None:
        runtime = {}
    if not isinstance(runtime, dict):
        raise ValueError("experiment.runtime must be an object.")

    agent = exp.get("agent")
    if not isinstance(agent, dict):
        raise ValueError("experiment.agent must be an object.")
    if not isinstance(agent.get("representation"), dict):
        raise ValueError("experiment.agent.representation must be an object.")
    if not isinstance(agent.get("learning"), dict):
        raise ValueError("experiment.agent.learning must be an object.")

    out = {
        "experiment": {
            "program": {"phases": phases},
            "agent": {
                "name": agent.get("name"),
                "representation": deepcopy(agent.get("representation")),
                "learning": deepcopy(agent.get("learning")),
                "policy": deepcopy(agent.get("policy")),
            },
            "runtime": deepcopy(runtime),
        },
        "report": deepcopy(src.get("report", {})),
    }
    return out
