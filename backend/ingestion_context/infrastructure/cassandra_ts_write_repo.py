"""Cassandra write repository for time-series data.

Handles append-only inserts into the ``data`` table, supporting both
single-record saves and chunked batch inserts.
"""

import logging

from cassandra.query import BatchStatement, BatchType

from ingestion_context.infrastructure.record_transformer import CanonicalRecord
from shared.config.settings import get_settings
from shared.database.cassandra_session import get_session

logger = logging.getLogger(__name__)


class CassandraTimeSeriesWriteRepo:
    """Write-side repository for canonical time-series records."""

    def __init__(self) -> None:
        self._session = get_session()
        self._stmt = self._session.prepare(
            """INSERT INTO data (asset_id, data_source_id, business_date_year,
               business_date, system_date, values_double, values_int, values_text, deleted)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        )

    def save(self, record: CanonicalRecord) -> None:
        """Persist a single canonical record."""
        self._session.execute(self._stmt, [
            record.asset_id, record.data_source_id, record.business_date_year,
            record.business_date, record.system_date,
            record.values_double, record.values_int, record.values_text, record.deleted,
        ])

    def save_batch(self, records: list[CanonicalRecord]) -> int:
        """Persist a list of records in chunked unlogged batches.

        Batch size is controlled by ``Settings.max_batch_size`` to avoid
        overwhelming Cassandra with oversized batch mutations.

        Returns
        -------
        int
            The total number of records persisted.
        """
        if not records:
            return 0

        batch_size = get_settings().max_batch_size
        total = 0
        for i in range(0, len(records), batch_size):
            chunk = records[i : i + batch_size]
            batch = BatchStatement(batch_type=BatchType.UNLOGGED)
            for r in chunk:
                batch.add(self._stmt, [
                    r.asset_id, r.data_source_id, r.business_date_year,
                    r.business_date, r.system_date,
                    r.values_double, r.values_int, r.values_text, r.deleted,
                ])
            self._session.execute(batch)
            total += len(chunk)
            logger.debug("Saved batch chunk of %d records (%d/%d)", len(chunk), total, len(records))

        logger.info("Saved %d time-series records in total", total)
        return total
