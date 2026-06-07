"""MCP tool handlers for the Asset bounded context.

Dispatches ``list_assets`` and ``get_asset_details`` tool calls through the
query bus and returns the results as plain dicts.
"""

from shared.mediator.query_bus import QueryBus
from asset_context.queries.list_assets import ListAssetsQuery
from asset_context.queries.get_asset_details import GetAssetDetailsQuery


async def handle_asset_tool(name: str, args: dict, query_bus: QueryBus) -> dict:
    """Route an asset-related MCP tool call to the correct query.

    Parameters
    ----------
    name:
        Either ``"list_assets"`` or ``"get_asset_details"``.
    args:
        Validated tool arguments.
    query_bus:
        The application query bus.

    Returns
    -------
    dict
        Query result or an error payload.
    """
    if name == "list_assets":
        return await query_bus.dispatch(
            ListAssetsQuery(offset=args.get("offset", 0), limit=args.get("limit", 20))
        )
    elif name == "get_asset_details":
        result = await query_bus.dispatch(GetAssetDetailsQuery(asset_id=args["assetId"]))
        if not result:
            return {"error": "not_found", "detail": f"Asset '{args['assetId']}' not found"}
        return result
    else:
        return {"error": "unknown_tool", "detail": f"Asset tool '{name}' not recognized"}
