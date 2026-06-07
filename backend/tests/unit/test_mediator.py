"""Unit tests for CommandBus and QueryBus (mediator pattern)."""
import pytest
from unittest.mock import AsyncMock
from dataclasses import dataclass
from shared.mediator.command_bus import CommandBus
from shared.mediator.query_bus import QueryBus
from shared.mediator.types import Command, Query, CommandHandler, QueryHandler


# ── Fake command / query types used only by these tests ──────────────


@dataclass(frozen=True)
class FakeCommand(Command):
    value: str = "test"


@dataclass(frozen=True)
class AnotherCommand(Command):
    value: int = 42


@dataclass(frozen=True)
class FakeQuery(Query):
    term: str = ""


@dataclass(frozen=True)
class AnotherQuery(Query):
    count: int = 0


# ── CommandBus ───────────────────────────────────────────────────────


class TestCommandBus:
    @pytest.mark.asyncio
    async def test_register_and_dispatch_command(self):
        bus = CommandBus()
        handler = AsyncMock(spec=CommandHandler)
        handler.handle = AsyncMock(return_value=None)
        bus.register(FakeCommand, handler)

        cmd = FakeCommand(value="hello")
        await bus.dispatch(cmd)
        handler.handle.assert_called_once_with(cmd)

    @pytest.mark.asyncio
    async def test_dispatch_unknown_command_raises(self):
        bus = CommandBus()
        with pytest.raises(ValueError, match="No handler registered"):
            await bus.dispatch(FakeCommand())

    @pytest.mark.asyncio
    async def test_multiple_command_handlers(self):
        bus = CommandBus()
        handler_a = AsyncMock(spec=CommandHandler)
        handler_a.handle = AsyncMock(return_value="a")
        handler_b = AsyncMock(spec=CommandHandler)
        handler_b.handle = AsyncMock(return_value="b")

        bus.register(FakeCommand, handler_a)
        bus.register(AnotherCommand, handler_b)

        await bus.dispatch(FakeCommand(value="x"))
        await bus.dispatch(AnotherCommand(value=1))

        handler_a.handle.assert_called_once()
        handler_b.handle.assert_called_once()

    @pytest.mark.asyncio
    async def test_handler_return_value_propagated(self):
        bus = CommandBus()
        handler = AsyncMock(spec=CommandHandler)
        handler.handle = AsyncMock(return_value={"id": "abc", "status": "created"})
        bus.register(FakeCommand, handler)

        result = await bus.dispatch(FakeCommand())
        assert result == {"id": "abc", "status": "created"}


# ── QueryBus ─────────────────────────────────────────────────────────


class TestQueryBus:
    @pytest.mark.asyncio
    async def test_register_and_dispatch_query(self):
        bus = QueryBus()
        handler = AsyncMock(spec=QueryHandler)
        handler.handle = AsyncMock(return_value={"items": []})
        bus.register(FakeQuery, handler)

        query = FakeQuery(term="search")
        result = await bus.dispatch(query)

        handler.handle.assert_called_once_with(query)
        assert result == {"items": []}

    @pytest.mark.asyncio
    async def test_dispatch_unknown_query_raises(self):
        bus = QueryBus()
        with pytest.raises(ValueError, match="No handler registered"):
            await bus.dispatch(FakeQuery())
