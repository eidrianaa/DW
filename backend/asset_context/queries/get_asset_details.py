from dataclasses import dataclass
from shared.mediator.types import Query, QueryHandler
from asset_context.infrastructure.cassandra_asset_read_repo import CassandraAssetReadRepo

@dataclass(frozen=True)
class GetAssetDetailsQuery(Query):
    asset_id: str

class GetAssetDetailsHandler(QueryHandler[GetAssetDetailsQuery]):
    def __init__(self, read_repo: CassandraAssetReadRepo):
        self._read_repo = read_repo

    async def handle(self, query: GetAssetDetailsQuery) -> list[dict]:
        versions = self._read_repo.find_all_versions(query.asset_id)
        return [
            {
                "id": v.id,
                "system_time": v.system_date.isoformat(),
                "name": v.name,
                "description": v.description,
                "attributes": v.attributes,
            }
            for v in versions
        ]
