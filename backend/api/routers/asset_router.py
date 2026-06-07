"""Asset REST API router.

Provides CRUD endpoints for the Asset aggregate, dispatching commands
and queries through the CQRS buses.
"""

from fastapi import APIRouter, HTTPException, Query as Q

from api.schemas.asset_schemas import CreateAssetRequest, UpdateAssetRequest
from asset_context.commands.create_asset import CreateAssetCommand
from asset_context.commands.delete_asset import DeleteAssetCommand
from asset_context.commands.update_asset import UpdateAssetCommand
from asset_context.queries.get_asset_details import GetAssetDetailsQuery
from asset_context.queries.list_assets import ListAssetsQuery
from shared.mediator.command_bus import CommandBus
from shared.mediator.query_bus import QueryBus

router = APIRouter(prefix="/api/v1/assets", tags=["Assets"])

_query_bus: QueryBus | None = None
_command_bus: CommandBus | None = None


def set_query_bus(bus: QueryBus) -> None:
    """Inject the query bus at startup."""
    global _query_bus
    _query_bus = bus


def set_command_bus(bus: CommandBus) -> None:
    """Inject the command bus at startup."""
    global _command_bus
    _command_bus = bus


@router.get("")
async def list_assets(offset: int = Q(0, ge=0), limit: int = Q(20, ge=1, le=100)):
    """Return a paginated list of asset IDs."""
    result = await _query_bus.dispatch(ListAssetsQuery(offset=offset, limit=limit))
    return result


@router.get("/{asset_id:path}")
async def get_asset_details(asset_id: str):
    """Return all temporal versions of a specific asset."""
    result = await _query_bus.dispatch(GetAssetDetailsQuery(asset_id=asset_id))
    if not result:
        raise HTTPException(404, f"Asset '{asset_id}' not found")
    return result


@router.post("")
async def create_asset(request: CreateAssetRequest):
    """Create a new asset aggregate."""
    result = await _command_bus.dispatch(CreateAssetCommand(
        asset_id=request.asset_id,
        name=request.name,
        description=request.description,
        attributes=request.attributes or {},
    ))
    return {"id": result.id, "system_date": result.system_date.isoformat()}


@router.put("/{asset_id:path}")
async def update_asset(asset_id: str, request: UpdateAssetRequest):
    """Insert a new version of an existing asset (temporal update)."""
    try:
        result = await _command_bus.dispatch(UpdateAssetCommand(
            asset_id=asset_id,
            name=request.name,
            description=request.description,
            attributes=request.attributes,
        ))
        return {"id": result.id, "system_date": result.system_date.isoformat()}
    except ValueError as e:
        raise HTTPException(404, str(e))


@router.delete("/{asset_id:path}")
async def delete_asset(asset_id: str):
    """Soft-delete an asset by inserting a version with deleted=true."""
    try:
        result = await _command_bus.dispatch(DeleteAssetCommand(asset_id=asset_id))
        return {"id": result.id, "deleted": True}
    except ValueError as e:
        raise HTTPException(404, str(e))
