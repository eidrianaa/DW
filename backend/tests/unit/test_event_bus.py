"""Unit tests for EventBus with subscriber isolation."""
import pytest
from unittest.mock import AsyncMock
from dataclasses import dataclass
from shared.events.event_bus import EventBus
from shared.events.domain_event import DomainEvent


# ── Fake domain events used only by these tests ─────────────────────


@dataclass(frozen=True)
class EventA(DomainEvent):
    payload: str = ""


@dataclass(frozen=True)
class EventB(DomainEvent):
    payload: str = ""


# ── Tests ────────────────────────────────────────────────────────────


class TestEventBus:
    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe(EventA, handler)

        event = EventA(payload="hello")
        await bus.publish(event)

        handler.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        bus = EventBus()
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        bus.subscribe(EventA, handler1)
        bus.subscribe(EventA, handler2)

        event = EventA(payload="multi")
        await bus.publish(event)

        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_no_subscribers_no_error(self):
        bus = EventBus()
        # Should not raise even though nobody is listening
        await bus.publish(EventA(payload="nobody listening"))

    @pytest.mark.asyncio
    async def test_different_event_types(self):
        bus = EventBus()
        handler_a = AsyncMock()
        handler_b = AsyncMock()
        bus.subscribe(EventA, handler_a)
        bus.subscribe(EventB, handler_b)

        await bus.publish(EventA(payload="only A"))

        handler_a.assert_called_once()
        handler_b.assert_not_called()

    @pytest.mark.asyncio
    async def test_subscriber_error_isolation(self):
        """One failing subscriber must not prevent the remaining ones from running.

        This validates the error-isolation fix added to EventBus.publish().
        """
        bus = EventBus()
        failing_handler = AsyncMock(side_effect=RuntimeError("boom"))
        surviving_handler = AsyncMock()

        bus.subscribe(EventA, failing_handler)
        bus.subscribe(EventA, surviving_handler)

        # publish should NOT propagate the RuntimeError
        await bus.publish(EventA(payload="test"))

        failing_handler.assert_called_once()
        surviving_handler.assert_called_once()
