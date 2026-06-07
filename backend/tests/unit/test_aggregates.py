"""Unit tests for domain aggregates."""
import pytest
from datetime import datetime
from asset_context.domain.asset_aggregate import AssetAggregate
from asset_context.domain.asset_id import AssetId
from datasource_context.domain.data_source_aggregate import DataSourceAggregate
from datasource_context.domain.data_source_id import DataSourceId
from ingestion_context.domain.ingestion_job import IngestionJob, IngestionStatus
from ingestion_context.domain.ingestion_result import IngestionResult


class TestAssetAggregate:
    def test_create_asset(self):
        asset = AssetAggregate(
            id="TEST/ASSET", system_date=datetime.utcnow(),
            name="Test Asset", description="A test asset",
            attributes={"type": "equity"},
        )
        assert asset.id == "TEST/ASSET"
        assert asset.name == "Test Asset"
        assert asset.description == "A test asset"
        assert asset.attributes == {"type": "equity"}
        assert not asset.is_deleted

    def test_update_asset(self):
        asset = AssetAggregate(
            id="TEST/ASSET", system_date=datetime.utcnow(),
            name="Original", description="Original desc",
        )
        updated = asset.update(name="Updated Name")
        assert updated.name == "Updated Name"
        assert updated.description == "Original desc"
        assert updated.id == asset.id
        assert updated.system_date != asset.system_date

    def test_mark_deleted(self):
        asset = AssetAggregate(
            id="TEST/ASSET", system_date=datetime.utcnow(),
            name="Test", description="",
        )
        assert not asset.is_deleted
        deleted = asset.mark_deleted()
        assert deleted.is_deleted
        assert deleted.attributes["deleted"] == "true"

    def test_update_preserves_unmodified_fields(self):
        asset = AssetAggregate(
            id="TEST/ASSET", system_date=datetime.utcnow(),
            name="Name", description="Desc",
            attributes={"key": "value"},
        )
        updated = asset.update(description="New Desc")
        assert updated.name == "Name"
        assert updated.description == "New Desc"
        assert updated.attributes == {"key": "value"}


class TestAssetId:
    def test_valid_asset_id(self):
        aid = AssetId(value="NASDAQ/AAPL")
        assert str(aid) == "NASDAQ/AAPL"

    def test_empty_asset_id_raises(self):
        with pytest.raises(ValueError):
            AssetId(value="")

    def test_blank_asset_id_raises(self):
        with pytest.raises(ValueError):
            AssetId(value="   ")


class TestDataSourceAggregate:
    def test_create_data_source(self):
        ds = DataSourceAggregate(
            id="NASDAQ-DATA-LINK", system_date=datetime.utcnow(),
            name="Nasdaq", description="Provider",
            attributes={"Open", "Close", "High"},
        )
        assert ds.id == "NASDAQ-DATA-LINK"
        assert "Open" in ds.attributes
        assert not ds.is_deleted

    def test_update_data_source(self):
        ds = DataSourceAggregate(
            id="NASDAQ", system_date=datetime.utcnow(),
            name="Original",
        )
        updated = ds.update(name="Updated")
        assert updated.name == "Updated"
        assert updated.id == ds.id


class TestDataSourceId:
    def test_valid_data_source_id(self):
        dsid = DataSourceId(value="NASDAQ-DATA-LINK")
        assert str(dsid) == "NASDAQ-DATA-LINK"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            DataSourceId(value="")


class TestIngestionJob:
    def test_initial_status(self):
        job = IngestionJob(id="job1", provider="NASDAQ", dataset_codes=["WIKI/AAPL"])
        assert job.status == IngestionStatus.PENDING

    def test_start_job(self):
        job = IngestionJob(id="job1", provider="NASDAQ", dataset_codes=["WIKI/AAPL"])
        job.start()
        assert job.status == IngestionStatus.RUNNING
        assert job.started_at is not None

    def test_complete_job(self):
        job = IngestionJob(id="job1", provider="NASDAQ", dataset_codes=["WIKI/AAPL"])
        job.start()
        job.complete({"stored": 100, "errors": 0})
        assert job.status == IngestionStatus.COMPLETED
        assert job.stats["stored"] == 100

    def test_fail_job(self):
        job = IngestionJob(id="job1", provider="NASDAQ", dataset_codes=["WIKI/AAPL"])
        job.start()
        job.fail("Connection timeout")
        assert job.status == IngestionStatus.FAILED


class TestIngestionResult:
    def test_success_rate(self):
        result = IngestionResult(fetched=100, stored=90, skipped=5, errors=5)
        assert result.success_rate == 90.0

    def test_zero_fetched(self):
        result = IngestionResult(fetched=0, stored=0, skipped=0, errors=0)
        assert result.success_rate == 0.0
