from __future__ import annotations

from copy import deepcopy
from typing import Any


def from_legacy_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Test-only helper for legacy fixture normalization.

    Runtime payload conversion is intentionally removed from
    `experiment.payload_contract`; this adapter exists only to keep
    older test fixture definitions readable while closeout work proceeds.
    """
    if not isinstance(payload, dict) or not isinstance(payload.get("experiment"), dict):
        raise ValueError("Legacy payload must include experiment object.")

    src = deepcopy(payload)
    exp = src["experiment"]

    has_protocol = bool(exp.get("protocol"))
    phases = exp.get("phases")
    if has_protocol and phases:
        raise ValueError("Legacy payload must use either protocol or phases, not both.")
    if phases is None:
        phases = [
            {
                "name": "Phase 0",
                "protocol": exp.get("protocol"),
                "stimuli": deepcopy(exp.get("stimuli", {})),
                "params": deepcopy(exp.get("params", {})),
            }
        ]
    if not isinstance(phases, list) or not phases:
        raise ValueError("Legacy payload must include at least one phase.")

    canonical_phases: list[dict[str, Any]] = []
    for idx, phase in enumerate(phases):
        if not isinstance(phase, dict):
            raise ValueError(f"phase[{idx}] must be an object.")
        params = dict(phase.get("params", {}) or {})
        trials = int(params.get("n_trials", phase.get("trials", 1)))
        if trials <= 0:
            raise ValueError(f"phase[{idx}] trials must be > 0.")
        params["n_trials"] = trials
        canonical_phases.append(
            {
                "name": phase.get("name") or f"Phase {idx}",
                "protocol": phase.get("protocol"),
                "stimuli": deepcopy(phase.get("stimuli", {})),
                "params": params,
                "trials": trials,
            }
        )

    representation = exp.get("representation")
    if isinstance(representation, str):
        representation = {"name": representation, "params": {}}
    if not isinstance(representation, dict):
        raise ValueError("Legacy experiment.representation must be a string or object.")
    representation = deepcopy(representation)
    representation.setdefault("params", {})
    if not isinstance(representation["params"], dict):
        raise ValueError("representation.params must be an object.")
    if isinstance(exp.get("salience"), dict) and exp.get("salience"):
        representation["salience"] = deepcopy(exp["salience"])

    learning: dict[str, Any] = {
        "rule": exp.get("learner"),
        "params": {},
    }
    attention_initial = exp.get("attention", {})
    attention_config = exp.get("attention_config", {})
    if isinstance(attention_initial, dict) and attention_initial or isinstance(attention_config, dict) and attention_config:
        learning["attention"] = {
            "initial": deepcopy(attention_initial if isinstance(attention_initial, dict) else {}),
            "config": deepcopy(attention_config if isinstance(attention_config, dict) else {}),
        }

    runtime = deepcopy(exp.get("runtime", {})) if isinstance(exp.get("runtime"), dict) else {}
    if isinstance(exp.get("context_inference"), dict):
        runtime["context_inference"] = deepcopy(exp["context_inference"])

    return {
        "experiment": {
            "program": {"phases": canonical_phases},
            "agent": {
                "name": exp.get("agent"),
                "representation": representation,
                "learning": learning,
                "policy": deepcopy(exp.get("policy")),
            },
            "runtime": runtime,
        },
        "report": deepcopy(src.get("report", {})),
    }
