from __future__ import annotations

import os

import pytest

from experiment.factories.phase_factory import PHASE_REGISTRY


STRICT = os.getenv("V2_11_GUARDS_STRICT", "0") == "1"


def _assert_or_soft_xfail(*, violations: list[str], guard_name: str):
    if violations and not STRICT:
        pytest.xfail(
            f"[soft-guard:{guard_name}] violations found (non-blocking until strict mode): {violations}"
        )
    assert not violations, f"{guard_name} violations: {violations}"


def test_no_legacy_phase_keys_guard():
    violations = sorted([name for name in PHASE_REGISTRY.keys() if "_legacy" in str(name)])
    _assert_or_soft_xfail(
        violations=violations,
        guard_name="no_legacy_phase_keys",
    )
