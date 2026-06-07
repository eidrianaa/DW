from shared.database.cassandra_session import get_session
from datasource_context.domain.data_source_aggregate import DataSourceAggregate

class CassandraDataSourceWriteRepo:
    def __init__(self):
        self._session = get_session()
        self._stmt = self._session.prepare(
            "INSERT INTO data_source (id, system_date, name, description, attributes) "
            "VALUES (?, ?, ?, ?, ?)"
        )

    def save(self, aggregate: DataSourceAggregate) -> None:
        self._session.execute(self._stmt, [
            aggregate.id, aggregate.system_date, aggregate.name,
            aggregate.description, aggregate.attributes,
        ])
