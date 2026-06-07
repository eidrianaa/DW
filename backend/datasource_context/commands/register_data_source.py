from dataclasses import dataclass, field
from shared.mediator.types import Command, CommandHandler
from datasource_context.domain.data_source_aggregate import DataSourceAggregate
from datasource_context.infrastructure.cassandra_ds_write_repo import CassandraDataSourceWriteRepo
from datetime import datetime

@dataclass(frozen=True)
class RegisterDataSourceCommand(Command):
    data_source_id: str
    name: str
    description: str
    attributes: frozenset[str] = frozenset()

class RegisterDataSourceHandler(CommandHandler[RegisterDataSourceCommand]):
    def __init__(self, write_repo: CassandraDataSourceWriteRepo):
        self._write_repo = write_repo

    async def handle(self, command: RegisterDataSourceCommand):
        aggregate = DataSourceAggregate(
            id=command.data_source_id,
            system_date=datetime.utcnow(),
            name=command.name,
            description=command.description,
            attributes=set(command.attributes),
        )
        self._write_repo.save(aggregate)
        return aggregate
