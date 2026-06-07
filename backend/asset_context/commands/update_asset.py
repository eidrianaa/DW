from dataclasses import dataclass, field
from shared.mediator.types import Command, CommandHandler
from asset_context.infrastructure.cassandra_asset_read_repo import CassandraAssetReadRepo
from asset_context.infrastructure.cassandra_asset_write_repo import CassandraAssetWriteRepo
from shared.events.event_bus import EventBus
from asset_context.domain.events import AssetUpdated

@dataclass(frozen=True)
class UpdateAssetCommand(Command):
    asset_id: str
    name: str | None = None
    description: str | None = None
    attributes: dict[str, str] | None = None

class UpdateAssetHandler(CommandHandler[UpdateAssetCommand]):
    def __init__(self, read_repo: CassandraAssetReadRepo,
                 write_repo: CassandraAssetWriteRepo, event_bus: EventBus):
        self._read_repo = read_repo
        self._write_repo = write_repo
        self._event_bus = event_bus

    async def handle(self, command: UpdateAssetCommand):
        current = self._read_repo.find_latest(command.asset_id)
        if current is None:
            raise ValueError(f"Asset '{command.asset_id}' not found")
        if current.is_deleted:
            raise ValueError(f"Asset '{command.asset_id}' has been deleted")

        updated = current.update(
            name=command.name,
            description=command.description,
            attributes=command.attributes,
        )
        self._write_repo.save(updated)
        await self._event_bus.publish(AssetUpdated(asset_id=command.asset_id))
        return updated
