"""Base domain event class.

All domain events in every bounded context inherit from ``DomainEvent``.
Each instance carries a unique ``event_id`` and an ``occurred_at``
timestamp set at creation time.
"""

from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
    """Immutable base class for domain events.

    Attributes
    ----------
    event_id : str
        A UUID-4 string uniquely identifying the event.
    occurred_at : datetime
        UTC timestamp of when the event was created.
    """

    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
