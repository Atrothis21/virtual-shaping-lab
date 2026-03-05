"""Public phase construction facade.

Runtime and protocol code should import phase construction from this module
instead of importing factory internals directly.
"""

from __future__ import annotations

from typing import Any

from experiment.factories.phase_factory import build_phase as _build_phase


def build_phase(name: str, *, agent: Any, stimuli: Any = None, **phase_params):
    return _build_phase(name, agent=agent, stimuli=stimuli, **phase_params)

