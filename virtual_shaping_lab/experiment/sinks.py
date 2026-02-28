"""Record sink implementations for experiment runtime."""

from __future__ import annotations

from typing import List

from experiment.domain.interfaces import IRecordSink
from experiment.domain.types import TrialRecord


class InMemorySink(IRecordSink):
    """Collect records in memory for downstream analysis/reporting."""

    def __init__(self):
        self.records: List[TrialRecord] = []
        self.closed: bool = False

    def emit(self, record: TrialRecord) -> None:
        self.records.append(record)

    def close(self) -> None:
        self.closed = True

