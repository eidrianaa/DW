"""Data Source REST API router.

Provides endpoints for registering and querying data sources (providers),
dispatching through the CQRS buses.
"""

from fastapi import APIRouter, HTTPException, Query as Q

from api.schemas.data_source_schemas import RegisterDataSourceRequest
from datasource_context.commands.register_data_source import RegisterDataSourceCommand
from datasource_context.queries.get_data_source_details import GetDataSourceDetailsQuery
from datasource_context.queries.list_data_sources import ListDataSourcesQuery
from shared.mediator.command_bus import CommandBus
from shared.mediator.query_bus import QueryBus

router = APIRouter(prefix="/api/v1/data-sources", tags=["Data Sources"])

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
async def list_data_sources(offset: int = Q(0, ge=0), limit: int = Q(20, ge=1, le=100)):
    """Return a paginated list of data source IDs."""
    result = await _query_bus.dispatch(ListDataSourcesQuery(offset=offset, limit=limit))
    return result


@router.get("/{source_id:path}")
async def get_data_source_details(source_id: str):
    """Return details and supported attributes for a specific data source."""
    result = await _query_bus.dispatch(GetDataSourceDetailsQuery(data_source_id=source_id))
    if not result:
        raise HTTPException(404, f"Data source '{source_id}' not found")
    return result


@router.post("")
async def register_data_source(request: RegisterDataSourceRequest):
    """Register a new data source / provider."""
    result = await _command_bus.dispatch(RegisterDataSourceCommand(
        data_source_id=request.data_source_id,
        name=request.name,
        description=request.description,
        attributes=frozenset(request.attributes or []),
    ))
    return {"id": result.id, "system_date": result.system_date.isoformat()}
