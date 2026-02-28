"""Record sink implementations for experiment runtime."""

from __future__ import annotations

import json
from pathlib import Path
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


class JsonlSink(IRecordSink):
    """Append-only JSONL sink for durable long-running experiment output."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a", encoding="utf-8")
        self.closed: bool = False

    def emit(self, record: TrialRecord) -> None:
        json.dump(record, self._fh, ensure_ascii=True, separators=(",", ":"))
        self._fh.write("\n")
        self._fh.flush()

    def close(self) -> None:
        if not self.closed:
            self._fh.close()
            self.closed = True


class CompositeSink(IRecordSink):
    """Fan-out sink that writes each record to multiple sinks."""

    def __init__(self, sinks: list[IRecordSink]):
        if not sinks:
            raise ValueError("CompositeSink requires at least one child sink.")
        self.sinks = list(sinks)
        self.closed: bool = False

    def emit(self, record: TrialRecord) -> None:
        for sink in self.sinks:
            sink.emit(record)

    def close(self) -> None:
        if self.closed:
            return
        for sink in self.sinks:
            sink.close()
        self.closed = True

