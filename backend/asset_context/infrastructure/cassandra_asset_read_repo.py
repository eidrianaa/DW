from shared.database.cassandra_session import get_session
from asset_context.domain.asset_aggregate import AssetAggregate

class CassandraAssetReadRepo:
    def __init__(self):
        self._session = get_session()
        self._stmt_latest = self._session.prepare(
            "SELECT * FROM asset WHERE id = ? LIMIT 1"
        )
        self._stmt_all = self._session.prepare(
            "SELECT * FROM asset WHERE id = ?"
        )

    def find_latest(self, asset_id: str) -> AssetAggregate | None:
        row = self._session.execute(self._stmt_latest, [asset_id]).one()
        return self._to_aggregate(row) if row else None

    def find_all_versions(self, asset_id: str) -> list[AssetAggregate]:
        rows = self._session.execute(self._stmt_all, [asset_id])
        return [self._to_aggregate(r) for r in rows]

    def find_all_ids(self, offset: int = 0, limit: int = 20) -> tuple[list[str], int]:
        rows = list(self._session.execute("SELECT DISTINCT id FROM asset"))
        all_ids = sorted(r.id for r in rows)
        total = len(all_ids)
        return all_ids[offset:offset + limit], total

    def _to_aggregate(self, row) -> AssetAggregate:
        return AssetAggregate(
            id=row.id, system_date=row.system_date,
            name=row.name or "", description=row.description or "",
            attributes=dict(row.attributes) if row.attributes else {},
        )
