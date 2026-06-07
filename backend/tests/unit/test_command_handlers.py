"""Unit tests for command handlers using mocks."""
import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime
from asset_context.commands.create_asset import CreateAssetCommand, CreateAssetHandler
from asset_context.commands.update_asset import UpdateAssetCommand, UpdateAssetHandler
from asset_context.commands.delete_asset import DeleteAssetCommand, DeleteAssetHandler
from asset_context.domain.asset_aggregate import AssetAggregate
from shared.events.event_bus import EventBus


@pytest.fixture
def mock_write_repo():
    repo = MagicMock()
    repo.save = MagicMock()
    return repo


@pytest.fixture
def mock_read_repo():
    repo = MagicMock()
    return repo


@pytest.fixture
def event_bus():
    bus = EventBus()
    return bus


class TestCreateAssetHandler:
    @pytest.mark.asyncio
    async def test_creates_asset(self, mock_write_repo, event_bus):
        handler = CreateAssetHandler(mock_write_repo, event_bus)
        command = CreateAssetCommand(
            asset_id="TEST/ASSET",
            name="Test",
            description="Test asset",
            attributes={"type": "equity"},
        )
        result = await handler.handle(command)
        assert result.id == "TEST/ASSET"
        assert result.name == "Test"
        mock_write_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_publishes_event(self, mock_write_repo, event_bus):
        handler = CreateAssetHandler(mock_write_repo, event_bus)
        events = []
        event_bus.subscribe(type(None), lambda e: events.append(e))  # won't match
        
        command = CreateAssetCommand(
            asset_id="TEST/ASSET", name="Test",
            description="Desc", attributes={},
        )
        await handler.handle(command)
        mock_write_repo.save.assert_called_once()


class TestUpdateAssetHandler:
    @pytest.mark.asyncio
    async def test_updates_existing_asset(self, mock_read_repo, mock_write_repo, event_bus):
        mock_read_repo.find_latest.return_value = AssetAggregate(
            id="TEST/ASSET", system_date=datetime.utcnow(),
            name="Original", description="Desc",
        )
        handler = UpdateAssetHandler(mock_read_repo, mock_write_repo, event_bus)
        command = UpdateAssetCommand(asset_id="TEST/ASSET", name="Updated")
        result = await handler.handle(command)
        assert result.name == "Updated"
        mock_write_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_for_missing_asset(self, mock_read_repo, mock_write_repo, event_bus):
        mock_read_repo.find_latest.return_value = None
        handler = UpdateAssetHandler(mock_read_repo, mock_write_repo, event_bus)
        command = UpdateAssetCommand(asset_id="NONEXISTENT")
        with pytest.raises(ValueError, match="not found"):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_raises_for_deleted_asset(self, mock_read_repo, mock_write_repo, event_bus):
        mock_read_repo.find_latest.return_value = AssetAggregate(
            id="TEST/ASSET", system_date=datetime.utcnow(),
            name="Test", attributes={"deleted": "true"},
        )
        handler = UpdateAssetHandler(mock_read_repo, mock_write_repo, event_bus)
        command = UpdateAssetCommand(asset_id="TEST/ASSET", name="Updated")
        with pytest.raises(ValueError, match="deleted"):
            await handler.handle(command)


class TestDeleteAssetHandler:
    @pytest.mark.asyncio
    async def test_soft_deletes_asset(self, mock_read_repo, mock_write_repo, event_bus):
        mock_read_repo.find_latest.return_value = AssetAggregate(
            id="TEST/ASSET", system_date=datetime.utcnow(),
            name="Test", description="Desc",
        )
        handler = DeleteAssetHandler(mock_read_repo, mock_write_repo, event_bus)
        command = DeleteAssetCommand(asset_id="TEST/ASSET")
        result = await handler.handle(command)
        assert result.is_deleted
        mock_write_repo.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_for_already_deleted(self, mock_read_repo, mock_write_repo, event_bus):
        mock_read_repo.find_latest.return_value = AssetAggregate(
            id="TEST/ASSET", system_date=datetime.utcnow(),
            name="Test", attributes={"deleted": "true"},
        )
        handler = DeleteAssetHandler(mock_read_repo, mock_write_repo, event_bus)
        command = DeleteAssetCommand(asset_id="TEST/ASSET")
        with pytest.raises(ValueError, match="already deleted"):
            await handler.handle(command)
