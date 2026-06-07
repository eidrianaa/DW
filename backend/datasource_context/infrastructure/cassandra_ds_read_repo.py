from shared.database.cassandra_session import get_session
from datasource_context.domain.data_source_aggregate import DataSourceAggregate

class CassandraDataSourceReadRepo:
    def __init__(self):
        self._session = get_session()
        self._stmt_latest = self._session.prepare(
            "SELECT * FROM data_source WHERE id = ? LIMIT 1"
        )
        self._stmt_all = self._session.prepare(
            "SELECT * FROM data_source WHERE id = ?"
        )

    def find_latest(self, data_source_id: str) -> DataSourceAggregate | None:
        row = self._session.execute(self._stmt_latest, [data_source_id]).one()
        return self._to_aggregate(row) if row else None

    def find_all_versions(self, data_source_id: str) -> list[DataSourceAggregate]:
        rows = self._session.execute(self._stmt_all, [data_source_id])
        return [self._to_aggregate(r) for r in rows]

    def find_all_ids(self, offset: int = 0, limit: int = 20) -> tuple[list[str], int]:
        rows = list(self._session.execute("SELECT DISTINCT id FROM data_source"))
        all_ids = sorted(r.id for r in rows)
        total = len(all_ids)
        return all_ids[offset:offset + limit], total

    def _to_aggregate(self, row) -> DataSourceAggregate:
        return DataSourceAggregate(
            id=row.id, system_date=row.system_date,
            name=row.name or "", description=row.description or "",
            attributes=set(row.attributes) if row.attributes else set(),
        )
