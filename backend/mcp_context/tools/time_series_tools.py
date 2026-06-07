"""MCP tool handler for time-series queries.

Validates date inputs and dispatches a ``GetTimeSeriesQuery`` through the
query bus.
"""

from datetime import date

from shared.mediator.query_bus import QueryBus
from timeseries_context.queries.get_time_series import GetTimeSeriesQuery


async def handle_ts_tool(args: dict, query_bus: QueryBus) -> dict:
    """Handle the ``get_time_series_data`` MCP tool call.

    Parameters
    ----------
    args:
        Validated tool arguments (must include ``assetId``,
        ``dataSourceId``, ``startBusinessDate``, ``endBusinessDate``).
    query_bus:
        The application query bus.

    Returns
    -------
    dict
        Query result or an error payload.
    """
    try:
        start_date = date.fromisoformat(args["startBusinessDate"])
        end_date = date.fromisoformat(args["endBusinessDate"])
    except (KeyError, ValueError) as e:
        return {"error": "invalid_date", "detail": str(e)}

    if (end_date - start_date).days > 365:
        return {"error": "range_too_large", "detail": "Date range exceeds 365 days"}

    if start_date >= end_date:
        return {"error": "invalid_range", "detail": "startBusinessDate must be before endBusinessDate"}

    return await query_bus.dispatch(GetTimeSeriesQuery(
        asset_id=args["assetId"],
        data_source_id=args["dataSourceId"],
        start_date=start_date,
        end_date=end_date,
        include_attributes=args.get("includeAttributes", False),
    ))
