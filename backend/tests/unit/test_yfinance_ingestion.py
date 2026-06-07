"""Tests for the yfinance-based ingestion handler and record transformer."""
import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, date

from ingestion_context.commands.start_ingestion import (
    StartIngestionCommand,
    StartIngestionHandler,
)
from ingestion_context.infrastructure.record_transformer import (
    RecordTransformer,
    CanonicalRecord,
)
from shared.events.event_bus import EventBus


# ---------------------------------------------------------------------------
# RecordTransformer tests
# ---------------------------------------------------------------------------


class TestRecordTransformer:
    """Verify the raw-dict -> CanonicalRecord conversion."""

    def test_transforms_valid_record(self):
        transformer = RecordTransformer()
        raw = [{"date": "2024-06-01", "Open": 150.0, "Close": 152.0}]
        columns = ["date", "Open", "Close"]
        result = transformer.transform(raw, columns, "YFINANCE/AAPL", "YFINANCE")

        assert len(result) == 1
        rec = result[0]
        assert isinstance(rec, CanonicalRecord)
        assert rec.asset_id == "YFINANCE/AAPL"
        assert rec.data_source_id == "YFINANCE"
        assert rec.business_date == date(2024, 6, 1)
        assert rec.business_date_year == 2024
        assert rec.values_double["Open"] == 150.0
        assert rec.values_double["Close"] == 152.0
        assert rec.deleted is False

    def test_skips_record_with_missing_date(self):
        transformer = RecordTransformer()
        raw = [{"Open": 100.0}]  # no "date" key
        result = transformer.transform(raw, ["date", "Open"], "A", "P")
        assert result == []

    def test_skips_record_with_bad_date(self):
        transformer = RecordTransformer()
        raw = [{"date": "not-a-date", "Open": 100.0}]
        result = transformer.transform(raw, ["date", "Open"], "A", "P")
        assert result == []

    def test_puts_non_numeric_into_values_text(self):
        transformer = RecordTransformer()
        raw = [{"date": "2024-01-01", "Note": "ex-dividend"}]
        columns = ["date", "Note"]
        result = transformer.transform(raw, columns, "A", "P")

        assert len(result) == 1
        assert result[0].values_text["Note"] == "ex-dividend"
        assert "Note" not in result[0].values_double

    def test_handles_volume_as_int_float(self):
        transformer = RecordTransformer()
        raw = [{"date": "2024-01-01", "Volume": 5000000}]
        columns = ["date", "Volume"]
        result = transformer.transform(raw, columns, "A", "P")

        # Volume is numeric, should land in values_double
        assert result[0].values_double["Volume"] == 5_000_000.0

    def test_multiple_records(self):
        transformer = RecordTransformer()
        raw = [
            {"date": "2024-01-01", "Close": 100.0},
            {"date": "2024-01-02", "Close": 102.0},
            {"date": "2024-01-03", "Close": 101.0},
        ]
        columns = ["date", "Close"]
        result = transformer.transform(raw, columns, "A", "P")
        assert len(result) == 3
        assert result[0].business_date == date(2024, 1, 1)
        assert result[2].business_date == date(2024, 1, 3)

    def test_none_values_are_skipped(self):
        transformer = RecordTransformer()
        raw = [{"date": "2024-01-01", "Open": None, "Close": 50.0}]
        columns = ["date", "Open", "Close"]
        result = transformer.transform(raw, columns, "A", "P")

        assert "Open" not in result[0].values_double
        assert result[0].values_double["Close"] == 50.0


# ---------------------------------------------------------------------------
# StartIngestionHandler tests (fully mocked, no yfinance network)
# ---------------------------------------------------------------------------


def _make_mock_extractor(records: list[dict], columns: list[str]):
    """Return a mock extractor whose .fetch() resolves to the given data."""
    extractor = MagicMock()
    extractor.fetch = AsyncMock(return_value={
        "records": records,
        "columns": columns,
        "next_cursor": None,
    })
    return extractor


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.fixture
def mock_repos():
    """Return a dict of mocked repositories."""
    ts_write = MagicMock()
    ts_write.save_batch = MagicMock(side_effect=lambda recs: len(recs))

    asset_write = MagicMock()
    asset_read = MagicMock()
    asset_read.find_latest = MagicMock(return_value=None)  # asset doesn't exist yet

    ds_write = MagicMock()
    ds_read = MagicMock()
    ds_read.find_latest = MagicMock(return_value=None)  # ds doesn't exist yet

    return {
        "ts_write": ts_write,
        "asset_write": asset_write,
        "asset_read": asset_read,
        "ds_write": ds_write,
        "ds_read": ds_read,
    }


class TestStartIngestionHandler:
    @pytest.mark.asyncio
    async def test_ingests_records_and_returns_stats(self, mock_repos, event_bus):
        extractor = _make_mock_extractor(
            records=[
                {"date": "2024-06-01", "Open": 100.0, "Close": 102.0},
                {"date": "2024-06-02", "Open": 102.0, "Close": 105.0},
            ],
            columns=["date", "Open", "Close"],
        )

        handler = StartIngestionHandler(
            extractor, RecordTransformer(),
            mock_repos["ts_write"], mock_repos["asset_write"],
            mock_repos["asset_read"], mock_repos["ds_write"],
            mock_repos["ds_read"], event_bus,
        )

        cmd = StartIngestionCommand(
            provider="YFINANCE", dataset_codes=["AAPL"],
        )
        stats = await handler.handle(cmd)

        assert stats["fetched"] == 2
        assert stats["stored"] == 2
        assert stats["errors"] == 0
        mock_repos["ts_write"].save_batch.assert_called_once()

    @pytest.mark.asyncio
    async def test_auto_creates_asset(self, mock_repos, event_bus):
        extractor = _make_mock_extractor(
            records=[{"date": "2024-01-01", "Close": 50.0}],
            columns=["date", "Close"],
        )
        mock_repos["asset_read"].find_latest.return_value = None

        handler = StartIngestionHandler(
            extractor, RecordTransformer(),
            mock_repos["ts_write"], mock_repos["asset_write"],
            mock_repos["asset_read"], mock_repos["ds_write"],
            mock_repos["ds_read"], event_bus,
        )

        await handler.handle(StartIngestionCommand(
            provider="YFINANCE", dataset_codes=["MSFT"],
        ))

        mock_repos["asset_write"].save.assert_called_once()
        saved_asset = mock_repos["asset_write"].save.call_args[0][0]
        assert saved_asset.id == "YFINANCE/MSFT"
        assert saved_asset.name == "MSFT"

    @pytest.mark.asyncio
    async def test_auto_creates_data_source(self, mock_repos, event_bus):
        extractor = _make_mock_extractor(
            records=[{"date": "2024-01-01", "Open": 10.0, "Close": 11.0}],
            columns=["date", "Open", "Close"],
        )
        mock_repos["ds_read"].find_latest.return_value = None

        handler = StartIngestionHandler(
            extractor, RecordTransformer(),
            mock_repos["ts_write"], mock_repos["asset_write"],
            mock_repos["asset_read"], mock_repos["ds_write"],
            mock_repos["ds_read"], event_bus,
        )

        await handler.handle(StartIngestionCommand(
            provider="YFINANCE", dataset_codes=["GOOG"],
        ))

        mock_repos["ds_write"].save.assert_called_once()
        saved_ds = mock_repos["ds_write"].save.call_args[0][0]
        assert saved_ds.id == "YFINANCE"
        assert saved_ds.name == "Yahoo Finance"
        assert "Open" in saved_ds.attributes
        assert "Close" in saved_ds.attributes
        assert "date" not in saved_ds.attributes  # date excluded

    @pytest.mark.asyncio
    async def test_skips_asset_creation_when_exists(self, mock_repos, event_bus):
        extractor = _make_mock_extractor(
            records=[{"date": "2024-01-01", "Close": 1.0}],
            columns=["date", "Close"],
        )
        # Asset already exists
        from asset_context.domain.asset_aggregate import AssetAggregate
        mock_repos["asset_read"].find_latest.return_value = AssetAggregate(
            id="YFINANCE/AAPL", system_date=datetime.utcnow(), name="AAPL",
        )

        handler = StartIngestionHandler(
            extractor, RecordTransformer(),
            mock_repos["ts_write"], mock_repos["asset_write"],
            mock_repos["asset_read"], mock_repos["ds_write"],
            mock_repos["ds_read"], event_bus,
        )

        await handler.handle(StartIngestionCommand(
            provider="YFINANCE", dataset_codes=["AAPL"],
        ))

        mock_repos["asset_write"].save.assert_not_called()

    @pytest.mark.asyncio
    async def test_publishes_ingestion_completed_event(self, mock_repos, event_bus):
        extractor = _make_mock_extractor(
            records=[{"date": "2024-01-01", "Close": 1.0}],
            columns=["date", "Close"],
        )

        captured_events = []

        from ingestion_context.domain.events import IngestionCompleted

        async def _capture(e):
            captured_events.append(e)

        event_bus.subscribe(IngestionCompleted, _capture)

        handler = StartIngestionHandler(
            extractor, RecordTransformer(),
            mock_repos["ts_write"], mock_repos["asset_write"],
            mock_repos["asset_read"], mock_repos["ds_write"],
            mock_repos["ds_read"], event_bus,
        )

        await handler.handle(StartIngestionCommand(
            provider="YFINANCE", dataset_codes=["TSLA"],
        ))

        assert len(captured_events) == 1
        evt = captured_events[0]
        assert evt.provider == "YFINANCE"
        assert "TSLA" in evt.datasets
        assert evt.total_stored == 1

    @pytest.mark.asyncio
    async def test_handles_empty_fetch(self, mock_repos, event_bus):
        extractor = _make_mock_extractor(records=[], columns=[])

        handler = StartIngestionHandler(
            extractor, RecordTransformer(),
            mock_repos["ts_write"], mock_repos["asset_write"],
            mock_repos["asset_read"], mock_repos["ds_write"],
            mock_repos["ds_read"], event_bus,
        )

        stats = await handler.handle(StartIngestionCommand(
            provider="YFINANCE", dataset_codes=["INVALID"],
        ))

        assert stats["fetched"] == 0
        assert stats["stored"] == 0
        mock_repos["ts_write"].save_batch.assert_not_called()

    @pytest.mark.asyncio
    async def test_multiple_tickers(self, mock_repos, event_bus):
        extractor = _make_mock_extractor(
            records=[{"date": "2024-01-01", "Close": 10.0}],
            columns=["date", "Close"],
        )

        handler = StartIngestionHandler(
            extractor, RecordTransformer(),
            mock_repos["ts_write"], mock_repos["asset_write"],
            mock_repos["asset_read"], mock_repos["ds_write"],
            mock_repos["ds_read"], event_bus,
        )

        stats = await handler.handle(StartIngestionCommand(
            provider="YFINANCE",
            dataset_codes=["AAPL", "MSFT", "GOOGL"],
        ))

        assert stats["fetched"] == 3  # 1 record per ticker * 3 tickers
        assert stats["stored"] == 3
        assert extractor.fetch.call_count == 3

    @pytest.mark.asyncio
    async def test_passes_dates_to_extractor(self, mock_repos, event_bus):
        extractor = _make_mock_extractor(
            records=[{"date": "2024-03-15", "Close": 42.0}],
            columns=["date", "Close"],
        )

        handler = StartIngestionHandler(
            extractor, RecordTransformer(),
            mock_repos["ts_write"], mock_repos["asset_write"],
            mock_repos["asset_read"], mock_repos["ds_write"],
            mock_repos["ds_read"], event_bus,
        )

        await handler.handle(StartIngestionCommand(
            provider="YFINANCE",
            dataset_codes=["SPY"],
            start_date="2024-01-01",
            end_date="2024-06-01",
        ))

        extractor.fetch.assert_called_once_with(
            "SPY", start="2024-01-01", end="2024-06-01", period=None,
        )

    @pytest.mark.asyncio
    async def test_counts_transform_errors(self, mock_repos, event_bus):
        extractor = _make_mock_extractor(
            records=[
                {"date": "2024-01-01", "Close": 10.0},
                {"date": "not-a-date", "Close": 20.0},   # will fail transform
                {"Close": 30.0},                           # missing date, will fail
            ],
            columns=["date", "Close"],
        )

        handler = StartIngestionHandler(
            extractor, RecordTransformer(),
            mock_repos["ts_write"], mock_repos["asset_write"],
            mock_repos["asset_read"], mock_repos["ds_write"],
            mock_repos["ds_read"], event_bus,
        )

        stats = await handler.handle(StartIngestionCommand(
            provider="YFINANCE", dataset_codes=["XYZ"],
        ))

        assert stats["fetched"] == 3
        assert stats["stored"] == 1
        assert stats["errors"] == 2
