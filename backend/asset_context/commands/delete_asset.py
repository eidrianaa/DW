from dataclasses import dataclass
from shared.mediator.types import Command, CommandHandler
from asset_context.infrastructure.cassandra_asset_read_repo import CassandraAssetReadRepo
from asset_context.infrastructure.cassandra_asset_write_repo import CassandraAssetWriteRepo
from shared.events.event_bus import EventBus
from asset_context.domain.events import AssetDeleted

@dataclass(frozen=True)
class DeleteAssetCommand(Command):
    asset_id: str

class DeleteAssetHandler(CommandHandler[DeleteAssetCommand]):
    def __init__(self, read_repo: CassandraAssetReadRepo,
                 write_repo: CassandraAssetWriteRepo, event_bus: EventBus):
        self._read_repo = read_repo
        self._write_repo = write_repo
        self._event_bus = event_bus

    async def handle(self, command: DeleteAssetCommand):
        current = self._read_repo.find_latest(command.asset_id)
        if current is None:
            raise ValueError(f"Asset '{command.asset_id}' not found")
        if current.is_deleted:
            raise ValueError(f"Asset '{command.asset_id}' is already deleted")

        deleted = current.mark_deleted()
        self._write_repo.save(deleted)
        await self._event_bus.publish(AssetDeleted(asset_id=command.asset_id))
        return deleted
