"""Record transformer for the ingestion pipeline.

Converts raw dictionaries (as returned by extractors) into
``CanonicalRecord`` dataclass instances suitable for Cassandra persistence.
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, date, datetime

logger = logging.getLogger(__name__)


@dataclass
class CanonicalRecord:
    """A normalised time-series record ready for Cassandra insertion.

    Numeric values are split into ``values_double`` and ``values_int``
    maps; everything else goes into ``values_text``.
    """

    asset_id: str
    data_source_id: str
    business_date_year: int
    business_date: date
    system_date: datetime
    values_double: dict[str, float] = field(default_factory=dict)
    values_int: dict[str, int] = field(default_factory=dict)
    values_text: dict[str, str] = field(default_factory=dict)
    deleted: bool = False


class RecordTransformer:
    """Transforms raw provider records into ``CanonicalRecord`` instances."""

    def transform(
        self,
        raw_records: list[dict],
        columns: list[str],
        asset_id: str,
        provider: str,
    ) -> list[CanonicalRecord]:
        """Transform a batch of raw records.

        Records that cannot be parsed (e.g. missing date) are logged and
        skipped rather than raising an exception.

        Returns
        -------
        list[CanonicalRecord]
            Successfully transformed records.
        """
        results: list[CanonicalRecord] = []
        for idx, raw in enumerate(raw_records):
            try:
                bdate = date.fromisoformat(
                    str(raw.get("date", raw.get("Date", "")))
                )
                vals_d: dict[str, float] = {}
                vals_t: dict[str, str] = {}
                for col in columns:
                    if col.lower() == "date":
                        continue
                    val = raw.get(col)
                    if val is None:
                        continue
                    try:
                        vals_d[col] = float(val)
                    except (ValueError, TypeError):
                        vals_t[col] = str(val)

                results.append(CanonicalRecord(
                    asset_id=asset_id,
                    data_source_id=provider,
                    business_date_year=bdate.year,
                    business_date=bdate,
                    system_date=datetime.now(UTC),
                    values_double=vals_d,
                    values_text=vals_t,
                ))
            except Exception:
                logger.warning(
                    "Skipping record %d for %s: failed to parse", idx, asset_id,
                    exc_info=True,
                )
                continue
        return results
