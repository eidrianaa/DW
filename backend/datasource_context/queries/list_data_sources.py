from dataclasses import dataclass
from shared.mediator.types import Query, QueryHandler
from datasource_context.infrastructure.cassandra_ds_read_repo import CassandraDataSourceReadRepo

@dataclass(frozen=True)
class ListDataSourcesQuery(Query):
    offset: int = 0
    limit: int = 20

class ListDataSourcesHandler(QueryHandler[ListDataSourcesQuery]):
    def __init__(self, read_repo: CassandraDataSourceReadRepo):
        self._read_repo = read_repo

    async def handle(self, query: ListDataSourcesQuery) -> dict:
        ids, total = self._read_repo.find_all_ids(query.offset, query.limit)
        return {
            "items": ids,
            "offset": query.offset,
            "limit": query.limit,
            "total": total,
            "has_next": query.offset + query.limit < total,
        }
