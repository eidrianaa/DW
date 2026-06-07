"""Unit tests for MCP tool handlers (asset, data-source, time-series)."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from mcp_context.tools.asset_tools import handle_asset_tool
from mcp_context.tools.data_source_tools import handle_ds_tool
from mcp_context.tools.time_series_tools import handle_ts_tool


@pytest.fixture
def mock_query_bus():
    bus = MagicMock()
    bus.dispatch = AsyncMock()
    return bus


# ── Asset tools ──────────────────────────────────────────────────────


class TestAssetTools:
    @pytest.mark.asyncio
    async def test_list_assets_tool(self, mock_query_bus):
        mock_query_bus.dispatch.return_value = {
            "items": ["AAPL", "MSFT"],
            "total": 2,
            "has_next": False,
            "offset": 0,
            "limit": 20,
        }
        result = await handle_asset_tool(
            "list_assets", {"offset": 0, "limit": 20}, mock_query_bus,
        )
        assert result["items"] == ["AAPL", "MSFT"]
        assert result["total"] == 2
        mock_query_bus.dispatch.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_asset_details_tool(self, mock_query_bus):
        mock_query_bus.dispatch.return_value = [
            {"id": "TEST", "name": "V2", "system_time": "2024-01-02T00:00:00"},
            {"id": "TEST", "name": "V1", "system_time": "2024-01-01T00:00:00"},
        ]
        result = await handle_asset_tool(
            "get_asset_details", {"assetId": "TEST"}, mock_query_bus,
        )
        assert len(result) == 2
        assert result[0]["name"] == "V2"

    @pytest.mark.asyncio
    async def test_get_asset_details_not_found(self, mock_query_bus):
        mock_query_bus.dispatch.return_value = []
        result = await handle_asset_tool(
            "get_asset_details", {"assetId": "NONEXISTENT"}, mock_query_bus,
        )
        assert result["error"] == "not_found"
        assert "NONEXISTENT" in result["detail"]


# ── Data-source tools ────────────────────────────────────────────────


class TestDataSourceTools:
    @pytest.mark.asyncio
    async def test_list_data_sources_tool(self, mock_query_bus):
        mock_query_bus.dispatch.return_value = {
            "items": ["NASDAQ"],
            "total": 1,
            "has_next": False,
            "offset": 0,
            "limit": 20,
        }
        result = await handle_ds_tool(
            "list_data_sources", {}, mock_query_bus,
        )
        assert result["items"] == ["NASDAQ"]
        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_get_data_source_details_tool(self, mock_query_bus):
        mock_query_bus.dispatch.return_value = [
            {"id": "NASDAQ", "name": "Nasdaq", "attributes": ["Open", "Close"]},
        ]
        result = await handle_ds_tool(
            "get_data_source_details", {"dataSourceId": "NASDAQ"}, mock_query_bus,
        )
        assert len(result) == 1
        assert result[0]["name"] == "Nasdaq"

    @pytest.mark.asyncio
    async def test_get_data_source_details_not_found(self, mock_query_bus):
        mock_query_bus.dispatch.return_value = []
        result = await handle_ds_tool(
            "get_data_source_details", {"dataSourceId": "NOPE"}, mock_query_bus,
        )
        assert result["error"] == "not_found"
        assert "NOPE" in result["detail"]


# ── Time-series tools ────────────────────────────────────────────────


class TestTimeSeriesTools:
    @pytest.mark.asyncio
    async def test_time_series_tool_valid(self, mock_query_bus):
        mock_query_bus.dispatch.return_value = {
            "data": {
                "assetId": "NASDAQ/AAPL",
                "datasourceId": "NASDAQ",
                "records": [
                    {"businessDate": "2024-06-01", "values": {"Close": 150.0}},
                ],
            }
        }
        result = await handle_ts_tool(
            {
                "assetId": "NASDAQ/AAPL",
                "dataSourceId": "NASDAQ",
                "startBusinessDate": "2024-01-01",
                "endBusinessDate": "2024-06-01",
            },
            mock_query_bus,
        )
        assert "data" in result
        assert result["data"]["assetId"] == "NASDAQ/AAPL"
        mock_query_bus.dispatch.assert_called_once()

    @pytest.mark.asyncio
    async def test_time_series_tool_invalid_date(self, mock_query_bus):
        result = await handle_ts_tool(
            {
                "assetId": "X",
                "dataSourceId": "Y",
                "startBusinessDate": "not-a-date",
                "endBusinessDate": "2024-06-01",
            },
            mock_query_bus,
        )
        assert result["error"] == "invalid_date"
        mock_query_bus.dispatch.assert_not_called()

    @pytest.mark.asyncio
    async def test_time_series_tool_range_too_large(self, mock_query_bus):
        result = await handle_ts_tool(
            {
                "assetId": "X",
                "dataSourceId": "Y",
                "startBusinessDate": "2022-01-01",
                "endBusinessDate": "2024-06-01",
            },
            mock_query_bus,
        )
        assert result["error"] == "range_too_large"
        mock_query_bus.dispatch.assert_not_called()

    @pytest.mark.asyncio
    async def test_time_series_tool_start_after_end(self, mock_query_bus):
        result = await handle_ts_tool(
            {
                "assetId": "X",
                "dataSourceId": "Y",
                "startBusinessDate": "2024-06-01",
                "endBusinessDate": "2024-01-01",
            },
            mock_query_bus,
        )
        assert result["error"] == "invalid_range"
        mock_query_bus.dispatch.assert_not_called()
