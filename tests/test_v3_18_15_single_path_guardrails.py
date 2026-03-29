from __future__ import annotations

import re
from pathlib import Path

from virtual_shaping_lab.vsl.agent.learning import (
    executable_learner_preset_names,
    learner_preset_hash,
    learner_registry_hash,
)


ROOT = Path(__file__).resolve().parents[1]

_RUNTIME_SURFACE_FILES = [
    ROOT / "virtual_shaping_lab" / "vsl" / "runtime" / "learner_adapter.py",
    ROOT / "virtual_shaping_lab" / "vsl" / "rollout" / "harness.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "runner.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "trial_executor.py",
    ROOT / "virtual_shaping_lab" / "experiment" / "phases" / "learning_helpers.py",
]

_BANNED_RUNTIME_IMPORT_TOKENS = [
    "experiment.factories.learner_factory",
    "virtual_shaping_lab.agents.learners.rescorla_wagner",
    "virtual_shaping_lab.agents.learners.td_value",
    "virtual_shaping_lab.agents.learners.q_learner",
]


def test_v3_18_15_runtime_surfaces_do_not_import_legacy_learner_execution_paths():
    violations: list[tuple[str, str]] = []
    for path in _RUNTIME_SURFACE_FILES:
        text = path.read_text(encoding="utf-8")
        import_lines = [
            line.strip()
            for line in text.splitlines()
            if re.match(r"^(from|import)\s+", line.strip())
        ]
        for token in _BANNED_RUNTIME_IMPORT_TOKENS:
            if any(token in line for line in import_lines):
                violations.append((str(path.relative_to(ROOT)), token))
    assert not violations, f"Legacy learner import tokens found in runtime surfaces: {violations}"


def test_v3_18_15_learning_helper_keeps_single_transition_dispatch_path():
    text = (
        ROOT
        / "virtual_shaping_lab"
        / "experiment"
        / "phases"
        / "learning_helpers.py"
    ).read_text(encoding="utf-8")
    assert "hasattr(agent, \"update\")" not in text
    assert "update(state, reward, action)" not in text
    assert "agent.learn(transition)" in text


def test_v3_18_15_canonical_learner_contract_snapshots_are_stable():
    assert executable_learner_preset_names() == [
        "rescorla_wagner",
        "td0",
        "pearce_hall_rw",
        "mackintosh_rw",
        "td_lambda",
    ]
    registry_hashes = [learner_registry_hash() for _ in range(10)]
    preset_hashes = [learner_preset_hash("rescorla_wagner") for _ in range(10)]
    assert len(set(registry_hashes)) == 1
    assert len(set(preset_hashes)) == 1
    assert isinstance(registry_hashes[0], str) and len(registry_hashes[0]) == 64
    assert isinstance(preset_hashes[0], str) and len(preset_hashes[0]) == 64
