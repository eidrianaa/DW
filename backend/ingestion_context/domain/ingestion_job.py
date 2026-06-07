"""Ingestion job aggregate.

Tracks the lifecycle of a single ingestion run (pending -> running ->
completed / failed) within the ingestion bounded context.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class IngestionStatus(Enum):
    """Possible states for an ingestion job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class IngestionJob:
    """Mutable aggregate representing an in-progress ingestion run.

    Attributes
    ----------
    id : str
        Unique job identifier.
    provider : str
        Data provider key (e.g. ``YFINANCE``).
    dataset_codes : list[str]
        Ticker symbols being ingested.
    status : IngestionStatus
        Current lifecycle state.
    started_at / completed_at : datetime | None
        Timestamps for status transitions.
    stats : dict[str, int]
        Counters for fetched / stored / errors.
    """

    id: str
    provider: str
    dataset_codes: list[str]
    status: IngestionStatus = IngestionStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    stats: dict[str, int] = field(default_factory=dict)

    def start(self) -> "IngestionJob":
        """Transition to the RUNNING state."""
        self.status = IngestionStatus.RUNNING
        self.started_at = datetime.now(UTC)
        return self

    def complete(self, stats: dict[str, int]) -> "IngestionJob":
        """Transition to the COMPLETED state with final statistics."""
        self.status = IngestionStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self.stats = stats
        return self

    def fail(self, error: str) -> "IngestionJob":
        """Transition to the FAILED state with an error message."""
        self.status = IngestionStatus.FAILED
        self.completed_at = datetime.now(UTC)
        self.stats["error"] = error
        return self
