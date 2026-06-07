"""Time Series REST API router.

Provides the ``GET /api/v1/data`` endpoint that returns bi-temporal
time-series records for a given asset and data source within a date range.
"""

from datetime import date

from fastapi import APIRouter, HTTPException, Query as Q

from shared.config.constants import MAX_DATE_RANGE_DAYS
from shared.mediator.query_bus import QueryBus
from timeseries_context.queries.get_time_series import GetTimeSeriesQuery

router = APIRouter(prefix="/api/v1/data", tags=["Time Series"])

_query_bus: QueryBus | None = None


def set_query_bus(bus: QueryBus) -> None:
    """Inject the query bus at startup."""
    global _query_bus
    _query_bus = bus


@router.get("")
async def get_time_series(
    assetId: str = Q(..., description="Asset ID"),
    dataSourceId: str = Q(..., description="Data source ID"),
    startBusinessDate: date = Q(..., description="Start date YYYY-MM-DD"),
    endBusinessDate: date = Q(..., description="End date YYYY-MM-DD"),
    includeAttributes: bool = Q(False, description="Include attribute list"),
):
    """Return time-series records (latest version per business date, newest first)."""
    if (endBusinessDate - startBusinessDate).days > MAX_DATE_RANGE_DAYS:
        raise HTTPException(400, f"Date range exceeds maximum of {MAX_DATE_RANGE_DAYS} days")
    if startBusinessDate >= endBusinessDate:
        raise HTTPException(400, "startBusinessDate must be before endBusinessDate")

    result = await _query_bus.dispatch(GetTimeSeriesQuery(
        asset_id=assetId,
        data_source_id=dataSourceId,
        start_date=startBusinessDate,
        end_date=endBusinessDate,
        include_attributes=includeAttributes,
    ))
    return result
