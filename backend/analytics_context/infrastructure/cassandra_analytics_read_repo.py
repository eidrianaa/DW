"""Cassandra read repository for analytics results.

Provides read access to the ``totals`` and ``regression_results`` tables
populated by PySpark jobs.
"""

from shared.database.cassandra_session import get_session


class CassandraAnalyticsReadRepo:
    """Read-side repository for aggregation totals and ML predictions."""

    def __init__(self) -> None:
        self._session = get_session()

    def get_totals(self, asset_id: str | None = None) -> list[dict]:
        """Return aggregation totals, optionally filtered by asset.

        Parameters
        ----------
        asset_id:
            If provided, only rows for this asset are returned.

        Returns
        -------
        list[dict]
            Each dict contains ``asset_id``, ``business_date_year``, and ``cnt``.
        """
        if asset_id:
            stmt = self._session.prepare(
                "SELECT * FROM totals WHERE asset_id = ?"
            )
            rows = self._session.execute(stmt, [asset_id])
        else:
            rows = self._session.execute("SELECT * FROM totals")

        return [
            {
                "asset_id": r.asset_id,
                "business_date_year": r.business_date_year,
                "cnt": r.cnt,
            }
            for r in rows
        ]

    def get_predictions(self) -> list[dict]:
        """Return all stored ML prediction results.

        Returns
        -------
        list[dict]
            Each dict contains ``seconds``, ``open``, and ``prediction``.
        """
        rows = self._session.execute("SELECT * FROM regression_results")
        return [
            {
                "seconds": r.seconds,
                "open": r.open,
                "prediction": r.prediction,
            }
            for r in rows
        ]

    def get_anomalies(self, asset_id: str | None = None) -> list[dict]:
        """Return detected anomalies, optionally filtered by asset.

        Returns
        -------
        list[dict]
            Each dict contains bdate, asset_id, close, z_score, and flags.
        """
        if asset_id:
            stmt = self._session.prepare(
                "SELECT * FROM anomalies WHERE asset_id = ?"
            )
            rows = self._session.execute(stmt, [asset_id])
        else:
            rows = self._session.execute("SELECT * FROM anomalies")
        return [
            {
                "business_date": str(r.bdate),
                "asset_id": r.asset_id,
                "close": r.close,
                "z_score": round(r.z_score, 4),
                "z_flag": r.z_flag,
                "bb_flag": r.bb_flag,
                "vol_flag": r.vol_flag,
            }
            for r in rows
        ]
