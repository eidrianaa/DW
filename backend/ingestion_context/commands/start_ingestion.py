"""Start-ingestion command and handler.

Orchestrates the full ingestion pipeline: fetch data from the configured
extractor, auto-create missing asset / data-source records, transform raw
rows into canonical records, and persist them in Cassandra.
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

from asset_context.domain.asset_aggregate import AssetAggregate
from asset_context.infrastructure.cassandra_asset_read_repo import CassandraAssetReadRepo
from asset_context.infrastructure.cassandra_asset_write_repo import CassandraAssetWriteRepo
from datasource_context.domain.data_source_aggregate import DataSourceAggregate
from datasource_context.infrastructure.cassandra_ds_read_repo import CassandraDataSourceReadRepo
from datasource_context.infrastructure.cassandra_ds_write_repo import CassandraDataSourceWriteRepo
from ingestion_context.domain.events import IngestionCompleted
from ingestion_context.infrastructure.cassandra_ts_write_repo import CassandraTimeSeriesWriteRepo
from ingestion_context.infrastructure.record_transformer import RecordTransformer
from ingestion_context.infrastructure.yfinance_extractor import YFinanceExtractor
from shared.events.event_bus import EventBus
from shared.mediator.types import Command, CommandHandler

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StartIngestionCommand(Command):
    """Command to ingest financial time-series data for a list of tickers."""

    provider: str = "YFINANCE"
    dataset_codes: list[str] = field(default_factory=list)
    start_date: str | None = None  # YYYY-MM-DD or None
    end_date: str | None = None  # YYYY-MM-DD or None
    period: str | None = None  # yfinance period, e.g. "1y", "5y", "max"


class StartIngestionHandler(CommandHandler[StartIngestionCommand]):
    """Handles ``StartIngestionCommand`` by running the full ETL pipeline."""

    def __init__(
        self,
        extractor: YFinanceExtractor,
        transformer: RecordTransformer,
        ts_write_repo: CassandraTimeSeriesWriteRepo,
        asset_write_repo: CassandraAssetWriteRepo,
        asset_read_repo: CassandraAssetReadRepo,
        ds_write_repo: CassandraDataSourceWriteRepo,
        ds_read_repo: CassandraDataSourceReadRepo,
        event_bus: EventBus,
    ):
        self._extractor = extractor
        self._transformer = transformer
        self._ts_write = ts_write_repo
        self._asset_write = asset_write_repo
        self._asset_read = asset_read_repo
        self._ds_write = ds_write_repo
        self._ds_read = ds_read_repo
        self._event_bus = event_bus

    async def handle(self, command: StartIngestionCommand) -> dict:
        """Execute the ingestion pipeline for every requested ticker.

        Returns
        -------
        dict
            Ingestion statistics (fetched, stored, skipped, errors).
        """
        stats = {"fetched": 0, "stored": 0, "skipped": 0, "errors": 0}

        for ticker in command.dataset_codes:
            try:
                logger.info("Starting ingestion for ticker %s", ticker)

                raw_page = await self._extractor.fetch(
                    ticker,
                    start=command.start_date,
                    end=command.end_date,
                    period=command.period,
                )
                stats["fetched"] += len(raw_page["records"])

                # Auto-create asset if it doesn't exist yet
                asset_id = f"{command.provider}/{ticker}"
                if self._asset_read.find_latest(asset_id) is None:
                    self._asset_write.save(AssetAggregate(
                        id=asset_id,
                        system_date=datetime.now(UTC),
                        name=ticker,
                        description=f"Auto-ingested from Yahoo Finance ({ticker})",
                    ))

                # Auto-create data-source entry
                if self._ds_read.find_latest(command.provider) is None:
                    self._ds_write.save(DataSourceAggregate(
                        id=command.provider,
                        system_date=datetime.now(UTC),
                        name="Yahoo Finance",
                        description="Yahoo Finance via yfinance library",
                        attributes=set(
                            c for c in raw_page["columns"] if c.lower() != "date"
                        ),
                    ))

                # Transform raw dicts -> CanonicalRecords
                records = self._transformer.transform(
                    raw_page["records"],
                    raw_page["columns"],
                    asset_id,
                    command.provider,
                )
                stats["errors"] += len(raw_page["records"]) - len(records)

                if records:
                    stats["stored"] += self._ts_write.save_batch(records)

                logger.info(
                    "Completed ingestion for ticker %s: %d records stored",
                    ticker,
                    len(records),
                )
            except Exception:
                logger.exception("Failed to ingest ticker %s", ticker)
                stats["errors"] += 1

        await self._event_bus.publish(IngestionCompleted(
            provider=command.provider,
            datasets=command.dataset_codes,
            total_stored=stats["stored"],
        ))

        return stats
