"""MCP tool handlers for the Data Source bounded context.

Dispatches ``list_data_sources`` and ``get_data_source_details`` tool calls
through the query bus.
"""

from shared.mediator.query_bus import QueryBus
from datasource_context.queries.list_data_sources import ListDataSourcesQuery
from datasource_context.queries.get_data_source_details import GetDataSourceDetailsQuery


async def handle_ds_tool(name: str, args: dict, query_bus: QueryBus) -> dict:
    """Route a data-source-related MCP tool call to the correct query.

    Parameters
    ----------
    name:
        Either ``"list_data_sources"`` or ``"get_data_source_details"``.
    args:
        Validated tool arguments.
    query_bus:
        The application query bus.

    Returns
    -------
    dict
        Query result or an error payload.
    """
    if name == "list_data_sources":
        return await query_bus.dispatch(
            ListDataSourcesQuery(offset=args.get("offset", 0), limit=args.get("limit", 20))
        )
    elif name == "get_data_source_details":
        result = await query_bus.dispatch(
            GetDataSourceDetailsQuery(data_source_id=args["dataSourceId"])
        )
        if not result:
            return {"error": "not_found", "detail": f"Data source '{args['dataSourceId']}' not found"}
        return result
    else:
        return {"error": "unknown_tool", "detail": f"Data source tool '{name}' not recognized"}
