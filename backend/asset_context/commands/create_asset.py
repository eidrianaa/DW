"""Create-asset command and handler.

Persists a brand-new ``AssetAggregate`` and publishes an ``AssetCreated``
domain event.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from asset_context.domain.asset_aggregate import AssetAggregate
from asset_context.domain.events import AssetCreated
from asset_context.infrastructure.cassandra_asset_write_repo import CassandraAssetWriteRepo
from shared.events.event_bus import EventBus
from shared.mediator.types import Command, CommandHandler


@dataclass(frozen=True)
class CreateAssetCommand(Command):
    """Command to create a new financial asset."""

    asset_id: str
    name: str
    description: str
    attributes: dict[str, str] = field(default_factory=dict)


class CreateAssetHandler(CommandHandler[CreateAssetCommand]):
    """Handles ``CreateAssetCommand`` by persisting a new aggregate version."""

    def __init__(self, write_repo: CassandraAssetWriteRepo, event_bus: EventBus):
        self._write_repo = write_repo
        self._event_bus = event_bus

    async def handle(self, command: CreateAssetCommand) -> Any:
        """Create and persist the asset, then publish ``AssetCreated``."""
        aggregate = AssetAggregate(
            id=command.asset_id,
            system_date=datetime.now(UTC),
            name=command.name,
            description=command.description,
            attributes=command.attributes,
        )
        self._write_repo.save(aggregate)
        await self._event_bus.publish(AssetCreated(asset_id=command.asset_id))
        return aggregate
