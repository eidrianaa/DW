"""Unit tests for query handlers using mocks."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime
from asset_context.queries.list_assets import ListAssetsQuery, ListAssetsHandler
from asset_context.queries.get_asset_details import GetAssetDetailsQuery, GetAssetDetailsHandler
from asset_context.domain.asset_aggregate import AssetAggregate
from datasource_context.queries.list_data_sources import ListDataSourcesQuery, ListDataSourcesHandler
from datasource_context.queries.get_data_source_details import GetDataSourceDetailsQuery, GetDataSourceDetailsHandler
from datasource_context.domain.data_source_aggregate import DataSourceAggregate


@pytest.fixture
def mock_asset_read():
    return MagicMock()


@pytest.fixture
def mock_ds_read():
    return MagicMock()


class TestListAssetsHandler:
    @pytest.mark.asyncio
    async def test_returns_paginated_ids(self, mock_asset_read):
        mock_asset_read.find_all_ids.return_value = (["A", "B", "C"], 10)
        handler = ListAssetsHandler(mock_asset_read)
        result = await handler.handle(ListAssetsQuery(offset=0, limit=3))
        assert result["items"] == ["A", "B", "C"]
        assert result["total"] == 10
        assert result["has_next"] is True

    @pytest.mark.asyncio
    async def test_empty_list(self, mock_asset_read):
        mock_asset_read.find_all_ids.return_value = ([], 0)
        handler = ListAssetsHandler(mock_asset_read)
        result = await handler.handle(ListAssetsQuery())
        assert result["items"] == []
        assert result["total"] == 0
        assert result["has_next"] is False


class TestGetAssetDetailsHandler:
    @pytest.mark.asyncio
    async def test_returns_versions(self, mock_asset_read):
        now = datetime.utcnow()
        mock_asset_read.find_all_versions.return_value = [
            AssetAggregate(id="TEST", system_date=now, name="V2"),
            AssetAggregate(id="TEST", system_date=now, name="V1"),
        ]
        handler = GetAssetDetailsHandler(mock_asset_read)
        result = await handler.handle(GetAssetDetailsQuery(asset_id="TEST"))
        assert len(result) == 2
        assert result[0]["name"] == "V2"

    @pytest.mark.asyncio
    async def test_empty_when_not_found(self, mock_asset_read):
        mock_asset_read.find_all_versions.return_value = []
        handler = GetAssetDetailsHandler(mock_asset_read)
        result = await handler.handle(GetAssetDetailsQuery(asset_id="NONEXISTENT"))
        assert result == []


class TestListDataSourcesHandler:
    @pytest.mark.asyncio
    async def test_returns_paginated(self, mock_ds_read):
        mock_ds_read.find_all_ids.return_value = (["NASDAQ"], 1)
        handler = ListDataSourcesHandler(mock_ds_read)
        result = await handler.handle(ListDataSourcesQuery())
        assert result["items"] == ["NASDAQ"]
        assert result["total"] == 1


class TestGetDataSourceDetailsHandler:
    @pytest.mark.asyncio
    async def test_returns_versions(self, mock_ds_read):
        now = datetime.utcnow()
        mock_ds_read.find_all_versions.return_value = [
            DataSourceAggregate(id="NASDAQ", system_date=now, name="Nasdaq",
                                description="Provider", attributes={"Open", "Close"}),
        ]
        handler = GetDataSourceDetailsHandler(mock_ds_read)
        result = await handler.handle(GetDataSourceDetailsQuery(data_source_id="NASDAQ"))
        assert len(result) == 1
        assert result[0]["name"] == "Nasdaq"
        assert "Open" in result[0]["attributes"]
