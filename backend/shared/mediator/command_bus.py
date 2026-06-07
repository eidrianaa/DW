"""Command bus for the CQRS write side.

Routes ``Command`` instances to their registered ``CommandHandler``
and returns the handler's result.
"""

import logging
from typing import Any

from shared.mediator.types import Command, CommandHandler

logger = logging.getLogger(__name__)


class CommandBus:
    """Dispatches commands to the single handler registered for each command type."""

    def __init__(self) -> None:
        self._handlers: dict[type, CommandHandler] = {}

    def register(self, command_type: type, handler: CommandHandler) -> None:
        """Register a handler for the given command type.

        Parameters
        ----------
        command_type:
            The concrete ``Command`` subclass.
        handler:
            The ``CommandHandler`` instance that will process commands of that type.
        """
        self._handlers[command_type] = handler

    async def dispatch(self, command: Command) -> Any:
        """Dispatch a command to its registered handler.

        Parameters
        ----------
        command:
            The command instance to dispatch.

        Returns
        -------
        Any
            The value returned by the handler.

        Raises
        ------
        ValueError
            If no handler has been registered for the command's type.
        """
        handler = self._handlers.get(type(command))
        if handler is None:
            raise ValueError(f"No handler registered for {type(command).__name__}")
        logger.debug("Dispatching command %s", type(command).__name__)
        return await handler.handle(command)
