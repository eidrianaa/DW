"""Cassandra read repository for time-series data.

Queries the ``data`` table partitioned by ``(asset_id, data_source_id,
business_date_year)`` and returns the latest version of each business
date within a given range.
"""

from datetime import date

from shared.database.cassandra_session import get_session


class CassandraTimeSeriesReadRepo:
    """Read-side repository for bi-temporal time-series records."""

    def __init__(self) -> None:
        self._session = get_session()
        self._stmt = self._session.prepare(
            """SELECT * FROM data
               WHERE asset_id = ? AND data_source_id = ? AND business_date_year = ?
               AND business_date >= ? AND business_date < ?"""
        )

    def find_latest_by_range(
        self,
        asset_id: str,
        data_source_id: str,
        start_date: date,
        end_date: date,
    ) -> list[dict]:
        """Return the newest version of each record in the date range.

        Parameters
        ----------
        asset_id:
            The asset to query.
        data_source_id:
            The data source to query.
        start_date:
            Inclusive lower bound of the business-date range.
        end_date:
            Exclusive upper bound of the business-date range.

        Returns
        -------
        list[dict]
            Records sorted by ``business_date`` descending, excluding
            soft-deleted rows.
        """
        all_rows = []
        for year in range(start_date.year, end_date.year + 1):
            rows = self._session.execute(self._stmt, [
                asset_id, data_source_id, year, start_date, end_date
            ])
            all_rows.extend(rows)

        # Keep latest system_date per business_date
        latest: dict[date, dict] = {}
        for row in all_rows:
            bd = row.business_date
            existing = latest.get(bd)
            if existing is None or row.system_date > existing["system_date"]:
                latest[bd] = {
                    "business_date": row.business_date,
                    "system_date": row.system_date,
                    "values_double": dict(row.values_double) if row.values_double else {},
                    "values_int": dict(row.values_int) if row.values_int else {},
                    "values_text": dict(row.values_text) if row.values_text else {},
                    "deleted": row.deleted or False,
                }

        # Filter deleted, sort newest first
        return sorted(
            [r for r in latest.values() if not r["deleted"]],
            key=lambda r: r["business_date"],
            reverse=True,
        )
