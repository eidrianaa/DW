from shared.database.cassandra_session import get_session
from asset_context.domain.asset_aggregate import AssetAggregate

class CassandraAssetWriteRepo:
    def __init__(self):
        self._session = get_session()
        self._stmt = self._session.prepare(
            "INSERT INTO asset (id, system_date, name, description, attributes) "
            "VALUES (?, ?, ?, ?, ?)"
        )

    def save(self, aggregate: AssetAggregate) -> None:
        self._session.execute(self._stmt, [
            aggregate.id, aggregate.system_date, aggregate.name,
            aggregate.description, aggregate.attributes,
        ])
