"""Get-time-series query and handler.

Retrieves bi-temporal time-series records for a given asset and data
source within a date range, returning only the latest version per
business date.
"""

from dataclasses import dataclass
from datetime import date

from shared.mediator.types import Query, QueryHandler
from timeseries_context.infrastructure.cassandra_ts_read_repo import CassandraTimeSeriesReadRepo


@dataclass(frozen=True)
class GetTimeSeriesQuery(Query):
    """Query for time-series data within a date range.

    Attributes
    ----------
    asset_id : str
        The asset identifier.
    data_source_id : str
        The data-source identifier.
    start_date / end_date : date
        Inclusive start / exclusive end of the business-date range.
    include_attributes : bool
        If ``True``, the response includes a sorted list of all value
        attribute names found in the result set.
    """

    asset_id: str
    data_source_id: str
    start_date: date
    end_date: date
    include_attributes: bool = False


class GetTimeSeriesHandler(QueryHandler[GetTimeSeriesQuery]):
    """Handles ``GetTimeSeriesQuery`` by reading from the time-series repo."""

    def __init__(self, read_repo: CassandraTimeSeriesReadRepo):
        self._read_repo = read_repo

    async def handle(self, query: GetTimeSeriesQuery) -> dict:
        """Return the latest time-series records per business date, newest first."""
        records = self._read_repo.find_latest_by_range(
            query.asset_id, query.data_source_id,
            query.start_date, query.end_date,
        )

        response_records = []
        all_attrs: set[str] = set()
        for r in records:
            merged_vals = {**r["values_double"], **r["values_int"], **r["values_text"]}
            all_attrs.update(merged_vals.keys())
            response_records.append({
                "businessDate": r["business_date"].isoformat(),
                "values": merged_vals,
            })

        result: dict = {
            "data": {
                "assetId": query.asset_id,
                "datasourceId": query.data_source_id,
                "records": response_records,
            }
        }

        if query.include_attributes:
            result["attributes"] = sorted(all_attrs)

        return result
