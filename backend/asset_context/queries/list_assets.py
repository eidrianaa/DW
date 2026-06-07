from dataclasses import dataclass
from shared.mediator.types import Query, QueryHandler
from asset_context.infrastructure.cassandra_asset_read_repo import CassandraAssetReadRepo

@dataclass(frozen=True)
class ListAssetsQuery(Query):
    offset: int = 0
    limit: int = 20

class ListAssetsHandler(QueryHandler[ListAssetsQuery]):
    def __init__(self, read_repo: CassandraAssetReadRepo):
        self._read_repo = read_repo

    async def handle(self, query: ListAssetsQuery) -> dict:
        ids, total = self._read_repo.find_all_ids(query.offset, query.limit)
        return {
            "items": ids,
            "offset": query.offset,
            "limit": query.limit,
            "total": total,
            "has_next": query.offset + query.limit < total,
        }
