"""Ingestion domain events.

Events emitted during the ingestion lifecycle to decouple the ingestion
context from downstream consumers (e.g. analytics).
"""

from dataclasses import dataclass, field

from shared.events.domain_event import DomainEvent


@dataclass(frozen=True)
class IngestionStarted(DomainEvent):
    """Raised when an ingestion job begins."""

    provider: str = ""
    datasets: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IngestionCompleted(DomainEvent):
    """Raised when an ingestion job finishes successfully."""

    provider: str = ""
    datasets: list[str] = field(default_factory=list)
    total_stored: int = 0
