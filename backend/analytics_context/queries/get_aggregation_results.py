"""Get-aggregation-results query and handler.

Returns stored aggregation totals (per-asset, per-year record counts)
from the ``totals`` table.
"""

from dataclasses import dataclass

from analytics_context.infrastructure.cassandra_analytics_read_repo import CassandraAnalyticsReadRepo
from shared.mediator.types import Query, QueryHandler


@dataclass(frozen=True)
class GetAggregationResultsQuery(Query):
    """Query for aggregation totals.

    Attributes
    ----------
    asset_id : str | None
        If set, only totals for this asset are returned.
    """

    asset_id: str | None = None


class GetAggregationResultsHandler(QueryHandler[GetAggregationResultsQuery]):
    """Handles ``GetAggregationResultsQuery`` by reading from the analytics repo."""

    def __init__(self, read_repo: CassandraAnalyticsReadRepo):
        self._read_repo = read_repo

    async def handle(self, query: GetAggregationResultsQuery) -> dict:
        """Return aggregation totals as a dict with a ``totals`` list."""
        rows = self._read_repo.get_totals(query.asset_id)
        return {
            "totals": [
                {
                    "asset_id": r["asset_id"],
                    "business_date_year": r["business_date_year"],
                    "count": r["cnt"],
                }
                for r in rows
            ]
        }
