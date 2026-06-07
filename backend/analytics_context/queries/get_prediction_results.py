"""Get-prediction-results query and handler.

Returns stored ML regression predictions from the ``regression_results``
table.
"""

from dataclasses import dataclass

from analytics_context.infrastructure.cassandra_analytics_read_repo import CassandraAnalyticsReadRepo
from shared.mediator.types import Query, QueryHandler


@dataclass(frozen=True)
class GetPredictionResultsQuery(Query):
    """Query to retrieve all stored ML prediction results."""

    pass


class GetPredictionResultsHandler(QueryHandler[GetPredictionResultsQuery]):
    """Handles ``GetPredictionResultsQuery`` by reading from the analytics repo."""

    def __init__(self, read_repo: CassandraAnalyticsReadRepo):
        self._read_repo = read_repo

    async def handle(self, query: GetPredictionResultsQuery) -> dict:
        """Return predictions as a dict with a ``predictions`` list."""
        rows = self._read_repo.get_predictions()
        return {
            "predictions": [
                {
                    "seconds": r["seconds"],
                    "actual_open": r["open"],
                    "predicted_open": r["prediction"],
                }
                for r in rows
            ]
        }
