"""Query bus for the CQRS read side.

Routes ``Query`` instances to their registered ``QueryHandler``
and returns the handler's result.
"""

import logging
from typing import Any

from shared.mediator.types import Query, QueryHandler

logger = logging.getLogger(__name__)


class QueryBus:
    """Dispatches queries to the single handler registered for each query type."""

    def __init__(self) -> None:
        self._handlers: dict[type, QueryHandler] = {}

    def register(self, query_type: type, handler: QueryHandler) -> None:
        """Register a handler for the given query type.

        Parameters
        ----------
        query_type:
            The concrete ``Query`` subclass.
        handler:
            The ``QueryHandler`` instance that will process queries of that type.
        """
        self._handlers[query_type] = handler

    async def dispatch(self, query: Query) -> Any:
        """Dispatch a query to its registered handler.

        Parameters
        ----------
        query:
            The query instance to dispatch.

        Returns
        -------
        Any
            The value returned by the handler.

        Raises
        ------
        ValueError
            If no handler has been registered for the query's type.
        """
        handler = self._handlers.get(type(query))
        if handler is None:
            raise ValueError(f"No handler registered for {type(query).__name__}")
        logger.debug("Dispatching query %s", type(query).__name__)
        return await handler.handle(query)
