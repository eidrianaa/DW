"""Get-anomaly-results query and handler."""

from dataclasses import dataclass
from analytics_context.infrastructure.cassandra_analytics_read_repo import CassandraAnalyticsReadRepo
from shared.mediator.types import Query, QueryHandler


@dataclass(frozen=True)
class GetAnomalyResultsQuery(Query):
    """Query to retrieve detected anomalies, optionally filtered by asset."""
    asset_id: str | None = None


class GetAnomalyResultsHandler(QueryHandler[GetAnomalyResultsQuery]):
    """Reads anomaly results from Cassandra."""

    def __init__(self, read_repo: CassandraAnalyticsReadRepo):
        self._read_repo = read_repo

    async def handle(self, query: GetAnomalyResultsQuery) -> dict:
        """Return anomalies as a dict with an ``anomalies`` list."""
        rows = self._read_repo.get_anomalies(query.asset_id)
        return {"anomalies": rows}
