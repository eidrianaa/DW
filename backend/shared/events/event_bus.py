"""In-memory domain event bus.

Provides a simple publish/subscribe mechanism so that bounded contexts
can react to domain events without direct coupling.
"""

import logging
from collections import defaultdict
from typing import Awaitable, Callable

from shared.events.domain_event import DomainEvent

logger = logging.getLogger(__name__)

# Type alias for subscriber callables.
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """Lightweight async event bus with per-handler error isolation.

    Each subscriber is invoked independently; a failure in one handler
    does not prevent the remaining handlers from executing.
    """

    def __init__(self) -> None:
        self._subscribers: dict[type, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        """Register *handler* for the given *event_type*.

        Parameters
        ----------
        event_type:
            The concrete ``DomainEvent`` subclass to subscribe to.
        handler:
            An async callable that accepts a ``DomainEvent`` instance.
        """
        self._subscribers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publish *event* to all registered subscribers.

        Each handler is called in order.  If a handler raises an exception
        it is logged and the remaining handlers still execute.

        Parameters
        ----------
        event:
            The domain event to broadcast.
        """
        event_name = type(event).__name__
        handlers = self._subscribers.get(type(event), [])
        logger.debug("Publishing %s to %d subscriber(s)", event_name, len(handlers))
        for handler in handlers:
            try:
                await handler(event)
            except Exception:
                logger.exception(
                    "Handler %s failed while processing %s",
                    getattr(handler, "__name__", repr(handler)),
                    event_name,
                )
