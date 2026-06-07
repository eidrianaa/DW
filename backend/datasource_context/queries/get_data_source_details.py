from dataclasses import dataclass
from shared.mediator.types import Query, QueryHandler
from datasource_context.infrastructure.cassandra_ds_read_repo import CassandraDataSourceReadRepo

@dataclass(frozen=True)
class GetDataSourceDetailsQuery(Query):
    data_source_id: str

class GetDataSourceDetailsHandler(QueryHandler[GetDataSourceDetailsQuery]):
    def __init__(self, read_repo: CassandraDataSourceReadRepo):
        self._read_repo = read_repo

    async def handle(self, query: GetDataSourceDetailsQuery) -> list[dict]:
        versions = self._read_repo.find_all_versions(query.data_source_id)
        return [
            {
                "id": v.id,
                "system_time": v.system_date.isoformat(),
                "name": v.name,
                "description": v.description,
                "attributes": sorted(v.attributes),
            }
            for v in versions
        ]
