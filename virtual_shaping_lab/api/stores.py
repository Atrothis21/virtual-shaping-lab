"""Run status store contracts and default in-memory implementation."""

from __future__ import annotations

from typing import Any, Dict, Optional, Protocol


class RunStatusStoreProtocol(Protocol):
    def set(
        self,
        run_id: str,
        *,
        state: str,
        artifacts: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
    ) -> None:
        ...

    def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        ...

    def clear(self, run_id: Optional[str] = None) -> None:
        ...


class InMemoryRunStatusStore:
    """Default in-process run status store."""

    def __init__(self):
        self._runs: Dict[str, Dict[str, Any]] = {}

    def set(
        self,
        run_id: str,
        *,
        state: str,
        artifacts: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._runs[run_id] = {
            "state": state,
            "artifacts": artifacts or {},
            "metadata": metadata or {},
            "error": error,
        }

    def get(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._runs.get(run_id)

    def clear(self, run_id: Optional[str] = None) -> None:
        if run_id is None:
            self._runs.clear()
            return
        self._runs.pop(run_id, None)

