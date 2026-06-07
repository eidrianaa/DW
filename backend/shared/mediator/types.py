"""CQRS mediator base types.

Defines the abstract base classes for commands, queries, and their
corresponding handlers used throughout the application's CQRS pipeline.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Command:
    """Base class for all commands (write operations).

    Commands represent an intent to change the system state.  Every
    concrete command should inherit from this class and be frozen
    (immutable) to guarantee safety when passed through the bus.
    """


@dataclass(frozen=True)
class Query:
    """Base class for all queries (read operations).

    Queries represent a request to retrieve data without side-effects.
    Every concrete query should inherit from this class.
    """


class CommandHandler(ABC, Generic[T]):
    """Abstract handler that processes a single command type."""

    @abstractmethod
    async def handle(self, command: T) -> Any:
        """Execute the command and return a result."""
        ...


class QueryHandler(ABC, Generic[T]):
    """Abstract handler that processes a single query type."""

    @abstractmethod
    async def handle(self, query: T) -> Any:
        """Execute the query and return a result."""
        ...
